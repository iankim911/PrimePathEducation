import { getAcademyId } from '@/lib/academyUtils'
import { 
  getGradeConfiguration, 
  upsertGradeConfiguration,
  initializeDefaultGradeSystem
} from '@/lib/services/grades'
import type { 
  CreateGradeConfigurationRequest, 
  UpdateGradeConfigurationRequest 
} from '@/types/grades'

/**
 * GET /api/grades/configuration
 * Get grade configuration for the academy
 */
export async function GET() {
  try {
    const academyId = await getAcademyId()
    const configuration = await getGradeConfiguration(academyId)
    
    if (!configuration) {
      // Initialize default configuration if none exists
      const defaultSystem = await initializeDefaultGradeSystem(academyId)
      
      return Response.json({
        configuration: defaultSystem.configuration,
        message: 'Default grade configuration initialized'
      })
    }
    
    return Response.json({ 
      configuration,
      academy_id: academyId 
    })
  } catch (error) {
    console.error('Error in GET /api/grades/configuration:', error)
    
    return Response.json(
      { 
        error: 'Failed to fetch grade configuration',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/grades/configuration
 * Update grade configuration for the academy
 */
export async function PUT(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    // Validate required fields
    const configData: CreateGradeConfigurationRequest | UpdateGradeConfigurationRequest = {
      field_label: body.field_label,
      show_all_option: body.show_all_option,
      all_grades_label: body.all_grades_label,
    }
    
    // Basic validation
    if (!configData.field_label || configData.field_label.trim().length === 0) {
      return Response.json(
        { error: 'Field label is required' },
        { status: 400 }
      )
    }
    
    if (configData.show_all_option && (!configData.all_grades_label || configData.all_grades_label.trim().length === 0)) {
      return Response.json(
        { error: 'All grades label is required when show all option is enabled' },
        { status: 400 }
      )
    }
    
    const configuration = await upsertGradeConfiguration(academyId, configData)
    
    return Response.json({
      configuration,
      message: 'Grade configuration updated successfully'
    })
  } catch (error) {
    console.error('Error in PUT /api/grades/configuration:', error)
    
    return Response.json(
      { 
        error: 'Failed to update grade configuration',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/grades/configuration/initialize
 * Initialize default grade system for academy
 */
export async function POST() {
  try {
    const academyId = await getAcademyId()
    
    // Check if configuration already exists
    const existing = await getGradeConfiguration(academyId)
    if (existing) {
      return Response.json(
        { error: 'Grade configuration already exists for this academy' },
        { status: 400 }
      )
    }
    
    const gradeSystem = await initializeDefaultGradeSystem(academyId)
    
    return Response.json({
      ...gradeSystem,
      message: 'Default grade system initialized successfully'
    })
  } catch (error) {
    console.error('Error in POST /api/grades/configuration/initialize:', error)
    
    return Response.json(
      { 
        error: 'Failed to initialize grade system',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}