import { markAttendance } from '@/lib/services/attendance'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * POST /api/attendance/bulk
 * Mark attendance for multiple students at once
 */
export async function POST(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Validate required fields
    if (!body.class_id || !body.class_date || !Array.isArray(body.records)) {
      return Response.json(
        { 
          error: 'Missing required fields',
          message: 'class_id, class_date, and records array are required'
        },
        { status: 400 }
      )
    }

    const results = []
    const errors = []

    // Process each attendance record
    for (const record of body.records) {
      try {
        const attendance = await markAttendance({
          academy_id: academyId,
          class_id: body.class_id,
          student_id: record.student_id,
          class_date: body.class_date,
          status: record.status,
          note: record.note || null
        })
        results.push(attendance)
      } catch (error) {
        errors.push({
          student_id: record.student_id,
          error: error instanceof Error ? error.message : 'Unknown error'
        })
      }
    }
    
    return Response.json(
      { 
        results,
        errors,
        message: `Marked attendance for ${results.length} students`,
        success: errors.length === 0
      },
      { status: errors.length > 0 ? 207 : 201 } // 207 = Multi-Status
    )
  } catch (error) {
    console.error('Error in POST /api/attendance/bulk:', error)
    
    return Response.json(
      { 
        error: 'Failed to mark bulk attendance',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}