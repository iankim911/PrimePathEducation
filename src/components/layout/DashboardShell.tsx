/**
 * DashboardShell Component
 * 
 * This is a shared layout component for all dashboard pages.
 * The (dashboard)/layout.tsx file should be as thin as possible and delegate layout to this component.
 * This provides consistent navigation, header, and container structure across all dashboard pages.
 * 
 * Enhanced with:
 * - Active page highlighting
 * - Optional PageHeader integration
 * - Backward-compatible design (all new features are opt-in)
 */

'use client'

import { ReactNode } from 'react'
import { PageHeader } from '@/components/navigation/PageHeader'
import { getActiveNavItem } from '@/hooks/useNavigation'

interface BreadcrumbItem {
  label: string
  href?: string
  isActive?: boolean
}

interface DashboardShellProps {
  children: ReactNode
  // Optional navigation enhancements (backward compatible)
  pageHeader?: {
    title: string
    subtitle?: string
    backButton?: {
      href: string
      label?: string
    }
    breadcrumbs?: BreadcrumbItem[]
  }
}

export function DashboardShell({ children, pageHeader }: DashboardShellProps) {
  // Get current active page for highlighting
  const activeNavItem = getActiveNavItem()
  
  // Navigation items with active state detection
  const navItems = [
    { href: '/students', label: 'Students', key: 'students' },
    { href: '/classes', label: 'Classes', key: 'classes' },
    { href: '/curriculum', label: 'Curriculum', key: 'curriculum' },
    { href: '/teachers', label: 'Teachers', key: 'teachers' },
    { href: '/tests', label: 'Tests', key: 'tests' },
    { href: '/enrollments', label: 'Class Assignments', key: 'enrollments' },
    { href: '/attendance', label: 'Attendance', key: 'attendance' }
  ]

  const getNavItemClass = (itemKey: string) => {
    const isActive = activeNavItem === itemKey
    return isActive
      ? "bg-gray-900 text-white px-3 py-2 text-sm font-medium rounded-md"
      : "text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium rounded-md hover:bg-gray-100"
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-semibold text-gray-900">
              PrimePath LMS Dashboard
            </h1>
            
            {/* Enhanced Navigation with Active State */}
            <nav className="flex items-center space-x-1">
              {navItems.map((item) => (
                <a 
                  key={item.key}
                  href={item.href} 
                  className={getNavItemClass(item.key)}
                >
                  {item.label}
                </a>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white shadow-sm rounded-lg">
          {/* Optional PageHeader Integration */}
          {pageHeader && (
            <div className="p-6 border-b border-gray-200">
              <PageHeader
                title={pageHeader.title}
                subtitle={pageHeader.subtitle}
                backButton={pageHeader.backButton}
                breadcrumbs={pageHeader.breadcrumbs}
              />
            </div>
          )}
          
          {/* Page Content */}
          <div className={pageHeader ? "" : "p-6"}>
            {children}
          </div>
        </div>
      </main>
    </div>
  )
}