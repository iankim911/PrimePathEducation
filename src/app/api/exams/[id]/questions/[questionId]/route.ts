/**
 * Individual Question API Route
 * 
 * Handles operations on specific questions
 */

import { updateExamQuestion, deleteExamQuestion } from '@/lib/services/exams'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * PUT /api/exams/[id]/questions/[questionId]
 * 
 * Updates a specific question
 */
export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string; questionId: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Remove fields that shouldn't be updated
    const { 
      id, 
      academy_id, 
      exam_id,
      created_at, 
      updated_at, 
      deleted_at,
      ...updateData 
    } = body
    
    const question = await updateExamQuestion(params.questionId, academyId, updateData)
    
    return Response.json({ 
      question,
      message: 'Question updated successfully'
    })
  } catch (error) {
    console.error('Error in PUT /api/exams/[id]/questions/[questionId]:', error)
    
    return Response.json(
      { 
        error: 'Failed to update question',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/exams/[id]/questions/[questionId]
 * 
 * Deletes a specific question (soft delete)
 */
export async function DELETE(
  request: Request,
  context: { params: Promise<{ id: string; questionId: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    
    await deleteExamQuestion(params.questionId, academyId)
    
    return Response.json({ 
      message: 'Question deleted successfully'
    })
  } catch (error) {
    console.error('Error in DELETE /api/exams/[id]/questions/[questionId]:', error)
    
    return Response.json(
      { 
        error: 'Failed to delete question',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}