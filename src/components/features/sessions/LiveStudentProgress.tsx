"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { 
  RefreshCw, 
  Users, 
  CheckCircle2, 
  Clock, 
  BarChart3,
  TrendingUp,
  AlertCircle,
  User
} from 'lucide-react'
import type { SessionStatus, ExamMessage } from '@/lib/websocket/socketManager'

interface LiveStudentProgressProps {
  sessionStatus: SessionStatus | null
  messages: ExamMessage[]
  totalQuestions: number
  onRequestProgress: () => void
  isConnected: boolean
}

interface StudentProgressData {
  studentId: string
  studentName: string
  questionsAnswered: number
  lastActivity: string
  timeSpent: number
  isActive: boolean
}

export function LiveStudentProgress({
  sessionStatus,
  messages,
  totalQuestions,
  onRequestProgress,
  isConnected
}: LiveStudentProgressProps) {
  const [studentProgress, setStudentProgress] = useState<StudentProgressData[]>([])
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // Process messages to track student progress
  useEffect(() => {
    const progressMap = new Map<string, StudentProgressData>()

    // Process student join messages
    messages.forEach(message => {
      if (message.type === 'student_joined' && message.data) {
        const { userId, userName } = message.data
        if (!progressMap.has(userId)) {
          progressMap.set(userId, {
            studentId: userId,
            studentName: userName,
            questionsAnswered: 0,
            lastActivity: message.timestamp,
            timeSpent: 0,
            isActive: true
          })
        }
      }

      // Process answer submissions
      if (message.type === 'answer_submitted' && message.data) {
        const { studentId } = message.data
        const existing = progressMap.get(studentId)
        if (existing) {
          progressMap.set(studentId, {
            ...existing,
            questionsAnswered: existing.questionsAnswered + 1,
            lastActivity: message.timestamp,
            timeSpent: existing.timeSpent + (message.data.timeSpent || 0),
            isActive: true
          })
        }
      }

      // Process student leave messages
      if (message.type === 'student_left' && message.data) {
        const { userId } = message.data
        const existing = progressMap.get(userId)
        if (existing) {
          progressMap.set(userId, {
            ...existing,
            isActive: false
          })
        }
      }
    })

    setStudentProgress(Array.from(progressMap.values()))
  }, [messages])

  const handleRefresh = () => {
    onRequestProgress()
    setLastRefresh(new Date())
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const formatLastActivity = (timestamp: string) => {
    const now = new Date()
    const activity = new Date(timestamp)
    const diffMs = now.getTime() - activity.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins === 1) return '1 minute ago'
    if (diffMins < 60) return `${diffMins} minutes ago`
    
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours === 1) return '1 hour ago'
    return `${diffHours} hours ago`
  }

  const getProgressColor = (progress: number) => {
    if (progress >= 100) return 'bg-green-500'
    if (progress >= 75) return 'bg-blue-500'
    if (progress >= 50) return 'bg-yellow-500'
    if (progress >= 25) return 'bg-orange-500'
    return 'bg-red-500'
  }

  // Calculate overall statistics
  const totalStudents = studentProgress.length
  const activeStudents = studentProgress.filter(s => s.isActive).length
  const completedStudents = studentProgress.filter(s => s.questionsAnswered >= totalQuestions).length
  const averageProgress = totalStudents > 0 
    ? Math.round(studentProgress.reduce((sum, s) => sum + (s.questionsAnswered / totalQuestions * 100), 0) / totalStudents)
    : 0
  const totalSubmissions = messages.filter(m => m.type === 'answer_submitted').length

  return (
    <div className="space-y-6">
      {/* Overview Statistics */}
      <div className="grid grid-cols-5 gap-4">
        <Card className="bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-blue-600">Total Students</p>
                <p className="text-2xl font-bold text-blue-900">{totalStudents}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-green-600">Active</p>
                <p className="text-2xl font-bold text-green-900">{activeStudents}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-purple-600">Completed</p>
                <p className="text-2xl font-bold text-purple-900">{completedStudents}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-orange-600">Avg Progress</p>
                <p className="text-2xl font-bold text-orange-900">{averageProgress}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-5 w-5 text-gray-600" />
              <div>
                <p className="text-sm text-gray-600">Submissions</p>
                <p className="text-2xl font-bold text-gray-900">{totalSubmissions}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Progress Chart */}
      <Card className="bg-white">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-gray-900">Live Student Progress</CardTitle>
              <CardDescription>
                Real-time tracking of student progress and activity
              </CardDescription>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">
                Last updated: {lastRefresh.toLocaleTimeString()}
              </span>
              <Button 
                onClick={handleRefresh}
                disabled={!isConnected}
                variant="outline"
                size="sm"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {studentProgress.length === 0 ? (
            <div className="text-center py-12">
              <Users className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Student Data</h3>
              <p className="text-gray-600">
                Student progress will appear here once they join the session and start answering questions.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Progress Overview */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">Overall Progress</h4>
                <Progress value={averageProgress} className="h-3 mb-2" />
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Average: {averageProgress}%</span>
                  <span>{completedStudents}/{totalStudents} completed</span>
                </div>
              </div>

              {/* Individual Student Progress */}
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900">Individual Progress</h4>
                
                <div className="space-y-2">
                  {studentProgress
                    .sort((a, b) => b.questionsAnswered - a.questionsAnswered)
                    .map((student) => {
                      const progress = (student.questionsAnswered / totalQuestions) * 100
                      
                      return (
                        <div 
                          key={student.studentId} 
                          className="flex items-center justify-between p-3 bg-white border rounded-lg hover:shadow-sm"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="flex items-center space-x-2">
                              <User className="h-5 w-5 text-gray-400" />
                              <div>
                                <p className="font-medium text-gray-900">{student.studentName}</p>
                                <p className="text-xs text-gray-500">{student.studentId}</p>
                              </div>
                            </div>

                            <Badge variant="secondary" className={student.isActive ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"}>
                              {student.isActive ? 'Online' : 'Offline'}
                            </Badge>
                          </div>

                          <div className="flex items-center space-x-4">
                            {/* Progress Bar */}
                            <div className="w-32">
                              <Progress value={progress} className="h-2" />
                            </div>

                            {/* Questions Answered */}
                            <div className="text-center min-w-[60px]">
                              <p className="text-sm font-medium text-gray-900">
                                {student.questionsAnswered}/{totalQuestions}
                              </p>
                              <p className="text-xs text-gray-500">{Math.round(progress)}%</p>
                            </div>

                            {/* Time Spent */}
                            <div className="text-center min-w-[80px]">
                              <p className="text-sm font-medium text-gray-900">
                                <Clock className="h-3 w-3 inline mr-1" />
                                {formatTime(student.timeSpent)}
                              </p>
                            </div>

                            {/* Last Activity */}
                            <div className="text-center min-w-[100px]">
                              <p className="text-xs text-gray-500">
                                {formatLastActivity(student.lastActivity)}
                              </p>
                            </div>

                            {/* Status Indicator */}
                            <div className="flex items-center">
                              {progress >= 100 ? (
                                <CheckCircle2 className="h-5 w-5 text-green-500" />
                              ) : student.isActive ? (
                                <div className="h-3 w-3 bg-green-400 rounded-full animate-pulse" />
                              ) : (
                                <AlertCircle className="h-5 w-5 text-gray-400" />
                              )}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                </div>
              </div>
            </div>
          )}

          {!isConnected && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <p className="text-red-800 font-medium">
                  Not connected to server. Progress data may not be current.
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}