"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
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
  Clock,
  AlertTriangle,
  CheckCircle2,
  Settings
} from 'lucide-react'
import type { ExamSession } from '@/app/(dashboard)/tests/[id]/sessions/page'
import type { SessionStatus } from '@/lib/websocket/socketManager'

interface SessionControlPanelProps {
  session: ExamSession
  sessionStatus: SessionStatus | null
  isConnected: boolean
  onControlSession: (action: 'start' | 'pause' | 'resume' | 'end', timeLimit?: number) => void
}

export function SessionControlPanel({
  session,
  sessionStatus,
  isConnected,
  onControlSession
}: SessionControlPanelProps) {
  const [customTimeLimit, setCustomTimeLimit] = useState<string>('')
  const [confirmAction, setConfirmAction] = useState<string | null>(null)

  const handleStartSession = () => {
    const timeLimit = customTimeLimit ? parseInt(customTimeLimit) : 
                     session.time_limit_override || 
                     (session as any).exam?.time_limit_minutes
    
    onControlSession('start', timeLimit)
    setConfirmAction(null)
  }

  const handleControlAction = (action: 'pause' | 'resume' | 'end') => {
    onControlSession(action)
    setConfirmAction(null)
  }

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const getStatusIndicator = () => {
    switch (sessionStatus?.status) {
      case 'active':
        return (
          <Badge className="bg-green-100 text-green-800">
            <CheckCircle2 className="h-3 w-3 mr-1" />
            Session Active
          </Badge>
        )
      case 'paused':
        return (
          <Badge className="bg-yellow-100 text-yellow-800">
            <Pause className="h-3 w-3 mr-1" />
            Session Paused
          </Badge>
        )
      case 'completed':
        return (
          <Badge className="bg-gray-100 text-gray-600">
            <Square className="h-3 w-3 mr-1" />
            Session Ended
          </Badge>
        )
      default:
        return (
          <Badge className="bg-blue-100 text-blue-800">
            <Clock className="h-3 w-3 mr-1" />
            Ready to Start
          </Badge>
        )
    }
  }

  return (
    <div className="space-y-6">
      {/* Session Status */}
      <Card className="bg-white">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="text-gray-900">Session Control</span>
            {getStatusIndicator()}
          </CardTitle>
          <CardDescription>
            Manage the current exam session - start, pause, resume, or end the session
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Current Status */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-sm text-gray-600">Status</p>
                <p className="text-lg font-semibold text-gray-900 capitalize">
                  {sessionStatus?.status || 'Waiting'}
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-sm text-gray-600">Connected Students</p>
                <p className="text-lg font-semibold text-gray-900">
                  {sessionStatus?.connectedStudents || 0}
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-sm text-gray-600">Time Remaining</p>
                <p className="text-lg font-semibold text-gray-900 font-mono">
                  {sessionStatus?.timeRemaining !== undefined 
                    ? formatTime(sessionStatus.timeRemaining)
                    : 'Not started'
                  }
                </p>
              </div>
            </div>

            {sessionStatus?.timeRemaining !== undefined && sessionStatus.timeRemaining < 300 && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  <p className="text-red-800 font-medium">
                    Warning: Less than 5 minutes remaining!
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Control Actions */}
          <div className="space-y-4">
            {!sessionStatus?.status || sessionStatus?.status === 'waiting' ? (
              // Start Session
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Start Exam Session</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Begin the exam for all connected students. Make sure all students have joined before starting.
                  </p>
                  
                  <div className="space-y-3">
                    <div>
                      <Label htmlFor="time-limit" className="text-gray-900">
                        Time Limit (minutes) - Optional Override
                      </Label>
                      <Input
                        id="time-limit"
                        type="number"
                        value={customTimeLimit}
                        onChange={(e) => setCustomTimeLimit(e.target.value)}
                        placeholder={`Default: ${session.time_limit_override || 'No limit'}`}
                        className="mt-1 text-gray-900"
                        min="1"
                        max="480"
                      />
                    </div>
                    
                    <Dialog open={confirmAction === 'start'} onOpenChange={(open) => !open && setConfirmAction(null)}>
                      <DialogTrigger asChild>
                        <Button 
                          className="w-full bg-green-600 hover:bg-green-700 text-white h-12 text-lg"
                          disabled={!isConnected}
                          onClick={() => setConfirmAction('start')}
                        >
                          <Play className="h-5 w-5 mr-2" />
                          Start Exam Session
                        </Button>
                      </DialogTrigger>
                      
                      <DialogContent className="bg-white">
                        <DialogHeader>
                          <DialogTitle className="text-gray-900">Start Exam Session</DialogTitle>
                          <DialogDescription className="text-gray-600">
                            Are you sure you want to start the exam session? All connected students will begin the exam immediately.
                          </DialogDescription>
                        </DialogHeader>
                        
                        <div className="space-y-4">
                          <div className="bg-blue-50 p-4 rounded-lg">
                            <h4 className="font-medium text-gray-900 mb-2">Session Details</h4>
                            <ul className="text-sm text-gray-700 space-y-1">
                              <li>• Connected Students: {sessionStatus?.connectedStudents || 0}</li>
                              <li>• Time Limit: {customTimeLimit || session.time_limit_override || 'No limit'} 
                                  {(customTimeLimit || session.time_limit_override) && ' minutes'}</li>
                              <li>• Late Entry: {session.allow_late_entry ? 'Allowed' : 'Not Allowed'}</li>
                            </ul>
                          </div>
                          
                          <div className="flex justify-end space-x-2">
                            <Button variant="outline" onClick={() => setConfirmAction(null)}>
                              Cancel
                            </Button>
                            <Button 
                              onClick={handleStartSession}
                              className="bg-green-600 hover:bg-green-700 text-white"
                            >
                              Start Session
                            </Button>
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              </div>
            ) : sessionStatus?.status === 'active' ? (
              // Active Session Controls
              <div className="grid grid-cols-2 gap-4">
                <Dialog open={confirmAction === 'pause'} onOpenChange={(open) => !open && setConfirmAction(null)}>
                  <DialogTrigger asChild>
                    <Button 
                      variant="outline"
                      className="h-12 text-lg"
                      disabled={!isConnected}
                      onClick={() => setConfirmAction('pause')}
                    >
                      <Pause className="h-5 w-5 mr-2" />
                      Pause Session
                    </Button>
                  </DialogTrigger>
                  
                  <DialogContent className="bg-white">
                    <DialogHeader>
                      <DialogTitle className="text-gray-900">Pause Exam Session</DialogTitle>
                      <DialogDescription className="text-gray-600">
                        This will pause the exam for all students. The timer will stop and students won't be able to submit answers.
                      </DialogDescription>
                    </DialogHeader>
                    
                    <div className="flex justify-end space-x-2">
                      <Button variant="outline" onClick={() => setConfirmAction(null)}>
                        Cancel
                      </Button>
                      <Button 
                        onClick={() => handleControlAction('pause')}
                        className="bg-yellow-600 hover:bg-yellow-700 text-white"
                      >
                        Pause Session
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>

                <Dialog open={confirmAction === 'end'} onOpenChange={(open) => !open && setConfirmAction(null)}>
                  <DialogTrigger asChild>
                    <Button 
                      variant="outline"
                      className="h-12 text-lg border-red-300 text-red-600 hover:bg-red-50"
                      disabled={!isConnected}
                      onClick={() => setConfirmAction('end')}
                    >
                      <Square className="h-5 w-5 mr-2" />
                      End Session
                    </Button>
                  </DialogTrigger>
                  
                  <DialogContent className="bg-white">
                    <DialogHeader>
                      <DialogTitle className="text-gray-900">End Exam Session</DialogTitle>
                      <DialogDescription className="text-gray-600">
                        This will immediately end the exam for all students. All submitted answers will be saved, but students won't be able to make further changes.
                      </DialogDescription>
                    </DialogHeader>
                    
                    <div className="bg-red-50 p-4 rounded-lg mb-4">
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="h-5 w-5 text-red-600" />
                        <p className="text-red-800 font-medium">
                          This action cannot be undone!
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex justify-end space-x-2">
                      <Button variant="outline" onClick={() => setConfirmAction(null)}>
                        Cancel
                      </Button>
                      <Button 
                        onClick={() => handleControlAction('end')}
                        className="bg-red-600 hover:bg-red-700 text-white"
                      >
                        End Session
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            ) : sessionStatus?.status === 'paused' ? (
              // Resume Session
              <div className="space-y-4">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Session Paused</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    The exam session is currently paused. Students cannot submit answers while paused.
                  </p>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <Button 
                      onClick={() => handleControlAction('resume')}
                      className="h-12 text-lg bg-green-600 hover:bg-green-700 text-white"
                      disabled={!isConnected}
                    >
                      <Play className="h-5 w-5 mr-2" />
                      Resume Session
                    </Button>
                    
                    <Dialog open={confirmAction === 'end'} onOpenChange={(open) => !open && setConfirmAction(null)}>
                      <DialogTrigger asChild>
                        <Button 
                          variant="outline"
                          className="h-12 text-lg border-red-300 text-red-600 hover:bg-red-50"
                          disabled={!isConnected}
                          onClick={() => setConfirmAction('end')}
                        >
                          <Square className="h-5 w-5 mr-2" />
                          End Session
                        </Button>
                      </DialogTrigger>
                      
                      <DialogContent className="bg-white">
                        <DialogHeader>
                          <DialogTitle className="text-gray-900">End Exam Session</DialogTitle>
                          <DialogDescription className="text-gray-600">
                            This will permanently end the exam session. Students will not be able to resume.
                          </DialogDescription>
                        </DialogHeader>
                        
                        <div className="flex justify-end space-x-2">
                          <Button variant="outline" onClick={() => setConfirmAction(null)}>
                            Cancel
                          </Button>
                          <Button 
                            onClick={() => handleControlAction('end')}
                            className="bg-red-600 hover:bg-red-700 text-white"
                          >
                            End Session
                          </Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              </div>
            ) : (
              // Session Completed
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
                <CheckCircle2 className="h-12 w-12 text-gray-500 mx-auto mb-2" />
                <h4 className="font-medium text-gray-900 mb-2">Session Completed</h4>
                <p className="text-sm text-gray-600">
                  This exam session has ended. View the results and analytics in the other tabs.
                </p>
              </div>
            )}
          </div>

          {/* Connection Warning */}
          {!isConnected && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <p className="text-red-800 font-medium">
                  Not connected to server. Session controls are disabled.
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Session Information */}
      <Card className="bg-white">
        <CardHeader>
          <CardTitle className="text-gray-900 flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Session Configuration
          </CardTitle>
          <CardDescription>Current session settings and overrides</CardDescription>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Default Time Limit:</span>
              <span className="ml-2 text-gray-900">
                {session.time_limit_override || 'No override'}
                {session.time_limit_override && ' minutes'}
              </span>
            </div>
            
            <div>
              <span className="font-medium text-gray-700">Attempts Allowed:</span>
              <span className="ml-2 text-gray-900">
                {session.attempts_allowed_override || 'No override'}
              </span>
            </div>
            
            <div>
              <span className="font-medium text-gray-700">Late Entry:</span>
              <span className="ml-2 text-gray-900">
                {session.allow_late_entry ? 'Allowed' : 'Not Allowed'}
              </span>
            </div>
            
            <div>
              <span className="font-medium text-gray-700">Shuffle Questions:</span>
              <span className="ml-2 text-gray-900">
                {session.shuffle_questions ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}