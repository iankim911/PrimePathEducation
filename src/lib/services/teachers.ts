/**
 * Teachers Service Layer
 * 
 * This service encapsulates all data access and business logic for teachers.
 * Teachers are users with role='teacher' in the users table.
 */

import { supabase } from '@/lib/supabaseClient'
import type { Class } from './classes'

/**
 * User type matching the users table in db/schema.sql
 */
export interface User {
  id: string
  academy_id: string
  email: string
  full_name: string
  role: 'admin' | 'teacher'
  password_hash?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Teacher type (User with role='teacher')
 */
export type Teacher = User & {
  role: 'teacher'
}

/**
 * Class-Teacher assignment type matching the class_teachers table
 */
export interface ClassTeacher {
  id: string
  academy_id: string
  class_id: string
  teacher_id: string
  role: 'main' | 'sub' | 'native'
  is_primary: boolean
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Extended ClassTeacher with teacher information
 */
export interface ClassTeacherWithDetails extends ClassTeacher {
  teacher: Teacher
}

/**
 * Extended ClassTeacher with class information (for teacher's class assignments)
 */
export interface TeacherClassAssignment extends ClassTeacher {
  class: Class
}


/**
 * Days of the week (0 = Sunday, 6 = Saturday)
 */
export type DayOfWeek = 0 | 1 | 2 | 3 | 4 | 5 | 6

/**
 * Teacher weekly availability schedule
 */
export interface TeacherAvailability {
  id: string
  academy_id: string
  teacher_id: string
  day_of_week: DayOfWeek
  start_time: string  // Format: "HH:MM" (24-hour format)
  end_time: string    // Format: "HH:MM" (24-hour format)
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Grouped availability by day for easier display
 */
export interface DayAvailability {
  day: DayOfWeek
  day_name: string
  time_slots: {
    start_time: string
    end_time: string
    id: string
  }[]
}

/**
 * List all teachers for a specific academy
 */
export async function listTeachersByAcademy(academyId: string): Promise<Teacher[]> {
  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('academy_id', academyId)
    .eq('role', 'teacher')
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('full_name', { ascending: true })

  if (error) {
    console.error('Error fetching teachers:', error)
    throw new Error(`Failed to fetch teachers: ${error.message}`)
  }

  return data || []
}

/**
 * Get a single teacher by ID
 */
export async function getTeacherById(
  teacherId: string,
  academyId: string
): Promise<Teacher | null> {
  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('id', teacherId)
    .eq('academy_id', academyId)
    .eq('role', 'teacher')
    .is('deleted_at', null)
    .single()

  if (error) {
    if (error.code === 'PGRST116') {
      return null // Record not found
    }
    console.error('Error fetching teacher:', error)
    throw new Error(`Failed to fetch teacher: ${error.message}`)
  }

  return data
}

/**
 * Create a new teacher
 */
export async function createTeacher(
  teacherData: Omit<Teacher, 'id' | 'created_at' | 'updated_at' | 'deleted_at'>
): Promise<Teacher> {
  const { data, error } = await supabase
    .from('users')
    .insert({
      ...teacherData,
      role: 'teacher',
    })
    .select()
    .single()

  if (error) {
    console.error('Error creating teacher:', error)
    throw new Error(`Failed to create teacher: ${error.message}`)
  }

  return data
}

/**
 * Update an existing teacher
 */
export async function updateTeacher(
  teacherId: string,
  academyId: string,
  updates: Partial<Omit<Teacher, 'id' | 'academy_id' | 'role' | 'created_at' | 'updated_at'>>
): Promise<Teacher> {
  const { data, error } = await supabase
    .from('users')
    .update({
      ...updates,
      updated_at: new Date().toISOString(),
    })
    .eq('id', teacherId)
    .eq('academy_id', academyId)
    .eq('role', 'teacher')
    .is('deleted_at', null)
    .select()
    .single()

  if (error) {
    console.error('Error updating teacher:', error)
    throw new Error(`Failed to update teacher: ${error.message}`)
  }

  return data
}

/**
 * Soft delete a teacher
 */
export async function deleteTeacher(
  teacherId: string,
  academyId: string
): Promise<void> {
  const { error } = await supabase
    .from('users')
    .update({
      deleted_at: new Date().toISOString(),
      is_active: false,
      updated_at: new Date().toISOString(),
    })
    .eq('id', teacherId)
    .eq('academy_id', academyId)
    .eq('role', 'teacher')
    .is('deleted_at', null)

  if (error) {
    console.error('Error deleting teacher:', error)
    throw new Error(`Failed to delete teacher: ${error.message}`)
  }
}

/**
 * Assign a teacher to a class
 */
export async function assignTeacherToClass(
  academyId: string,
  classId: string,
  teacherId: string,
  role: 'main' | 'sub' | 'native' = 'main',
  isPrimary: boolean = false
): Promise<ClassTeacher> {
  // If setting as primary, first unset any existing primary teacher for this class
  if (isPrimary) {
    await supabase
      .from('class_teachers')
      .update({ is_primary: false, updated_at: new Date().toISOString() })
      .eq('academy_id', academyId)
      .eq('class_id', classId)
      .eq('is_primary', true)
      .is('deleted_at', null)
  }

  const { data, error } = await supabase
    .from('class_teachers')
    .insert({
      academy_id: academyId,
      class_id: classId,
      teacher_id: teacherId,
      role,
      is_primary: isPrimary,
    })
    .select()
    .single()

  if (error) {
    console.error('Error assigning teacher to class:', error)
    throw new Error(`Failed to assign teacher to class: ${error.message}`)
  }

  return data
}

/**
 * Remove a teacher from a class
 */
export async function removeTeacherFromClass(
  academyId: string,
  classId: string,
  teacherId: string
): Promise<void> {
  const { error } = await supabase
    .from('class_teachers')
    .update({
      deleted_at: new Date().toISOString(),
      is_active: false,
      updated_at: new Date().toISOString(),
    })
    .eq('academy_id', academyId)
    .eq('class_id', classId)
    .eq('teacher_id', teacherId)
    .is('deleted_at', null)

  if (error) {
    console.error('Error removing teacher from class:', error)
    throw new Error(`Failed to remove teacher from class: ${error.message}`)
  }
}

/**
 * Get teachers assigned to a specific class
 */
export async function getTeachersByClass(
  academyId: string,
  classId: string
): Promise<ClassTeacherWithDetails[]> {
  const { data, error } = await supabase
    .from('class_teachers')
    .select(`
      *,
      teacher:users!inner(*)
    `)
    .eq('academy_id', academyId)
    .eq('class_id', classId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('is_primary', { ascending: false })
    .order('role', { ascending: true })

  if (error) {
    console.error('Error fetching teachers by class:', error)
    throw new Error(`Failed to fetch teachers by class: ${error.message}`)
  }

  return data || []
}

/**
 * Get primary teacher for a class
 */
export async function getPrimaryTeacherByClass(
  academyId: string,
  classId: string
): Promise<Teacher | null> {
  const { data, error } = await supabase
    .from('class_teachers')
    .select(`
      teacher:users!inner(*)
    `)
    .eq('academy_id', academyId)
    .eq('class_id', classId)
    .eq('is_primary', true)
    .is('deleted_at', null)
    .eq('is_active', true)
    .single()

  if (error) {
    if (error.code === 'PGRST116') {
      return null // No primary teacher found
    }
    console.error('Error fetching primary teacher:', error)
    throw new Error(`Failed to fetch primary teacher: ${error.message}`)
  }

  return (data as any)?.teacher || null
}

/**
 * Get classes assigned to a specific teacher
 */
export async function getClassesByTeacher(
  academyId: string,
  teacherId: string
): Promise<TeacherClassAssignment[]> {
  const { data, error } = await supabase
    .from('class_teachers')
    .select(`
      *,
      class:classes!inner(*)
    `)
    .eq('academy_id', academyId)
    .eq('teacher_id', teacherId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('is_primary', { ascending: false })
    .order('role', { ascending: true })

  if (error) {
    console.error('Error fetching classes by teacher:', error)
    throw new Error(`Failed to fetch classes by teacher: ${error.message}`)
  }

  return data || []
}

/**
 * Extended Teacher with workload information
 */
export interface TeacherWithWorkload extends Teacher {
  class_count: number
  student_count: number
  classes: TeacherClassAssignment[]
}

/**
 * Get teachers with their workload (class and student counts)
 */
export async function getTeachersWithWorkload(academyId: string): Promise<TeacherWithWorkload[]> {
  // First get all teachers
  const teachers = await listTeachersByAcademy(academyId)
  
  // Then get workload data for each teacher
  const teachersWithWorkload = await Promise.all(
    teachers.map(async (teacher) => {
      // Get teacher's class assignments
      const classes = await getClassesByTeacher(academyId, teacher.id)
      
      // Get student count across all their classes
      let enrollmentData = null
      let enrollmentError = null
      
      if (classes.length > 0) {
        const result = await supabase
          .from('enrollments')
          .select('id')
          .eq('academy_id', academyId)
          .in('class_id', classes.map(c => c.class_id))
          .eq('status', 'active')
          .is('deleted_at', null)
        
        enrollmentData = result.data
        enrollmentError = result.error
      }

      if (enrollmentError) {
        console.error('Error fetching student count for teacher:', enrollmentError)
      }

      return {
        ...teacher,
        class_count: classes.length,
        student_count: enrollmentData?.length || 0,
        classes
      } as TeacherWithWorkload
    })
  )
  
  return teachersWithWorkload
}


/**
 * Get teacher's weekly availability schedule
 */
export async function getTeacherAvailability(
  academyId: string,
  teacherId: string
): Promise<DayAvailability[]> {
  // TODO: Replace with actual database query when teacher_availability table exists
  
  // const { data, error } = await supabase
  //   .from('teacher_availability')
  //   .select('*')
  //   .eq('academy_id', academyId)
  //   .eq('teacher_id', teacherId)
  //   .is('deleted_at', null)
  //   .eq('is_active', true)
  //   .order('day_of_week', { ascending: true })
  //   .order('start_time', { ascending: true })

  // if (error) {
  //   console.error('Error fetching teacher availability:', error)
  //   throw new Error(`Failed to fetch teacher availability: ${error.message}`)
  // }

  // Group by day
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const groupedAvailability: DayAvailability[] = []

  for (let day = 0; day < 7; day++) {
    groupedAvailability.push({
      day: day as DayOfWeek,
      day_name: dayNames[day],
      time_slots: []
    })
  }

  return groupedAvailability
}

/**
 * Add teacher availability time slot
 */
export async function addTeacherAvailability(
  academyId: string,
  teacherId: string,
  dayOfWeek: DayOfWeek,
  startTime: string,
  endTime: string
): Promise<TeacherAvailability> {
  // TODO: Replace with actual database operation when table exists
  
  // Validate time format and logic
  if (startTime >= endTime) {
    throw new Error('Start time must be before end time')
  }

  // const { data, error } = await supabase
  //   .from('teacher_availability')
  //   .insert({
  //     academy_id: academyId,
  //     teacher_id: teacherId,
  //     day_of_week: dayOfWeek,
  //     start_time: startTime,
  //     end_time: endTime,
  //   })
  //   .select()
  //   .single()

  // if (error) {
  //   console.error('Error adding teacher availability:', error)
  //   throw new Error(`Failed to add teacher availability: ${error.message}`)
  // }

  // return data

  // Mock return for now
  return {
    id: `temp-avail-${Date.now()}`,
    academy_id: academyId,
    teacher_id: teacherId,
    day_of_week: dayOfWeek,
    start_time: startTime,
    end_time: endTime,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
}

/**
 * Remove teacher availability time slot
 */
export async function removeTeacherAvailability(
  academyId: string,
  availabilityId: string
): Promise<void> {
  // TODO: Replace with actual database operation when table exists
  
  // const { error } = await supabase
  //   .from('teacher_availability')
  //   .update({
  //     deleted_at: new Date().toISOString(),
  //     is_active: false,
  //     updated_at: new Date().toISOString(),
  //   })
  //   .eq('id', availabilityId)
  //   .eq('academy_id', academyId)
  //   .is('deleted_at', null)

  // if (error) {
  //   console.error('Error removing teacher availability:', error)
  //   throw new Error(`Failed to remove teacher availability: ${error.message}`)
  // }
}

/**
 * Helper function to get day name from day number
 */
export function getDayName(day: DayOfWeek): string {
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  return dayNames[day]
}

/**
 * Helper function to format time for display
 */
export function formatTime(time: string): string {
  // Convert "HH:MM" to "HH:MM AM/PM"
  const [hours, minutes] = time.split(':').map(Number)
  const ampm = hours >= 12 ? 'PM' : 'AM'
  const displayHours = hours % 12 || 12
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${ampm}`
}