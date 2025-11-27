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
import type { Class } from '@/lib/services/classes'

interface ClassEditFormProps {
  classItem: Class
  onSuccess?: () => void
}

export function ClassEditForm({ classItem, onSuccess }: ClassEditFormProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()
  
  const [formData, setFormData] = useState({
    name: '',
    level_label: '',
    target_grade: '',
    schedule_info: '',
  })

  useEffect(() => {
    if (open) {
      setFormData({
        name: classItem.name || '',
        level_label: classItem.level_label || '',
        target_grade: classItem.target_grade?.toString() || '',
        schedule_info: classItem.schedule_info || '',
      })
    }
  }, [open, classItem])

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
      const response = await fetch(`/api/classes/${classItem.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          target_grade: formData.target_grade ? parseInt(formData.target_grade) : null,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to update class')
      }

      toast({
        title: "Success!",
        description: "Class updated successfully",
      })
      
      setOpen(false)
      
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update class. Please try again.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setOpen(true)}
      >
        <Pencil className="h-4 w-4" />
      </Button>
      
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>Edit Class</DialogTitle>
              <DialogDescription>
                Update class information
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
                    <SelectItem value="none" className="text-gray-900">No level</SelectItem>
                    <SelectItem value="Beginner">Beginner</SelectItem>
                    <SelectItem value="Elementary">Elementary</SelectItem>
                    <SelectItem value="Pre-Intermediate">Pre-Intermediate</SelectItem>
                    <SelectItem value="Intermediate">Intermediate</SelectItem>
                    <SelectItem value="Upper-Intermediate">Upper-Intermediate</SelectItem>
                    <SelectItem value="Advanced">Advanced</SelectItem>
                    <SelectItem value="TOEFL Prep">TOEFL Prep</SelectItem>
                    <SelectItem value="TOEIC Prep">TOEIC Prep</SelectItem>
                    <SelectItem value="Speaking Focus">Speaking Focus</SelectItem>
                    <SelectItem value="Writing Focus">Writing Focus</SelectItem>
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
                    <SelectItem value="1">Grade 1</SelectItem>
                    <SelectItem value="2">Grade 2</SelectItem>
                    <SelectItem value="3">Grade 3</SelectItem>
                    <SelectItem value="4">Grade 4</SelectItem>
                    <SelectItem value="5">Grade 5</SelectItem>
                    <SelectItem value="6">Grade 6</SelectItem>
                    <SelectItem value="7">Middle 1</SelectItem>
                    <SelectItem value="8">Middle 2</SelectItem>
                    <SelectItem value="9">Middle 3</SelectItem>
                    <SelectItem value="10">High 1</SelectItem>
                    <SelectItem value="11">High 2</SelectItem>
                    <SelectItem value="12">High 3</SelectItem>
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