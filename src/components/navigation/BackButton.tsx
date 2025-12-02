'use client'

import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface BackButtonProps {
  href: string
  label?: string
  className?: string
  variant?: 'default' | 'outline' | 'ghost'
}

/**
 * BackButton Component
 * 
 * Provides consistent back navigation with clear labeling.
 * Uses simple href navigation (compatible with existing codebase).
 * 
 * @param href - URL to navigate back to
 * @param label - Optional label text (defaults to "Back")
 * @param className - Optional additional CSS classes
 * @param variant - Button variant (defaults to "outline")
 */
export function BackButton({ 
  href, 
  label = "Back", 
  className = "",
  variant = "outline" 
}: BackButtonProps) {
  return (
    <Button
      variant={variant}
      className={`text-gray-600 hover:text-gray-900 ${className}`}
      onClick={() => {
        // Safe navigation using window.location (compatible with existing pattern)
        window.location.href = href
      }}
    >
      <ArrowLeft className="h-4 w-4 mr-2" />
      {label}
    </Button>
  )
}