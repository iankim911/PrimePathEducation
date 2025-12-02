/**
 * Exam Questions API Route
 * 
 * Handles question operations for specific exams
 */

import { 
  getExamQuestions, 
  createExamQuestion, 
  bulkUpsertExamQuestions,
  reorderExamQuestions,
  type ExamQuestion 
} from '@/lib/services/exams'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/exams/[id]/questions
 * 
 * Returns all questions for a specific exam
 */
export async function GET(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    
    const questions = await getExamQuestions(params.id, academyId)
    
    return Response.json({ 
      questions,
      count: questions.length
    })
  } catch (error) {
    console.error('Error in GET /api/exams/[id]/questions:', error)
    
    return Response.json(
      { 
        error: 'Failed to fetch questions',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/exams/[id]/questions
 * 
 * Creates a new question or bulk upserts multiple questions
 */
export async function POST(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Check if bulk operation
    if (Array.isArray(body.questions)) {
      // Bulk upsert
      const questions = await bulkUpsertExamQuestions(params.id, academyId, body.questions)
      
      return Response.json({ 
        questions,
        message: `${questions.length} questions processed successfully`
      })
    } else {
      // Single question creation
      const questionData: Omit<ExamQuestion, 'id' | 'created_at' | 'updated_at' | 'deleted_at'> = {
        academy_id: academyId,
        exam_id: params.id,
        section_id: body.section_id || null,
        question_number: body.question_number,
        question_text: body.question_text,
        question_type: body.question_type,
        correct_answers: body.correct_answers || null,
        answer_options: body.answer_options || null,
        points: body.points || 1,
        sort_order: body.sort_order || body.question_number,
        instructions: body.instructions || null,
        explanation: body.explanation || null,
        file_references: body.file_references || null,
        audio_start_seconds: body.audio_start_seconds || null,
        audio_end_seconds: body.audio_end_seconds || null,
        is_active: true
      }
      
      const question = await createExamQuestion(params.id, academyId, questionData)
      
      return Response.json({ 
        question,
        message: 'Question created successfully'
      }, { status: 201 })
    }
  } catch (error) {
    console.error('Error in POST /api/exams/[id]/questions:', error)
    
    return Response.json(
      { 
        error: 'Failed to create question(s)',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/exams/[id]/questions
 * 
 * Reorders questions for an exam
 */
export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const body = await request.json()
    
    if (!body.orders || !Array.isArray(body.orders)) {
      return Response.json(
        { error: 'Invalid request: orders array required' },
        { status: 400 }
      )
    }
    
    await reorderExamQuestions(params.id, academyId, body.orders)
    
    return Response.json({ 
      message: 'Questions reordered successfully'
    })
  } catch (error) {
    console.error('Error in PUT /api/exams/[id]/questions:', error)
    
    return Response.json(
      { 
        error: 'Failed to reorder questions',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}