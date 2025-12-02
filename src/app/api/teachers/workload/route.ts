import { NextResponse } from 'next/server'
import { getTeachersWithWorkload } from '@/lib/services/teachers'
import { getAcademyId } from '@/lib/academyUtils'

export async function GET() {
  try {
    const academyId = await getAcademyId()
    const teachers = await getTeachersWithWorkload(academyId)
    
    return NextResponse.json({
      success: true,
      teachers,
    })
  } catch (error) {
    console.error('GET /api/teachers/workload error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch teachers with workload data' 
      },
      { status: 500 }
    )
  }
}