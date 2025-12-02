"use client"

import { useEffect, useState } from 'react'
import { CurriculumSettingsComponent } from '@/components/features/curriculum/CurriculumSettings'
import { CurriculumTreeComponent } from '@/components/features/curriculum/CurriculumTree'
import { GradeConfigurationComponent } from '@/components/features/grades/GradeConfiguration'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Loader2, GraduationCap } from 'lucide-react'
import type { CurriculumSettings } from '@/lib/services/curriculum'

export default function CurriculumPage() {
  const [settings, setSettings] = useState<CurriculumSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<string>("settings")

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/curriculum/settings')
      if (!response.ok) {
        throw new Error('Failed to fetch curriculum settings')
      }
      const data = await response.json()
      setSettings(data.settings)
      
      // If settings exist, switch to structure tab
      if (data.settings) {
        setActiveTab("structure")
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

  const handleSettingsChange = (newSettings: CurriculumSettings) => {
    setSettings(newSettings)
    setActiveTab("structure")
  }

  const refreshTree = () => {
    // This will trigger a re-render of the CurriculumTree component
    // The tree component handles its own data fetching
    return
  }

  return (
    <div className="p-6">
      {/* Page Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <GraduationCap className="h-7 w-7 text-gray-900" />
          <h2 className="text-2xl font-bold text-gray-900">Curriculum Management</h2>
        </div>
        <p className="text-gray-600">
          Configure your academy's curriculum structure and manage educational programs
        </p>
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
        </div>
      ) : (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          {/* Tab Navigation */}
          <TabsList className="grid w-full grid-cols-3 max-w-[600px]">
            <TabsTrigger value="settings" className="text-gray-900">
              Configuration
            </TabsTrigger>
            <TabsTrigger 
              value="structure" 
              className="text-gray-900"
              disabled={!settings}
            >
              Structure
              {!settings && (
                <span className="ml-2 text-xs text-gray-500">(Configure first)</span>
              )}
            </TabsTrigger>
            <TabsTrigger value="grades" className="text-gray-900">
              Grade Settings
            </TabsTrigger>
          </TabsList>

          {/* Configuration Tab */}
          <TabsContent value="settings" className="space-y-6">
            <CurriculumSettingsComponent onSettingsChange={handleSettingsChange} />
          </TabsContent>

          {/* Structure Management Tab */}
          <TabsContent value="structure" className="space-y-6">
            <CurriculumTreeComponent settings={settings} onRefresh={refreshTree} />
          </TabsContent>

          {/* Grade Configuration Tab */}
          <TabsContent value="grades" className="space-y-6">
            <GradeConfigurationComponent />
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}