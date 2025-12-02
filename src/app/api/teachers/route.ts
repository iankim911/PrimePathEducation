import { NextRequest, NextResponse } from 'next/server'
import { 
  listTeachersByAcademy, 
  createTeacher,
  type Teacher 
} from '@/lib/services/teachers'
import { getAcademyId } from '@/lib/academyUtils'

export async function GET() {
  try {
    const academyId = await getAcademyId()
    const teachers = await listTeachersByAcademy(academyId)
    
    return NextResponse.json({
      success: true,
      teachers,
    })
  } catch (error) {
    console.error('GET /api/teachers error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch teachers' 
      },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Validate required fields
    if (!body.full_name || !body.email) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Full name and email are required' 
        },
        { status: 400 }
      )
    }
    
    const teacherData: Omit<Teacher, 'id' | 'created_at' | 'updated_at' | 'deleted_at'> = {
      academy_id: academyId,
      email: body.email.trim().toLowerCase(),
      full_name: body.full_name.trim(),
      role: 'teacher',
      is_active: true,
    }

    const teacher = await createTeacher(teacherData)
    
    return NextResponse.json({
      success: true,
      teacher,
    })
  } catch (error) {
    console.error('POST /api/teachers error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to create teacher' 
      },
      { status: 500 }
    )
  }
}