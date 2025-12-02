/**
 * File URL API
 * 
 * Returns the best available URL for a file using the storage manager.
 */

import { getFileUrl } from '@/lib/services/storageManager'
import { supabase } from '@/lib/supabaseClient'
import { getAcademyId } from '@/lib/academyUtils'

export async function GET(
  request: Request,
  context: { params: Promise<{ fileId: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    
    // Get file record from database
    const { data: file, error } = await supabase
      .from('exam_files')
      .select('*')
      .eq('id', params.fileId)
      .eq('academy_id', academyId)
      .eq('is_active', true)
      .is('deleted_at', null)
      .single()

    if (error || !file) {
      return Response.json({ 
        success: false,
        error: 'File not found'
      }, { status: 404 })
    }

    // Use storage manager to get the best URL
    const result = await getFileUrl(file)
    
    if (result.success) {
      return Response.json({
        success: true,
        url: result.url,
        method: result.method,
        file_info: {
          id: file.id,
          original_filename: file.original_filename,
          file_type: file.file_type,
          mime_type: file.mime_type
        }
      })
    } else {
      return Response.json({
        success: false,
        error: result.error || 'Failed to get file URL',
        method: result.method
      }, { status: 500 })
    }
    
  } catch (error) {
    console.error('File URL API error:', error)
    return Response.json({
      success: false,
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}