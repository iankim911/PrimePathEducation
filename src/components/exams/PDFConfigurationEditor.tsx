'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { 
  RotateCw,
  ZoomIn,
  ZoomOut,
  Split,
  Save,
  RotateCcw,
  Eye,
  EyeOff,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'

interface PDFConfiguration {
  rotation_degrees: number
  zoom_level: number
  is_split_enabled: boolean
  split_orientation: 'vertical' | 'horizontal'
  split_page_1_position: 'left' | 'right' | 'top' | 'bottom'
  split_page_2_position: 'left' | 'right' | 'top' | 'bottom'
}

interface PDFConfigurationEditorProps {
  pdfUrl: string | null
  onConfigurationSave: (config: PDFConfiguration) => Promise<void>
  initialConfig?: Partial<PDFConfiguration>
  showSaveButton?: boolean
  className?: string
}

export function PDFConfigurationEditor({
  pdfUrl,
  onConfigurationSave,
  initialConfig = {},
  showSaveButton = true,
  className = ''
}: PDFConfigurationEditorProps) {
  const [config, setConfig] = useState<PDFConfiguration>({
    rotation_degrees: 0,
    zoom_level: 1.0,
    is_split_enabled: false,
    split_orientation: 'vertical',
    split_page_1_position: 'left',
    split_page_2_position: 'right',
    ...initialConfig
  })

  const [saving, setSaving] = useState(false)
  const [showPreview, setShowPreview] = useState(true)
  
  // Virtual pagination state for split mode
  const [currentVirtualPage, setCurrentVirtualPage] = useState(1) // Current virtual page
  const [totalPdfPages, setTotalPdfPages] = useState(1) // Total actual PDF pages (default 1, user should set)
  const [manualPageCount, setManualPageCount] = useState<string>('') // Manual input for page count (empty by default)
  
  const iframeRef = useRef<HTMLIFrameElement>(null)
  
  // Helper functions for virtual pagination
  const getTotalVirtualPages = () => {
    // Ensure we have a valid page count
    const actualPages = totalPdfPages > 0 ? totalPdfPages : 1
    return config.is_split_enabled ? actualPages * 2 : actualPages
  }
  
  const getCurrentPdfPage = () => {
    if (!config.is_split_enabled) return currentVirtualPage
    return Math.ceil(currentVirtualPage / 2)
  }
  
  const getCurrentSplitHalf = (): 'left' | 'right' | 'top' | 'bottom' => {
    if (!config.is_split_enabled) return 'left' // Default, won't be used
    
    const isOddPage = currentVirtualPage % 2 === 1
    
    if (config.split_orientation === 'vertical') {
      return isOddPage ? 'left' : 'right'
    } else {
      return isOddPage ? 'top' : 'bottom'
    }
  }
  
  // Check if split navigation should be disabled
  const isSplitNavigationDisabled = () => {
    return config.is_split_enabled && (!manualPageCount || parseInt(manualPageCount) < 1)
  }
  
  // Navigation functions
  const navigateToVirtualPage = (page: number) => {
    if (isSplitNavigationDisabled()) return
    
    const maxPage = getTotalVirtualPages()
    if (page < 1 || page > maxPage) return
    setCurrentVirtualPage(page)
  }
  
  const navigatePrevious = () => {
    navigateToVirtualPage(currentVirtualPage - 1)
  }
  
  const navigateNext = () => {
    navigateToVirtualPage(currentVirtualPage + 1)
  }

  // Update config when initialConfig changes
  useEffect(() => {
    setConfig(prev => ({
      ...prev,
      ...initialConfig
    }))
  }, [initialConfig])

  const handleRotate = (degrees: number) => {
    setConfig(prev => ({
      ...prev,
      rotation_degrees: (prev.rotation_degrees + degrees) % 360
    }))
  }

  const handleZoomIn = () => {
    setConfig(prev => ({
      ...prev,
      zoom_level: Math.min(prev.zoom_level + 0.2, 2.0)
    }))
  }

  const handleZoomOut = () => {
    setConfig(prev => ({
      ...prev,
      zoom_level: Math.max(prev.zoom_level - 0.2, 0.5)
    }))
  }

  const handleResetZoom = () => {
    setConfig(prev => ({
      ...prev,
      zoom_level: 1.0
    }))
  }

  const handleSplitToggle = (enabled: boolean) => {
    setConfig(prev => ({
      ...prev,
      is_split_enabled: enabled,
      // Auto-adjust positions based on orientation when enabling split
      split_page_1_position: prev.split_orientation === 'vertical' ? 'left' : 'top',
      split_page_2_position: prev.split_orientation === 'vertical' ? 'right' : 'bottom'
    }))
    
    // Reset to first page when toggling split mode
    setCurrentVirtualPage(1)
  }

  const handleOrientationChange = (orientation: 'vertical' | 'horizontal') => {
    setConfig(prev => ({
      ...prev,
      split_orientation: orientation,
      split_page_1_position: orientation === 'vertical' ? 'left' : 'top',
      split_page_2_position: orientation === 'vertical' ? 'right' : 'bottom'
    }))
  }

  const handleSave = async () => {
    if (!onConfigurationSave) return

    setSaving(true)
    try {
      await onConfigurationSave(config)
    } catch (error) {
      console.error('Error saving PDF configuration:', error)
    } finally {
      setSaving(false)
    }
  }

  const getSplitStyle = () => {
    if (!config.is_split_enabled) return {}

    if (config.split_orientation === 'vertical') {
      return {
        clipPath: config.split_page_1_position === 'left' 
          ? 'inset(0 50% 0 0)' // Show left half
          : 'inset(0 0 0 50%)'  // Show right half
      }
    } else {
      return {
        clipPath: config.split_page_1_position === 'top'
          ? 'inset(0 0 50% 0)' // Show top half
          : 'inset(50% 0 0 0)'  // Show bottom half
      }
    }
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Controls Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">PDF Configuration</h3>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowPreview(!showPreview)}
            >
              {showPreview ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              {showPreview ? 'Hide' : 'Show'} Preview
            </Button>
            
            {showSaveButton && (
              <Button
                onClick={handleSave}
                disabled={saving}
                className="bg-gray-900 hover:bg-gray-800 text-white"
                size="sm"
              >
                {saving ? (
                  <>Saving...</>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Configuration
                  </>
                )}
              </Button>
            )}
          </div>
        </div>

        {/* Controls Row 1: PDF Pages & Rotation/Zoom */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="space-y-2">
            <Label className="text-sm font-medium text-gray-700">PDF Page Count *</Label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="1"
                max="1000"
                value={manualPageCount}
                onChange={(e) => {
                  const value = e.target.value
                  setManualPageCount(value)
                  const numValue = parseInt(value) || 1
                  setTotalPdfPages(numValue)
                  // Reset to page 1 when changing page count
                  setCurrentVirtualPage(1)
                }}
                placeholder="e.g., 5"
                className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-gray-900"
              />
              <span className="text-xs text-gray-500">
                {config.is_split_enabled && manualPageCount 
                  ? `→ ${parseInt(manualPageCount) * 2} split pages`
                  : 'total pages'
                }
              </span>
            </div>
            <p className="text-xs text-gray-500">
              How many pages are in your PDF?
            </p>
          </div>
          
          <div className="space-y-2">
            <Label className="text-sm font-medium text-gray-700">Rotation & Zoom</Label>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="icon" onClick={() => handleRotate(-90)}>
                <RotateCcw className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={() => handleRotate(90)}>
                <RotateCw className="h-4 w-4" />
              </Button>
              <div className="text-xs text-gray-500 min-w-[2rem]">
                {config.rotation_degrees}°
              </div>
              <div className="w-px h-6 bg-gray-300 mx-2" />
              <Button variant="outline" size="icon" onClick={handleZoomOut}>
                <ZoomOut className="h-4 w-4" />
              </Button>
              <div className="text-xs text-gray-500 min-w-[3rem] text-center">
                {Math.round(config.zoom_level * 100)}%
              </div>
              <Button variant="outline" size="icon" onClick={handleZoomIn}>
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={handleResetZoom}>
                Reset
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium text-gray-700">Page Split</Label>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Switch
                  checked={config.is_split_enabled}
                  onCheckedChange={handleSplitToggle}
                />
                <Label className="text-sm">Enable Split</Label>
              </div>
              
              {config.is_split_enabled && (
                <div className="flex items-center gap-2">
                  <Button
                    variant={config.split_orientation === 'vertical' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleOrientationChange('vertical')}
                  >
                    Vertical
                  </Button>
                  <Button
                    variant={config.split_orientation === 'horizontal' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleOrientationChange('horizontal')}
                  >
                    Horizontal
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Split Configuration Info */}
        {config.is_split_enabled && (
          <div className="space-y-2">
            {!manualPageCount && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                <div className="text-sm text-yellow-800">
                  <div className="font-medium mb-1">⚠️ Page Count Required</div>
                  <div>Please set the PDF page count above to enable proper split functionality.</div>
                </div>
              </div>
            )}
            
            {manualPageCount && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                <div className="text-sm text-blue-800">
                  <div className="font-medium mb-1">Split Configuration:</div>
                  <div className="space-y-1">
                    <div>
                      PDF Pages: <span className="font-mono">{manualPageCount}</span> → 
                      Virtual Pages: <span className="font-mono">{parseInt(manualPageCount) * 2}</span>
                    </div>
                    <div>
                      Orientation: <span className="font-mono">{config.split_orientation}</span> • 
                      First Half: <span className="font-mono">{config.split_page_1_position}</span> • 
                      Second Half: <span className="font-mono">{config.split_page_2_position}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* PDF Preview */}
      {showPreview && (
        <div className="p-4">
          {pdfUrl ? (
            <div className="space-y-2">
              {/* Navigation Controls - Only show when split is enabled */}
              {config.is_split_enabled && (
                <div className={`flex items-center justify-between rounded-lg px-4 py-2 ${
                  isSplitNavigationDisabled() ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-100'
                }`}>
                  {isSplitNavigationDisabled() ? (
                    <div className="flex items-center justify-center w-full text-yellow-700 text-sm">
                      ⚠️ Set PDF page count above to enable navigation
                    </div>
                  ) : (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={navigatePrevious}
                        disabled={currentVirtualPage === 1}
                      >
                        <ChevronLeft className="h-4 w-4 mr-1" />
                        Previous
                      </Button>
                      
                      <div className="flex items-center gap-4">
                        <span className="text-sm font-medium">
                          Page {currentVirtualPage} of {getTotalVirtualPages()}
                        </span>
                        <span className="text-xs text-gray-500">
                          (PDF Page {getCurrentPdfPage()}, {getCurrentSplitHalf()} half)
                        </span>
                      </div>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={navigateNext}
                        disabled={currentVirtualPage === getTotalVirtualPages()}
                      >
                        Next
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </Button>
                    </>
                  )}
                </div>
              )}
              
              {/* PDF Viewer */}
              <div className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50" style={{ height: '600px' }}>
                <div 
                  className="w-full h-full overflow-auto"
                  style={{
                    transform: `scale(${config.zoom_level}) rotate(${config.rotation_degrees}deg)`,
                    transformOrigin: 'center center',
                    transition: 'transform 0.2s ease'
                  }}
                >
                  <iframe
                    ref={iframeRef}
                    src={`${pdfUrl}#toolbar=0&navpanes=0&scrollbar=0&view=FitH&pagemode=none&page=${getCurrentPdfPage()}`}
                    className="w-full h-full border-0"
                    style={{
                      clipPath: config.is_split_enabled ? (
                        getCurrentSplitHalf() === 'left' ? 'inset(0 50% 0 0)' :
                        getCurrentSplitHalf() === 'right' ? 'inset(0 0 0 50%)' :
                        getCurrentSplitHalf() === 'top' ? 'inset(0 0 50% 0)' :
                        'inset(50% 0 0 0)'
                      ) : 'none',
                      minWidth: config.is_split_enabled && config.split_orientation === 'vertical' 
                        ? `${200 / config.zoom_level}%` 
                        : config.zoom_level < 1 ? `${100 / config.zoom_level}%` : '100%',
                      minHeight: config.is_split_enabled && config.split_orientation === 'horizontal'
                        ? `${200 / config.zoom_level}%`
                        : config.zoom_level < 1 ? `${100 / config.zoom_level}%` : '100%',
                      position: 'relative',
                      left: config.is_split_enabled && getCurrentSplitHalf() === 'right' ? '-100%' : '0',
                      top: config.is_split_enabled && getCurrentSplitHalf() === 'bottom' ? '-100%' : '0'
                    }}
                    title="PDF Preview"
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="border-2 border-dashed border-gray-200 rounded-lg flex items-center justify-center" style={{ height: '600px' }}>
              <div className="text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <p className="mt-2 text-sm text-gray-500">
                  Upload a PDF to configure its display settings
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}