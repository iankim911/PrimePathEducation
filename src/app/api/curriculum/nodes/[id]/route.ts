import { updateCurriculumNode, deleteCurriculumNode, getCurriculumNodeChildren } from '@/lib/services/curriculum'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/curriculum/nodes/[id]
 * Returns children of a specific curriculum node
 */
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params
    const academyId = await getAcademyId()
    
    const children = await getCurriculumNodeChildren(academyId, id)
    
    return Response.json({ 
      children,
      academy_id: academyId,
      parent_id: id,
      count: children.length 
    })
  } catch (error) {
    console.error('Error in GET /api/curriculum/nodes/[id]:', error)
    
    return Response.json(
      { 
        error: 'Failed to fetch curriculum node children',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/curriculum/nodes/[id]
 * Updates a curriculum node
 */
export async function PUT(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params
    const academyId = await getAcademyId()
    const body = await request.json()
    
    const updates = {
      name: body.name,
      code: body.code,
      description: body.description,
      target_grade_min: body.target_grade_min,
      target_grade_max: body.target_grade_max,
      capacity: body.capacity,
      sort_order: body.sort_order,
      is_active: body.is_active
    }
    
    // Filter out undefined values
    const filteredUpdates = Object.fromEntries(
      Object.entries(updates).filter(([_, value]) => value !== undefined)
    )
    
    const updatedNode = await updateCurriculumNode(id, academyId, filteredUpdates)
    
    return Response.json(
      { 
        node: updatedNode,
        message: 'Curriculum node updated successfully' 
      },
      { status: 200 }
    )
  } catch (error) {
    console.error('Error in PUT /api/curriculum/nodes/[id]:', error)
    
    return Response.json(
      { 
        error: 'Failed to update curriculum node',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/curriculum/nodes/[id]
 * Soft deletes a curriculum node and all its children
 */
export async function DELETE(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params
    const academyId = await getAcademyId()
    
    await deleteCurriculumNode(id, academyId)
    
    return Response.json(
      { 
        message: 'Curriculum node deleted successfully' 
      },
      { status: 200 }
    )
  } catch (error) {
    console.error('Error in DELETE /api/curriculum/nodes/[id]:', error)
    
    return Response.json(
      { 
        error: 'Failed to delete curriculum node',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}