"use client"

import { useEffect, useState } from 'react'
import { EnrollmentsList } from '@/components/features/enrollments/EnrollmentsList'
import { EnrollmentForm } from '@/components/features/enrollments/EnrollmentForm'
import type { EnrollmentWithRelations } from '@/lib/services/enrollments'
import { Loader2 } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function EnrollmentsPage() {
  const [enrollments, setEnrollments] = useState<EnrollmentWithRelations[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'all' | 'by-class' | 'by-student'>('all')

  const fetchEnrollments = async () => {
    try {
      const response = await fetch('/api/enrollments')
      if (!response.ok) {
        throw new Error('Failed to fetch enrollments')
      }
      const data = await response.json()
      setEnrollments(data.enrollments)
    } catch (error) {
      console.error('Error fetching enrollments:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEnrollments()
  }, [])

  return (
    <div className="p-6">
      {/* Page Header with Add Button */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Enrollments</h2>
          <p className="mt-1 text-sm text-gray-600">
            Manage student class assignments
          </p>
        </div>
        <EnrollmentForm onSuccess={fetchEnrollments} />
      </div>

      {/* View Tabs */}
      <Tabs defaultValue="all" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="all">All Enrollments</TabsTrigger>
          <TabsTrigger value="by-class">By Class</TabsTrigger>
          <TabsTrigger value="by-student">By Student</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
            </div>
          ) : (
            <EnrollmentsList 
              enrollments={enrollments} 
              onRefresh={fetchEnrollments}
              viewMode="all"
            />
          )}
        </TabsContent>

        <TabsContent value="by-class">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
            </div>
          ) : (
            <EnrollmentsList 
              enrollments={enrollments} 
              onRefresh={fetchEnrollments}
              viewMode="by-class"
            />
          )}
        </TabsContent>

        <TabsContent value="by-student">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
            </div>
          ) : (
            <EnrollmentsList 
              enrollments={enrollments} 
              onRefresh={fetchEnrollments}
              viewMode="by-student"
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}