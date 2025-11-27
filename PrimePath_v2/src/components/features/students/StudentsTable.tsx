"use client"

import type { Student } from '@/lib/services/students'
import { StudentEditForm } from './StudentEditForm'
import { StudentDeleteButton } from './StudentDeleteButton'

interface StudentsTableProps {
  students: Student[]
  onRefresh?: () => void
}

export function StudentsTable({ students, onRefresh }: StudentsTableProps) {
  if (students.length === 0) {
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
        <h3 className="mt-2 text-sm font-semibold text-gray-900">No students</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by creating your first student.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Student Name
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              English Name
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Grade
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              School
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Status
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Parent Contact
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {students.map((student) => (
            <tr key={student.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {student.full_name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {student.english_name || '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {student.grade ? `Grade ${student.grade}` : '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {student.school_name || '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    student.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : student.status === 'paused'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {student.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div>
                  <div>{student.parent_name || '-'}</div>
                  {student.parent_phone && (
                    <div className="text-xs text-gray-400">{student.parent_phone}</div>
                  )}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div className="flex items-center gap-2">
                  <StudentEditForm student={student} onSuccess={onRefresh} />
                  <StudentDeleteButton student={student} onSuccess={onRefresh} />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}