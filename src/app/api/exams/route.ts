/**
 * Exams API Route
 * 
 * IMPORTANT: API routes must be "thin" - they are just the HTTP layer.
 * - Always call service-layer functions for business logic
 * - Never talk to Supabase directly from API routes
 * - Keep routes focused on HTTP concerns (parsing params, returning responses)
 */

import { getAllExamsByAcademy, createExam, getExamStatistics, type Exam } from '@/lib/services/exams'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/exams
 * 
 * Returns a list of all exams for the current academy.
 * In production, academy_id would be determined from the authenticated user's session.
 */
export async function GET() {
  try {
    const academyId = await getAcademyId()
    
    // Call service layer function - all business logic lives there
    const exams = await getAllExamsByAcademy(academyId)
    const statistics = await getExamStatistics(academyId)
    
    // Return the data as JSON
    return Response.json({ 
      exams,
      academy_id: academyId,
      count: exams.length,
      statistics
    })
  } catch (error) {
    console.error('Error in GET /api/exams:', error)
    
    // Return error response
    return Response.json(
      { 
        error: 'Failed to fetch exams',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/exams
 * 
 * Creates a new exam for the current academy.
 */
export async function POST(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Prepare exam data
    const examData: Omit<Exam, 'id' | 'total_questions' | 'total_points' | 'created_at' | 'updated_at' | 'deleted_at'> = {
      academy_id: academyId,
      title: body.title,
      description: body.description || null,
      exam_type_id: body.exam_type_id || null,
      time_limit_minutes: body.time_limit_minutes || null,
      attempts_allowed: body.attempts_allowed || 1,
      passing_score: body.passing_score || null,
      randomize_questions: body.randomize_questions || false,
      randomize_answers: body.randomize_answers || false,
      status: body.status || 'draft',
      show_results: body.show_results ?? true,
      allow_review: body.allow_review ?? true,
      require_webcam: body.require_webcam || false,
      difficulty_level: body.difficulty_level || null,
      subject_tags: body.subject_tags || null,
      learning_objectives: body.learning_objectives || null,
      metadata: body.metadata || null,
      created_by: body.created_by || null,
      is_active: true
    }
    
    // Call service layer to create exam
    const newExam = await createExam(examData)
    
    return Response.json(
      { 
        exam: newExam,
        message: 'Exam created successfully' 
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('Error in POST /api/exams:', error)
    
    return Response.json(
      { 
        error: 'Failed to create exam',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}