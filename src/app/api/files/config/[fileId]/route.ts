/**
 * PDF Configuration API
 * 
 * Saves and retrieves PDF display configuration (rotation, zoom, split settings)
 */

import { supabase } from '@/lib/supabaseClient'
import { getAcademyId } from '@/lib/academyUtils'

interface PDFConfiguration {
  rotation_degrees?: number
  zoom_level?: number
  is_split_enabled?: boolean
  split_orientation?: 'vertical' | 'horizontal'
  split_page_1_position?: 'left' | 'right' | 'top' | 'bottom'
  split_page_2_position?: 'left' | 'right' | 'top' | 'bottom'
}

export async function GET(
  request: Request,
  context: { params: Promise<{ fileId: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    
    // Get file configuration from database
    const { data: file, error } = await supabase
      .from('exam_files')
      .select(`
        id,
        rotation_degrees,
        zoom_level,
        is_split_enabled,
        split_orientation,
        split_page_1_position,
        split_page_2_position
      `)
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

    return Response.json({
      success: true,
      configuration: {
        rotation_degrees: file.rotation_degrees || 0,
        zoom_level: file.zoom_level || 1.0,
        is_split_enabled: file.is_split_enabled || false,
        split_orientation: file.split_orientation || 'vertical',
        split_page_1_position: file.split_page_1_position || 'left',
        split_page_2_position: file.split_page_2_position || 'right'
      }
    })
    
  } catch (error) {
    console.error('PDF Configuration GET error:', error)
    return Response.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 })
  }
}

export async function PUT(
  request: Request,
  context: { params: Promise<{ fileId: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const configuration: PDFConfiguration = await request.json()
    
    // Validate file exists and belongs to this academy
    const { data: existingFile, error: findError } = await supabase
      .from('exam_files')
      .select('id, file_type')
      .eq('id', params.fileId)
      .eq('academy_id', academyId)
      .eq('is_active', true)
      .is('deleted_at', null)
      .single()

    if (findError || !existingFile) {
      return Response.json({ 
        success: false,
        error: 'File not found'
      }, { status: 404 })
    }

    if (existingFile.file_type !== 'pdf') {
      return Response.json({ 
        success: false,
        error: 'Configuration can only be saved for PDF files'
      }, { status: 400 })
    }

    // Validate configuration values
    const updateData: Record<string, any> = {
      updated_at: new Date().toISOString()
    }

    if (configuration.rotation_degrees !== undefined) {
      if (typeof configuration.rotation_degrees !== 'number' || configuration.rotation_degrees % 90 !== 0) {
        return Response.json({ 
          success: false,
          error: 'Rotation must be a multiple of 90 degrees'
        }, { status: 400 })
      }
      updateData.rotation_degrees = configuration.rotation_degrees
    }

    if (configuration.zoom_level !== undefined) {
      if (typeof configuration.zoom_level !== 'number' || configuration.zoom_level < 0.5 || configuration.zoom_level > 2.0) {
        return Response.json({ 
          success: false,
          error: 'Zoom level must be between 0.5 and 2.0'
        }, { status: 400 })
      }
      updateData.zoom_level = configuration.zoom_level
    }

    if (configuration.is_split_enabled !== undefined) {
      updateData.is_split_enabled = Boolean(configuration.is_split_enabled)
    }

    if (configuration.split_orientation !== undefined) {
      if (!['vertical', 'horizontal'].includes(configuration.split_orientation)) {
        return Response.json({ 
          success: false,
          error: 'Split orientation must be vertical or horizontal'
        }, { status: 400 })
      }
      updateData.split_orientation = configuration.split_orientation
    }

    if (configuration.split_page_1_position !== undefined) {
      if (!['left', 'right', 'top', 'bottom'].includes(configuration.split_page_1_position)) {
        return Response.json({ 
          success: false,
          error: 'Invalid split page 1 position'
        }, { status: 400 })
      }
      updateData.split_page_1_position = configuration.split_page_1_position
    }

    if (configuration.split_page_2_position !== undefined) {
      if (!['left', 'right', 'top', 'bottom'].includes(configuration.split_page_2_position)) {
        return Response.json({ 
          success: false,
          error: 'Invalid split page 2 position'
        }, { status: 400 })
      }
      updateData.split_page_2_position = configuration.split_page_2_position
    }

    // Update the file configuration
    const { data: updatedFile, error: updateError } = await supabase
      .from('exam_files')
      .update(updateData)
      .eq('id', params.fileId)
      .eq('academy_id', academyId)
      .select(`
        id,
        rotation_degrees,
        zoom_level,
        is_split_enabled,
        split_orientation,
        split_page_1_position,
        split_page_2_position
      `)
      .single()

    if (updateError) {
      console.error('Database update error:', updateError)
      return Response.json({
        success: false,
        error: 'Failed to update configuration'
      }, { status: 500 })
    }

    return Response.json({
      success: true,
      configuration: {
        rotation_degrees: updatedFile.rotation_degrees || 0,
        zoom_level: updatedFile.zoom_level || 1.0,
        is_split_enabled: updatedFile.is_split_enabled || false,
        split_orientation: updatedFile.split_orientation || 'vertical',
        split_page_1_position: updatedFile.split_page_1_position || 'left',
        split_page_2_position: updatedFile.split_page_2_position || 'right'
      }
    })
    
  } catch (error) {
    console.error('PDF Configuration PUT error:', error)
    return Response.json({
      success: false,
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}