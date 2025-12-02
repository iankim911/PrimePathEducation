"use client"

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  MessageSquare, 
  Send, 
  Clock, 
  User, 
  AlertCircle,
  CheckCircle2,
  Users,
  Megaphone,
  FileText
} from 'lucide-react'
import type { ExamMessage } from '@/lib/websocket/socketManager'

interface SessionMessagesProps {
  messages: ExamMessage[]
  onBroadcastMessage: (message: string, type?: 'announcement' | 'warning' | 'reminder') => void
  isConnected: boolean
}

export function SessionMessages({
  messages,
  onBroadcastMessage,
  isConnected
}: SessionMessagesProps) {
  const [newMessage, setNewMessage] = useState('')
  const [messageType, setMessageType] = useState<'announcement' | 'warning' | 'reminder'>('announcement')
  const [filter, setFilter] = useState<string>('all')
  
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = () => {
    if (newMessage.trim() && isConnected) {
      onBroadcastMessage(newMessage.trim(), messageType)
      setNewMessage('')
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'session_start':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'session_end':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'answer_submitted':
        return <FileText className="h-4 w-4 text-blue-500" />
      case 'student_joined':
        return <User className="h-4 w-4 text-green-500" />
      case 'student_left':
        return <User className="h-4 w-4 text-red-500" />
      case 'broadcast_message':
        return <Megaphone className="h-4 w-4 text-purple-500" />
      case 'time_warning':
        return <Clock className="h-4 w-4 text-orange-500" />
      default:
        return <MessageSquare className="h-4 w-4 text-gray-500" />
    }
  }

  const getMessageTypeLabel = (type: string) => {
    switch (type) {
      case 'session_start':
        return 'Session Started'
      case 'session_end':
        return 'Session Ended'
      case 'answer_submitted':
        return 'Answer Submitted'
      case 'student_joined':
        return 'Student Joined'
      case 'student_left':
        return 'Student Left'
      case 'broadcast_message':
        return 'Broadcast'
      case 'time_warning':
        return 'Time Warning'
      default:
        return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
  }

  const getMessageTypeColor = (type: string) => {
    switch (type) {
      case 'session_start':
        return 'bg-green-100 text-green-800'
      case 'session_end':
        return 'bg-red-100 text-red-800'
      case 'answer_submitted':
        return 'bg-blue-100 text-blue-800'
      case 'student_joined':
        return 'bg-green-100 text-green-800'
      case 'student_left':
        return 'bg-red-100 text-red-800'
      case 'broadcast_message':
        return 'bg-purple-100 text-purple-800'
      case 'time_warning':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getBroadcastTypeColor = (type?: string) => {
    switch (type) {
      case 'warning':
        return 'bg-red-100 text-red-800'
      case 'reminder':
        return 'bg-yellow-100 text-yellow-800'
      case 'announcement':
      default:
        return 'bg-blue-100 text-blue-800'
    }
  }

  const formatMessageContent = (message: ExamMessage) => {
    switch (message.type) {
      case 'session_start':
        return 'Exam session has started. Students can now begin answering questions.'
      
      case 'session_end':
        const reason = message.data?.reason
        if (reason === 'time_limit_reached') {
          return 'Session ended automatically - time limit reached.'
        }
        return 'Exam session has ended. All answers have been saved.'
      
      case 'answer_submitted':
        const questionId = message.data?.questionId
        const studentId = message.data?.studentId
        const timeSpent = message.data?.timeSpent
        return `Student ${studentId || 'Unknown'} submitted answer for question ${questionId || 'N/A'}${timeSpent ? ` (${timeSpent}s)` : ''}`
      
      case 'student_joined':
        return `${message.data?.userName || 'A student'} joined the session`
      
      case 'student_left':
        return `${message.data?.userName || 'A student'} left the session`
      
      case 'broadcast_message':
        return message.data?.message || 'No message content'
      
      case 'time_warning':
        return message.data?.message || 'Time warning issued'
      
      default:
        return JSON.stringify(message.data) || 'Unknown message type'
    }
  }

  // Filter messages
  const filteredMessages = messages.filter(message => {
    if (filter === 'all') return true
    if (filter === 'system') {
      return ['session_start', 'session_end', 'time_warning'].includes(message.type)
    }
    if (filter === 'students') {
      return ['student_joined', 'student_left', 'answer_submitted'].includes(message.type)
    }
    if (filter === 'broadcasts') {
      return message.type === 'broadcast_message'
    }
    return true
  })

  const messageStats = {
    total: messages.length,
    submissions: messages.filter(m => m.type === 'answer_submitted').length,
    broadcasts: messages.filter(m => m.type === 'broadcast_message').length,
    students: new Set(messages.filter(m => m.type === 'student_joined').map(m => m.data?.userId)).size
  }

  return (
    <div className="space-y-6">
      {/* Message Statistics */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-blue-600">Total Messages</p>
                <p className="text-2xl font-bold text-blue-900">{messageStats.total}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-green-600">Submissions</p>
                <p className="text-2xl font-bold text-green-900">{messageStats.submissions}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Megaphone className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-purple-600">Broadcasts</p>
                <p className="text-2xl font-bold text-purple-900">{messageStats.broadcasts}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-orange-600">Active Students</p>
                <p className="text-2xl font-bold text-orange-900">{messageStats.students}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Send Message */}
      <Card className="bg-white">
        <CardHeader>
          <CardTitle className="text-gray-900">Send Broadcast Message</CardTitle>
          <CardDescription>Send a message to all students in this session</CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div className="grid grid-cols-4 gap-4">
            <div className="col-span-3">
              <Textarea
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message to students..."
                className="text-gray-900"
                rows={3}
                disabled={!isConnected}
              />
            </div>
            
            <div className="space-y-2">
              <Select value={messageType} onValueChange={(value: any) => setMessageType(value)}>
                <SelectTrigger className="text-gray-900">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="announcement">📢 Announcement</SelectItem>
                  <SelectItem value="warning">⚠️ Warning</SelectItem>
                  <SelectItem value="reminder">💡 Reminder</SelectItem>
                </SelectContent>
              </Select>
              
              <Button 
                onClick={handleSendMessage}
                disabled={!newMessage.trim() || !isConnected}
                className="w-full bg-gray-900 hover:bg-gray-800 text-white"
              >
                <Send className="h-4 w-4 mr-2" />
                Send
              </Button>
            </div>
          </div>

          {!isConnected && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <p className="text-red-800 text-sm">Not connected. Cannot send messages.</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Messages List */}
      <Card className="bg-white">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-gray-900">Session Messages</CardTitle>
              <CardDescription>Real-time activity log and communication</CardDescription>
            </div>
            
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="w-48 text-gray-900">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-white">
                <SelectItem value="all">All Messages</SelectItem>
                <SelectItem value="system">System Events</SelectItem>
                <SelectItem value="students">Student Activity</SelectItem>
                <SelectItem value="broadcasts">Broadcasts</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        
        <CardContent>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filteredMessages.length === 0 ? (
              <div className="text-center py-8">
                <MessageSquare className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                <p className="text-gray-600">No messages yet</p>
                <p className="text-sm text-gray-500">
                  Messages will appear here as the session progresses
                </p>
              </div>
            ) : (
              filteredMessages.map((message, index) => (
                <div 
                  key={index}
                  className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
                >
                  <div className="flex-shrink-0">
                    {getMessageIcon(message.type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <Badge variant="secondary" className={`text-xs ${getMessageTypeColor(message.type)}`}>
                        {getMessageTypeLabel(message.type)}
                      </Badge>
                      
                      {message.type === 'broadcast_message' && message.data?.messageType && (
                        <Badge variant="secondary" className={`text-xs ${getBroadcastTypeColor(message.data.messageType)}`}>
                          {message.data.messageType.toUpperCase()}
                        </Badge>
                      )}
                      
                      <span className="text-xs text-gray-500">
                        {formatTimestamp(message.timestamp)}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {formatMessageContent(message)}
                    </p>
                    
                    {message.from && (
                      <p className="text-xs text-gray-500 mt-1">
                        From: {message.from}
                      </p>
                    )}
                  </div>
                </div>
              ))
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}