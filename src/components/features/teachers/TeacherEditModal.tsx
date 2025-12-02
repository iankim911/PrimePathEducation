"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Edit, Plus, X, Loader2, Clock } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import type { Teacher, DayAvailability, DayOfWeek } from '@/lib/services/teachers'
import type { Class } from '@/lib/services/classes'

interface TeacherEditModalProps {
  teacher: Teacher
  onSuccess?: () => void
}

interface ClassAssignment {
  id: string
  class_id: string
  class_name: string
  role: 'main' | 'sub' | 'native'
  is_primary: boolean
}


export function TeacherEditModal({ teacher, onSuccess }: TeacherEditModalProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [classes, setClasses] = useState<Class[]>([])
  const [assignments, setAssignments] = useState<ClassAssignment[]>([])
  const [selectedClassId, setSelectedClassId] = useState<string>('')
  const [selectedRole, setSelectedRole] = useState<'main' | 'sub' | 'native'>('main')
  const [hasChanges, setHasChanges] = useState(false)
  

  // Schedule availability state
  const [weeklyAvailability, setWeeklyAvailability] = useState<DayAvailability[]>([])
  const [selectedDay, setSelectedDay] = useState<DayOfWeek>(1) // Monday default
  const [selectedStartTime, setSelectedStartTime] = useState<string>('09:00')
  const [selectedEndTime, setSelectedEndTime] = useState<string>('17:00')
  
  const { toast } = useToast()

  // Fetch available classes
  const fetchClasses = async () => {
    try {
      const response = await fetch('/api/classes')
      if (!response.ok) throw new Error('Failed to fetch classes')
      const data = await response.json()
      setClasses(data.classes)
    } catch (error) {
      console.error('Error fetching classes:', error)
    }
  }

  // Fetch teacher's current assignments
  const fetchAssignments = async () => {
    try {
      const response = await fetch(`/api/teachers/${teacher.id}/assignments`)
      if (!response.ok) throw new Error('Failed to fetch assignments')
      const data = await response.json()
      
      // Transform the data to match our local interface
      const transformedAssignments: ClassAssignment[] = data.assignments.map((a: any) => ({
        id: a.id,
        class_id: a.class_id,
        class_name: a.class?.name || 'Unknown Class',
        role: a.role,
        is_primary: a.is_primary
      }))
      
      setAssignments(transformedAssignments)
    } catch (error) {
      console.error('Error fetching assignments:', error)
      toast({
        title: "Error",
        description: "Failed to load class assignments",
        variant: "destructive",
      })
    }
  }


  // Fetch teacher's availability schedule (mock for now)
  const fetchAvailability = async () => {
    // TODO: Replace with actual API call when teacher_availability table exists
    // For now, show empty schedule for all days
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    const emptySchedule = dayNames.map((dayName, index) => ({
      day: index as DayOfWeek,
      day_name: dayName,
      time_slots: []
    }))
    setWeeklyAvailability(emptySchedule)
  }

  useEffect(() => {
    if (open) {
      fetchClasses()
      fetchAssignments()
      fetchAvailability()
      setHasChanges(false) // Reset changes flag when modal opens
    }
  }, [open])

  const handleAddAssignment = async () => {
    if (!selectedClassId) return

    setLoading(true)
    try {
      const selectedClass = classes.find(c => c.id === selectedClassId)
      if (!selectedClass) return

      const response = await fetch(`/api/teachers/${teacher.id}/assignments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          class_id: selectedClassId,
          role: selectedRole,
          is_primary: false
        })
      })

      if (!response.ok) {
        throw new Error('Failed to add assignment')
      }

      const data = await response.json()

      // Add to local state
      const newAssignment: ClassAssignment = {
        id: data.assignment.id,
        class_id: selectedClassId,
        class_name: selectedClass.name,
        role: selectedRole,
        is_primary: false
      }

      setAssignments(prev => [...prev, newAssignment])
      setSelectedClassId('')
      setSelectedRole('main')
      setHasChanges(true)

      toast({
        title: "Assignment Added",
        description: `${teacher.full_name} assigned to ${selectedClass.name}`,
      })
    } catch (error) {
      console.error('Error adding assignment:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to add class assignment",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveAssignment = async (assignment: ClassAssignment) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/teachers/${teacher.id}/assignments?class_id=${assignment.class_id}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Failed to remove assignment')
      }

      setAssignments(prev => prev.filter(a => a.id !== assignment.id))
      setHasChanges(true)

      toast({
        title: "Assignment Removed",
        description: "Class assignment removed successfully",
      })
    } catch (error) {
      console.error('Error removing assignment:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to remove assignment",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }


  const handleAddAvailability = async () => {
    if (!selectedStartTime || !selectedEndTime) return
    if (selectedStartTime >= selectedEndTime) {
      toast({
        title: "Invalid Time Range",
        description: "Start time must be before end time",
        variant: "destructive",
      })
      return
    }

    setLoading(true)
    try {
      // TODO: Replace with actual API call when ready
      const newTimeSlot = {
        id: `temp-avail-${Date.now()}`,
        start_time: selectedStartTime,
        end_time: selectedEndTime
      }

      setWeeklyAvailability(prev => prev.map(day => 
        day.day === selectedDay 
          ? { ...day, time_slots: [...day.time_slots, newTimeSlot] }
          : day
      ))

      setSelectedStartTime('09:00')
      setSelectedEndTime('17:00')

      const dayName = weeklyAvailability.find(d => d.day === selectedDay)?.day_name || 'Selected day'
      toast({
        title: "Availability Added",
        description: `Added availability for ${dayName} from ${selectedStartTime} to ${selectedEndTime}`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add availability",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveAvailability = async (dayIndex: DayOfWeek, slotId: string) => {
    setLoading(true)
    try {
      // TODO: Replace with actual API call when ready
      setWeeklyAvailability(prev => prev.map(day => 
        day.day === dayIndex
          ? { ...day, time_slots: day.time_slots.filter(slot => slot.id !== slotId) }
          : day
      ))

      toast({
        title: "Availability Removed",
        description: "Time slot removed successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to remove availability",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (time: string) => {
    // Convert "HH:MM" to "HH:MM AM/PM"
    const [hours, minutes] = time.split(':').map(Number)
    const ampm = hours >= 12 ? 'PM' : 'AM'
    const displayHours = hours % 12 || 12
    return `${displayHours}:${minutes.toString().padStart(2, '0')} ${ampm}`
  }

  const availableClasses = classes.filter(
    c => !assignments.some(a => a.class_id === c.id)
  )

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="border-gray-300 hover:bg-gray-50"
        >
          <Edit className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Manage Teacher Assignments</DialogTitle>
          <DialogDescription>
            Manage class assignments for {teacher.full_name}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Current Assignments */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">
              Current Class Assignments
            </h4>
            {assignments.length === 0 ? (
              <p className="text-sm text-gray-500 italic">
                No classes assigned yet
              </p>
            ) : (
              <div className="space-y-2">
                {assignments.map((assignment) => (
                  <div
                    key={assignment.id}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-md"
                  >
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-gray-900">
                        {assignment.class_name}
                      </span>
                      <Badge
                        variant="secondary"
                        className="text-xs"
                      >
                        {assignment.role}
                      </Badge>
                      {assignment.is_primary && (
                        <Badge className="text-xs bg-blue-100 text-blue-800">
                          Primary
                        </Badge>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveAssignment(assignment)}
                      disabled={loading}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Add New Assignment */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">
              Add Class Assignment
            </h4>
            <div className="flex gap-2">
              <Select value={selectedClassId} onValueChange={setSelectedClassId}>
                <SelectTrigger className="flex-1">
                  <SelectValue placeholder="Select a class" />
                </SelectTrigger>
                <SelectContent>
                  {availableClasses.map((cls) => (
                    <SelectItem key={cls.id} value={cls.id}>
                      {cls.name}
                      {cls.level_label && ` (${cls.level_label})`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedRole} onValueChange={(value: 'main' | 'sub' | 'native') => setSelectedRole(value)}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="main">Main</SelectItem>
                  <SelectItem value="sub">Sub</SelectItem>
                  <SelectItem value="native">Native</SelectItem>
                </SelectContent>
              </Select>

              <Button
                onClick={handleAddAssignment}
                disabled={!selectedClassId || loading}
                size="sm"
                className="bg-gray-900 hover:bg-gray-800"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
              </Button>
            </div>
            {availableClasses.length === 0 && classes.length > 0 && (
              <p className="text-sm text-gray-500 mt-2">
                All available classes are already assigned
              </p>
            )}
          </div>


          {/* Schedule & Availability */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Weekly Schedule & Availability
            </h4>
            
            {/* Weekly availability display */}
            <div className="space-y-3 mb-4">
              {weeklyAvailability.map((day) => (
                <div key={day.day} className="border border-gray-200 rounded-md p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900">{day.day_name}</span>
                    {day.time_slots.length === 0 && (
                      <span className="text-sm text-gray-400 italic">Not available</span>
                    )}
                  </div>
                  {day.time_slots.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {day.time_slots.map((slot) => (
                        <div
                          key={slot.id}
                          className="flex items-center gap-2 bg-gray-50 px-2 py-1 rounded text-sm"
                        >
                          <span>
                            {formatTime(slot.start_time)} - {formatTime(slot.end_time)}
                          </span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveAvailability(day.day, slot.id)}
                            disabled={loading}
                            className="h-4 w-4 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Add new availability */}
            <div>
              <h5 className="text-sm font-medium text-gray-900 mb-3">
                Add Availability
              </h5>
              <div className="flex gap-2 items-end">
                <div className="flex-1">
                  <label className="text-xs text-gray-500 mb-1 block">Day</label>
                  <Select 
                    value={selectedDay.toString()} 
                    onValueChange={(value) => setSelectedDay(parseInt(value) as DayOfWeek)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {weeklyAvailability.map((day) => (
                        <SelectItem key={day.day} value={day.day.toString()}>
                          {day.day_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex-1">
                  <label className="text-xs text-gray-500 mb-1 block">Start Time</label>
                  <input
                    type="time"
                    value={selectedStartTime}
                    onChange={(e) => setSelectedStartTime(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
                
                <div className="flex-1">
                  <label className="text-xs text-gray-500 mb-1 block">End Time</label>
                  <input
                    type="time"
                    value={selectedEndTime}
                    onChange={(e) => setSelectedEndTime(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>

                <Button
                  onClick={handleAddAvailability}
                  disabled={loading}
                  size="sm"
                  className="bg-gray-900 hover:bg-gray-800"
                >
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => {
              setOpen(false)
              setHasChanges(false) // Reset changes flag
            }}
            className="border-gray-300"
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              setOpen(false)
              setHasChanges(false) // Reset changes flag
              // Always refresh the parent table when Done is clicked to ensure data is synced
              // Remove the conditional check - always refresh when Done is clicked
              setTimeout(() => {
                onSuccess?.()
              }, 100) // Small delay to ensure modal closes first
            }}
            className="bg-gray-900 hover:bg-gray-800"
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Done'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}