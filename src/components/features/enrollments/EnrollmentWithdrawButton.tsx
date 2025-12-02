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
import { UserMinus } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import type { EnrollmentWithRelations } from '@/lib/services/enrollments'

interface EnrollmentWithdrawButtonProps {
  enrollment: EnrollmentWithRelations
  onSuccess?: () => void
}

export function EnrollmentWithdrawButton({ enrollment, onSuccess }: EnrollmentWithdrawButtonProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleWithdraw = async () => {
    setLoading(true)

    try {
      const response = await fetch(`/api/enrollments/${enrollment.id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to withdraw enrollment')
      }

      toast({
        title: "Success",
        description: "Student withdrawn from class",
      })
      
      setOpen(false)
      
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to withdraw student. Please try again.",
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
        className="border-gray-300 hover:bg-red-50 text-red-600 hover:text-red-700"
      >
        <UserMinus className="h-4 w-4" />
      </Button>
      
      <AlertDialog open={open} onOpenChange={setOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove Assignment?</AlertDialogTitle>
            <AlertDialogDescription>
              This will remove <strong>{enrollment.student?.english_name || enrollment.student?.full_name}</strong> from <strong>{enrollment.class?.name}</strong>.
              The student can be re-assigned later if needed.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleWithdraw}
              disabled={loading}
              className="bg-red-600 hover:bg-red-700"
            >
              {loading ? 'Removing...' : 'Remove Assignment'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}