"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { 
  Play, 
  Pause, 
  Square, 
  Users, 
  Clock, 
  BarChart3, 
  MessageSquare,
  Wifi,
  WifiOff,
  AlertCircle,
  CheckCircle2,
  ArrowLeft,
  Megaphone,
  RefreshCw
} from 'lucide-react'
import { SessionControlPanel } from './SessionControlPanel'
import { LiveStudentProgress } from './LiveStudentProgress'
import { SessionMessages } from './SessionMessages'
import type { ExamSession } from '@/app/(dashboard)/tests/[id]/sessions/page'
import type { SessionStatus, ExamMessage } from '@/lib/websocket/socketManager'

interface TeacherSessionDashboardProps {
  session: ExamSession
  exam: any
  sessionStatus: SessionStatus | null
  messages: ExamMessage[]
  isConnected: boolean
  onControlSession: (action: 'start' | 'pause' | 'resume' | 'end', timeLimit?: number) => void
  onBroadcastMessage: (message: string, type?: 'announcement' | 'warning' | 'reminder') => void
  onRequestProgress: () => void
}

export function TeacherSessionDashboard({
  session,
  exam,
  sessionStatus,
  messages,
  isConnected,
  onControlSession,
  onBroadcastMessage,
  onRequestProgress
}: TeacherSessionDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview')
  const [broadcastOpen, setBroadcastOpen] = useState(false)
  const [broadcastMessage, setBroadcastMessage] = useState('')
  const [broadcastType, setBroadcastType] = useState<'announcement' | 'warning' | 'reminder'>('announcement')

  // Auto-refresh progress every 30 seconds when session is active
  useEffect(() => {
    if (sessionStatus?.status === 'active') {
      const interval = setInterval(() => {
        onRequestProgress()
      }, 30000)

      return () => clearInterval(interval)
    }
  }, [sessionStatus?.status, onRequestProgress])

  // Format time remaining
  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const handleBroadcast = () => {
    if (broadcastMessage.trim()) {
      onBroadcastMessage(broadcastMessage.trim(), broadcastType)
      setBroadcastMessage('')
      setBroadcastOpen(false)
    }
  }

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'waiting':
      case 'scheduled':
        return 'bg-blue-100 text-blue-800'
      case 'paused':
        return 'bg-yellow-100 text-yellow-800'
      case 'completed':
        return 'bg-gray-100 text-gray-600'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'active':
        return <Play className="h-4 w-4" />
      case 'paused':
        return <Pause className="h-4 w-4" />
      case 'completed':
        return <Square className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => window.history.back()}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{session.title}</h1>
              <p className="text-gray-600">{exam.title}</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <Badge variant="secondary" className={isConnected ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
              {isConnected ? (
                <>
                  <Wifi className="h-3 w-3 mr-1" />
                  Connected
                </>
              ) : (
                <>
                  <WifiOff className="h-3 w-3 mr-1" />
                  Disconnected
                </>
              )}
            </Badge>

            {/* Session Status */}
            <Badge variant="secondary" className={getStatusColor(sessionStatus?.status)}>
              {getStatusIcon(sessionStatus?.status)}
              <span className="ml-1 capitalize">{sessionStatus?.status || 'Unknown'}</span>
            </Badge>

            {/* Time Remaining */}
            {sessionStatus?.timeRemaining !== undefined && sessionStatus.status === 'active' && (
              <div className="flex items-center space-x-2 bg-gray-100 px-3 py-1 rounded-lg">
                <Clock className="h-4 w-4 text-gray-600" />
                <span className={`font-mono text-lg ${
                  sessionStatus.timeRemaining < 300 ? 'text-red-600' : 'text-gray-900'
                }`}>
                  {formatTime(sessionStatus.timeRemaining)}
                </span>
              </div>
            )}

            {/* Quick Actions */}
            <Dialog open={broadcastOpen} onOpenChange={setBroadcastOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" disabled={!isConnected}>
                  <Megaphone className="h-4 w-4 mr-2" />
                  Broadcast
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-white">
                <DialogHeader>
                  <DialogTitle className="text-gray-900">Broadcast Message</DialogTitle>
                  <DialogDescription className="text-gray-600">
                    Send a message to all students in this session
                  </DialogDescription>
                </DialogHeader>
                
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Message Type</label>
                    <select 
                      value={broadcastType}
                      onChange={(e) => setBroadcastType(e.target.value as any)}
                      className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="announcement">Announcement</option>
                      <option value="warning">Warning</option>
                      <option value="reminder">Reminder</option>
                    </select>
                  </div>
                  
                  <Textarea
                    value={broadcastMessage}
                    onChange={(e) => setBroadcastMessage(e.target.value)}
                    placeholder="Type your message here..."
                    className="text-gray-900"
                    rows={4}
                  />
                  
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setBroadcastOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleBroadcast} disabled={!broadcastMessage.trim()}>
                      Send Message
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Stats Row */}
        <div className="mt-4 grid grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-blue-600">Students Connected</p>
                <p className="text-lg font-semibold text-blue-900">
                  {sessionStatus?.connectedStudents || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-green-50 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-green-600">Submissions</p>
                <p className="text-lg font-semibold text-green-900">
                  {messages.filter(m => m.type === 'answer_submitted').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-sm text-yellow-600">Total Questions</p>
                <p className="text-lg font-semibold text-yellow-900">
                  {exam.total_questions || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-purple-50 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-purple-600">Duration</p>
                <p className="text-lg font-semibold text-purple-900">
                  {session.time_limit_override || exam.time_limit_minutes || 'No limit'}
                  {(session.time_limit_override || exam.time_limit_minutes) && 'm'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-white">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="control">Session Control</TabsTrigger>
            <TabsTrigger value="progress">Live Progress</TabsTrigger>
            <TabsTrigger value="messages">Messages</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-2 gap-6">
              {/* Session Information */}
              <Card className="bg-white">
                <CardHeader>
                  <CardTitle className="text-gray-900">Session Information</CardTitle>
                  <CardDescription>Basic session details and configuration</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Session ID:</span>
                      <span className="ml-2 text-gray-900">{session.id.slice(-8)}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Class:</span>
                      <span className="ml-2 text-gray-900">{session.class_id.slice(-4)}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Status:</span>
                      <Badge variant="secondary" className={`ml-2 ${getStatusColor(sessionStatus?.status)}`}>
                        {sessionStatus?.status || 'Unknown'}
                      </Badge>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Late Entry:</span>
                      <span className="ml-2 text-gray-900">{session.allow_late_entry ? 'Allowed' : 'Not Allowed'}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Shuffle Questions:</span>
                      <span className="ml-2 text-gray-900">{session.shuffle_questions ? 'Yes' : 'No'}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Created:</span>
                      <span className="ml-2 text-gray-900">{new Date(session.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  {session.instructions && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-2">Instructions</h4>
                      <p className="text-gray-700 text-sm">{session.instructions}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Exam Information */}
              <Card className="bg-white">
                <CardHeader>
                  <CardTitle className="text-gray-900">Exam Information</CardTitle>
                  <CardDescription>Details about the exam being conducted</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Title:</span>
                      <span className="ml-2 text-gray-900">{exam.title}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Questions:</span>
                      <span className="ml-2 text-gray-900">{exam.total_questions}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Time Limit:</span>
                      <span className="ml-2 text-gray-900">
                        {session.time_limit_override || exam.time_limit_minutes || 'No limit'}
                        {(session.time_limit_override || exam.time_limit_minutes) && ' minutes'}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Attempts:</span>
                      <span className="ml-2 text-gray-900">
                        {session.attempts_allowed_override || exam.attempts_allowed}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Passing Score:</span>
                      <span className="ml-2 text-gray-900">{exam.passing_score || 'Not set'}%</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Show Results:</span>
                      <span className="ml-2 text-gray-900">{exam.show_results ? 'Yes' : 'No'}</span>
                    </div>
                  </div>

                  {exam.subject_tags && exam.subject_tags.length > 0 && (
                    <div className="mt-4">
                      <h4 className="font-medium text-gray-900 mb-2">Subject Tags</h4>
                      <div className="flex gap-2">
                        {exam.subject_tags.map((tag: string, index: number) => (
                          <Badge key={index} variant="secondary" className="bg-gray-100 text-gray-800">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card className="bg-white">
              <CardHeader>
                <CardTitle className="text-gray-900">Quick Actions</CardTitle>
                <CardDescription>Common session management actions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex space-x-4">
                  <Button 
                    onClick={onRequestProgress}
                    disabled={!isConnected}
                    variant="outline"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh Progress
                  </Button>
                  
                  <Button 
                    onClick={() => setActiveTab('control')}
                    disabled={!isConnected}
                    className="bg-gray-900 hover:bg-gray-800 text-white"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Session Control
                  </Button>
                  
                  <Button 
                    onClick={() => setActiveTab('progress')}
                    variant="outline"
                  >
                    <BarChart3 className="h-4 w-4 mr-2" />
                    View Progress
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Session Control Tab */}
          <TabsContent value="control">
            <SessionControlPanel
              session={session}
              sessionStatus={sessionStatus}
              isConnected={isConnected}
              onControlSession={onControlSession}
            />
          </TabsContent>

          {/* Live Progress Tab */}
          <TabsContent value="progress">
            <LiveStudentProgress
              sessionStatus={sessionStatus}
              messages={messages}
              totalQuestions={exam.total_questions}
              onRequestProgress={onRequestProgress}
              isConnected={isConnected}
            />
          </TabsContent>

          {/* Messages Tab */}
          <TabsContent value="messages">
            <SessionMessages
              messages={messages}
              onBroadcastMessage={onBroadcastMessage}
              isConnected={isConnected}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}