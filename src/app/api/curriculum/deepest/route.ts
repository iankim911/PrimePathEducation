import { getCurriculumSettings } from '@/lib/services/curriculum'
import { getAcademyId } from '@/lib/academyUtils'
import { supabase } from '@/lib/supabaseClient'

/**
 * GET /api/curriculum/deepest
 * Returns deepest level curriculum nodes with full breadcrumb paths for exam assignment
 */
export async function GET(request: Request) {
  try {
    const academyId = await getAcademyId()
    
    // Get curriculum settings to determine max depth
    const settings = await getCurriculumSettings(academyId)
    if (!settings) {
      return Response.json({ 
        nodes: [],
        academy_id: academyId,
        count: 0,
        error: 'No curriculum settings found'
      })
    }

    // Get all curriculum nodes to build paths
    const { data: allNodes, error: nodesError } = await supabase
      .from('curriculum_nodes')
      .select('*')
      .eq('academy_id', academyId)
      .is('deleted_at', null)
      .order('level_depth', { ascending: true })
      .order('sort_order', { ascending: true })

    if (nodesError) {
      console.error('Database error fetching curriculum nodes:', nodesError)
      return Response.json(
        { 
          error: 'Failed to fetch curriculum nodes',
          message: nodesError.message,
          nodes: [],
          academy_id: academyId,
          count: 0
        },
        { status: 500 }
      )
    }

    if (!allNodes || allNodes.length === 0) {
      return Response.json({ 
        nodes: [],
        academy_id: academyId,
        count: 0
      })
    }

    // Create a map of nodes by ID for quick lookup
    const nodeMap = new Map()
    allNodes.forEach(node => {
      nodeMap.set(node.id, node)
    })

    // Function to build breadcrumb path for a node
    const buildPath = (nodeId: string): string[] => {
      const path: string[] = []
      let currentNode = nodeMap.get(nodeId)
      
      while (currentNode) {
        path.unshift(currentNode.name) // Add to beginning
        currentNode = currentNode.parent_id ? nodeMap.get(currentNode.parent_id) : null
      }
      
      return path
    }

    // Get only the deepest level nodes and build their paths
    const deepestNodes = allNodes.filter(node => node.level_depth === settings.max_depth)
    
    // Transform the data to include breadcrumb information
    const nodesWithBreadcrumbs = deepestNodes.map(node => ({
      id: node.id,
      name: node.name,
      code: node.code,
      level_depth: node.level_depth,
      path_name: buildPath(node.id).join(' > '), // Full breadcrumb like "Program A > Track 1 > Level 1"
      path_code: node.code || node.name, // Use code if available, otherwise name
      academy_id: node.academy_id,
      parent_id: node.parent_id
    }))
    
    return Response.json({ 
      nodes: nodesWithBreadcrumbs,
      academy_id: academyId,
      count: nodesWithBreadcrumbs.length 
    })
  } catch (error) {
    console.error('Error in GET /api/curriculum/deepest:', error)
    
    const academyId = await getAcademyId()
    return Response.json(
      { 
        error: 'Failed to fetch deepest curriculum nodes',
        message: error instanceof Error ? error.message : 'Unknown error',
        nodes: [],
        academy_id: academyId,
        count: 0
      },
      { status: 500 }
    )
  }
}