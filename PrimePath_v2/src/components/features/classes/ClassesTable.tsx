"use client"

import type { ClassWithTeacher } from '@/lib/services/classes'
import { ClassEditForm } from './ClassEditForm'
import { ClassDeleteButton } from './ClassDeleteButton'

interface ClassesTableProps {
  classes: ClassWithTeacher[]
  onRefresh?: () => void
}

export function ClassesTable({ classes, onRefresh }: ClassesTableProps) {
  if (classes.length === 0) {
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
            d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
          />
        </svg>
        <h3 className="mt-2 text-sm font-semibold text-gray-900">No classes</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by creating your first class.
        </p>
      </div>
    )
  }

  // Helper to format grade display
  const formatGrade = (grade: number | null | undefined) => {
    if (!grade) return '-'
    if (grade <= 6) return `Grade ${grade}`
    if (grade <= 9) return `Middle ${grade - 6}`
    if (grade <= 12) return `High ${grade - 9}`
    return `Grade ${grade}`
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
              Class Name
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Level
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Target Grade
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Schedule
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Primary Teacher
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
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {classes.map((classItem) => (
            <tr key={classItem.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {classItem.name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {classItem.level_label || '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatGrade(classItem.target_grade)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {classItem.schedule_info || '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {classItem.primary_teacher?.full_name || '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    classItem.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {classItem.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div className="flex items-center gap-2">
                  <ClassEditForm classItem={classItem} onSuccess={onRefresh} />
                  <ClassDeleteButton classItem={classItem} onSuccess={onRefresh} />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}