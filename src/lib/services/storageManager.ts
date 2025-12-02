/**
 * Storage Manager Service
 * 
 * Provides robust file access with fallback mechanisms and error handling.
 * Handles both Supabase storage and local fallbacks.
 */

import { supabase } from '@/lib/supabaseClient'

// Define ExamFile type locally to avoid circular imports
export interface ExamFile {
  id: string
  academy_id: string
  exam_id: string | null
  section_id: string | null
  filename: string
  original_filename: string
  file_path: string
  file_type: 'pdf' | 'image' | 'audio'
  mime_type: string
  file_size_bytes: number
  title: string | null
  description: string | null
  sort_order: number
  rotation_degrees: number
  zoom_level: number
  ocr_text: string | null
  audio_duration_seconds: number | null
  audio_transcript: string | null
  processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  metadata: any | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface StorageConfig {
  bucketName: string
  maxRetries: number
  fallbackEnabled: boolean
  signedUrlExpiry: number
}

export const STORAGE_CONFIG: StorageConfig = {
  bucketName: 'PrimePath_Testmaterials',
  maxRetries: 3,
  fallbackEnabled: true,
  signedUrlExpiry: 3600 // 1 hour
}

export interface FileAccessResult {
  success: boolean
  url?: string
  method: 'public' | 'signed' | 'local' | 'error'
  error?: string
  retries?: number
}

/**
 * Get the best available URL for a file with fallback mechanisms
 */
export async function getFileUrl(file: ExamFile): Promise<FileAccessResult> {
  // Skip if file doesn't exist in database
  if (!file || !file.file_path) {
    return {
      success: false,
      method: 'error',
      error: 'File record not found or invalid'
    }
  }

  // Handle local files (audio files stored locally during development)
  if (file.file_path.startsWith('/Users/') || file.file_path.startsWith('./')) {
    return await handleLocalFile(file)
  }

  // Try Supabase storage methods
  return await handleSupabaseFile(file)
}

/**
 * Handle files stored in Supabase storage
 */
async function handleSupabaseFile(file: ExamFile): Promise<FileAccessResult> {
  let retries = 0
  
  // Method 1: Try public URL first
  try {
    const { data: urlData } = supabase.storage
      .from(STORAGE_CONFIG.bucketName)
      .getPublicUrl(file.file_path)
    
    // Test if public URL is accessible
    const isPublicAccessible = await testUrl(urlData.publicUrl)
    if (isPublicAccessible) {
      return {
        success: true,
        url: urlData.publicUrl,
        method: 'public',
        retries
      }
    }
  } catch (error) {
    console.warn('Public URL failed:', error)
  }

  // Method 2: Try signed URL
  try {
    const { data: signedData, error: signedError } = await supabase.storage
      .from(STORAGE_CONFIG.bucketName)
      .createSignedUrl(file.file_path, STORAGE_CONFIG.signedUrlExpiry)
    
    if (signedError) throw signedError
    
    if (signedData?.signedUrl) {
      const isSignedAccessible = await testUrl(signedData.signedUrl)
      if (isSignedAccessible) {
        return {
          success: true,
          url: signedData.signedUrl,
          method: 'signed',
          retries
        }
      }
    }
  } catch (error) {
    console.warn('Signed URL failed:', error)
  }

  // Method 3: Create bucket if it doesn't exist and retry
  try {
    await ensureBucketExists()
    retries++
    
    // Retry signed URL after ensuring bucket exists
    const { data: signedData, error: signedError } = await supabase.storage
      .from(STORAGE_CONFIG.bucketName)
      .createSignedUrl(file.file_path, STORAGE_CONFIG.signedUrlExpiry)
    
    if (!signedError && signedData?.signedUrl) {
      return {
        success: true,
        url: signedData.signedUrl,
        method: 'signed',
        retries
      }
    }
  } catch (error) {
    console.warn('Bucket creation/retry failed:', error)
  }

  return {
    success: false,
    method: 'error',
    error: 'All Supabase storage methods failed',
    retries
  }
}

/**
 * Handle locally stored files with API proxy
 */
async function handleLocalFile(file: ExamFile): Promise<FileAccessResult> {
  try {
    // Create a proxied URL through our API for local files
    const localUrl = `/api/files/proxy/${encodeURIComponent(file.id)}`
    
    // Test if the local file is accessible through our API
    const response = await fetch(localUrl, { method: 'HEAD' })
    if (response.ok) {
      return {
        success: true,
        url: localUrl,
        method: 'local'
      }
    }
  } catch (error) {
    console.warn('Local file access failed:', error)
  }

  return {
    success: false,
    method: 'error',
    error: 'Local file not accessible'
  }
}

/**
 * Test if a URL is accessible (server-side only)
 */
async function testUrl(url: string): Promise<boolean> {
  // Skip URL testing in browser environment
  if (typeof window !== 'undefined') {
    return true
  }
  
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout
    
    const response = await fetch(url, { 
      method: 'HEAD',
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    return response.ok
  } catch (error) {
    return false
  }
}

/**
 * Ensure the storage bucket exists and is properly configured
 */
async function ensureBucketExists(): Promise<void> {
  try {
    // Check if bucket exists
    const { data: buckets, error: listError } = await supabase.storage.listBuckets()
    
    if (listError) {
      console.error('Failed to list buckets:', listError)
      return
    }

    const bucketExists = buckets?.some(bucket => bucket.name === STORAGE_CONFIG.bucketName)
    
    if (!bucketExists) {
      // Create bucket
      const { error: createError } = await supabase.storage.createBucket(STORAGE_CONFIG.bucketName, {
        public: true,
        allowedMimeTypes: ['application/pdf', 'image/*', 'audio/*'],
        fileSizeLimit: 100 * 1024 * 1024 // 100MB
      })
      
      if (createError) {
        console.error('Failed to create bucket:', createError)
        throw createError
      }
      
      console.log(`Created storage bucket: ${STORAGE_CONFIG.bucketName}`)
    }
  } catch (error) {
    console.error('Bucket management error:', error)
    throw error
  }
}

/**
 * Batch get URLs for multiple files
 */
export async function getBatchFileUrls(files: ExamFile[]): Promise<Map<string, FileAccessResult>> {
  const results = new Map<string, FileAccessResult>()
  
  // Process files concurrently but limit concurrency
  const BATCH_SIZE = 5
  for (let i = 0; i < files.length; i += BATCH_SIZE) {
    const batch = files.slice(i, i + BATCH_SIZE)
    const batchPromises = batch.map(async (file) => {
      const result = await getFileUrl(file)
      return { fileId: file.id, result }
    })
    
    const batchResults = await Promise.all(batchPromises)
    batchResults.forEach(({ fileId, result }) => {
      results.set(fileId, result)
    })
  }
  
  return results
}

/**
 * Initialize storage system - call this on app startup
 */
export async function initializeStorage(): Promise<{ success: boolean; message: string }> {
  try {
    await ensureBucketExists()
    return {
      success: true,
      message: 'Storage system initialized successfully'
    }
  } catch (error) {
    return {
      success: false,
      message: `Storage initialization failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    }
  }
}