"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { User, Wifi, WifiOff, BookOpen } from 'lucide-react'

interface ExamJoinScreenProps {
  sessionId: string
  onJoin: (studentData: { name: string; studentId: string }) => void
  isConnected: boolean
}

export function ExamJoinScreen({ sessionId, onJoin, isConnected }: ExamJoinScreenProps) {
  const [studentName, setStudentName] = useState('')
  const [studentId, setStudentId] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!studentName.trim() || !studentId.trim()) {
      alert('Please enter both your name and student ID')
      return
    }

    if (!isConnected) {
      alert('Not connected to server. Please check your internet connection.')
      return
    }

    setLoading(true)
    
    try {
      await onJoin({
        name: studentName.trim(),
        studentId: studentId.trim()
      })
    } catch (error) {
      console.error('Error joining exam:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Connection Status */}
        <div className="mb-6 text-center">
          <Badge 
            variant={isConnected ? "default" : "secondary"} 
            className={`${isConnected ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"} mb-2`}
          >
            {isConnected ? (
              <>
                <Wifi className="h-3 w-3 mr-1" />
                Connected
              </>
            ) : (
              <>
                <WifiOff className="h-3 w-3 mr-1" />
                Connecting...
              </>
            )}
          </Badge>
        </div>

        <Card className="bg-white shadow-sm border">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <BookOpen className="h-8 w-8 text-gray-600" />
            </div>
            <CardTitle className="text-2xl font-bold text-gray-900">
              Join Exam Session
            </CardTitle>
            <CardDescription className="text-gray-600">
              Enter your information to join the exam
            </CardDescription>
            <div className="mt-2">
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                Session: {sessionId.slice(-8)}
              </Badge>
            </div>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Student Name */}
              <div className="space-y-2">
                <Label htmlFor="studentName" className="text-gray-900 font-medium">
                  Full Name *
                </Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="studentName"
                    type="text"
                    value={studentName}
                    onChange={(e) => setStudentName(e.target.value)}
                    placeholder="Enter your full name"
                    className="pl-10 text-gray-900 h-12 text-lg"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Student ID */}
              <div className="space-y-2">
                <Label htmlFor="studentId" className="text-gray-900 font-medium">
                  Student ID *
                </Label>
                <Input
                  id="studentId"
                  type="text"
                  value={studentId}
                  onChange={(e) => setStudentId(e.target.value)}
                  placeholder="Enter your student ID"
                  className="text-gray-900 h-12 text-lg"
                  required
                  disabled={loading}
                />
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={!isConnected || loading || !studentName.trim() || !studentId.trim()}
                className="w-full h-12 text-lg bg-gray-900 hover:bg-gray-800 text-white"
              >
                {loading ? 'Joining...' : 'Join Exam'}
              </Button>
            </form>

            {/* Instructions */}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Instructions:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Make sure you have a stable internet connection</li>
                <li>• Use your full name as registered in class</li>
                <li>• Enter your student ID exactly as provided</li>
                <li>• Wait for your teacher to start the exam</li>
              </ul>
            </div>

            {/* Tablet Optimization Notice */}
            <div className="mt-4 text-center">
              <p className="text-xs text-gray-500">
                This exam is optimized for tablets and large screens
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Technical Support */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            Having issues? Contact your teacher or IT support
          </p>
        </div>
      </div>
    </div>
  )
}