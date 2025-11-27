import { 
  getAttendanceByClassAndDate,
  getEnrolledStudentsForAttendance,
  markAttendance,
  getClassAttendanceHistory,
  getStudentAttendanceSummary
} from '@/lib/services/attendance'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/attendance
 * Get attendance data with various filters
 */
export async function GET(request: Request) {
  try {
    const academyId = await getAcademyId()
    const { searchParams } = new URL(request.url)
    const classId = searchParams.get('class_id')
    const date = searchParams.get('date')
    const studentId = searchParams.get('student_id')
    const mode = searchParams.get('mode') // 'roster', 'history', 'summary'

    // Get student attendance summary
    if (mode === 'summary' && studentId) {
      const startDate = searchParams.get('start_date') || undefined
      const endDate = searchParams.get('end_date') || undefined
      const summary = await getStudentAttendanceSummary(
        studentId, 
        academyId,
        startDate,
        endDate
      )
      return Response.json({ summary })
    }

    // Get class attendance history
    if (mode === 'history' && classId) {
      const limit = searchParams.get('limit')
      const history = await getClassAttendanceHistory(
        classId, 
        academyId,
        limit ? parseInt(limit) : 30
      )
      return Response.json({ history })
    }

    // Get enrollment roster for taking attendance
    if (mode === 'roster' && classId && date) {
      const roster = await getEnrolledStudentsForAttendance(
        classId,
        date,
        academyId
      )
      return Response.json({ 
        roster,
        class_id: classId,
        date,
        count: roster.length 
      })
    }

    // Get attendance records for a class and date
    if (classId && date) {
      const attendance = await getAttendanceByClassAndDate(
        classId,
        date,
        academyId
      )
      return Response.json({ 
        attendance,
        count: attendance.length 
      })
    }

    return Response.json(
      { 
        error: 'Invalid parameters',
        message: 'Please provide class_id and date, or use mode parameter'
      },
      { status: 400 }
    )
  } catch (error) {
    console.error('Error in GET /api/attendance:', error)
    
    return Response.json(
      { 
        error: 'Failed to fetch attendance',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/attendance
 * Mark attendance for a student
 */
export async function POST(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Validate required fields
    if (!body.class_id || !body.student_id || !body.class_date || !body.status) {
      return Response.json(
        { 
          error: 'Missing required fields',
          message: 'class_id, student_id, class_date, and status are required'
        },
        { status: 400 }
      )
    }

    // Validate status value
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

    const attendance = await markAttendance({
      academy_id: academyId,
      class_id: body.class_id,
      student_id: body.student_id,
      class_date: body.class_date,
      status: body.status,
      note: body.note || null
    })
    
    return Response.json(
      { 
        attendance,
        message: 'Attendance marked successfully' 
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('Error in POST /api/attendance:', error)
    
    return Response.json(
      { 
        error: 'Failed to mark attendance',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/attendance/bulk
 * Mark attendance for multiple students at once
 */
export async function POST_bulk(request: Request) {
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