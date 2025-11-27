/**
 * Shared utilities for academy operations
 */

import { supabase } from './supabaseClient'

/**
 * Get the academy ID from the database
 * In production, this would come from the authenticated user's session
 */
export async function getAcademyId(): Promise<string> {
  const { data } = await supabase
    .from('academies')
    .select('id')
    .eq('slug', 'my-academy')
    .single()
  
  if (!data) {
    throw new Error('Academy not found')
  }
  
  return data.id
}