/**
 * Exam Session Control API Route
 * 
 * Handles session state changes (start, pause, resume, end).
 */

import { 
  startExamSession, 
  pauseExamSession, 
  endExamSession,
  updateExamSession 
} from '@/lib/services/examSessions'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * POST /api/exam-sessions/[id]/control
 * 
 * Controls exam session state (start, pause, resume, end).
 */
export async function POST(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const body = await request.json()
    
    const { action } = body
    
    if (!action) {
      return Response.json(
        { error: 'action is required. Must be: start, pause, resume, or end' },
        { status: 400 }
      )
    }
    
    let updatedSession
    
    switch (action) {
      case 'start':
        updatedSession = await startExamSession(params.id, academyId)
        break
        
      case 'pause':
        updatedSession = await pauseExamSession(params.id, academyId)
        break
        
      case 'resume':
        // Resume is just setting status back to active
        updatedSession = await updateExamSession(params.id, academyId, { 
          status: 'active' 
        })
        break
        
      case 'end':
        updatedSession = await endExamSession(params.id, academyId)
        break
        
      default:
        return Response.json(
          { error: 'Invalid action. Must be: start, pause, resume, or end' },
          { status: 400 }
        )
    }
    
    return Response.json(
      { 
        session: updatedSession,
        message: `Exam session ${action}ed successfully` 
      }
    )
  } catch (error) {
    console.error('Error in POST /api/exam-sessions/[id]/control:', error)
    
    return Response.json(
      { 
        error: 'Failed to control exam session',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}