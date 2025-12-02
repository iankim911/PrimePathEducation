"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { GradeSelector, useGradeSystem, GradeLabel } from './GradeSelector'

/**
 * Test component to verify grade system functionality
 * This can be temporarily added to any page to test the grade system
 */
export function GradeSystemTest() {
  const [selectedGrade, setSelectedGrade] = useState<string>('')
  const [testGradeValue, setTestGradeValue] = useState<number>(7)
  const { configuration, options, loading, error, refreshGradeSystem } = useGradeSystem()

  const handleInitializeSystem = async () => {
    try {
      const response = await fetch('/api/grades/configuration/initialize', {
        method: 'POST'
      })
      
      const data = await response.json()
      
      if (response.ok) {
        alert('Grade system initialized successfully!')
        refreshGradeSystem()
      } else {
        alert(`Error: ${data.error}`)
      }
    } catch (error) {
      console.error('Error initializing grade system:', error)
      alert('Failed to initialize grade system')
    }
  }

  const handleTestApiEndpoints = async () => {
    try {
      console.log('Testing API endpoints...')
      
      // Test configuration endpoint
      const configResponse = await fetch('/api/grades/configuration')
      const configData = await configResponse.json()
      console.log('Configuration:', configData)
      
      // Test options endpoint  
      const optionsResponse = await fetch('/api/grades/options')
      const optionsData = await optionsResponse.json()
      console.log('Options:', optionsData)
      
      // Test dropdown format
      const dropdownResponse = await fetch('/api/grades/options?format=dropdown&includeAll=true')
      const dropdownData = await dropdownResponse.json()
      console.log('Dropdown items:', dropdownData)
      
      alert('API tests completed - check console for results')
    } catch (error) {
      console.error('Error testing API endpoints:', error)
      alert('API test failed - check console')
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Grade System Test</CardTitle>
          <CardDescription>
            Test the new configurable grade system functionality
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          
          {/* System Status */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-medium mb-2">System Status</h3>
            {loading ? (
              <p className="text-yellow-600">Loading grade system...</p>
            ) : error ? (
              <p className="text-red-600">Error: {error}</p>
            ) : configuration ? (
              <div className="text-green-600">
                <p>✓ Configuration loaded</p>
                <p>✓ Field Label: "{configuration.field_label}"</p>
                <p>✓ Grade Options: {options.length} available</p>
                <p>✓ Show All Option: {configuration.show_all_option ? 'Yes' : 'No'}</p>
              </div>
            ) : (
              <p className="text-gray-600">No configuration found</p>
            )}
          </div>

          {/* Grade Selector Test */}
          <div className="space-y-2">
            <h3 className="font-medium">Grade Selector Component Test</h3>
            <div className="flex items-center gap-4">
              <div className="w-48">
                <GradeSelector
                  value={selectedGrade}
                  onValueChange={setSelectedGrade}
                  placeholder="Test grade selector"
                />
              </div>
              <div className="text-sm text-gray-600">
                Selected: {selectedGrade || 'None'}
              </div>
            </div>
          </div>

          {/* Grade Label Test */}
          <div className="space-y-2">
            <h3 className="font-medium">Grade Label Component Test</h3>
            <div className="flex items-center gap-4">
              <input
                type="number"
                value={testGradeValue}
                onChange={(e) => setTestGradeValue(parseInt(e.target.value) || 1)}
                min="1"
                max="12"
                className="w-20 px-2 py-1 border rounded"
              />
              <span>displays as:</span>
              <GradeLabel gradeValue={testGradeValue} className="font-medium" />
            </div>
          </div>

          {/* Available Grade Options */}
          <div className="space-y-2">
            <h3 className="font-medium">Available Grade Options</h3>
            <div className="grid grid-cols-4 gap-2 text-sm">
              {options.map(option => (
                <div key={option.value} className="bg-gray-100 p-2 rounded">
                  <div className="font-medium">{option.label}</div>
                  <div className="text-gray-600">Value: {option.grade_value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 pt-4 border-t">
            <Button onClick={handleInitializeSystem} variant="outline">
              Initialize Default System
            </Button>
            <Button onClick={handleTestApiEndpoints} variant="outline">
              Test API Endpoints
            </Button>
            <Button onClick={refreshGradeSystem} variant="outline">
              Refresh System
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}