/**
 * Storage Debug API - Check file storage state
 * 
 * This temporary diagnostic endpoint helps identify storage issues.
 */

import { supabase } from '@/lib/supabaseClient'
import { getAcademyId } from '@/lib/academyUtils'

export async function GET(request: Request) {
  try {
    const academyId = await getAcademyId()
    
    // Get all exam files from database
    const { data: dbFiles, error: dbError } = await supabase
      .from('exam_files')
      .select('*')
      .eq('academy_id', academyId)
      .eq('is_active', true)
      .is('deleted_at', null)
      .order('created_at', { ascending: false })

    if (dbError) {
      console.error('Database query error:', dbError)
      return Response.json({ error: 'Database error', details: dbError.message }, { status: 500 })
    }

    const results = []

    // Check each file in storage
    for (const file of dbFiles || []) {
      try {
        // Try to get public URL
        const { data: urlData } = supabase.storage
          .from('PrimePath_Testmaterials')
          .getPublicUrl(file.file_path)
        
        // Try to check if file exists in storage
        const { data: existsData, error: existsError } = await supabase.storage
          .from('PrimePath_Testmaterials')
          .list('', {
            search: file.file_path
          })

        results.push({
          id: file.id,
          original_filename: file.original_filename,
          file_path: file.file_path,
          file_type: file.file_type,
          file_size_bytes: file.file_size_bytes,
          created_at: file.created_at,
          public_url: urlData.publicUrl,
          storage_exists: !existsError && existsData && existsData.length > 0,
          storage_error: existsError?.message || null
        })
      } catch (error) {
        results.push({
          id: file.id,
          original_filename: file.original_filename,
          file_path: file.file_path,
          error: error instanceof Error ? error.message : 'Unknown error'
        })
      }
    }

    // Also check bucket info
    const { data: buckets, error: bucketError } = await supabase.storage.listBuckets()
    
    return Response.json({
      academy_id: academyId,
      database_files_count: dbFiles?.length || 0,
      database_files: results,
      available_buckets: buckets || [],
      bucket_error: bucketError?.message || null,
      target_bucket: 'PrimePath_Testmaterials'
    })
    
  } catch (error) {
    console.error('Storage check error:', error)
    return Response.json({
      error: 'Failed to check storage',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}