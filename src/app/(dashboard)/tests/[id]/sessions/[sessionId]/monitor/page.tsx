"use client"

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { TeacherSessionDashboard } from '@/components/features/sessions/TeacherSessionDashboard'
import { useSocket } from '@/lib/hooks/useSocket'
import { Loader2 } from 'lucide-react'
import type { ExamSession } from '@/app/(dashboard)/tests/[id]/sessions/page'

export default function SessionMonitorPage() {
  const params = useParams()
  const examId = params.id as string
  const sessionId = params.sessionId as string

  const [session, setSession] = useState<ExamSession | null>(null)
  const [exam, setExam] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const {
    socket,
    isConnected,
    sessionStatus,
    messages,
    joinSession,
    controlSession,
    broadcastMessage,
    requestProgress,
    connectionError
  } = useSocket()

  // Fetch session and exam data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch session data
        const sessionResponse = await fetch(`/api/exam-sessions/${sessionId}`)
        if (!sessionResponse.ok) {
          throw new Error('Session not found')
        }
        const sessionData = await sessionResponse.json()
        setSession(sessionData.session)

        // Fetch exam data
        const examResponse = await fetch(`/api/exams/${examId}`)
        if (!examResponse.ok) {
          throw new Error('Exam not found')
        }
        const examData = await examResponse.json()
        setExam(examData.exam)

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [examId, sessionId])

  // Join session as teacher when data is loaded
  useEffect(() => {
    if (session && !socket && !loading) {
      joinSession({
        sessionId,
        userId: 'teacher-123', // This should come from auth context
        userName: 'Teacher Name', // This should come from auth context
        role: 'teacher',
        academyId: 'default-academy-id'
      })
    }
  }, [session, socket, loading, joinSession, sessionId])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading session...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-lg shadow-sm border max-w-md w-full text-center">
          <div className="text-red-500 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Session</h2>
          <p className="text-gray-600 mb-4">{error}</p>
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

  if (connectionError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-lg shadow-sm border max-w-md w-full text-center">
          <div className="text-red-500 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">{connectionError}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 rounded-lg"
          >
            Retry Connection
          </button>
        </div>
      </div>
    )
  }

  if (!session || !exam) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Session or exam not found</p>
        </div>
      </div>
    )
  }

  return (
    <TeacherSessionDashboard
      session={session}
      exam={exam}
      sessionStatus={sessionStatus}
      messages={messages}
      isConnected={isConnected}
      onControlSession={controlSession}
      onBroadcastMessage={broadcastMessage}
      onRequestProgress={requestProgress}
    />
  )
}