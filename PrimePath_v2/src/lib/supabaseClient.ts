/**
 * Supabase Client Configuration
 * 
 * IMPORTANT: This is the ONLY place where the Supabase client should be created.
 * All data access should go through service functions in src/lib/services.
 * 
 * Never import createClient directly in components or pages.
 * Always use the exported supabase instance from this file.
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://demo.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkZW1vIiwicm9sZSI6ImFub24ifQ.demo_key'

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(
    'Missing Supabase environment variables. Using demo values. Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in your .env.local file.'
  )
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    detectSessionInUrl: true,
    autoRefreshToken: true,
  },
  db: {
    schema: 'public',
  },
  global: {
    headers: {
      'x-application-name': 'PrimePath LMS',
    },
  },
})

export type SupabaseClient = typeof supabase