'use client'

import { useState, useEffect } from 'react'
import { X, Plus, Trash2, Save } from 'lucide-react'
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
import { Switch } from '@/components/ui/switch'

export interface Question {
  id?: string
  question_number: number
  question_text: string
  question_type: 'multiple_choice' | 'multiple_select' | 'short_answer' | 'long_answer' | 'true_false' | 'fill_blank'
  correct_answers?: string[] | null
  answer_options?: any | null
  points: number
  sort_order: number
  instructions?: string | null
  explanation?: string | null
}

interface QuestionEditorProps {
  question?: Question | null
  questionNumber?: number
  onSave: (question: Question) => void
  onCancel: () => void
}

export function QuestionEditor({ question, questionNumber, onSave, onCancel }: QuestionEditorProps) {
  const [formData, setFormData] = useState<Question>({
    question_number: question?.question_number || questionNumber || 1,
    question_text: question?.question_text || '',
    question_type: question?.question_type || 'multiple_choice',
    correct_answers: question?.correct_answers || [],
    answer_options: question?.answer_options || null,
    points: question?.points || 1,
    sort_order: question?.sort_order || question?.question_number || questionNumber || 1,
    instructions: question?.instructions || '',
    explanation: question?.explanation || ''
  })

  // Answer options for multiple choice
  const [mcOptions, setMcOptions] = useState<{ key: string; text: string; is_correct: boolean }[]>([
    { key: 'A', text: '', is_correct: false },
    { key: 'B', text: '', is_correct: false },
    { key: 'C', text: '', is_correct: false },
    { key: 'D', text: '', is_correct: false }
  ])

  // For multiple select
  const [msOptions, setMsOptions] = useState<{ key: string; text: string; is_correct: boolean }[]>([
    { key: 'A', text: '', is_correct: false },
    { key: 'B', text: '', is_correct: false },
    { key: 'C', text: '', is_correct: false },
    { key: 'D', text: '', is_correct: false }
  ])

  // For short answer (multiple acceptable answers)
  const [acceptableAnswers, setAcceptableAnswers] = useState<string[]>([''])

  // Initialize from existing question
  useEffect(() => {
    if (question) {
      setFormData(question)
      
      // Parse answer options based on type
      if (question.question_type === 'multiple_choice' && question.answer_options) {
        const options = question.answer_options.options || []
        setMcOptions(options.map((opt: any, idx: number) => ({
          key: String.fromCharCode(65 + idx),
          text: opt.text || '',
          is_correct: question.correct_answers?.includes(String.fromCharCode(65 + idx)) || false
        })))
      } else if (question.question_type === 'multiple_select' && question.answer_options) {
        const options = question.answer_options.options || []
        setMsOptions(options.map((opt: any, idx: number) => ({
          key: String.fromCharCode(65 + idx),
          text: opt.text || '',
          is_correct: question.correct_answers?.includes(String.fromCharCode(65 + idx)) || false
        })))
      } else if (question.question_type === 'short_answer' && question.correct_answers) {
        setAcceptableAnswers(question.correct_answers.length > 0 ? question.correct_answers : [''])
      }
    }
  }, [question])

  const handleSave = () => {
    // Prepare data based on question type
    let finalData = { ...formData }
    
    if (formData.question_type === 'multiple_choice') {
      // Store answer options and correct answer
      const validOptions = mcOptions.filter(opt => opt.text.trim())
      finalData.answer_options = {
        options: validOptions.map(opt => ({ key: opt.key, text: opt.text }))
      }
      finalData.correct_answers = mcOptions.filter(opt => opt.is_correct).map(opt => opt.key)
    } else if (formData.question_type === 'multiple_select') {
      // Store answer options and correct answers (multiple)
      const validOptions = msOptions.filter(opt => opt.text.trim())
      finalData.answer_options = {
        options: validOptions.map(opt => ({ key: opt.key, text: opt.text }))
      }
      finalData.correct_answers = msOptions.filter(opt => opt.is_correct).map(opt => opt.key)
    } else if (formData.question_type === 'true_false') {
      // Store true/false answer
      finalData.answer_options = { options: [{ key: 'T', text: 'True' }, { key: 'F', text: 'False' }] }
    } else if (formData.question_type === 'short_answer') {
      // Store acceptable answers
      finalData.correct_answers = acceptableAnswers.filter(ans => ans.trim())
    } else if (formData.question_type === 'long_answer') {
      // Long answer - no automatic grading
      finalData.correct_answers = null
      finalData.answer_options = null
    } else if (formData.question_type === 'fill_blank') {
      // Fill in the blank - exact match answers
      finalData.correct_answers = acceptableAnswers.filter(ans => ans.trim())
    }

    // Include existing ID if editing
    if (question?.id) {
      finalData.id = question.id
    }

    onSave(finalData)
  }

  const addMCOption = () => {
    const nextKey = String.fromCharCode(65 + mcOptions.length)
    setMcOptions([...mcOptions, { key: nextKey, text: '', is_correct: false }])
  }

  const removeMCOption = (index: number) => {
    if (mcOptions.length > 2) {
      setMcOptions(mcOptions.filter((_, i) => i !== index))
    }
  }

  const addMSOption = () => {
    const nextKey = String.fromCharCode(65 + msOptions.length)
    setMsOptions([...msOptions, { key: nextKey, text: '', is_correct: false }])
  }

  const removeMSOption = (index: number) => {
    if (msOptions.length > 2) {
      setMsOptions(msOptions.filter((_, i) => i !== index))
    }
  }

  const addAcceptableAnswer = () => {
    setAcceptableAnswers([...acceptableAnswers, ''])
  }

  const removeAcceptableAnswer = (index: number) => {
    if (acceptableAnswers.length > 1) {
      setAcceptableAnswers(acceptableAnswers.filter((_, i) => i !== index))
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          {question ? `Edit Question ${formData.question_number}` : `Add Question ${questionNumber}`}
        </h3>
        <Button variant="ghost" size="icon" onClick={onCancel}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      <div className="space-y-6">
        {/* Question Number and Points */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="question_number" className="text-gray-900">
              Question Number <span className="text-red-500">*</span>
            </Label>
            <Input
              id="question_number"
              type="number"
              min="1"
              value={formData.question_number}
              onChange={(e) => setFormData({ ...formData, question_number: parseInt(e.target.value), sort_order: parseInt(e.target.value) })}
              className="mt-1 text-gray-900"
            />
          </div>
          <div>
            <Label htmlFor="points" className="text-gray-900">
              Points
            </Label>
            <Input
              id="points"
              type="number"
              min="0"
              step="0.5"
              value={formData.points}
              onChange={(e) => setFormData({ ...formData, points: parseFloat(e.target.value) })}
              className="mt-1 text-gray-900"
            />
          </div>
        </div>

        {/* Question Type */}
        <div>
          <Label htmlFor="question_type" className="text-gray-900">
            Question Type <span className="text-red-500">*</span>
          </Label>
          <Select 
            value={formData.question_type} 
            onValueChange={(value: any) => setFormData({ ...formData, question_type: value })}
          >
            <SelectTrigger className="mt-1 text-gray-900">
              <SelectValue placeholder="Select question type" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              <SelectItem value="multiple_choice" className="text-gray-900">Multiple Choice</SelectItem>
              <SelectItem value="multiple_select" className="text-gray-900">Multiple Select (Checkbox)</SelectItem>
              <SelectItem value="true_false" className="text-gray-900">True/False</SelectItem>
              <SelectItem value="short_answer" className="text-gray-900">Short Answer</SelectItem>
              <SelectItem value="long_answer" className="text-gray-900">Long Answer (Essay)</SelectItem>
              <SelectItem value="fill_blank" className="text-gray-900">Fill in the Blank</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Question Text */}
        <div>
          <Label htmlFor="question_text" className="text-gray-900">
            Question Text <span className="text-red-500">*</span>
          </Label>
          <Textarea
            id="question_text"
            value={formData.question_text}
            onChange={(e) => setFormData({ ...formData, question_text: e.target.value })}
            placeholder="Enter the question as it appears in the PDF"
            className="mt-1 text-gray-900"
            rows={3}
          />
        </div>

        {/* Instructions (optional) */}
        <div>
          <Label htmlFor="instructions" className="text-gray-900">
            Instructions (Optional)
          </Label>
          <Textarea
            id="instructions"
            value={formData.instructions || ''}
            onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
            placeholder="Any special instructions for this question"
            className="mt-1 text-gray-900"
            rows={2}
          />
        </div>

        {/* Answer Configuration Based on Type */}
        <div className="border-t pt-4">
          <Label className="text-gray-900 font-medium mb-3 block">Answer Configuration</Label>
          
          {/* Multiple Choice */}
          {formData.question_type === 'multiple_choice' && (
            <div className="space-y-3">
              {mcOptions.map((option, index) => (
                <div key={index} className="flex items-center gap-3">
                  <span className="w-8 text-center font-medium text-gray-900">{option.key}.</span>
                  <Input
                    value={option.text}
                    onChange={(e) => {
                      const newOptions = [...mcOptions]
                      newOptions[index].text = e.target.value
                      setMcOptions(newOptions)
                    }}
                    placeholder={`Option ${option.key}`}
                    className="flex-1 text-gray-900"
                  />
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={option.is_correct}
                      onCheckedChange={(checked) => {
                        const newOptions = mcOptions.map((opt, i) => ({
                          ...opt,
                          is_correct: i === index ? checked : false // Only one correct for MC
                        }))
                        setMcOptions(newOptions)
                      }}
                    />
                    <span className="text-sm text-gray-600 w-16">Correct</span>
                  </div>
                  {mcOptions.length > 2 && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeMCOption(index)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  )}
                </div>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={addMCOption}
                className="mt-2"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Option
              </Button>
            </div>
          )}

          {/* Multiple Select */}
          {formData.question_type === 'multiple_select' && (
            <div className="space-y-3">
              {msOptions.map((option, index) => (
                <div key={index} className="flex items-center gap-3">
                  <span className="w-8 text-center font-medium text-gray-900">{option.key}.</span>
                  <Input
                    value={option.text}
                    onChange={(e) => {
                      const newOptions = [...msOptions]
                      newOptions[index].text = e.target.value
                      setMsOptions(newOptions)
                    }}
                    placeholder={`Option ${option.key}`}
                    className="flex-1 text-gray-900"
                  />
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={option.is_correct}
                      onCheckedChange={(checked) => {
                        const newOptions = [...msOptions]
                        newOptions[index].is_correct = checked // Multiple can be correct
                        setMsOptions(newOptions)
                      }}
                    />
                    <span className="text-sm text-gray-600 w-16">Correct</span>
                  </div>
                  {msOptions.length > 2 && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeMSOption(index)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  )}
                </div>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={addMSOption}
                className="mt-2"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Option
              </Button>
              <p className="text-sm text-gray-500 mt-2">Multiple options can be marked as correct</p>
            </div>
          )}

          {/* True/False */}
          {formData.question_type === 'true_false' && (
            <div className="space-y-3">
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="tf_answer"
                    checked={formData.correct_answers?.[0] === 'T'}
                    onChange={() => setFormData({ ...formData, correct_answers: ['T'] })}
                    className="text-gray-900"
                  />
                  <span className="text-gray-900">True</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="tf_answer"
                    checked={formData.correct_answers?.[0] === 'F'}
                    onChange={() => setFormData({ ...formData, correct_answers: ['F'] })}
                    className="text-gray-900"
                  />
                  <span className="text-gray-900">False</span>
                </label>
              </div>
            </div>
          )}

          {/* Short Answer / Fill in Blank */}
          {(formData.question_type === 'short_answer' || formData.question_type === 'fill_blank') && (
            <div className="space-y-3">
              <Label className="text-sm text-gray-600">Acceptable Answers (exact match)</Label>
              {acceptableAnswers.map((answer, index) => (
                <div key={index} className="flex items-center gap-3">
                  <Input
                    value={answer}
                    onChange={(e) => {
                      const newAnswers = [...acceptableAnswers]
                      newAnswers[index] = e.target.value
                      setAcceptableAnswers(newAnswers)
                    }}
                    placeholder="Enter acceptable answer"
                    className="flex-1 text-gray-900"
                  />
                  {acceptableAnswers.length > 1 && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeAcceptableAnswer(index)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  )}
                </div>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={addAcceptableAnswer}
                className="mt-2"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Acceptable Answer
              </Button>
              <p className="text-sm text-gray-500 mt-2">
                {formData.question_type === 'fill_blank' 
                  ? 'Enter exact text that should fill the blank'
                  : 'Enter all acceptable variations of the answer'}
              </p>
            </div>
          )}

          {/* Long Answer */}
          {formData.question_type === 'long_answer' && (
            <div className="space-y-3">
              <p className="text-sm text-gray-600">
                Long answer questions require manual grading. You can optionally add grading guidelines below.
              </p>
              <div>
                <Label htmlFor="explanation" className="text-gray-900">
                  Grading Guidelines / Model Answer
                </Label>
                <Textarea
                  id="explanation"
                  value={formData.explanation || ''}
                  onChange={(e) => setFormData({ ...formData, explanation: e.target.value })}
                  placeholder="Enter key points or model answer for grading reference"
                  className="mt-1 text-gray-900"
                  rows={4}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-3 mt-6 pt-6 border-t">
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button 
          onClick={handleSave}
          disabled={!formData.question_text || !formData.question_number}
          className="bg-gray-900 hover:bg-gray-800 text-white"
        >
          <Save className="h-4 w-4 mr-2" />
          {question ? 'Update Question' : 'Add Question'}
        </Button>
      </div>
    </div>
  )
}