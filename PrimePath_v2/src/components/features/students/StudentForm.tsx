"use client"

import { useState } from 'react'
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
import { PlusCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface StudentFormProps {
  onSuccess?: () => void
}

export function StudentForm({ onSuccess }: StudentFormProps) {
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
      const response = await fetch('/api/students', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          grade: formData.grade ? parseInt(formData.grade) : null,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to add student')
      }

      toast({
        title: "Success!",
        description: "Student added successfully",
      })

      // Reset form
      setFormData({
        full_name: '',
        english_name: '',
        grade: '',
        school_name: '',
        parent_name: '',
        parent_phone: '',
      })
      
      setOpen(false)
      
      // Refresh the students list
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add student. Please try again.",
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
          Add Student
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add New Student</DialogTitle>
            <DialogDescription>
              Enter the student's information below
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
              <Label htmlFor="grade" className="text-right">
                Grade
              </Label>
              <Select
                value={formData.grade}
                onValueChange={(value) => setFormData({ ...formData, grade: value })}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select grade" />
                </SelectTrigger>
                <SelectContent className="bg-white">
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
              {loading ? 'Adding...' : 'Add Student'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}