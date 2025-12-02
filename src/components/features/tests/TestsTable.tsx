"use client"

import { useState } from 'react'
import { type Exam } from '@/lib/services/exams'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  Play, 
  FileText, 
  Users,
  Clock,
  HelpCircle
} from 'lucide-react'

interface TestsTableProps {
  exams: Exam[]
  onRefresh: () => void
}

export function TestsTable({ exams, onRefresh }: TestsTableProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleDelete = async (examId: string) => {
    if (!confirm('Are you sure you want to delete this exam? This action cannot be undone.')) {
      return
    }

    setDeletingId(examId)
    try {
      const response = await fetch(`/api/exams/${examId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete exam')
      }

      onRefresh()
    } catch (error) {
      console.error('Error deleting exam:', error)
      alert('Failed to delete exam. Please try again.')
    } finally {
      setDeletingId(null)
    }
  }

  const formatDuration = (minutes?: number | null) => {
    if (!minutes) return 'No limit'
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString()
  }

  if (exams.length === 0) {
    return (
      <div className="text-center py-12">
        <FileText className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No exams</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by creating your first exam.
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Exam Title</TableHead>
            <TableHead>Subject</TableHead>
            <TableHead>Questions</TableHead>
            <TableHead>Duration</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Created</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {exams.map((exam) => (
            <TableRow key={exam.id} className="hover:bg-gray-50">
              <TableCell className="font-medium">
                <div className="space-y-1">
                  <div className="text-gray-900">{exam.title}</div>
                  {exam.description && (
                    <div className="text-sm text-gray-500 line-clamp-1">
                      {exam.description}
                    </div>
                  )}
                </div>
              </TableCell>
              <TableCell>
                {exam.subject_tags && exam.subject_tags.length > 0 ? (
                  <Badge variant="secondary" className="bg-gray-100 text-gray-800">
                    {exam.subject_tags[0]}
                  </Badge>
                ) : (
                  <span className="text-gray-400">-</span>
                )}
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1">
                  <HelpCircle className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-900">{exam.total_questions || 0}</span>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-900">{formatDuration(exam.time_limit_minutes)}</span>
                </div>
              </TableCell>
              <TableCell>
                <Badge 
                  variant={exam.is_active ? "default" : "secondary"}
                  className={exam.is_active ? "bg-green-100 text-green-800 hover:bg-green-100" : "bg-gray-100 text-gray-800"}
                >
                  {exam.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </TableCell>
              <TableCell className="text-gray-600">
                {formatDate(exam.created_at)}
              </TableCell>
              <TableCell className="text-right">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-white">
                    <DropdownMenuItem asChild>
                      <a 
                        href={`/tests/${exam.id}`}
                        className="flex items-center cursor-pointer"
                      >
                        <Edit className="mr-2 h-4 w-4" />
                        Edit Exam
                      </a>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <a 
                        href={`/tests/${exam.id}/questions`}
                        className="flex items-center cursor-pointer"
                      >
                        <HelpCircle className="mr-2 h-4 w-4" />
                        Manage Questions
                      </a>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <a 
                        href={`/tests/${exam.id}/sessions`}
                        className="flex items-center cursor-pointer"
                      >
                        <Play className="mr-2 h-4 w-4" />
                        Start Session
                      </a>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <a 
                        href={`/tests/${exam.id}/analytics`}
                        className="flex items-center cursor-pointer"
                      >
                        <Users className="mr-2 h-4 w-4" />
                        View Analytics
                      </a>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      className="text-red-600 focus:text-red-600"
                      onClick={() => handleDelete(exam.id)}
                      disabled={deletingId === exam.id}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      {deletingId === exam.id ? 'Deleting...' : 'Delete Exam'}
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}