"use client"

import React, { Component, ReactNode } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react'
import { logger, AppError, ErrorContext } from '@/lib/utils/errorHandler'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
  errorId: string | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorId: Math.random().toString(36).substr(2, 9)
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to our logging system
    const context: ErrorContext = {
      additionalData: {
        componentStack: errorInfo.componentStack,
        errorBoundary: true,
        errorId: this.state.errorId,
        errorInfo
      }
    }

    logger.error(
      `React Error Boundary caught error: ${error.message}`,
      error,
      context,
      'ui'
    )

    this.setState({ errorInfo })

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    })
  }

  private handleReportError = () => {
    const { error, errorInfo, errorId } = this.state
    
    // Create error report
    const report = {
      errorId,
      message: error?.message,
      stack: error?.stack,
      componentStack: errorInfo?.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    }

    // In a real implementation, send to error reporting service
    logger.error(
      'User reported error',
      error || undefined,
      { additionalData: report },
      'ui'
    )

    // Copy error details to clipboard for easy sharing
    navigator.clipboard?.writeText(JSON.stringify(report, null, 2))
      .then(() => alert('Error details copied to clipboard'))
      .catch(() => alert('Error details logged - please contact support'))
  }

  private getErrorTitle = (error: Error | null): string => {
    if (error instanceof AppError) {
      return error.category === 'auth' ? 'Authentication Error' :
             error.category === 'validation' ? 'Validation Error' :
             error.category === 'websocket' ? 'Connection Error' :
             error.category === 'database' ? 'Data Error' :
             'Application Error'
    }
    return 'Unexpected Error'
  }

  private getErrorDescription = (error: Error | null): string => {
    if (error instanceof AppError) {
      return error.message
    }
    return 'An unexpected error occurred while rendering this component. This might be due to a temporary issue or a problem with the data.'
  }

  private getSuggestions = (error: Error | null): string[] => {
    if (error instanceof AppError) {
      switch (error.category) {
        case 'auth':
          return [
            'Try refreshing the page',
            'Check if you are still logged in',
            'Clear your browser cache and cookies'
          ]
        case 'websocket':
          return [
            'Check your internet connection',
            'Try refreshing the page',
            'Disable browser extensions temporarily'
          ]
        case 'validation':
          return [
            'Check the data you entered',
            'Try again with different inputs',
            'Contact support if the problem persists'
          ]
        default:
          return [
            'Try refreshing the page',
            'Check your internet connection',
            'Try again in a few moments'
          ]
      }
    }
    
    return [
      'Try refreshing the page',
      'Check your internet connection',
      'Clear your browser cache',
      'Try again in a few moments'
    ]
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI if provided
      if (this.props.fallback) {
        return this.props.fallback
      }

      const { error, errorId } = this.state
      const errorTitle = this.getErrorTitle(error)
      const errorDescription = this.getErrorDescription(error)
      const suggestions = this.getSuggestions(error)

      return (
        <div className="min-h-[400px] flex items-center justify-center p-4 bg-gray-50">
          <Card className="max-w-2xl w-full bg-white shadow-lg">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <AlertTriangle className="h-16 w-16 text-red-500" />
              </div>
              <CardTitle className="text-2xl text-gray-900">{errorTitle}</CardTitle>
              <CardDescription className="text-gray-600">
                {errorDescription}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Error ID for support */}
              {errorId && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Error ID:</span>
                    <code className="text-sm bg-white px-2 py-1 rounded border font-mono text-gray-800">
                      {errorId}
                    </code>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Include this ID when contacting support
                  </p>
                </div>
              )}

              {/* Suggestions */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Try these solutions:</h4>
                <ul className="space-y-2">
                  {suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-gray-700 text-sm">{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Button 
                  onClick={this.handleRetry}
                  className="flex-1 bg-gray-900 hover:bg-gray-800 text-white"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
                
                <Button 
                  onClick={() => window.location.href = '/'}
                  variant="outline"
                  className="flex-1"
                >
                  <Home className="h-4 w-4 mr-2" />
                  Go Home
                </Button>
                
                <Button 
                  onClick={this.handleReportError}
                  variant="outline"
                  className="flex-1"
                >
                  <Bug className="h-4 w-4 mr-2" />
                  Report Issue
                </Button>
              </div>

              {/* Technical Details (Development Only) */}
              {process.env.NODE_ENV === 'development' && error && (
                <details className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <summary className="font-medium text-red-900 cursor-pointer mb-2">
                    Technical Details (Development Mode)
                  </summary>
                  <div className="space-y-3 text-sm">
                    <div>
                      <strong className="text-red-800">Error Message:</strong>
                      <pre className="bg-white p-2 rounded border mt-1 text-xs overflow-auto">
                        {error.message}
                      </pre>
                    </div>
                    <div>
                      <strong className="text-red-800">Stack Trace:</strong>
                      <pre className="bg-white p-2 rounded border mt-1 text-xs overflow-auto">
                        {error.stack}
                      </pre>
                    </div>
                    {this.state.errorInfo && (
                      <div>
                        <strong className="text-red-800">Component Stack:</strong>
                        <pre className="bg-white p-2 rounded border mt-1 text-xs overflow-auto">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              )}
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * HOC to wrap components with error boundary
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode,
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary fallback={fallback} onError={onError}>
      <Component {...props} />
    </ErrorBoundary>
  )
  
  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`
  
  return WrappedComponent
}