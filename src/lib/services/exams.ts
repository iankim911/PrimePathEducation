/**
 * Exams Service Layer
 * 
 * This service encapsulates all data access and business logic for exams.
 * Components should never directly query Supabase; they should use these service functions.
 */

import { supabase } from '@/lib/supabaseClient'

/**
 * Exam type matching the exams table in the database schema
 */
export interface Exam {
  id: string
  academy_id: string
  title: string
  description?: string | null
  exam_type_id?: string | null
  time_limit_minutes?: number | null
  attempts_allowed: number
  passing_score?: number | null
  total_questions: number
  total_points: number
  randomize_questions: boolean
  randomize_answers: boolean
  status: 'draft' | 'published' | 'archived'
  show_results: boolean
  allow_review: boolean
  require_webcam: boolean
  difficulty_level?: 'beginner' | 'intermediate' | 'advanced' | null
  subject_tags?: string[] | null
  learning_objectives?: string[] | null
  metadata?: any | null
  created_by?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Exam with related data for detailed views
 */
export interface ExamWithRelations extends Exam {
  exam_type?: ExamType | null
  questions?: ExamQuestion[]
  files?: ExamFile[]
  sessions?: ExamSession[]
  creator?: {
    id: string
    full_name: string
  } | null
}

/**
 * Exam type for categorizing exams
 */
export interface ExamType {
  id: string
  academy_id: string
  name: string
  code?: string | null
  description?: string | null
  color_hex: string
  default_time_limit?: number | null
  default_attempts_allowed: number
  default_passing_score?: number | null
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Exam question interface
 */
export interface ExamQuestion {
  id: string
  academy_id: string
  exam_id: string
  section_id?: string | null
  question_number: number
  question_text: string
  question_type: 'multiple_choice' | 'multiple_select' | 'short_answer' | 'long_answer' | 'true_false' | 'fill_blank'
  correct_answers?: string[] | null
  answer_options?: any | null
  points: number
  sort_order: number
  instructions?: string | null
  explanation?: string | null
  file_references?: string[] | null
  audio_start_seconds?: number | null
  audio_end_seconds?: number | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Exam file interface
 */
export interface ExamFile {
  id: string
  academy_id: string
  exam_id?: string | null
  section_id?: string | null
  filename: string
  original_filename: string
  file_path: string
  file_type: 'pdf' | 'image' | 'audio'
  mime_type: string
  file_size_bytes: number
  title?: string | null
  description?: string | null
  sort_order: number
  rotation_degrees: number
  zoom_level: number
  ocr_text?: string | null
  audio_duration_seconds?: number | null
  audio_transcript?: string | null
  processing_status: string
  metadata?: any | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Exam session interface
 */
export interface ExamSession {
  id: string
  academy_id: string
  exam_id: string
  class_id?: string | null
  teacher_id?: string | null
  title: string
  instructions?: string | null
  scheduled_start?: string | null
  scheduled_end?: string | null
  actual_start?: string | null
  actual_end?: string | null
  time_limit_override?: number | null
  attempts_allowed_override?: number | null
  allow_late_entry: boolean
  shuffle_questions: boolean
  require_all_students: boolean
  status: 'scheduled' | 'active' | 'paused' | 'completed' | 'cancelled'
  total_invited: number
  total_started: number
  total_completed: number
  average_score?: number | null
  session_type?: string | null
  metadata?: any | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Get all exams for an academy
 */
export async function getAllExamsByAcademy(academyId: string): Promise<Exam[]> {
  const { data, error } = await supabase
    .from('exams')
    .select('*')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('title', { ascending: true })

  if (error) {
    console.error('Error fetching exams:', error)
    throw new Error(`Failed to fetch exams: ${error.message}`)
  }

  return data || []
}

/**
 * Get exam by ID
 */
export async function getExamById(examId: string, academyId: string): Promise<Exam | null> {
  const { data, error } = await supabase
    .from('exams')
    .select('*')
    .eq('id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .single()

  if (error) {
    console.error('Error fetching exam:', error)
    return null
  }

  return data
}

/**
 * Get exam with all related data
 */
export async function getExamWithRelations(examId: string, academyId: string): Promise<ExamWithRelations | null> {
  const { data: exam, error: examError } = await supabase
    .from('exams')
    .select(`
      *,
      exam_type:exam_types(*),
      creator:users(id, full_name)
    `)
    .eq('id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .single()

  if (examError) {
    console.error('Error fetching exam with relations:', examError)
    return null
  }

  if (!exam) return null

  // Get questions
  const { data: questions } = await supabase
    .from('exam_questions')
    .select('*')
    .eq('exam_id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('sort_order', { ascending: true })

  // Get files
  const { data: files } = await supabase
    .from('exam_files')
    .select('*')
    .eq('exam_id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('sort_order', { ascending: true })

  // Get recent sessions
  const { data: sessions } = await supabase
    .from('exam_sessions')
    .select('*')
    .eq('exam_id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('created_at', { ascending: false })
    .limit(5)

  return {
    ...exam,
    questions: questions || [],
    files: files || [],
    sessions: sessions || []
  }
}

/**
 * Create a new exam
 */
export async function createExam(examData: Omit<Exam, 'id' | 'total_questions' | 'total_points' | 'created_at' | 'updated_at' | 'deleted_at'>): Promise<Exam> {
  const { data, error } = await supabase
    .from('exams')
    .insert({
      ...examData,
      total_questions: 0, // Will be updated by triggers when questions are added
      total_points: 0,    // Will be updated by triggers when questions are added
    })
    .select()
    .single()

  if (error) {
    console.error('Error creating exam:', error)
    throw new Error(`Failed to create exam: ${error.message}`)
  }

  return data
}

/**
 * Update an exam
 */
export async function updateExam(examId: string, academyId: string, updates: Partial<Exam>): Promise<Exam> {
  const { data, error } = await supabase
    .from('exams')
    .update({
      ...updates,
      updated_at: new Date().toISOString()
    })
    .eq('id', examId)
    .eq('academy_id', academyId)
    .select()
    .single()

  if (error) {
    console.error('Error updating exam:', error)
    throw new Error(`Failed to update exam: ${error.message}`)
  }

  return data
}

/**
 * Delete an exam (soft delete)
 */
export async function deleteExam(examId: string, academyId: string): Promise<void> {
  const { error } = await supabase
    .from('exams')
    .update({
      deleted_at: new Date().toISOString(),
      is_active: false,
      updated_at: new Date().toISOString()
    })
    .eq('id', examId)
    .eq('academy_id', academyId)

  if (error) {
    console.error('Error deleting exam:', error)
    throw new Error(`Failed to delete exam: ${error.message}`)
  }
}

/**
 * Duplicate an exam
 */
export async function duplicateExam(examId: string, academyId: string, newTitle?: string): Promise<Exam> {
  // Get the original exam
  const originalExam = await getExamWithRelations(examId, academyId)
  if (!originalExam) {
    throw new Error('Exam not found')
  }

  // Create new exam
  const { data: newExam, error } = await supabase
    .from('exams')
    .insert({
      academy_id: academyId,
      title: newTitle || `${originalExam.title} (Copy)`,
      description: originalExam.description,
      exam_type_id: originalExam.exam_type_id,
      time_limit_minutes: originalExam.time_limit_minutes,
      attempts_allowed: originalExam.attempts_allowed,
      passing_score: originalExam.passing_score,
      randomize_questions: originalExam.randomize_questions,
      randomize_answers: originalExam.randomize_answers,
      status: 'draft', // Always start as draft
      show_results: originalExam.show_results,
      allow_review: originalExam.allow_review,
      require_webcam: originalExam.require_webcam,
      difficulty_level: originalExam.difficulty_level,
      subject_tags: originalExam.subject_tags,
      learning_objectives: originalExam.learning_objectives,
      metadata: originalExam.metadata,
      created_by: originalExam.created_by,
      is_active: true,
      total_questions: 0,
      total_points: 0
    })
    .select()
    .single()

  if (error) {
    console.error('Error duplicating exam:', error)
    throw new Error(`Failed to duplicate exam: ${error.message}`)
  }

  // TODO: Copy questions, files, and sections in a transaction
  // This would be implemented in the next phase

  return newExam
}

/**
 * Get all exam types for an academy
 */
export async function getAllExamTypesByAcademy(academyId: string): Promise<ExamType[]> {
  const { data, error } = await supabase
    .from('exam_types')
    .select('*')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('sort_order', { ascending: true })

  if (error) {
    console.error('Error fetching exam types:', error)
    throw new Error(`Failed to fetch exam types: ${error.message}`)
  }

  return data || []
}

/**
 * Create a new exam type
 */
export async function createExamType(examTypeData: Omit<ExamType, 'id' | 'created_at' | 'updated_at' | 'deleted_at'>): Promise<ExamType> {
  const { data, error } = await supabase
    .from('exam_types')
    .insert(examTypeData)
    .select()
    .single()

  if (error) {
    console.error('Error creating exam type:', error)
    throw new Error(`Failed to create exam type: ${error.message}`)
  }

  return data
}

/**
 * Get exams by status for an academy
 */
export async function getExamsByStatus(academyId: string, status: Exam['status']): Promise<Exam[]> {
  const { data, error } = await supabase
    .from('exams')
    .select('*')
    .eq('academy_id', academyId)
    .eq('status', status)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('updated_at', { ascending: false })

  if (error) {
    console.error('Error fetching exams by status:', error)
    throw new Error(`Failed to fetch exams by status: ${error.message}`)
  }

  return data || []
}

/**
 * Search exams by title
 */
export async function searchExamsByTitle(academyId: string, searchTerm: string): Promise<Exam[]> {
  const { data, error } = await supabase
    .from('exams')
    .select('*')
    .eq('academy_id', academyId)
    .ilike('title', `%${searchTerm}%`)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('title', { ascending: true })
    .limit(50)

  if (error) {
    console.error('Error searching exams:', error)
    throw new Error(`Failed to search exams: ${error.message}`)
  }

  return data || []
}

/**
 * Get exam statistics for an academy
 */
export async function getExamStatistics(academyId: string): Promise<{
  total: number
  published: number
  draft: number
  archived: number
  recentActivity: number
}> {
  const { data, error } = await supabase
    .from('exams')
    .select('status, created_at')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)

  if (error) {
    console.error('Error fetching exam statistics:', error)
    throw new Error(`Failed to fetch exam statistics: ${error.message}`)
  }

  const exams = data || []
  const now = new Date()
  const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)

  return {
    total: exams.length,
    published: exams.filter(e => e.status === 'published').length,
    draft: exams.filter(e => e.status === 'draft').length,
    archived: exams.filter(e => e.status === 'archived').length,
    recentActivity: exams.filter(e => new Date(e.created_at) > sevenDaysAgo).length
  }
}

/**
 * Question CRUD operations
 */

/**
 * Get all questions for an exam
 */
export async function getExamQuestions(examId: string, academyId: string): Promise<ExamQuestion[]> {
  const { data, error } = await supabase
    .from('exam_questions')
    .select('*')
    .eq('exam_id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('sort_order', { ascending: true })

  if (error) {
    console.error('Error fetching exam questions:', error)
    throw new Error(`Failed to fetch exam questions: ${error.message}`)
  }

  return data || []
}

/**
 * Create a new question
 */
export async function createExamQuestion(
  examId: string, 
  academyId: string, 
  questionData: Omit<ExamQuestion, 'id' | 'created_at' | 'updated_at' | 'deleted_at'>
): Promise<ExamQuestion> {
  const { data, error } = await supabase
    .from('exam_questions')
    .insert({
      ...questionData,
      exam_id: examId,
      academy_id: academyId,
      is_active: true
    })
    .select()
    .single()

  if (error) {
    console.error('Error creating exam question:', error)
    throw new Error(`Failed to create exam question: ${error.message}`)
  }

  // Update exam totals
  await updateExamTotals(examId, academyId)

  return data
}

/**
 * Update an existing question
 */
export async function updateExamQuestion(
  questionId: string,
  academyId: string,
  updates: Partial<ExamQuestion>
): Promise<ExamQuestion> {
  const { data, error } = await supabase
    .from('exam_questions')
    .update({
      ...updates,
      updated_at: new Date().toISOString()
    })
    .eq('id', questionId)
    .eq('academy_id', academyId)
    .select()
    .single()

  if (error) {
    console.error('Error updating exam question:', error)
    throw new Error(`Failed to update exam question: ${error.message}`)
  }

  // Update exam totals if points changed
  if (updates.points !== undefined || updates.exam_id) {
    const examId = updates.exam_id || data.exam_id
    await updateExamTotals(examId, academyId)
  }

  return data
}

/**
 * Delete a question (soft delete)
 */
export async function deleteExamQuestion(questionId: string, academyId: string): Promise<void> {
  // Get the question to find the exam ID
  const { data: question } = await supabase
    .from('exam_questions')
    .select('exam_id')
    .eq('id', questionId)
    .eq('academy_id', academyId)
    .single()

  const { error } = await supabase
    .from('exam_questions')
    .update({
      deleted_at: new Date().toISOString(),
      is_active: false,
      updated_at: new Date().toISOString()
    })
    .eq('id', questionId)
    .eq('academy_id', academyId)

  if (error) {
    console.error('Error deleting exam question:', error)
    throw new Error(`Failed to delete exam question: ${error.message}`)
  }

  // Update exam totals
  if (question?.exam_id) {
    await updateExamTotals(question.exam_id, academyId)
  }
}

/**
 * Bulk upsert questions for an exam
 */
export async function bulkUpsertExamQuestions(
  examId: string,
  academyId: string,
  questions: Partial<ExamQuestion>[]
): Promise<ExamQuestion[]> {
  const questionsWithDefaults = questions.map(q => ({
    ...q,
    exam_id: examId,
    academy_id: academyId,
    is_active: true,
    updated_at: new Date().toISOString()
  }))

  const { data, error } = await supabase
    .from('exam_questions')
    .upsert(questionsWithDefaults, { onConflict: 'id' })
    .select()

  if (error) {
    console.error('Error bulk upserting exam questions:', error)
    throw new Error(`Failed to bulk upsert exam questions: ${error.message}`)
  }

  // Update exam totals
  await updateExamTotals(examId, academyId)

  return data || []
}

/**
 * Reorder questions
 */
export async function reorderExamQuestions(
  examId: string,
  academyId: string,
  questionOrders: { id: string; sort_order: number }[]
): Promise<void> {
  // Update each question's sort order
  const updates = questionOrders.map(({ id, sort_order }) => 
    supabase
      .from('exam_questions')
      .update({ 
        sort_order, 
        updated_at: new Date().toISOString() 
      })
      .eq('id', id)
      .eq('exam_id', examId)
      .eq('academy_id', academyId)
  )

  await Promise.all(updates)
}

/**
 * Update exam totals (question count and total points)
 */
async function updateExamTotals(examId: string, academyId: string): Promise<void> {
  // Get all active questions for the exam
  const { data: questions } = await supabase
    .from('exam_questions')
    .select('points')
    .eq('exam_id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)

  const total_questions = questions?.length || 0
  const total_points = questions?.reduce((sum, q) => sum + (q.points || 0), 0) || 0

  // Update the exam with new totals
  await supabase
    .from('exams')
    .update({
      total_questions,
      total_points,
      updated_at: new Date().toISOString()
    })
    .eq('id', examId)
    .eq('academy_id', academyId)
}