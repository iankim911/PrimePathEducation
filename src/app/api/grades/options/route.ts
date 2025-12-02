import { getAcademyId } from '@/lib/academyUtils'
import { 
  getGradeOptions,
  getGradeDropdownItems,
  createGradeOption,
  reorderGradeOptions
} from '@/lib/services/grades'
import type { 
  CreateGradeOptionRequest,
  ReorderGradeOptionsRequest
} from '@/types/grades'

/**
 * GET /api/grades/options
 * Get grade options for the academy
 * Query params:
 * - format=dropdown - Returns formatted dropdown items
 * - includeAll=true/false - Include "All Grades" option (default: true)
 */
export async function GET(request: Request) {
  try {
    const academyId = await getAcademyId()
    const url = new URL(request.url)
    const format = url.searchParams.get('format')
    const includeAll = url.searchParams.get('includeAll') !== 'false'
    
    if (format === 'dropdown') {
      const dropdownItems = await getGradeDropdownItems(academyId, includeAll)
      
      return Response.json({
        items: dropdownItems,
        academy_id: academyId,
        count: dropdownItems.length
      })
    } else {
      const options = await getGradeOptions(academyId)
      
      return Response.json({
        options,
        academy_id: academyId,
        count: options.length
      })
    }
  } catch (error) {
    console.error('Error in GET /api/grades/options:', error)
    
    return Response.json(
      { 
        error: 'Failed to fetch grade options',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/grades/options
 * Create a new grade option
 */
export async function POST(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    const optionData: CreateGradeOptionRequest = {
      grade_value: body.grade_value,
      display_name: body.display_name,
      short_name: body.short_name || null,
      sort_order: body.sort_order || 0,
    }
    
    // Validation
    if (!optionData.grade_value || !Number.isInteger(optionData.grade_value)) {
      return Response.json(
        { error: 'Valid grade value is required' },
        { status: 400 }
      )
    }
    
    if (!optionData.display_name || optionData.display_name.trim().length === 0) {
      return Response.json(
        { error: 'Display name is required' },
        { status: 400 }
      )
    }
    
    if (optionData.grade_value < 1 || optionData.grade_value > 15) {
      return Response.json(
        { error: 'Grade value must be between 1 and 15' },
        { status: 400 }
      )
    }
    
    const option = await createGradeOption(academyId, optionData)
    
    return Response.json({
      option,
      message: 'Grade option created successfully'
    }, { status: 201 })
  } catch (error) {
    console.error('Error in POST /api/grades/options:', error)
    
    // Check for duplicate grade value error
    if (error instanceof Error && error.message.includes('duplicate')) {
      return Response.json(
        { error: 'A grade option with this value already exists' },
        { status: 409 }
      )
    }
    
    return Response.json(
      { 
        error: 'Failed to create grade option',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * PATCH /api/grades/options
 * Reorder grade options
 */
export async function PATCH(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    const reorderData: ReorderGradeOptionsRequest = {
      grade_option_ids: body.grade_option_ids
    }
    
    // Validation
    if (!Array.isArray(reorderData.grade_option_ids)) {
      return Response.json(
        { error: 'grade_option_ids must be an array' },
        { status: 400 }
      )
    }
    
    if (reorderData.grade_option_ids.length === 0) {
      return Response.json(
        { error: 'At least one grade option ID is required' },
        { status: 400 }
      )
    }
    
    await reorderGradeOptions(academyId, reorderData.grade_option_ids)
    
    return Response.json({
      message: 'Grade options reordered successfully'
    })
  } catch (error) {
    console.error('Error in PATCH /api/grades/options:', error)
    
    return Response.json(
      { 
        error: 'Failed to reorder grade options',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}