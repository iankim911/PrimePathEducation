"use client"

import { useEffect, useState, useMemo } from 'react'
import { StudentsTable } from '@/components/features/students/StudentsTable'
import { StudentForm } from '@/components/features/students/StudentForm'
import type { Student } from '@/lib/services/students'
import { Loader2, Search, X } from 'lucide-react'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'

export default function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [gradeFilter, setGradeFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const fetchStudents = async () => {
    try {
      const response = await fetch('/api/students')
      if (!response.ok) {
        throw new Error('Failed to fetch students')
      }
      const data = await response.json()
      setStudents(data.students)
    } catch (error) {
      console.error('Error fetching students:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStudents()
  }, [])

  // Filter students based on search and filters
  const filteredStudents = useMemo(() => {
    return students.filter(student => {
      // Search filter
      const searchLower = searchTerm.toLowerCase()
      const matchesSearch = !searchTerm || 
        student.full_name.toLowerCase().includes(searchLower) ||
        (student.english_name && student.english_name.toLowerCase().includes(searchLower)) ||
        (student.parent_name && student.parent_name.toLowerCase().includes(searchLower)) ||
        (student.school_name && student.school_name.toLowerCase().includes(searchLower))

      // Grade filter
      const matchesGrade = gradeFilter === 'all' || 
        (student.grade && student.grade.toString() === gradeFilter)

      // Status filter
      const matchesStatus = statusFilter === 'all' || 
        student.status === statusFilter

      return matchesSearch && matchesGrade && matchesStatus
    })
  }, [students, searchTerm, gradeFilter, statusFilter])

  const clearFilters = () => {
    setSearchTerm('')
    setGradeFilter('all')
    setStatusFilter('all')
  }

  const hasActiveFilters = searchTerm || gradeFilter !== 'all' || statusFilter !== 'all'

  return (
    <div className="p-6">
      {/* Page Header with Add Button */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Students</h2>
          <p className="mt-1 text-sm text-gray-600">
            Manage student records and enrollment status
          </p>
        </div>
        <StudentForm onSuccess={fetchStudents} />
      </div>

      {/* Search and Filter Bar */}
      <div className="mb-6 space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search students, parents, or schools..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 text-gray-900 placeholder:text-gray-500"
            />
          </div>

          {/* Grade Filter */}
          <Select value={gradeFilter} onValueChange={setGradeFilter}>
            <SelectTrigger className="w-full sm:w-[180px] text-gray-900">
              <SelectValue placeholder="All Grades" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              <SelectItem value="all" className="text-gray-900">All Grades</SelectItem>
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

          {/* Status Filter */}
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-full sm:w-[180px] text-gray-900">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              <SelectItem value="all" className="text-gray-900">All Status</SelectItem>
              <SelectItem value="active" className="text-gray-900">Active</SelectItem>
              <SelectItem value="paused" className="text-gray-900">Paused</SelectItem>
              <SelectItem value="inactive" className="text-gray-900">Inactive</SelectItem>
            </SelectContent>
          </Select>

          {/* Clear Filters Button */}
          {hasActiveFilters && (
            <Button
              variant="outline"
              onClick={clearFilters}
              className="w-full sm:w-auto"
            >
              <X className="h-4 w-4 mr-2" />
              Clear
            </Button>
          )}
        </div>

        {/* Results Count */}
        {hasActiveFilters && (
          <div className="text-sm text-gray-600">
            Showing {filteredStudents.length} of {students.length} students
          </div>
        )}
      </div>

      {/* Students Table or Loading State */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
        </div>
      ) : (
        <StudentsTable students={filteredStudents} onRefresh={fetchStudents} />
      )}
    </div>
  )
}