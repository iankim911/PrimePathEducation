/**
 * Students Service Layer
 * 
 * This service encapsulates all data access and business logic for students.
 * Components should never directly query Supabase; they should use these service functions.
 */

import { supabase } from '@/lib/supabaseClient'

/**
 * Student type matching the students table in db/schema.sql
 */
export interface Student {
  id: string
  academy_id: string
  full_name: string
  english_name?: string | null
  student_code?: string | null
  school_name?: string | null
  grade?: number | null
  status: 'active' | 'paused' | 'withdrawn'
  parent_name?: string | null
  parent_phone?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * List all students for a specific academy
 * @param academyId - The UUID of the academy
 * @returns Promise<Student[]> - Array of active students
 */
export async function listStudentsByAcademy(academyId: string): Promise<Student[]> {
  const { data, error } = await supabase
    .from('students')
    .select('*')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('full_name', { ascending: true })

  if (error) {
    console.error('Error fetching students:', error)
    throw new Error(`Failed to fetch students: ${error.message}`)
  }

  return data || []
}

/**
 * Get a single student by ID
 * @param studentId - The UUID of the student
 * @param academyId - The UUID of the academy (for multi-tenancy validation)
 * @returns Promise<Student | null> - The student or null if not found
 */
export async function getStudentById(
  studentId: string,
  academyId: string
): Promise<Student | null> {
  const { data, error } = await supabase
    .from('students')
    .select('*')
    .eq('id', studentId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .single()

  if (error) {
    if (error.code === 'PGRST116') {
      return null // Record not found
    }
    console.error('Error fetching student:', error)
    throw new Error(`Failed to fetch student: ${error.message}`)
  }

  return data
}

/**
 * Create a new student
 * @param student - The student data (without id, created_at, updated_at)
 * @returns Promise<Student> - The created student
 */
export async function createStudent(
  student: Omit<Student, 'id' | 'created_at' | 'updated_at' | 'deleted_at'>
): Promise<Student> {
  const { data, error } = await supabase
    .from('students')
    .insert(student)
    .select()
    .single()

  if (error) {
    console.error('Error creating student:', error)
    throw new Error(`Failed to create student: ${error.message}`)
  }

  return data
}

/**
 * Update an existing student
 * @param studentId - The UUID of the student to update
 * @param academyId - The UUID of the academy (for multi-tenancy validation)
 * @param updates - Partial student data to update
 * @returns Promise<Student> - The updated student
 */
export async function updateStudent(
  studentId: string,
  academyId: string,
  updates: Partial<Omit<Student, 'id' | 'academy_id' | 'created_at' | 'updated_at'>>
): Promise<Student> {
  const { data, error } = await supabase
    .from('students')
    .update({
      ...updates,
      updated_at: new Date().toISOString(),
    })
    .eq('id', studentId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .select()
    .single()

  if (error) {
    console.error('Error updating student:', error)
    throw new Error(`Failed to update student: ${error.message}`)
  }

  return data
}

/**
 * Soft delete a student (sets deleted_at timestamp)
 * @param studentId - The UUID of the student to delete
 * @param academyId - The UUID of the academy (for multi-tenancy validation)
 * @returns Promise<void>
 */
export async function deleteStudent(
  studentId: string,
  academyId: string
): Promise<void> {
  const { error } = await supabase
    .from('students')
    .update({
      deleted_at: new Date().toISOString(),
      is_active: false,
      updated_at: new Date().toISOString(),
    })
    .eq('id', studentId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)

  if (error) {
    console.error('Error deleting student:', error)
    throw new Error(`Failed to delete student: ${error.message}`)
  }
}

/**
 * Get students by status
 * @param academyId - The UUID of the academy
 * @param status - The student status to filter by
 * @returns Promise<Student[]> - Array of students with the specified status
 */
export async function getStudentsByStatus(
  academyId: string,
  status: Student['status']
): Promise<Student[]> {
  const { data, error } = await supabase
    .from('students')
    .select('*')
    .eq('academy_id', academyId)
    .eq('status', status)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('full_name', { ascending: true })

  if (error) {
    console.error('Error fetching students by status:', error)
    throw new Error(`Failed to fetch students by status: ${error.message}`)
  }

  return data || []
}

/**
 * Search students by name
 * @param academyId - The UUID of the academy
 * @param searchTerm - The search term to match against full_name and english_name
 * @returns Promise<Student[]> - Array of matching students
 */
export async function searchStudents(
  academyId: string,
  searchTerm: string
): Promise<Student[]> {
  const { data, error } = await supabase
    .from('students')
    .select('*')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .or(`full_name.ilike.%${searchTerm}%,english_name.ilike.%${searchTerm}%`)
    .order('full_name', { ascending: true })

  if (error) {
    console.error('Error searching students:', error)
    throw new Error(`Failed to search students: ${error.message}`)
  }

  return data || []
}