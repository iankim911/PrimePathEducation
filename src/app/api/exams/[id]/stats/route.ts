import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: examId } = await params

    // Mock stats data - In a real implementation, this would query your database
    const mockStats = {
      totalSessions: 3,
      totalAttempts: 75,
      averageScore: 76.4,
      completionRate: 89.3
    }

    return NextResponse.json(mockStats)
  } catch (error) {
    console.error('Error fetching exam stats:', error)
    return NextResponse.json(
      { error: 'Failed to fetch exam stats' },
      { status: 500 }
    )
  }
}