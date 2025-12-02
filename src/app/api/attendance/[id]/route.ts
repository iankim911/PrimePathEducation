import { updateAttendance, deleteAttendance } from '@/lib/services/attendance'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * PUT /api/attendance/[id]
 * Update an attendance record
 */
export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Validate status if provided
    if (body.status) {
      const validStatuses = ['present', 'absent', 'late', 'excused']
      if (!validStatuses.includes(body.status)) {
        return Response.json(
          { 
            error: 'Invalid status',
            message: `Status must be one of: ${validStatuses.join(', ')}`
          },
          { status: 400 }
        )
      }
    }
    
    const attendance = await updateAttendance(params.id, academyId, {
      status: body.status,
      note: body.note
    })
    
    return Response.json(
      { 
        attendance,
        message: 'Attendance updated successfully' 
      }
    )
  } catch (error) {
    console.error('Error in PUT /api/attendance/[id]:', error)
    return Response.json(
      { 
        error: 'Failed to update attendance',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/attendance/[id]
 * Delete an attendance record
 */
export async function DELETE(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    
    await deleteAttendance(params.id, academyId)
    
    return Response.json(
      { message: 'Attendance record deleted successfully' }
    )
  } catch (error) {
    console.error('Error in DELETE /api/attendance/[id]:', error)
    return Response.json(
      { 
        error: 'Failed to delete attendance',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}