import { NextRequest, NextResponse } from 'next/server'
import { 
  assignTeacherToClass,
} from '@/lib/services/teachers'

// Hardcoded academy ID for MVP - TODO: Get from auth/session
const ACADEMY_ID = 'academy-123'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate required fields
    if (!body.classId || !body.teachers || !Array.isArray(body.teachers)) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Class ID and teachers array are required' 
        },
        { status: 400 }
      )
    }
    
    const { classId, teachers } = body
    const assignments = []

    // Assign each teacher to the class
    for (const teacher of teachers) {
      if (!teacher.teacherId || !teacher.role) {
        continue // Skip invalid teacher assignments
      }

      try {
        const assignment = await assignTeacherToClass(
          ACADEMY_ID,
          classId,
          teacher.teacherId,
          teacher.role,
          teacher.isPrimary || false
        )
        assignments.push(assignment)
      } catch (error) {
        console.error(`Failed to assign teacher ${teacher.teacherId}:`, error)
        // Continue with other assignments
      }
    }
    
    return NextResponse.json({
      success: true,
      assignments,
    })
  } catch (error) {
    console.error('POST /api/class-teachers error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to assign teachers to class' 
      },
      { status: 500 }
    )
  }
}