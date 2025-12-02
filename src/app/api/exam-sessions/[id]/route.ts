/**
 * Individual Exam Session API Route
 * 
 * Handles operations on specific exam sessions.
 */

import { 
  getExamSessionWithDetails, 
  updateExamSession, 
  startExamSession, 
  pauseExamSession, 
  endExamSession
} from '@/lib/services/examSessions'
import { type ExamSession } from '@/lib/services/exams'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/exam-sessions/[id]
 * 
 * Returns a specific exam session with details.
 */
export async function GET(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    
    // Get detailed session data
    const session = await getExamSessionWithDetails(params.id, academyId)
    
    if (!session) {
      return Response.json(
        { error: 'Exam session not found' },
        { status: 404 }
      )
    }
    
    return Response.json({ session })
  } catch (error) {
    console.error('Error in GET /api/exam-sessions/[id]:', error)
    
    return Response.json(
      { 
        error: 'Failed to fetch exam session',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/exam-sessions/[id]
 * 
 * Updates a specific exam session.
 */
export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Prepare update data
    const updates: Partial<ExamSession> = {}
    
    // Only update fields that are provided
    if (body.title !== undefined) updates.title = body.title
    if (body.instructions !== undefined) updates.instructions = body.instructions
    if (body.scheduled_start !== undefined) updates.scheduled_start = body.scheduled_start
    if (body.scheduled_end !== undefined) updates.scheduled_end = body.scheduled_end
    if (body.time_limit_override !== undefined) updates.time_limit_override = body.time_limit_override
    if (body.attempts_allowed_override !== undefined) updates.attempts_allowed_override = body.attempts_allowed_override
    if (body.allow_late_entry !== undefined) updates.allow_late_entry = body.allow_late_entry
    if (body.shuffle_questions !== undefined) updates.shuffle_questions = body.shuffle_questions
    if (body.require_all_students !== undefined) updates.require_all_students = body.require_all_students
    if (body.session_type !== undefined) updates.session_type = body.session_type
    if (body.metadata !== undefined) updates.metadata = body.metadata
    
    // Call service layer to update session
    const updatedSession = await updateExamSession(params.id, academyId, updates)
    
    return Response.json(
      { 
        session: updatedSession,
        message: 'Exam session updated successfully' 
      }
    )
  } catch (error) {
    console.error('Error in PUT /api/exam-sessions/[id]:', error)
    
    return Response.json(
      { 
        error: 'Failed to update exam session',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}