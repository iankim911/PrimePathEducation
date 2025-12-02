'use client'

import { BackButton } from './BackButton'
import { Breadcrumbs } from './Breadcrumbs'

interface BreadcrumbItem {
  label: string
  href?: string
  isActive?: boolean
}

interface PageHeaderProps {
  title: string
  subtitle?: string
  backButton?: {
    href: string
    label?: string
  }
  breadcrumbs?: BreadcrumbItem[]
  className?: string
  children?: React.ReactNode
}

/**
 * PageHeader Component
 * 
 * Unified header component combining title, breadcrumbs, and back navigation.
 * Provides consistent layout across all pages.
 * 
 * @param title - Main page title
 * @param subtitle - Optional subtitle/description
 * @param backButton - Optional back button configuration
 * @param breadcrumbs - Optional breadcrumb items
 * @param className - Optional additional CSS classes
 * @param children - Optional additional content (action buttons, etc.)
 */
export function PageHeader({
  title,
  subtitle,
  backButton,
  breadcrumbs,
  className = "",
  children
}: PageHeaderProps) {
  return (
    <div className={`mb-6 ${className}`}>
      {/* Breadcrumbs */}
      {breadcrumbs && breadcrumbs.length > 0 && (
        <div className="mb-3">
          <Breadcrumbs items={breadcrumbs} />
        </div>
      )}
      
      {/* Main header content */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex-1">
          {/* Back button + Title section */}
          <div className="flex items-center gap-3">
            {backButton && (
              <BackButton 
                href={backButton.href}
                label={backButton.label}
              />
            )}
            
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {title}
              </h1>
              {subtitle && (
                <p className="mt-1 text-sm text-gray-600">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
        </div>
        
        {/* Action buttons or additional content */}
        {children && (
          <div className="flex-shrink-0">
            {children}
          </div>
        )}
      </div>
    </div>
  )
}