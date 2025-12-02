'use client'

import { useState, useEffect } from 'react'
import { ArrowLeft, ArrowRight, Save, RotateCw, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react'
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

interface SplitScreenQuestionEditorProps {
  questions: Question[]
  examId: string
  pdfUrl?: string | null
  pdfFileId?: string | null
  initialQuestionIndex?: number
  onSave: (question: Question) => void
  onClose: () => void
}

export function SplitScreenQuestionEditor({
  questions,
  examId,
  pdfUrl,
  pdfFileId,
  initialQuestionIndex = 0,
  onSave,
  onClose
}: SplitScreenQuestionEditorProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(initialQuestionIndex)
  const [saving, setSaving] = useState(false)
  
  // PDF configuration state
  const [pdfConfig, setPdfConfig] = useState({
    rotation_degrees: 0,
    zoom_level: 1.0,
    is_split_enabled: false,
    split_orientation: 'vertical' as 'vertical' | 'horizontal',
    split_page_1_position: 'left' as 'left' | 'right' | 'top' | 'bottom',
    split_page_2_position: 'right' as 'left' | 'right' | 'top' | 'bottom'
  })
  
  // Legacy compatibility
  const pdfZoom = pdfConfig.zoom_level
  const pdfRotation = pdfConfig.rotation_degrees
  
  // Question form state
  const [formData, setFormData] = useState<Question | null>(null)
  
  // Answer options for different question types
  const [mcOptions, setMcOptions] = useState<{ key: string; text: string; is_correct: boolean }[]>([])
  const [msOptions, setMsOptions] = useState<{ key: string; text: string; is_correct: boolean }[]>([])
  const [acceptableAnswers, setAcceptableAnswers] = useState<string[]>([''])

  const currentQuestion = questions[currentQuestionIndex]

  // Load PDF configuration if file ID is available
  useEffect(() => {
    const loadPDFConfiguration = async () => {
      if (!pdfFileId) return

      try {
        const response = await fetch(`/api/files/config/${pdfFileId}`)
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            setPdfConfig(data.configuration)
          }
        }
      } catch (error) {
        console.error('Error loading PDF configuration:', error)
        // Use defaults if loading fails
      }
    }

    loadPDFConfiguration()
  }, [pdfFileId])

  // Initialize form data when question changes
  useEffect(() => {
    if (currentQuestion) {
      setFormData({ ...currentQuestion })
      
      // Initialize answer options based on question type
      if (currentQuestion.question_type === 'multiple_choice') {
        if (currentQuestion.answer_options?.options) {
          setMcOptions(currentQuestion.answer_options.options.map((opt: any, idx: number) => ({
            key: String.fromCharCode(65 + idx),
            text: opt.text || '',
            is_correct: currentQuestion.correct_answers?.includes(String.fromCharCode(65 + idx)) || false
          })))
        } else {
          setMcOptions([
            { key: 'A', text: '', is_correct: false },
            { key: 'B', text: '', is_correct: false },
            { key: 'C', text: '', is_correct: false },
            { key: 'D', text: '', is_correct: false }
          ])
        }
      } else if (currentQuestion.question_type === 'multiple_select') {
        if (currentQuestion.answer_options?.options) {
          setMsOptions(currentQuestion.answer_options.options.map((opt: any, idx: number) => ({
            key: String.fromCharCode(65 + idx),
            text: opt.text || '',
            is_correct: currentQuestion.correct_answers?.includes(String.fromCharCode(65 + idx)) || false
          })))
        } else {
          setMsOptions([
            { key: 'A', text: '', is_correct: false },
            { key: 'B', text: '', is_correct: false },
            { key: 'C', text: '', is_correct: false },
            { key: 'D', text: '', is_correct: false }
          ])
        }
      } else if (currentQuestion.question_type === 'short_answer' || currentQuestion.question_type === 'fill_blank') {
        setAcceptableAnswers(currentQuestion.correct_answers?.length ? currentQuestion.correct_answers : [''])
      }
    }
  }, [currentQuestionIndex, currentQuestion])

  const handleSave = async () => {
    if (!formData) return

    setSaving(true)
    try {
      let finalData = { ...formData }
      
      // Prepare data based on question type
      if (formData.question_type === 'multiple_choice') {
        const validOptions = mcOptions.filter(opt => opt.text.trim())
        finalData.answer_options = {
          options: validOptions.map(opt => ({ key: opt.key, text: opt.text }))
        }
        finalData.correct_answers = mcOptions.filter(opt => opt.is_correct).map(opt => opt.key)
      } else if (formData.question_type === 'multiple_select') {
        const validOptions = msOptions.filter(opt => opt.text.trim())
        finalData.answer_options = {
          options: validOptions.map(opt => ({ key: opt.key, text: opt.text }))
        }
        finalData.correct_answers = msOptions.filter(opt => opt.is_correct).map(opt => opt.key)
      } else if (formData.question_type === 'true_false') {
        finalData.answer_options = { options: [{ key: 'T', text: 'True' }, { key: 'F', text: 'False' }] }
      } else if (formData.question_type === 'short_answer' || formData.question_type === 'fill_blank') {
        finalData.correct_answers = acceptableAnswers.filter(ans => ans.trim())
      } else if (formData.question_type === 'long_answer') {
        finalData.correct_answers = null
        finalData.answer_options = null
      }

      await onSave(finalData)
      
      // Move to next question or show completion
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1)
      }
    } catch (error) {
      console.error('Error saving question:', error)
    } finally {
      setSaving(false)
    }
  }

  const isQuestionConfigured = (question: Question) => {
    const hasCustomText = !question.question_text.includes('(configure this question)')
    
    if (question.question_type === 'long_answer') {
      return hasCustomText
    } else {
      return hasCustomText && question.correct_answers && question.correct_answers.length > 0
    }
  }

  const goToPreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1)
    }
  }

  const goToNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    }
  }

  const goToQuestion = (index: number) => {
    setCurrentQuestionIndex(index)
  }

  // PDF controls are now read-only, configuration is set in Create Exam page

  if (!formData) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-gray-500">Loading question data...</div>
      </div>
    )
  }

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={onClose}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Configure Questions
              </h2>
              <p className="text-sm text-gray-600">
                Question {currentQuestionIndex + 1} of {questions.length}
              </p>
            </div>
          </div>
          
          {/* Question Navigation */}
          <div className="flex items-center gap-2">
            {questions.map((question, index) => (
              <button
                key={index}
                onClick={() => goToQuestion(index)}
                className={`w-8 h-8 rounded-full text-xs font-medium border transition-colors ${
                  index === currentQuestionIndex
                    ? 'bg-gray-900 text-white border-gray-900'
                    : isQuestionConfigured(question)
                    ? 'bg-green-100 text-green-800 border-green-300 hover:bg-green-200'
                    : 'bg-orange-100 text-orange-800 border-orange-300 hover:bg-orange-200'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Split Screen Content */}
      <div className="flex-1 flex">
        {/* Left Panel - PDF Viewer */}
        <div className="w-1/2 bg-white border-r border-gray-200 flex flex-col">
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Exam PDF</h3>
            
            {pdfUrl && (
              <div className="flex items-center gap-4">
                {/* PDF Configuration Status */}
                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <span>Zoom: {Math.round(pdfZoom * 100)}%</span>
                  <span>•</span>
                  <span>Rotation: {pdfRotation}°</span>
                  {pdfConfig.is_split_enabled && (
                    <>
                      <span>•</span>
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        Split: {pdfConfig.split_orientation}
                      </span>
                    </>
                  )}
                </div>
                <div className="text-xs text-gray-500">
                  (Configure in Create Exam page)
                </div>
              </div>
            )}
          </div>
          
          <div className="flex-1 p-4 overflow-hidden">
            {pdfUrl ? (
              <div className="h-full relative">
                {pdfConfig.is_split_enabled ? (
                  // Split view - show both pages side by side
                  <div className={`grid ${pdfConfig.split_orientation === 'vertical' ? 'grid-cols-2' : 'grid-rows-2'} h-full gap-2`}>
                    {/* Page 1 */}
                    <div className="relative bg-white rounded border">
                      <div className="absolute top-2 left-2 z-10 bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                        Page 1
                      </div>
                      <div className="w-full h-full overflow-hidden">
                        <iframe
                          src={`${pdfUrl}#toolbar=0&navpanes=0&scrollbar=0&view=FitH&pagemode=none`}
                          className="w-full h-full border-0"
                          style={{
                            transform: `scale(${pdfZoom}) rotate(${pdfRotation}deg)`,
                            transformOrigin: 'top left',
                            clipPath: pdfConfig.split_page_1_position === 'left' 
                              ? 'inset(0 50% 0 0)' 
                              : pdfConfig.split_page_1_position === 'right'
                              ? 'inset(0 0 0 50%)'
                              : pdfConfig.split_page_1_position === 'top'
                              ? 'inset(0 0 50% 0)'
                              : 'inset(50% 0 0 0)',
                            width: pdfZoom !== 1 ? `${100 / pdfZoom}%` : '100%',
                            height: pdfZoom !== 1 ? `${100 / pdfZoom}%` : '100%',
                            transition: 'transform 0.2s ease'
                          }}
                          title="Exam PDF - Page 1"
                        />
                      </div>
                    </div>

                    {/* Page 2 */}
                    <div className="relative bg-white rounded border">
                      <div className="absolute top-2 left-2 z-10 bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                        Page 2
                      </div>
                      <div className="w-full h-full overflow-hidden">
                        <iframe
                          src={`${pdfUrl}#toolbar=0&navpanes=0&scrollbar=0&view=FitH&pagemode=none`}
                          className="w-full h-full border-0"
                          style={{
                            transform: `scale(${pdfZoom}) rotate(${pdfRotation}deg)`,
                            transformOrigin: 'top left',
                            clipPath: pdfConfig.split_page_2_position === 'left' 
                              ? 'inset(0 50% 0 0)' 
                              : pdfConfig.split_page_2_position === 'right'
                              ? 'inset(0 0 0 50%)'
                              : pdfConfig.split_page_2_position === 'top'
                              ? 'inset(0 0 50% 0)'
                              : 'inset(50% 0 0 0)',
                            width: pdfZoom !== 1 ? `${100 / pdfZoom}%` : '100%',
                            height: pdfZoom !== 1 ? `${100 / pdfZoom}%` : '100%',
                            transition: 'transform 0.2s ease'
                          }}
                          title="Exam PDF - Page 2"
                        />
                      </div>
                    </div>
                  </div>
                ) : (
                  // Normal view - single PDF
                  <iframe
                    src={`${pdfUrl}#toolbar=0&navpanes=0&scrollbar=0&view=FitH&pagemode=none`}
                    className="w-full h-full border border-gray-200 rounded-lg"
                    style={{
                      transform: `scale(${pdfZoom}) rotate(${pdfRotation}deg)`,
                      transformOrigin: 'top left',
                      width: pdfZoom !== 1 ? `${100 / pdfZoom}%` : '100%',
                      height: pdfZoom !== 1 ? `${100 / pdfZoom}%` : '100%',
                      transition: 'transform 0.2s ease'
                    }}
                    title="Exam PDF"
                  />
                )}
              </div>
            ) : (
              <div className="h-full border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <p>No PDF available</p>
                  <p className="text-sm">Upload an exam PDF to view it here</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Question Configuration */}
        <div className="w-1/2 bg-white flex flex-col">
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Question {formData.question_number} Configuration
            </h3>
            
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={goToPreviousQuestion}
                disabled={currentQuestionIndex === 0}
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Previous
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={goToNextQuestion}
                disabled={currentQuestionIndex === questions.length - 1}
              >
                Next
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </div>
          
          {/* Question Form */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Basic Question Info */}
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
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    question_number: parseInt(e.target.value), 
                    sort_order: parseInt(e.target.value) 
                  })}
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
                  <SelectItem value="multiple_select" className="text-gray-900">Multiple Select</SelectItem>
                  <SelectItem value="true_false" className="text-gray-900">True/False</SelectItem>
                  <SelectItem value="short_answer" className="text-gray-900">Short Answer</SelectItem>
                  <SelectItem value="long_answer" className="text-gray-900">Long Answer</SelectItem>
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
                placeholder="Type the question text from the PDF"
                className="mt-1 text-gray-900"
                rows={3}
              />
            </div>

            {/* Answer Configuration */}
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
                              is_correct: i === index ? checked : false
                            }))
                            setMcOptions(newOptions)
                          }}
                        />
                        <span className="text-sm text-gray-600">Correct</span>
                      </div>
                    </div>
                  ))}
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
                  <Label className="text-sm text-gray-600">Acceptable Answers</Label>
                  {acceptableAnswers.map((answer, index) => (
                    <Input
                      key={index}
                      value={answer}
                      onChange={(e) => {
                        const newAnswers = [...acceptableAnswers]
                        newAnswers[index] = e.target.value
                        setAcceptableAnswers(newAnswers)
                      }}
                      placeholder="Enter acceptable answer"
                      className="text-gray-900"
                    />
                  ))}
                </div>
              )}

              {/* Long Answer */}
              {formData.question_type === 'long_answer' && (
                <div className="space-y-3">
                  <p className="text-sm text-gray-600">
                    Long answer questions require manual grading.
                  </p>
                </div>
              )}
            </div>

            {/* Save Button */}
            <div className="pt-4 border-t">
              <Button 
                onClick={handleSave}
                disabled={saving || !formData.question_text || !formData.question_number}
                className="bg-gray-900 hover:bg-gray-800 text-white w-full"
              >
                {saving ? (
                  <>Saving...</>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Question {formData.question_number}
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}