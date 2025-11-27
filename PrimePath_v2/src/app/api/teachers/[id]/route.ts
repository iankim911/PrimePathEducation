import { NextRequest, NextResponse } from 'next/server'
import { 
  getTeacherById,
  updateTeacher,
  deleteTeacher 
} from '@/lib/services/teachers'

// Hardcoded academy ID for MVP - TODO: Get from auth/session  
const ACADEMY_ID = 'academy-123'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  try {
    const teacher = await getTeacherById(id, ACADEMY_ID)
    
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
    const body = await request.json()
    
    // Remove fields that shouldn't be updated
    const { id: bodyId, academy_id, role, created_at, updated_at, deleted_at, ...updates } = body
    
    const teacher = await updateTeacher(id, ACADEMY_ID, updates)
    
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
    await deleteTeacher(id, ACADEMY_ID)
    
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