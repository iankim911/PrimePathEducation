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
import { CurriculumSelector } from '@/components/features/curriculum/CurriculumSelector'
import { GradeSelector } from '@/components/features/grades/GradeSelector'
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
    curriculum_node_id: '',
    target_grade: '',
    schedule_info: '',
  })
  
  const [curriculumPathName, setCurriculumPathName] = useState<string | null>(null)

  useEffect(() => {
    if (open) {
      setFormData({
        name: classItem.name || '',
        level_label: classItem.level_label || '',
        curriculum_node_id: classItem.curriculum_node_id || '',
        target_grade: classItem.target_grade?.toString() || '',
        schedule_info: classItem.schedule_info || '',
      })
      setCurriculumPathName(classItem.level_label || null)
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
          curriculum_node_id: formData.curriculum_node_id || null,
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
                <Label className="text-right">
                  Curriculum Level
                </Label>
                <div className="col-span-3">
                  <CurriculumSelector
                    value={formData.curriculum_node_id || null}
                    onValueChange={(nodeId, pathName) => {
                      setFormData({ 
                        ...formData, 
                        curriculum_node_id: nodeId || '',
                        level_label: pathName || '' // Keep backward compatibility for existing data
                      })
                      setCurriculumPathName(pathName)
                    }}
                    placeholder="Select curriculum level"
                    allowEmpty={true}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-4 items-center gap-4">
                <Label className="text-right">
                  Target Grade
                </Label>
                <div className="col-span-3">
                  <GradeSelector
                    value={formData.target_grade}
                    onValueChange={(value) => setFormData({ ...formData, target_grade: value })}
                    placeholder="Select target grade"
                    includeAllOption={true}
                    allowEmpty={true}
                  />
                </div>
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