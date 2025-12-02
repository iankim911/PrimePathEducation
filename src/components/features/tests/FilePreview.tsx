"use client"

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  RotateCw,
  RotateCcw,
  ZoomIn,
  ZoomOut,
  Play,
  Pause,
  Volume2,
  VolumeX,
  Download,
  Maximize,
  X,
  FileText,
  Image,
  Music
} from 'lucide-react'
import { PDFViewer } from './PDFViewer'

interface FilePreviewProps {
  file: File | string
  fileType?: 'pdf' | 'image' | 'audio'
  onClose?: () => void
  className?: string
  showControls?: boolean
  title?: string
}

interface PreviewSettings {
  zoom: number
  rotation: number
  volume: number
  isPlaying: boolean
  isMuted: boolean
}

export function FilePreview({ 
  file, 
  fileType,
  onClose, 
  className = '',
  showControls = true,
  title
}: FilePreviewProps) {
  const [settings, setSettings] = useState<PreviewSettings>({
    zoom: 1,
    rotation: 0,
    volume: 0.7,
    isPlaying: false,
    isMuted: false
  })
  
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const containerRef = useRef<HTMLDivElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  // Detect file type if not provided
  const detectedFileType = fileType || detectFileType(file)

  useEffect(() => {
    if (!file) return

    if (typeof file === 'string') {
      setPreviewUrl(file)
      setLoading(false)
    } else if (file instanceof File) {
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setLoading(false)
      
      return () => {
        URL.revokeObjectURL(url)
      }
    }
  }, [file])

  function detectFileType(file: File | string): 'pdf' | 'image' | 'audio' {
    if (typeof file === 'string') {
      const extension = file.split('.').pop()?.toLowerCase()
      if (['pdf'].includes(extension || '')) return 'pdf'
      if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(extension || '')) return 'image'
      if (['mp3', 'wav', 'ogg', 'm4a', 'aac'].includes(extension || '')) return 'audio'
    } else if (file instanceof File) {
      if (file.type.startsWith('image/')) return 'image'
      if (file.type === 'application/pdf') return 'pdf'
      if (file.type.startsWith('audio/')) return 'audio'
    }
    return 'image' // default fallback
  }

  const updateSetting = <K extends keyof PreviewSettings>(
    key: K, 
    value: PreviewSettings[K]
  ) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleZoomIn = () => updateSetting('zoom', Math.min(settings.zoom + 0.25, 3))
  const handleZoomOut = () => updateSetting('zoom', Math.max(settings.zoom - 0.25, 0.25))
  const handleRotateLeft = () => updateSetting('rotation', settings.rotation - 90)
  const handleRotateRight = () => updateSetting('rotation', settings.rotation + 90)
  
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
    if (!previewUrl || !file) return

    const link = document.createElement('a')
    link.href = previewUrl
    
    if (typeof file === 'string') {
      const filename = file.split('/').pop() || 'download'
      link.download = filename
    } else {
      link.download = file.name
    }
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const resetSettings = () => {
    setSettings({
      zoom: 1,
      rotation: 0,
      volume: 0.7,
      isPlaying: false,
      isMuted: false
    })
  }

  // Audio control handlers
  const togglePlayPause = () => {
    if (!audioRef.current) return
    
    if (settings.isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    updateSetting('isPlaying', !settings.isPlaying)
  }

  const toggleMute = () => {
    if (!audioRef.current) return
    
    audioRef.current.muted = !settings.isMuted
    updateSetting('isMuted', !settings.isMuted)
  }

  const handleVolumeChange = (volume: number) => {
    if (!audioRef.current) return
    
    audioRef.current.volume = volume
    updateSetting('volume', volume)
  }

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-96 bg-gray-50 rounded-lg ${className}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading preview...</p>
        </div>
      </div>
    )
  }

  if (error || !previewUrl) {
    return (
      <div className={`flex items-center justify-center h-96 bg-gray-50 rounded-lg ${className}`}>
        <div className="text-center">
          <div className="mx-auto h-12 w-12 text-gray-400 mb-2">
            <X className="h-full w-full" />
          </div>
          <p className="text-gray-600">{error || 'Preview not available'}</p>
        </div>
      </div>
    )
  }

  // For PDF files, use the dedicated PDFViewer component
  if (detectedFileType === 'pdf') {
    return (
      <PDFViewer
        file={file}
        onClose={onClose}
        className={className}
        showControls={showControls}
        initialZoom={settings.zoom}
        initialRotation={settings.rotation}
      />
    )
  }

  return (
    <div 
      ref={containerRef}
      className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className} ${
        isFullscreen ? 'fixed inset-0 z-50' : ''
      }`}
    >
      {/* Header with File Info and Controls */}
      {showControls && (
        <div className="flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            {/* File Type Icon */}
            <div className="flex items-center space-x-2">
              {detectedFileType === 'image' && <Image className="h-5 w-5 text-blue-500" />}
              {detectedFileType === 'audio' && <Music className="h-5 w-5 text-green-500" />}
              
              <Badge variant="secondary" className="text-xs">
                {detectedFileType?.toUpperCase()}
              </Badge>
            </div>

            {/* File Name */}
            <div>
              <p className="text-sm font-medium text-gray-900">
                {title || (typeof file === 'string' ? file.split('/').pop() : file?.name)}
              </p>
              {typeof file === 'object' && (
                <p className="text-xs text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              )}
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex items-center space-x-1">
            {detectedFileType === 'image' && (
              <>
                {/* Zoom Controls */}
                <Button variant="outline" size="sm" onClick={handleZoomOut} disabled={settings.zoom <= 0.25}>
                  <ZoomOut className="h-4 w-4" />
                </Button>
                
                <span className="text-xs text-gray-600 min-w-[3rem] text-center">
                  {Math.round(settings.zoom * 100)}%
                </span>
                
                <Button variant="outline" size="sm" onClick={handleZoomIn} disabled={settings.zoom >= 3}>
                  <ZoomIn className="h-4 w-4" />
                </Button>

                {/* Rotation Controls */}
                <Button variant="outline" size="sm" onClick={handleRotateLeft}>
                  <RotateCcw className="h-4 w-4" />
                </Button>
                
                <Button variant="outline" size="sm" onClick={handleRotateRight}>
                  <RotateCw className="h-4 w-4" />
                </Button>
              </>
            )}

            {detectedFileType === 'audio' && (
              <>
                {/* Audio Controls */}
                <Button variant="outline" size="sm" onClick={togglePlayPause}>
                  {settings.isPlaying ? (
                    <Pause className="h-4 w-4" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </Button>
                
                <Button variant="outline" size="sm" onClick={toggleMute}>
                  {settings.isMuted ? (
                    <VolumeX className="h-4 w-4" />
                  ) : (
                    <Volume2 className="h-4 w-4" />
                  )}
                </Button>
                
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.volume}
                  onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                  className="w-16 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </>
            )}

            {/* Common Controls */}
            <Button variant="outline" size="sm" onClick={resetSettings}>
              Reset
            </Button>
            
            <Button variant="outline" size="sm" onClick={handleDownload}>
              <Download className="h-4 w-4" />
            </Button>
            
            <Button variant="outline" size="sm" onClick={toggleFullscreen}>
              <Maximize className="h-4 w-4" />
            </Button>

            {onClose && (
              <Button variant="outline" size="sm" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Preview Content */}
      <div 
        className={`relative flex items-center justify-center ${
          isFullscreen ? 'h-[calc(100vh-80px)]' : 'h-96'
        } bg-gray-50 overflow-hidden`}
      >
        {detectedFileType === 'image' && (
          <div className="flex items-center justify-center h-full w-full p-4">
            <img
              ref={imageRef}
              src={previewUrl}
              alt={typeof file === 'string' ? file : file?.name}
              className="max-h-full max-w-full object-contain shadow-lg"
              style={{
                transform: `scale(${settings.zoom}) rotate(${settings.rotation}deg)`,
                transition: 'transform 0.2s ease-in-out'
              }}
              onError={() => setError('Failed to load image')}
            />
          </div>
        )}

        {detectedFileType === 'audio' && (
          <div className="flex flex-col items-center justify-center h-full w-full p-8">
            <div className="text-center mb-6">
              <Music className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {typeof file === 'string' ? file.split('/').pop() : file?.name}
              </h3>
              <p className="text-gray-600">Click play to start audio playback</p>
            </div>
            
            <audio
              ref={audioRef}
              src={previewUrl}
              onPlay={() => updateSetting('isPlaying', true)}
              onPause={() => updateSetting('isPlaying', false)}
              onEnded={() => updateSetting('isPlaying', false)}
              onError={() => setError('Failed to load audio file')}
              controls
              className="w-full max-w-md"
            />
          </div>
        )}
      </div>

      {/* Footer with Settings Info */}
      {showControls && (
        <div className="flex items-center justify-between p-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-600">
          <div>
            {typeof file === 'string' ? 'Remote File' : 'Local File'}
          </div>
          <div className="flex space-x-4">
            {detectedFileType === 'image' && (
              <>
                <span>Zoom: {Math.round(settings.zoom * 100)}%</span>
                <span>Rotation: {settings.rotation}°</span>
              </>
            )}
            {detectedFileType === 'audio' && (
              <span>Volume: {Math.round(settings.volume * 100)}%</span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}