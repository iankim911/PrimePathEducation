/**
 * Exam File Upload API Route
 * 
 * Handles secure file uploads for exams (PDFs, images, audio).
 */

import { uploadFile, validateFile } from '@/lib/services/fileStorage'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * POST /api/exam-files/upload
 * 
 * Uploads a file and creates a database record.
 */
export async function POST(request: Request) {
  try {
    const academyId = await getAcademyId()
    const formData = await request.formData()
    
    const file = formData.get('file') as File
    const fileType = formData.get('fileType') as 'pdf' | 'image' | 'audio'
    const examId = formData.get('examId') as string || undefined
    const sectionId = formData.get('sectionId') as string || undefined
    
    // Validate required fields
    if (!file) {
      return Response.json(
        { error: 'No file provided' },
        { status: 400 }
      )
    }
    
    if (!fileType || !['pdf', 'image', 'audio'].includes(fileType)) {
      return Response.json(
        { error: 'fileType is required and must be pdf, image, or audio' },
        { status: 400 }
      )
    }
    
    // Validate file
    const validation = validateFile(file, fileType)
    if (!validation.valid) {
      return Response.json(
        { error: validation.error },
        { status: 400 }
      )
    }
    
    try {
      // Upload file using service layer
      const result = await uploadFile(file, academyId, fileType, examId, sectionId)
      
      return Response.json(
        { 
          file: result.file,
          uploadPath: result.uploadPath,
          publicUrl: result.publicUrl,
          message: 'File uploaded successfully' 
        },
        { status: 201 }
      )
    } catch (uploadError) {
      console.error('File upload failed:', uploadError)
      
      return Response.json(
        { 
          error: 'File upload failed',
          message: uploadError instanceof Error ? uploadError.message : 'Unknown upload error'
        },
        { status: 500 }
      )
    }
    
  } catch (error) {
    console.error('Error in POST /api/exam-files/upload:', error)
    
    return Response.json(
      { 
        error: 'Failed to process file upload',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}