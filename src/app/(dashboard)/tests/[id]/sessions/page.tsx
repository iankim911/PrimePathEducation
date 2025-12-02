"use client"

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { SessionsTable } from '@/components/features/tests/SessionsTable'
import { SessionForm } from '@/components/features/tests/SessionForm'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { Exam } from '@/lib/services/exams'
import { Loader2, Search, X, Plus, ArrowLeft, Calendar } from 'lucide-react'

export interface ExamSession {
  id: string
  academy_id: string
  exam_id: string
  class_id: string
  teacher_id: string
  title: string
  instructions?: string | null
  scheduled_start?: string | null
  scheduled_end?: string | null
  actual_start?: string | null
  actual_end?: string | null
  time_limit_override?: number | null
  attempts_allowed_override?: number | null
  allow_late_entry: boolean
  shuffle_questions: boolean
  status: string
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

export default function ExamSessionsPage() {
  const params = useParams()
  const examId = params.id as string

  const [exam, setExam] = useState<Exam | null>(null)
  const [sessions, setSessions] = useState<ExamSession[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const fetchExam = async () => {
    try {
      const response = await fetch(`/api/exams/${examId}`)
      if (!response.ok) throw new Error('Failed to fetch exam')
      const data = await response.json()
      setExam(data.exam)
    } catch (error) {
      console.error('Error fetching exam:', error)
    }
  }

  const fetchSessions = async () => {
    try {
      const response = await fetch(`/api/exam-sessions?examId=${examId}`)
      if (!response.ok) throw new Error('Failed to fetch sessions')
      const data = await response.json()
      setSessions(data.sessions || [])
    } catch (error) {
      console.error('Error fetching sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchExam()
    fetchSessions()
  }, [examId])

  const filteredSessions = sessions.filter(session => {
    const matchesSearch = !searchTerm || 
      session.title.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus = statusFilter === 'all' || session.status === statusFilter

    return matchesSearch && matchesStatus
  })

  const clearFilters = () => {
    setSearchTerm('')
    setStatusFilter('all')
  }

  const hasActiveFilters = searchTerm || statusFilter !== 'all'

  if (loading && !exam) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header with Navigation */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => window.history.back()}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Tests
          </Button>
        </div>
        
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Exam Sessions
            </h2>
            {exam && (
              <div className="mt-2 space-y-1">
                <p className="text-lg text-gray-700">{exam.title}</p>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>{sessions.length} sessions</span>
                  </div>
                  {exam.subject_tags && exam.subject_tags.length > 0 && (
                    <div className="flex gap-1">
                      {exam.subject_tags.map((tag, index) => (
                        <Badge key={index} variant="secondary" className="bg-gray-100 text-gray-800">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
          <SessionForm examId={examId} onSuccess={fetchSessions} />
        </div>
      </div>

      {/* Search and Filter Bar */}
      <div className="mb-6 space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search sessions by title..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 text-gray-900 placeholder:text-gray-500"
            />
          </div>

          {/* Status Filter */}
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-full sm:w-[200px] text-gray-900">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              <SelectItem value="all" className="text-gray-900">All Statuses</SelectItem>
              <SelectItem value="scheduled" className="text-gray-900">Scheduled</SelectItem>
              <SelectItem value="active" className="text-gray-900">Active</SelectItem>
              <SelectItem value="completed" className="text-gray-900">Completed</SelectItem>
              <SelectItem value="cancelled" className="text-gray-900">Cancelled</SelectItem>
            </SelectContent>
          </Select>

          {/* Clear Filters Button */}
          {hasActiveFilters && (
            <Button
              variant="outline"
              onClick={clearFilters}
              className="w-full sm:w-auto"
            >
              <X className="h-4 w-4 mr-2" />
              Clear
            </Button>
          )}
        </div>

        {/* Results Count */}
        {hasActiveFilters && (
          <div className="text-sm text-gray-600">
            Showing {filteredSessions.length} of {sessions.length} sessions
          </div>
        )}
      </div>

      {/* Sessions Table */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
        </div>
      ) : (
        <SessionsTable 
          sessions={filteredSessions} 
          examId={examId}
          onRefresh={fetchSessions} 
        />
      )}
    </div>
  )
}