'use client'

import { ChevronRight, Home } from 'lucide-react'

interface BreadcrumbItem {
  label: string
  href?: string
  isActive?: boolean
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[]
  showHome?: boolean
  className?: string
}

/**
 * Breadcrumbs Component
 * 
 * Provides visual navigation path showing current location.
 * Compatible with existing href-based navigation pattern.
 * 
 * @param items - Array of breadcrumb items
 * @param showHome - Whether to show home icon for first item (defaults to true)
 * @param className - Optional additional CSS classes
 */
export function Breadcrumbs({ 
  items, 
  showHome = true, 
  className = "" 
}: BreadcrumbsProps) {
  if (!items || items.length === 0) {
    return null
  }

  const handleNavigation = (href: string) => {
    window.location.href = href
  }

  return (
    <nav className={`flex items-center space-x-2 text-sm text-gray-600 ${className}`} aria-label="Breadcrumb">
      {items.map((item, index) => {
        const isLast = index === items.length - 1
        const isFirst = index === 0
        
        return (
          <div key={index} className="flex items-center">
            {/* Show separator before all items except first */}
            {!isFirst && (
              <ChevronRight className="h-4 w-4 mx-1 text-gray-400" />
            )}
            
            {/* Breadcrumb item */}
            {item.href && !isLast ? (
              <button
                onClick={() => handleNavigation(item.href!)}
                className="flex items-center hover:text-gray-900 transition-colors"
              >
                {isFirst && showHome && (
                  <Home className="h-4 w-4 mr-1" />
                )}
                {item.label}
              </button>
            ) : (
              <span className={`flex items-center ${isLast ? 'text-gray-900 font-medium' : ''}`}>
                {isFirst && showHome && (
                  <Home className="h-4 w-4 mr-1" />
                )}
                {item.label}
              </span>
            )}
          </div>
        )
      })}
    </nav>
  )
}