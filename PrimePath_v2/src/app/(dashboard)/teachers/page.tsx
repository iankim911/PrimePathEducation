"use client"

import { useEffect, useState } from 'react'
import { TeachersTable } from '@/components/features/teachers/TeachersTable'
import { TeacherForm } from '@/components/features/teachers/TeacherForm'
import type { Teacher } from '@/lib/services/teachers'
import { Loader2 } from 'lucide-react'

export default function TeachersPage() {
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [loading, setLoading] = useState(true)

  const fetchTeachers = async () => {
    try {
      const response = await fetch('/api/teachers')
      if (!response.ok) {
        throw new Error('Failed to fetch teachers')
      }
      const data = await response.json()
      setTeachers(data.teachers)
    } catch (error) {
      console.error('Error fetching teachers:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTeachers()
  }, [])

  return (
    <div className="p-6">
      {/* Page Header with Add Button */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Teachers</h2>
          <p className="mt-1 text-sm text-gray-600">
            Manage your academy's teaching staff
          </p>
        </div>
        <TeacherForm onSuccess={fetchTeachers} />
      </div>

      {/* Teachers Table or Loading State */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
        </div>
      ) : (
        <TeachersTable teachers={teachers} onRefresh={fetchTeachers} />
      )}
    </div>
  )
}