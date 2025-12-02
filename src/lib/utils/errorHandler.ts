/**
 * Enhanced Error Handling and Logging System
 * 
 * Provides comprehensive error handling, logging, and monitoring
 * for the Test Management Module with production-ready features.
 */

export interface ErrorContext {
  userId?: string
  sessionId?: string
  examId?: string
  academyId?: string
  userAgent?: string
  url?: string
  timestamp?: string
  additionalData?: Record<string, any>
}

export interface LogEvent {
  level: 'debug' | 'info' | 'warn' | 'error' | 'critical'
  message: string
  error?: Error
  context?: ErrorContext
  category?: 'auth' | 'exam' | 'websocket' | 'api' | 'ui' | 'database' | 'file'
  timestamp: string
}

export class AppError extends Error {
  public readonly statusCode: number
  public readonly isOperational: boolean
  public readonly context?: ErrorContext
  public readonly category: string

  constructor(
    message: string,
    statusCode: number = 500,
    isOperational: boolean = true,
    context?: ErrorContext,
    category: string = 'general'
  ) {
    super(message)
    this.statusCode = statusCode
    this.isOperational = isOperational
    this.context = context
    this.category = category
    
    // Maintains proper stack trace for where error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, AppError)
    }
    
    this.name = this.constructor.name
  }
}

export class ValidationError extends AppError {
  constructor(message: string, context?: ErrorContext) {
    super(message, 400, true, context, 'validation')
  }
}

export class AuthenticationError extends AppError {
  constructor(message: string = 'Authentication required', context?: ErrorContext) {
    super(message, 401, true, context, 'auth')
  }
}

export class AuthorizationError extends AppError {
  constructor(message: string = 'Insufficient permissions', context?: ErrorContext) {
    super(message, 403, true, context, 'auth')
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, context?: ErrorContext) {
    super(`${resource} not found`, 404, true, context, 'resource')
  }
}

export class DatabaseError extends AppError {
  constructor(message: string, context?: ErrorContext) {
    super(message, 500, true, context, 'database')
  }
}

export class WebSocketError extends AppError {
  constructor(message: string, context?: ErrorContext) {
    super(message, 500, true, context, 'websocket')
  }
}

export class FileUploadError extends AppError {
  constructor(message: string, context?: ErrorContext) {
    super(message, 400, true, context, 'file')
  }
}

class Logger {
  private static instance: Logger
  private logs: LogEvent[] = []
  private maxLogs: number = 1000

  private constructor() {}

  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger()
    }
    return Logger.instance
  }

  private createLogEvent(
    level: LogEvent['level'],
    message: string,
    error?: Error,
    context?: ErrorContext,
    category?: LogEvent['category']
  ): LogEvent {
    return {
      level,
      message,
      error,
      context: {
        ...context,
        timestamp: new Date().toISOString(),
        url: typeof window !== 'undefined' ? window.location.href : undefined,
        userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined
      },
      category,
      timestamp: new Date().toISOString()
    }
  }

  private addLog(logEvent: LogEvent): void {
    this.logs.push(logEvent)
    
    // Maintain max logs limit
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs)
    }

    // Console output in development
    if (process.env.NODE_ENV === 'development') {
      this.consoleOutput(logEvent)
    }

    // Send to external logging service in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToLoggingService(logEvent)
    }
  }

  private consoleOutput(logEvent: LogEvent): void {
    const { level, message, error, context, category } = logEvent
    const prefix = `[${logEvent.timestamp}] [${level.toUpperCase()}] [${category || 'GENERAL'}]`
    
    switch (level) {
      case 'debug':
        console.debug(prefix, message, context)
        break
      case 'info':
        console.info(prefix, message, context)
        break
      case 'warn':
        console.warn(prefix, message, context)
        break
      case 'error':
      case 'critical':
        console.error(prefix, message, error, context)
        break
    }
  }

  private async sendToLoggingService(logEvent: LogEvent): Promise<void> {
    try {
      // In a real implementation, you would send to services like:
      // - Sentry
      // - LogRocket  
      // - DataDog
      // - CloudWatch
      // - Custom logging endpoint
      
      if (logEvent.level === 'error' || logEvent.level === 'critical') {
        // Send critical errors immediately
        await fetch('/api/logging/error', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(logEvent)
        }).catch(() => {
          // Silently fail if logging service is down
        })
      }
    } catch (error) {
      // Never throw errors from logging system
      console.error('Failed to send log to external service:', error)
    }
  }

  public debug(message: string, context?: ErrorContext, category?: LogEvent['category']): void {
    this.addLog(this.createLogEvent('debug', message, undefined, context, category))
  }

  public info(message: string, context?: ErrorContext, category?: LogEvent['category']): void {
    this.addLog(this.createLogEvent('info', message, undefined, context, category))
  }

  public warn(message: string, context?: ErrorContext, category?: LogEvent['category']): void {
    this.addLog(this.createLogEvent('warn', message, undefined, context, category))
  }

  public error(message: string, error?: Error, context?: ErrorContext, category?: LogEvent['category']): void {
    this.addLog(this.createLogEvent('error', message, error, context, category))
  }

  public critical(message: string, error?: Error, context?: ErrorContext, category?: LogEvent['category']): void {
    this.addLog(this.createLogEvent('critical', message, error, context, category))
  }

  public getLogs(level?: LogEvent['level'], category?: LogEvent['category'], limit?: number): LogEvent[] {
    let filteredLogs = [...this.logs]
    
    if (level) {
      filteredLogs = filteredLogs.filter(log => log.level === level)
    }
    
    if (category) {
      filteredLogs = filteredLogs.filter(log => log.category === category)
    }
    
    if (limit) {
      filteredLogs = filteredLogs.slice(-limit)
    }
    
    return filteredLogs.reverse() // Most recent first
  }

  public clearLogs(): void {
    this.logs = []
  }

  public getLogStats(): {
    total: number
    byLevel: Record<LogEvent['level'], number>
    byCategory: Record<string, number>
  } {
    const byLevel: Record<LogEvent['level'], number> = {
      debug: 0,
      info: 0,
      warn: 0,
      error: 0,
      critical: 0
    }
    
    const byCategory: Record<string, number> = {}
    
    this.logs.forEach(log => {
      byLevel[log.level]++
      
      const category = log.category || 'general'
      byCategory[category] = (byCategory[category] || 0) + 1
    })
    
    return {
      total: this.logs.length,
      byLevel,
      byCategory
    }
  }
}

export const logger = Logger.getInstance()

/**
 * Error Handler Decorator for API Routes
 */
export function withErrorHandling<T extends (...args: any[]) => Promise<Response>>(
  handler: T,
  category?: LogEvent['category']
): T {
  return (async (...args: any[]) => {
    try {
      return await handler(...args)
    } catch (error) {
      const appError = error instanceof AppError ? error : new AppError(
        'Internal server error',
        500,
        false,
        { additionalData: { originalError: error instanceof Error ? error.message : String(error) } },
        category || 'api'
      )

      logger.error(
        `API Error: ${appError.message}`,
        appError,
        appError.context,
        appError.category as LogEvent['category']
      )

      return new Response(
        JSON.stringify({
          error: appError.message,
          statusCode: appError.statusCode,
          timestamp: new Date().toISOString(),
          ...(process.env.NODE_ENV === 'development' && { stack: appError.stack })
        }),
        {
          status: appError.statusCode,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }
  }) as T
}

/**
 * Error Handler Hook for React Components
 */
export function useErrorHandler() {
  const handleError = (error: Error, context?: ErrorContext) => {
    const appError = error instanceof AppError ? error : new AppError(
      error.message || 'An unexpected error occurred',
      500,
      true,
      context,
      'ui'
    )

    logger.error(
      `UI Error: ${appError.message}`,
      appError,
      appError.context,
      'ui'
    )

    // In a real app, you might show a toast notification or redirect to error page
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by error handler:', appError)
    }

    return appError
  }

  return { handleError }
}

/**
 * Performance Monitoring
 */
export class PerformanceMonitor {
  private static timers: Map<string, number> = new Map()
  
  static startTimer(name: string): void {
    this.timers.set(name, Date.now())
  }
  
  static endTimer(name: string, context?: ErrorContext): number {
    const startTime = this.timers.get(name)
    if (!startTime) {
      logger.warn(`Timer "${name}" not found`, context)
      return 0
    }
    
    const duration = Date.now() - startTime
    this.timers.delete(name)
    
    // Log slow operations
    if (duration > 1000) {
      logger.warn(
        `Slow operation detected: ${name} took ${duration}ms`,
        { ...context, additionalData: { duration, operationName: name } }
      )
    }
    
    logger.debug(
      `Operation "${name}" completed in ${duration}ms`,
      { ...context, additionalData: { duration, operationName: name } }
    )
    
    return duration
  }
}

/**
 * Rate Limiting and Abuse Detection
 */
export class RateLimiter {
  private static requests: Map<string, number[]> = new Map()
  
  static isRateLimited(
    identifier: string,
    maxRequests: number = 100,
    timeWindow: number = 60000 // 1 minute
  ): boolean {
    const now = Date.now()
    const requests = this.requests.get(identifier) || []
    
    // Remove old requests outside time window
    const recentRequests = requests.filter(time => now - time < timeWindow)
    
    if (recentRequests.length >= maxRequests) {
      logger.warn(
        `Rate limit exceeded for ${identifier}`,
        { additionalData: { identifier, requestCount: recentRequests.length, maxRequests, timeWindow } }
      )
      return true
    }
    
    // Add current request
    recentRequests.push(now)
    this.requests.set(identifier, recentRequests)
    
    return false
  }
  
  static clearRateLimit(identifier: string): void {
    this.requests.delete(identifier)
  }
}