/**
 * Curriculum Service Layer
 * 
 * This service handles the hierarchical curriculum system that allows academies
 * to configure flexible curriculum structures from 1-4 levels deep.
 */

import { supabase } from '@/lib/supabaseClient'
import { checkCurriculumTablesExist } from './curriculumInit'

/**
 * Academy-level curriculum configuration
 */
export interface CurriculumSettings {
  id: string
  academy_id: string
  max_depth: number        // 1-4, how many levels the academy wants
  level_1_name: string     // e.g., "Program", "Department"
  level_2_name: string     // e.g., "Track", "Focus Area"
  level_3_name: string     // e.g., "Level", "Grade"
  level_4_name: string     // e.g., "Section", "Class"
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Individual curriculum node in the hierarchy tree
 */
export interface CurriculumNode {
  id: string
  academy_id: string
  parent_id?: string | null
  level_depth: number      // 1, 2, 3, or 4
  sort_order: number
  name: string
  code?: string | null     // Optional short code like "ELM-A1"
  description?: string | null
  target_grade_min?: number | null
  target_grade_max?: number | null
  capacity?: number | null  // Max students for this curriculum path
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Extended node with parent/children information
 */
export interface CurriculumNodeWithRelations extends CurriculumNode {
  parent?: CurriculumNode | null
  children?: CurriculumNode[]
  path_name?: string       // Full path like "Elementary > Reading Focus > Beginner"
  path_code?: string       // Full code path like "ELM.READ.BEG"
}

/**
 * Curriculum tree view for display
 */
export interface CurriculumTree {
  settings: CurriculumSettings
  nodes: CurriculumNodeWithRelations[]
}

/**
 * Get curriculum settings for an academy
 */
export async function getCurriculumSettings(academyId: string): Promise<CurriculumSettings | null> {
  try {
    // Skip table check - tables exist but may have permission issues
    // const { settingsTableExists } = await checkCurriculumTablesExist()
    // if (!settingsTableExists) {
    //   console.log('Curriculum settings table does not exist yet')
    //   return null
    // }

    const { data, error } = await supabase
      .from('curriculum_settings')
      .select('*')
      .eq('academy_id', academyId)
      .is('deleted_at', null)
      .single()

    if (error) {
      if (error.code === 'PGRST116' || error.code === '42P01') {
        return null // No settings found or table doesn't exist
      }
      console.error('Error fetching curriculum settings:', error)
      return null // Return null instead of throwing to handle gracefully
    }

    return data
  } catch (error) {
    console.error('Error in getCurriculumSettings:', error)
    return null
  }
}

/**
 * Create or update curriculum settings for an academy
 */
export async function upsertCurriculumSettings(
  academyId: string,
  settings: Partial<Omit<CurriculumSettings, 'id' | 'academy_id' | 'created_at' | 'updated_at'>>
): Promise<CurriculumSettings> {
  const settingsData = {
    academy_id: academyId,
    ...settings,
    updated_at: new Date().toISOString(),
  }

  const { data, error } = await supabase
    .from('curriculum_settings')
    .upsert(settingsData, {
      onConflict: 'academy_id',
      ignoreDuplicates: false
    })
    .select()
    .single()

  if (error) {
    console.error('Error upserting curriculum settings:', error)
    throw new Error(`Failed to save curriculum settings: ${error.message}`)
  }

  return data
}

/**
 * Get all curriculum nodes for an academy
 */
export async function getCurriculumNodes(academyId: string): Promise<CurriculumNode[]> {
  try {
    // Skip table check - tables exist but may have permission issues  
    // const { nodesTableExists } = await checkCurriculumTablesExist()
    // if (!nodesTableExists) {
    //   console.log('Curriculum nodes table does not exist yet')
    //   return []
    // }

    const { data, error } = await supabase
      .from('curriculum_nodes')
      .select('*')
      .eq('academy_id', academyId)
      .is('deleted_at', null)
      .order('level_depth', { ascending: true })
      .order('sort_order', { ascending: true })

    if (error) {
      if (error.code === '42P01') {
        return [] // Table doesn't exist
      }
      console.error('Error fetching curriculum nodes:', error)
      return [] // Return empty array instead of throwing
    }

    return data || []
  } catch (error) {
    console.error('Error in getCurriculumNodes:', error)
    return []
  }
}

/**
 * Get curriculum nodes by level depth
 */
export async function getCurriculumNodesByLevel(
  academyId: string,
  levelDepth: number
): Promise<CurriculumNode[]> {
  const { data, error } = await supabase
    .from('curriculum_nodes')
    .select('*')
    .eq('academy_id', academyId)
    .eq('level_depth', levelDepth)
    .is('deleted_at', null)
    .order('sort_order', { ascending: true })

  if (error) {
    console.error('Error fetching curriculum nodes by level:', error)
    throw new Error(`Failed to fetch curriculum nodes by level: ${error.message}`)
  }

  return data || []
}

/**
 * Get children of a specific curriculum node
 */
export async function getCurriculumNodeChildren(
  academyId: string,
  parentId: string
): Promise<CurriculumNode[]> {
  const { data, error } = await supabase
    .from('curriculum_nodes')
    .select('*')
    .eq('academy_id', academyId)
    .eq('parent_id', parentId)
    .is('deleted_at', null)
    .order('sort_order', { ascending: true })

  if (error) {
    console.error('Error fetching curriculum node children:', error)
    throw new Error(`Failed to fetch curriculum node children: ${error.message}`)
  }

  return data || []
}

/**
 * Get full curriculum tree with hierarchy
 */
export async function getCurriculumTree(academyId: string): Promise<CurriculumTree | null> {
  // Get settings first
  const settings = await getCurriculumSettings(academyId)
  if (!settings) {
    return null
  }

  // Get all nodes
  const nodes = await getCurriculumNodes(academyId)
  
  // Build tree structure
  const nodeMap = new Map<string, CurriculumNodeWithRelations>()
  
  // Initialize all nodes
  nodes.forEach(node => {
    nodeMap.set(node.id, { ...node, children: [] })
  })

  // Build parent-child relationships
  const rootNodes: CurriculumNodeWithRelations[] = []
  
  nodes.forEach(node => {
    const nodeWithRelations = nodeMap.get(node.id)!
    
    if (node.parent_id) {
      const parent = nodeMap.get(node.parent_id)
      if (parent) {
        nodeWithRelations.parent = parent
        parent.children = parent.children || []
        parent.children.push(nodeWithRelations)
      }
    } else {
      rootNodes.push(nodeWithRelations)
    }
  })

  return {
    settings,
    nodes: rootNodes
  }
}

/**
 * Create a JSON-serializable version of the curriculum tree
 * Removes circular references by excluding parent references
 */
export function serializeCurriculumTree(tree: CurriculumTree | null): any {
  if (!tree) return null

  // Helper function to create serializable nodes
  function serializeNode(node: CurriculumNodeWithRelations): any {
    const serialized: any = {
      id: node.id,
      academy_id: node.academy_id,
      parent_id: node.parent_id,
      level_depth: node.level_depth,
      sort_order: node.sort_order,
      name: node.name,
      code: node.code,
      description: node.description,
      target_grade_min: node.target_grade_min,
      target_grade_max: node.target_grade_max,
      capacity: node.capacity,
      is_active: node.is_active,
      created_at: node.created_at,
      updated_at: node.updated_at,
      deleted_at: node.deleted_at,
      path_name: node.path_name,
      path_code: node.path_code
    }

    // Serialize children recursively but exclude parent references
    if (node.children && node.children.length > 0) {
      serialized.children = node.children.map(serializeNode)
    }

    return serialized
  }

  return {
    settings: tree.settings,
    nodes: tree.nodes.map(serializeNode)
  }
}

/**
 * Create a new curriculum node
 */
export async function createCurriculumNode(
  academyId: string,
  nodeData: Omit<CurriculumNode, 'id' | 'academy_id' | 'created_at' | 'updated_at' | 'deleted_at'>
): Promise<CurriculumNode> {
  const { data, error } = await supabase
    .from('curriculum_nodes')
    .insert({
      academy_id: academyId,
      ...nodeData
    })
    .select()
    .single()

  if (error) {
    console.error('Error creating curriculum node:', error)
    throw new Error(`Failed to create curriculum node: ${error.message}`)
  }

  return data
}

/**
 * Update a curriculum node
 */
export async function updateCurriculumNode(
  nodeId: string,
  academyId: string,
  updates: Partial<Omit<CurriculumNode, 'id' | 'academy_id' | 'created_at' | 'updated_at'>>
): Promise<CurriculumNode> {
  const { data, error } = await supabase
    .from('curriculum_nodes')
    .update({
      ...updates,
      updated_at: new Date().toISOString(),
    })
    .eq('id', nodeId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .select()
    .single()

  if (error) {
    console.error('Error updating curriculum node:', error)
    throw new Error(`Failed to update curriculum node: ${error.message}`)
  }

  return data
}

/**
 * Soft delete a curriculum node and all its children
 */
export async function deleteCurriculumNode(
  nodeId: string,
  academyId: string
): Promise<void> {
  // First get all descendant IDs
  const descendants = await getCurriculumNodeDescendants(academyId, nodeId)
  const allIds = [nodeId, ...descendants.map(d => d.id)]

  // Soft delete all nodes in the subtree
  const { error } = await supabase
    .from('curriculum_nodes')
    .update({
      deleted_at: new Date().toISOString(),
      is_active: false,
      updated_at: new Date().toISOString(),
    })
    .eq('academy_id', academyId)
    .in('id', allIds)
    .is('deleted_at', null)

  if (error) {
    console.error('Error deleting curriculum node:', error)
    throw new Error(`Failed to delete curriculum node: ${error.message}`)
  }
}

/**
 * Get all descendants of a curriculum node (recursive)
 */
async function getCurriculumNodeDescendants(
  academyId: string, 
  nodeId: string
): Promise<CurriculumNode[]> {
  const descendants: CurriculumNode[] = []
  const children = await getCurriculumNodeChildren(academyId, nodeId)
  
  for (const child of children) {
    descendants.push(child)
    const grandchildren = await getCurriculumNodeDescendants(academyId, child.id)
    descendants.push(...grandchildren)
  }
  
  return descendants
}

/**
 * Reorder curriculum nodes within the same parent
 */
export async function reorderCurriculumNodes(
  academyId: string,
  parentId: string | null,
  nodeOrders: { nodeId: string; sortOrder: number }[]
): Promise<void> {
  // Update all sort orders in a transaction-like manner
  for (const { nodeId, sortOrder } of nodeOrders) {
    await supabase
      .from('curriculum_nodes')
      .update({
        sort_order: sortOrder,
        updated_at: new Date().toISOString(),
      })
      .eq('id', nodeId)
      .eq('academy_id', academyId)
      .eq('parent_id', parentId)
      .is('deleted_at', null)
  }
}

/**
 * Get curriculum path for a given node (breadcrumb trail)
 */
export async function getCurriculumPath(
  academyId: string,
  nodeId: string
): Promise<CurriculumNode[]> {
  const path: CurriculumNode[] = []
  let currentNodeId: string | null = nodeId

  while (currentNodeId) {
    const { data: nodeData, error } = await supabase
      .from('curriculum_nodes')
      .select('*')
      .eq('id', currentNodeId)
      .eq('academy_id', academyId)
      .is('deleted_at', null)
      .single() as { data: CurriculumNode | null, error: any }

    if (error || !nodeData) {
      break
    }

    path.unshift(nodeData) // Add to beginning
    currentNodeId = nodeData.parent_id || null
  }

  return path
}

/**
 * Check if curriculum system is properly configured for an academy
 */
export async function isCurriculumConfigured(academyId: string): Promise<boolean> {
  const settings = await getCurriculumSettings(academyId)
  if (!settings) {
    return false
  }

  const nodes = await getCurriculumNodes(academyId)
  return nodes.length > 0
}

/**
 * Get curriculum nodes at the deepest level (for class assignment)
 * These are the actual curriculum levels that classes can be assigned to
 */
export async function getDeepestCurriculumNodes(academyId: string): Promise<CurriculumNode[]> {
  const settings = await getCurriculumSettings(academyId)
  if (!settings) {
    return []
  }

  const { data, error } = await supabase
    .from('curriculum_nodes')
    .select('*')
    .eq('academy_id', academyId)
    .eq('level_depth', settings.max_depth)
    .is('deleted_at', null)
    .order('sort_order', { ascending: true })

  if (error) {
    console.error('Error fetching deepest curriculum nodes:', error)
    return []
  }

  return data || []
}

/**
 * Get root level curriculum nodes (level 1)
 */
export async function getRootCurriculumNodes(academyId: string): Promise<CurriculumNode[]> {
  const { data, error } = await supabase
    .from('curriculum_nodes')
    .select('*')
    .eq('academy_id', academyId)
    .eq('level_depth', 1)
    .is('deleted_at', null)
    .order('sort_order', { ascending: true })

  if (error) {
    console.error('Error fetching root curriculum nodes:', error)
    return []
  }

  return data || []
}

/**
 * Check if a curriculum node can have children (not at max depth)
 */
export async function canNodeHaveChildren(
  academyId: string, 
  nodeId: string
): Promise<boolean> {
  const settings = await getCurriculumSettings(academyId)
  if (!settings) {
    return false
  }

  const { data, error } = await supabase
    .from('curriculum_nodes')
    .select('level_depth')
    .eq('id', nodeId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .single()

  if (error || !data) {
    return false
  }

  return data.level_depth < settings.max_depth
}