import { withdrawEnrollment } from '@/lib/services/enrollments'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * DELETE /api/enrollments/[id]
 * Withdraw a student from a class
 */
export async function DELETE(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    
    await withdrawEnrollment(params.id, academyId)
    
    return Response.json(
      { message: 'Student withdrawn from class successfully' }
    )
  } catch (error) {
    console.error('Error in DELETE /api/enrollments/[id]:', error)
    return Response.json(
      { 
        error: 'Failed to withdraw enrollment',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}