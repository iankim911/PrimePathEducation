/**
 * Individual Exam API Route
 * 
 * Handles operations on specific exams by ID.
 */

import { getExamById, getExamWithRelations, updateExam, deleteExam, type Exam } from '@/lib/services/exams'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/exams/[id]
 * 
 * Returns a specific exam with all related data.
 */
export async function GET(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    
    // Get detailed exam data with relations
    const exam = await getExamWithRelations(params.id, academyId)
    
    if (!exam) {
      return Response.json(
        { error: 'Exam not found' },
        { status: 404 }
      )
    }
    
    return Response.json({ exam })
  } catch (error) {
    console.error('Error in GET /api/exams/[id]:', error)
    
    return Response.json(
      { 
        error: 'Failed to fetch exam',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/exams/[id]
 * 
 * Updates a specific exam.
 */
export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Prepare update data
    const updates: Partial<Exam> = {}
    
    // Only update fields that are provided
    if (body.title !== undefined) updates.title = body.title
    if (body.description !== undefined) updates.description = body.description
    if (body.exam_type_id !== undefined) updates.exam_type_id = body.exam_type_id
    if (body.time_limit_minutes !== undefined) updates.time_limit_minutes = body.time_limit_minutes
    if (body.attempts_allowed !== undefined) updates.attempts_allowed = body.attempts_allowed
    if (body.passing_score !== undefined) updates.passing_score = body.passing_score
    if (body.randomize_questions !== undefined) updates.randomize_questions = body.randomize_questions
    if (body.randomize_answers !== undefined) updates.randomize_answers = body.randomize_answers
    if (body.status !== undefined) updates.status = body.status
    if (body.show_results !== undefined) updates.show_results = body.show_results
    if (body.allow_review !== undefined) updates.allow_review = body.allow_review
    if (body.require_webcam !== undefined) updates.require_webcam = body.require_webcam
    if (body.difficulty_level !== undefined) updates.difficulty_level = body.difficulty_level
    if (body.subject_tags !== undefined) updates.subject_tags = body.subject_tags
    if (body.learning_objectives !== undefined) updates.learning_objectives = body.learning_objectives
    if (body.metadata !== undefined) updates.metadata = body.metadata
    
    // Call service layer to update exam
    const updatedExam = await updateExam(params.id, academyId, updates)
    
    return Response.json(
      { 
        exam: updatedExam,
        message: 'Exam updated successfully' 
      }
    )
  } catch (error) {
    console.error('Error in PUT /api/exams/[id]:', error)
    
    return Response.json(
      { 
        error: 'Failed to update exam',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/exams/[id]
 * 
 * Deletes a specific exam (soft delete).
 */
export async function DELETE(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    
    // Call service layer to delete exam
    await deleteExam(params.id, academyId)
    
    return Response.json(
      { message: 'Exam deleted successfully' }
    )
  } catch (error) {
    console.error('Error in DELETE /api/exams/[id]:', error)
    
    return Response.json(
      { 
        error: 'Failed to delete exam',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}