"use client"

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  RotateCw,
  RotateCcw,
  ZoomIn,
  ZoomOut,
  ChevronLeft,
  ChevronRight,
  Maximize,
  Minimize,
  Download,
  X
} from 'lucide-react'

interface PDFViewerProps {
  file?: File | string // File object or URL
  onClose?: () => void
  className?: string
  showControls?: boolean
  initialZoom?: number
  initialRotation?: number
}

export function PDFViewer({ 
  file, 
  onClose, 
  className = '',
  showControls = true,
  initialZoom = 1,
  initialRotation = 0
}: PDFViewerProps) {
  const [zoom, setZoom] = useState(initialZoom)
  const [rotation, setRotation] = useState(initialRotation)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const containerRef = useRef<HTMLDivElement>(null)
  const viewerRef = useRef<HTMLIFrameElement>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)

  useEffect(() => {
    if (!file) return

    if (typeof file === 'string') {
      // File is a URL
      setPdfUrl(file)
      setLoading(false)
    } else if (file instanceof File) {
      // File is a File object
      if (file.type === 'application/pdf') {
        const url = URL.createObjectURL(file)
        setPdfUrl(url)
        setLoading(false)
        
        return () => {
          URL.revokeObjectURL(url)
        }
      } else {
        setError('Selected file is not a PDF')
        setLoading(false)
      }
    }
  }, [file])

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.25, 3))
  }

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.25, 0.5))
  }

  const handleRotateLeft = () => {
    setRotation(prev => prev - 90)
  }

  const handleRotateRight = () => {
    setRotation(prev => prev + 90)
  }

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage)
    }
  }

  const toggleFullscreen = () => {
    if (!containerRef.current) return

    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen()
        setIsFullscreen(true)
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
        setIsFullscreen(false)
      }
    }
  }

  const handleDownload = () => {
    if (!pdfUrl || !file) return

    const link = document.createElement('a')
    link.href = pdfUrl
    
    if (typeof file === 'string') {
      link.download = 'document.pdf'
    } else {
      link.download = file.name
    }
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const resetView = () => {
    setZoom(1)
    setRotation(0)
    setCurrentPage(1)
  }

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-96 bg-gray-50 rounded-lg ${className}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading PDF...</p>
        </div>
      </div>
    )
  }

  if (error || !pdfUrl) {
    return (
      <div className={`flex items-center justify-center h-96 bg-gray-50 rounded-lg ${className}`}>
        <div className="text-center">
          <div className="mx-auto h-12 w-12 text-gray-400 mb-2">
            <X className="h-full w-full" />
          </div>
          <p className="text-gray-600">{error || 'Failed to load PDF'}</p>
        </div>
      </div>
    )
  }

  return (
    <div 
      ref={containerRef}
      className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className} ${
        isFullscreen ? 'fixed inset-0 z-50' : ''
      }`}
    >
      {/* Controls Bar */}
      {showControls && (
        <div className="flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            {/* Page Navigation */}
            <div className="flex items-center space-x-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage <= 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              <div className="flex items-center space-x-1">
                <Input
                  type="number"
                  value={currentPage}
                  onChange={(e) => handlePageChange(parseInt(e.target.value) || 1)}
                  className="w-16 h-8 text-center text-xs"
                  min="1"
                  max={totalPages}
                />
                <span className="text-xs text-gray-600">of {totalPages}</span>
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            {/* Zoom Controls */}
            <Button variant="outline" size="sm" onClick={handleZoomOut} disabled={zoom <= 0.5}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            
            <span className="text-xs text-gray-600 min-w-[3rem] text-center">
              {Math.round(zoom * 100)}%
            </span>
            
            <Button variant="outline" size="sm" onClick={handleZoomIn} disabled={zoom >= 3}>
              <ZoomIn className="h-4 w-4" />
            </Button>

            {/* Rotation Controls */}
            <Button variant="outline" size="sm" onClick={handleRotateLeft}>
              <RotateCcw className="h-4 w-4" />
            </Button>
            
            <Button variant="outline" size="sm" onClick={handleRotateRight}>
              <RotateCw className="h-4 w-4" />
            </Button>

            {/* Utility Controls */}
            <Button variant="outline" size="sm" onClick={resetView}>
              Reset
            </Button>
            
            <Button variant="outline" size="sm" onClick={handleDownload}>
              <Download className="h-4 w-4" />
            </Button>
            
            <Button variant="outline" size="sm" onClick={toggleFullscreen}>
              {isFullscreen ? (
                <Minimize className="h-4 w-4" />
              ) : (
                <Maximize className="h-4 w-4" />
              )}
            </Button>

            {onClose && (
              <Button variant="outline" size="sm" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      )}

      {/* PDF Viewer */}
      <div 
        className={`relative overflow-auto ${
          isFullscreen ? 'h-[calc(100vh-64px)]' : 'h-96'
        }`}
        style={{ backgroundColor: '#f5f5f5' }}
      >
        <div 
          className="flex items-center justify-center p-4 min-h-full"
          style={{
            transform: `scale(${zoom}) rotate(${rotation}deg)`,
            transformOrigin: 'center',
            transition: 'transform 0.2s ease-in-out'
          }}
        >
          <iframe
            ref={viewerRef}
            src={`${pdfUrl}#page=${currentPage}&zoom=${Math.round(zoom * 100)}&toolbar=0&navpanes=0&scrollbar=0`}
            className="border-none shadow-lg"
            style={{
              width: '800px',
              height: '1000px',
              backgroundColor: 'white'
            }}
            title="PDF Viewer"
            onLoad={() => {
              // Try to detect total pages (this is browser-dependent)
              // For now, we'll use a default or require it to be passed as a prop
              setTotalPages(1) // This would need to be enhanced for multi-page PDFs
              setLoading(false)
            }}
          />
        </div>
      </div>

      {/* PDF Info Bar */}
      {showControls && (
        <div className="flex items-center justify-between p-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-600">
          <div>
            {typeof file === 'string' ? 'PDF Document' : file?.name}
          </div>
          <div>
            Zoom: {Math.round(zoom * 100)}% | Rotation: {rotation}°
          </div>
        </div>
      )}
    </div>
  )
}

// Enhanced PDF Viewer with pdf.js integration (requires additional setup)
export function EnhancedPDFViewer({ 
  file, 
  onClose, 
  className = '',
  showControls = true 
}: PDFViewerProps) {
  // This would integrate with react-pdf or pdf.js for more advanced features
  // For now, we'll use the basic iframe viewer above
  return (
    <PDFViewer 
      file={file}
      onClose={onClose}
      className={className}
      showControls={showControls}
    />
  )
}