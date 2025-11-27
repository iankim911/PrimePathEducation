import { listClassesWithTeachers, createClass, type Class } from '@/lib/services/classes'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/classes
 * Returns all classes for the academy
 */
export async function GET() {
  try {
    const academyId = await getAcademyId()
    const classes = await listClassesWithTeachers(academyId)
    
    return Response.json({ 
      classes,
      academy_id: academyId,
      count: classes.length 
    })
  } catch (error) {
    console.error('Error in GET /api/classes:', error)
    
    return Response.json(
      { 
        error: 'Failed to fetch classes',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/classes
 * Creates a new class
 */
export async function POST(request: Request) {
  try {
    const academyId = await getAcademyId()
    const body = await request.json()
    
    const classData: Omit<Class, 'id' | 'created_at' | 'updated_at' | 'deleted_at'> = {
      academy_id: academyId,
      name: body.name,
      level_label: body.level_label || null,
      target_grade: body.target_grade || null,
      schedule_info: body.schedule_info || null,
      is_active: true
    }
    
    const newClass = await createClass(classData)
    
    return Response.json(
      { 
        class: newClass,
        message: 'Class created successfully' 
      },
      { status: 201 }
    )
  } catch (error) {
    console.error('Error in POST /api/classes:', error)
    
    return Response.json(
      { 
        error: 'Failed to create class',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}