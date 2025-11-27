"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { UserPlus } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import type { Student } from '@/lib/services/students'
import type { Class } from '@/lib/services/classes'

interface EnrollmentFormProps {
  onSuccess?: () => void
}

export function EnrollmentForm({ onSuccess }: EnrollmentFormProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [students, setStudents] = useState<Student[]>([])
  const [classes, setClasses] = useState<Class[]>([])
  const [availableStudents, setAvailableStudents] = useState<Student[]>([])
  const { toast } = useToast()
  
  const [formData, setFormData] = useState({
    student_id: '',
    class_id: '',
  })

  // Fetch students and classes when dialog opens
  useEffect(() => {
    if (open) {
      fetchStudents()
      fetchClasses()
    }
  }, [open])

  // Fetch available students when class is selected
  useEffect(() => {
    if (formData.class_id) {
      fetchAvailableStudents(formData.class_id)
    } else {
      setAvailableStudents(students)
    }
  }, [formData.class_id, students])

  const fetchStudents = async () => {
    try {
      const response = await fetch('/api/students')
      const data = await response.json()
      setStudents(data.students)
      setAvailableStudents(data.students)
    } catch (error) {
      console.error('Error fetching students:', error)
    }
  }

  const fetchClasses = async () => {
    try {
      const response = await fetch('/api/classes')
      const data = await response.json()
      setClasses(data.classes)
    } catch (error) {
      console.error('Error fetching classes:', error)
    }
  }

  const fetchAvailableStudents = async (classId: string) => {
    try {
      const response = await fetch(`/api/enrollments?class_id=${classId}&available=true`)
      const data = await response.json()
      setAvailableStudents(data.students)
    } catch (error) {
      console.error('Error fetching available students:', error)
      setAvailableStudents(students)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.student_id || !formData.class_id) {
      toast({
        title: "Error",
        description: "Please select both a student and a class",
        variant: "destructive",
      })
      return
    }

    setLoading(true)

    try {
      const response = await fetch('/api/enrollments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'Failed to enroll student')
      }

      toast({
        title: "Success!",
        description: "Student enrolled successfully",
      })

      // Reset form
      setFormData({
        student_id: '',
        class_id: '',
      })
      
      setOpen(false)
      
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to enroll student",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-gray-900 hover:bg-gray-800 text-white">
          <UserPlus className="mr-2 h-4 w-4" />
          Enroll Student
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Enroll Student in Class</DialogTitle>
            <DialogDescription>
              Assign a student to a class
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="class_id" className="text-right">
                Class*
              </Label>
              <Select
                value={formData.class_id}
                onValueChange={(value) => setFormData({ ...formData, class_id: value })}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select a class first" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  {classes.map((classItem) => (
                    <SelectItem key={classItem.id} value={classItem.id} className="text-gray-900">
                      {classItem.name} 
                      {classItem.schedule_info && ` - ${classItem.schedule_info}`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="student_id" className="text-right">
                Student*
              </Label>
              <Select
                value={formData.student_id}
                onValueChange={(value) => setFormData({ ...formData, student_id: value })}
                disabled={!formData.class_id}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder={
                    formData.class_id 
                      ? `${availableStudents.length} students available`
                      : "Select a class first"
                  } />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  {availableStudents.map((student) => (
                    <SelectItem key={student.id} value={student.id} className="text-gray-900">
                      {student.english_name || student.full_name}
                      {student.grade && ` (Grade ${student.grade})`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {formData.class_id && availableStudents.length === 0 && (
              <p className="text-sm text-gray-500 col-span-4 text-center">
                All students are already enrolled in this class
              </p>
            )}
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={loading || !formData.student_id || !formData.class_id}
            >
              {loading ? 'Enrolling...' : 'Enroll Student'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}