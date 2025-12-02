import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Basic health checks
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV,
      serverId: process.env.SERVER_ID || 'unknown'
    }

    // Add more health checks as needed:
    // - Database connection
    // - Redis connection  
    // - External service availability
    // - Disk space
    // - Memory usage thresholds

    return NextResponse.json(health)
  } catch (error) {
    return NextResponse.json(
      { 
        status: 'unhealthy', 
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { status: 503 }
    )
  }
}