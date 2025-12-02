"use client"

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  Clock,
  CheckCircle2,
  AlertCircle,
  Download,
  Calendar,
  Target,
  Award,
  FileText
} from 'lucide-react'
import { ExamResultsChart } from '@/components/features/analytics/ExamResultsChart'
import { StudentPerformanceTable } from '@/components/features/analytics/StudentPerformanceTable'
import { QuestionAnalysis } from '@/components/features/analytics/QuestionAnalysis'
import { PerformanceTrends } from '@/components/features/analytics/PerformanceTrends'

interface ExamAnalytics {
  exam: {
    id: string
    title: string
    total_questions: number
    time_limit_minutes?: number
    passing_score?: number
    created_at: string
  }
  sessions: {
    id: string
    title: string
    completed_at?: string
    total_participants: number
    completion_rate: number
  }[]
  overview: {
    total_attempts: number
    total_students: number
    average_score: number
    completion_rate: number
    average_time_minutes: number
    pass_rate: number
  }
  performance_distribution: {
    score_range: string
    count: number
    percentage: number
  }[]
  question_analytics: {
    question_id: string
    question_text: string
    correct_rate: number
    average_time_seconds: number
    difficulty_level: 'easy' | 'medium' | 'hard'
    common_wrong_answers: string[]
  }[]
  student_performance: {
    student_id: string
    student_name: string
    attempts: number
    best_score: number
    latest_score: number
    total_time_minutes: number
    completion_date: string
    status: 'completed' | 'in_progress' | 'not_started'
  }[]
  time_trends: {
    date: string
    attempts: number
    average_score: number
    completion_rate: number
  }[]
}

export default function ExamAnalyticsPage() {
  const params = useParams()
  const examId = params.id as string

  const [analytics, setAnalytics] = useState<ExamAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dateRange, setDateRange] = useState('30')
  const [sessionFilter, setSessionFilter] = useState('all')

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch(`/api/exams/${examId}/analytics?range=${dateRange}&session=${sessionFilter}`)
        if (!response.ok) {
          throw new Error('Failed to fetch analytics')
        }
        const data = await response.json()
        setAnalytics(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load analytics')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [examId, dateRange, sessionFilter])

  const handleExportResults = async () => {
    try {
      const response = await fetch(`/api/exams/${examId}/analytics/export?range=${dateRange}&session=${sessionFilter}`)
      if (!response.ok) {
        throw new Error('Export failed')
      }
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `exam-${examId}-analytics-${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error || !analytics) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-red-900 mb-2">Analytics Unavailable</h3>
          <p className="text-red-700">{error || 'No analytics data available'}</p>
        </div>
      </div>
    )
  }

  const { exam, overview, performance_distribution, question_analytics, student_performance } = analytics

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{exam.title}</h1>
          <p className="text-gray-600">Comprehensive exam analytics and performance insights</p>
        </div>

        <div className="flex items-center space-x-3">
          <Select value={dateRange} onValueChange={setDateRange}>
            <SelectTrigger className="w-40">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-white">
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
              <SelectItem value="all">All time</SelectItem>
            </SelectContent>
          </Select>

          <Select value={sessionFilter} onValueChange={setSessionFilter}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-white">
              <SelectItem value="all">All sessions</SelectItem>
              {analytics.sessions.map((session) => (
                <SelectItem key={session.id} value={session.id}>
                  {session.title}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button onClick={handleExportResults} className="bg-gray-900 hover:bg-gray-800 text-white">
            <Download className="h-4 w-4 mr-2" />
            Export Results
          </Button>
        </div>
      </div>

      {/* Overview Statistics */}
      <div className="grid grid-cols-6 gap-4">
        <Card className="bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-blue-600">Total Students</p>
                <p className="text-2xl font-bold text-blue-900">{overview.total_students}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-green-600">Attempts</p>
                <p className="text-2xl font-bold text-green-900">{overview.total_attempts}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-purple-600">Avg Score</p>
                <p className="text-2xl font-bold text-purple-900">{overview.average_score.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-yellow-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Award className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-sm text-yellow-600">Pass Rate</p>
                <p className="text-2xl font-bold text-yellow-900">{overview.pass_rate.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-orange-600">Avg Time</p>
                <p className="text-2xl font-bold text-orange-900">{overview.average_time_minutes.toFixed(0)}m</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-gray-600" />
              <div>
                <p className="text-sm text-gray-600">Completion</p>
                <p className="text-2xl font-bold text-gray-900">{overview.completion_rate.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Analytics */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5 bg-white">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="students">Student Performance</TabsTrigger>
          <TabsTrigger value="questions">Question Analysis</TabsTrigger>
          <TabsTrigger value="trends">Performance Trends</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Score Distribution */}
            <Card className="bg-white">
              <CardHeader>
                <CardTitle className="text-gray-900">Score Distribution</CardTitle>
                <CardDescription>How students performed across score ranges</CardDescription>
              </CardHeader>
              <CardContent>
                <ExamResultsChart data={performance_distribution} />
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card className="bg-white">
              <CardHeader>
                <CardTitle className="text-gray-900">Exam Information</CardTitle>
                <CardDescription>Key exam details and settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Total Questions:</span>
                    <span className="ml-2 text-gray-900">{exam.total_questions}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Time Limit:</span>
                    <span className="ml-2 text-gray-900">
                      {exam.time_limit_minutes ? `${exam.time_limit_minutes} min` : 'No limit'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Passing Score:</span>
                    <span className="ml-2 text-gray-900">
                      {exam.passing_score ? `${exam.passing_score}%` : 'Not set'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Created:</span>
                    <span className="ml-2 text-gray-900">
                      {new Date(exam.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <h4 className="font-medium text-gray-900 mb-3">Performance Summary</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Highest Score:</span>
                      <span className="font-medium text-gray-900">
                        {Math.max(...student_performance.map(s => s.best_score)).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Lowest Score:</span>
                      <span className="font-medium text-gray-900">
                        {Math.min(...student_performance.map(s => s.best_score)).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Standard Deviation:</span>
                      <span className="font-medium text-gray-900">
                        {(() => {
                          const scores = student_performance.map(s => s.best_score)
                          const avg = scores.reduce((a, b) => a + b, 0) / scores.length
                          const variance = scores.reduce((a, b) => a + Math.pow(b - avg, 2), 0) / scores.length
                          return Math.sqrt(variance).toFixed(1)
                        })()}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sessions Overview */}
          <Card className="bg-white">
            <CardHeader>
              <CardTitle className="text-gray-900">Recent Sessions</CardTitle>
              <CardDescription>Overview of exam sessions conducted</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analytics.sessions.slice(0, 5).map((session) => (
                  <div key={session.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium text-gray-900">{session.title}</h4>
                      <p className="text-sm text-gray-600">
                        {session.total_participants} participants • {session.completion_rate.toFixed(1)}% completion
                      </p>
                    </div>
                    <div className="text-right">
                      <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                        {session.completed_at ? 'Completed' : 'In Progress'}
                      </Badge>
                      {session.completed_at && (
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(session.completed_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Student Performance Tab */}
        <TabsContent value="students">
          <StudentPerformanceTable 
            students={student_performance}
            examId={examId}
            passingScore={exam.passing_score}
          />
        </TabsContent>

        {/* Question Analysis Tab */}
        <TabsContent value="questions">
          <QuestionAnalysis 
            questions={question_analytics}
            totalAttempts={overview.total_attempts}
          />
        </TabsContent>

        {/* Performance Trends Tab */}
        <TabsContent value="trends">
          <PerformanceTrends 
            trends={analytics.time_trends}
            examTitle={exam.title}
          />
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports" className="space-y-6">
          <Card className="bg-white">
            <CardHeader>
              <CardTitle className="text-gray-900">Export Options</CardTitle>
              <CardDescription>Download detailed reports and raw data</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Button variant="outline" onClick={handleExportResults} className="h-24 flex-col">
                  <FileText className="h-8 w-8 mb-2" />
                  <span>Complete Analytics Report</span>
                  <span className="text-xs text-gray-500">Excel format with all data</span>
                </Button>

                <Button variant="outline" className="h-24 flex-col">
                  <Users className="h-8 w-8 mb-2" />
                  <span>Student Performance</span>
                  <span className="text-xs text-gray-500">Individual student results</span>
                </Button>

                <Button variant="outline" className="h-24 flex-col">
                  <BarChart3 className="h-8 w-8 mb-2" />
                  <span>Question Analysis</span>
                  <span className="text-xs text-gray-500">Question difficulty & statistics</span>
                </Button>

                <Button variant="outline" className="h-24 flex-col">
                  <TrendingUp className="h-8 w-8 mb-2" />
                  <span>Trends Report</span>
                  <span className="text-xs text-gray-500">Performance over time</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}