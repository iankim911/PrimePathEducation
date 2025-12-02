/**
 * Grade Management Service Layer
 * 
 * This service handles all grade configuration operations including:
 * - Academy grade configuration management
 * - Grade option CRUD operations
 * - Dropdown data formatting
 * - Grade display utilities
 */

import { supabase } from '@/lib/supabaseClient'
import type {
  GradeConfiguration,
  GradeOption,
  GradeOptionFormatted,
  GradeDropdownItem,
  CreateGradeConfigurationRequest,
  UpdateGradeConfigurationRequest,
  CreateGradeOptionRequest,
  UpdateGradeOptionRequest,
  GradeConfigurationResponse,
  GradeValue,
  GradeValueString
} from '@/types/grades'
import { GRADE_CONSTANTS } from '@/types/grades'

/**
 * Get grade configuration for an academy
 */
export async function getGradeConfiguration(academyId: string): Promise<GradeConfiguration | null> {
  const { data, error } = await supabase
    .from('grade_configurations')
    .select('*')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .single()

  if (error) {
    if (error.code === 'PGRST116') {
      return null // No configuration found
    }
    console.error('Error fetching grade configuration:', error)
    throw new Error(`Failed to fetch grade configuration: ${error.message}`)
  }

  return data
}

/**
 * Get all grade options for an academy
 */
export async function getGradeOptions(academyId: string): Promise<GradeOption[]> {
  const { data, error } = await supabase
    .from('grade_options')
    .select('*')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('sort_order', { ascending: true })
    .order('grade_value', { ascending: true })

  if (error) {
    console.error('Error fetching grade options:', error)
    throw new Error(`Failed to fetch grade options: ${error.message}`)
  }

  return data || []
}

/**
 * Get complete grade configuration with options
 */
export async function getGradeConfigurationWithOptions(academyId: string): Promise<GradeConfigurationResponse> {
  const [configuration, options] = await Promise.all([
    getGradeConfiguration(academyId),
    getGradeOptions(academyId)
  ])

  if (!configuration) {
    throw new Error('No grade configuration found for academy')
  }

  return { configuration, options }
}

/**
 * Get formatted grade options for dropdown components
 */
export async function getGradeDropdownItems(
  academyId: string, 
  includeAllOption: boolean = true
): Promise<GradeDropdownItem[]> {
  const { configuration, options } = await getGradeConfigurationWithOptions(academyId)
  
  const items: GradeDropdownItem[] = []
  
  // Add "All Grades" option if requested and configured
  if (includeAllOption && configuration.show_all_option) {
    items.push({
      value: GRADE_CONSTANTS.ALL_GRADES_VALUE,
      label: configuration.all_grades_label,
      sort_order: -1 // Always first
    })
  }
  
  // Add individual grade options
  options.forEach(option => {
    items.push({
      value: option.grade_value.toString(),
      label: option.display_name,
      grade_value: option.grade_value,
      sort_order: option.sort_order
    })
  })
  
  // Sort by sort_order
  return items.sort((a, b) => a.sort_order - b.sort_order)
}

/**
 * Get grade display name by value
 */
export async function getGradeDisplayName(
  academyId: string, 
  gradeValue: GradeValue
): Promise<string> {
  const { data, error } = await supabase
    .rpc('get_grade_display_name', {
      p_academy_id: academyId,
      p_grade_value: gradeValue
    })

  if (error) {
    console.error('Error getting grade display name:', error)
    // Fallback to generic format
    return `Grade ${gradeValue}`
  }

  return data || `Grade ${gradeValue}`
}

/**
 * Validate if grade value exists for academy
 */
export async function validateGradeValue(
  academyId: string, 
  gradeValue: GradeValue
): Promise<boolean> {
  const { data, error } = await supabase
    .rpc('validate_grade_value', {
      p_academy_id: academyId,
      p_grade_value: gradeValue
    })

  if (error) {
    console.error('Error validating grade value:', error)
    return false
  }

  return data === true
}

/**
 * Create or update grade configuration
 */
export async function upsertGradeConfiguration(
  academyId: string,
  configData: CreateGradeConfigurationRequest | UpdateGradeConfigurationRequest
): Promise<GradeConfiguration> {
  // Try to get existing configuration
  const existing = await getGradeConfiguration(academyId)
  
  if (existing) {
    // Update existing
    const { data, error } = await supabase
      .from('grade_configurations')
      .update({
        ...configData,
        updated_at: new Date().toISOString(),
      })
      .eq('id', existing.id)
      .select()
      .single()

    if (error) {
      console.error('Error updating grade configuration:', error)
      throw new Error(`Failed to update grade configuration: ${error.message}`)
    }

    return data
  } else {
    // Create new
    const { data, error } = await supabase
      .from('grade_configurations')
      .insert({
        academy_id: academyId,
        ...configData,
      })
      .select()
      .single()

    if (error) {
      console.error('Error creating grade configuration:', error)
      throw new Error(`Failed to create grade configuration: ${error.message}`)
    }

    return data
  }
}

/**
 * Create a new grade option
 */
export async function createGradeOption(
  academyId: string,
  optionData: CreateGradeOptionRequest
): Promise<GradeOption> {
  const { data, error } = await supabase
    .from('grade_options')
    .insert({
      academy_id: academyId,
      ...optionData,
    })
    .select()
    .single()

  if (error) {
    console.error('Error creating grade option:', error)
    throw new Error(`Failed to create grade option: ${error.message}`)
  }

  return data
}

/**
 * Update an existing grade option
 */
export async function updateGradeOption(
  optionId: string,
  academyId: string,
  updates: UpdateGradeOptionRequest
): Promise<GradeOption> {
  const { data, error } = await supabase
    .from('grade_options')
    .update({
      ...updates,
      updated_at: new Date().toISOString(),
    })
    .eq('id', optionId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .select()
    .single()

  if (error) {
    console.error('Error updating grade option:', error)
    throw new Error(`Failed to update grade option: ${error.message}`)
  }

  return data
}

/**
 * Delete a grade option (soft delete)
 */
export async function deleteGradeOption(
  optionId: string,
  academyId: string
): Promise<void> {
  const { error } = await supabase
    .from('grade_options')
    .update({
      deleted_at: new Date().toISOString(),
      is_active: false,
      updated_at: new Date().toISOString(),
    })
    .eq('id', optionId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)

  if (error) {
    console.error('Error deleting grade option:', error)
    throw new Error(`Failed to delete grade option: ${error.message}`)
  }
}

/**
 * Reorder grade options
 */
export async function reorderGradeOptions(
  academyId: string,
  orderedIds: string[]
): Promise<void> {
  const updates = orderedIds.map((id, index) => ({
    id,
    sort_order: (index + 1) * GRADE_CONSTANTS.DEFAULT_SORT_INCREMENT
  }))

  for (const update of updates) {
    const { error } = await supabase
      .from('grade_options')
      .update({ 
        sort_order: update.sort_order,
        updated_at: new Date().toISOString()
      })
      .eq('id', update.id)
      .eq('academy_id', academyId)
      .is('deleted_at', null)

    if (error) {
      console.error('Error reordering grade option:', error)
      throw new Error(`Failed to reorder grade options: ${error.message}`)
    }
  }
}

/**
 * Initialize default grade configuration and options for an academy
 * This is called when setting up a new academy
 */
export async function initializeDefaultGradeSystem(academyId: string): Promise<GradeConfigurationResponse> {
  // Create default configuration
  const configuration = await upsertGradeConfiguration(academyId, {
    field_label: GRADE_CONSTANTS.DEFAULT_FIELD_LABEL,
    show_all_option: true,
    all_grades_label: GRADE_CONSTANTS.DEFAULT_ALL_GRADES_LABEL
  })

  // Create default grade options matching current hardcoded values
  const defaultGrades = [
    { grade_value: 1, display_name: 'Grade 1', short_name: 'G1', sort_order: 10 },
    { grade_value: 2, display_name: 'Grade 2', short_name: 'G2', sort_order: 20 },
    { grade_value: 3, display_name: 'Grade 3', short_name: 'G3', sort_order: 30 },
    { grade_value: 4, display_name: 'Grade 4', short_name: 'G4', sort_order: 40 },
    { grade_value: 5, display_name: 'Grade 5', short_name: 'G5', sort_order: 50 },
    { grade_value: 6, display_name: 'Grade 6', short_name: 'G6', sort_order: 60 },
    { grade_value: 7, display_name: 'Middle 1', short_name: 'M1', sort_order: 70 },
    { grade_value: 8, display_name: 'Middle 2', short_name: 'M2', sort_order: 80 },
    { grade_value: 9, display_name: 'Middle 3', short_name: 'M3', sort_order: 90 },
    { grade_value: 10, display_name: 'High 1', short_name: 'H1', sort_order: 100 },
    { grade_value: 11, display_name: 'High 2', short_name: 'H2', sort_order: 110 },
    { grade_value: 12, display_name: 'High 3', short_name: 'H3', sort_order: 120 },
  ]

  const options: GradeOption[] = []
  for (const gradeData of defaultGrades) {
    try {
      const option = await createGradeOption(academyId, gradeData)
      options.push(option)
    } catch (error) {
      // Continue if grade already exists (duplicate key error)
      if (error instanceof Error && error.message.includes('duplicate')) {
        console.log(`Grade ${gradeData.grade_value} already exists for academy ${academyId}`)
      } else {
        throw error
      }
    }
  }

  return { configuration, options }
}

/**
 * Utility function for backward compatibility
 * Formats grade value using the new system, with fallback to old format
 */
export async function formatGradeDisplay(
  academyId: string, 
  gradeValue: GradeValue | null | undefined
): Promise<string> {
  if (!gradeValue) return '-'
  
  try {
    return await getGradeDisplayName(academyId, gradeValue)
  } catch (error) {
    console.warn('Failed to get grade display name, using fallback:', error)
    return `Grade ${gradeValue}`
  }
}

/**
 * Utility to convert grade value string to number for database operations
 */
export function parseGradeValue(value: GradeValueString): GradeValue | null {
  if (value === 'all' || value === '' || value == null) {
    return null
  }
  
  const parsed = parseInt(value, 10)
  if (isNaN(parsed)) {
    return null
  }
  
  return parsed
}