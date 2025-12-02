import { NextRequest, NextResponse } from 'next/server'
import { 
  getClassesByTeacher,
  assignTeacherToClass,
  removeTeacherFromClass
} from '@/lib/services/teachers'
import { getAcademyId } from '@/lib/academyUtils'

// GET teacher's current class assignments
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const academyId = await getAcademyId()
    const { id: teacherId } = await params
    
    const assignments = await getClassesByTeacher(academyId, teacherId)
    
    return NextResponse.json({
      success: true,
      assignments
    })
  } catch (error) {
    console.error('GET /api/teachers/[id]/assignments error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch teacher assignments' 
      },
      { status: 500 }
    )
  }
}

// POST add a new class assignment for teacher
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const academyId = await getAcademyId()
    const { id: teacherId } = await params
    const body = await request.json()
    
    // Validate required fields
    if (!body.class_id || !body.role) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Class ID and role are required' 
        },
        { status: 400 }
      )
    }
    
    const assignment = await assignTeacherToClass(
      academyId,
      body.class_id,
      teacherId,
      body.role,
      body.is_primary || false
    )
    
    return NextResponse.json({
      success: true,
      assignment
    })
  } catch (error) {
    console.error('POST /api/teachers/[id]/assignments error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to assign teacher to class' 
      },
      { status: 500 }
    )
  }
}

// DELETE remove a class assignment from teacher
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const academyId = await getAcademyId()
    const { id: teacherId } = await params
    const { searchParams } = new URL(request.url)
    const classId = searchParams.get('class_id')
    
    if (!classId) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Class ID is required' 
        },
        { status: 400 }
      )
    }
    
    await removeTeacherFromClass(academyId, classId, teacherId)
    
    return NextResponse.json({
      success: true,
      message: 'Teacher removed from class successfully'
    })
  } catch (error) {
    console.error('DELETE /api/teachers/[id]/assignments error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to remove teacher from class' 
      },
      { status: 500 }
    )
  }
}