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
  Upload, 
  FileText, 
  Image, 
  Music, 
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { toast } from 'sonner'
import { FilePreview } from './FilePreview'

interface ExamWizardProps {
  onSuccess: () => void
}

interface UploadedFile {
  id: string
  file: File
  type: 'pdf' | 'image' | 'audio'
  preview?: string
  rotation?: number
  zoom?: number
}

interface ExamFormData {
  // Basic Info
  title: string
  description: string
  subject_tags: string[]
  time_limit_minutes: string
  attempts_allowed: string
  passing_score: string
  
  // Settings
  show_results: boolean
  allow_review: boolean
  randomize_questions: boolean
  randomize_answers: boolean
  require_webcam: boolean
  is_active: boolean
  
  // Files
  files: UploadedFile[]
}

export function ExamWizard({ onSuccess }: ExamWizardProps) {
  const [open, setOpen] = useState(false)
  const [currentStep, setCurrentStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [previewFile, setPreviewFile] = useState<UploadedFile | null>(null)
  
  const [formData, setFormData] = useState<ExamFormData>({
    title: '',
    description: '',
    subject_tags: [],
    time_limit_minutes: '',
    attempts_allowed: '1',
    passing_score: '',
    show_results: true,
    allow_review: true,
    randomize_questions: false,
    randomize_answers: false,
    require_webcam: false,
    is_active: true,
    files: []
  })

  const steps = [
    { number: 1, title: 'Basic Information', description: 'Exam title, description, and basic settings' },
    { number: 2, title: 'Upload Files', description: 'Upload PDFs, images, and audio files' },
    { number: 3, title: 'Preview & Settings', description: 'Review files and configure final settings' },
    { number: 4, title: 'Complete', description: 'Finish creating the exam' }
  ]

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    const newFiles: UploadedFile[] = []

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const fileType = file.type

      let type: 'pdf' | 'image' | 'audio'
      if (fileType.startsWith('image/')) {
        type = 'image'
      } else if (fileType === 'application/pdf') {
        type = 'pdf'
      } else if (fileType.startsWith('audio/')) {
        type = 'audio'
      } else {
        toast.error(`Unsupported file type: ${file.name}`)
        continue
      }

      const uploadedFile: UploadedFile = {
        id: `${Date.now()}-${i}`,
        file,
        type,
        rotation: 0,
        zoom: 1
      }

      // Create preview for images
      if (type === 'image') {
        uploadedFile.preview = URL.createObjectURL(file)
      }

      newFiles.push(uploadedFile)
    }

    setFormData(prev => ({
      ...prev,
      files: [...prev.files, ...newFiles]
    }))

    // Reset file input
    event.target.value = ''
  }

  const removeFile = (fileId: string) => {
    setFormData(prev => ({
      ...prev,
      files: prev.files.filter(f => f.id !== fileId)
    }))
    
    if (previewFile?.id === fileId) {
      setPreviewFile(null)
    }
  }

  const updateFileProperty = (fileId: string, property: keyof UploadedFile, value: any) => {
    setFormData(prev => ({
      ...prev,
      files: prev.files.map(f => 
        f.id === fileId ? { ...f, [property]: value } : f
      )
    }))
    
    if (previewFile?.id === fileId) {
      setPreviewFile(prev => prev ? { ...prev, [property]: value } : null)
    }
  }

  const addSubjectTag = (tag: string) => {
    if (!tag.trim()) return
    if (!formData.subject_tags.includes(tag.trim())) {
      setFormData(prev => ({
        ...prev,
        subject_tags: [...prev.subject_tags, tag.trim()]
      }))
    }
  }

  const removeSubjectTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      subject_tags: prev.subject_tags.filter(t => t !== tag)
    }))
  }

  const handleSubmit = async () => {
    if (!formData.title.trim()) {
      toast.error('Title is required')
      return
    }

    setLoading(true)

    try {
      // First create the exam
      const examResponse = await fetch('/api/exams', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: formData.title.trim(),
          description: formData.description.trim() || null,
          subject_tags: formData.subject_tags.length > 0 ? formData.subject_tags : null,
          time_limit_minutes: formData.time_limit_minutes ? parseInt(formData.time_limit_minutes) : null,
          attempts_allowed: parseInt(formData.attempts_allowed),
          passing_score: formData.passing_score ? parseFloat(formData.passing_score) : null,
          show_results: formData.show_results,
          allow_review: formData.allow_review,
          randomize_questions: formData.randomize_questions,
          randomize_answers: formData.randomize_answers,
          require_webcam: formData.require_webcam,
          is_active: formData.is_active
        }),
      })

      if (!examResponse.ok) {
        const errorData = await examResponse.json()
        throw new Error(errorData.message || 'Failed to create exam')
      }

      const { exam } = await examResponse.json()
      const examId = exam.id

      // Upload files if any
      if (formData.files.length > 0) {
        for (const uploadedFile of formData.files) {
          const formDataFile = new FormData()
          formDataFile.append('file', uploadedFile.file)
          formDataFile.append('fileType', uploadedFile.type)
          formDataFile.append('examId', examId)

          const fileResponse = await fetch('/api/exam-files/upload', {
            method: 'POST',
            body: formDataFile
          })

          if (!fileResponse.ok) {
            console.warn(`Failed to upload file: ${uploadedFile.file.name}`)
          }
        }
      }

      toast.success('Exam created successfully!')
      
      // Reset form and close dialog
      setFormData({
        title: '',
        description: '',
        subject_tags: [],
        time_limit_minutes: '',
        attempts_allowed: '1',
        passing_score: '',
        show_results: true,
        allow_review: true,
        randomize_questions: false,
        randomize_answers: false,
        require_webcam: false,
        is_active: true,
        files: []
      })
      
      setCurrentStep(1)
      setPreviewFile(null)
      setOpen(false)
      onSuccess()
    } catch (error) {
      console.error('Error creating exam:', error)
      toast.error(error instanceof Error ? error.message : 'Failed to create exam')
    } finally {
      setLoading(false)
    }
  }

  const nextStep = () => {
    if (currentStep < 4) {
      setCurrentStep(prev => prev + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const isStepValid = (step: number): boolean => {
    switch (step) {
      case 1:
        return formData.title.trim().length > 0
      case 2:
      case 3:
      case 4:
        return true
      default:
        return false
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-gray-900 hover:bg-gray-800 text-white">
          <Plus className="h-4 w-4 mr-2" />
          Create Exam
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[900px] bg-white max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-gray-900">Create New Exam</DialogTitle>
          <DialogDescription className="text-gray-600">
            Follow the steps to create a comprehensive exam with files and questions.
          </DialogDescription>
        </DialogHeader>

        {/* Step Indicator */}
        <div className="flex items-center justify-between mb-6">
          {steps.map((step, index) => (
            <div
              key={step.number}
              className={`flex items-center ${index < steps.length - 1 ? 'flex-1' : ''}`}
            >
              <div className={`
                flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium
                ${currentStep >= step.number 
                  ? 'bg-gray-900 text-white' 
                  : 'bg-gray-200 text-gray-600'
                }
              `}>
                {step.number}
              </div>
              <div className="ml-3 min-w-0">
                <p className={`text-sm font-medium ${
                  currentStep >= step.number ? 'text-gray-900' : 'text-gray-600'
                }`}>
                  {step.title}
                </p>
              </div>
              {index < steps.length - 1 && (
                <div className={`
                  flex-1 h-0.5 mx-4 
                  ${currentStep > step.number ? 'bg-gray-900' : 'bg-gray-200'}
                `} />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div className="space-y-6">
          {/* Step 1: Basic Information */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="title" className="text-gray-900">Exam Title *</Label>
                <Input
                  id="title"
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="e.g., Mid-term English Assessment"
                  className="mt-1 text-gray-900"
                />
              </div>

              <div>
                <Label htmlFor="description" className="text-gray-900">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Brief description of this exam..."
                  className="mt-1 text-gray-900"
                  rows={3}
                />
              </div>

              <div>
                <Label className="text-gray-900">Subject Tags</Label>
                <div className="mt-1 space-y-2">
                  <div className="flex flex-wrap gap-2 mb-2">
                    {formData.subject_tags.map((tag, index) => (
                      <Badge key={index} variant="secondary" className="bg-gray-100 text-gray-800">
                        {tag}
                        <button
                          type="button"
                          onClick={() => removeSubjectTag(tag)}
                          className="ml-1 text-gray-500 hover:text-gray-700"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                  <Input
                    placeholder="Type and press Enter to add tags..."
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        addSubjectTag(e.currentTarget.value)
                        e.currentTarget.value = ''
                      }
                    }}
                    className="text-gray-900"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="time_limit" className="text-gray-900">Time Limit (minutes)</Label>
                  <Input
                    id="time_limit"
                    type="number"
                    value={formData.time_limit_minutes}
                    onChange={(e) => setFormData(prev => ({ ...prev, time_limit_minutes: e.target.value }))}
                    placeholder="No limit"
                    className="mt-1 text-gray-900"
                    min="1"
                  />
                </div>

                <div>
                  <Label htmlFor="attempts" className="text-gray-900">Attempts Allowed</Label>
                  <Select 
                    value={formData.attempts_allowed} 
                    onValueChange={(value) => setFormData(prev => ({ ...prev, attempts_allowed: value }))}
                  >
                    <SelectTrigger className="mt-1 text-gray-900">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      <SelectItem value="1">1 attempt</SelectItem>
                      <SelectItem value="2">2 attempts</SelectItem>
                      <SelectItem value="3">3 attempts</SelectItem>
                      <SelectItem value="-1">Unlimited</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="passing_score" className="text-gray-900">Passing Score (%)</Label>
                  <Input
                    id="passing_score"
                    type="number"
                    value={formData.passing_score}
                    onChange={(e) => setFormData(prev => ({ ...prev, passing_score: e.target.value }))}
                    placeholder="70"
                    className="mt-1 text-gray-900"
                    min="0"
                    max="100"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Upload Files */}
          {currentStep === 2 && (
            <div className="space-y-6">
              {/* File Upload Area */}
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <input
                  type="file"
                  id="file-upload"
                  multiple
                  accept=".pdf,.jpg,.jpeg,.png,.gif,.mp3,.wav,.m4a"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-2 text-lg font-medium text-gray-900">Upload Files</p>
                  <p className="mt-1 text-sm text-gray-600">
                    Drag and drop files here, or click to browse
                  </p>
                  <p className="mt-1 text-xs text-gray-500">
                    Supports PDF, images (JPG, PNG), and audio files (MP3, WAV)
                  </p>
                </label>
              </div>

              {/* Uploaded Files List */}
              {formData.files.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-gray-900">Uploaded Files</h4>
                  <div className="space-y-2">
                    {formData.files.map((file) => (
                      <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          {file.type === 'pdf' && <FileText className="h-5 w-5 text-red-500" />}
                          {file.type === 'image' && <Image className="h-5 w-5 text-blue-500" />}
                          {file.type === 'audio' && <Music className="h-5 w-5 text-green-500" />}
                          
                          <div>
                            <p className="text-sm font-medium text-gray-900">{file.file.name}</p>
                            <p className="text-xs text-gray-500">
                              {(file.file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => setPreviewFile(file)}
                          >
                            Preview
                          </Button>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => removeFile(file.id)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* File Preview Modal */}
              {previewFile && (
                <div className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4">
                  <div className="w-full max-w-6xl max-h-[95vh]">
                    <FilePreview
                      file={previewFile.file}
                      fileType={previewFile.type}
                      title={previewFile.file.name}
                      onClose={() => setPreviewFile(null)}
                      showControls={true}
                      className="h-[90vh]"
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Preview & Settings */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-medium text-gray-900 mb-4">Exam Settings</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-gray-900">Show Results Immediately</Label>
                      <p className="text-sm text-gray-600">Students see their score when they finish</p>
                    </div>
                    <Switch
                      checked={formData.show_results}
                      onCheckedChange={(checked) => setFormData(prev => ({ ...prev, show_results: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-gray-900">Allow Review</Label>
                      <p className="text-sm text-gray-600">Students can review answers before submitting</p>
                    </div>
                    <Switch
                      checked={formData.allow_review}
                      onCheckedChange={(checked) => setFormData(prev => ({ ...prev, allow_review: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-gray-900">Randomize Questions</Label>
                      <p className="text-sm text-gray-600">Questions appear in random order</p>
                    </div>
                    <Switch
                      checked={formData.randomize_questions}
                      onCheckedChange={(checked) => setFormData(prev => ({ ...prev, randomize_questions: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-gray-900">Randomize Answer Options</Label>
                      <p className="text-sm text-gray-600">Answer choices appear in random order</p>
                    </div>
                    <Switch
                      checked={formData.randomize_answers}
                      onCheckedChange={(checked) => setFormData(prev => ({ ...prev, randomize_answers: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-gray-900">Require Webcam</Label>
                      <p className="text-sm text-gray-600">Students must have webcam access during exam</p>
                    </div>
                    <Switch
                      checked={formData.require_webcam}
                      onCheckedChange={(checked) => setFormData(prev => ({ ...prev, require_webcam: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-gray-900">Active</Label>
                      <p className="text-sm text-gray-600">Exam is available for use</p>
                    </div>
                    <Switch
                      checked={formData.is_active}
                      onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_active: checked }))}
                    />
                  </div>
                </div>
              </div>

              {/* Exam Summary */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-medium text-gray-900 mb-3">Exam Summary</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Title:</span>
                    <span className="ml-2 text-gray-900">{formData.title}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Subject Tags:</span>
                    <span className="ml-2 text-gray-900">
                      {formData.subject_tags.length > 0 ? formData.subject_tags.join(', ') : 'None'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Time Limit:</span>
                    <span className="ml-2 text-gray-900">
                      {formData.time_limit_minutes ? `${formData.time_limit_minutes} minutes` : 'No limit'}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Files Uploaded:</span>
                    <span className="ml-2 text-gray-900">{formData.files.length}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Complete */}
          {currentStep === 4 && (
            <div className="text-center py-8">
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Create Exam!</h3>
              <p className="text-gray-600 mb-6">
                Review the information above and click "Create Exam" to finish.
              </p>
              <Button
                onClick={handleSubmit}
                disabled={loading}
                className="bg-gray-900 hover:bg-gray-800 text-white px-8 py-2"
              >
                {loading ? 'Creating...' : 'Create Exam'}
              </Button>
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        {currentStep < 4 && (
          <div className="flex items-center justify-between pt-6 border-t border-gray-200">
            <Button
              type="button"
              variant="outline"
              onClick={prevStep}
              disabled={currentStep === 1}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>

            <Button
              type="button"
              onClick={nextStep}
              disabled={!isStepValid(currentStep)}
              className="bg-gray-900 hover:bg-gray-800 text-white"
            >
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}