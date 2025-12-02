"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
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
import type { TeacherWithWorkload } from '@/lib/services/teachers'
import { TeacherEditModal } from './TeacherEditModal'

interface TeachersTableProps {
  teachers: TeacherWithWorkload[]
  onRefresh: () => void
}

export function TeachersTable({ teachers, onRefresh }: TeachersTableProps) {
  const [deleteTeacherId, setDeleteTeacherId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleDelete = async (teacherId: string) => {
    setLoading(true)

    try {
      const response = await fetch(`/api/teachers/${teacherId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete teacher')
      }

      toast({
        title: "Success!",
        description: "Teacher removed successfully",
      })

      setDeleteTeacherId(null)
      onRefresh()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete teacher. Please try again.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="rounded-md border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="font-medium">Name</TableHead>
              <TableHead className="font-medium">Email</TableHead>
              <TableHead className="font-medium">Classes Assigned</TableHead>
              <TableHead className="font-medium">Total Students</TableHead>
              <TableHead className="font-medium">Status</TableHead>
              <TableHead className="font-medium w-24">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {teachers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center text-gray-500">
                  No teachers found
                </TableCell>
              </TableRow>
            ) : (
              teachers.map((teacher) => (
                <TableRow key={teacher.id}>
                  <TableCell className="font-medium text-gray-900">
                    {teacher.full_name}
                  </TableCell>
                  <TableCell className="text-gray-600">
                    {teacher.email}
                  </TableCell>
                  <TableCell className="text-gray-600">
                    <div className="space-y-1">
                      {teacher.class_count > 0 ? (
                        <>
                          <div className="text-sm font-medium">
                            {teacher.class_count} {teacher.class_count === 1 ? 'class' : 'classes'}
                          </div>
                          <div className="text-xs text-gray-500">
                            {teacher.classes.slice(0, 2).map(assignment => assignment.class.name).join(', ')}
                            {teacher.classes.length > 2 && ` +${teacher.classes.length - 2} more`}
                          </div>
                        </>
                      ) : (
                        <span className="text-sm text-gray-400">No classes assigned</span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-gray-600">
                    <span className="text-sm">
                      {teacher.student_count} {teacher.student_count === 1 ? 'student' : 'students'}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant={teacher.is_active ? "default" : "secondary"}
                      className={teacher.is_active ? "bg-green-100 text-green-800 hover:bg-green-200" : ""}
                    >
                      {teacher.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <TeacherEditModal teacher={teacher} onSuccess={onRefresh} />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setDeleteTeacherId(teacher.id)}
                        className="border-gray-300 hover:bg-red-50 text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog 
        open={deleteTeacherId !== null} 
        onOpenChange={(open) => !open && setDeleteTeacherId(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Teacher</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this teacher? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteTeacherId && handleDelete(deleteTeacherId)}
              disabled={loading}
              className="bg-red-600 hover:bg-red-700"
            >
              {loading ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}