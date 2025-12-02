"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  Search, 
  User, 
  Clock, 
  Target, 
  CheckCircle2, 
  XCircle,
  MinusCircle,
  TrendingUp,
  TrendingDown,
  Eye
} from 'lucide-react'

interface StudentPerformance {
  student_id: string
  student_name: string
  attempts: number
  best_score: number
  latest_score: number
  total_time_minutes: number
  completion_date: string
  status: 'completed' | 'in_progress' | 'not_started'
}

interface StudentPerformanceTableProps {
  students: StudentPerformance[]
  examId: string
  passingScore?: number
}

export function StudentPerformanceTable({ students, examId, passingScore = 70 }: StudentPerformanceTableProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<string>('best_score_desc')

  // Filter and sort students
  const filteredStudents = students
    .filter(student => {
      const matchesSearch = student.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           student.student_id.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = statusFilter === 'all' || student.status === statusFilter
      return matchesSearch && matchesStatus
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name_asc':
          return a.student_name.localeCompare(b.student_name)
        case 'name_desc':
          return b.student_name.localeCompare(a.student_name)
        case 'best_score_asc':
          return a.best_score - b.best_score
        case 'best_score_desc':
          return b.best_score - a.best_score
        case 'latest_score_desc':
          return b.latest_score - a.latest_score
        case 'attempts_desc':
          return b.attempts - a.attempts
        case 'time_asc':
          return a.total_time_minutes - b.total_time_minutes
        case 'date_desc':
          return new Date(b.completion_date).getTime() - new Date(a.completion_date).getTime()
        default:
          return b.best_score - a.best_score
      }
    })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'in_progress':
        return <MinusCircle className="h-4 w-4 text-yellow-500" />
      case 'not_started':
        return <XCircle className="h-4 w-4 text-gray-400" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800'
      case 'not_started':
        return 'bg-gray-100 text-gray-600'
      default:
        return 'bg-gray-100 text-gray-600'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= passingScore) return 'text-green-600'
    if (score >= passingScore * 0.8) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getPerformanceTrend = (best: number, latest: number) => {
    if (latest > best * 1.05) return <TrendingUp className="h-4 w-4 text-green-500" />
    if (latest < best * 0.95) return <TrendingDown className="h-4 w-4 text-red-500" />
    return null
  }

  // Calculate statistics
  const stats = {
    total: students.length,
    completed: students.filter(s => s.status === 'completed').length,
    passed: students.filter(s => s.best_score >= passingScore).length,
    avgScore: students.length > 0 ? students.reduce((sum, s) => sum + s.best_score, 0) / students.length : 0,
    avgAttempts: students.length > 0 ? students.reduce((sum, s) => sum + s.attempts, 0) / students.length : 0
  }

  return (
    <div className="space-y-6">
      {/* Statistics */}
      <div className="grid grid-cols-5 gap-4">
        <Card className="bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <User className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-blue-600">Total Students</p>
                <p className="text-2xl font-bold text-blue-900">{stats.total}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-green-600">Completed</p>
                <p className="text-2xl font-bold text-green-900">{stats.completed}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-purple-600">Passed</p>
                <p className="text-2xl font-bold text-purple-900">{stats.passed}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-yellow-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-sm text-yellow-600">Avg Score</p>
                <p className="text-2xl font-bold text-yellow-900">{stats.avgScore.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-orange-600">Avg Attempts</p>
                <p className="text-2xl font-bold text-orange-900">{stats.avgAttempts.toFixed(1)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Controls */}
      <Card className="bg-white">
        <CardHeader>
          <CardTitle className="text-gray-900">Student Performance Details</CardTitle>
          <CardDescription>Individual student results and progress tracking</CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search by student name or ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 text-gray-900"
                />
              </div>
            </div>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent className="bg-white">
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="not_started">Not Started</SelectItem>
              </SelectContent>
            </Select>

            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent className="bg-white">
                <SelectItem value="best_score_desc">Best Score (High to Low)</SelectItem>
                <SelectItem value="best_score_asc">Best Score (Low to High)</SelectItem>
                <SelectItem value="latest_score_desc">Latest Score</SelectItem>
                <SelectItem value="name_asc">Name (A-Z)</SelectItem>
                <SelectItem value="name_desc">Name (Z-A)</SelectItem>
                <SelectItem value="attempts_desc">Most Attempts</SelectItem>
                <SelectItem value="time_asc">Least Time</SelectItem>
                <SelectItem value="date_desc">Most Recent</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Results Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Student</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Best Score</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Latest Score</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Attempts</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Total Time</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Last Activity</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredStudents.map((student) => (
                  <tr key={student.student_id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-3">
                        <User className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="font-medium text-gray-900">{student.student_name}</p>
                          <p className="text-sm text-gray-500">{student.student_id}</p>
                        </div>
                      </div>
                    </td>

                    <td className="py-3 px-4">
                      <Badge variant="secondary" className={getStatusColor(student.status)}>
                        <span className="mr-1">{getStatusIcon(student.status)}</span>
                        {student.status.replace('_', ' ')}
                      </Badge>
                    </td>

                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <span className={`font-semibold ${getScoreColor(student.best_score)}`}>
                          {student.best_score.toFixed(1)}%
                        </span>
                        {student.best_score >= passingScore && (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        )}
                      </div>
                    </td>

                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <span className={`font-medium ${getScoreColor(student.latest_score)}`}>
                          {student.latest_score.toFixed(1)}%
                        </span>
                        {getPerformanceTrend(student.best_score, student.latest_score)}
                      </div>
                    </td>

                    <td className="py-3 px-4">
                      <span className="font-medium text-gray-900">{student.attempts}</span>
                    </td>

                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-1">
                        <Clock className="h-4 w-4 text-gray-400" />
                        <span className="text-gray-700">{student.total_time_minutes}m</span>
                      </div>
                    </td>

                    <td className="py-3 px-4">
                      <span className="text-sm text-gray-600">
                        {new Date(student.completion_date).toLocaleDateString()}
                      </span>
                    </td>

                    <td className="py-3 px-4">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-1" />
                        View Details
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredStudents.length === 0 && (
              <div className="text-center py-8">
                <User className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Students Found</h3>
                <p className="text-gray-600">
                  {searchTerm || statusFilter !== 'all' 
                    ? 'Try adjusting your search criteria or filters.'
                    : 'No students have been assigned to this exam yet.'}
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}