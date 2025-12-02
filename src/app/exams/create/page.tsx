'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { supabase } from '@/lib/supabaseClient'
import { uploadFile } from '@/lib/services/fileStorage'
import { createExam } from '@/lib/services/exams'
import { getAcademyId } from '@/lib/academyUtils'
import { PDFConfigurationEditor } from '@/components/exams/PDFConfigurationEditor'

interface CurriculumNode {
  id: string
  name: string
  code?: string
  level_depth: number
  path_name?: string  // Full breadcrumb like "Program A > Track 1 > Level 1"
  path_code?: string  // Full code path like "PROG-A.TRACK-1.LVL-1"
  academy_id: string
  parent_id?: string
}

interface AudioFile {
  id: string
  filename: string
  original_filename: string
  title: string
  file_size_bytes: number
}

export default function CreateExam() {
  const [step, setStep] = useState(1)
  const [examData, setExamData] = useState({
    title: '',
    description: '',
    duration_minutes: 60,
    passing_score: 70,
    number_of_questions: 0,
    curriculum_node_id: '', // Keep for backward compatibility
    curriculum_node_ids: [] as string[], // New: array for multiple selections
  })
  
  // File handling states
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [uploadedFileId, setUploadedFileId] = useState<string | null>(null)
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([])
  const [uploadingAudio, setUploadingAudio] = useState(false)
  
  // UI states
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const audioInputRef = useRef<HTMLInputElement>(null)
  
  // PDF Configuration states
  const [pdfConfig, setPdfConfig] = useState({
    rotation_degrees: 0,
    zoom_level: 1.0,
    is_split_enabled: false,
    split_orientation: 'vertical' as 'vertical' | 'horizontal',
    split_page_1_position: 'left' as 'left' | 'right' | 'top' | 'bottom',
    split_page_2_position: 'right' as 'left' | 'right' | 'top' | 'bottom'
  })
  
  // Curriculum states
  const [curriculumNodes, setCurriculumNodes] = useState<CurriculumNode[]>([])
  const [loadingCurriculum, setLoadingCurriculum] = useState(true)
  const [showCurriculumDropdown, setShowCurriculumDropdown] = useState(false)

  // Load curriculum nodes on component mount
  useEffect(() => {
    const fetchCurriculumNodes = async () => {
      try {
        const response = await fetch('/api/curriculum/deepest')
        const data = await response.json()
        setCurriculumNodes(data.nodes || [])
      } catch (error) {
        console.error('Error fetching curriculum nodes:', error)
      } finally {
        setLoadingCurriculum(false)
      }
    }

    fetchCurriculumNodes()
  }, [])

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('.curriculum-dropdown-container')) {
        setShowCurriculumDropdown(false)
      }
    }

    if (showCurriculumDropdown) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showCurriculumDropdown])

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (file.type !== 'application/pdf') {
      setUploadError('Please select a PDF file')
      return
    }

    // Validate file size (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
      setUploadError('File size must be less than 50MB')
      return
    }

    setUploadError(null)
    setUploadedFile(file)

    // Create local preview URL
    const localUrl = URL.createObjectURL(file)
    setPdfUrl(localUrl)
    // Reset PDF configuration to defaults
    setPdfConfig({
      rotation_degrees: 0,
      zoom_level: 1.0,
      is_split_enabled: false,
      split_orientation: 'vertical',
      split_page_1_position: 'left',
      split_page_2_position: 'right'
    })
  }

  const handleAudioSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploadingAudio(true)
    setUploadError(null)

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        
        // Validate file type
        const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/m4a', 'audio/mp3']
        if (!allowedTypes.includes(file.type)) {
          setUploadError(`Invalid file type: ${file.name}. Please upload MP3, WAV, or M4A files.`)
          continue
        }

        // Validate file size (max 50MB)
        if (file.size > 50 * 1024 * 1024) {
          setUploadError(`File too large: ${file.name}. Maximum size is 50MB.`)
          continue
        }

        const formData = new FormData()
        formData.append('audio', file)
        formData.append('title', file.name)
        formData.append('description', `Audio file for exam`)

        const response = await fetch('/api/exams/upload-audio', {
          method: 'POST',
          body: formData,
        })

        const data = await response.json()

        if (response.ok) {
          setAudioFiles(prev => [...prev, data.file])
        } else {
          setUploadError(data.error || 'Failed to upload audio file')
        }
      }
    } catch (error) {
      console.error('Error uploading audio files:', error)
      setUploadError('Failed to upload audio files')
    } finally {
      setUploadingAudio(false)
    }
  }

  const removeAudioFile = async (audioFileId: string) => {
    setAudioFiles(prev => prev.filter(f => f.id !== audioFileId))
  }

  const handlePDFConfigurationSave = async (config: typeof pdfConfig) => {
    if (!uploadedFileId) {
      console.warn('No file ID available for PDF configuration save')
      return
    }

    try {
      const response = await fetch(`/api/files/config/${uploadedFileId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
      })

      if (!response.ok) {
        throw new Error('Failed to save PDF configuration')
      }

      const result = await response.json()
      if (result.success) {
        setPdfConfig(result.configuration)
        console.log('PDF configuration saved successfully')
      }
    } catch (error) {
      console.error('Error saving PDF configuration:', error)
      throw error // Re-throw so the component can handle the error
    }
  }

  const toggleCurriculumSelection = (nodeId: string) => {
    setExamData(prev => {
      const currentIds = [...prev.curriculum_node_ids]
      const index = currentIds.indexOf(nodeId)
      
      if (index > -1) {
        // Remove if already selected
        currentIds.splice(index, 1)
      } else {
        // Add if not selected
        currentIds.push(nodeId)
      }
      
      return {
        ...prev,
        curriculum_node_ids: currentIds,
        curriculum_node_id: currentIds[0] || '' // Keep backward compatibility
      }
    })
  }

  const removeCurriculumTag = (nodeId: string) => {
    setExamData(prev => ({
      ...prev,
      curriculum_node_ids: prev.curriculum_node_ids.filter(id => id !== nodeId),
      curriculum_node_id: prev.curriculum_node_ids.filter(id => id !== nodeId)[0] || ''
    }))
  }

  const handleCreateExam = async () => {
    if (!examData.title || !uploadedFile || !examData.number_of_questions || examData.number_of_questions < 1) {
      setUploadError('Please provide a title, upload a PDF, and specify the number of questions')
      return
    }

    // Curriculum selection is now optional - removed validation

    setIsUploading(true)
    try {
      const academyId = await getAcademyId()
      
      // Create exam first
      const newExam = await createExam({
        academy_id: academyId,
        title: examData.title,
        description: examData.description || null,
        time_limit_minutes: examData.duration_minutes,
        passing_score: examData.passing_score,
        attempts_allowed: 1,
        randomize_questions: false,
        randomize_answers: false,
        status: 'draft', // Start as draft since questions need to be configured
        show_results: true,
        allow_review: true,
        require_webcam: false,
        difficulty_level: null,
        subject_tags: null,
        learning_objectives: null,
        metadata: { expected_questions: examData.number_of_questions },
        created_by: null,
        exam_type_id: null,
        is_active: true
      })

      // Upload PDF file and capture the file ID
      const uploadResult = await uploadFile(
        uploadedFile,
        academyId,
        'pdf',
        newExam.id
      )
      
      // Set the uploaded file ID for configuration saving
      setUploadedFileId(uploadResult.file.id)

      // Create placeholder questions based on the specified count
      if (examData.number_of_questions > 0) {
        const placeholderQuestions = Array.from({ length: examData.number_of_questions }, (_, index) => ({
          question_number: index + 1,
          question_text: `Question ${index + 1} (configure this question)`,
          question_type: 'multiple_choice',
          correct_answers: null,
          answer_options: null,
          points: 1,
          sort_order: index + 1,
          instructions: null,
          explanation: null
        }))

        // Bulk create the placeholder questions
        const response = await fetch(`/api/exams/${newExam.id}/questions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            questions: placeholderQuestions
          })
        })

        if (!response.ok) {
          console.error('Failed to create placeholder questions')
        }
      }

      // Create curriculum mappings for all selected nodes
      if (examData.curriculum_node_ids.length > 0) {
        // Create mappings for all selected curriculum nodes
        const mappingPromises = examData.curriculum_node_ids.map((nodeId, index) => 
          fetch('/api/exams/curriculum-mapping', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              exam_id: newExam.id,
              curriculum_node_id: nodeId,
              mapping_type: 'placement',
              slot_position: index + 1,
              weight: 1.0
            })
          })
        )

        try {
          await Promise.all(mappingPromises)
        } catch (mappingError) {
          console.warn('Some curriculum mappings may have failed, but exam was created successfully', mappingError)
        }
      }

      // Success - redirect to edit page to configure questions
      window.location.href = `/exams/${newExam.id}/edit?tab=questions`
    } catch (error) {
      console.error('Error creating exam:', error)
      setUploadError('Failed to create exam. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Create New Exam
        </h2>
        <p className="text-gray-600">
          Upload your exam PDF and configure settings
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Panel - Form */}
        <div className="space-y-6">
          {/* Step 1: Basic Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Step 1: Basic Information
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Exam Title *
                </label>
                <input
                  type="text"
                  value={examData.title}
                  onChange={(e) => setExamData({ ...examData, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-900"
                  placeholder="e.g., Mid-term English Assessment"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={examData.description}
                  onChange={(e) => setExamData({ ...examData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-900"
                  rows={3}
                  placeholder="Brief description of this exam..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Curriculum Levels <span className="text-gray-500 text-xs font-normal">(Optional)</span>
                </label>
                
                {/* Selected Tags */}
                {examData.curriculum_node_ids.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-2">
                    {examData.curriculum_node_ids.map(nodeId => {
                      const node = curriculumNodes.find(n => n.id === nodeId)
                      if (!node) return null
                      return (
                        <span
                          key={nodeId}
                          className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-gray-100 text-sm"
                        >
                          <span className="text-gray-700">
                            {node.path_name || node.name}
                          </span>
                          <button
                            onClick={() => removeCurriculumTag(nodeId)}
                            className="text-gray-500 hover:text-gray-700"
                          >
                            <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </span>
                      )
                    })}
                  </div>
                )}

                {/* Dropdown Toggle */}
                {loadingCurriculum ? (
                  <div className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50">
                    Loading curriculum levels...
                  </div>
                ) : (
                  <div className="relative curriculum-dropdown-container">
                    <button
                      type="button"
                      onClick={() => setShowCurriculumDropdown(!showCurriculumDropdown)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-left focus:outline-none focus:ring-2 focus:ring-gray-900 bg-white flex justify-between items-center"
                    >
                      <span className="text-gray-700">
                        {examData.curriculum_node_ids.length > 0 
                          ? `${examData.curriculum_node_ids.length} level(s) selected`
                          : "Select curriculum levels"}
                      </span>
                      <svg 
                        className={`h-4 w-4 text-gray-500 transition-transform ${showCurriculumDropdown ? 'rotate-180' : ''}`} 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    {/* Dropdown Menu */}
                    {showCurriculumDropdown && (
                      <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                        {curriculumNodes.map((node) => (
                          <label
                            key={node.id}
                            className="flex items-center px-3 py-2 hover:bg-gray-50 cursor-pointer"
                          >
                            <input
                              type="checkbox"
                              checked={examData.curriculum_node_ids.includes(node.id)}
                              onChange={() => toggleCurriculumSelection(node.id)}
                              className="h-4 w-4 text-gray-900 border-gray-300 rounded focus:ring-gray-900"
                            />
                            <span className="ml-2 text-sm text-gray-700">
                              {node.path_name || (node.code ? `${node.code} - ${node.name}` : node.name)}
                            </span>
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Select one or more curriculum levels this exam is designed for
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duration (minutes)
                  </label>
                  <input
                    type="number"
                    value={examData.duration_minutes}
                    onChange={(e) => setExamData({ ...examData, duration_minutes: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-900"
                    min="1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Passing Score (%)
                  </label>
                  <input
                    type="number"
                    value={examData.passing_score}
                    onChange={(e) => setExamData({ ...examData, passing_score: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-900"
                    min="0"
                    max="100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Number of Questions *
                </label>
                <input
                  type="number"
                  value={examData.number_of_questions || ''}
                  onChange={(e) => setExamData({ ...examData, number_of_questions: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-900"
                  min="1"
                  placeholder="How many questions are in this PDF exam?"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Specify how many questions are contained in your PDF exam file
                </p>
              </div>
            </div>
          </div>

          {/* Step 2: Upload PDF */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Step 2: Upload Exam PDF *
            </h3>

            <div className="space-y-4">
              {!uploadedFile ? (
                <div 
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-gray-400 transition-colors"
                >
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="mt-2 text-sm text-gray-600">
                    Click to upload PDF or drag and drop
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    PDF up to 50MB
                  </p>
                </div>
              ) : (
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <svg className="h-8 w-8 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                    </svg>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{uploadedFile.name}</p>
                      <p className="text-xs text-gray-500">
                        {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setUploadedFile(null)
                      setPdfUrl(null)
                      if (fileInputRef.current) {
                        fileInputRef.current.value = ''
                      }
                    }}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              )}

              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                onChange={handleFileSelect}
                className="hidden"
              />

              {uploadError && (
                <p className="text-sm text-red-600">{uploadError}</p>
              )}
            </div>
          </div>

          {/* Step 3: Upload Audio Files (Optional) */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Step 3: Upload Audio Files (Optional)
            </h3>

            <div className="space-y-4">
              <div 
                onClick={() => audioInputRef.current?.click()}
                className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-gray-400 transition-colors"
              >
                <svg className="mx-auto h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
                <p className="mt-2 text-sm text-gray-600">
                  {uploadingAudio ? 'Uploading audio files...' : 'Click to upload audio files'}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  MP3, WAV, M4A up to 50MB each
                </p>
              </div>

              <input
                ref={audioInputRef}
                type="file"
                accept="audio/*"
                multiple
                onChange={handleAudioSelect}
                className="hidden"
              />

              {/* Audio Files List */}
              {audioFiles.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700">Uploaded Audio Files:</h4>
                  {audioFiles.map((audioFile) => (
                    <div key={audioFile.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <svg className="h-6 w-6 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M9 2a2 2 0 000 4h2a2 2 0 100-4H9zM4 5a2 2 0 012-2v6h8V3a2 2 0 012 2v6h2a2 2 0 010 4h-2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2H2a2 2 0 010-4h2V5z" />
                        </svg>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{audioFile.title}</p>
                          <p className="text-xs text-gray-500">
                            {(audioFile.file_size_bytes / (1024 * 1024)).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeAudioFile(audioFile.id)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between">
            <Link
              href="/exams"
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </Link>
            <button
              onClick={handleCreateExam}
              disabled={!examData.title || !uploadedFile || !examData.number_of_questions || examData.number_of_questions < 1 || isUploading}
              className="px-6 py-2 bg-gray-900 text-white rounded-md hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isUploading ? 'Creating...' : 'Create Exam'}
            </button>
          </div>
        </div>

        {/* Right Panel - PDF Configuration */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <PDFConfigurationEditor
            pdfUrl={pdfUrl}
            onConfigurationSave={handlePDFConfigurationSave}
            initialConfig={pdfConfig}
            showSaveButton={false}
            className="border-0 shadow-none"
          />
        </div>
      </div>
    </div>
  )
}