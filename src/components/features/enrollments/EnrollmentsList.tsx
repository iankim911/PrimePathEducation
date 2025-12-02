"use client"

import type { EnrollmentWithRelations } from '@/lib/services/enrollments'
import { EnrollmentWithdrawButton } from './EnrollmentWithdrawButton'
import { Badge } from '@/components/ui/badge'

interface EnrollmentsListProps {
  enrollments: EnrollmentWithRelations[]
  onRefresh?: () => void
  viewMode: 'all' | 'by-class' | 'by-student'
}

export function EnrollmentsList({ enrollments, onRefresh, viewMode }: EnrollmentsListProps) {
  if (enrollments.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-semibold text-gray-900">No class assignments</h3>
        <p className="mt-1 text-sm text-gray-500">
          Start by assigning students to classes.
        </p>
      </div>
    )
  }

  // Group enrollments if needed
  if (viewMode === 'by-class') {
    const groupedByClass = enrollments.reduce((acc, enrollment) => {
      const className = enrollment.class?.name || 'Unknown Class'
      if (!acc[className]) {
        acc[className] = []
      }
      acc[className].push(enrollment)
      return acc
    }, {} as Record<string, EnrollmentWithRelations[]>)

    return (
      <div className="space-y-6">
        {Object.entries(groupedByClass).map(([className, classEnrollments]) => (
          <div key={className} className="bg-white shadow rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3">
              {className}
              <Badge className="ml-2 bg-gray-100 text-gray-800 hover:bg-gray-200">
                {classEnrollments.length} students
              </Badge>
            </h3>
            <div className="grid gap-2">
              {classEnrollments.map((enrollment) => (
                <div key={enrollment.id} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                  <div>
                    <span className="font-medium">
                      {enrollment.student?.english_name || enrollment.student?.full_name}
                    </span>
                    {enrollment.student?.grade && (
                      <span className="text-sm text-gray-500 ml-2">
                        Grade {enrollment.student.grade}
                      </span>
                    )}
                  </div>
                  <EnrollmentWithdrawButton 
                    enrollment={enrollment} 
                    onSuccess={onRefresh}
                  />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (viewMode === 'by-student') {
    const groupedByStudent = enrollments.reduce((acc, enrollment) => {
      const studentName = enrollment.student?.english_name || enrollment.student?.full_name || 'Unknown Student'
      if (!acc[studentName]) {
        acc[studentName] = []
      }
      acc[studentName].push(enrollment)
      return acc
    }, {} as Record<string, EnrollmentWithRelations[]>)

    return (
      <div className="space-y-6">
        {Object.entries(groupedByStudent).map(([studentName, studentEnrollments]) => (
          <div key={studentName} className="bg-white shadow rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3">
              {studentName}
              <Badge className="ml-2 bg-gray-100 text-gray-800 hover:bg-gray-200">
                {studentEnrollments.length} classes
              </Badge>
            </h3>
            <div className="grid gap-2">
              {studentEnrollments.map((enrollment) => (
                <div key={enrollment.id} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                  <div>
                    <span className="font-medium">
                      {enrollment.class?.name}
                    </span>
                    {enrollment.class?.schedule_info && (
                      <span className="text-sm text-gray-500 ml-2">
                        {enrollment.class.schedule_info}
                      </span>
                    )}
                  </div>
                  <EnrollmentWithdrawButton 
                    enrollment={enrollment} 
                    onSuccess={onRefresh}
                  />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    )
  }

  // Default "all" view - simple table
  return (
    <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Student
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Class
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Schedule
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Start Date
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {enrollments.map((enrollment) => (
            <tr key={enrollment.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {enrollment.student?.english_name || enrollment.student?.full_name}
                {enrollment.student?.grade && (
                  <span className="text-gray-500 ml-2">
                    (Grade {enrollment.student.grade})
                  </span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {enrollment.class?.name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {enrollment.class?.schedule_info || '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {enrollment.start_date}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <EnrollmentWithdrawButton 
                  enrollment={enrollment} 
                  onSuccess={onRefresh}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}