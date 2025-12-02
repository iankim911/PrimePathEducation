import { NextRequest } from 'next/server'
import { getAcademyId } from '@/lib/academyUtils'
import { supabase } from '@/lib/supabaseClient'

/**
 * POST /api/exams/curriculum-mapping
 * Creates a mapping between exam and curriculum node
 */
export async function POST(req: NextRequest) {
  try {
    const academyId = await getAcademyId()
    const body = await req.json()
    
    const { exam_id, curriculum_node_id, mapping_type = 'placement', slot_position = 1, weight = 1.0 } = body
    
    if (!exam_id || !curriculum_node_id) {
      return Response.json(
        { error: 'exam_id and curriculum_node_id are required' },
        { status: 400 }
      )
    }

    // Check if mapping already exists
    const { data: existing } = await supabase
      .from('curriculum_exam_mappings')
      .select('id')
      .eq('academy_id', academyId)
      .eq('curriculum_node_id', curriculum_node_id)
      .eq('exam_id', exam_id)
      .eq('mapping_type', mapping_type)
      .is('deleted_at', null)
      .single()

    if (existing) {
      return Response.json(
        { error: 'Mapping already exists for this exam and curriculum node' },
        { status: 409 }
      )
    }

    // Create new mapping
    const { data: mapping, error } = await supabase
      .from('curriculum_exam_mappings')
      .insert({
        academy_id: academyId,
        curriculum_node_id,
        exam_id,
        mapping_type,
        slot_position,
        weight,
        is_active: true
      })
      .select()
      .single()

    if (error) {
      console.error('Database error creating mapping:', error)
      return Response.json(
        { error: 'Failed to create curriculum mapping' },
        { status: 500 }
      )
    }

    return Response.json({
      success: true,
      mapping,
      message: 'Curriculum mapping created successfully'
    })

  } catch (error) {
    console.error('Error creating curriculum mapping:', error)
    return Response.json(
      { 
        error: 'Failed to create curriculum mapping',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * GET /api/exams/curriculum-mapping
 * Gets curriculum mappings for an exam or curriculum node
 */
export async function GET(req: NextRequest) {
  try {
    const academyId = await getAcademyId()
    const { searchParams } = new URL(req.url)
    
    const examId = searchParams.get('exam_id')
    const curriculumNodeId = searchParams.get('curriculum_node_id')
    
    let query = supabase
      .from('curriculum_exam_mappings')
      .select(`
        *,
        exams (id, title, description),
        curriculum_nodes (id, name, code, level_depth)
      `)
      .eq('academy_id', academyId)
      .is('deleted_at', null)

    if (examId) {
      query = query.eq('exam_id', examId)
    }
    
    if (curriculumNodeId) {
      query = query.eq('curriculum_node_id', curriculumNodeId)
    }

    const { data: mappings, error } = await query

    if (error) {
      console.error('Database error fetching mappings:', error)
      return Response.json(
        { error: 'Failed to fetch curriculum mappings' },
        { status: 500 }
      )
    }

    return Response.json({
      mappings: mappings || [],
      count: (mappings || []).length
    })

  } catch (error) {
    console.error('Error fetching curriculum mappings:', error)
    return Response.json(
      { 
        error: 'Failed to fetch curriculum mappings',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}