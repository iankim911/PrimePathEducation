import { getAcademyId } from '@/lib/academyUtils'
import { 
  updateGradeOption,
  deleteGradeOption
} from '@/lib/services/grades'
import type { UpdateGradeOptionRequest } from '@/types/grades'

/**
 * PUT /api/grades/options/[id]
 * Update a grade option
 */
export async function PUT(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const academyId = await getAcademyId()
    const { id: optionId } = await params
    const body = await request.json()
    
    const updates: UpdateGradeOptionRequest = {
      grade_value: body.grade_value,
      display_name: body.display_name,
      short_name: body.short_name,
      sort_order: body.sort_order,
      is_active: body.is_active,
    }
    
    // Remove undefined values to avoid updating with undefined
    Object.keys(updates).forEach(key => {
      if (updates[key as keyof UpdateGradeOptionRequest] === undefined) {
        delete updates[key as keyof UpdateGradeOptionRequest]
      }
    })
    
    // Validation for required fields if provided
    if (updates.grade_value !== undefined) {
      if (!Number.isInteger(updates.grade_value) || updates.grade_value < 1 || updates.grade_value > 15) {
        return Response.json(
          { error: 'Grade value must be an integer between 1 and 15' },
          { status: 400 }
        )
      }
    }
    
    if (updates.display_name !== undefined) {
      if (!updates.display_name || updates.display_name.trim().length === 0) {
        return Response.json(
          { error: 'Display name cannot be empty' },
          { status: 400 }
        )
      }
    }
    
    const option = await updateGradeOption(optionId, academyId, updates)
    
    return Response.json({
      option,
      message: 'Grade option updated successfully'
    })
  } catch (error) {
    console.error('Error in PUT /api/grades/options/[id]:', error)
    
    // Check for duplicate grade value error
    if (error instanceof Error && error.message.includes('duplicate')) {
      return Response.json(
        { error: 'A grade option with this value already exists' },
        { status: 409 }
      )
    }
    
    return Response.json(
      { 
        error: 'Failed to update grade option',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/grades/options/[id]
 * Delete a grade option
 */
export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const academyId = await getAcademyId()
    const { id: optionId } = await params
    
    await deleteGradeOption(optionId, academyId)
    
    return Response.json({
      message: 'Grade option deleted successfully'
    })
  } catch (error) {
    console.error('Error in DELETE /api/grades/options/[id]:', error)
    
    return Response.json(
      { 
        error: 'Failed to delete grade option',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}