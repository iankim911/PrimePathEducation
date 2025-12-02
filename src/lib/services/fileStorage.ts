/**
 * File Storage Service Layer
 * 
 * This service handles secure file upload, storage, and access for exam materials.
 * Components should use these service functions for all file operations.
 */

import { supabase } from '@/lib/supabaseClient'
import { ExamFile } from './exams'

/**
 * File upload configuration
 */
export interface FileUploadConfig {
  maxSizeBytes: number
  allowedTypes: string[]
  allowedMimeTypes: string[]
}

export const FILE_UPLOAD_CONFIGS = {
  pdf: {
    maxSizeBytes: 50 * 1024 * 1024, // 50MB
    allowedTypes: ['pdf'],
    allowedMimeTypes: ['application/pdf']
  },
  image: {
    maxSizeBytes: 10 * 1024 * 1024, // 10MB  
    allowedTypes: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    allowedMimeTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  },
  audio: {
    maxSizeBytes: 100 * 1024 * 1024, // 100MB
    allowedTypes: ['mp3', 'wav', 'm4a', 'aac', 'ogg'],
    allowedMimeTypes: ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/aac', 'audio/ogg']
  }
}

/**
 * File upload result interface
 */
export interface FileUploadResult {
  file: ExamFile
  uploadPath: string
  publicUrl?: string
}

/**
 * Validate file for upload
 */
export function validateFile(
  file: File, 
  fileType: 'pdf' | 'image' | 'audio'
): { valid: boolean; error?: string } {
  const config = FILE_UPLOAD_CONFIGS[fileType]
  
  // Check file size
  if (file.size > config.maxSizeBytes) {
    return {
      valid: false,
      error: `File size exceeds maximum allowed (${Math.round(config.maxSizeBytes / (1024 * 1024))}MB)`
    }
  }

  // Check MIME type
  if (!config.allowedMimeTypes.includes(file.type)) {
    return {
      valid: false,
      error: `File type ${file.type} is not allowed for ${fileType} files`
    }
  }

  // Check file extension
  const extension = file.name.split('.').pop()?.toLowerCase()
  if (!extension || !config.allowedTypes.includes(extension)) {
    return {
      valid: false,
      error: `File extension .${extension} is not allowed for ${fileType} files`
    }
  }

  return { valid: true }
}

/**
 * Generate secure file path for storage
 */
export function generateFilePath(
  academyId: string,
  fileType: 'pdf' | 'image' | 'audio',
  originalFilename: string
): { filePath: string; filename: string } {
  const timestamp = new Date().toISOString().split('T')[0].replace(/-/g, '')
  const randomId = Math.random().toString(36).substring(2, 15)
  const extension = originalFilename.split('.').pop()?.toLowerCase() || ''
  
  const filename = `${timestamp}_${randomId}.${extension}`
  const filePath = `academies/${academyId}/exams/${fileType}s/${filename}`
  
  return { filePath, filename }
}

/**
 * Upload file to Supabase storage
 */
export async function uploadFile(
  file: File,
  academyId: string,
  fileType: 'pdf' | 'image' | 'audio',
  examId?: string,
  sectionId?: string
): Promise<FileUploadResult> {
  // Validate file
  const validation = validateFile(file, fileType)
  if (!validation.valid) {
    throw new Error(validation.error || 'File validation failed')
  }

  // Generate file path
  const { filePath, filename } = generateFilePath(academyId, fileType, file.name)

  try {
    // Upload to Supabase Storage
    const { data: uploadData, error: uploadError } = await supabase.storage
      .from('PrimePath_Testmaterials')
      .upload(filePath, file, {
        cacheControl: '3600',
        upsert: false
      })

    if (uploadError) {
      console.error('Error uploading file:', uploadError)
      throw new Error(`Failed to upload file: ${uploadError.message}`)
    }

    // Get public URL
    const { data: urlData } = supabase.storage
      .from('PrimePath_Testmaterials')
      .getPublicUrl(filePath)

    // Save file record to database
    const fileRecord: Omit<ExamFile, 'id' | 'created_at' | 'updated_at' | 'deleted_at'> = {
      academy_id: academyId,
      exam_id: examId || null,
      section_id: sectionId || null,
      filename,
      original_filename: file.name,
      file_path: filePath,
      file_type: fileType,
      mime_type: file.type,
      file_size_bytes: file.size,
      title: file.name,
      description: null,
      sort_order: 0,
      rotation_degrees: 0,
      zoom_level: 1.0,
      ocr_text: null,
      audio_duration_seconds: null,
      audio_transcript: null,
      processing_status: 'pending',
      metadata: null,
      is_active: true
    }

    const { data: dbRecord, error: dbError } = await supabase
      .from('exam_files')
      .insert(fileRecord)
      .select()
      .single()

    if (dbError) {
      // Clean up uploaded file if database insert fails
      await supabase.storage
        .from('PrimePath_Testmaterials')
        .remove([filePath])
      
      console.error('Error saving file record:', dbError)
      throw new Error(`Failed to save file record: ${dbError.message}`)
    }

    return {
      file: dbRecord,
      uploadPath: uploadData.path,
      publicUrl: urlData.publicUrl
    }

  } catch (error) {
    console.error('File upload failed:', error)
    throw error
  }
}

/**
 * Get file by ID with access control
 */
export async function getFile(
  fileId: string,
  academyId: string
): Promise<ExamFile | null> {
  const { data, error } = await supabase
    .from('exam_files')
    .select('*')
    .eq('id', fileId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .single()

  if (error) {
    console.error('Error fetching file:', error)
    return null
  }

  return data
}

/**
 * Get files for an exam
 */
export async function getFilesByExam(
  examId: string,
  academyId: string,
  fileType?: 'pdf' | 'image' | 'audio'
): Promise<ExamFile[]> {
  let query = supabase
    .from('exam_files')
    .select('*')
    .eq('exam_id', examId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)

  if (fileType) {
    query = query.eq('file_type', fileType)
  }

  const { data, error } = await query.order('sort_order', { ascending: true })

  if (error) {
    console.error('Error fetching files:', error)
    throw new Error(`Failed to fetch files: ${error.message}`)
  }

  return data || []
}

/**
 * Update file metadata
 */
export async function updateFile(
  fileId: string,
  academyId: string,
  updates: {
    title?: string
    description?: string
    rotation_degrees?: number
    zoom_level?: number
    sort_order?: number
  }
): Promise<ExamFile> {
  const { data, error } = await supabase
    .from('exam_files')
    .update({
      ...updates,
      updated_at: new Date().toISOString()
    })
    .eq('id', fileId)
    .eq('academy_id', academyId)
    .select()
    .single()

  if (error) {
    console.error('Error updating file:', error)
    throw new Error(`Failed to update file: ${error.message}`)
  }

  return data
}

/**
 * Delete file (soft delete + storage cleanup)
 */
export async function deleteFile(
  fileId: string,
  academyId: string
): Promise<void> {
  // Get file record to access file path
  const file = await getFile(fileId, academyId)
  if (!file) {
    throw new Error('File not found')
  }

  try {
    // Soft delete in database first
    const { error: dbError } = await supabase
      .from('exam_files')
      .update({
        deleted_at: new Date().toISOString(),
        is_active: false,
        updated_at: new Date().toISOString()
      })
      .eq('id', fileId)
      .eq('academy_id', academyId)

    if (dbError) {
      console.error('Error soft deleting file:', dbError)
      throw new Error(`Failed to delete file record: ${dbError.message}`)
    }

    // Remove from storage (optional - could be done in background)
    const { error: storageError } = await supabase.storage
      .from('PrimePath_Testmaterials')
      .remove([file.file_path])

    if (storageError) {
      console.warn('Warning: Failed to remove file from storage:', storageError)
      // Don't throw error here - file record is already marked as deleted
    }

  } catch (error) {
    console.error('File deletion failed:', error)
    throw error
  }
}

/**
 * Generate secure download URL for file
 */
export async function generateDownloadUrl(
  fileId: string,
  academyId: string,
  expiresInSeconds: number = 3600 // 1 hour default
): Promise<string> {
  const file = await getFile(fileId, academyId)
  if (!file) {
    throw new Error('File not found')
  }

  const { data, error } = await supabase.storage
    .from('PrimePath_Testmaterials')
    .createSignedUrl(file.file_path, expiresInSeconds)

  if (error) {
    console.error('Error generating download URL:', error)
    throw new Error(`Failed to generate download URL: ${error.message}`)
  }

  return data.signedUrl
}

/**
 * Get file statistics for an academy
 */
export async function getFileStatistics(academyId: string): Promise<{
  totalFiles: number
  totalSizeBytes: number
  filesByType: { pdf: number; image: number; audio: number }
  processingFiles: number
}> {
  const { data, error } = await supabase
    .from('exam_files')
    .select('file_type, file_size_bytes, processing_status')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)

  if (error) {
    console.error('Error fetching file statistics:', error)
    throw new Error(`Failed to fetch file statistics: ${error.message}`)
  }

  const files = data || []
  const totalSizeBytes = files.reduce((sum, f) => sum + f.file_size_bytes, 0)

  return {
    totalFiles: files.length,
    totalSizeBytes,
    filesByType: {
      pdf: files.filter(f => f.file_type === 'pdf').length,
      image: files.filter(f => f.file_type === 'image').length,
      audio: files.filter(f => f.file_type === 'audio').length
    },
    processingFiles: files.filter(f => f.processing_status === 'processing').length
  }
}

/**
 * Search files by name or title
 */
export async function searchFiles(
  academyId: string,
  searchTerm: string,
  fileType?: 'pdf' | 'image' | 'audio'
): Promise<ExamFile[]> {
  let query = supabase
    .from('exam_files')
    .select('*')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)

  if (fileType) {
    query = query.eq('file_type', fileType)
  }

  // Search in filename, original_filename, and title
  query = query.or(`filename.ilike.%${searchTerm}%,original_filename.ilike.%${searchTerm}%,title.ilike.%${searchTerm}%`)

  const { data, error } = await query
    .order('created_at', { ascending: false })
    .limit(50)

  if (error) {
    console.error('Error searching files:', error)
    throw new Error(`Failed to search files: ${error.message}`)
  }

  return data || []
}