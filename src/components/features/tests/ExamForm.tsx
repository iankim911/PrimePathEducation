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
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Switch } from '@/components/ui/switch'
import { Plus } from 'lucide-react'
import { toast } from 'sonner'

interface ExamFormProps {
  onSuccess: () => void
}

export function ExamForm({ onSuccess }: ExamFormProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    subject_tags: '',
    time_limit_minutes: '',
    attempts_allowed: '1',
    passing_score: '',
    show_results: true,
    allow_review: true,
    randomize_questions: false,
    is_active: true
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.title.trim()) {
      toast.error('Title is required')
      return
    }

    setLoading(true)

    try {
      const response = await fetch('/api/exams', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: formData.title.trim(),
          description: formData.description.trim() || null,
          subject_tags: formData.subject_tags.trim() ? [formData.subject_tags.trim()] : null,
          time_limit_minutes: formData.time_limit_minutes ? parseInt(formData.time_limit_minutes) : null,
          attempts_allowed: parseInt(formData.attempts_allowed),
          passing_score: formData.passing_score ? parseFloat(formData.passing_score) : null,
          show_results: formData.show_results,
          allow_review: formData.allow_review,
          randomize_questions: formData.randomize_questions,
          is_active: formData.is_active
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Failed to create exam')
      }

      toast.success('Exam created successfully')
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        subject_tags: '',
        time_limit_minutes: '',
        attempts_allowed: '1',
        passing_score: '',
        show_results: true,
        allow_review: true,
        randomize_questions: false,
        is_active: true
      })
      
      setOpen(false)
      onSuccess()
    } catch (error) {
      console.error('Error creating exam:', error)
      toast.error(error instanceof Error ? error.message : 'Failed to create exam')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-gray-900 hover:bg-gray-800 text-white">
          <Plus className="h-4 w-4 mr-2" />
          New Exam
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] bg-white">
        <DialogHeader>
          <DialogTitle className="text-gray-900">Create New Exam</DialogTitle>
          <DialogDescription className="text-gray-600">
            Set up a new exam with questions and settings. You can add questions after creating the exam.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            {/* Basic Information */}
            <div className="col-span-2">
              <Label htmlFor="title" className="text-gray-900">Title *</Label>
              <Input
                id="title"
                type="text"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="e.g., Mid-term English Assessment"
                className="mt-1 text-gray-900"
                required
              />
            </div>

            <div className="col-span-2">
              <Label htmlFor="description" className="text-gray-900">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Brief description of this exam..."
                className="mt-1 text-gray-900"
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="subject_tags" className="text-gray-900">Subject</Label>
              <Input
                id="subject_tags"
                type="text"
                value={formData.subject_tags}
                onChange={(e) => handleInputChange('subject_tags', e.target.value)}
                placeholder="e.g., English, Math"
                className="mt-1 text-gray-900"
              />
            </div>

            <div>
              <Label htmlFor="time_limit_minutes" className="text-gray-900">Time Limit (minutes)</Label>
              <Input
                id="time_limit_minutes"
                type="number"
                value={formData.time_limit_minutes}
                onChange={(e) => handleInputChange('time_limit_minutes', e.target.value)}
                placeholder="Leave empty for no limit"
                className="mt-1 text-gray-900"
                min="1"
              />
            </div>

            <div>
              <Label htmlFor="attempts_allowed" className="text-gray-900">Attempts Allowed *</Label>
              <Select value={formData.attempts_allowed} onValueChange={(value) => handleInputChange('attempts_allowed', value)}>
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
                onChange={(e) => handleInputChange('passing_score', e.target.value)}
                placeholder="e.g., 70"
                className="mt-1 text-gray-900"
                min="0"
                max="100"
              />
            </div>
          </div>


          {/* Settings */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-gray-900">Show Results Immediately</Label>
                <p className="text-sm text-gray-600">Students see their score when they finish</p>
              </div>
              <Switch
                checked={formData.show_results}
                onCheckedChange={(checked) => handleInputChange('show_results', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-gray-900">Allow Review</Label>
                <p className="text-sm text-gray-600">Students can review their answers before submitting</p>
              </div>
              <Switch
                checked={formData.allow_review}
                onCheckedChange={(checked) => handleInputChange('allow_review', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-gray-900">Randomize Questions</Label>
                <p className="text-sm text-gray-600">Questions appear in random order for each student</p>
              </div>
              <Switch
                checked={formData.randomize_questions}
                onCheckedChange={(checked) => handleInputChange('randomize_questions', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-gray-900">Active</Label>
                <p className="text-sm text-gray-600">Exam is available for use</p>
              </div>
              <Switch
                checked={formData.is_active}
                onCheckedChange={(checked) => handleInputChange('is_active', checked)}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={loading}
              className="bg-gray-900 hover:bg-gray-800 text-white"
            >
              {loading ? 'Creating...' : 'Create Exam'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}