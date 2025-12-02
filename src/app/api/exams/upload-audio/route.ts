import { NextRequest } from 'next/server'
import { getAcademyId } from '@/lib/academyUtils'
import { supabase } from '@/lib/supabaseClient'
import path from 'path'
import { promises as fs } from 'fs'

/**
 * POST /api/exams/upload-audio
 * Handles audio file uploads for exams
 */
export async function POST(req: NextRequest) {
  try {
    const academyId = await getAcademyId()
    const formData = await req.formData()
    
    const file = formData.get('audio') as File
    const examId = formData.get('examId') as string
    const title = formData.get('title') as string
    const description = formData.get('description') as string
    
    if (!file) {
      return Response.json(
        { error: 'No audio file provided' },
        { status: 400 }
      )
    }

    // Validate file type
    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/m4a', 'audio/mp3']
    if (!allowedTypes.includes(file.type)) {
      return Response.json(
        { error: 'Invalid file type. Please upload MP3, WAV, or M4A files.' },
        { status: 400 }
      )
    }

    // Validate file size (max 50MB)
    const maxSize = 50 * 1024 * 1024 // 50MB
    if (file.size > maxSize) {
      return Response.json(
        { error: 'File size exceeds 50MB limit' },
        { status: 400 }
      )
    }

    // Create uploads directory if it doesn't exist
    const uploadDir = path.join(process.cwd(), 'uploads', 'audio')
    try {
      await fs.access(uploadDir)
    } catch {
      await fs.mkdir(uploadDir, { recursive: true })
    }

    // Generate unique filename
    const timestamp = Date.now()
    const fileExtension = path.extname(file.name)
    const filename = `${timestamp}_${file.name.replace(/[^a-zA-Z0-9.-]/g, '_')}`
    const filepath = path.join(uploadDir, filename)

    // Save file to disk
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    await fs.writeFile(filepath, buffer)

    // Save file record to database
    const { data: audioFile, error } = await supabase
      .from('exam_files')
      .insert({
        academy_id: academyId,
        exam_id: examId || null,
        filename: filename,
        original_filename: file.name,
        file_path: filepath,
        file_type: 'audio',
        mime_type: file.type,
        file_size_bytes: file.size,
        title: title || file.name,
        description: description || null,
        sort_order: 0,
        processing_status: 'completed',
        is_active: true
      })
      .select()
      .single()

    if (error) {
      console.error('Database error:', error)
      // Clean up uploaded file on database error
      try {
        await fs.unlink(filepath)
      } catch (cleanupError) {
        console.error('Error cleaning up file:', cleanupError)
      }
      
      return Response.json(
        { error: 'Failed to save audio file record to database' },
        { status: 500 }
      )
    }

    return Response.json({
      success: true,
      file: audioFile,
      message: 'Audio file uploaded successfully'
    })

  } catch (error) {
    console.error('Error uploading audio file:', error)
    return Response.json(
      { 
        error: 'Failed to upload audio file',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}