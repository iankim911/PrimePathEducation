import { getCurriculumTree, getCurriculumNodes, createCurriculumNode, serializeCurriculumTree } from '@/lib/services/curriculum'
import { getAcademyId } from '@/lib/academyUtils'
import { checkCurriculumTablesExist, getCurriculumFallbackResponse } from '@/lib/services/curriculumInit'

/**
 * GET /api/curriculum/nodes
 * Returns curriculum tree or flat list of nodes for the academy
 */
export async function GET(request: Request) {
  try {
    const academyId = await getAcademyId()
    
    // Skip table check - tables exist but may have permission issues
    // const { settingsTableExists, nodesTableExists } = await checkCurriculumTablesExist()
    
    // if (!settingsTableExists || !nodesTableExists) {
    //   // Return graceful fallback response
    //   const fallback = getCurriculumFallbackResponse()
    //   return Response.json({ 
    //     ...fallback,
    //     academy_id: academyId
    //   })
    // }
    
    const { searchParams } = new URL(request.url)
    const format = searchParams.get('format') || 'tree'
    const levelDepth = searchParams.get('level')
    
    if (format === 'flat') {
      const nodes = await getCurriculumNodes(academyId)
      return Response.json({ 
        nodes,
        academy_id: academyId,
        count: nodes.length 
      })
    }
    
    if (levelDepth) {
      const { getCurriculumNodesByLevel } = await import('@/lib/services/curriculum')
      const nodes = await getCurriculumNodesByLevel(academyId, parseInt(levelDepth))
      return Response.json({ 
        nodes,
        academy_id: academyId,
        level: parseInt(levelDepth),
        count: nodes.length 
      })
    }
    
    // Default: return tree format
    try {
      const tree = await getCurriculumTree(academyId)
      const serializedTree = serializeCurriculumTree(tree)
      
      return Response.json({ 
        tree: serializedTree,
        academy_id: academyId 
      })
    } catch (treeError) {
      console.error('Error building curriculum tree:', treeError)
      // Try to return flat structure as fallback
      const nodes = await getCurriculumNodes(academyId)
      return Response.json({ 
        tree: null,
        nodes,
        academy_id: academyId,
        error: 'Tree building failed, returned flat structure'
      })
    }
  } catch (error) {
    console.error('Error in GET /api/curriculum/nodes:', error)
    
    // Return graceful fallback instead of 500 error
    const fallback = getCurriculumFallbackResponse()
    return Response.json({ 
      ...fallback,
      academy_id: await getAcademyId(),
      error: 'Curriculum system temporarily unavailable'
    })
  }
}

/**
 * POST /api/curriculum/nodes
 * Creates a new curriculum node
 */
export async function POST(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    const nodeData = {
      parent_id: body.parent_id || null,
      level_depth: body.level_depth,
      sort_order: body.sort_order || 0,
      name: body.name,
      code: body.code || null,
      description: body.description || null,
      target_grade_min: body.target_grade_min || null,
      target_grade_max: body.target_grade_max || null,
      capacity: body.capacity || null,
      is_active: body.is_active !== false
    }
    
    const newNode = await createCurriculumNode(academyId, nodeData)
    
    return Response.json(
      { 
        node: newNode,
        message: 'Curriculum node created successfully' 
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('Error in POST /api/curriculum/nodes:', error)
    
    return Response.json(
      { 
        error: 'Failed to create curriculum node',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}