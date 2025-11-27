/**
 * Students API Route
 * 
 * IMPORTANT: API routes must be "thin" - they are just the HTTP layer.
 * - Always call service-layer functions for business logic
 * - Never talk to Supabase directly from API routes
 * - Keep routes focused on HTTP concerns (parsing params, returning responses)
 */

import { listStudentsByAcademy, createStudent, type Student } from '@/lib/services/students'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/students
 * 
 * Returns a list of all students for the current academy.
 * In production, academy_id would be determined from the authenticated user's session.
 */
export async function GET() {
  try {
    const academyId = await getAcademyId()
    
    // Call service layer function - all business logic lives there
    const students = await listStudentsByAcademy(academyId)
    
    // Return the data as JSON
    return Response.json({ 
      students,
      academy_id: academyId,
      count: students.length 
    })
  } catch (error) {
    console.error('Error in GET /api/students:', error)
    
    // Return error response
    return Response.json(
      { 
        error: 'Failed to fetch students',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/students
 * 
 * Creates a new student for the current academy.
 */
export async function POST(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Prepare student data
    const studentData: Omit<Student, 'id' | 'created_at' | 'updated_at' | 'deleted_at'> = {
      academy_id: academyId,
      full_name: body.full_name,
      english_name: body.english_name || null,
      student_code: body.student_code || null,
      school_name: body.school_name || null,
      grade: body.grade || null,
      status: body.status || 'active',
      parent_name: body.parent_name || null,
      parent_phone: body.parent_phone || null,
      is_active: true
    }
    
    // Call service layer to create student
    const newStudent = await createStudent(studentData)
    
    return Response.json(
      { 
        student: newStudent,
        message: 'Student created successfully' 
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('Error in POST /api/students:', error)
    
    return Response.json(
      { 
        error: 'Failed to create student',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}