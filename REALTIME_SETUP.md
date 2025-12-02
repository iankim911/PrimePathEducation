# Real-Time Exam System - Setup & Deployment Guide

## Overview

This document provides comprehensive instructions for setting up and deploying the real-time exam system with WebSocket functionality for your PrimePath educational platform.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- SQLite/Supabase database
- npm/yarn package manager

### 1. Install Dependencies

```bash
# Install WebSocket dependencies
npm install ws jsonwebtoken

# Install development types
npm install -D @types/ws @types/jsonwebtoken
```

### 2. Database Setup

Run the exam system schema:

```bash
# Apply the real-time exam schema
sqlite3 db/database.db < db/exam-realtime-schema.sql
```

### 3. Environment Variables

Create or update your `.env.local`:

```env
# WebSocket Configuration
WEBSOCKET_PORT=3001
JWT_SECRET=your-super-secret-key-here
ALLOWED_ORIGINS=localhost:3000,yourdomain.com

# Development
NODE_ENV=development
```

### 4. Development Server

For development with WebSocket support:

```bash
# Start Next.js with WebSocket server
npm run dev:ws

# OR start separately
npm run dev          # Next.js (port 3000)
npm run dev:ws       # WebSocket server (port 3001)
```

### 5. Production Deployment

```bash
# Build the application
npm run build

# Start production server with WebSocket
npm run start:ws
```

## 📁 File Structure

The real-time system adds these files to your project:

```
src/
├── lib/websocket/
│   ├── server.ts              # WebSocket server implementation
│   ├── integration.ts         # Next.js integration
│   └── security.ts           # Security & performance layer
├── hooks/
│   ├── useWebSocket.ts       # Core WebSocket hook
│   └── useExamSession.ts     # Exam session management hook
├── components/features/exams/
│   ├── ExamSessionDashboard.tsx    # Teacher dashboard
│   ├── ExamSessionsList.tsx        # Session management
│   └── StudentExamInterface.tsx    # Student exam interface
├── lib/services/
│   └── exams.ts              # Exam service layer
├── types/
│   └── websocket.ts          # TypeScript definitions
└── app/api/ws/
    └── route.ts              # WebSocket API endpoint

db/
└── exam-realtime-schema.sql  # Database schema

server.js                     # Production server entry point
```

## 🔧 Configuration

### WebSocket Server Settings

In `src/lib/websocket/server.ts`, configure:

```typescript
const RATE_LIMITS = {
  AUTH_ATTEMPTS: { max: 5, window: 300000 },    // 5 attempts per 5 min
  MESSAGE_RATE: { max: 60, window: 60000 },     // 60 messages per minute
  ANSWER_SUBMISSION: { max: 10, window: 10000 }  // 10 answers per 10 sec
}

const MESSAGE_LIMITS = {
  MAX_MESSAGE_SIZE: 1024 * 50,  // 50KB per message
  MAX_ANSWER_SIZE: 1024 * 10,   // 10KB per answer
}
```

### Security Configuration

```typescript
const SECURITY_CONFIG = {
  SESSION_TIMEOUT: 4 * 60 * 60 * 1000,    // 4 hours
  CONNECTION_TIMEOUT: 30 * 60 * 1000,     // 30 minutes inactivity
  MAX_CONNECTIONS_PER_USER: 3,            // Multiple device support
  REQUIRE_HTTPS: process.env.NODE_ENV === 'production'
}
```

## 🎯 Usage Examples

### Creating an Exam Session (Teacher)

```typescript
import { ExamSessionDashboard } from '@/components/features/exams/ExamSessionDashboard'

function TeacherPage() {
  const examData = {
    id: 'exam-123',
    title: 'English Assessment',
    duration: 60, // minutes
    totalQuestions: 25,
    enrolledStudents: ['student-1', 'student-2', 'student-3']
  }

  return (
    <ExamSessionDashboard 
      sessionId="session-456"
      examData={examData}
    />
  )
}
```

### Student Exam Interface

```typescript
import { StudentExamInterface } from '@/components/features/exams/StudentExamInterface'

function StudentExamPage() {
  const examData = {
    id: 'exam-123',
    title: 'English Assessment',
    questions: [
      {
        id: 'q1',
        type: 'multiple_choice',
        question: 'What is the correct form?',
        options: ['go', 'goes', 'going', 'gone']
      }
      // ... more questions
    ],
    duration: 60
  }

  return (
    <StudentExamInterface
      sessionId="session-456"
      studentId="student-1"
      examData={examData}
      onComplete={() => console.log('Exam completed!')}
    />
  )
}
```

### Using the WebSocket Hook

```typescript
import { useExamSession } from '@/hooks/useExamSession'

function ExamComponent() {
  const {
    sessionStatus,
    connectedStudents,
    timeRemaining,
    launchExam,
    submitAnswer,
    isConnected
  } = useExamSession({
    sessionId: 'session-456',
    userType: 'teacher',
    onStudentJoined: (data) => console.log('Student joined:', data),
    onProgressUpdate: (data) => console.log('Progress:', data)
  })

  return (
    <div>
      <p>Status: {sessionStatus}</p>
      <p>Connected: {connectedStudents.length}</p>
      <p>Time: {timeRemaining}s</p>
      {sessionStatus === 'preparing' && (
        <button onClick={launchExam}>Launch Exam</button>
      )}
    </div>
  )
}
```

## 🔒 Security Features

### Rate Limiting
- Authentication attempts: 5 per 5 minutes
- Message rate: 60 per minute
- Answer submissions: 10 per 10 seconds

### Message Validation
- Size limits: 50KB messages, 10KB answers
- Content sanitization
- Event type validation
- Timestamp verification

### Connection Security
- Academy isolation
- User session tracking
- IP-based rate limiting
- Automatic cleanup of stale connections

### Data Protection
- Secure token generation
- Message authentication
- Connection state encryption
- Graceful error handling

## 📊 Monitoring & Performance

### Health Monitoring
The server logs health stats every 5 minutes:

```json
{
  "timestamp": "2024-11-28T10:30:00Z",
  "uptime": 3600,
  "memory": {
    "rss": 45000000,
    "heapUsed": 25000000
  },
  "activeConnections": 15
}
```

### Performance Metrics
- Average message processing time
- Connection duration tracking
- Memory usage monitoring
- Database query performance

### Error Handling
- Automatic reconnection (max 10 attempts)
- Graceful degradation
- Offline support with queuing
- Comprehensive logging

## 🚦 Deployment Options

### Option 1: Integrated Server (Recommended)
Single server handling both HTTP and WebSocket:

```bash
npm run start:ws
```

### Option 2: Separate Services
Run Next.js and WebSocket on different ports:

```bash
# Terminal 1: Next.js
PORT=3000 npm start

# Terminal 2: WebSocket Server  
PORT=3001 node websocket-server.js
```

### Option 3: Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "start:ws"]
```

## 🔧 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   ```bash
   # Check if port is available
   netstat -tulpn | grep :3000
   
   # Verify environment variables
   echo $WEBSOCKET_PORT
   ```

2. **High Memory Usage**
   - Check connection cleanup
   - Monitor active sessions
   - Review rate limiting settings

3. **Message Delivery Issues**
   - Verify network connectivity
   - Check rate limiting logs
   - Review security settings

### Debug Mode

Enable detailed logging:

```env
NODE_ENV=development
DEBUG=websocket:*
```

### Performance Optimization

1. **Connection Pooling**: Limit concurrent connections
2. **Message Compression**: Enable WebSocket compression
3. **Database Optimization**: Use connection pooling
4. **Caching**: Implement Redis for session state

## 📈 Scaling Considerations

### Horizontal Scaling
- Use Redis for session state
- Implement sticky sessions
- Load balance WebSocket connections

### Database Optimization
- Index frequently queried fields
- Use read replicas for analytics
- Implement connection pooling

### Monitoring & Alerting
- Set up connection count alerts
- Monitor response times
- Track error rates

## 🆘 Support & Maintenance

### Regular Tasks
- Clean up old sessions (daily)
- Archive completed exams (weekly)
- Review security logs (daily)
- Update dependencies (monthly)

### Backup Strategy
- Database: Automated daily backups
- Session data: Real-time replication
- Config files: Version control

### Updates & Patches
- Test in staging environment
- Gradual rollout strategy
- Rollback procedures

---

For additional support or questions about the real-time exam system, refer to the main project documentation or create an issue in the project repository.