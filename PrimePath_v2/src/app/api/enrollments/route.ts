import { 
  listEnrollmentsByAcademy, 
  createEnrollment,
  getEnrollmentsByStudent,
  getEnrollmentsByClass,
  getAvailableStudentsForClass
} from '@/lib/services/enrollments'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/enrollments
 * Get enrollments with optional filters
 */
export async function GET(request: Request) {
  try {
    const academyId = await getAcademyId()
    const { searchParams } = new URL(request.url)
    const studentId = searchParams.get('student_id')
    const classId = searchParams.get('class_id')
    const available = searchParams.get('available')

    // If looking for available students for a class
    if (available === 'true' && classId) {
      const students = await getAvailableStudentsForClass(classId, academyId)
      return Response.json({ 
        students,
        count: students.length 
      })
    }

    // Get enrollments by student
    if (studentId) {
      const enrollments = await getEnrollmentsByStudent(studentId, academyId)
      return Response.json({ 
        enrollments,
        count: enrollments.length 
      })
    }

    // Get enrollments by class
    if (classId) {
      const enrollments = await getEnrollmentsByClass(classId, academyId)
      return Response.json({ 
        enrollments,
        count: enrollments.length 
      })
    }

    // Get all enrollments
    const enrollments = await listEnrollmentsByAcademy(academyId)
    
    return Response.json({ 
      enrollments,
      academy_id: academyId,
      count: enrollments.length 
    })
  } catch (error) {
    console.error('Error in GET /api/enrollments:', error)
    
    return Response.json(
      { 
        error: 'Failed to fetch enrollments',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/enrollments
 * Create a new enrollment
 */
export async function POST(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    if (!body.student_id || !body.class_id) {
      return Response.json(
        { 
          error: 'Missing required fields',
          message: 'student_id and class_id are required'
        },
        { status: 400 }
      )
    }

    const enrollment = await createEnrollment({
      academy_id: academyId,
      student_id: body.student_id,
      class_id: body.class_id,
      start_date: body.start_date || new Date().toISOString().split('T')[0]
    })
    
    return Response.json(
      { 
        enrollment,
        message: 'Student enrolled successfully' 
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('Error in POST /api/enrollments:', error)
    
    // Check if it's a duplicate enrollment error
    if (error instanceof Error && error.message.includes('already enrolled')) {
      return Response.json(
        { 
          error: 'Duplicate enrollment',
          message: error.message
        },
        { status: 409 }
      )
    }
    
    return Response.json(
      { 
        error: 'Failed to create enrollment',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}