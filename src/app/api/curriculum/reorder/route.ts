import { reorderCurriculumNodes } from '@/lib/services/curriculum'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * POST /api/curriculum/reorder
 * Reorders curriculum nodes within the same parent
 */
export async function POST(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    const { parent_id, node_orders } = body
    
    if (!Array.isArray(node_orders) || node_orders.length === 0) {
      return Response.json(
        { error: 'node_orders must be a non-empty array' },
        { status: 400 }
      )
    }
    
    // Validate node_orders format
    for (const item of node_orders) {
      if (!item.nodeId || typeof item.sortOrder !== 'number') {
        return Response.json(
          { error: 'Each item in node_orders must have nodeId (string) and sortOrder (number)' },
          { status: 400 }
        )
      }
    }
    
    await reorderCurriculumNodes(academyId, parent_id || null, node_orders)
    
    return Response.json(
      { 
        message: 'Curriculum nodes reordered successfully',
        reordered_count: node_orders.length
      },
      { status: 200 }
    )
  } catch (error) {
    console.error('Error in POST /api/curriculum/reorder:', error)
    
    return Response.json(
      { 
        error: 'Failed to reorder curriculum nodes',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}