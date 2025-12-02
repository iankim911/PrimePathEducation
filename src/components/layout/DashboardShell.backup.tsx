/**
 * DashboardShell Component
 * 
 * This is a shared layout component for all dashboard pages.
 * The (dashboard)/layout.tsx file should be as thin as possible and delegate layout to this component.
 * This provides consistent navigation, header, and container structure across all dashboard pages.
 */

import { ReactNode } from 'react'

interface DashboardShellProps {
  children: ReactNode
}

export function DashboardShell({ children }: DashboardShellProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-semibold text-gray-900">
              PrimePath LMS Dashboard
            </h1>
            
            {/* Navigation */}
            <nav className="flex items-center space-x-4">
              <a 
                href="/students" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                Students
              </a>
              <a 
                href="/classes" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                Classes
              </a>
              <a 
                href="/curriculum" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                Curriculum
              </a>
              <a 
                href="/teachers" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                Teachers
              </a>
              <a 
                href="/enrollments" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                Class Assignments
              </a>
              <a 
                href="/attendance" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
              >
                Attendance
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white shadow-sm rounded-lg">
          {children}
        </div>
      </main>
    </div>
  )
}