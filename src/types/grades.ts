/**
 * Grade Configuration System Types
 * 
 * These types define the structure for the configurable grade management system
 * that replaces hardcoded grade dropdowns throughout the application.
 */

/**
 * Grade Configuration - Academy-level settings for grade system
 */
export interface GradeConfiguration {
  id: string
  academy_id: string
  
  // Field customization
  field_label: string        // "Target Grade", "Year Level", "Academic Level", etc.
  show_all_option: boolean   // Whether to show "All Grades" option in dropdowns
  all_grades_label: string   // Label for "All Grades" option
  
  // Metadata
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Grade Option - Individual grade choices available in the academy
 */
export interface GradeOption {
  id: string
  academy_id: string
  
  // Grade details
  grade_value: number        // Numeric value for database storage (1, 2, 7, 10, etc.)
  display_name: string       // Full display name ("Grade 1", "Middle 1", "Year 7", etc.)
  short_name?: string | null // Short version ("G1", "M1", "Y7", etc.) 
  sort_order: number         // Order in dropdowns
  
  // Metadata
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Combined view for easy consumption by components
 */
export interface GradeOptionFormatted extends GradeOption {
  // Configuration details for convenience
  field_label: string
  show_all_option: boolean
  all_grades_label: string
}

/**
 * Grade dropdown item for UI components
 */
export interface GradeDropdownItem {
  value: string              // String representation for form values
  label: string              // Display text
  grade_value?: number       // Original numeric value (undefined for "all" option)
  sort_order: number
}

/**
 * Request types for API endpoints
 */
export interface CreateGradeConfigurationRequest {
  field_label: string
  show_all_option: boolean
  all_grades_label: string
}

export interface UpdateGradeConfigurationRequest {
  field_label?: string
  show_all_option?: boolean
  all_grades_label?: string
}

export interface CreateGradeOptionRequest {
  grade_value: number
  display_name: string
  short_name?: string
  sort_order: number
}

export interface UpdateGradeOptionRequest {
  grade_value?: number
  display_name?: string
  short_name?: string
  sort_order?: number
  is_active?: boolean
}

export interface ReorderGradeOptionsRequest {
  grade_option_ids: string[] // Array of IDs in new order
}

/**
 * Response types
 */
export interface GradeConfigurationResponse {
  configuration: GradeConfiguration
  options: GradeOption[]
}

export interface GradeOptionsResponse {
  options: GradeOption[]
  configuration: GradeConfiguration
}

/**
 * Utility types for grade validation
 */
export type GradeValue = number
export type GradeValueString = string | 'all'

/**
 * Grade system constants
 */
export const GRADE_CONSTANTS = {
  DEFAULT_FIELD_LABEL: 'Target Grade',
  DEFAULT_ALL_GRADES_LABEL: 'All Grades',
  ALL_GRADES_VALUE: 'all',
  MIN_GRADE_VALUE: 1,
  MAX_GRADE_VALUE: 15, // Allow for international systems with extra years
  DEFAULT_SORT_INCREMENT: 10 // Space between sort_order values for easy reordering
} as const

/**
 * Validation schemas (for use with form validation libraries)
 */
export const gradeValidationRules = {
  field_label: {
    required: true,
    minLength: 1,
    maxLength: 50
  },
  all_grades_label: {
    required: true,
    minLength: 1,
    maxLength: 50
  },
  display_name: {
    required: true,
    minLength: 1,
    maxLength: 100
  },
  short_name: {
    maxLength: 20
  },
  grade_value: {
    required: true,
    min: GRADE_CONSTANTS.MIN_GRADE_VALUE,
    max: GRADE_CONSTANTS.MAX_GRADE_VALUE,
    integer: true
  }
} as const