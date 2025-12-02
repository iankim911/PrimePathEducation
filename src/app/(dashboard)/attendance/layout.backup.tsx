/**
 * Attendance Page Layout
 * 
 * Provides specific navigation configuration for the attendance page
 * including back button and breadcrumbs.
 */

import { ReactNode } from 'react'
import { DashboardShell } from '@/components/layout/DashboardShell'

export default function AttendanceLayout({ children }: { children: ReactNode }) {
  return (
    <DashboardShell 
      pageHeader={{
        title: 'Attendance',
        subtitle: 'Take daily attendance for your classes',
        backButton: {
          href: '/',
          label: 'Back to Dashboard'
        },
        breadcrumbs: [
          { label: 'Dashboard', href: '/' },
          { label: 'Attendance', isActive: true }
        ]
      }}
    >
      {children}
    </DashboardShell>
  )
}