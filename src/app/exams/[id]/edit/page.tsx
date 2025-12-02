'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { Loader2, ArrowLeft, Save, FileText, Settings, HelpCircle, File, Plus, Edit, Trash2, GripVertical } from 'lucide-react'
import { QuestionEditor, type Question } from '@/components/exams/QuestionEditor'
import { SplitScreenQuestionEditor } from '@/components/exams/SplitScreenQuestionEditor'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface Exam {
  id: string
  academy_id: string
  title: string
  description?: string | null
  exam_type_id?: string | null
  time_limit_minutes?: number | null
  attempts_allowed: number
  passing_score?: number | null
  total_questions: number
  total_points: number
  randomize_questions: boolean
  randomize_answers: boolean
  status: 'draft' | 'published' | 'archived'
  show_results: boolean
  allow_review: boolean
  require_webcam: boolean
  difficulty_level?: 'beginner' | 'intermediate' | 'advanced' | null
  subject_tags?: string[] | null
  learning_objectives?: string[] | null
  metadata?: any | null
  created_by?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  questions?: any[]
  files?: any[]
}

export default function EditExamPage() {
  const router = useRouter()
  const params = useParams()
  const examId = params.id as string
  
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [exam, setExam] = useState<Exam | null>(null)
  const [activeTab, setActiveTab] = useState('basic')
  const [questions, setQuestions] = useState<Question[]>([])
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null)
  const [showQuestionEditor, setShowQuestionEditor] = useState(false)
  const [showSplitScreenEditor, setShowSplitScreenEditor] = useState(false)
  const [examPdfUrl, setExamPdfUrl] = useState<string | null>(null)
  const [examPdfFileId, setExamPdfFileId] = useState<string | null>(null)
  const [autoOpenPdfEditor, setAutoOpenPdfEditor] = useState(false)
  const [initialQuestionIndex, setInitialQuestionIndex] = useState(0)
  
  // Check for tab parameter from URL
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search)
      const tabParam = urlParams.get('tab')
      if (tabParam && ['basic', 'files', 'questions', 'settings'].includes(tabParam)) {
        setActiveTab(tabParam)
        // Auto-open PDF editor if questions tab is selected
        if (tabParam === 'questions') {
          setAutoOpenPdfEditor(true)
        }
      }
    }
  }, [])
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    time_limit_minutes: 60,
    attempts_allowed: 1,
    passing_score: 70,
    status: 'draft' as 'draft' | 'published' | 'archived',
    difficulty_level: null as 'beginner' | 'intermediate' | 'advanced' | null,
    randomize_questions: false,
    randomize_answers: false,
    show_results: true,
    allow_review: true,
    require_webcam: false,
  })

  // Fetch questions
  const fetchQuestions = async () => {
    try {
      const response = await fetch(`/api/exams/${examId}/questions`)
      
      if (response.ok) {
        const data = await response.json()
        const fetchedQuestions = data.questions || []
        setQuestions(fetchedQuestions)
        
        // Auto-open PDF editor when questions are loaded if flag is set
        if (autoOpenPdfEditor && fetchedQuestions.length > 0 && examPdfUrl) {
          setShowSplitScreenEditor(true)
          setAutoOpenPdfEditor(false)
        }
      }
    } catch (error) {
      console.error('Error fetching questions:', error)
    }
  }

  // Fetch exam data
  useEffect(() => {
    const fetchExam = async () => {
      try {
        const response = await fetch(`/api/exams/${examId}`)
        if (!response.ok) {
          throw new Error('Failed to fetch exam')
        }
        const data = await response.json()
        setExam(data.exam)
        
        // Update form data with exam data
        setFormData({
          title: data.exam.title || '',
          description: data.exam.description || '',
          time_limit_minutes: data.exam.time_limit_minutes || 60,
          attempts_allowed: data.exam.attempts_allowed || 1,
          passing_score: data.exam.passing_score || 70,
          status: data.exam.status || 'draft',
          difficulty_level: data.exam.difficulty_level || null,
          randomize_questions: data.exam.randomize_questions || false,
          randomize_answers: data.exam.randomize_answers || false,
          show_results: data.exam.show_results ?? true,
          allow_review: data.exam.allow_review ?? true,
          require_webcam: data.exam.require_webcam || false,
        })
      } catch (error) {
        console.error('Error fetching exam:', error)
        alert('Failed to load exam data')
        router.push('/exams/list')
      } finally {
        setLoading(false)
      }
    }

    if (examId) {
      fetchExam()
      fetchQuestions()
      fetchExamPdf()
    }
  }, [examId, router])

  // Fetch exam PDF URL
  const fetchExamPdf = async () => {
    try {
      // Look for PDF file in exam files
      if (exam?.files) {
        const pdfFile = exam.files.find((file: any) => file.file_type === 'pdf')
        if (pdfFile) {
          setExamPdfUrl(pdfFile.file_path)
        }
      }
    } catch (error) {
      console.error('Error fetching exam PDF:', error)
    }
  }

  // Re-fetch PDF when exam data changes
  useEffect(() => {
    const loadPdfUrl = async () => {
      if (exam?.files) {
        const pdfFile = exam.files.find((file: any) => file.file_type === 'pdf')
        if (pdfFile) {
          try {
            // Capture the PDF file ID for configuration loading
            setExamPdfFileId(pdfFile.id)
            
            // Use API endpoint to get the best available URL
            const response = await fetch(`/api/files/url/${pdfFile.id}`)
            
            if (response.ok) {
              const result = await response.json()
              
              if (result.success && result.url) {
                setExamPdfUrl(result.url)
                
                // Auto-open PDF editor if flag is set and questions are loaded
                if (autoOpenPdfEditor && questions.length > 0) {
                  setShowSplitScreenEditor(true)
                  setAutoOpenPdfEditor(false)
                }
              } else {
                console.error('Failed to get PDF URL:', result.error)
                setExamPdfUrl(null)
                setExamPdfFileId(null)
              }
            } else {
              console.error('API request failed:', response.status)
              setExamPdfUrl(null)
              setExamPdfFileId(null)
            }
          } catch (error) {
            console.error('Error loading PDF URL:', error)
            setExamPdfUrl(null)
            setExamPdfFileId(null)
          }
        } else {
          setExamPdfUrl(null)
          setExamPdfFileId(null)
        }
      }
    }
    
    loadPdfUrl()
  }, [exam, autoOpenPdfEditor, questions])

  // Save basic info
  const handleSaveBasicInfo = async () => {
    setSaving(true)
    try {
      const response = await fetch(`/api/exams/${examId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: formData.title,
          description: formData.description || null,
          time_limit_minutes: formData.time_limit_minutes || null,
          attempts_allowed: formData.attempts_allowed,
          passing_score: formData.passing_score || null,
          status: formData.status,
          difficulty_level: formData.difficulty_level,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to update exam')
      }

      const data = await response.json()
      setExam(data.exam)
      
      console.log('Exam updated successfully')
    } catch (error) {
      console.error('Error saving exam:', error)
      alert('Failed to save changes')
    } finally {
      setSaving(false)
    }
  }

  // Question Management Functions
  const handleSaveQuestion = async (question: Question) => {
    try {
      const isEdit = !!question.id
      
      if (isEdit) {
        // Update existing question
        const response = await fetch(`/api/exams/${examId}/questions/${question.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(question)
        })
        
        if (response.ok) {
          await fetchQuestions()
          setEditingQuestion(null)
          setShowQuestionEditor(false)
          console.log('Question updated successfully')
        }
      } else {
        // Create new question
        const response = await fetch(`/api/exams/${examId}/questions`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(question)
        })
        
        if (response.ok) {
          await fetchQuestions()
          setShowQuestionEditor(false)
          console.log('Question created successfully')
          
          // Refresh exam to update totals
          const examResponse = await fetch(`/api/exams/${examId}`)
          if (examResponse.ok) {
            const data = await examResponse.json()
            setExam(data.exam)
          }
        }
      }
    } catch (error) {
      console.error('Error saving question:', error)
      alert('Failed to save question')
    }
  }

  const handleDeleteQuestion = async (questionId: string) => {
    if (!confirm('Are you sure you want to delete this question?')) {
      return
    }
    
    try {
      const response = await fetch(`/api/exams/${examId}/questions/${questionId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        await fetchQuestions()
        console.log('Question deleted successfully')
        
        // Refresh exam to update totals
        const examResponse = await fetch(`/api/exams/${examId}`)
        if (examResponse.ok) {
          const data = await examResponse.json()
          setExam(data.exam)
        }
      }
    } catch (error) {
      console.error('Error deleting question:', error)
      alert('Failed to delete question')
    }
  }

  const handleEditQuestion = (question: Question) => {
    // Open split screen editor and navigate to the specific question
    const questionIndex = questions.findIndex(q => q.id === question.id)
    setInitialQuestionIndex(questionIndex >= 0 ? questionIndex : 0)
    setShowSplitScreenEditor(true)
  }

  const handleAddQuestion = () => {
    setEditingQuestion(null)
    setShowQuestionEditor(true)
  }

  const handleOpenSplitScreenEditor = () => {
    setInitialQuestionIndex(0)
    setShowSplitScreenEditor(true)
  }

  const handleCloseSplitScreenEditor = () => {
    setShowSplitScreenEditor(false)
    fetchQuestions() // Refresh questions after editing
  }

  const getQuestionTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'multiple_choice': 'Multiple Choice',
      'multiple_select': 'Multiple Select',
      'true_false': 'True/False',
      'short_answer': 'Short Answer',
      'long_answer': 'Long Answer',
      'fill_blank': 'Fill in Blank'
    }
    return labels[type] || type
  }

  const isQuestionConfigured = (question: Question) => {
    // A question is considered configured if:
    // 1. Has custom question text (not the placeholder)
    // 2. Has correct answers defined (for types that need them)
    const hasCustomText = !question.question_text.includes('(configure this question)')
    
    if (question.question_type === 'long_answer') {
      // Long answer just needs custom text
      return hasCustomText
    } else {
      // Other types need both custom text AND correct answers
      return hasCustomText && question.correct_answers && question.correct_answers.length > 0
    }
  }

  // Save settings
  const handleSaveSettings = async () => {
    setSaving(true)
    try {
      const response = await fetch(`/api/exams/${examId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          randomize_questions: formData.randomize_questions,
          randomize_answers: formData.randomize_answers,
          show_results: formData.show_results,
          allow_review: formData.allow_review,
          require_webcam: formData.require_webcam,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to update exam settings')
      }

      const data = await response.json()
      setExam(data.exam)
      
      console.log('Settings updated successfully')
    } catch (error) {
      console.error('Error saving settings:', error)
      alert('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
      </div>
    )
  }

  if (!exam) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Exam not found</h3>
        <Link href="/exams/list">
          <Button className="mt-4">Back to Exams</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/exams/list">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Edit Exam</h1>
            <p className="text-sm text-gray-600 mt-1">
              ID: {examId} • Created: {new Date(exam.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`px-3 py-1 text-sm font-medium rounded-full ${
            exam.status === 'published' 
              ? 'bg-green-100 text-green-800' 
              : exam.status === 'archived'
              ? 'bg-gray-100 text-gray-600'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {exam.status.charAt(0).toUpperCase() + exam.status.slice(1)}
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 max-w-2xl">
          <TabsTrigger value="basic" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Basic Info
          </TabsTrigger>
          <TabsTrigger value="files" className="flex items-center gap-2">
            <File className="h-4 w-4" />
            Files
          </TabsTrigger>
          <TabsTrigger value="questions" className="flex items-center gap-2">
            <HelpCircle className="h-4 w-4" />
            Questions
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Settings
          </TabsTrigger>
        </TabsList>

        {/* Basic Info Tab */}
        <TabsContent value="basic" className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="title" className="text-gray-900">
                  Exam Title <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Enter exam title"
                  className="mt-1 text-gray-900"
                />
              </div>

              <div>
                <Label htmlFor="description" className="text-gray-900">
                  Description
                </Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Enter exam description (optional)"
                  className="mt-1 text-gray-900"
                  rows={4}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="time_limit" className="text-gray-900">
                    Time Limit (minutes)
                  </Label>
                  <Input
                    id="time_limit"
                    type="number"
                    value={formData.time_limit_minutes}
                    onChange={(e) => setFormData({ ...formData, time_limit_minutes: parseInt(e.target.value) })}
                    placeholder="60"
                    className="mt-1 text-gray-900"
                  />
                </div>

                <div>
                  <Label htmlFor="attempts" className="text-gray-900">
                    Attempts Allowed
                  </Label>
                  <Input
                    id="attempts"
                    type="number"
                    value={formData.attempts_allowed}
                    onChange={(e) => setFormData({ ...formData, attempts_allowed: parseInt(e.target.value) })}
                    min="1"
                    placeholder="1"
                    className="mt-1 text-gray-900"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="passing_score" className="text-gray-900">
                    Passing Score (%)
                  </Label>
                  <Input
                    id="passing_score"
                    type="number"
                    value={formData.passing_score}
                    onChange={(e) => setFormData({ ...formData, passing_score: parseInt(e.target.value) })}
                    min="0"
                    max="100"
                    placeholder="70"
                    className="mt-1 text-gray-900"
                  />
                </div>

                <div>
                  <Label htmlFor="difficulty" className="text-gray-900">
                    Difficulty Level
                  </Label>
                  <Select 
                    value={formData.difficulty_level || 'none'} 
                    onValueChange={(value) => setFormData({ ...formData, difficulty_level: value === 'none' ? null : value as any })}
                  >
                    <SelectTrigger className="mt-1 text-gray-900">
                      <SelectValue placeholder="Select difficulty" />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      <SelectItem value="none" className="text-gray-900">Not Set</SelectItem>
                      <SelectItem value="beginner" className="text-gray-900">Beginner</SelectItem>
                      <SelectItem value="intermediate" className="text-gray-900">Intermediate</SelectItem>
                      <SelectItem value="advanced" className="text-gray-900">Advanced</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="status" className="text-gray-900">
                  Exam Status
                </Label>
                <Select 
                  value={formData.status} 
                  onValueChange={(value) => setFormData({ ...formData, status: value as any })}
                >
                  <SelectTrigger className="mt-1 text-gray-900">
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent className="bg-white">
                    <SelectItem value="draft" className="text-gray-900">Draft</SelectItem>
                    <SelectItem value="published" className="text-gray-900">Published</SelectItem>
                    <SelectItem value="archived" className="text-gray-900">Archived</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <Button 
                onClick={handleSaveBasicInfo}
                disabled={saving || !formData.title}
                className="bg-gray-900 hover:bg-gray-800 text-white"
              >
                {saving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </>
                )}
              </Button>
            </div>
          </div>
        </TabsContent>

        {/* Files Tab */}
        <TabsContent value="files" className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Exam Files</h2>
            
            {exam.files && exam.files.length > 0 ? (
              <div className="space-y-4">
                {exam.files.map((file: any) => (
                  <div key={file.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gray-200 rounded flex items-center justify-center">
                        {file.file_type === 'pdf' ? (
                          <FileText className="h-5 w-5 text-gray-600" />
                        ) : file.file_type === 'audio' ? (
                          <svg className="h-5 w-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                          </svg>
                        ) : (
                          <File className="h-5 w-5 text-gray-600" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{file.original_filename}</p>
                        <p className="text-sm text-gray-500">
                          {file.file_type.toUpperCase()} • {(file.file_size_bytes / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Uploaded: {new Date(file.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <File className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p>No files uploaded for this exam</p>
                <p className="text-sm mt-2">Files can be added when creating the exam</p>
              </div>
            )}
          </div>
        </TabsContent>

        {/* Questions Tab */}
        <TabsContent value="questions" className="space-y-6">
          {!showQuestionEditor && !showSplitScreenEditor ? (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">Exam Questions</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Configure questions and answers for this exam
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">
                    Total Questions: <span className="font-semibold text-gray-900">{exam.total_questions}</span>
                  </span>
                  <span className="text-sm text-gray-600">
                    Total Points: <span className="font-semibold text-gray-900">{exam.total_points}</span>
                  </span>
                  {questions.length > 0 && (
                    <span className={`text-sm px-2 py-1 rounded-full ${
                      questions.filter(q => isQuestionConfigured(q)).length === questions.length
                        ? 'bg-green-100 text-green-700'
                        : 'bg-orange-100 text-orange-700'
                    }`}>
                      {questions.filter(q => isQuestionConfigured(q)).length} of {questions.length} configured
                    </span>
                  )}
                  <Button 
                    onClick={handleOpenSplitScreenEditor}
                    className="bg-gray-900 hover:bg-gray-800 text-white"
                    disabled={questions.length === 0}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Configure with PDF
                  </Button>
                </div>
              </div>
              
              {questions.length > 0 ? (
                <div className="space-y-3">
                  {questions.map((question) => {
                    const isConfigured = isQuestionConfigured(question)
                    return (
                      <div 
                        key={question.id} 
                        className={`border rounded-lg p-4 transition-colors ${
                          isConfigured 
                            ? 'border-green-200 bg-green-50 hover:bg-green-100' 
                            : 'border-orange-200 bg-orange-50 hover:bg-orange-100'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-4 mb-2">
                              <span className="font-semibold text-gray-900">
                                Question {question.question_number}
                              </span>
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                isConfigured 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-orange-100 text-orange-800'
                              }`}>
                                {isConfigured ? '✓ Configured' : '⚠ Needs Setup'}
                              </span>
                              <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                                {getQuestionTypeLabel(question.question_type)}
                              </span>
                              <span className="text-sm text-gray-600">
                                {question.points} {question.points === 1 ? 'point' : 'points'}
                              </span>
                            </div>
                            <p className={`mb-2 ${
                              isConfigured ? 'text-gray-700' : 'text-orange-700 italic'
                            }`}>
                              {question.question_text}
                            </p>
                            {question.correct_answers && question.correct_answers.length > 0 && (
                              <div className="text-sm text-gray-600">
                                <span className="font-medium">Answer: </span>
                                {question.question_type === 'true_false' ? (
                                  question.correct_answers[0] === 'T' ? 'True' : 'False'
                                ) : question.question_type === 'multiple_choice' || question.question_type === 'multiple_select' ? (
                                  `Option(s) ${question.correct_answers.join(', ')}`
                                ) : (
                                  question.correct_answers.join(', ')
                                )}
                              </div>
                            )}
                            {!isConfigured && (
                              <p className="text-sm text-orange-600 mt-1">
                                Click "Configure with PDF" above to set up this question
                              </p>
                            )}
                          </div>
                          <div className="flex items-center gap-2 ml-4">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleEditQuestion(question)}
                              className={!isConfigured ? 'border border-orange-300' : ''}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDeleteQuestion(question.id!)}
                            >
                              <Trash2 className="h-4 w-4 text-red-500" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                  <HelpCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Questions Yet</h3>
                  <p className="text-sm text-gray-600 mb-6 max-w-md mx-auto">
                    Questions are automatically created when you upload an exam PDF. 
                    Go to the "Files" tab to upload your exam document first.
                  </p>
                  <Button 
                    onClick={() => setActiveTab('files')}
                    className="bg-gray-900 hover:bg-gray-800 text-white"
                  >
                    Go to Files Tab
                  </Button>
                </div>
              )}
            </div>
          ) : showQuestionEditor ? (
            <QuestionEditor
              question={editingQuestion}
              questionNumber={questions.length + 1}
              onSave={handleSaveQuestion}
              onCancel={() => {
                setEditingQuestion(null)
                setShowQuestionEditor(false)
              }}
            />
          ) : null}
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Exam Settings</h2>
            
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="randomize_questions" className="text-gray-900 font-medium">
                    Randomize Question Order
                  </Label>
                  <p className="text-sm text-gray-600 mt-1">
                    Questions will appear in random order for each student
                  </p>
                </div>
                <Switch
                  id="randomize_questions"
                  checked={formData.randomize_questions}
                  onCheckedChange={(checked) => setFormData({ ...formData, randomize_questions: checked })}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="randomize_answers" className="text-gray-900 font-medium">
                    Randomize Answer Order
                  </Label>
                  <p className="text-sm text-gray-600 mt-1">
                    Multiple choice answers will appear in random order
                  </p>
                </div>
                <Switch
                  id="randomize_answers"
                  checked={formData.randomize_answers}
                  onCheckedChange={(checked) => setFormData({ ...formData, randomize_answers: checked })}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="show_results" className="text-gray-900 font-medium">
                    Show Results After Submission
                  </Label>
                  <p className="text-sm text-gray-600 mt-1">
                    Students can see their scores immediately after completing the exam
                  </p>
                </div>
                <Switch
                  id="show_results"
                  checked={formData.show_results}
                  onCheckedChange={(checked) => setFormData({ ...formData, show_results: checked })}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="allow_review" className="text-gray-900 font-medium">
                    Allow Answer Review
                  </Label>
                  <p className="text-sm text-gray-600 mt-1">
                    Students can review their answers after submission
                  </p>
                </div>
                <Switch
                  id="allow_review"
                  checked={formData.allow_review}
                  onCheckedChange={(checked) => setFormData({ ...formData, allow_review: checked })}
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="require_webcam" className="text-gray-900 font-medium">
                    Require Webcam
                  </Label>
                  <p className="text-sm text-gray-600 mt-1">
                    Students must enable webcam monitoring during the exam
                  </p>
                </div>
                <Switch
                  id="require_webcam"
                  checked={formData.require_webcam}
                  onCheckedChange={(checked) => setFormData({ ...formData, require_webcam: checked })}
                />
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <Button 
                onClick={handleSaveSettings}
                disabled={saving}
                className="bg-gray-900 hover:bg-gray-800 text-white"
              >
                {saving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Settings
                  </>
                )}
              </Button>
            </div>
          </div>
        </TabsContent>
      </Tabs>

      {/* Split Screen Question Editor - Rendered as overlay */}
      {showSplitScreenEditor && questions.length > 0 && (
        <div className="fixed inset-0 z-50">
          <SplitScreenQuestionEditor
            questions={questions}
            examId={examId}
            pdfUrl={examPdfUrl}
            pdfFileId={examPdfFileId}
            initialQuestionIndex={initialQuestionIndex}
            onSave={handleSaveQuestion}
            onClose={handleCloseSplitScreenEditor}
          />
        </div>
      )}
    </div>
  )
}