/**
 * Exam Sessions API Route
 * 
 * Handles live exam session management.
 */

import { getAllExamSessionsByAcademy, createExamSession, getExamSessionStatistics } from '@/lib/services/examSessions'
import { type ExamSession } from '@/lib/services/exams'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/exam-sessions
 * 
 * Returns exam sessions for the academy with optional filters.
 */
export async function GET(request: Request) {
  try {
    const academyId = await getAcademyId()
    const url = new URL(request.url)
    
    // Parse query parameters for filtering
    const filters = {
      status: url.searchParams.get('status') as ExamSession['status'] | undefined,
      exam_id: url.searchParams.get('exam_id') || undefined,
      class_id: url.searchParams.get('class_id') || undefined,
      teacher_id: url.searchParams.get('teacher_id') || undefined,
      limit: url.searchParams.get('limit') ? parseInt(url.searchParams.get('limit')!) : undefined
    }
    
    // Remove undefined values
    Object.keys(filters).forEach(key => {
      if (filters[key as keyof typeof filters] === undefined) {
        delete filters[key as keyof typeof filters]
      }
    })
    
    // Call service layer
    const sessions = await getAllExamSessionsByAcademy(academyId, filters)
    const statistics = await getExamSessionStatistics(academyId)
    
    return Response.json({ 
      sessions,
      academy_id: academyId,
      count: sessions.length,
      statistics,
      filters
    })
  } catch (error) {
    console.error('Error in GET /api/exam-sessions:', error)
    
    return Response.json(
      { 
        error: 'Failed to fetch exam sessions',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/exam-sessions
 * 
 * Creates a new exam session.
 */
export async function POST(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Validate required fields
    if (!body.exam_id) {
      return Response.json(
        { error: 'exam_id is required' },
        { status: 400 }
      )
    }
    
    if (!body.title) {
      return Response.json(
        { error: 'title is required' },
        { status: 400 }
      )
    }
    
    // Prepare session data
    const sessionData = {
      academy_id: academyId,
      exam_id: body.exam_id,
      class_id: body.class_id || undefined,
      teacher_id: body.teacher_id || undefined,
      title: body.title,
      instructions: body.instructions || undefined,
      scheduled_start: body.scheduled_start || undefined,
      scheduled_end: body.scheduled_end || undefined,
      time_limit_override: body.time_limit_override || undefined,
      attempts_allowed_override: body.attempts_allowed_override || undefined,
      allow_late_entry: body.allow_late_entry,
      shuffle_questions: body.shuffle_questions,
      require_all_students: body.require_all_students,
      session_type: body.session_type || undefined
    }
    
    // Call service layer to create session
    const newSession = await createExamSession(sessionData)
    
    return Response.json(
      { 
        session: newSession,
        message: 'Exam session created successfully' 
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('Error in POST /api/exam-sessions:', error)
    
    return Response.json(
      { 
        error: 'Failed to create exam session',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}