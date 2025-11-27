/**
 * Enrollments Service Layer
 * 
 * This service manages the relationship between students and classes.
 * An enrollment represents a student being registered in a specific class.
 */

import { supabase } from '@/lib/supabaseClient'
import type { Student } from './students'
import type { Class } from './classes'

/**
 * Enrollment type matching the enrollments table
 */
export interface Enrollment {
  id: string
  academy_id: string
  student_id: string
  class_id: string
  start_date: string
  end_date?: string | null
  status: 'active' | 'completed' | 'cancelled'
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Enrollment with related data
 */
export interface EnrollmentWithRelations extends Enrollment {
  student?: Student
  class?: Class
}

/**
 * List all enrollments for an academy
 */
export async function listEnrollmentsByAcademy(
  academyId: string
): Promise<EnrollmentWithRelations[]> {
  const { data, error } = await supabase
    .from('enrollments')
    .select(`
      *,
      students (
        id, full_name, english_name, grade, status
      ),
      classes (
        id, name, level_label, schedule_info
      )
    `)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('status', 'active')
    .order('created_at', { ascending: false })

  if (error) {
    console.error('Error fetching enrollments:', error)
    throw new Error(`Failed to fetch enrollments: ${error.message}`)
  }

  // Transform the data to match our interface
  const enrollments = (data || []).map(item => ({
    ...item,
    student: item.students,
    class: item.classes
  }))

  return enrollments
}

/**
 * Get enrollments for a specific student
 */
export async function getEnrollmentsByStudent(
  studentId: string,
  academyId: string
): Promise<EnrollmentWithRelations[]> {
  const { data, error } = await supabase
    .from('enrollments')
    .select(`
      *,
      classes (
        id, name, level_label, schedule_info
      )
    `)
    .eq('student_id', studentId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('status', 'active')
    .order('start_date', { ascending: false })

  if (error) {
    console.error('Error fetching student enrollments:', error)
    throw new Error(`Failed to fetch student enrollments: ${error.message}`)
  }

  const enrollments = (data || []).map(item => ({
    ...item,
    class: item.classes
  }))

  return enrollments
}

/**
 * Get enrollments for a specific class
 */
export async function getEnrollmentsByClass(
  classId: string,
  academyId: string
): Promise<EnrollmentWithRelations[]> {
  const { data, error } = await supabase
    .from('enrollments')
    .select(`
      *,
      students (
        id, full_name, english_name, grade, status
      )
    `)
    .eq('class_id', classId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('status', 'active')
    .order('start_date', { ascending: false })

  if (error) {
    console.error('Error fetching class enrollments:', error)
    throw new Error(`Failed to fetch class enrollments: ${error.message}`)
  }

  const enrollments = (data || []).map(item => ({
    ...item,
    student: item.students
  }))

  return enrollments
}

/**
 * Create a new enrollment
 */
export async function createEnrollment(
  enrollment: {
    academy_id: string
    student_id: string
    class_id: string
    start_date: string
  }
): Promise<Enrollment> {
  // Check if student is already enrolled in this class
  const { data: existing } = await supabase
    .from('enrollments')
    .select('id')
    .eq('student_id', enrollment.student_id)
    .eq('class_id', enrollment.class_id)
    .eq('academy_id', enrollment.academy_id)
    .eq('status', 'active')
    .is('deleted_at', null)
    .single()

  if (existing) {
    throw new Error('Student is already enrolled in this class')
  }

  const { data, error } = await supabase
    .from('enrollments')
    .insert({
      ...enrollment,
      status: 'active',
      is_active: true
    })
    .select()
    .single()

  if (error) {
    console.error('Error creating enrollment:', error)
    throw new Error(`Failed to create enrollment: ${error.message}`)
  }

  return data
}

/**
 * Withdraw a student from a class (soft delete)
 */
export async function withdrawEnrollment(
  enrollmentId: string,
  academyId: string,
  endDate?: string
): Promise<void> {
  const { error } = await supabase
    .from('enrollments')
    .update({
      status: 'cancelled',
      end_date: endDate || new Date().toISOString().split('T')[0],
      is_active: false,
      deleted_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })
    .eq('id', enrollmentId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)

  if (error) {
    console.error('Error withdrawing enrollment:', error)
    throw new Error(`Failed to withdraw enrollment: ${error.message}`)
  }
}

/**
 * Get available students (not enrolled in a specific class)
 */
export async function getAvailableStudentsForClass(
  classId: string,
  academyId: string
): Promise<Student[]> {
  // First get all students
  const { data: allStudents, error: studentsError } = await supabase
    .from('students')
    .select('*')
    .eq('academy_id', academyId)
    .eq('status', 'active')
    .is('deleted_at', null)

  if (studentsError) {
    throw new Error(`Failed to fetch students: ${studentsError.message}`)
  }

  // Get enrolled student IDs for this class
  const { data: enrollments, error: enrollmentsError } = await supabase
    .from('enrollments')
    .select('student_id')
    .eq('class_id', classId)
    .eq('academy_id', academyId)
    .eq('status', 'active')
    .is('deleted_at', null)

  if (enrollmentsError) {
    throw new Error(`Failed to fetch enrollments: ${enrollmentsError.message}`)
  }

  const enrolledStudentIds = new Set(enrollments?.map(e => e.student_id) || [])
  
  // Filter out enrolled students
  const availableStudents = allStudents?.filter(
    student => !enrolledStudentIds.has(student.id)
  ) || []

  return availableStudents
}