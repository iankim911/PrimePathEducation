"use client"

import { useEffect, useState, useMemo } from 'react'
import { TestsTable } from '@/components/features/tests/TestsTable'
import { ExamWizard } from '@/components/features/tests/ExamWizard'
import type { Exam } from '@/lib/services/exams'
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

export default function TestsPage() {
  const [exams, setExams] = useState<Exam[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const fetchExams = async () => {
    try {
      const response = await fetch('/api/exams')
      if (!response.ok) {
        throw new Error('Failed to fetch exams')
      }
      const data = await response.json()
      setExams(data.exams)
    } catch (error) {
      console.error('Error fetching exams:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchExams()
  }, [])

  // Filter exams based on search and filters
  const filteredExams = useMemo(() => {
    return exams.filter(exam => {
      // Search filter
      const searchLower = searchTerm.toLowerCase()
      const matchesSearch = !searchTerm || 
        exam.title.toLowerCase().includes(searchLower) ||
        (exam.description && exam.description.toLowerCase().includes(searchLower)) ||
        (exam.subject_tags && exam.subject_tags.some(tag => tag.toLowerCase().includes(searchLower)))

      // Status filter
      const matchesStatus = statusFilter === 'all' || 
        (statusFilter === 'active' && exam.is_active) ||
        (statusFilter === 'inactive' && !exam.is_active)

      return matchesSearch && matchesStatus
    })
  }, [exams, searchTerm, statusFilter])

  const clearFilters = () => {
    setSearchTerm('')
    setStatusFilter('all')
  }

  const hasActiveFilters = searchTerm || statusFilter !== 'all'

  return (
    <div className="p-6">
      {/* Page Header with Add Button */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Tests & Exams</h2>
          <p className="mt-1 text-sm text-gray-600">
            Manage exams, questions, and assessment sessions
          </p>
        </div>
        <ExamWizard onSuccess={fetchExams} />
      </div>

      {/* Search and Filter Bar */}
      <div className="mb-6 space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search exams by title, description, or subject..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 text-gray-900 placeholder:text-gray-500"
            />
          </div>

          {/* Status Filter */}
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-full sm:w-[180px] text-gray-900">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              <SelectItem value="all" className="text-gray-900">All Status</SelectItem>
              <SelectItem value="active" className="text-gray-900">Active</SelectItem>
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
            Showing {filteredExams.length} of {exams.length} exams
          </div>
        )}
      </div>

      {/* Exams Table or Loading State */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
        </div>
      ) : (
        <TestsTable exams={filteredExams} onRefresh={fetchExams} />
      )}
    </div>
  )
}