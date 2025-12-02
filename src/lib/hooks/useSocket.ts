/**
 * WebSocket Hook for Real-time Exam Communication
 * 
 * Provides a React hook interface for connecting to WebSocket server
 * and managing real-time communication during exam sessions.
 */

import { useEffect, useRef, useState, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'
import type { ExamMessage, SessionStatus } from '@/lib/websocket/socketManager'

export interface UseSocketOptions {
  sessionId?: string
  userId?: string
  userName?: string
  role?: 'teacher' | 'student'
  academyId?: string
  autoConnect?: boolean
}

export interface UseSocketReturn {
  socket: Socket | null
  isConnected: boolean
  sessionStatus: SessionStatus | null
  messages: ExamMessage[]
  joinSession: (sessionData: {
    sessionId: string
    userId: string
    userName: string
    role: 'teacher' | 'student'
    academyId: string
  }) => void
  leaveSession: () => void
  sendAnswer: (data: {
    questionId: string
    answer: any
    timeSpent: number
  }) => void
  controlSession: (action: 'start' | 'pause' | 'resume' | 'end', timeLimit?: number) => void
  broadcastMessage: (message: string, type?: 'announcement' | 'warning' | 'reminder') => void
  requestProgress: () => void
  clearMessages: () => void
  connectionError: string | null
}

export function useSocket(options: UseSocketOptions = {}): UseSocketReturn {
  const {
    sessionId,
    userId,
    userName,
    role,
    academyId,
    autoConnect = false
  } = options

  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [sessionStatus, setSessionStatus] = useState<SessionStatus | null>(null)
  const [messages, setMessages] = useState<ExamMessage[]>([])
  const [connectionError, setConnectionError] = useState<string | null>(null)
  
  const currentSessionRef = useRef<string | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)

  // Initialize socket connection
  const initializeSocket = useCallback(() => {
    if (socket) return socket

    const newSocket = io(process.env.NODE_ENV === 'production' 
      ? process.env.NEXT_PUBLIC_WEBSOCKET_URL || ''
      : 'http://localhost:3000', {
      transports: ['websocket', 'polling'],
      timeout: 10000,
      forceNew: true
    })

    // Connection handlers
    newSocket.on('connect', () => {
      console.log('✅ Socket connected:', newSocket.id)
      setIsConnected(true)
      setConnectionError(null)
      reconnectAttemptsRef.current = 0
    })

    newSocket.on('disconnect', (reason) => {
      console.log('❌ Socket disconnected:', reason)
      setIsConnected(false)
      
      // Attempt to reconnect for certain disconnect reasons
      if (reason === 'io server disconnect') {
        setConnectionError('Server disconnected')
      } else {
        attemptReconnect()
      }
    })

    newSocket.on('connect_error', (error) => {
      console.error('❌ Connection error:', error)
      setConnectionError(`Connection failed: ${error.message}`)
      attemptReconnect()
    })

    // Exam-specific event handlers
    newSocket.on('session_status', (status: SessionStatus) => {
      setSessionStatus(status)
    })

    newSocket.on('exam_message', (message: ExamMessage) => {
      setMessages(prev => [...prev, message])
    })

    newSocket.on('session_control', (data: { action: string; sessionStatus: SessionStatus }) => {
      setSessionStatus(data.sessionStatus)
      
      // Handle automatic session end
      if (data.action === 'end') {
        setMessages(prev => [...prev, {
          type: 'session_end',
          sessionId: data.sessionStatus.sessionId,
          data: { reason: 'session_ended' },
          timestamp: new Date().toISOString()
        }])
      }
    })

    newSocket.on('time_update', (data: { timeRemaining: number }) => {
      setSessionStatus(prev => prev ? {
        ...prev,
        timeRemaining: data.timeRemaining
      } : null)
    })

    newSocket.on('answer_confirmed', (data: { questionId: string; timestamp: string }) => {
      // Handle answer confirmation for students
      setMessages(prev => [...prev, {
        type: 'answer_submitted' as const,
        sessionId: currentSessionRef.current || '',
        data: { questionId: data.questionId, confirmed: true },
        timestamp: data.timestamp
      }])
    })

    newSocket.on('user_joined', (data: { user: any; timestamp: string }) => {
      setMessages(prev => [...prev, {
        type: 'student_joined' as const,
        sessionId: currentSessionRef.current || '',
        data: data.user,
        timestamp: data.timestamp
      }])
    })

    newSocket.on('progress_update', (data: any) => {
      // Handle progress updates for teachers
      setMessages(prev => [...prev, {
        type: 'broadcast_message' as const,
        sessionId: currentSessionRef.current || '',
        data: { progress: data.progress },
        timestamp: data.timestamp
      }])
    })

    newSocket.on('error', (error: { message: string }) => {
      setConnectionError(error.message)
    })

    setSocket(newSocket)
    return newSocket
  }, [socket])

  // Reconnection logic
  const attemptReconnect = useCallback(() => {
    if (reconnectAttemptsRef.current >= 5) {
      setConnectionError('Maximum reconnection attempts reached')
      return
    }

    const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000)
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }

    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectAttemptsRef.current++
      console.log(`🔄 Reconnect attempt ${reconnectAttemptsRef.current}`)
      
      if (socket) {
        socket.connect()
      } else {
        initializeSocket()
      }
    }, delay)
  }, [socket, initializeSocket])

  // Join session
  const joinSession = useCallback((sessionData: {
    sessionId: string
    userId: string
    userName: string
    role: 'teacher' | 'student'
    academyId: string
  }) => {
    const socketInstance = socket || initializeSocket()
    
    if (socketInstance && socketInstance.connected) {
      currentSessionRef.current = sessionData.sessionId
      socketInstance.emit('join_session', sessionData)
    } else {
      setConnectionError('Socket not connected')
    }
  }, [socket, initializeSocket])

  // Leave session
  const leaveSession = useCallback(() => {
    if (socket && currentSessionRef.current) {
      socket.disconnect()
      currentSessionRef.current = null
      setSessionStatus(null)
      setMessages([])
    }
  }, [socket])

  // Send answer (students)
  const sendAnswer = useCallback((data: {
    questionId: string
    answer: any
    timeSpent: number
  }) => {
    if (socket && currentSessionRef.current && isConnected) {
      socket.emit('submit_answer', {
        sessionId: currentSessionRef.current,
        ...data
      })
    }
  }, [socket, isConnected])

  // Control session (teachers)
  const controlSession = useCallback((action: 'start' | 'pause' | 'resume' | 'end', timeLimit?: number) => {
    if (socket && currentSessionRef.current && isConnected) {
      socket.emit('control_session', {
        action,
        sessionId: currentSessionRef.current,
        timeLimit
      })
    }
  }, [socket, isConnected])

  // Broadcast message (teachers)
  const broadcastMessage = useCallback((message: string, type: 'announcement' | 'warning' | 'reminder' = 'announcement') => {
    if (socket && currentSessionRef.current && isConnected) {
      socket.emit('broadcast_message', {
        sessionId: currentSessionRef.current,
        message,
        type
      })
    }
  }, [socket, isConnected])

  // Request progress (teachers)
  const requestProgress = useCallback(() => {
    if (socket && currentSessionRef.current && isConnected) {
      socket.emit('request_progress', {
        sessionId: currentSessionRef.current
      })
    }
  }, [socket, isConnected])

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  // Auto-connect if options provided
  useEffect(() => {
    if (autoConnect && sessionId && userId && userName && role && academyId) {
      const socketInstance = initializeSocket()
      
      // Wait for connection before joining
      const handleConnect = () => {
        joinSession({ sessionId, userId, userName, role, academyId })
        socketInstance.off('connect', handleConnect)
      }

      if (socketInstance.connected) {
        joinSession({ sessionId, userId, userName, role, academyId })
      } else {
        socketInstance.on('connect', handleConnect)
      }
    }
  }, [autoConnect, sessionId, userId, userName, role, academyId, initializeSocket, joinSession])

  // Cleanup
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      
      if (socket) {
        socket.disconnect()
      }
    }
  }, [socket])

  return {
    socket,
    isConnected,
    sessionStatus,
    messages,
    joinSession,
    leaveSession,
    sendAnswer,
    controlSession,
    broadcastMessage,
    requestProgress,
    clearMessages,
    connectionError
  }
}