import { NextRequest, NextResponse } from 'next/server'
import { 
  getTeacherById,
  updateTeacher,
  deleteTeacher 
} from '@/lib/services/teachers'
import { getAcademyId } from '@/lib/academyUtils'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  try {
    const academyId = await getAcademyId()
    const teacher = await getTeacherById(id, academyId)
    
    if (!teacher) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Teacher not found' 
        },
        { status: 404 }
      )
    }
    
    return NextResponse.json({
      success: true,
      teacher,
    })
  } catch (error) {
    console.error(`GET /api/teachers/${id} error:`, error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch teacher' 
      },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Remove fields that shouldn't be updated
    const { id: bodyId, academy_id, role, created_at, updated_at, deleted_at, ...updates } = body
    
    const teacher = await updateTeacher(id, academyId, updates)
    
    return NextResponse.json({
      success: true,
      teacher,
    })
  } catch (error) {
    console.error(`PUT /api/teachers/${id} error:`, error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to update teacher' 
      },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  try {
    const academyId = await getAcademyId()
    await deleteTeacher(id, academyId)
    
    return NextResponse.json({
      success: true,
    })
  } catch (error) {
    console.error(`DELETE /api/teachers/${id} error:`, error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to delete teacher' 
      },
      { status: 500 }
    )
  }
}