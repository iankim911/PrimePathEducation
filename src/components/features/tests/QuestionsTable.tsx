"use client"

import { useState } from 'react'
import { type ExamQuestion } from '@/lib/services/exams'
import { deleteQuestion as deleteQuestionService } from '@/lib/services/questions'
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
  HelpCircle,
  CheckSquare,
  FileText,
  MessageSquare,
  ToggleLeft
} from 'lucide-react'

interface QuestionsTableProps {
  questions: ExamQuestion[]
  examId: string
  onRefresh: () => void
}

export function QuestionsTable({ questions, examId, onRefresh }: QuestionsTableProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleDelete = async (questionId: string) => {
    if (!confirm('Are you sure you want to delete this question? This action cannot be undone.')) {
      return
    }

    setDeletingId(questionId)
    try {
      // Get academy ID - using same pattern as other components
      const academyId = 'default-academy-id' // This should be from context or props
      await deleteQuestionService(questionId, academyId)
      onRefresh()
    } catch (error) {
      console.error('Error deleting question:', error)
      alert('Failed to delete question. Please try again.')
    } finally {
      setDeletingId(null)
    }
  }

  const getQuestionTypeIcon = (type: string) => {
    switch (type) {
      case 'multiple_choice':
        return <CheckSquare className="h-4 w-4 text-blue-500" />
      case 'multiple_select':
        return <CheckSquare className="h-4 w-4 text-purple-500" />
      case 'short_answer':
        return <MessageSquare className="h-4 w-4 text-green-500" />
      case 'long_answer':
        return <FileText className="h-4 w-4 text-orange-500" />
      case 'true_false':
        return <ToggleLeft className="h-4 w-4 text-red-500" />
      default:
        return <HelpCircle className="h-4 w-4 text-gray-500" />
    }
  }

  const getQuestionTypeLabel = (type: string) => {
    switch (type) {
      case 'multiple_choice':
        return 'Multiple Choice'
      case 'multiple_select':
        return 'Multiple Select'
      case 'short_answer':
        return 'Short Answer'
      case 'long_answer':
        return 'Long Answer'
      case 'true_false':
        return 'True/False'
      default:
        return type
    }
  }

  const getQuestionTypeBadgeClass = (type: string) => {
    switch (type) {
      case 'multiple_choice':
        return 'bg-blue-100 text-blue-800'
      case 'multiple_select':
        return 'bg-purple-100 text-purple-800'
      case 'short_answer':
        return 'bg-green-100 text-green-800'
      case 'long_answer':
        return 'bg-orange-100 text-orange-800'
      case 'true_false':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const truncateText = (text: string, maxLength: number = 80) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  if (questions.length === 0) {
    return (
      <div className="text-center py-12">
        <HelpCircle className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No questions</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by creating your first question for this exam.
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-16">#</TableHead>
            <TableHead>Question Text</TableHead>
            <TableHead className="w-32">Type</TableHead>
            <TableHead className="w-20">Points</TableHead>
            <TableHead className="w-24">Required</TableHead>
            <TableHead className="text-right w-20">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {questions.map((question) => (
            <TableRow key={question.id} className="hover:bg-gray-50">
              <TableCell className="font-medium text-gray-900">
                {question.question_number}
              </TableCell>
              <TableCell>
                <div className="space-y-1">
                  <div className="text-gray-900 font-medium">
                    {truncateText(question.question_text)}
                  </div>
                  {question.instructions && (
                    <div className="text-sm text-gray-500">
                      {truncateText(question.instructions, 60)}
                    </div>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  {getQuestionTypeIcon(question.question_type)}
                  <Badge 
                    variant="secondary" 
                    className={`${getQuestionTypeBadgeClass(question.question_type)} text-xs`}
                  >
                    {getQuestionTypeLabel(question.question_type)}
                  </Badge>
                </div>
              </TableCell>
              <TableCell>
                <span className="text-gray-900 font-medium">
                  {question.points || 1}
                </span>
              </TableCell>
              <TableCell>
                <Badge 
                  variant="secondary"
                  className="bg-gray-100 text-gray-600"
                >
                  Question
                </Badge>
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
                        // TODO: Implement edit question functionality
                        console.log('Edit question:', question.id)
                      }}
                    >
                      <Edit className="mr-2 h-4 w-4" />
                      Edit Question
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      className="text-red-600 focus:text-red-600 flex items-center cursor-pointer"
                      onClick={() => handleDelete(question.id)}
                      disabled={deletingId === question.id}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      {deletingId === question.id ? 'Deleting...' : 'Delete Question'}
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