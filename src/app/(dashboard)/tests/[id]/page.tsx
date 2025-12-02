"use client"

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  ArrowLeft,
  FileText,
  Users,
  BarChart3,
  Play,
  Settings,
  Calendar,
  Clock,
  Target,
  HelpCircle,
  Download,
  Edit
} from 'lucide-react'
import type { Exam } from '@/lib/services/exams'

export default function ExamDetailPage() {
  const params = useParams()
  const router = useRouter()
  const examId = params.id as string

  const [exam, setExam] = useState<Exam | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState({
    totalSessions: 0,
    totalAttempts: 0,
    averageScore: 0,
    completionRate: 0
  })

  useEffect(() => {
    const fetchExamData = async () => {
      try {
        // Fetch exam details
        const examResponse = await fetch(`/api/exams/${examId}`)
        if (!examResponse.ok) {
          throw new Error('Exam not found')
        }
        const examData = await examResponse.json()
        setExam(examData.exam)

        // Fetch basic stats
        const statsResponse = await fetch(`/api/exams/${examId}/stats`)
        if (statsResponse.ok) {
          const statsData = await statsResponse.json()
          setStats(statsData)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load exam')
      } finally {
        setLoading(false)
      }
    }

    fetchExamData()
  }, [examId])

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error || !exam) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <FileText className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-red-900 mb-2">Exam Not Found</h3>
          <p className="text-red-700 mb-4">{error || 'The requested exam could not be found.'}</p>
          <Button onClick={() => router.push('/tests')} className="bg-gray-900 hover:bg-gray-800 text-white">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Exams
          </Button>
        </div>
      </div>
    )
  }

  const handleNavigate = (path: string) => {
    router.push(`/tests/${examId}${path}`)
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" onClick={() => router.push('/tests')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Exams
          </Button>
          
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{exam.title}</h1>
            <p className="text-gray-600">{exam.description || 'No description provided'}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={() => handleNavigate('/questions')}>
            <Edit className="h-4 w-4 mr-2" />
            Edit Questions
          </Button>
          
          <Button onClick={() => handleNavigate('/sessions')} className="bg-gray-900 hover:bg-gray-800 text-white">
            <Play className="h-4 w-4 mr-2" />
            Manage Sessions
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-blue-600">Total Sessions</p>
                <p className="text-2xl font-bold text-blue-900">{stats.totalSessions}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-green-600">Total Attempts</p>
                <p className="text-2xl font-bold text-green-900">{stats.totalAttempts}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-purple-600">Average Score</p>
                <p className="text-2xl font-bold text-purple-900">{stats.averageScore.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-orange-600">Completion Rate</p>
                <p className="text-2xl font-bold text-orange-900">{stats.completionRate.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 bg-white">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="sessions">Sessions</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Exam Details */}
            <Card className="bg-white">
              <CardHeader>
                <CardTitle className="text-gray-900">Exam Information</CardTitle>
                <CardDescription>Basic exam details and configuration</CardDescription>
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
                      {exam.time_limit_minutes ? `${exam.time_limit_minutes} minutes` : 'No limit'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Attempts Allowed:</span>
                    <span className="ml-2 text-gray-900">{exam.attempts_allowed}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Passing Score:</span>
                    <span className="ml-2 text-gray-900">
                      {exam.passing_score ? `${exam.passing_score}%` : 'Not set'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Show Results:</span>
                    <span className="ml-2 text-gray-900">{exam.show_results ? 'Yes' : 'No'}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Randomize Questions:</span>
                    <span className="ml-2 text-gray-900">{exam.randomize_questions ? 'Yes' : 'No'}</span>
                  </div>
                </div>

                {exam.subject_tags && exam.subject_tags.length > 0 && (
                  <div className="pt-4 border-t border-gray-200">
                    <h4 className="font-medium text-gray-900 mb-2">Subject Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      {exam.subject_tags.map((tag, index) => (
                        <Badge key={index} variant="secondary" className="bg-blue-100 text-blue-800">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-200">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Created:</span>
                      <span className="ml-2 text-gray-900">
                        {new Date(exam.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Last Modified:</span>
                      <span className="ml-2 text-gray-900">
                        {new Date(exam.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="bg-white">
              <CardHeader>
                <CardTitle className="text-gray-900">Quick Actions</CardTitle>
                <CardDescription>Common exam management tasks</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button 
                  onClick={() => handleNavigate('/sessions')}
                  className="w-full justify-start h-12 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <Calendar className="h-5 w-5 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">Manage Sessions</p>
                    <p className="text-xs text-blue-100">Create and monitor exam sessions</p>
                  </div>
                </Button>

                <Button 
                  onClick={() => handleNavigate('/questions')}
                  variant="outline"
                  className="w-full justify-start h-12"
                >
                  <HelpCircle className="h-5 w-5 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">Edit Questions</p>
                    <p className="text-xs text-gray-500">Add or modify exam questions</p>
                  </div>
                </Button>

                <Button 
                  onClick={() => handleNavigate('/analytics')}
                  variant="outline"
                  className="w-full justify-start h-12"
                >
                  <BarChart3 className="h-5 w-5 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">View Analytics</p>
                    <p className="text-xs text-gray-500">Performance reports and insights</p>
                  </div>
                </Button>

                <Button 
                  variant="outline"
                  className="w-full justify-start h-12"
                >
                  <Download className="h-5 w-5 mr-3" />
                  <div className="text-left">
                    <p className="font-medium">Export Data</p>
                    <p className="text-xs text-gray-500">Download exam results and analytics</p>
                  </div>
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Files Information - Note: In real implementation, files would be fetched separately */}
          <Card className="bg-white">
            <CardHeader>
              <CardTitle className="text-gray-900">Exam Files</CardTitle>
              <CardDescription>Manage PDF documents and audio files for this exam</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">
                  Upload and manage exam materials
                </p>
                <Button variant="outline">
                  Manage Files
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Sessions Tab */}
        <TabsContent value="sessions">
          <Card className="bg-white">
            <CardHeader>
              <CardTitle className="text-gray-900">Exam Sessions</CardTitle>
              <CardDescription>Manage live exam sessions and monitor student progress</CardDescription>
            </CardHeader>
            <CardContent className="text-center py-8">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">
                Create and manage exam sessions for your students
              </p>
              <Button onClick={() => handleNavigate('/sessions')} className="bg-gray-900 hover:bg-gray-800 text-white">
                Go to Sessions
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics">
          <Card className="bg-white">
            <CardHeader>
              <CardTitle className="text-gray-900">Analytics & Reports</CardTitle>
              <CardDescription>Detailed performance analysis and student insights</CardDescription>
            </CardHeader>
            <CardContent className="text-center py-8">
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">
                View comprehensive analytics and performance trends
              </p>
              <Button onClick={() => handleNavigate('/analytics')} className="bg-gray-900 hover:bg-gray-800 text-white">
                View Analytics
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings">
          <Card className="bg-white">
            <CardHeader>
              <CardTitle className="text-gray-900">Exam Settings</CardTitle>
              <CardDescription>Configure exam parameters and behavior</CardDescription>
            </CardHeader>
            <CardContent className="text-center py-8">
              <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">
                Modify exam settings and configuration options
              </p>
              <Button variant="outline">
                Edit Settings
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}