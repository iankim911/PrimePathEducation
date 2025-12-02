"use client"

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { StudentExamInterface } from '@/components/features/student/StudentExamInterface'
import { ExamJoinScreen } from '@/components/features/student/ExamJoinScreen'
import { ExamCompletedScreen } from '@/components/features/student/ExamCompletedScreen'
import { useSocket } from '@/lib/hooks/useSocket'
import { Loader2 } from 'lucide-react'
import type { ExamQuestion } from '@/lib/services/exams'

export default function StudentExamPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params.sessionId as string

  const [examState, setExamState] = useState<'joining' | 'waiting' | 'active' | 'completed'>('joining')
  const [studentInfo, setStudentInfo] = useState<{
    id: string
    name: string
    academyId: string
  } | null>(null)
  const [examData, setExamData] = useState<{
    exam: any
    questions: ExamQuestion[]
    session: any
  } | null>(null)
  const [loading, setLoading] = useState(false)

  const {
    socket,
    isConnected,
    sessionStatus,
    messages,
    joinSession,
    sendAnswer,
    connectionError
  } = useSocket()

  // Handle student joining the exam
  const handleJoinExam = async (studentData: { name: string; studentId: string }) => {
    setLoading(true)
    setStudentInfo({
      id: studentData.studentId,
      name: studentData.name,
      academyId: 'default-academy-id' // This should come from context
    })

    try {
      // Fetch exam session data
      const response = await fetch(`/api/exam-sessions/${sessionId}`)
      if (!response.ok) {
        throw new Error('Session not found')
      }

      const sessionData = await response.json()
      setExamData(sessionData)

      // Join the WebSocket session
      joinSession({
        sessionId,
        userId: studentData.studentId,
        userName: studentData.name,
        role: 'student',
        academyId: 'default-academy-id'
      })

      setExamState('waiting')
    } catch (error) {
      console.error('Error joining exam:', error)
      alert('Failed to join exam. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Handle exam state changes from WebSocket messages
  useEffect(() => {
    if (!messages.length) return

    const latestMessage = messages[messages.length - 1]
    
    switch (latestMessage.type) {
      case 'session_start':
        if (examState === 'waiting') {
          setExamState('active')
        }
        break
      
      case 'session_end':
        if (examState === 'active') {
          setExamState('completed')
        }
        break
    }
  }, [messages, examState])

  // Handle session status changes
  useEffect(() => {
    if (!sessionStatus) return

    if (sessionStatus.status === 'active' && examState === 'waiting') {
      setExamState('active')
    } else if (sessionStatus.status === 'completed' && examState === 'active') {
      setExamState('completed')
    }
  }, [sessionStatus, examState])

  // Handle answer submission
  const handleAnswerSubmission = (questionId: string, answer: any, timeSpent: number) => {
    sendAnswer({
      questionId,
      answer,
      timeSpent
    })
  }

  // Handle exam completion
  const handleExamComplete = async () => {
    try {
      // Submit final exam data to server
      const response = await fetch(`/api/exam-sessions/${sessionId}/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          studentId: studentInfo?.id,
          completedAt: new Date().toISOString()
        })
      })

      if (response.ok) {
        setExamState('completed')
      }
    } catch (error) {
      console.error('Error completing exam:', error)
    }
  }

  // Connection error handling
  if (connectionError && examState !== 'joining') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-lg shadow-sm border max-w-md w-full text-center">
          <div className="text-red-500 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">{connectionError}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 rounded-lg"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500 mx-auto mb-4" />
          <p className="text-gray-600">Joining exam...</p>
        </div>
      </div>
    )
  }

  // Render based on exam state
  switch (examState) {
    case 'joining':
      return (
        <ExamJoinScreen
          sessionId={sessionId}
          onJoin={handleJoinExam}
          isConnected={isConnected}
        />
      )

    case 'waiting':
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="bg-white p-8 rounded-lg shadow-sm border max-w-md w-full text-center">
            <div className="text-blue-500 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Waiting for Exam to Start</h2>
            <p className="text-gray-600 mb-4">
              You've successfully joined the exam session. Please wait for your teacher to start the exam.
            </p>
            {sessionStatus && (
              <div className="text-sm text-gray-500">
                <p>Connected students: {sessionStatus.connectedStudents}</p>
                <p>Status: {sessionStatus.status}</p>
              </div>
            )}
          </div>
        </div>
      )

    case 'active':
      return examData ? (
        <StudentExamInterface
          exam={examData.exam}
          questions={examData.questions}
          session={examData.session}
          sessionStatus={sessionStatus}
          messages={messages}
          onAnswerSubmit={handleAnswerSubmission}
          onComplete={handleExamComplete}
        />
      ) : (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-gray-500 mx-auto mb-4" />
            <p className="text-gray-600">Loading exam...</p>
          </div>
        </div>
      )

    case 'completed':
      return (
        <ExamCompletedScreen
          studentName={studentInfo?.name || 'Student'}
          examTitle={examData?.exam?.title || 'Exam'}
          sessionId={sessionId}
        />
      )

    default:
      return null
  }
}