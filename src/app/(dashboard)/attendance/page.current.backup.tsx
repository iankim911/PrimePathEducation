'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Calendar, CheckCircle2, XCircle, Clock, AlertCircle, Save, Users, FileText } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface Student {
  student_id: string
  student_name: string
  english_name?: string | null
  attendance?: {
    id: string
    status: 'present' | 'absent' | 'late' | 'excused'
    note?: string | null
  } | null
}

interface Class {
  id: string
  name: string
  schedule_info?: string | null
}

type AttendanceStatus = 'present' | 'absent' | 'late' | 'excused'

export default function AttendancePage() {
  const [classes, setClasses] = useState<Class[]>([])
  const [selectedClass, setSelectedClass] = useState<string>('')
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  )
  const [students, setStudents] = useState<Student[]>([])
  const [attendanceData, setAttendanceData] = useState<Map<string, AttendanceStatus>>(new Map())
  const [notesData, setNotesData] = useState<Map<string, string>>(new Map())
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const { toast } = useToast()

  // Load classes on mount
  useEffect(() => {
    loadClasses()
  }, [])

  // Load students when class and date are selected
  useEffect(() => {
    if (selectedClass && selectedDate) {
      loadAttendanceRoster()
    } else {
      setStudents([])
      setAttendanceData(new Map())
      setNotesData(new Map())
    }
  }, [selectedClass, selectedDate])

  const loadClasses = async () => {
    try {
      const response = await fetch('/api/classes')
      const data = await response.json()
      if (data.classes) {
        setClasses(data.classes)
      }
    } catch (error) {
      console.error('Error loading classes:', error)
      toast({
        title: 'Error',
        description: 'Failed to load classes',
        variant: 'destructive',
      })
    }
  }

  const loadAttendanceRoster = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `/api/attendance?mode=roster&class_id=${selectedClass}&date=${selectedDate}`
      )
      const data = await response.json()
      
      if (data.roster) {
        setStudents(data.roster)
        
        // Initialize attendance data from existing records
        const initialData = new Map<string, AttendanceStatus>()
        const initialNotes = new Map<string, string>()
        data.roster.forEach((student: Student) => {
          if (student.attendance?.status) {
            initialData.set(student.student_id, student.attendance.status)
          }
          if (student.attendance?.note) {
            initialNotes.set(student.student_id, student.attendance.note)
          }
        })
        setAttendanceData(initialData)
        setNotesData(initialNotes)
      }
    } catch (error) {
      console.error('Error loading attendance roster:', error)
      toast({
        title: 'Error',
        description: 'Failed to load attendance roster',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const markAttendance = (studentId: string, status: AttendanceStatus) => {
    setAttendanceData(prev => {
      const newData = new Map(prev)
      newData.set(studentId, status)
      return newData
    })
  }

  const updateNote = (studentId: string, note: string) => {
    setNotesData(prev => {
      const newData = new Map(prev)
      if (note.trim()) {
        newData.set(studentId, note.trim())
      } else {
        newData.delete(studentId)
      }
      return newData
    })
  }

  const markAllPresent = () => {
    const newData = new Map<string, AttendanceStatus>()
    students.forEach(student => {
      newData.set(student.student_id, 'present')
    })
    setAttendanceData(newData)
  }

  const saveAttendance = async () => {
    if (attendanceData.size === 0) {
      toast({
        title: 'Warning',
        description: 'No attendance data to save',
        variant: 'destructive',
      })
      return
    }

    setSaving(true)
    try {
      const records = Array.from(attendanceData.entries()).map(([student_id, status]) => ({
        student_id,
        status,
        note: notesData.get(student_id) || null,
      }))

      const response = await fetch('/api/attendance/bulk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          class_id: selectedClass,
          class_date: selectedDate,
          records,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        toast({
          title: 'Success',
          description: data.message,
        })
        // Reload to show updated data
        await loadAttendanceRoster()
      } else {
        throw new Error(data.message || 'Failed to save attendance')
      }
    } catch (error) {
      console.error('Error saving attendance:', error)
      toast({
        title: 'Error',
        description: 'Failed to save attendance',
        variant: 'destructive',
      })
    } finally {
      setSaving(false)
    }
  }

  const getStatusIcon = (status: AttendanceStatus) => {
    switch (status) {
      case 'present':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />
      case 'absent':
        return <XCircle className="h-5 w-5 text-red-600" />
      case 'late':
        return <Clock className="h-5 w-5 text-yellow-600" />
      case 'excused':
        return <AlertCircle className="h-5 w-5 text-blue-600" />
      default:
        return null
    }
  }

  const getStatusBadge = (status: AttendanceStatus) => {
    const variants: Record<AttendanceStatus, string> = {
      present: 'bg-green-100 text-green-800',
      absent: 'bg-red-100 text-red-800',
      late: 'bg-yellow-100 text-yellow-800',
      excused: 'bg-blue-100 text-blue-800',
    }
    
    return (
      <Badge className={variants[status]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  const getAttendanceSummary = () => {
    const summary = {
      total: students.length,
      present: 0,
      absent: 0,
      late: 0,
      excused: 0,
      unmarked: 0,
    }

    students.forEach(student => {
      const status = attendanceData.get(student.student_id)
      if (status) {
        summary[status]++
      } else {
        summary.unmarked++
      }
    })

    return summary
  }

  const summary = getAttendanceSummary()

  return (
    <div className="space-y-6">

      {/* Class and Date Selection */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Select Class and Date</CardTitle>
          <CardDescription>Choose a class and date to take attendance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="class">Class</Label>
              <Select value={selectedClass} onValueChange={setSelectedClass}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a class" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  {classes.map(cls => (
                    <SelectItem key={cls.id} value={cls.id} className="text-gray-900">
                      {cls.name}
                      {cls.schedule_info && (
                        <span className="text-sm text-gray-500 ml-2">
                          ({cls.schedule_info})
                        </span>
                      )}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="date">Date</Label>
              <Input
                id="date"
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
              />
            </div>

            <div className="flex items-end">
              <Button 
                onClick={markAllPresent}
                variant="outline"
                className="w-full"
                disabled={students.length === 0}
              >
                <Users className="h-4 w-4 mr-2" />
                Mark All Present
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Attendance Summary */}
      {students.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{summary.total}</div>
              <p className="text-xs text-gray-600">Total Students</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-green-600">{summary.present}</div>
              <p className="text-xs text-gray-600">Present</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-red-600">{summary.absent}</div>
              <p className="text-xs text-gray-600">Absent</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-yellow-600">{summary.late}</div>
              <p className="text-xs text-gray-600">Late</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-blue-600">{summary.excused}</div>
              <p className="text-xs text-gray-600">Excused</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-gray-400">{summary.unmarked}</div>
              <p className="text-xs text-gray-600">Unmarked</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Attendance Table */}
      {students.length > 0 ? (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Mark Attendance</CardTitle>
              <CardDescription>
                Click the status buttons to mark attendance and add notes for late/absent students
              </CardDescription>
            </div>
            <Button onClick={saveAttendance} disabled={saving}>
              {saving ? (
                <>Saving...</>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Attendance
                </>
              )}
            </Button>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">Loading students...</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Student Name</TableHead>
                    <TableHead>English Name</TableHead>
                    <TableHead>Current Status</TableHead>
                    <TableHead>Mark Attendance</TableHead>
                    <TableHead>Notes</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {students.map(student => {
                    const currentStatus = attendanceData.get(student.student_id) || 
                                        student.attendance?.status
                    const currentNote = notesData.get(student.student_id) || 
                                      student.attendance?.note || ''
                    
                    return (
                      <TableRow key={student.student_id}>
                        <TableCell className="font-medium">
                          {student.student_name}
                        </TableCell>
                        <TableCell>{student.english_name || '-'}</TableCell>
                        <TableCell>
                          {currentStatus ? (
                            <div className="flex items-center gap-2">
                              {getStatusIcon(currentStatus)}
                              {getStatusBadge(currentStatus)}
                            </div>
                          ) : (
                            <span className="text-gray-400">Not marked</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant={currentStatus === 'present' ? 'default' : 'outline'}
                              className="h-8"
                              onClick={() => markAttendance(student.student_id, 'present')}
                            >
                              <CheckCircle2 className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant={currentStatus === 'absent' ? 'default' : 'outline'}
                              className="h-8"
                              onClick={() => markAttendance(student.student_id, 'absent')}
                            >
                              <XCircle className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant={currentStatus === 'late' ? 'default' : 'outline'}
                              className="h-8"
                              onClick={() => markAttendance(student.student_id, 'late')}
                            >
                              <Clock className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant={currentStatus === 'excused' ? 'default' : 'outline'}
                              className="h-8"
                              onClick={() => markAttendance(student.student_id, 'excused')}
                            >
                              <AlertCircle className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                        <TableCell className="w-64">
                          <Textarea
                            placeholder="Add note (e.g., reason for absence/lateness)..."
                            value={currentNote}
                            onChange={(e) => updateNote(student.student_id, e.target.value)}
                            className="min-h-[60px] text-sm"
                            disabled={!currentStatus || currentStatus === 'present'}
                          />
                          {currentNote && (
                            <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
                              <FileText className="h-3 w-3" />
                              Note added
                            </div>
                          )}
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      ) : selectedClass && selectedDate ? (
        <Card>
          <CardContent className="py-8">
            <p className="text-center text-gray-500">
              No students found for this class. Make sure students are enrolled in this class.
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-8">
            <p className="text-center text-gray-500">
              Please select a class and date to view attendance
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}