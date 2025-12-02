"use client"

import { useState, useEffect } from 'react'
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
import { 
  Plus, 
  Calendar
} from 'lucide-react'
import { toast } from 'sonner'

interface SessionFormProps {
  examId: string
  onSuccess: () => void
}

interface Class {
  id: string
  name: string
  grade: string
  subject: string
}

interface Teacher {
  id: string
  first_name: string
  last_name: string
}

interface SessionFormData {
  title: string
  instructions: string
  class_id: string
  teacher_id: string
  scheduled_start: string
  scheduled_end: string
  time_limit_override: string
  attempts_allowed_override: string
  allow_late_entry: boolean
  shuffle_questions: boolean
}

export function SessionForm({ examId, onSuccess }: SessionFormProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [classes, setClasses] = useState<Class[]>([])
  const [teachers, setTeachers] = useState<Teacher[]>([])
  
  const [formData, setFormData] = useState<SessionFormData>({
    title: '',
    instructions: '',
    class_id: '',
    teacher_id: '',
    scheduled_start: '',
    scheduled_end: '',
    time_limit_override: '',
    attempts_allowed_override: '',
    allow_late_entry: true,
    shuffle_questions: false
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch classes
        const classesResponse = await fetch('/api/classes')
        if (classesResponse.ok) {
          const classesData = await classesResponse.json()
          setClasses(classesData.classes || [])
        }

        // Fetch teachers
        const teachersResponse = await fetch('/api/teachers')
        if (teachersResponse.ok) {
          const teachersData = await teachersResponse.json()
          setTeachers(teachersData.teachers || [])
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    }

    if (open) {
      fetchData()
    }
  }, [open])

  const handleSubmit = async () => {
    if (!formData.title.trim()) {
      toast.error('Session title is required')
      return
    }

    if (!formData.class_id) {
      toast.error('Please select a class')
      return
    }

    if (!formData.teacher_id) {
      toast.error('Please select a teacher')
      return
    }

    setLoading(true)

    try {
      const sessionData = {
        exam_id: examId,
        title: formData.title.trim(),
        instructions: formData.instructions.trim() || null,
        class_id: formData.class_id,
        teacher_id: formData.teacher_id,
        scheduled_start: formData.scheduled_start || null,
        scheduled_end: formData.scheduled_end || null,
        time_limit_override: formData.time_limit_override ? parseInt(formData.time_limit_override) : null,
        attempts_allowed_override: formData.attempts_allowed_override ? parseInt(formData.attempts_allowed_override) : null,
        allow_late_entry: formData.allow_late_entry,
        shuffle_questions: formData.shuffle_questions,
        status: 'scheduled'
      }

      const response = await fetch('/api/exam-sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Failed to create session')
      }

      toast.success('Session created successfully!')
      
      // Reset form
      setFormData({
        title: '',
        instructions: '',
        class_id: '',
        teacher_id: '',
        scheduled_start: '',
        scheduled_end: '',
        time_limit_override: '',
        attempts_allowed_override: '',
        allow_late_entry: true,
        shuffle_questions: false
      })
      
      setOpen(false)
      onSuccess()
    } catch (error) {
      console.error('Error creating session:', error)
      toast.error(error instanceof Error ? error.message : 'Failed to create session')
    } finally {
      setLoading(false)
    }
  }

  // Generate default session title when class is selected
  useEffect(() => {
    if (formData.class_id && !formData.title.includes('Session for')) {
      const selectedClass = classes.find(c => c.id === formData.class_id)
      if (selectedClass) {
        const today = new Date().toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        })
        setFormData(prev => ({
          ...prev,
          title: `Exam Session for ${selectedClass.name} - ${today}`
        }))
      }
    }
  }, [formData.class_id, classes])

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-gray-900 hover:bg-gray-800 text-white">
          <Plus className="h-4 w-4 mr-2" />
          Create Session
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] bg-white max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-gray-900">Create New Exam Session</DialogTitle>
          <DialogDescription className="text-gray-600">
            Set up a scheduled exam session for a specific class and teacher.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Basic Information */}
          <div>
            <Label htmlFor="title" className="text-gray-900">Session Title *</Label>
            <Input
              id="title"
              type="text"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              placeholder="e.g., Mid-term Exam Session for Grade 10A"
              className="mt-1 text-gray-900"
            />
          </div>

          <div>
            <Label htmlFor="instructions" className="text-gray-900">Instructions (Optional)</Label>
            <Textarea
              id="instructions"
              value={formData.instructions}
              onChange={(e) => setFormData(prev => ({ ...prev, instructions: e.target.value }))}
              placeholder="Special instructions for this session..."
              className="mt-1 text-gray-900"
              rows={3}
            />
          </div>

          {/* Class and Teacher Selection */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-gray-900">Class *</Label>
              <Select value={formData.class_id} onValueChange={(value) => setFormData(prev => ({ ...prev, class_id: value }))}>
                <SelectTrigger className="mt-1 text-gray-900">
                  <SelectValue placeholder="Select class" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  {classes.map((cls) => (
                    <SelectItem key={cls.id} value={cls.id} className="text-gray-900">
                      {cls.name} ({cls.grade} - {cls.subject})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-gray-900">Teacher *</Label>
              <Select value={formData.teacher_id} onValueChange={(value) => setFormData(prev => ({ ...prev, teacher_id: value }))}>
                <SelectTrigger className="mt-1 text-gray-900">
                  <SelectValue placeholder="Select teacher" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  {teachers.map((teacher) => (
                    <SelectItem key={teacher.id} value={teacher.id} className="text-gray-900">
                      {teacher.first_name} {teacher.last_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Scheduling */}
          <div>
            <Label className="text-gray-900">Scheduling (Optional)</Label>
            <div className="grid grid-cols-2 gap-4 mt-2">
              <div>
                <Label htmlFor="scheduled_start" className="text-sm text-gray-600">Start Date & Time</Label>
                <Input
                  id="scheduled_start"
                  type="datetime-local"
                  value={formData.scheduled_start}
                  onChange={(e) => setFormData(prev => ({ ...prev, scheduled_start: e.target.value }))}
                  className="text-gray-900"
                />
              </div>
              <div>
                <Label htmlFor="scheduled_end" className="text-sm text-gray-600">End Date & Time</Label>
                <Input
                  id="scheduled_end"
                  type="datetime-local"
                  value={formData.scheduled_end}
                  onChange={(e) => setFormData(prev => ({ ...prev, scheduled_end: e.target.value }))}
                  className="text-gray-900"
                />
              </div>
            </div>
          </div>

          {/* Overrides */}
          <div>
            <Label className="text-gray-900">Session Overrides (Optional)</Label>
            <div className="grid grid-cols-2 gap-4 mt-2">
              <div>
                <Label htmlFor="time_limit_override" className="text-sm text-gray-600">Time Limit (minutes)</Label>
                <Input
                  id="time_limit_override"
                  type="number"
                  value={formData.time_limit_override}
                  onChange={(e) => setFormData(prev => ({ ...prev, time_limit_override: e.target.value }))}
                  placeholder="Use exam default"
                  className="text-gray-900"
                  min="1"
                />
              </div>
              <div>
                <Label htmlFor="attempts_allowed_override" className="text-sm text-gray-600">Attempts Allowed</Label>
                <Input
                  id="attempts_allowed_override"
                  type="number"
                  value={formData.attempts_allowed_override}
                  onChange={(e) => setFormData(prev => ({ ...prev, attempts_allowed_override: e.target.value }))}
                  placeholder="Use exam default"
                  className="text-gray-900"
                  min="1"
                />
              </div>
            </div>
          </div>

          {/* Settings */}
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <Label className="text-gray-900">Allow Late Entry</Label>
                <p className="text-sm text-gray-600">Students can join after session has started</p>
              </div>
              <Switch
                checked={formData.allow_late_entry}
                onCheckedChange={(checked) => setFormData(prev => ({ ...prev, allow_late_entry: checked }))}
              />
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <Label className="text-gray-900">Shuffle Questions</Label>
                <p className="text-sm text-gray-600">Randomize question order for this session</p>
              </div>
              <Switch
                checked={formData.shuffle_questions}
                onCheckedChange={(checked) => setFormData(prev => ({ ...prev, shuffle_questions: checked }))}
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-4 border-t border-gray-200">
            <Button
              onClick={handleSubmit}
              disabled={loading}
              className="bg-gray-900 hover:bg-gray-800 text-white"
            >
              {loading ? 'Creating...' : 'Create Session'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}