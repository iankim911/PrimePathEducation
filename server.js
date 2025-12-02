/**
 * Production WebSocket Server with Next.js Integration
 * 
 * This server handles both HTTP requests through Next.js
 * and WebSocket connections for real-time functionality.
 */

const { createServer } = require('http')
const { parse } = require('url')
const next = require('next')

// Environment configuration
const dev = process.env.NODE_ENV !== 'production'
const hostname = process.env.HOSTNAME || 'localhost'
const port = parseInt(process.env.PORT || '3000', 10)

// Initialize Next.js
const app = next({ dev, hostname, port })
const handle = app.getRequestHandler()

// WebSocket server (will be imported after app is ready)
let realtimeServer = null

/**
 * Initialize the server
 */
async function startServer() {
  try {
    console.log('🚀 Starting PrimePath Real-time Server...')
    
    // Prepare Next.js app
    await app.prepare()
    console.log('✅ Next.js app prepared')

    // Create HTTP server
    const httpServer = createServer(async (req, res) => {
      try {
        const parsedUrl = parse(req.url, true)
        await handle(req, res, parsedUrl)
      } catch (err) {
        console.error('Error occurred handling', req.url, err)
        res.statusCode = 500
        res.end('Internal server error')
      }
    })

    // Import and initialize WebSocket server after Next.js is ready
    const { realtimeServer: wsServer } = await import('./dist/lib/websocket/server.js')
    realtimeServer = wsServer

    // Initialize WebSocket functionality
    realtimeServer.initialize(httpServer)
    console.log('✅ WebSocket server initialized')

    // Setup database event listeners
    setupDatabaseIntegration()
    console.log('✅ Database integration configured')

    // Start listening
    httpServer.listen(port, hostname, () => {
      console.log(`🚀 Server ready on http://${hostname}:${port}`)
      console.log(`🔌 WebSocket ready on ws://${hostname}:${port}/api/ws`)
      console.log(`📊 Environment: ${process.env.NODE_ENV}`)
    })

    // Setup graceful shutdown
    setupGracefulShutdown(httpServer)

  } catch (error) {
    console.error('❌ Failed to start server:', error)
    process.exit(1)
  }
}

/**
 * Setup database event listeners
 */
async function setupDatabaseIntegration() {
  if (!realtimeServer) return

  try {
    // Import service functions dynamically
    const { saveStudentAnswer, autoSaveStudentAnswer } = await import('./dist/lib/services/exams.js')

    // Handle answer submissions
    realtimeServer.on('answer_submitted', async (data) => {
      try {
        await saveStudentAnswer({
          sessionId: data.sessionId,
          studentId: data.studentId,
          questionId: data.questionId,
          answer: data.answer,
          submittedAt: data.timestamp,
          isAutoSave: false
        })
        console.log(`📝 Answer saved: ${data.studentId} -> ${data.questionId}`)
      } catch (error) {
        console.error('Failed to save answer:', error)
      }
    })

    // Handle auto-save events
    realtimeServer.on('answer_autosaved', async (data) => {
      try {
        await autoSaveStudentAnswer({
          sessionId: data.sessionId,
          studentId: data.studentId,
          questionId: data.questionId,
          answer: data.answer,
          savedAt: data.timestamp
        })
        // Don't log every autosave to avoid spam
      } catch (error) {
        console.error('Failed to autosave answer:', error)
      }
    })

    // Handle session state changes
    realtimeServer.on('session_status_changed', async (data) => {
      try {
        const { updateExamSessionStatus } = await import('./dist/lib/services/exams.js')
        
        await updateExamSessionStatus(
          data.sessionId,
          data.academyId,
          data.status,
          data.additionalData
        )
        console.log(`📊 Session status updated: ${data.sessionId} -> ${data.status}`)
      } catch (error) {
        console.error('Failed to update session status:', error)
      }
    })

  } catch (error) {
    console.warn('⚠️ Could not setup database integration:', error.message)
    console.warn('   This is normal during build process')
  }
}

/**
 * Setup graceful shutdown handlers
 */
function setupGracefulShutdown(httpServer) {
  const gracefulShutdown = (signal) => {
    console.log(`\n🔄 Received ${signal}. Starting graceful shutdown...`)

    // Stop accepting new connections
    httpServer.close(async () => {
      console.log('✅ HTTP server closed')

      try {
        // Cleanup WebSocket server
        if (realtimeServer) {
          realtimeServer.cleanup()
          console.log('✅ WebSocket server cleaned up')
        }

        console.log('✅ Graceful shutdown completed')
        process.exit(0)
      } catch (error) {
        console.error('❌ Error during shutdown:', error)
        process.exit(1)
      }
    })

    // Force close after 10 seconds
    setTimeout(() => {
      console.error('⚠️ Could not close connections in time, forcefully shutting down')
      process.exit(1)
    }, 10000)
  }

  // Listen for shutdown signals
  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'))
  process.on('SIGINT', () => gracefulShutdown('SIGINT'))

  // Handle uncaught exceptions
  process.on('uncaughtException', (error) => {
    console.error('❌ Uncaught Exception:', error)
    gracefulShutdown('UNCAUGHT_EXCEPTION')
  })

  // Handle unhandled promise rejections
  process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason)
    gracefulShutdown('UNHANDLED_REJECTION')
  })
}

/**
 * Health check endpoint monitoring
 */
function setupHealthMonitoring() {
  setInterval(() => {
    if (realtimeServer) {
      const stats = {
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        activeConnections: realtimeServer.getConnectionCount?.() || 0
      }
      
      // Log health stats every 5 minutes
      console.log('📊 Health Stats:', JSON.stringify(stats, null, 2))
    }
  }, 5 * 60 * 1000) // Every 5 minutes
}

// Start monitoring
setupHealthMonitoring()

// Start the server
if (require.main === module) {
  startServer()
}

module.exports = { startServer }