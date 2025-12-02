"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Pencil } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { GradeSelector } from '@/components/features/grades/GradeSelector'
import type { Student } from '@/lib/services/students'

interface StudentEditFormProps {
  student: Student
  onSuccess?: () => void
}

export function StudentEditForm({ student, onSuccess }: StudentEditFormProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()
  
  const [formData, setFormData] = useState({
    full_name: '',
    english_name: '',
    grade: '',
    school_name: '',
    parent_name: '',
    parent_phone: '',
  })

  // Load student data when dialog opens
  useEffect(() => {
    if (open) {
      setFormData({
        full_name: student.full_name || '',
        english_name: student.english_name || '',
        grade: student.grade?.toString() || '',
        school_name: student.school_name || '',
        parent_name: student.parent_name || '',
        parent_phone: student.parent_phone || '',
      })
    }
  }, [open, student])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.full_name) {
      toast({
        title: "Error",
        description: "Student name is required",
        variant: "destructive",
      })
      return
    }

    setLoading(true)

    try {
      const response = await fetch(`/api/students/${student.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          grade: formData.grade ? parseInt(formData.grade) : null,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to update student')
      }

      toast({
        title: "Success!",
        description: "Student updated successfully",
      })
      
      setOpen(false)
      
      // Refresh the students list
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update student. Please try again.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setOpen(true)}
        className="border-gray-300 hover:bg-gray-50 text-gray-700"
      >
        <Pencil className="h-4 w-4" />
      </Button>
      
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-[500px] bg-white text-gray-900">
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>Edit Student</DialogTitle>
              <DialogDescription>
                Update student information
              </DialogDescription>
            </DialogHeader>
            
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="full_name" className="text-right">
                  Korean Name*
                </Label>
                <Input
                  id="full_name"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="col-span-3"
                  placeholder="김지우"
                  required
                />
              </div>
              
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="english_name" className="text-right">
                  English Name
                </Label>
                <Input
                  id="english_name"
                  value={formData.english_name}
                  onChange={(e) => setFormData({ ...formData, english_name: e.target.value })}
                  className="col-span-3"
                  placeholder="Ji-woo Kim"
                />
              </div>
              
              <div className="grid grid-cols-4 items-center gap-4">
                <Label className="text-right">
                  Grade
                </Label>
                <div className="col-span-3">
                  <GradeSelector
                    value={formData.grade}
                    onValueChange={(value) => setFormData({ ...formData, grade: value })}
                    placeholder="Select grade"
                    includeAllOption={false}
                    allowEmpty={true}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="school_name" className="text-right">
                  School
                </Label>
                <Input
                  id="school_name"
                  value={formData.school_name}
                  onChange={(e) => setFormData({ ...formData, school_name: e.target.value })}
                  className="col-span-3"
                  placeholder="Seoul Elementary School"
                />
              </div>
              
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="parent_name" className="text-right">
                  Parent Name
                </Label>
                <Input
                  id="parent_name"
                  value={formData.parent_name}
                  onChange={(e) => setFormData({ ...formData, parent_name: e.target.value })}
                  className="col-span-3"
                  placeholder="김민정"
                />
              </div>
              
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="parent_phone" className="text-right">
                  Parent Phone
                </Label>
                <Input
                  id="parent_phone"
                  value={formData.parent_phone}
                  onChange={(e) => setFormData({ ...formData, parent_phone: e.target.value })}
                  className="col-span-3"
                  placeholder="010-1234-5678"
                />
              </div>
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Saving...' : 'Save Changes'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  )
}