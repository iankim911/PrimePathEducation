"use client"

import { useEffect, useState } from 'react'
import { ClassesTable } from '@/components/features/classes/ClassesTable'
import { ClassForm } from '@/components/features/classes/ClassForm'
import type { ClassWithTeacher } from '@/lib/services/classes'
import { Loader2 } from 'lucide-react'

export default function ClassesPage() {
  const [classes, setClasses] = useState<ClassWithTeacher[]>([])
  const [loading, setLoading] = useState(true)

  const fetchClasses = async () => {
    try {
      const response = await fetch('/api/classes')
      if (!response.ok) {
        throw new Error('Failed to fetch classes')
      }
      const data = await response.json()
      setClasses(data.classes)
    } catch (error) {
      console.error('Error fetching classes:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchClasses()
  }, [])

  return (
    <div className="p-6">
      {/* Page Header with Add Button */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Classes</h2>
          <p className="mt-1 text-sm text-gray-600">
            Manage your academy's class schedule and levels
          </p>
        </div>
        <ClassForm onSuccess={fetchClasses} />
      </div>

      {/* Classes Table or Loading State */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
        </div>
      ) : (
        <ClassesTable classes={classes} onRefresh={fetchClasses} />
      )}
    </div>
  )
}