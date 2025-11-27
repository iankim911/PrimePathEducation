import { updateClass, deleteClass, getClassById, type Class } from '@/lib/services/classes'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/classes/[id]
 */
export async function GET(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const classData = await getClassById(params.id, academyId)
    
    if (!classData) {
      return Response.json(
        { error: 'Class not found' },
        { status: 404 }
      )
    }
    
    return Response.json({ class: classData })
  } catch (error) {
    console.error('Error in GET /api/classes/[id]:', error)
    return Response.json(
      { 
        error: 'Failed to fetch class',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * PUT /api/classes/[id]
 */
export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    const body = await request.json()
    
    const updates: Partial<Class> = {
      name: body.name,
      level_label: body.level_label || null,
      target_grade: body.target_grade || null,
      schedule_info: body.schedule_info || null,
    }
    
    const updatedClass = await updateClass(params.id, academyId, updates)
    
    return Response.json(
      { 
        class: updatedClass,
        message: 'Class updated successfully' 
      }
    )
  } catch (error) {
    console.error('Error in PUT /api/classes/[id]:', error)
    return Response.json(
      { 
        error: 'Failed to update class',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/classes/[id]
 */
export async function DELETE(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const params = await context.params
    const academyId = await getAcademyId()
    await deleteClass(params.id, academyId)
    
    return Response.json(
      { message: 'Class deleted successfully' }
    )
  } catch (error) {
    console.error('Error in DELETE /api/classes/[id]:', error)
    return Response.json(
      { 
        error: 'Failed to delete class',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}