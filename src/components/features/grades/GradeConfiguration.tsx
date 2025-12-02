"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Loader2, Plus, Trash2, Save, Settings } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { getAcademyId } from '@/lib/academyUtils'
import type { GradeConfiguration, GradeOption } from '@/types/grades'

interface GradeConfigurationProps {
  onConfigurationChange?: () => void
}

export function GradeConfigurationComponent({ onConfigurationChange }: GradeConfigurationProps) {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [configuration, setConfiguration] = useState<GradeConfiguration | null>(null)
  const [gradeOptions, setGradeOptions] = useState<GradeOption[]>([])
  const [newOptionLabel, setNewOptionLabel] = useState('')
  const [newOptionValue, setNewOptionValue] = useState('')
  const { toast } = useToast()

  useEffect(() => {
    loadGradeConfiguration()
  }, [])

  const loadGradeConfiguration = async () => {
    setLoading(true)
    try {
      const academyId = await getAcademyId()
      
      // Load configuration and options in parallel
      const [configResponse, optionsResponse] = await Promise.all([
        fetch(`/api/grades/configuration?academyId=${academyId}`),
        fetch(`/api/grades/options?academyId=${academyId}`)
      ])

      if (configResponse.ok) {
        const configData = await configResponse.json()
        setConfiguration(configData.configuration)
      }

      if (optionsResponse.ok) {
        const optionsData = await optionsResponse.json()
        setGradeOptions(optionsData.options)
      }

    } catch (error) {
      console.error('Error loading grade configuration:', error)
      toast({
        title: "Error",
        description: "Failed to load grade configuration",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const saveConfiguration = async () => {
    if (!configuration) return

    setSaving(true)
    try {
      const academyId = await getAcademyId()
      
      const response = await fetch('/api/grades/configuration', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          academyId,
          ...configuration
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to save configuration')
      }

      toast({
        title: "Success!",
        description: "Grade configuration saved successfully",
      })

      if (onConfigurationChange) {
        onConfigurationChange()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save configuration. Please try again.",
        variant: "destructive",
      })
    } finally {
      setSaving(false)
    }
  }

  const addGradeOption = async () => {
    if (!newOptionLabel.trim() || !newOptionValue.trim()) {
      toast({
        title: "Error",
        description: "Both grade label and value are required",
        variant: "destructive",
      })
      return
    }

    // Check for duplicate values
    if (gradeOptions.some(option => option.grade_value === parseInt(newOptionValue))) {
      toast({
        title: "Error",
        description: "A grade with this value already exists",
        variant: "destructive",
      })
      return
    }

    try {
      const academyId = await getAcademyId()
      
      const response = await fetch('/api/grades/options', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          academy_id: academyId,
          display_name: newOptionLabel.trim(),
          grade_value: parseInt(newOptionValue),
          sort_order: (Math.max(...gradeOptions.map(o => o.sort_order || 0), 0) + 10)
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to add grade option')
      }

      const data = await response.json()
      setGradeOptions([...gradeOptions, data.option])
      setNewOptionLabel('')
      setNewOptionValue('')

      toast({
        title: "Success!",
        description: "Grade option added successfully",
      })

      if (onConfigurationChange) {
        onConfigurationChange()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add grade option. Please try again.",
        variant: "destructive",
      })
    }
  }

  const updateGradeOption = async (optionId: string, updates: Partial<GradeOption>) => {
    try {
      const response = await fetch(`/api/grades/options/${optionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      })

      if (!response.ok) {
        throw new Error('Failed to update grade option')
      }

      setGradeOptions(gradeOptions.map(option => 
        option.id === optionId ? { ...option, ...updates } : option
      ))

      toast({
        title: "Success!",
        description: "Grade option updated successfully",
      })

      if (onConfigurationChange) {
        onConfigurationChange()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update grade option. Please try again.",
        variant: "destructive",
      })
    }
  }

  const deleteGradeOption = async (optionId: string) => {
    try {
      const response = await fetch(`/api/grades/options/${optionId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete grade option')
      }

      setGradeOptions(gradeOptions.filter(option => option.id !== optionId))

      toast({
        title: "Success!",
        description: "Grade option deleted successfully",
      })

      if (onConfigurationChange) {
        onConfigurationChange()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete grade option. Please try again.",
        variant: "destructive",
      })
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-3 mb-6">
        <Settings className="h-6 w-6 text-gray-900" />
        <div>
          <h3 className="text-xl font-semibold text-gray-900">Grade Configuration</h3>
          <p className="text-sm text-gray-600">
            Configure grade field labels and manage grade options
          </p>
        </div>
      </div>

      {/* Configuration Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Field Configuration</CardTitle>
          <CardDescription>
            Customize how grade fields appear throughout the system
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="field-label">Field Label</Label>
              <Input
                id="field-label"
                value={configuration?.field_label || ''}
                onChange={(e) => setConfiguration(config => config ? 
                  { ...config, field_label: e.target.value } : null
                )}
                placeholder="Target Grade"
                className="text-gray-900"
              />
              <p className="text-xs text-gray-500 mt-1">
                This will appear as the label for grade fields (e.g., "Target Grade", "School Year")
              </p>
            </div>
            <div>
              <Label htmlFor="all-grades-label">All Grades Label</Label>
              <Input
                id="all-grades-label"
                value={configuration?.all_grades_label || ''}
                onChange={(e) => setConfiguration(config => config ? 
                  { ...config, all_grades_label: e.target.value } : null
                )}
                placeholder="All Grades"
                className="text-gray-900"
              />
              <p className="text-xs text-gray-500 mt-1">
                Label for the "all grades" option in filters
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="show-all-option"
              checked={configuration?.show_all_option || false}
              onCheckedChange={(checked) => setConfiguration(config => config ? 
                { ...config, show_all_option: checked } : null
              )}
            />
            <Label htmlFor="show-all-option">Show "All Grades" option in filters</Label>
          </div>

          <Button 
            onClick={saveConfiguration} 
            disabled={saving || !configuration}
            className="bg-gray-900 hover:bg-gray-800 text-white"
          >
            {saving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Configuration
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Grade Options Management */}
      <Card>
        <CardHeader>
          <CardTitle>Grade Options</CardTitle>
          <CardDescription>
            Manage the available grade options that appear in dropdowns
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Add New Option */}
          <div className="border rounded-lg p-4 bg-gray-50">
            <h4 className="font-medium text-gray-900 mb-3">Add New Grade Option</h4>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <Label htmlFor="new-label">Display Name</Label>
                <Input
                  id="new-label"
                  value={newOptionLabel}
                  onChange={(e) => setNewOptionLabel(e.target.value)}
                  placeholder="Grade 1"
                  className="text-gray-900"
                />
              </div>
              <div>
                <Label htmlFor="new-value">Numeric Value</Label>
                <Input
                  id="new-value"
                  type="number"
                  value={newOptionValue}
                  onChange={(e) => setNewOptionValue(e.target.value)}
                  placeholder="1"
                  className="text-gray-900"
                />
              </div>
              <div className="flex items-end">
                <Button 
                  onClick={addGradeOption}
                  className="w-full bg-gray-900 hover:bg-gray-800 text-white"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Add Option
                </Button>
              </div>
            </div>
          </div>

          {/* Existing Options */}
          <div className="space-y-3">
            {gradeOptions.length > 0 ? (
              gradeOptions
                .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
                .map((option) => (
                  <div key={option.id} className="flex items-center gap-3 p-3 border rounded-lg">
                    <div className="flex-1 grid grid-cols-2 gap-3">
                      <div>
                        <Label className="text-xs text-gray-600">Display Name</Label>
                        <Input
                          value={option.display_name}
                          onChange={(e) => updateGradeOption(option.id, { display_name: e.target.value })}
                          className="text-gray-900"
                        />
                      </div>
                      <div>
                        <Label className="text-xs text-gray-600">Numeric Value</Label>
                        <Input
                          type="number"
                          value={option.grade_value || ''}
                          onChange={(e) => updateGradeOption(option.id, { 
                            grade_value: e.target.value ? parseInt(e.target.value) : undefined 
                          })}
                          className="text-gray-900"
                        />
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        Order: {option.sort_order}
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => deleteGradeOption(option.id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Settings className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No grade options configured yet</p>
                <p className="text-sm">Add your first grade option above to get started</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}