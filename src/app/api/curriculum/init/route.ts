import { initializeCurriculumTables, checkCurriculumTablesExist } from '@/lib/services/curriculumInit'
import { getAcademyId } from '@/lib/academyUtils'

/**
 * GET /api/curriculum/init
 * Check if curriculum tables are initialized
 */
export async function GET() {
  try {
    const { settingsTableExists, nodesTableExists } = await checkCurriculumTablesExist()
    
    return Response.json({ 
      initialized: settingsTableExists && nodesTableExists,
      tables: {
        settings: settingsTableExists,
        nodes: nodesTableExists
      }
    })
  } catch (error) {
    console.error('Error checking curriculum initialization:', error)
    
    return Response.json(
      { 
        error: 'Failed to check curriculum initialization',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

/**
 * POST /api/curriculum/init
 * Initialize curriculum tables in the database
 */
export async function POST() {
  try {
    // Verify academy exists first
    const academyId = await getAcademyId()
    if (!academyId) {
      return Response.json(
        { error: 'Academy not found' },
        { status: 404 }
      )
    }
    
    const result = await initializeCurriculumTables()
    
    if (result.success) {
      return Response.json(
        { 
          message: result.message,
          initialized: true
        },
        { status: 200 }
      )
    } else {
      return Response.json(
        { 
          error: 'Failed to initialize curriculum tables',
          message: result.message,
          details: result.error
        },
        { status: 500 }
      )
    }
  } catch (error) {
    console.error('Error initializing curriculum:', error)
    
    return Response.json(
      { 
        error: 'Failed to initialize curriculum',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}