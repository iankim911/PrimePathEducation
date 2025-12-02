"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { 
  Plus, 
  X,
  Trash2,
  Check
} from 'lucide-react'
import { toast } from 'sonner'
import { createQuestion } from '@/lib/services/questions'
import type { ExamQuestion } from '@/lib/services/exams'

interface QuestionFormProps {
  examId: string
  onSuccess: () => void
}

interface AnswerOption {
  id: string
  text: string
  is_correct: boolean
}

interface QuestionFormData {
  question_text: string
  instructions: string
  question_type: string
  points: string
  answer_options: AnswerOption[]
  correct_answers: string[]
  explanation: string
  audio_start_seconds: string
  audio_end_seconds: string
}

export function QuestionForm({ examId, onSuccess }: QuestionFormProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  
  const [formData, setFormData] = useState<QuestionFormData>({
    question_text: '',
    instructions: '',
    question_type: 'multiple_choice',
    points: '1',
    answer_options: [
      { id: '1', text: '', is_correct: false },
      { id: '2', text: '', is_correct: false }
    ],
    correct_answers: [],
    explanation: '',
    audio_start_seconds: '',
    audio_end_seconds: ''
  })

  const questionTypes = [
    { value: 'multiple_choice', label: 'Multiple Choice' },
    { value: 'multiple_select', label: 'Multiple Select' },
    { value: 'short_answer', label: 'Short Answer' },
    { value: 'long_answer', label: 'Long Answer' },
    { value: 'true_false', label: 'True/False' }
  ]

  const addAnswerOption = () => {
    const newId = (formData.answer_options.length + 1).toString()
    setFormData(prev => ({
      ...prev,
      answer_options: [...prev.answer_options, { id: newId, text: '', is_correct: false }]
    }))
  }

  const removeAnswerOption = (optionId: string) => {
    setFormData(prev => ({
      ...prev,
      answer_options: prev.answer_options.filter(option => option.id !== optionId)
    }))
  }

  const updateAnswerOption = (optionId: string, field: keyof AnswerOption, value: any) => {
    setFormData(prev => ({
      ...prev,
      answer_options: prev.answer_options.map(option =>
        option.id === optionId ? { ...option, [field]: value } : option
      )
    }))
  }

  const setCorrectAnswer = (optionId: string) => {
    if (formData.question_type === 'multiple_choice' || formData.question_type === 'true_false') {
      // Single correct answer
      setFormData(prev => ({
        ...prev,
        answer_options: prev.answer_options.map(option => ({
          ...option,
          is_correct: option.id === optionId
        }))
      }))
    } else if (formData.question_type === 'multiple_select') {
      // Multiple correct answers
      updateAnswerOption(optionId, 'is_correct', !formData.answer_options.find(o => o.id === optionId)?.is_correct)
    }
  }

  const handleTypeChange = (newType: string) => {
    setFormData(prev => {
      let newAnswerOptions = prev.answer_options

      if (newType === 'true_false') {
        newAnswerOptions = [
          { id: '1', text: 'True', is_correct: false },
          { id: '2', text: 'False', is_correct: false }
        ]
      } else if (newType === 'short_answer' || newType === 'long_answer') {
        newAnswerOptions = []
      } else if (prev.question_type === 'true_false' && (newType === 'multiple_choice' || newType === 'multiple_select')) {
        newAnswerOptions = [
          { id: '1', text: '', is_correct: false },
          { id: '2', text: '', is_correct: false }
        ]
      }

      return {
        ...prev,
        question_type: newType,
        answer_options: newAnswerOptions
      }
    })
  }

  const handleSubmit = async () => {
    if (!formData.question_text.trim()) {
      toast.error('Question text is required')
      return
    }

    // Validate answer options for multiple choice questions
    if (['multiple_choice', 'multiple_select', 'true_false'].includes(formData.question_type)) {
      const hasCorrectAnswer = formData.answer_options.some(option => option.is_correct)
      if (!hasCorrectAnswer) {
        toast.error('Please select at least one correct answer')
        return
      }

      const hasEmptyOption = formData.answer_options.some(option => !option.text.trim())
      if (hasEmptyOption) {
        toast.error('All answer options must have text')
        return
      }
    }

    setLoading(true)

    try {
      const academyId = 'default-academy-id' // This should be from context

      // Prepare correct answers array
      let correctAnswers: string[] = []
      if (['multiple_choice', 'multiple_select', 'true_false'].includes(formData.question_type)) {
        correctAnswers = formData.answer_options
          .map((option, index) => option.is_correct ? index.toString() : null)
          .filter(Boolean) as string[]
      }

      // Prepare answer options
      let answerOptions: any = null
      if (['multiple_choice', 'multiple_select', 'true_false'].includes(formData.question_type)) {
        answerOptions = formData.answer_options.map(option => option.text.trim())
      }

      const questionData = {
        academy_id: academyId,
        exam_id: examId,
        question_text: formData.question_text.trim(),
        instructions: formData.instructions.trim() || undefined,
        question_type: formData.question_type as ExamQuestion['question_type'],
        points: parseInt(formData.points) || 1,
        correct_answers: correctAnswers.length > 0 ? correctAnswers : undefined,
        answer_options: answerOptions,
        explanation: formData.explanation.trim() || undefined,
        audio_start_seconds: formData.audio_start_seconds ? parseInt(formData.audio_start_seconds) : undefined,
        audio_end_seconds: formData.audio_end_seconds ? parseInt(formData.audio_end_seconds) : undefined
      }

      await createQuestion(questionData)

      toast.success('Question created successfully!')
      
      // Reset form
      setFormData({
        question_text: '',
        instructions: '',
        question_type: 'multiple_choice',
        points: '1',
        answer_options: [
          { id: '1', text: '', is_correct: false },
          { id: '2', text: '', is_correct: false }
        ],
        correct_answers: [],
        explanation: '',
        audio_start_seconds: '',
        audio_end_seconds: ''
      })
      
      setOpen(false)
      onSuccess()
    } catch (error) {
      console.error('Error creating question:', error)
      toast.error(error instanceof Error ? error.message : 'Failed to create question')
    } finally {
      setLoading(false)
    }
  }

  const requiresAnswerOptions = ['multiple_choice', 'multiple_select', 'true_false'].includes(formData.question_type)
  const allowsMultipleCorrect = formData.question_type === 'multiple_select'

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-gray-900 hover:bg-gray-800 text-white">
          <Plus className="h-4 w-4 mr-2" />
          Add Question
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[700px] bg-white max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-gray-900">Add New Question</DialogTitle>
          <DialogDescription className="text-gray-600">
            Create a new question for this exam with answer options and settings.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Basic Information */}
          <div>
            <Label htmlFor="points" className="text-gray-900">Points</Label>
            <Input
              id="points"
              type="number"
              value={formData.points}
              onChange={(e) => setFormData(prev => ({ ...prev, points: e.target.value }))}
              placeholder="1"
              className="mt-1 text-gray-900"
              min="1"
            />
          </div>

          <div>
            <Label htmlFor="question_text" className="text-gray-900">Question Text *</Label>
            <Textarea
              id="question_text"
              value={formData.question_text}
              onChange={(e) => setFormData(prev => ({ ...prev, question_text: e.target.value }))}
              placeholder="Enter your question here..."
              className="mt-1 text-gray-900"
              rows={3}
            />
          </div>

          <div>
            <Label htmlFor="instructions" className="text-gray-900">Instructions (Optional)</Label>
            <Textarea
              id="instructions"
              value={formData.instructions}
              onChange={(e) => setFormData(prev => ({ ...prev, instructions: e.target.value }))}
              placeholder="Additional instructions or context..."
              className="mt-1 text-gray-900"
              rows={2}
            />
          </div>

          {/* Question Type */}
          <div>
            <Label className="text-gray-900">Question Type</Label>
            <Select value={formData.question_type} onValueChange={handleTypeChange}>
              <SelectTrigger className="mt-1 text-gray-900">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-white">
                {questionTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value} className="text-gray-900">
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Answer Options (for multiple choice questions) */}
          {requiresAnswerOptions && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <Label className="text-gray-900">Answer Options</Label>
                {formData.question_type !== 'true_false' && (
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={addAnswerOption}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Add Option
                  </Button>
                )}
              </div>
              <div className="space-y-2">
                {formData.answer_options.map((option, index) => (
                  <div key={option.id} className="flex items-center gap-2">
                    <Button
                      type="button"
                      variant={option.is_correct ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCorrectAnswer(option.id)}
                      className={`min-w-[2rem] ${
                        option.is_correct 
                          ? 'bg-green-600 hover:bg-green-700' 
                          : 'border-gray-300'
                      }`}
                    >
                      {option.is_correct ? <Check className="h-4 w-4" /> : String.fromCharCode(65 + index)}
                    </Button>
                    <Input
                      value={option.text}
                      onChange={(e) => updateAnswerOption(option.id, 'text', e.target.value)}
                      placeholder={`Option ${String.fromCharCode(65 + index)}`}
                      className="flex-1 text-gray-900"
                      readOnly={formData.question_type === 'true_false'}
                    />
                    {formData.question_type !== 'true_false' && formData.answer_options.length > 2 && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => removeAnswerOption(option.id)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
              <p className="text-sm text-gray-600 mt-2">
                {allowsMultipleCorrect 
                  ? 'Click the buttons to mark correct answers (multiple allowed)'
                  : 'Click the button to mark the correct answer'
                }
              </p>
            </div>
          )}

          {/* Answer Explanation */}
          <div>
            <Label htmlFor="explanation" className="text-gray-900">Answer Explanation (Optional)</Label>
            <Textarea
              id="explanation"
              value={formData.explanation}
              onChange={(e) => setFormData(prev => ({ ...prev, explanation: e.target.value }))}
              placeholder="Explain why this is the correct answer..."
              className="mt-1 text-gray-900"
              rows={2}
            />
          </div>

          {/* Audio Timing (Optional) */}
          <div>
            <Label className="text-gray-900">Audio Timing (Optional)</Label>
            <div className="grid grid-cols-2 gap-4 mt-2">
              <div>
                <Label htmlFor="audio_start" className="text-sm text-gray-600">Start Time (seconds)</Label>
                <Input
                  id="audio_start"
                  type="number"
                  value={formData.audio_start_seconds}
                  onChange={(e) => setFormData(prev => ({ ...prev, audio_start_seconds: e.target.value }))}
                  placeholder="0"
                  className="text-gray-900"
                  min="0"
                />
              </div>
              <div>
                <Label htmlFor="audio_end" className="text-sm text-gray-600">End Time (seconds)</Label>
                <Input
                  id="audio_end"
                  type="number"
                  value={formData.audio_end_seconds}
                  onChange={(e) => setFormData(prev => ({ ...prev, audio_end_seconds: e.target.value }))}
                  placeholder="60"
                  className="text-gray-900"
                  min="0"
                />
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-4 border-t border-gray-200">
            <Button
              onClick={handleSubmit}
              disabled={loading}
              className="bg-gray-900 hover:bg-gray-800 text-white"
            >
              {loading ? 'Creating...' : 'Create Question'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}