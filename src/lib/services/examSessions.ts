/**
 * Exam Sessions Service Layer
 * 
 * This service handles live exam sessions, student participation, and real-time monitoring.
 * Components should use these service functions for all exam session operations.
 */

import { supabase } from '@/lib/supabaseClient'
import { ExamSession } from './exams'

/**
 * Student exam attempt interface
 */
export interface StudentExamAttempt {
  id: string
  academy_id: string
  student_id: string
  exam_id: string
  session_id?: string | null
  participant_id?: string | null
  attempt_number: number
  started_at: string
  submitted_at?: string | null
  time_spent_seconds?: number | null
  time_limit_seconds?: number | null
  current_question_id?: string | null
  questions_answered: number
  total_questions: number
  status: 'in_progress' | 'submitted' | 'auto_submitted' | 'abandoned'
  raw_score: number
  max_possible_score: number
  percentage_score?: number | null
  passed?: boolean | null
  ip_address?: string | null
  user_agent?: string | null
  tab_switches: number
  copy_paste_attempts: number
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Session participant interface
 */
export interface ExamSessionParticipant {
  id: string
  academy_id: string
  session_id: string
  student_id: string
  invited_at: string
  first_accessed?: string | null
  last_accessed?: string | null
  participation_status: 'invited' | 'started' | 'in_progress' | 'submitted' | 'auto_submitted' | 'absent'
  extra_time_minutes: number
  special_instructions?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Session with participants and attempts
 */
export interface ExamSessionWithDetails extends ExamSession {
  exam?: {
    title: string
    total_questions: number
    time_limit_minutes?: number | null
  }
  class?: {
    name: string
  }
  teacher?: {
    full_name: string
  }
  participants?: ExamSessionParticipant[]
  attempts?: StudentExamAttempt[]
}

/**
 * Get all exam sessions for an academy
 */
export async function getAllExamSessionsByAcademy(academyId: string, filters?: {
  status?: ExamSession['status']
  exam_id?: string
  class_id?: string
  teacher_id?: string
  limit?: number
}): Promise<ExamSession[]> {
  let query = supabase
    .from('exam_sessions')
    .select('*')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)

  if (filters?.status) {
    query = query.eq('status', filters.status)
  }

  if (filters?.exam_id) {
    query = query.eq('exam_id', filters.exam_id)
  }

  if (filters?.class_id) {
    query = query.eq('class_id', filters.class_id)
  }

  if (filters?.teacher_id) {
    query = query.eq('teacher_id', filters.teacher_id)
  }

  query = query
    .order('created_at', { ascending: false })
    .limit(filters?.limit || 100)

  const { data, error } = await query

  if (error) {
    console.error('Error fetching exam sessions:', error)
    throw new Error(`Failed to fetch exam sessions: ${error.message}`)
  }

  return data || []
}

/**
 * Get exam session by ID with details
 */
export async function getExamSessionWithDetails(sessionId: string, academyId: string): Promise<ExamSessionWithDetails | null> {
  const { data: session, error: sessionError } = await supabase
    .from('exam_sessions')
    .select(`
      *,
      exam:exams(title, total_questions, time_limit_minutes),
      class:classes(name),
      teacher:users(full_name)
    `)
    .eq('id', sessionId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .single()

  if (sessionError) {
    console.error('Error fetching exam session:', sessionError)
    return null
  }

  if (!session) return null

  // Get participants
  const { data: participants } = await supabase
    .from('exam_session_participants')
    .select(`
      *,
      student:students(full_name, english_name)
    `)
    .eq('session_id', sessionId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('invited_at', { ascending: true })

  // Get attempts
  const { data: attempts } = await supabase
    .from('student_exam_attempts')
    .select(`
      *,
      student:students(full_name, english_name)
    `)
    .eq('session_id', sessionId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('started_at', { ascending: false })

  return {
    ...session,
    participants: participants || [],
    attempts: attempts || []
  }
}

/**
 * Create a new exam session
 */
export async function createExamSession(sessionData: {
  academy_id: string
  exam_id: string
  class_id?: string
  teacher_id?: string
  title: string
  instructions?: string
  scheduled_start?: string
  scheduled_end?: string
  time_limit_override?: number
  attempts_allowed_override?: number
  allow_late_entry?: boolean
  shuffle_questions?: boolean
  require_all_students?: boolean
  session_type?: string
}): Promise<ExamSession> {
  const { data, error } = await supabase
    .from('exam_sessions')
    .insert({
      ...sessionData,
      status: 'scheduled',
      allow_late_entry: sessionData.allow_late_entry ?? true,
      shuffle_questions: sessionData.shuffle_questions ?? false,
      require_all_students: sessionData.require_all_students ?? false,
      total_invited: 0,
      total_started: 0,
      total_completed: 0
    })
    .select()
    .single()

  if (error) {
    console.error('Error creating exam session:', error)
    throw new Error(`Failed to create exam session: ${error.message}`)
  }

  return data
}

/**
 * Update exam session
 */
export async function updateExamSession(
  sessionId: string, 
  academyId: string, 
  updates: Partial<ExamSession>
): Promise<ExamSession> {
  const { data, error } = await supabase
    .from('exam_sessions')
    .update({
      ...updates,
      updated_at: new Date().toISOString()
    })
    .eq('id', sessionId)
    .eq('academy_id', academyId)
    .select()
    .single()

  if (error) {
    console.error('Error updating exam session:', error)
    throw new Error(`Failed to update exam session: ${error.message}`)
  }

  return data
}

/**
 * Start an exam session
 */
export async function startExamSession(sessionId: string, academyId: string): Promise<ExamSession> {
  const { data, error } = await supabase
    .from('exam_sessions')
    .update({
      status: 'active',
      actual_start: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
    .eq('id', sessionId)
    .eq('academy_id', academyId)
    .select()
    .single()

  if (error) {
    console.error('Error starting exam session:', error)
    throw new Error(`Failed to start exam session: ${error.message}`)
  }

  return data
}

/**
 * Pause an exam session
 */
export async function pauseExamSession(sessionId: string, academyId: string): Promise<ExamSession> {
  const { data, error } = await supabase
    .from('exam_sessions')
    .update({
      status: 'paused',
      updated_at: new Date().toISOString()
    })
    .eq('id', sessionId)
    .eq('academy_id', academyId)
    .select()
    .single()

  if (error) {
    console.error('Error pausing exam session:', error)
    throw new Error(`Failed to pause exam session: ${error.message}`)
  }

  return data
}

/**
 * End an exam session
 */
export async function endExamSession(sessionId: string, academyId: string): Promise<ExamSession> {
  const { data, error } = await supabase
    .from('exam_sessions')
    .update({
      status: 'completed',
      actual_end: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
    .eq('id', sessionId)
    .eq('academy_id', academyId)
    .select()
    .single()

  if (error) {
    console.error('Error ending exam session:', error)
    throw new Error(`Failed to end exam session: ${error.message}`)
  }

  return data
}

/**
 * Add participants to an exam session
 */
export async function addParticipantsToSession(
  sessionId: string,
  academyId: string,
  studentIds: string[]
): Promise<ExamSessionParticipant[]> {
  const participants = studentIds.map(studentId => ({
    academy_id: academyId,
    session_id: sessionId,
    student_id: studentId,
    participation_status: 'invited' as const,
    extra_time_minutes: 0
  }))

  const { data, error } = await supabase
    .from('exam_session_participants')
    .insert(participants)
    .select()

  if (error) {
    console.error('Error adding participants:', error)
    throw new Error(`Failed to add participants: ${error.message}`)
  }

  // Update session total_invited count
  await supabase
    .from('exam_sessions')
    .update({
      total_invited: studentIds.length,
      updated_at: new Date().toISOString()
    })
    .eq('id', sessionId)
    .eq('academy_id', academyId)

  return data || []
}

/**
 * Start student exam attempt
 */
export async function startStudentExamAttempt(
  sessionId: string,
  studentId: string,
  examId: string,
  academyId: string,
  participantId?: string
): Promise<StudentExamAttempt> {
  // Get exam details for attempt configuration
  const { data: exam } = await supabase
    .from('exams')
    .select('total_questions, total_points, time_limit_minutes')
    .eq('id', examId)
    .eq('academy_id', academyId)
    .single()

  if (!exam) {
    throw new Error('Exam not found')
  }

  // Check for existing attempts
  const { data: existingAttempts } = await supabase
    .from('student_exam_attempts')
    .select('attempt_number')
    .eq('student_id', studentId)
    .eq('exam_id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .order('attempt_number', { ascending: false })
    .limit(1)

  const nextAttemptNumber = existingAttempts && existingAttempts.length > 0 
    ? existingAttempts[0].attempt_number + 1 
    : 1

  const { data, error } = await supabase
    .from('student_exam_attempts')
    .insert({
      academy_id: academyId,
      student_id: studentId,
      exam_id: examId,
      session_id: sessionId,
      participant_id: participantId,
      attempt_number: nextAttemptNumber,
      total_questions: exam.total_questions,
      max_possible_score: exam.total_points,
      time_limit_seconds: exam.time_limit_minutes ? exam.time_limit_minutes * 60 : null,
      status: 'in_progress'
    })
    .select()
    .single()

  if (error) {
    console.error('Error starting student exam attempt:', error)
    throw new Error(`Failed to start exam attempt: ${error.message}`)
  }

  // Update participant status if participant_id provided
  if (participantId) {
    await supabase
      .from('exam_session_participants')
      .update({
        participation_status: 'started',
        first_accessed: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
      .eq('id', participantId)
      .eq('academy_id', academyId)
  }

  return data
}

/**
 * Get active exam sessions for a student
 */
export async function getActiveExamSessionsForStudent(
  studentId: string,
  academyId: string
): Promise<ExamSessionWithDetails[]> {
  const { data: participants, error } = await supabase
    .from('exam_session_participants')
    .select(`
      *,
      session:exam_sessions(
        *,
        exam:exams(title, total_questions, time_limit_minutes)
      )
    `)
    .eq('student_id', studentId)
    .eq('academy_id', academyId)
    .in('participation_status', ['invited', 'started', 'in_progress'])
    .is('deleted_at', null)
    .eq('is_active', true)

  if (error) {
    console.error('Error fetching active sessions for student:', error)
    throw new Error(`Failed to fetch active sessions: ${error.message}`)
  }

  return (participants || []).map(p => p.session).filter(Boolean)
}

/**
 * Get exam session statistics
 */
export async function getExamSessionStatistics(academyId: string): Promise<{
  total: number
  active: number
  scheduled: number
  completed: number
  totalParticipants: number
  averageCompletion: number
}> {
  const { data: sessions, error: sessionsError } = await supabase
    .from('exam_sessions')
    .select('status, total_invited, total_completed')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)

  if (sessionsError) {
    console.error('Error fetching session statistics:', sessionsError)
    throw new Error(`Failed to fetch session statistics: ${sessionsError.message}`)
  }

  const sessionData = sessions || []
  const totalParticipants = sessionData.reduce((sum, s) => sum + s.total_invited, 0)
  const totalCompleted = sessionData.reduce((sum, s) => sum + s.total_completed, 0)

  return {
    total: sessionData.length,
    active: sessionData.filter(s => s.status === 'active').length,
    scheduled: sessionData.filter(s => s.status === 'scheduled').length,
    completed: sessionData.filter(s => s.status === 'completed').length,
    totalParticipants,
    averageCompletion: totalParticipants > 0 ? (totalCompleted / totalParticipants) * 100 : 0
  }
}