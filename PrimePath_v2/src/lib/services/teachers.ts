/**
 * Teachers Service Layer
 * 
 * This service encapsulates all data access and business logic for teachers.
 * Teachers are users with role='teacher' in the users table.
 */

import { supabase } from '@/lib/supabaseClient'

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