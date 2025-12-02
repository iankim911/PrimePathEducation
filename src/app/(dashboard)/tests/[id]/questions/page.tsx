"use client"

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { QuestionsTable } from '@/components/features/tests/QuestionsTable'
import { QuestionForm } from '@/components/features/tests/QuestionForm'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { Exam, ExamQuestion } from '@/lib/services/exams'
import { getQuestionsByExam } from '@/lib/services/questions'
import { Loader2, Search, X, Plus, ArrowLeft, HelpCircle } from 'lucide-react'

export default function ExamQuestionsPage() {
  const params = useParams()
  const examId = params.id as string

  const [exam, setExam] = useState<Exam | null>(null)
  const [questions, setQuestions] = useState<ExamQuestion[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')

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

  const fetchQuestions = async () => {
    try {
      const academyId = 'default-academy-id' // This should be from context
      const questionsData = await getQuestionsByExam(examId, academyId)
      setQuestions(questionsData)
    } catch (error) {
      console.error('Error fetching questions:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchExam()
    fetchQuestions()
  }, [examId])

  const filteredQuestions = questions.filter(question => {
    const matchesSearch = !searchTerm || 
      question.question_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
      question.question_number.toString().includes(searchTerm)

    const matchesType = typeFilter === 'all' || question.question_type === typeFilter

    return matchesSearch && matchesType
  })

  const clearFilters = () => {
    setSearchTerm('')
    setTypeFilter('all')
  }

  const hasActiveFilters = searchTerm || typeFilter !== 'all'

  const questionTypeLabels = {
    multiple_choice: 'Multiple Choice',
    multiple_select: 'Multiple Select',
    short_answer: 'Short Answer',
    long_answer: 'Long Answer',
    true_false: 'True/False'
  }

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
              Question Management
            </h2>
            {exam && (
              <div className="mt-2 space-y-1">
                <p className="text-lg text-gray-700">{exam.title}</p>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <HelpCircle className="h-4 w-4" />
                    <span>{questions.length} questions</span>
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
          <QuestionForm examId={examId} onSuccess={fetchQuestions} />
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
              placeholder="Search questions by text or number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 text-gray-900 placeholder:text-gray-500"
            />
          </div>

          {/* Type Filter */}
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-full sm:w-[200px] text-gray-900">
              <SelectValue placeholder="All Types" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              <SelectItem value="all" className="text-gray-900">All Types</SelectItem>
              <SelectItem value="multiple_choice" className="text-gray-900">Multiple Choice</SelectItem>
              <SelectItem value="multiple_select" className="text-gray-900">Multiple Select</SelectItem>
              <SelectItem value="short_answer" className="text-gray-900">Short Answer</SelectItem>
              <SelectItem value="long_answer" className="text-gray-900">Long Answer</SelectItem>
              <SelectItem value="true_false" className="text-gray-900">True/False</SelectItem>
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
            Showing {filteredQuestions.length} of {questions.length} questions
          </div>
        )}
      </div>

      {/* Questions Table */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
        </div>
      ) : (
        <QuestionsTable 
          questions={filteredQuestions} 
          examId={examId}
          onRefresh={fetchQuestions} 
        />
      )}
    </div>
  )
}