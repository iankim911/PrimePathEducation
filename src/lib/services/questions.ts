/**
 * Questions Service Layer
 * 
 * This service handles exam questions, answers, and question management.
 * Components should use these service functions for all question operations.
 */

import { supabase } from '@/lib/supabaseClient'
import { ExamQuestion } from './exams'

/**
 * Student answer interface
 */
export interface StudentAnswer {
  id: string
  academy_id: string
  attempt_id: string
  question_id: string
  answer_text?: string | null
  selected_options?: number[] | null
  is_flagged: boolean
  answered_at: string
  time_spent_seconds?: number | null
  is_correct?: boolean | null
  points_earned: number
  points_possible: number
  manual_override: boolean
  teacher_feedback?: string | null
  graded_by?: string | null
  graded_at?: string | null
  confidence_level?: number | null
  difficulty_perceived?: string | null
  answer_pattern?: string | null
  keystroke_data?: any | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Question with student response (for exam taking)
 */
export interface QuestionWithResponse extends ExamQuestion {
  student_answer?: StudentAnswer | null
  files?: {
    id: string
    file_path: string
    file_type: string
    title?: string
  }[]
}

/**
 * Get all questions for an exam
 */
export async function getQuestionsByExam(examId: string, academyId: string): Promise<ExamQuestion[]> {
  const { data, error } = await supabase
    .from('exam_questions')
    .select('*')
    .eq('exam_id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('sort_order', { ascending: true })

  if (error) {
    console.error('Error fetching questions:', error)
    throw new Error(`Failed to fetch questions: ${error.message}`)
  }

  return data || []
}

/**
 * Get questions for student exam attempt with any existing answers
 */
export async function getQuestionsForAttempt(
  examId: string, 
  attemptId: string,
  academyId: string
): Promise<QuestionWithResponse[]> {
  const { data: questions, error: questionsError } = await supabase
    .from('exam_questions')
    .select('*')
    .eq('exam_id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('sort_order', { ascending: true })

  if (questionsError) {
    console.error('Error fetching questions for attempt:', questionsError)
    throw new Error(`Failed to fetch questions: ${questionsError.message}`)
  }

  if (!questions || questions.length === 0) {
    return []
  }

  // Get any existing answers for this attempt
  const questionIds = questions.map(q => q.id)
  const { data: answers } = await supabase
    .from('student_answers')
    .select('*')
    .eq('attempt_id', attemptId)
    .eq('academy_id', academyId)
    .in('question_id', questionIds)
    .is('deleted_at', null)
    .eq('is_active', true)

  // Get file references for questions
  const fileReferences = questions
    .filter(q => q.file_references && q.file_references.length > 0)
    .flatMap(q => q.file_references || [])

  let filesData: any[] = []
  if (fileReferences.length > 0) {
    const { data: files } = await supabase
      .from('exam_files')
      .select('id, file_path, file_type, title')
      .in('id', fileReferences)
      .eq('academy_id', academyId)
      .is('deleted_at', null)
      .eq('is_active', true)

    filesData = files || []
  }

  // Map questions with answers and files
  return questions.map(question => {
    const studentAnswer = answers?.find(a => a.question_id === question.id) || null
    const questionFiles = filesData.filter(f => 
      question.file_references?.includes(f.id)
    )

    return {
      ...question,
      student_answer: studentAnswer,
      files: questionFiles
    }
  })
}

/**
 * Create a new question
 */
export async function createQuestion(questionData: {
  academy_id: string
  exam_id: string
  section_id?: string
  question_text: string
  question_type: ExamQuestion['question_type']
  correct_answers?: string[]
  answer_options?: any
  points?: number
  instructions?: string
  explanation?: string
  file_references?: string[]
  audio_start_seconds?: number
  audio_end_seconds?: number
}): Promise<ExamQuestion> {
  // Get the next question number and sort order
  const { data: existingQuestions } = await supabase
    .from('exam_questions')
    .select('question_number, sort_order')
    .eq('exam_id', questionData.exam_id)
    .eq('academy_id', questionData.academy_id)
    .is('deleted_at', null)
    .order('question_number', { ascending: false })
    .limit(1)

  const nextQuestionNumber = existingQuestions && existingQuestions.length > 0
    ? existingQuestions[0].question_number + 1
    : 1

  const nextSortOrder = existingQuestions && existingQuestions.length > 0
    ? existingQuestions[0].sort_order + 1
    : 1

  const { data, error } = await supabase
    .from('exam_questions')
    .insert({
      ...questionData,
      question_number: nextQuestionNumber,
      sort_order: nextSortOrder,
      points: questionData.points || 1
    })
    .select()
    .single()

  if (error) {
    console.error('Error creating question:', error)
    throw new Error(`Failed to create question: ${error.message}`)
  }

  return data
}

/**
 * Update a question
 */
export async function updateQuestion(
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
    console.error('Error updating question:', error)
    throw new Error(`Failed to update question: ${error.message}`)
  }

  return data
}

/**
 * Delete a question (soft delete)
 */
export async function deleteQuestion(questionId: string, academyId: string): Promise<void> {
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
    console.error('Error deleting question:', error)
    throw new Error(`Failed to delete question: ${error.message}`)
  }
}

/**
 * Reorder questions in an exam
 */
export async function reorderQuestions(
  examId: string,
  academyId: string,
  questionOrders: { questionId: string; sortOrder: number; questionNumber: number }[]
): Promise<void> {
  // Update each question's order
  const updatePromises = questionOrders.map(({ questionId, sortOrder, questionNumber }) =>
    supabase
      .from('exam_questions')
      .update({
        sort_order: sortOrder,
        question_number: questionNumber,
        updated_at: new Date().toISOString()
      })
      .eq('id', questionId)
      .eq('academy_id', academyId)
  )

  const results = await Promise.allSettled(updatePromises)
  
  const failed = results.filter(r => r.status === 'rejected')
  if (failed.length > 0) {
    console.error('Error reordering questions:', failed)
    throw new Error('Failed to reorder some questions')
  }
}

/**
 * Bulk create questions
 */
export async function bulkCreateQuestions(
  examId: string,
  academyId: string,
  questionsData: Array<{
    question_text: string
    question_type: ExamQuestion['question_type']
    correct_answers?: string[]
    answer_options?: any
    points?: number
    instructions?: string
    explanation?: string
  }>
): Promise<ExamQuestion[]> {
  // Get the current max question number
  const { data: existingQuestions } = await supabase
    .from('exam_questions')
    .select('question_number, sort_order')
    .eq('exam_id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .order('question_number', { ascending: false })
    .limit(1)

  const startQuestionNumber = existingQuestions && existingQuestions.length > 0
    ? existingQuestions[0].question_number + 1
    : 1

  const startSortOrder = existingQuestions && existingQuestions.length > 0
    ? existingQuestions[0].sort_order + 1
    : 1

  // Prepare questions with proper numbering
  const questionsToInsert = questionsData.map((question, index) => ({
    academy_id: academyId,
    exam_id: examId,
    ...question,
    question_number: startQuestionNumber + index,
    sort_order: startSortOrder + index,
    points: question.points || 1
  }))

  const { data, error } = await supabase
    .from('exam_questions')
    .insert(questionsToInsert)
    .select()

  if (error) {
    console.error('Error bulk creating questions:', error)
    throw new Error(`Failed to bulk create questions: ${error.message}`)
  }

  return data || []
}

/**
 * Submit student answer
 */
export async function submitStudentAnswer(answerData: {
  academy_id: string
  attempt_id: string
  question_id: string
  answer_text?: string
  selected_options?: number[]
  time_spent_seconds?: number
  confidence_level?: number
}): Promise<StudentAnswer> {
  // Get question details for grading
  const { data: question } = await supabase
    .from('exam_questions')
    .select('*')
    .eq('id', answerData.question_id)
    .eq('academy_id', answerData.academy_id)
    .single()

  if (!question) {
    throw new Error('Question not found')
  }

  // Auto-grade if possible
  let isCorrect: boolean | null = null
  let pointsEarned = 0

  if (question.question_type === 'multiple_choice' && answerData.selected_options && question.correct_answers) {
    // For multiple choice, check if the selected option matches
    const selectedOption = answerData.selected_options[0]
    const correctAnswerIndex = parseInt(question.correct_answers[0])
    isCorrect = selectedOption === correctAnswerIndex
    pointsEarned = isCorrect ? question.points : 0
  } else if (question.question_type === 'multiple_select' && answerData.selected_options && question.correct_answers) {
    // For multiple select, check if all correct options are selected
    const selectedSet = new Set(answerData.selected_options)
    const correctSet = new Set(question.correct_answers.map((a: string) => parseInt(a)))
    
    isCorrect = selectedSet.size === correctSet.size && 
      Array.from(selectedSet).every(option => correctSet.has(option))
    pointsEarned = isCorrect ? question.points : 0
  } else if (question.question_type === 'true_false' && answerData.answer_text && question.correct_answers) {
    // For true/false, compare text answer
    isCorrect = answerData.answer_text.toLowerCase() === question.correct_answers[0].toLowerCase()
    pointsEarned = isCorrect ? question.points : 0
  }
  // For short_answer, long_answer, and fill_blank, manual grading is required

  // Check if answer already exists (for updates)
  const { data: existingAnswer } = await supabase
    .from('student_answers')
    .select('id')
    .eq('attempt_id', answerData.attempt_id)
    .eq('question_id', answerData.question_id)
    .eq('academy_id', answerData.academy_id)
    .is('deleted_at', null)
    .single()

  const answerPayload = {
    academy_id: answerData.academy_id,
    attempt_id: answerData.attempt_id,
    question_id: answerData.question_id,
    answer_text: answerData.answer_text || null,
    selected_options: answerData.selected_options || null,
    time_spent_seconds: answerData.time_spent_seconds,
    is_correct: isCorrect,
    points_earned: pointsEarned,
    points_possible: question.points,
    confidence_level: answerData.confidence_level,
    answered_at: new Date().toISOString()
  }

  if (existingAnswer) {
    // Update existing answer
    const { data, error } = await supabase
      .from('student_answers')
      .update({
        ...answerPayload,
        updated_at: new Date().toISOString()
      })
      .eq('id', existingAnswer.id)
      .select()
      .single()

    if (error) {
      console.error('Error updating student answer:', error)
      throw new Error(`Failed to update answer: ${error.message}`)
    }

    return data
  } else {
    // Create new answer
    const { data, error } = await supabase
      .from('student_answers')
      .insert(answerPayload)
      .select()
      .single()

    if (error) {
      console.error('Error creating student answer:', error)
      throw new Error(`Failed to submit answer: ${error.message}`)
    }

    return data
  }
}

/**
 * Get question statistics for an exam
 */
export async function getQuestionStatistics(
  examId: string,
  academyId: string
): Promise<Array<{
  question_id: string
  question_number: number
  question_text: string
  total_responses: number
  correct_responses: number
  incorrect_responses: number
  accuracy_rate: number
  average_time_spent: number
}>> {
  const { data: questions, error: questionsError } = await supabase
    .from('exam_questions')
    .select('id, question_number, question_text, points')
    .eq('exam_id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('sort_order', { ascending: true })

  if (questionsError) {
    console.error('Error fetching questions for statistics:', questionsError)
    throw new Error(`Failed to fetch questions: ${questionsError.message}`)
  }

  if (!questions || questions.length === 0) {
    return []
  }

  // Get answer statistics for each question
  const statisticsPromises = questions.map(async (question) => {
    const { data: answers } = await supabase
      .from('student_answers')
      .select('is_correct, time_spent_seconds')
      .eq('question_id', question.id)
      .eq('academy_id', academyId)
      .is('deleted_at', null)
      .eq('is_active', true)

    const answerData = answers || []
    const totalResponses = answerData.length
    const correctResponses = answerData.filter(a => a.is_correct === true).length
    const incorrectResponses = answerData.filter(a => a.is_correct === false).length
    const accuracyRate = totalResponses > 0 ? (correctResponses / totalResponses) * 100 : 0

    const timesWithData = answerData
      .filter(a => a.time_spent_seconds !== null)
      .map(a => a.time_spent_seconds)
    
    const averageTimeSpent = timesWithData.length > 0
      ? timesWithData.reduce((sum, time) => sum + time, 0) / timesWithData.length
      : 0

    return {
      question_id: question.id,
      question_number: question.question_number,
      question_text: question.question_text,
      total_responses: totalResponses,
      correct_responses: correctResponses,
      incorrect_responses: incorrectResponses,
      accuracy_rate: accuracyRate,
      average_time_spent: averageTimeSpent
    }
  })

  return Promise.all(statisticsPromises)
}