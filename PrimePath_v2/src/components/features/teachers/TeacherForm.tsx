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
import { PlusCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface TeacherFormProps {
  onSuccess?: () => void
}

export function TeacherForm({ onSuccess }: TeacherFormProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()
  
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.full_name || !formData.email) {
      toast({
        title: "Error",
        description: "Teacher name and email are required",
        variant: "destructive",
      })
      return
    }

    setLoading(true)

    try {
      const response = await fetch('/api/teachers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        throw new Error('Failed to add teacher')
      }

      toast({
        title: "Success!",
        description: "Teacher added successfully",
      })

      // Reset form
      setFormData({
        full_name: '',
        email: '',
      })
      
      setOpen(false)
      
      // Refresh the teachers list
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add teacher. Please try again.",
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
          Add Teacher
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add New Teacher</DialogTitle>
            <DialogDescription>
              Add a new teacher to your academy
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="full_name" className="text-right">
                Full Name*
              </Label>
              <Input
                id="full_name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="col-span-3"
                placeholder="John Smith"
                required
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="email" className="text-right">
                Email*
              </Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="col-span-3"
                placeholder="john.smith@academy.com"
                required
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Adding...' : 'Add Teacher'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}