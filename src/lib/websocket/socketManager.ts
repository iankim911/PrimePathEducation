/**
 * WebSocket Manager for Real-time Exam Communication
 * 
 * Handles WebSocket connections between teachers and students during live exam sessions.
 * Supports session management, real-time updates, and message broadcasting.
 */

import { Server as SocketIOServer } from 'socket.io'
import { Server as HTTPServer } from 'http'
import { logger, WebSocketError, RateLimiter, PerformanceMonitor } from '@/lib/utils/errorHandler'

export interface SocketUser {
  id: string
  sessionId: string
  role: 'teacher' | 'student'
  userId: string
  userName: string
  joinedAt: string
}

export interface ExamMessage {
  type: 'session_start' | 'session_end' | 'answer_submitted' | 'time_warning' | 'broadcast_message' | 'student_joined' | 'student_left'
  sessionId: string
  from?: string
  data?: any
  timestamp: string
}

export interface SessionStatus {
  sessionId: string
  status: 'waiting' | 'active' | 'paused' | 'completed'
  startedAt?: string
  endedAt?: string
  connectedStudents: number
  totalStudents: number
  timeRemaining?: number
}

class SocketManager {
  private io: SocketIOServer | null = null
  private activeSessions: Map<string, SessionStatus> = new Map()
  private connectedUsers: Map<string, SocketUser> = new Map()

  initialize(server: HTTPServer) {
    this.io = new SocketIOServer(server, {
      cors: {
        origin: process.env.NODE_ENV === 'production' 
          ? process.env.ALLOWED_ORIGINS?.split(',') || []
          : ['http://localhost:3000', 'http://127.0.0.1:3000'],
        methods: ['GET', 'POST'],
        credentials: true
      },
      transports: ['websocket', 'polling']
    })

    this.setupEventHandlers()
    console.log('✅ WebSocket server initialized')
  }

  private setupEventHandlers() {
    if (!this.io) return

    this.io.on('connection', (socket) => {
      console.log(`🔌 Client connected: ${socket.id}`)

      // Handle user authentication and session join
      socket.on('join_session', async (data: {
        sessionId: string
        userId: string
        userName: string
        role: 'teacher' | 'student'
        academyId: string
      }) => {
        PerformanceMonitor.startTimer(`join-session-${socket.id}`)
        
        try {
          const { sessionId, userId, userName, role, academyId } = data

          // Rate limiting for join attempts
          const clientId = socket.handshake.address
          if (RateLimiter.isRateLimited(clientId, 10, 60000)) {
            logger.warn('Rate limit exceeded for join_session', { additionalData: { clientId, sessionId, userId } }, 'websocket')
            socket.emit('error', { message: 'Too many join attempts. Please try again later.' })
            return
          }

          // Validate required fields
          if (!sessionId || !userId || !userName || !role || !academyId) {
            throw new WebSocketError('Missing required fields for session join')
          }

          logger.info('User attempting to join session', { additionalData: { sessionId, userId, userName, role } }, 'websocket')

          // Validate session exists (you'd implement session validation here)
          const sessionExists = await this.validateSession(sessionId, academyId)
          if (!sessionExists) {
            logger.warn('User attempted to join invalid session', { additionalData: { sessionId, userId, academyId } }, 'websocket')
            socket.emit('error', { message: 'Session not found or access denied' })
            return
          }

          // Create user object
          const user: SocketUser = {
            id: socket.id,
            sessionId,
            role,
            userId,
            userName,
            joinedAt: new Date().toISOString()
          }

          // Store user and join room
          this.connectedUsers.set(socket.id, user)
          socket.join(sessionId)

          // Update session status
          this.updateSessionStatus(sessionId)

          // Notify others in the session
          socket.to(sessionId).emit('user_joined', {
            user: { userId, userName, role },
            timestamp: new Date().toISOString()
          })

          // Send current session status to the new user
          const sessionStatus = this.activeSessions.get(sessionId)
          socket.emit('session_status', sessionStatus)

          const duration = PerformanceMonitor.endTimer(`join-session-${socket.id}`, { sessionId, userId })
          
          logger.info(
            `User ${userName} (${role}) successfully joined session ${sessionId}`,
            { additionalData: { sessionId, userId, userName, role, duration } },
            'websocket'
          )

        } catch (error) {
          PerformanceMonitor.endTimer(`join-session-${socket.id}`)
          
          logger.error(
            'Error joining session',
            error instanceof Error ? error : new Error(String(error)),
            { additionalData: { sessionId: data?.sessionId, userId: data?.userId, socketId: socket.id } },
            'websocket'
          )
          
          socket.emit('error', { 
            message: error instanceof WebSocketError ? error.message : 'Failed to join session',
            code: 'JOIN_SESSION_FAILED'
          })
        }
      })

      // Handle exam session control (teacher only)
      socket.on('control_session', (data: {
        action: 'start' | 'pause' | 'resume' | 'end'
        sessionId: string
        timeLimit?: number
      }) => {
        const user = this.connectedUsers.get(socket.id)
        if (!user || user.role !== 'teacher') {
          socket.emit('error', { message: 'Unauthorized action' })
          return
        }

        this.handleSessionControl(data, user)
      })

      // Handle student answer submission
      socket.on('submit_answer', (data: {
        sessionId: string
        questionId: string
        answer: any
        timeSpent: number
      }) => {
        const user = this.connectedUsers.get(socket.id)
        if (!user || user.role !== 'student') {
          socket.emit('error', { message: 'Unauthorized action' })
          return
        }

        this.handleAnswerSubmission(data, user)
      })

      // Handle broadcast messages from teacher
      socket.on('broadcast_message', (data: {
        sessionId: string
        message: string
        type: 'announcement' | 'warning' | 'reminder'
      }) => {
        const user = this.connectedUsers.get(socket.id)
        if (!user || user.role !== 'teacher') {
          socket.emit('error', { message: 'Unauthorized action' })
          return
        }

        const message: ExamMessage = {
          type: 'broadcast_message',
          sessionId: data.sessionId,
          from: user.userName,
          data: { message: data.message, messageType: data.type },
          timestamp: new Date().toISOString()
        }

        this.io!.to(data.sessionId).emit('exam_message', message)
        console.log(`📢 Broadcast from ${user.userName}: ${data.message}`)
      })

      // Handle real-time progress updates
      socket.on('request_progress', (data: { sessionId: string }) => {
        const user = this.connectedUsers.get(socket.id)
        if (!user || user.role !== 'teacher') {
          socket.emit('error', { message: 'Unauthorized action' })
          return
        }

        this.sendProgressUpdate(data.sessionId, socket.id)
      })

      // Handle disconnection
      socket.on('disconnect', () => {
        this.handleDisconnection(socket.id)
      })

      // Handle ping/pong for connection health
      socket.on('ping', () => {
        socket.emit('pong')
      })
    })
  }

  private async validateSession(sessionId: string, academyId: string): Promise<boolean> {
    // TODO: Implement actual session validation with database
    // This would check if the session exists, is active, and user has access
    return true
  }

  private handleSessionControl(data: {
    action: 'start' | 'pause' | 'resume' | 'end'
    sessionId: string
    timeLimit?: number
  }, teacher: SocketUser) {
    const { action, sessionId, timeLimit } = data

    let sessionStatus = this.activeSessions.get(sessionId) || {
      sessionId,
      status: 'waiting',
      connectedStudents: 0,
      totalStudents: 0
    }

    switch (action) {
      case 'start':
        sessionStatus.status = 'active'
        sessionStatus.startedAt = new Date().toISOString()
        if (timeLimit) {
          sessionStatus.timeRemaining = timeLimit * 60 // Convert minutes to seconds
        }
        break

      case 'pause':
        sessionStatus.status = 'paused'
        break

      case 'resume':
        sessionStatus.status = 'active'
        break

      case 'end':
        sessionStatus.status = 'completed'
        sessionStatus.endedAt = new Date().toISOString()
        break
    }

    this.activeSessions.set(sessionId, sessionStatus)

    // Broadcast session control to all participants
    const message: ExamMessage = {
      type: action === 'start' ? 'session_start' : 'session_end',
      sessionId,
      from: teacher.userName,
      data: { action, timeLimit },
      timestamp: new Date().toISOString()
    }

    this.io!.to(sessionId).emit('session_control', { action, sessionStatus })
    this.io!.to(sessionId).emit('exam_message', message)

    // Start timer for active sessions
    if (action === 'start' && timeLimit) {
      this.startSessionTimer(sessionId, timeLimit * 60)
    }

    console.log(`🎮 Session ${sessionId} ${action} by ${teacher.userName}`)
  }

  private handleAnswerSubmission(data: {
    sessionId: string
    questionId: string
    answer: any
    timeSpent: number
  }, student: SocketUser) {
    // TODO: Save answer to database
    
    // Notify teacher of submission
    const message: ExamMessage = {
      type: 'answer_submitted',
      sessionId: data.sessionId,
      from: student.userName,
      data: {
        questionId: data.questionId,
        timeSpent: data.timeSpent,
        studentId: student.userId
      },
      timestamp: new Date().toISOString()
    }

    // Send to teachers only
    this.getTeachersInSession(data.sessionId).forEach(teacherSocketId => {
      this.io!.to(teacherSocketId).emit('exam_message', message)
    })

    // Confirm submission to student
    this.io!.to(student.id).emit('answer_confirmed', {
      questionId: data.questionId,
      timestamp: new Date().toISOString()
    })
  }

  private startSessionTimer(sessionId: string, durationSeconds: number) {
    const startTime = Date.now()
    
    const timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000)
      const remaining = durationSeconds - elapsed

      if (remaining <= 0) {
        // Time's up - end session
        clearInterval(timer)
        this.handleAutoEndSession(sessionId)
      } else {
        // Update time remaining
        const sessionStatus = this.activeSessions.get(sessionId)
        if (sessionStatus) {
          sessionStatus.timeRemaining = remaining
          this.activeSessions.set(sessionId, sessionStatus)
        }

        // Send time warnings
        if (remaining === 300) { // 5 minutes
          this.sendTimeWarning(sessionId, '5 minutes remaining')
        } else if (remaining === 60) { // 1 minute
          this.sendTimeWarning(sessionId, '1 minute remaining')
        } else if (remaining === 30) { // 30 seconds
          this.sendTimeWarning(sessionId, '30 seconds remaining')
        }

        // Broadcast time update every 30 seconds
        if (elapsed % 30 === 0) {
          this.io!.to(sessionId).emit('time_update', { timeRemaining: remaining })
        }
      }
    }, 1000)
  }

  private handleAutoEndSession(sessionId: string) {
    const sessionStatus = this.activeSessions.get(sessionId)
    if (sessionStatus) {
      sessionStatus.status = 'completed'
      sessionStatus.endedAt = new Date().toISOString()
      sessionStatus.timeRemaining = 0
      this.activeSessions.set(sessionId, sessionStatus)
    }

    const message: ExamMessage = {
      type: 'session_end',
      sessionId,
      data: { reason: 'time_limit_reached' },
      timestamp: new Date().toISOString()
    }

    this.io!.to(sessionId).emit('session_control', { action: 'end', sessionStatus })
    this.io!.to(sessionId).emit('exam_message', message)

    console.log(`⏰ Session ${sessionId} ended automatically (time limit reached)`)
  }

  private sendTimeWarning(sessionId: string, message: string) {
    const examMessage: ExamMessage = {
      type: 'time_warning',
      sessionId,
      data: { message },
      timestamp: new Date().toISOString()
    }

    this.io!.to(sessionId).emit('exam_message', examMessage)
  }

  private sendProgressUpdate(sessionId: string, requestorSocketId: string) {
    // TODO: Get actual progress from database
    const mockProgress = {
      totalStudents: 25,
      studentsCompleted: 8,
      averageProgress: 65,
      questionsAnswered: 156,
      totalQuestions: 240
    }

    this.io!.to(requestorSocketId).emit('progress_update', {
      sessionId,
      progress: mockProgress,
      timestamp: new Date().toISOString()
    })
  }

  private getTeachersInSession(sessionId: string): string[] {
    return Array.from(this.connectedUsers.entries())
      .filter(([_, user]) => user.sessionId === sessionId && user.role === 'teacher')
      .map(([socketId, _]) => socketId)
  }

  private updateSessionStatus(sessionId: string) {
    const usersInSession = Array.from(this.connectedUsers.values())
      .filter(user => user.sessionId === sessionId)

    const connectedStudents = usersInSession.filter(user => user.role === 'student').length

    let sessionStatus = this.activeSessions.get(sessionId) || {
      sessionId,
      status: 'waiting' as const,
      connectedStudents: 0,
      totalStudents: 0
    }

    sessionStatus.connectedStudents = connectedStudents
    this.activeSessions.set(sessionId, sessionStatus)

    // Broadcast updated status to session
    this.io!.to(sessionId).emit('session_status', sessionStatus)
  }

  private handleDisconnection(socketId: string) {
    const user = this.connectedUsers.get(socketId)
    if (user) {
      // Remove user from connected users
      this.connectedUsers.delete(socketId)

      // Update session status
      this.updateSessionStatus(user.sessionId)

      // Notify others in the session
      const message: ExamMessage = {
        type: 'student_left',
        sessionId: user.sessionId,
        data: { userId: user.userId, userName: user.userName, role: user.role },
        timestamp: new Date().toISOString()
      }

      this.io!.to(user.sessionId).emit('exam_message', message)

      console.log(`👤 User ${user.userName} (${user.role}) left session ${user.sessionId}`)
    }

    console.log(`🔌 Client disconnected: ${socketId}`)
  }

  // Public methods for external use
  getActiveSessionsCount(): number {
    return this.activeSessions.size
  }

  getConnectedUsersCount(): number {
    return this.connectedUsers.size
  }

  getSessionStatus(sessionId: string): SessionStatus | undefined {
    return this.activeSessions.get(sessionId)
  }

  broadcastToSession(sessionId: string, event: string, data: any) {
    if (this.io) {
      this.io.to(sessionId).emit(event, data)
    }
  }
}

// Export singleton instance
export const socketManager = new SocketManager()
export default socketManager