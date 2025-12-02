"use client"

import { useState, useEffect } from 'react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { getGradeDropdownItems, getGradeConfiguration } from '@/lib/services/grades'
import { getAcademyId } from '@/lib/academyUtils'
import type { GradeDropdownItem, GradeConfiguration } from '@/types/grades'

interface GradeSelectorProps {
  value: string
  onValueChange: (value: string) => void
  placeholder?: string
  includeAllOption?: boolean
  className?: string
  disabled?: boolean
  allowEmpty?: boolean // Allow clearing the selection
}

export function GradeSelector({
  value,
  onValueChange,
  placeholder,
  includeAllOption = true,
  className,
  disabled = false,
  allowEmpty = false
}: GradeSelectorProps) {
  const [gradeOptions, setGradeOptions] = useState<GradeDropdownItem[]>([])
  const [configuration, setConfiguration] = useState<GradeConfiguration | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadGradeOptions()
  }, [includeAllOption])

  const loadGradeOptions = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const academyId = await getAcademyId()
      
      // Load configuration and options in parallel
      const [config, options] = await Promise.all([
        getGradeConfiguration(academyId),
        getGradeDropdownItems(academyId, includeAllOption)
      ])
      
      setConfiguration(config)
      setGradeOptions(options)
      
      // If no configuration exists, we might be in a state where the database
      // hasn't been initialized yet with the grade system
      if (!config) {
        setError('Grade system not configured for this academy')
      }
      
    } catch (err) {
      console.error('Error loading grade options:', err)
      setError('Failed to load grade options')
      // Provide fallback options for backward compatibility
      provideFallbackOptions()
    } finally {
      setLoading(false)
    }
  }

  const provideFallbackOptions = () => {
    // Fallback to hardcoded options if database is not yet configured
    const fallbackOptions: GradeDropdownItem[] = []
    
    if (includeAllOption) {
      fallbackOptions.push({
        value: 'all',
        label: 'All Grades',
        sort_order: -1
      })
    }
    
    // Add standard grade options
    const standardGrades = [
      { value: 1, label: 'Grade 1' },
      { value: 2, label: 'Grade 2' },
      { value: 3, label: 'Grade 3' },
      { value: 4, label: 'Grade 4' },
      { value: 5, label: 'Grade 5' },
      { value: 6, label: 'Grade 6' },
      { value: 7, label: 'Middle 1' },
      { value: 8, label: 'Middle 2' },
      { value: 9, label: 'Middle 3' },
      { value: 10, label: 'High 1' },
      { value: 11, label: 'High 2' },
      { value: 12, label: 'High 3' }
    ]
    
    standardGrades.forEach((grade, index) => {
      fallbackOptions.push({
        value: grade.value.toString(),
        label: grade.label,
        grade_value: grade.value,
        sort_order: index * 10
      })
    })
    
    setGradeOptions(fallbackOptions)
    setConfiguration({
      id: 'fallback',
      academy_id: 'fallback',
      field_label: 'Target Grade',
      show_all_option: includeAllOption,
      all_grades_label: 'All Grades',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
  }

  const getPlaceholderText = () => {
    if (placeholder) return placeholder
    if (loading) return 'Loading...'
    if (error) return 'Error loading grades'
    if (configuration) {
      return `Select ${configuration.field_label.toLowerCase()}`
    }
    return 'Select grade'
  }

  const handleValueChange = (newValue: string) => {
    // Convert "clear" to empty string for clearing selection
    const finalValue = newValue === "clear" ? "" : newValue
    onValueChange(finalValue)
  }

  if (loading) {
    return (
      <Select disabled>
        <SelectTrigger className={className}>
          <SelectValue placeholder="Loading grades..." />
        </SelectTrigger>
      </Select>
    )
  }

  return (
    <Select 
      value={value} 
      onValueChange={handleValueChange}
      disabled={disabled}
    >
      <SelectTrigger className={className}>
        <SelectValue placeholder={getPlaceholderText()} />
      </SelectTrigger>
      <SelectContent className="bg-white">
        {/* Empty option for clearing selection */}
        {allowEmpty && (
          <SelectItem value="clear" className="text-gray-900">
            <span className="text-gray-500">Clear selection</span>
          </SelectItem>
        )}
        
        {/* Grade options */}
        {gradeOptions.map((option) => (
          <SelectItem 
            key={option.value} 
            value={option.value}
            className="text-gray-900"
          >
            {option.label}
          </SelectItem>
        ))}
        
        {/* Show error state */}
        {error && gradeOptions.length === 0 && (
          <SelectItem value="error" disabled className="text-gray-500">
            {error}
          </SelectItem>
        )}
      </SelectContent>
    </Select>
  )
}

/**
 * Hook to get grade configuration and options
 * Useful for components that need to display grade information
 */
export function useGradeSystem() {
  const [configuration, setConfiguration] = useState<GradeConfiguration | null>(null)
  const [options, setOptions] = useState<GradeDropdownItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadGradeSystem()
  }, [])

  const loadGradeSystem = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const academyId = await getAcademyId()
      
      const [config, gradeOptions] = await Promise.all([
        getGradeConfiguration(academyId),
        getGradeDropdownItems(academyId, true)
      ])
      
      setConfiguration(config)
      setOptions(gradeOptions)
    } catch (err) {
      console.error('Error loading grade system:', err)
      setError('Failed to load grade system')
    } finally {
      setLoading(false)
    }
  }

  const refreshGradeSystem = () => {
    loadGradeSystem()
  }

  return {
    configuration,
    options,
    loading,
    error,
    refreshGradeSystem
  }
}

/**
 * Utility component for displaying grade labels consistently
 */
interface GradeLabelProps {
  gradeValue: number | null | undefined
  fallbackFormat?: 'grade' | 'number' // How to format if display name not found
  className?: string
}

export function GradeLabel({ 
  gradeValue, 
  fallbackFormat = 'grade',
  className 
}: GradeLabelProps) {
  const [displayName, setDisplayName] = useState<string>('-')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDisplayName()
  }, [gradeValue])

  const loadDisplayName = async () => {
    if (!gradeValue) {
      setDisplayName('-')
      setLoading(false)
      return
    }

    setLoading(true)
    try {
      const academyId = await getAcademyId()
      const options = await getGradeDropdownItems(academyId, false)
      
      const option = options.find(opt => opt.grade_value === gradeValue)
      if (option) {
        setDisplayName(option.label)
      } else {
        // Fallback formatting
        if (fallbackFormat === 'grade') {
          setDisplayName(`Grade ${gradeValue}`)
        } else {
          setDisplayName(gradeValue.toString())
        }
      }
    } catch (error) {
      console.error('Error loading grade display name:', error)
      // Use fallback format
      if (fallbackFormat === 'grade') {
        setDisplayName(`Grade ${gradeValue}`)
      } else {
        setDisplayName(gradeValue.toString())
      }
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <span className={className}>...</span>
  }

  return <span className={className}>{displayName}</span>
}