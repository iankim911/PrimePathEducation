import { NextRequest, NextResponse } from 'next/server'
import { withErrorHandling, logger, ValidationError, NotFoundError, PerformanceMonitor } from '@/lib/utils/errorHandler'

async function handler(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<Response> {
    const { id: examId } = await params
    PerformanceMonitor.startTimer(`analytics-${examId}`)
    const { searchParams } = new URL(request.url)
    const dateRange = searchParams.get('range') || '30'
    const sessionFilter = searchParams.get('session') || 'all'

    // Validate inputs
    if (!examId) {
      throw new ValidationError('Exam ID is required')
    }

    if (dateRange && !['7', '30', '90', 'all'].includes(dateRange)) {
      throw new ValidationError('Invalid date range. Must be one of: 7, 30, 90, all')
    }

    logger.info(
      `Fetching analytics for exam ${examId}`,
      { examId, additionalData: { dateRange, sessionFilter } },
      'api'
    )

    // Mock analytics data - In a real implementation, this would fetch from your database
    const mockAnalytics = {
      exam: {
        id: examId,
        title: "Advanced English Proficiency Test",
        total_questions: 50,
        time_limit_minutes: 120,
        passing_score: 70,
        created_at: "2024-01-15T10:00:00Z"
      },
      sessions: [
        {
          id: "session-1",
          title: "Morning Class Session",
          completed_at: "2024-11-20T12:00:00Z",
          total_participants: 25,
          completion_rate: 88.0
        },
        {
          id: "session-2", 
          title: "Afternoon Class Session",
          completed_at: "2024-11-22T16:00:00Z",
          total_participants: 30,
          completion_rate: 93.3
        },
        {
          id: "session-3",
          title: "Evening Class Session", 
          completed_at: "2024-11-25T19:00:00Z",
          total_participants: 20,
          completion_rate: 85.0
        }
      ],
      overview: {
        total_attempts: 75,
        total_students: 65,
        average_score: 76.4,
        completion_rate: 89.3,
        average_time_minutes: 98,
        pass_rate: 73.8
      },
      performance_distribution: [
        { score_range: "90-100", count: 12, percentage: 16.0 },
        { score_range: "80-89", count: 18, percentage: 24.0 },
        { score_range: "70-79", count: 25, percentage: 33.3 },
        { score_range: "60-69", count: 15, percentage: 20.0 },
        { score_range: "50-59", count: 5, percentage: 6.7 }
      ],
      question_analytics: [
        {
          question_id: "q1",
          question_text: "Choose the correct form of the verb: 'She _____ to the store yesterday.'",
          correct_rate: 85.3,
          average_time_seconds: 45,
          difficulty_level: "easy" as const,
          common_wrong_answers: ["goes", "going"]
        },
        {
          question_id: "q2", 
          question_text: "Identify the passive voice construction in the following sentence: 'The report was completed by the team.'",
          correct_rate: 62.7,
          average_time_seconds: 78,
          difficulty_level: "medium" as const,
          common_wrong_answers: ["active voice", "conditional"]
        },
        {
          question_id: "q3",
          question_text: "Which of the following best demonstrates subjunctive mood usage?",
          correct_rate: 41.3,
          average_time_seconds: 95,
          difficulty_level: "hard" as const,
          common_wrong_answers: ["I wish I was taller", "He insists that she comes"]
        },
        {
          question_id: "q4",
          question_text: "Complete the sentence with the appropriate preposition: 'She is interested ___ learning French.'",
          correct_rate: 91.2,
          average_time_seconds: 32,
          difficulty_level: "easy" as const,
          common_wrong_answers: ["on", "at"]
        },
        {
          question_id: "q5",
          question_text: "Analyze the rhetorical device used in: 'The pen is mightier than the sword.'",
          correct_rate: 58.9,
          average_time_seconds: 67,
          difficulty_level: "medium" as const,
          common_wrong_answers: ["alliteration", "simile"]
        }
      ],
      student_performance: [
        {
          student_id: "student-001",
          student_name: "Alice Chen", 
          attempts: 2,
          best_score: 94.5,
          latest_score: 94.5,
          total_time_minutes: 85,
          completion_date: "2024-11-25T14:30:00Z",
          status: "completed" as const
        },
        {
          student_id: "student-002",
          student_name: "Bob Martinez",
          attempts: 3,
          best_score: 78.2,
          latest_score: 78.2,
          total_time_minutes: 110,
          completion_date: "2024-11-24T16:45:00Z", 
          status: "completed" as const
        },
        {
          student_id: "student-003",
          student_name: "Carol Kim",
          attempts: 1,
          best_score: 88.7,
          latest_score: 88.7,
          total_time_minutes: 92,
          completion_date: "2024-11-23T11:15:00Z",
          status: "completed" as const
        },
        {
          student_id: "student-004", 
          student_name: "David Wilson",
          attempts: 2,
          best_score: 65.4,
          latest_score: 65.4,
          total_time_minutes: 118,
          completion_date: "2024-11-22T09:30:00Z",
          status: "completed" as const
        },
        {
          student_id: "student-005",
          student_name: "Emma Davis",
          attempts: 1,
          best_score: 82.3,
          latest_score: 82.3,
          total_time_minutes: 76,
          completion_date: "2024-11-26T13:20:00Z",
          status: "completed" as const
        },
        {
          student_id: "student-006",
          student_name: "Frank Lopez",
          attempts: 1,
          best_score: 0,
          latest_score: 0,
          total_time_minutes: 45,
          completion_date: "2024-11-20T10:00:00Z",
          status: "in_progress" as const
        }
      ],
      time_trends: [
        {
          date: "2024-11-20",
          attempts: 8,
          average_score: 74.2,
          completion_rate: 87.5
        },
        {
          date: "2024-11-21",
          attempts: 12,
          average_score: 76.8,
          completion_rate: 91.7
        },
        {
          date: "2024-11-22",
          attempts: 15,
          average_score: 78.1,
          completion_rate: 93.3
        },
        {
          date: "2024-11-23",
          attempts: 10,
          average_score: 75.5,
          completion_rate: 90.0
        },
        {
          date: "2024-11-24",
          attempts: 18,
          average_score: 77.9,
          completion_rate: 88.9
        },
        {
          date: "2024-11-25",
          attempts: 12,
          average_score: 76.4,
          completion_rate: 91.7
        },
        {
          date: "2024-11-26",
          attempts: 6,
          average_score: 79.2,
          completion_rate: 83.3
        }
      ]
    }

    // Filter data based on session if specified
    if (sessionFilter !== 'all') {
      const filteredSession = mockAnalytics.sessions.find(s => s.id === sessionFilter)
      if (filteredSession) {
        mockAnalytics.sessions = [filteredSession]
      }
    }

    // Filter time trends based on date range
    if (dateRange !== 'all') {
      const daysBack = parseInt(dateRange)
      const cutoffDate = new Date()
      cutoffDate.setDate(cutoffDate.getDate() - daysBack)
      
      mockAnalytics.time_trends = mockAnalytics.time_trends.filter(trend => {
        const trendDate = new Date(trend.date)
        return trendDate >= cutoffDate
      })
    }

    // Check if exam exists (in real implementation)
    if (examId === 'non-existent') {
      throw new NotFoundError('Exam')
    }

    const duration = PerformanceMonitor.endTimer(`analytics-${examId}`, { examId })
    
    logger.info(
      `Analytics fetched successfully for exam ${examId}`,
      { examId, additionalData: { dateRange, sessionFilter, duration } },
      'api'
    )

    return NextResponse.json(mockAnalytics)
}

export const GET = withErrorHandling(handler, 'api')