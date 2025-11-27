/**
 * Dashboard Layout
 * 
 * Thin wrapper that delegates all layout concerns to DashboardShell component.
 * This keeps the app router layout file minimal and moves UI logic to components.
 */

import { ReactNode } from 'react'
import { DashboardShell } from '@/components/layout/DashboardShell'

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return <DashboardShell>{children}</DashboardShell>
}