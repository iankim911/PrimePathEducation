/**
 * WebSocket API Route for Next.js
 * 
 * This route handles WebSocket server management and provides status information.
 * The actual WebSocket connections are handled by the Socket.IO server.
 */

import { NextRequest } from 'next/server'
import { socketManager } from '@/lib/websocket/socketManager'

export async function GET(request: NextRequest) {
  // WebSocket server status and documentation
  
  return Response.json({
    message: 'WebSocket endpoint active',
    endpoint: '/api/ws',
    protocols: ['ws', 'wss'],
    features: [
      'Real-time exam session control',
      'Live student progress monitoring', 
      'Auto-save answer synchronization',
      'Session management and timing',
      'Broadcast messaging to classes',
      'Connection health monitoring'
    ],
    stats: {
      activeSessions: socketManager.getActiveSessionsCount(),
      connectedUsers: socketManager.getConnectedUsersCount()
    },
    usage: {
      connect: process.env.NODE_ENV === 'production' 
        ? 'wss://your-domain.com/socket.io'
        : 'ws://localhost:3000/socket.io',
      events: {
        'join_session': 'Join an exam session',
        'control_session': 'Start/pause/end session (teacher only)',
        'submit_answer': 'Submit student answer',
        'broadcast_message': 'Send message to session (teacher only)',
        'request_progress': 'Get session progress (teacher only)'
      }
    }
  })
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, sessionId, data } = body

    switch (action) {
      case 'broadcast':
        if (!sessionId || !data) {
          return Response.json(
            { success: false, message: 'Missing sessionId or data' },
            { status: 400 }
          )
        }
        
        socketManager.broadcastToSession(sessionId, data.event, data.payload)
        
        return Response.json({
          success: true,
          message: `Message broadcasted to session ${sessionId}`
        })

      case 'status':
        const sessionStatus = sessionId 
          ? socketManager.getSessionStatus(sessionId)
          : {
              activeSessions: socketManager.getActiveSessionsCount(),
              connectedUsers: socketManager.getConnectedUsersCount()
            }

        return Response.json({
          success: true,
          status: sessionStatus
        })

      default:
        return Response.json(
          { success: false, message: 'Invalid action' },
          { status: 400 }
        )
    }

  } catch (error) {
    console.error('Error handling WebSocket API request:', error)
    return Response.json(
      { 
        success: false, 
        message: 'Internal server error',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}