/**
 * WebSocket Event Types and Message Schemas
 * 
 * Comprehensive type definitions for real-time communication system
 */

// Base message structure
export interface WebSocketMessage<T = any> {
  type: string
  data: T
  timestamp: number
  messageId: string
}

// Authentication types
export interface AuthRequestData {
  userId: string
  userType: 'teacher' | 'student'
  academyId: string
  token?: string
}

export interface AuthSuccessData {
  userId: string
  userType: 'teacher' | 'student'
  academyId: string
  message: string
}

export interface AuthFailedData {
  error: string
  code?: string
}

// Exam session types
export interface ExamPrepareData {
  sessionId: string
  examId: string
  enrolledStudents: string[]
  duration: number // minutes
  instructions?: string
}

export interface ExamLaunchData {
  sessionId: string
  examId?: string
  startTime?: string | Date
  duration?: number
  message?: string
}

export interface ExamStatusData {
  sessionId: string
  status: 'preparing' | 'active' | 'paused' | 'completed' | 'terminated'
  connectedStudents?: number
  enrolledStudents?: number
}

// Student progress types
export interface StudentJoinedData {
  sessionId: string
  studentId: string
  connectedStudents?: string[]
  examId?: string
  status?: string
  startTime?: string | Date
}

export interface StudentLeftData {
  sessionId: string
  studentId: string
  connectedStudents?: string[]
  reason?: 'disconnect' | 'complete' | 'terminate'
}

export interface StudentProgressData {
  sessionId: string
  studentId: string
  questionId?: string
  progress: number // percentage 0-100
  questionsAnswered?: number
  totalQuestions?: number
  timeSpent?: number // seconds
  timestamp: number
}

// Answer submission types
export interface AnswerSubmissionData {
  sessionId: string
  questionId: string
  answer: any // Can be string, number, array, etc.
  progress?: number
  timeSpent?: number
  isPartial?: boolean
}

export interface AnswerAutoSaveData {
  sessionId: string
  questionId: string
  answer: any
  isPartial?: boolean
}

export interface AnswerResponseData {
  questionId: string
  status: 'saved' | 'autosaved' | 'error'
  timestamp?: number
  error?: string
}

// Real-time updates
export interface LiveUpdateData {
  sessionId: string
  type: 'student_progress' | 'connection_status' | 'exam_status'
  data: any
  affectedUsers?: string[]
}

export interface BroadcastMessageData {
  sessionId: string
  message: string
  type: 'info' | 'warning' | 'error' | 'success'
  sender: string
  targetUsers?: string[] // If null, broadcast to all
}

export interface TimeWarningData {
  sessionId: string
  minutesRemaining: number
  message: string
  isUrgent?: boolean
}

// Connection management
export interface HeartbeatData {
  status: 'alive' | 'ping' | 'pong'
  timestamp?: number
}

export interface ReconnectData {
  sessionId?: string
  lastMessageId?: string
  missedMessages?: boolean
}

// Error types
export interface ErrorData {
  error: string
  code?: string
  details?: string
  recoverable?: boolean
}

// Exam management extended types
export interface ExamSessionInfo {
  id: string
  examId: string
  academyId: string
  teacherId: string
  status: 'preparing' | 'active' | 'paused' | 'completed' | 'terminated'
  startTime?: Date
  endTime?: Date
  duration: number
  enrolledStudents: string[]
  activeStudents: string[]
  createdAt: Date
}

export interface StudentSessionInfo {
  studentId: string
  sessionId: string
  joinedAt: Date
  lastActivity: Date
  progress: number
  questionsAnswered: number
  timeSpent: number
  connectionStatus: 'connected' | 'disconnected' | 'reconnecting'
}

// Message type unions for type safety
export type WebSocketMessageData = 
  | AuthRequestData
  | AuthSuccessData 
  | AuthFailedData
  | ExamPrepareData
  | ExamLaunchData
  | ExamStatusData
  | StudentJoinedData
  | StudentLeftData
  | StudentProgressData
  | AnswerSubmissionData
  | AnswerAutoSaveData
  | AnswerResponseData
  | LiveUpdateData
  | BroadcastMessageData
  | TimeWarningData
  | HeartbeatData
  | ReconnectData
  | ErrorData

// Event type constants (matching server.ts)
export const WS_EVENT_TYPES = {
  // Authentication
  AUTH_REQUEST: 'auth_request',
  AUTH_SUCCESS: 'auth_success',
  AUTH_FAILED: 'auth_failed',
  
  // Exam Session Management
  EXAM_PREPARE: 'exam_prepare',
  EXAM_LAUNCH: 'exam_launch',
  EXAM_PAUSE: 'exam_pause',
  EXAM_RESUME: 'exam_resume',
  EXAM_COMPLETE: 'exam_complete',
  EXAM_TERMINATE: 'exam_terminate',
  
  // Student Progress
  STUDENT_JOINED: 'student_joined',
  STUDENT_LEFT: 'student_left',
  STUDENT_PROGRESS: 'student_progress',
  ANSWER_SUBMITTED: 'answer_submitted',
  ANSWER_AUTOSAVED: 'answer_autosaved',
  
  // Real-time Updates
  LIVE_UPDATE: 'live_update',
  BROADCAST_MESSAGE: 'broadcast_message',
  TIME_WARNING: 'time_warning',
  
  // Connection Management
  HEARTBEAT: 'heartbeat',
  RECONNECT: 'reconnect',
  
  // Errors
  ERROR: 'error'
} as const

// Type for event type values
export type WebSocketEventType = typeof WS_EVENT_TYPES[keyof typeof WS_EVENT_TYPES]

// Connection state types
export interface WebSocketConnectionState {
  status: 'connecting' | 'connected' | 'disconnected' | 'error' | 'reconnecting'
  authenticated: boolean
  userId?: string
  userType?: 'teacher' | 'student'
  academyId?: string
  sessionId?: string
  lastActivity?: Date
  reconnectAttempts: number
  maxReconnectAttempts: number
}

// Callback types for hooks
export type WebSocketEventCallback<T = any> = (data: T) => void
export type WebSocketErrorCallback = (error: Error | string) => void
export type WebSocketStatusCallback = (status: WebSocketConnectionState) => void

// Hook configuration types
export interface UseWebSocketConfig {
  url?: string
  autoConnect?: boolean
  autoReconnect?: boolean
  maxReconnectAttempts?: number
  reconnectInterval?: number
  heartbeatInterval?: number
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: WebSocketErrorCallback
  onMessage?: WebSocketEventCallback<WebSocketMessage>
}

// Exam management hook types
export interface UseExamSessionConfig {
  sessionId: string
  userType: 'teacher' | 'student'
  onStudentJoined?: WebSocketEventCallback<StudentJoinedData>
  onStudentLeft?: WebSocketEventCallback<StudentLeftData>
  onProgressUpdate?: WebSocketEventCallback<StudentProgressData>
  onAnswerSubmitted?: WebSocketEventCallback<AnswerSubmissionData>
  onExamLaunched?: WebSocketEventCallback<ExamLaunchData>
  onTimeWarning?: WebSocketEventCallback<TimeWarningData>
  onBroadcastMessage?: WebSocketEventCallback<BroadcastMessageData>
}

// Teacher dashboard types
export interface TeacherDashboardData {
  activeSessions: ExamSessionInfo[]
  connectedStudents: StudentSessionInfo[]
  recentActivity: {
    type: string
    studentId: string
    timestamp: Date
    details: any
  }[]
}

// Student exam interface types
export interface StudentExamData {
  sessionInfo: ExamSessionInfo
  currentQuestion?: number
  totalQuestions?: number
  timeRemaining?: number
  answers: Record<string, any>
  progress: number
  connectionStatus: 'connected' | 'disconnected' | 'reconnecting'
}