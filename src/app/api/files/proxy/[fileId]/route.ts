/**
 * File Proxy API
 * 
 * Serves files through a secure proxy, handling both local and remote files.
 */

import { readFile } from 'fs/promises'
import { getAcademyId } from '@/lib/academyUtils'
import { supabase } from '@/lib/supabaseClient'
import { existsSync } from 'fs'

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
      return Response.json({ error: 'File not found' }, { status: 404 })
    }

    // Handle local files
    if (file.file_path.startsWith('/Users/') || file.file_path.startsWith('./')) {
      return await serveLocalFile(file)
    }

    // Handle Supabase files
    return await serveSupabaseFile(file)
    
  } catch (error) {
    console.error('File proxy error:', error)
    return Response.json({ 
      error: 'Failed to serve file',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

async function serveLocalFile(file: any): Promise<Response> {
  try {
    // Security check - ensure file is in allowed directories
    const allowedPaths = [
      '/Users/ian/Desktop/VIBECODE/PrimePath_v2/uploads/',
      './uploads/'
    ]
    
    const isAllowed = allowedPaths.some(allowedPath => file.file_path.startsWith(allowedPath))
    if (!isAllowed) {
      console.warn('Attempted access to unauthorized file path:', file.file_path)
      return Response.json({ error: 'Unauthorized file access' }, { status: 403 })
    }

    // Check if file exists
    if (!existsSync(file.file_path)) {
      return Response.json({ error: 'File not found on disk' }, { status: 404 })
    }

    // Read and serve file
    const fileBuffer = await readFile(file.file_path)
    
    return new Response(fileBuffer, {
      headers: {
        'Content-Type': file.mime_type || 'application/octet-stream',
        'Content-Length': fileBuffer.length.toString(),
        'Content-Disposition': `inline; filename="${file.original_filename}"`,
        'Cache-Control': 'public, max-age=3600'
      }
    })
    
  } catch (error) {
    console.error('Local file serve error:', error)
    return Response.json({ error: 'Failed to read local file' }, { status: 500 })
  }
}

async function serveSupabaseFile(file: any): Promise<Response> {
  try {
    // Try to download from Supabase and proxy it
    const { data, error } = await supabase.storage
      .from('PrimePath_Testmaterials')
      .download(file.file_path)

    if (error || !data) {
      return Response.json({ error: 'Failed to download from storage' }, { status: 404 })
    }

    return new Response(data, {
      headers: {
        'Content-Type': file.mime_type || 'application/octet-stream',
        'Content-Disposition': `inline; filename="${file.original_filename}"`,
        'Cache-Control': 'public, max-age=3600'
      }
    })
    
  } catch (error) {
    console.error('Supabase file serve error:', error)
    return Response.json({ error: 'Failed to serve from storage' }, { status: 500 })
  }
}

export async function HEAD(
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
      return new Response(null, { status: 404 })
    }

    // Quick existence check
    if (file.file_path.startsWith('/Users/') || file.file_path.startsWith('./')) {
      const exists = existsSync(file.file_path)
      return new Response(null, { 
        status: exists ? 200 : 404,
        headers: {
          'Content-Type': file.mime_type || 'application/octet-stream',
          'Content-Length': file.file_size_bytes?.toString() || '0'
        }
      })
    }

    // For Supabase files, return OK if database record exists
    return new Response(null, { 
      status: 200,
      headers: {
        'Content-Type': file.mime_type || 'application/octet-stream',
        'Content-Length': file.file_size_bytes?.toString() || '0'
      }
    })
    
  } catch (error) {
    return new Response(null, { status: 500 })
  }
}