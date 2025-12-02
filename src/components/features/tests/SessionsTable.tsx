"use client"

import { useState } from 'react'
import { type ExamSession } from '@/app/(dashboard)/tests/[id]/sessions/page'
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
  Calendar,
  Play,
  Users,
  Clock,
  Pause
} from 'lucide-react'

interface SessionsTableProps {
  sessions: ExamSession[]
  examId: string
  onRefresh: () => void
}

export function SessionsTable({ sessions, examId, onRefresh }: SessionsTableProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleDelete = async (sessionId: string) => {
    if (!confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
      return
    }

    setDeletingId(sessionId)
    try {
      const response = await fetch(`/api/exam-sessions/${sessionId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete session')
      }

      onRefresh()
    } catch (error) {
      console.error('Error deleting session:', error)
      alert('Failed to delete session. Please try again.')
    } finally {
      setDeletingId(null)
    }
  }

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800'
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'completed':
        return 'bg-gray-100 text-gray-600'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'scheduled':
        return <Calendar className="h-4 w-4 text-blue-500" />
      case 'active':
        return <Play className="h-4 w-4 text-green-500" />
      case 'completed':
        return <Clock className="h-4 w-4 text-gray-500" />
      case 'cancelled':
        return <Pause className="h-4 w-4 text-red-500" />
      default:
        return <Calendar className="h-4 w-4 text-gray-500" />
    }
  }

  const formatDateTime = (dateString?: string | null) => {
    if (!dateString) return 'Not set'
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatDuration = (minutes?: number | null) => {
    if (!minutes) return 'No limit'
    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`
  }

  if (sessions.length === 0) {
    return (
      <div className="text-center py-12">
        <Calendar className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No sessions</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by creating your first exam session.
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Session Title</TableHead>
            <TableHead>Class</TableHead>
            <TableHead>Scheduled</TableHead>
            <TableHead>Duration</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Students</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sessions.map((session) => (
            <TableRow key={session.id} className="hover:bg-gray-50">
              <TableCell className="font-medium">
                <div className="space-y-1">
                  <div className="text-gray-900">{session.title}</div>
                  {session.instructions && (
                    <div className="text-sm text-gray-500 line-clamp-1">
                      {session.instructions}
                    </div>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <span className="text-gray-900">Class {session.class_id.slice(-4)}</span>
              </TableCell>
              <TableCell>
                <div className="text-sm">
                  <div className="text-gray-900">{formatDateTime(session.scheduled_start)}</div>
                  {session.scheduled_end && (
                    <div className="text-gray-500">to {formatDateTime(session.scheduled_end)}</div>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-900">{formatDuration(session.time_limit_override)}</span>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  {getStatusIcon(session.status)}
                  <Badge 
                    variant="secondary" 
                    className={`${getStatusBadgeClass(session.status)} text-xs capitalize`}
                  >
                    {session.status}
                  </Badge>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1">
                  <Users className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-900">0 joined</span>
                </div>
              </TableCell>
              <TableCell className="text-right">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-white">
                    <DropdownMenuItem 
                      className="flex items-center cursor-pointer"
                      onClick={() => {
                        // TODO: Implement edit session functionality
                        console.log('Edit session:', session.id)
                      }}
                    >
                      <Edit className="mr-2 h-4 w-4" />
                      Edit Session
                    </DropdownMenuItem>
                    {session.status === 'scheduled' && (
                      <>
                        <DropdownMenuItem 
                          className="flex items-center cursor-pointer"
                          onClick={() => {
                            // TODO: Implement start session functionality
                            console.log('Start session:', session.id)
                          }}
                        >
                          <Play className="mr-2 h-4 w-4" />
                          Start Session
                        </DropdownMenuItem>
                      </>
                    )}
                    {session.status === 'active' && (
                      <DropdownMenuItem 
                        className="flex items-center cursor-pointer"
                        onClick={() => {
                          // TODO: Implement monitor session functionality
                          console.log('Monitor session:', session.id)
                        }}
                      >
                        <Users className="mr-2 h-4 w-4" />
                        Monitor Session
                      </DropdownMenuItem>
                    )}
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      className="text-red-600 focus:text-red-600 flex items-center cursor-pointer"
                      onClick={() => handleDelete(session.id)}
                      disabled={deletingId === session.id}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      {deletingId === session.id ? 'Deleting...' : 'Delete Session'}
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