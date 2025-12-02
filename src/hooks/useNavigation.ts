'use client'

import { useMemo } from 'react'
import { usePathname } from 'next/navigation'

interface BreadcrumbItem {
  label: string
  href?: string
  isActive?: boolean
}

interface NavigationConfig {
  title: string
  subtitle?: string
  backButton?: {
    href: string
    label?: string
  }
  breadcrumbs?: BreadcrumbItem[]
}

/**
 * Navigation configuration for each route
 * Maps pathname to navigation settings
 */
const NAVIGATION_CONFIG: Record<string, NavigationConfig> = {
  // Dashboard pages
  '/students': {
    title: 'Students',
    subtitle: 'Manage student records and enrollment status',
    breadcrumbs: [
      { label: 'Dashboard', href: '/' },
      { label: 'Students', isActive: true }
    ]
  },
  '/classes': {
    title: 'Classes',
    subtitle: 'Manage class schedules and curriculum',
    breadcrumbs: [
      { label: 'Dashboard', href: '/' },
      { label: 'Classes', isActive: true }
    ]
  },
  '/teachers': {
    title: 'Teachers',
    subtitle: 'Manage instructor profiles and assignments',
    breadcrumbs: [
      { label: 'Dashboard', href: '/' },
      { label: 'Teachers', isActive: true }
    ]
  },
  '/curriculum': {
    title: 'Curriculum',
    subtitle: 'Manage curriculum structure and levels',
    breadcrumbs: [
      { label: 'Dashboard', href: '/' },
      { label: 'Curriculum', isActive: true }
    ]
  },
  '/tests': {
    title: 'Tests & Exams',
    subtitle: 'Manage exams, questions, and assessment sessions',
    breadcrumbs: [
      { label: 'Dashboard', href: '/' },
      { label: 'Tests', isActive: true }
    ]
  },
  '/enrollments': {
    title: 'Class Assignments',
    subtitle: 'Manage student-class enrollments',
    breadcrumbs: [
      { label: 'Dashboard', href: '/' },
      { label: 'Class Assignments', isActive: true }
    ]
  },
  '/attendance': {
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
  }
}

/**
 * useNavigation Hook
 * 
 * Provides navigation configuration for current route.
 * Returns title, breadcrumbs, and back button settings.
 * 
 * @param pathname - Current pathname (from usePathname or window.location.pathname)
 * @param customConfig - Optional custom configuration to override defaults
 */
export function useNavigation(
  pathname?: string, 
  customConfig?: Partial<NavigationConfig>
): NavigationConfig {
  const nextPathname = usePathname()
  const currentPath = pathname || nextPathname
  
  const navigationConfig = useMemo(() => {
    const baseConfig = NAVIGATION_CONFIG[currentPath] || {
      title: 'PrimePath LMS',
      breadcrumbs: [{ label: 'Dashboard', href: '/' }]
    }
    
    // Merge with custom config if provided
    if (customConfig) {
      return {
        ...baseConfig,
        ...customConfig,
        breadcrumbs: customConfig.breadcrumbs || baseConfig.breadcrumbs
      }
    }
    
    return baseConfig
  }, [currentPath, customConfig])
  
  return navigationConfig
}

/**
 * Helper function to get the current page's active nav item
 * Used for highlighting active navigation links
 */
export function getActiveNavItem(pathname?: string): string | null {
  const nextPathname = usePathname()
  const currentPath = pathname || nextPathname
  
  // Extract the main section from the path
  const sections = currentPath.split('/').filter(Boolean)
  return sections[0] || null
}