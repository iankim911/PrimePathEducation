/**
 * Test Storage Manager API
 */

import { getFileUrl } from '@/lib/services/storageManager'
import { supabase } from '@/lib/supabaseClient'
import { getAcademyId } from '@/lib/academyUtils'

export async function GET(request: Request) {
  try {
    const academyId = await getAcademyId()
    
    // Get a known PDF file from the database
    const { data: file, error } = await supabase
      .from('exam_files')
      .select('*')
      .eq('academy_id', academyId)
      .eq('file_type', 'pdf')
      .eq('is_active', true)
      .is('deleted_at', null)
      .limit(1)
      .single()

    if (error || !file) {
      return Response.json({ error: 'No PDF files found', details: error?.message })
    }

    // Test the storage manager
    const result = await getFileUrl(file)
    
    return Response.json({
      file_info: {
        id: file.id,
        original_filename: file.original_filename,
        file_path: file.file_path,
        file_type: file.file_type
      },
      storage_result: result
    })
    
  } catch (error) {
    return Response.json({
      error: 'Test failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}