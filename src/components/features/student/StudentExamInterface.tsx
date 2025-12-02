"use client"

import { useState, useEffect, useRef, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Textarea } from '@/components/ui/textarea'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { 
  Clock, 
  FileText, 
  Volume2, 
  ChevronLeft, 
  ChevronRight,
  Flag,
  CheckCircle2,
  AlertCircle,
  BookOpen
} from 'lucide-react'
import type { ExamQuestion } from '@/lib/services/exams'
import type { SessionStatus, ExamMessage } from '@/lib/websocket/socketManager'

interface StudentExamInterfaceProps {
  exam: any
  questions: ExamQuestion[]
  session: any
  sessionStatus: SessionStatus | null
  messages: ExamMessage[]
  onAnswerSubmit: (questionId: string, answer: any, timeSpent: number) => void
  onComplete: () => void
}

interface StudentAnswer {
  questionId: string
  answer: any
  timeSpent: number
  answered: boolean
  flagged: boolean
}

export function StudentExamInterface({
  exam,
  questions,
  session,
  sessionStatus,
  messages,
  onAnswerSubmit,
  onComplete
}: StudentExamInterfaceProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<Map<string, StudentAnswer>>(new Map())
  const [showCompleteModal, setShowCompleteModal] = useState(false)
  const [autoSaveStatus, setAutoSaveStatus] = useState<'saved' | 'saving' | 'error'>('saved')
  
  const questionStartTimeRef = useRef<number>(Date.now())
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  
  const currentQuestion = questions[currentQuestionIndex]
  const totalQuestions = questions.length
  const answeredCount = Array.from(answers.values()).filter(a => a.answered).length
  const progressPercentage = (answeredCount / totalQuestions) * 100

  // Initialize answers map
  useEffect(() => {
    const initialAnswers = new Map<string, StudentAnswer>()
    questions.forEach(question => {
      initialAnswers.set(question.id, {
        questionId: question.id,
        answer: null,
        timeSpent: 0,
        answered: false,
        flagged: false
      })
    })
    setAnswers(initialAnswers)
  }, [questions])

  // Track time spent on current question
  useEffect(() => {
    questionStartTimeRef.current = Date.now()
  }, [currentQuestionIndex])

  // Auto-save functionality
  const autoSave = useCallback((questionId: string, answer: any) => {
    setAutoSaveStatus('saving')
    
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current)
    }

    autoSaveTimeoutRef.current = setTimeout(() => {
      const timeSpent = Math.floor((Date.now() - questionStartTimeRef.current) / 1000)
      
      try {
        onAnswerSubmit(questionId, answer, timeSpent)
        setAutoSaveStatus('saved')
      } catch (error) {
        setAutoSaveStatus('error')
        console.error('Auto-save failed:', error)
      }
    }, 2000) // Save after 2 seconds of inactivity
  }, [onAnswerSubmit])

  // Update answer and trigger auto-save
  const updateAnswer = useCallback((questionId: string, answer: any) => {
    setAnswers(prev => {
      const updated = new Map(prev)
      const current = updated.get(questionId) || {
        questionId,
        answer: null,
        timeSpent: 0,
        answered: false,
        flagged: false
      }
      
      updated.set(questionId, {
        ...current,
        answer,
        answered: answer !== null && answer !== '' && answer !== undefined
      })
      
      return updated
    })

    autoSave(questionId, answer)
  }, [autoSave])

  // Toggle flag for question
  const toggleFlag = useCallback((questionId: string) => {
    setAnswers(prev => {
      const updated = new Map(prev)
      const current = updated.get(questionId) || {
        questionId,
        answer: null,
        timeSpent: 0,
        answered: false,
        flagged: false
      }
      
      updated.set(questionId, {
        ...current,
        flagged: !current.flagged
      })
      
      return updated
    })
  }, [])

  // Navigation functions
  const goToQuestion = useCallback((index: number) => {
    if (index >= 0 && index < totalQuestions) {
      setCurrentQuestionIndex(index)
    }
  }, [totalQuestions])

  const nextQuestion = useCallback(() => {
    if (currentQuestionIndex < totalQuestions - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
    }
  }, [currentQuestionIndex, totalQuestions])

  const previousQuestion = useCallback(() => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1)
    }
  }, [currentQuestionIndex])

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

  // Handle exam completion
  const handleComplete = () => {
    const unansweredQuestions = Array.from(answers.values()).filter(a => !a.answered)
    
    if (unansweredQuestions.length > 0) {
      const confirmMessage = `You have ${unansweredQuestions.length} unanswered questions. Are you sure you want to submit your exam?`
      if (!confirm(confirmMessage)) {
        return
      }
    }
    
    setShowCompleteModal(true)
  }

  // Confirm completion
  const confirmComplete = () => {
    // Submit all final answers
    answers.forEach((answer, questionId) => {
      if (answer.answered) {
        onAnswerSubmit(questionId, answer.answer, answer.timeSpent)
      }
    })
    
    onComplete()
  }

  // Render question based on type
  const renderQuestion = (question: ExamQuestion) => {
    const currentAnswer = answers.get(question.id)
    
    switch (question.question_type) {
      case 'multiple_choice':
        return (
          <RadioGroup
            value={currentAnswer?.answer || ''}
            onValueChange={(value) => updateAnswer(question.id, value)}
            className="space-y-3"
          >
            {question.answer_options && Array.isArray(question.answer_options) && 
              question.answer_options.map((option: string, index: number) => (
                <div key={index} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                  <RadioGroupItem value={index.toString()} id={`${question.id}-${index}`} />
                  <Label htmlFor={`${question.id}-${index}`} className="text-gray-900 cursor-pointer flex-1">
                    {String.fromCharCode(65 + index)}. {option}
                  </Label>
                </div>
              ))}
          </RadioGroup>
        )

      case 'multiple_select':
        const selectedAnswers = currentAnswer?.answer || []
        return (
          <div className="space-y-3">
            {question.answer_options && Array.isArray(question.answer_options) && 
              question.answer_options.map((option: string, index: number) => (
                <div key={index} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                  <Checkbox
                    id={`${question.id}-${index}`}
                    checked={selectedAnswers.includes(index)}
                    onCheckedChange={(checked) => {
                      const newAnswers = checked
                        ? [...selectedAnswers, index]
                        : selectedAnswers.filter((i: number) => i !== index)
                      updateAnswer(question.id, newAnswers)
                    }}
                  />
                  <Label htmlFor={`${question.id}-${index}`} className="text-gray-900 cursor-pointer flex-1">
                    {String.fromCharCode(65 + index)}. {option}
                  </Label>
                </div>
              ))}
          </div>
        )

      case 'true_false':
        return (
          <RadioGroup
            value={currentAnswer?.answer || ''}
            onValueChange={(value) => updateAnswer(question.id, value)}
            className="space-y-3"
          >
            <div className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50">
              <RadioGroupItem value="true" id={`${question.id}-true`} />
              <Label htmlFor={`${question.id}-true`} className="text-gray-900 cursor-pointer flex-1">
                True
              </Label>
            </div>
            <div className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50">
              <RadioGroupItem value="false" id={`${question.id}-false`} />
              <Label htmlFor={`${question.id}-false`} className="text-gray-900 cursor-pointer flex-1">
                False
              </Label>
            </div>
          </RadioGroup>
        )

      case 'short_answer':
        return (
          <Textarea
            value={currentAnswer?.answer || ''}
            onChange={(e) => updateAnswer(question.id, e.target.value)}
            placeholder="Enter your answer here..."
            className="min-h-[100px] text-gray-900 text-lg"
            rows={3}
          />
        )

      case 'long_answer':
        return (
          <Textarea
            value={currentAnswer?.answer || ''}
            onChange={(e) => updateAnswer(question.id, e.target.value)}
            placeholder="Enter your detailed answer here..."
            className="min-h-[200px] text-gray-900 text-lg"
            rows={8}
          />
        )

      default:
        return (
          <div className="text-gray-500 italic">
            Unsupported question type: {question.question_type}
          </div>
        )
    }
  }

  // Handle session end via WebSocket
  useEffect(() => {
    const sessionEndMessage = messages.find(m => m.type === 'session_end')
    if (sessionEndMessage) {
      // Auto-submit exam when session ends
      confirmComplete()
    }
  }, [messages])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <BookOpen className="h-6 w-6 text-gray-600" />
            <div>
              <h1 className="text-lg font-semibold text-gray-900">{exam.title}</h1>
              <p className="text-sm text-gray-600">
                Question {currentQuestionIndex + 1} of {totalQuestions}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Auto-save status */}
            <div className="flex items-center space-x-2 text-sm">
              {autoSaveStatus === 'saved' && (
                <>
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <span className="text-green-600">Saved</span>
                </>
              )}
              {autoSaveStatus === 'saving' && (
                <>
                  <div className="h-4 w-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin" />
                  <span className="text-gray-600">Saving...</span>
                </>
              )}
              {autoSaveStatus === 'error' && (
                <>
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-red-600">Error</span>
                </>
              )}
            </div>

            {/* Time remaining */}
            {sessionStatus?.timeRemaining !== undefined && (
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-gray-600" />
                <span className={`font-mono text-lg ${
                  sessionStatus.timeRemaining < 300 ? 'text-red-600' : 'text-gray-900'
                }`}>
                  {formatTime(sessionStatus.timeRemaining)}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-3">
          <Progress value={progressPercentage} className="h-2" />
          <div className="flex justify-between text-xs text-gray-600 mt-1">
            <span>{answeredCount} answered</span>
            <span>{totalQuestions - answeredCount} remaining</span>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Question Navigation Sidebar */}
        <div className="w-64 bg-white border-r border-gray-200 p-4 overflow-y-auto h-[calc(100vh-140px)]">
          <h3 className="font-medium text-gray-900 mb-3">Questions</h3>
          <div className="grid grid-cols-4 gap-2">
            {questions.map((question, index) => {
              const answer = answers.get(question.id)
              return (
                <Button
                  key={question.id}
                  onClick={() => goToQuestion(index)}
                  variant={currentQuestionIndex === index ? "default" : "outline"}
                  size="sm"
                  className={`
                    h-10 relative
                    ${answer?.answered ? 'border-green-500 bg-green-50 hover:bg-green-100' : ''}
                    ${answer?.flagged ? 'border-orange-500' : ''}
                  `}
                >
                  {index + 1}
                  {answer?.flagged && (
                    <Flag className="h-3 w-3 text-orange-500 absolute -top-1 -right-1" />
                  )}
                </Button>
              )
            })}
          </div>
        </div>

        {/* Main Question Area */}
        <div className="flex-1 p-6">
          <Card className="bg-white shadow-sm">
            <CardContent className="p-6">
              {/* Question Header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <Badge variant="secondary" className="bg-gray-100 text-gray-800">
                      Question {currentQuestionIndex + 1}
                    </Badge>
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                      {currentQuestion.question_type.replace('_', ' ').toUpperCase()}
                    </Badge>
                    {currentQuestion.points && (
                      <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                        {currentQuestion.points} pts
                      </Badge>
                    )}
                  </div>
                  
                  <h2 className="text-xl font-medium text-gray-900 leading-relaxed">
                    {currentQuestion.question_text}
                  </h2>
                  
                  {currentQuestion.instructions && (
                    <p className="text-gray-600 mt-2">
                      {currentQuestion.instructions}
                    </p>
                  )}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => toggleFlag(currentQuestion.id)}
                  className={answers.get(currentQuestion.id)?.flagged ? 'border-orange-500 bg-orange-50' : ''}
                >
                  <Flag className="h-4 w-4" />
                  Flag
                </Button>
              </div>

              {/* Audio Player if applicable */}
              {currentQuestion.audio_start_seconds && (
                <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Volume2 className="h-5 w-5 text-blue-600" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Audio Section</p>
                      <p className="text-xs text-gray-600">
                        Listen from {currentQuestion.audio_start_seconds}s
                        {currentQuestion.audio_end_seconds && ` to ${currentQuestion.audio_end_seconds}s`}
                      </p>
                    </div>
                    <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                      Play Audio
                    </Button>
                  </div>
                </div>
              )}

              {/* Question Content */}
              <div className="mb-8">
                {renderQuestion(currentQuestion)}
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-between pt-6 border-t border-gray-200">
                <Button
                  onClick={previousQuestion}
                  disabled={currentQuestionIndex === 0}
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  <ChevronLeft className="h-4 w-4" />
                  <span>Previous</span>
                </Button>

                <div className="flex space-x-4">
                  {currentQuestionIndex === totalQuestions - 1 ? (
                    <Button
                      onClick={handleComplete}
                      className="bg-green-600 hover:bg-green-700 text-white px-8"
                    >
                      Submit Exam
                    </Button>
                  ) : (
                    <Button
                      onClick={nextQuestion}
                      className="bg-gray-900 hover:bg-gray-800 text-white flex items-center space-x-2"
                    >
                      <span>Next</span>
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Completion Confirmation Modal */}
      {showCompleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <Card className="bg-white max-w-md w-full">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Submit Exam?
              </h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to submit your exam? You won't be able to make changes after submitting.
              </p>
              <div className="flex space-x-4">
                <Button
                  onClick={() => setShowCompleteModal(false)}
                  variant="outline"
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={confirmComplete}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                >
                  Submit
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}