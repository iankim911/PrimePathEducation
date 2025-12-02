/**
 * Storage Initialization API
 * 
 * Initialize and configure storage buckets for the application.
 */

import { initializeStorage } from '@/lib/services/storageManager'
import { getAcademyId } from '@/lib/academyUtils'

export async function POST(request: Request) {
  try {
    await getAcademyId() // Ensure valid academy context
    
    const result = await initializeStorage()
    
    return Response.json({
      ...result,
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Storage initialization API error:', error)
    
    return Response.json({
      success: false,
      message: `Storage initialization failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
}

export async function GET(request: Request) {
  try {
    await getAcademyId() // Ensure valid academy context
    
    // Just check status, don't initialize
    return Response.json({
      message: 'Storage initialization endpoint available',
      usage: 'Send POST request to initialize storage buckets',
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    return Response.json({
      error: 'Storage check failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}