"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'
import { AlertCircle } from 'lucide-react'
import type { CurriculumSettings } from '@/lib/services/curriculum'

interface CurriculumSettingsProps {
  onSettingsChange?: (settings: CurriculumSettings) => void
}

export function CurriculumSettingsComponent({ onSettingsChange }: CurriculumSettingsProps) {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [needsInit, setNeedsInit] = useState(false)
  const [initializing, setInitializing] = useState(false)
  const { toast } = useToast()
  
  const [formData, setFormData] = useState({
    max_depth: 3,
    level_1_name: 'Program',
    level_2_name: 'Track',
    level_3_name: 'Level',
    level_4_name: 'Section'
  })

  const checkInitialization = async () => {
    try {
      const response = await fetch('/api/curriculum/init')
      const data = await response.json()
      
      if (!data.initialized) {
        setNeedsInit(true)
      }
      return data.initialized
    } catch (error) {
      console.error('Error checking initialization:', error)
      setNeedsInit(true)
      return false
    }
  }

  const initializeCurriculum = async () => {
    setInitializing(true)
    try {
      const response = await fetch('/api/curriculum/init', {
        method: 'POST'
      })
      
      if (response.ok) {
        toast({
          title: "Success!",
          description: "Curriculum system initialized successfully",
        })
        setNeedsInit(false)
        // Reload settings after initialization
        await fetchSettings()
      } else {
        throw new Error('Failed to initialize curriculum')
      }
    } catch (error) {
      console.error('Error initializing curriculum:', error)
      toast({
        title: "Error",
        description: "Failed to initialize curriculum system. Please contact support.",
        variant: "destructive",
      })
    } finally {
      setInitializing(false)
    }
  }

  const fetchSettings = async () => {
    try {
      // First check if curriculum is initialized
      const isInitialized = await checkInitialization()
      
      if (!isInitialized) {
        setLoading(false)
        return
      }
      
      const response = await fetch('/api/curriculum/settings')
      const data = await response.json()
      
      if (data.settings) {
        setFormData({
          max_depth: data.settings.max_depth,
          level_1_name: data.settings.level_1_name,
          level_2_name: data.settings.level_2_name,
          level_3_name: data.settings.level_3_name,
          level_4_name: data.settings.level_4_name,
        })
      }
    } catch (error) {
      console.error('Error fetching curriculum settings:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSettings()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)

    try {
      const response = await fetch('/api/curriculum/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        throw new Error('Failed to save curriculum settings')
      }

      const data = await response.json()
      
      toast({
        title: "Success!",
        description: "Curriculum settings saved successfully",
      })

      if (onSettingsChange && data.settings) {
        onSettingsChange(data.settings)
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save curriculum settings. Please try again.",
        variant: "destructive",
      })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-gray-900">Curriculum Configuration</CardTitle>
          <CardDescription className="text-gray-600">
            Loading curriculum settings...
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }
  
  if (needsInit) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-gray-900">Curriculum Configuration</CardTitle>
          <CardDescription className="text-gray-600">
            Configure your academy's curriculum structure. (Database setup required for persistence)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-6">
            <div className="flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div className="text-sm">
                <p className="text-yellow-800 font-medium mb-2">Database Setup Required</p>
                <p className="text-yellow-700">
                  Settings will be temporary until database tables are created. 
                  Run the SQL script in Supabase Dashboard → SQL Editor to enable persistence.
                </p>
              </div>
            </div>
          </div>
          
          {/* Show the configuration form even without database tables */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Depth Selection */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="max_depth" className="text-right font-medium text-gray-900">
                Levels Needed*
              </Label>
              <Select
                value={formData.max_depth.toString()}
                onValueChange={(value) => setFormData({ ...formData, max_depth: parseInt(value) })}
              >
                <SelectTrigger className="col-span-3 text-gray-900">
                  <SelectValue placeholder="How many curriculum levels?" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="1" className="text-gray-900">1 Level (Simple)</SelectItem>
                  <SelectItem value="2" className="text-gray-900">2 Levels (Category → Level)</SelectItem>
                  <SelectItem value="3" className="text-gray-900">3 Levels (Program → Track → Level)</SelectItem>
                  <SelectItem value="4" className="text-gray-900">4 Levels (Full Hierarchy)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Level Name Configuration */}
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-900">Level Names</h4>
              <p className="text-sm text-gray-600">
                Customize what to call each level in your curriculum hierarchy.
              </p>

              {/* Level 1 - Always shown */}
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="level_1_name" className="text-right text-gray-900">
                  Level 1 Name*
                </Label>
                <Input
                  id="level_1_name"
                  value={formData.level_1_name}
                  onChange={(e) => setFormData({ ...formData, level_1_name: e.target.value })}
                  className="col-span-3"
                  placeholder="Program, Department, Category..."
                  required
                />
              </div>

              {/* Level 2 - Show if max_depth >= 2 */}
              {formData.max_depth >= 2 && (
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="level_2_name" className="text-right text-gray-900">
                    Level 2 Name*
                  </Label>
                  <Input
                    id="level_2_name"
                    value={formData.level_2_name}
                    onChange={(e) => setFormData({ ...formData, level_2_name: e.target.value })}
                    className="col-span-3"
                    placeholder="Track, Focus Area, Sub-Category..."
                    required
                  />
                </div>
              )}

              {/* Level 3 - Show if max_depth >= 3 */}
              {formData.max_depth >= 3 && (
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="level_3_name" className="text-right text-gray-900">
                    Level 3 Name*
                  </Label>
                  <Input
                    id="level_3_name"
                    value={formData.level_3_name}
                    onChange={(e) => setFormData({ ...formData, level_3_name: e.target.value })}
                    className="col-span-3"
                    placeholder="Level, Grade, Difficulty..."
                    required
                  />
                </div>
              )}

              {/* Level 4 - Show if max_depth = 4 */}
              {formData.max_depth === 4 && (
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="level_4_name" className="text-right text-gray-900">
                    Level 4 Name*
                  </Label>
                  <Input
                    id="level_4_name"
                    value={formData.level_4_name}
                    onChange={(e) => setFormData({ ...formData, level_4_name: e.target.value })}
                    className="col-span-3"
                    placeholder="Section, Class, Sub-Level..."
                    required
                  />
                </div>
              )}
            </div>

            {/* Example Structure */}
            <div className="space-y-3 pt-4 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-900">Example Structure</h4>
              <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg border border-gray-200">
                <div className="space-y-1">
                  <div>{formData.level_1_name} (e.g., "Elementary English")</div>
                  {formData.max_depth >= 2 && (
                    <div className="ml-4">├── {formData.level_2_name} (e.g., "Speaking Focus")</div>
                  )}
                  {formData.max_depth >= 3 && (
                    <div className="ml-8">├── {formData.level_3_name} (e.g., "Beginner")</div>
                  )}
                  {formData.max_depth === 4 && (
                    <div className="ml-12">├── {formData.level_4_name} (e.g., "Section A")</div>
                  )}
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end pt-4 border-t border-gray-200">
              <Button 
                type="submit" 
                disabled={saving}
                className="bg-gray-900 hover:bg-gray-800 text-white"
              >
                {saving ? 'Saving...' : 'Save Configuration'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-gray-900">Curriculum Configuration</CardTitle>
        <CardDescription className="text-gray-600">
          Configure your academy's curriculum structure. Choose how many levels you need (1-4) 
          and customize the names for each level to match your educational programs.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Depth Selection */}
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="max_depth" className="text-right font-medium text-gray-900">
              Levels Needed*
            </Label>
            <Select
              value={formData.max_depth.toString()}
              onValueChange={(value) => setFormData({ ...formData, max_depth: parseInt(value) })}
            >
              <SelectTrigger className="col-span-3 text-gray-900">
                <SelectValue placeholder="How many curriculum levels?" />
              </SelectTrigger>
              <SelectContent className="bg-white">
                <SelectItem value="1" className="text-gray-900">1 Level (Simple)</SelectItem>
                <SelectItem value="2" className="text-gray-900">2 Levels (Category → Level)</SelectItem>
                <SelectItem value="3" className="text-gray-900">3 Levels (Program → Track → Level)</SelectItem>
                <SelectItem value="4" className="text-gray-900">4 Levels (Full Hierarchy)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Level Name Configuration */}
          <div className="space-y-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900">Level Names</h4>
            <p className="text-sm text-gray-600">
              Customize what to call each level in your curriculum hierarchy.
            </p>

            {/* Level 1 - Always shown */}
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="level_1_name" className="text-right text-gray-900">
                Level 1 Name*
              </Label>
              <Input
                id="level_1_name"
                value={formData.level_1_name}
                onChange={(e) => setFormData({ ...formData, level_1_name: e.target.value })}
                className="col-span-3"
                placeholder="Program, Department, Category..."
                required
              />
            </div>

            {/* Level 2 - Show if max_depth >= 2 */}
            {formData.max_depth >= 2 && (
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="level_2_name" className="text-right text-gray-900">
                  Level 2 Name*
                </Label>
                <Input
                  id="level_2_name"
                  value={formData.level_2_name}
                  onChange={(e) => setFormData({ ...formData, level_2_name: e.target.value })}
                  className="col-span-3"
                  placeholder="Track, Focus Area, Sub-Category..."
                  required
                />
              </div>
            )}

            {/* Level 3 - Show if max_depth >= 3 */}
            {formData.max_depth >= 3 && (
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="level_3_name" className="text-right text-gray-900">
                  Level 3 Name*
                </Label>
                <Input
                  id="level_3_name"
                  value={formData.level_3_name}
                  onChange={(e) => setFormData({ ...formData, level_3_name: e.target.value })}
                  className="col-span-3"
                  placeholder="Level, Grade, Difficulty..."
                  required
                />
              </div>
            )}

            {/* Level 4 - Show if max_depth = 4 */}
            {formData.max_depth === 4 && (
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="level_4_name" className="text-right text-gray-900">
                  Level 4 Name*
                </Label>
                <Input
                  id="level_4_name"
                  value={formData.level_4_name}
                  onChange={(e) => setFormData({ ...formData, level_4_name: e.target.value })}
                  className="col-span-3"
                  placeholder="Section, Class, Sub-Level..."
                  required
                />
              </div>
            )}
          </div>

          {/* Example Structure */}
          <div className="space-y-3 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900">Example Structure</h4>
            <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg border border-gray-200">
              <div className="space-y-1">
                <div>{formData.level_1_name} (e.g., "Elementary English")</div>
                {formData.max_depth >= 2 && (
                  <div className="ml-4">├── {formData.level_2_name} (e.g., "Speaking Focus")</div>
                )}
                {formData.max_depth >= 3 && (
                  <div className="ml-8">├── {formData.level_3_name} (e.g., "Beginner")</div>
                )}
                {formData.max_depth === 4 && (
                  <div className="ml-12">├── {formData.level_4_name} (e.g., "Section A")</div>
                )}
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-4 border-t border-gray-200">
            <Button 
              type="submit" 
              disabled={saving}
              className="bg-gray-900 hover:bg-gray-800 text-white"
            >
              {saving ? 'Saving...' : 'Save Configuration'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}