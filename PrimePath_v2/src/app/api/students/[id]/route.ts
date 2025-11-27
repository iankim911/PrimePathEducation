import { updateStudent, deleteStudent, getStudentById, type Student } from '@/lib/services/students'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/students/[id]
 * Get a single student by ID
 */
export async function GET(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const student = await getStudentById(params.id, academyId)
    
    if (!student) {
      return Response.json(
        { error: 'Student not found' },
        { status: 404 }
      )
    }
    
    return Response.json({ student })
  } catch (error) {
    console.error('Error in GET /api/students/[id]:', error)
    return Response.json(
      { 
        error: 'Failed to fetch student',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/students/[id]
 * Update a student
 */
export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const body = await request.json()
    
    const updates: Partial<Student> = {
      full_name: body.full_name,
      english_name: body.english_name || null,
      student_code: body.student_code || null,
      school_name: body.school_name || null,
      grade: body.grade || null,
      status: body.status || 'active',
      parent_name: body.parent_name || null,
      parent_phone: body.parent_phone || null,
    }
    
    const updatedStudent = await updateStudent(params.id, academyId, updates)
    
    return Response.json(
      { 
        student: updatedStudent,
        message: 'Student updated successfully' 
      }
    )
  } catch (error) {
    console.error('Error in PUT /api/students/[id]:', error)
    return Response.json(
      { 
        error: 'Failed to update student',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/students/[id]
 * Soft delete a student
 */
export async function DELETE(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    await deleteStudent(params.id, academyId)
    
    return Response.json(
      { message: 'Student deleted successfully' }
    )
  } catch (error) {
    console.error('Error in DELETE /api/students/[id]:', error)
    return Response.json(
      { 
        error: 'Failed to delete student',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}