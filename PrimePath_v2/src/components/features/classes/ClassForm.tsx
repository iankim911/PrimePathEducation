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
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { PlusCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import type { Teacher } from '@/lib/services/teachers'

interface ClassFormProps {
  onSuccess?: () => void
}

export function ClassForm({ onSuccess }: ClassFormProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [loadingTeachers, setLoadingTeachers] = useState(false)
  const { toast } = useToast()
  
  const [formData, setFormData] = useState({
    name: '',
    level_label: '',
    target_grade: '',
    schedule_info: '',
  })

  const [selectedTeachers, setSelectedTeachers] = useState<{
    [teacherId: string]: {
      selected: boolean
      role: 'main' | 'sub' | 'native'
      isPrimary: boolean
    }
  }>({})

  // Fetch teachers when dialog opens
  useEffect(() => {
    if (open) {
      fetchTeachers()
    }
  }, [open])

  const fetchTeachers = async () => {
    setLoadingTeachers(true)
    try {
      const response = await fetch('/api/teachers')
      if (!response.ok) {
        throw new Error('Failed to fetch teachers')
      }
      const data = await response.json()
      setTeachers(data.teachers)
    } catch (error) {
      console.error('Error fetching teachers:', error)
      toast({
        title: "Warning",
        description: "Could not load teachers. You can still create the class.",
        variant: "destructive",
      })
    } finally {
      setLoadingTeachers(false)
    }
  }

  const handleTeacherSelection = (
    teacherId: string, 
    field: 'selected' | 'role' | 'isPrimary', 
    value: boolean | string
  ) => {
    setSelectedTeachers(prev => {
      const updated = { ...prev }
      
      if (!updated[teacherId]) {
        updated[teacherId] = { selected: false, role: 'main', isPrimary: false }
      }
      
      if (field === 'isPrimary' && value === true) {
        // Unset all other primary teachers
        Object.keys(updated).forEach(id => {
          if (id !== teacherId) {
            updated[id].isPrimary = false
          }
        })
      }
      
      updated[teacherId] = { ...updated[teacherId], [field]: value }
      
      return updated
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name) {
      toast({
        title: "Error",
        description: "Class name is required",
        variant: "destructive",
      })
      return
    }

    setLoading(true)

    try {
      // First create the class
      const response = await fetch('/api/classes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          target_grade: formData.target_grade ? parseInt(formData.target_grade) : null,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to add class')
      }

      const { class: newClass } = await response.json()

      // Then assign selected teachers
      const teacherAssignments = Object.entries(selectedTeachers)
        .filter(([_, teacher]) => teacher.selected)
        .map(([teacherId, teacher]) => ({
          teacherId,
          role: teacher.role,
          isPrimary: teacher.isPrimary
        }))

      if (teacherAssignments.length > 0) {
        await fetch('/api/class-teachers', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            classId: newClass.id,
            teachers: teacherAssignments
          }),
        })
      }

      toast({
        title: "Success!",
        description: "Class added successfully",
      })

      // Reset form
      setFormData({
        name: '',
        level_label: '',
        target_grade: '',
        schedule_info: '',
      })
      setSelectedTeachers({})
      
      setOpen(false)
      
      // Refresh the classes list
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add class. Please try again.",
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
          <PlusCircle className="mr-2 h-4 w-4" />
          Add Class
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add New Class</DialogTitle>
            <DialogDescription>
              Create a new class for your academy
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Class Name*
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="col-span-3"
                placeholder="Elementary A"
                required
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="level_label" className="text-right">
                Level
              </Label>
              <Select
                value={formData.level_label}
                onValueChange={(value) => setFormData({ ...formData, level_label: value })}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select level" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="Beginner" className="text-gray-900">Beginner</SelectItem>
                  <SelectItem value="Elementary" className="text-gray-900">Elementary</SelectItem>
                  <SelectItem value="Pre-Intermediate" className="text-gray-900">Pre-Intermediate</SelectItem>
                  <SelectItem value="Intermediate" className="text-gray-900">Intermediate</SelectItem>
                  <SelectItem value="Upper-Intermediate" className="text-gray-900">Upper-Intermediate</SelectItem>
                  <SelectItem value="Advanced" className="text-gray-900">Advanced</SelectItem>
                  <SelectItem value="TOEFL Prep" className="text-gray-900">TOEFL Prep</SelectItem>
                  <SelectItem value="TOEIC Prep" className="text-gray-900">TOEIC Prep</SelectItem>
                  <SelectItem value="Speaking Focus" className="text-gray-900">Speaking Focus</SelectItem>
                  <SelectItem value="Writing Focus" className="text-gray-900">Writing Focus</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="target_grade" className="text-right">
                Target Grade
              </Label>
              <Select
                value={formData.target_grade}
                onValueChange={(value) => setFormData({ ...formData, target_grade: value })}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select target grade" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="all" className="text-gray-900">All Grades</SelectItem>
                  <SelectItem value="1" className="text-gray-900">Grade 1</SelectItem>
                  <SelectItem value="2" className="text-gray-900">Grade 2</SelectItem>
                  <SelectItem value="3" className="text-gray-900">Grade 3</SelectItem>
                  <SelectItem value="4" className="text-gray-900">Grade 4</SelectItem>
                  <SelectItem value="5" className="text-gray-900">Grade 5</SelectItem>
                  <SelectItem value="6" className="text-gray-900">Grade 6</SelectItem>
                  <SelectItem value="7" className="text-gray-900">Middle 1</SelectItem>
                  <SelectItem value="8" className="text-gray-900">Middle 2</SelectItem>
                  <SelectItem value="9" className="text-gray-900">Middle 3</SelectItem>
                  <SelectItem value="10" className="text-gray-900">High 1</SelectItem>
                  <SelectItem value="11" className="text-gray-900">High 2</SelectItem>
                  <SelectItem value="12" className="text-gray-900">High 3</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="schedule_info" className="text-right">
                Schedule
              </Label>
              <Input
                id="schedule_info"
                value={formData.schedule_info}
                onChange={(e) => setFormData({ ...formData, schedule_info: e.target.value })}
                className="col-span-3"
                placeholder="Mon/Wed 14:00-15:30"
              />
            </div>
            
            {/* Teacher Assignment Section */}
            <div className="grid grid-cols-4 items-start gap-4 pt-4 border-t">
              <Label className="text-right mt-2">
                Assign Teachers
              </Label>
              <div className="col-span-3">
                {loadingTeachers ? (
                  <div className="text-sm text-gray-500">Loading teachers...</div>
                ) : teachers.length === 0 ? (
                  <div className="text-sm text-gray-500">
                    No teachers available. Add teachers first to assign them to classes.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {teachers.map(teacher => {
                      const teacherData = selectedTeachers[teacher.id] || { 
                        selected: false, 
                        role: 'main', 
                        isPrimary: false 
                      }
                      
                      return (
                        <div key={teacher.id} className="border rounded-lg p-3 space-y-2">
                          <div className="flex items-center space-x-2">
                            <Checkbox
                              id={`teacher-${teacher.id}`}
                              checked={teacherData.selected}
                              onCheckedChange={(checked) => 
                                handleTeacherSelection(teacher.id, 'selected', checked as boolean)
                              }
                            />
                            <Label htmlFor={`teacher-${teacher.id}`} className="font-medium">
                              {teacher.full_name}
                            </Label>
                          </div>
                          
                          {teacherData.selected && (
                            <div className="ml-6 space-y-2">
                              <div className="flex items-center gap-4">
                                <Select
                                  value={teacherData.role}
                                  onValueChange={(value) => 
                                    handleTeacherSelection(teacher.id, 'role', value)
                                  }
                                >
                                  <SelectTrigger className="w-32">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent className="bg-white">
                                    <SelectItem value="main" className="text-gray-900">Main</SelectItem>
                                    <SelectItem value="sub" className="text-gray-900">Sub</SelectItem>
                                    <SelectItem value="native" className="text-gray-900">Native</SelectItem>
                                  </SelectContent>
                                </Select>
                                
                                <div className="flex items-center space-x-2">
                                  <Checkbox
                                    id={`primary-${teacher.id}`}
                                    checked={teacherData.isPrimary}
                                    onCheckedChange={(checked) => 
                                      handleTeacherSelection(teacher.id, 'isPrimary', checked as boolean)
                                    }
                                  />
                                  <Label htmlFor={`primary-${teacher.id}`} className="text-sm">
                                    Primary Teacher
                                  </Label>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Adding...' : 'Add Class'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}