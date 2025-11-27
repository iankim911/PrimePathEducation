"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Trash2 } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import type { Class } from '@/lib/services/classes'

interface ClassDeleteButtonProps {
  classItem: Class
  onSuccess?: () => void
}

export function ClassDeleteButton({ classItem, onSuccess }: ClassDeleteButtonProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleDelete = async () => {
    setLoading(true)

    try {
      const response = await fetch(`/api/classes/${classItem.id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete class')
      }

      toast({
        title: "Success",
        description: "Class removed successfully",
      })
      
      setOpen(false)
      
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete class. Please try again.",
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
        <Trash2 className="h-4 w-4 text-red-500" />
      </Button>
      
      <AlertDialog open={open} onOpenChange={setOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will remove <strong>{classItem.name}</strong> from your class list.
              Any students enrolled in this class will need to be reassigned.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={loading}
              className="bg-red-600 hover:bg-red-700"
            >
              {loading ? 'Deleting...' : 'Delete Class'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}