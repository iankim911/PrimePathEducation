/**
 * Curriculum Database Initialization Service
 * 
 * This service handles safe initialization of curriculum tables.
 * It checks if tables exist and creates them if needed, ensuring
 * the system works gracefully whether tables exist or not.
 */

import { supabase } from '@/lib/supabaseClient'

/**
 * Check if curriculum tables exist in the database
 */
export async function checkCurriculumTablesExist(): Promise<{
  settingsTableExists: boolean
  nodesTableExists: boolean
}> {
  try {
    // Try to query the curriculum_settings table
    const { error: settingsError } = await supabase
      .from('curriculum_settings')
      .select('id')
      .limit(1)
    
    // Try to query the curriculum_nodes table
    const { error: nodesError } = await supabase
      .from('curriculum_nodes')
      .select('id')
      .limit(1)
    
    // Table exists only if there's no error
    // Any error (42P01, schema cache, permissions) means table is not accessible
    const settingsTableExists = !settingsError
    const nodesTableExists = !nodesError
    
    console.log('Table check results:', {
      settingsError: settingsError?.message || null,
      nodesError: nodesError?.message || null,
      settingsTableExists,
      nodesTableExists
    })
    
    return {
      settingsTableExists,
      nodesTableExists
    }
  } catch (error) {
    console.error('Error checking curriculum tables:', error)
    return {
      settingsTableExists: false,
      nodesTableExists: false
    }
  }
}

/**
 * Initialize curriculum tables in the database
 * This creates the tables if they don't exist
 */
export async function initializeCurriculumTables(): Promise<{
  success: boolean
  message: string
  error?: any
}> {
  // For now, return instructions for manual setup since automated table creation
  // via RPC is not available in this Supabase instance
  return {
    success: false,
    message: `Database tables need to be created manually. Please run the SQL script:

STEP 1: Open Supabase Dashboard (https://jkqatbcpezsbmlsmlkxj.supabase.co)
STEP 2: Go to SQL Editor
STEP 3: Copy and paste this SQL script:

CREATE TABLE IF NOT EXISTS curriculum_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
  max_depth INTEGER NOT NULL DEFAULT 4 CHECK (max_depth >= 1 AND max_depth <= 4),
  level_1_name VARCHAR(50) DEFAULT 'Category',
  level_2_name VARCHAR(50) DEFAULT 'Sub-Category', 
  level_3_name VARCHAR(50) DEFAULT 'Level',
  level_4_name VARCHAR(50) DEFAULT 'Sub-Level',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS curriculum_nodes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
  parent_id UUID REFERENCES curriculum_nodes(id) ON DELETE CASCADE,
  level_depth INTEGER NOT NULL CHECK (level_depth >= 1 AND level_depth <= 4),
  sort_order INTEGER NOT NULL DEFAULT 0,
  name VARCHAR(255) NOT NULL,
  code VARCHAR(50),
  description TEXT,
  target_grade_min INTEGER,
  target_grade_max INTEGER, 
  capacity INTEGER,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

STEP 4: Click 'Run' to execute
STEP 5: Refresh this page`,
    error: 'Manual database setup required'
  }
}

/**
 * Get safe fallback response when tables don't exist
 */
export function getCurriculumFallbackResponse() {
  return {
    settings: null,
    tree: null,
    nodes: [],
    message: 'Curriculum system not initialized',
    requiresInit: true
  }
}