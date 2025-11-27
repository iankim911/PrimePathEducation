/**
 * Classes Service Layer
 * 
 * This service encapsulates all data access and business logic for classes.
 * Classes represent the actual courses/sessions that students can enroll in.
 */

import { supabase } from '@/lib/supabaseClient'
import type { Teacher } from './teachers'

/**
 * Class type matching the classes table in db/schema.sql
 */
export interface Class {
  id: string
  academy_id: string
  name: string
  level_label?: string | null
  target_grade?: number | null
  schedule_info?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

/**
 * Extended Class type with primary teacher information
 */
export interface ClassWithTeacher extends Class {
  primary_teacher?: Teacher | null
}

/**
 * List all classes for a specific academy
 */
export async function listClassesByAcademy(academyId: string): Promise<Class[]> {
  const { data, error } = await supabase
    .from('classes')
    .select('*')
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('name', { ascending: true })

  if (error) {
    console.error('Error fetching classes:', error)
    throw new Error(`Failed to fetch classes: ${error.message}`)
  }

  return data || []
}

/**
 * Get a single class by ID
 */
export async function getClassById(
  classId: string,
  academyId: string
): Promise<Class | null> {
  const { data, error } = await supabase
    .from('classes')
    .select('*')
    .eq('id', classId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .single()

  if (error) {
    if (error.code === 'PGRST116') {
      return null // Record not found
    }
    console.error('Error fetching class:', error)
    throw new Error(`Failed to fetch class: ${error.message}`)
  }

  return data
}

/**
 * Create a new class
 */
export async function createClass(
  classData: Omit<Class, 'id' | 'created_at' | 'updated_at' | 'deleted_at'>
): Promise<Class> {
  const { data, error } = await supabase
    .from('classes')
    .insert(classData)
    .select()
    .single()

  if (error) {
    console.error('Error creating class:', error)
    throw new Error(`Failed to create class: ${error.message}`)
  }

  return data
}

/**
 * Update an existing class
 */
export async function updateClass(
  classId: string,
  academyId: string,
  updates: Partial<Omit<Class, 'id' | 'academy_id' | 'created_at' | 'updated_at'>>
): Promise<Class> {
  const { data, error } = await supabase
    .from('classes')
    .update({
      ...updates,
      updated_at: new Date().toISOString(),
    })
    .eq('id', classId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .select()
    .single()

  if (error) {
    console.error('Error updating class:', error)
    throw new Error(`Failed to update class: ${error.message}`)
  }

  return data
}

/**
 * Soft delete a class
 */
export async function deleteClass(
  classId: string,
  academyId: string
): Promise<void> {
  const { error } = await supabase
    .from('classes')
    .update({
      deleted_at: new Date().toISOString(),
      is_active: false,
      updated_at: new Date().toISOString(),
    })
    .eq('id', classId)
    .eq('academy_id', academyId)
    .is('deleted_at', null)

  if (error) {
    console.error('Error deleting class:', error)
    throw new Error(`Failed to delete class: ${error.message}`)
  }
}

/**
 * Get classes by target grade
 */
export async function getClassesByGrade(
  academyId: string,
  grade: number
): Promise<Class[]> {
  const { data, error } = await supabase
    .from('classes')
    .select('*')
    .eq('academy_id', academyId)
    .eq('target_grade', grade)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('name', { ascending: true })

  if (error) {
    console.error('Error fetching classes by grade:', error)
    throw new Error(`Failed to fetch classes by grade: ${error.message}`)
  }

  return data || []
}

/**
 * List all classes with their primary teachers for a specific academy
 */
export async function listClassesWithTeachers(academyId: string): Promise<ClassWithTeacher[]> {
  const { data, error } = await supabase
    .from('classes')
    .select(`
      *,
      class_teachers!inner(
        primary_teacher:users!inner(*)
      )
    `)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .eq('class_teachers.is_primary', true)
    .eq('class_teachers.is_active', true)
    .is('class_teachers.deleted_at', null)
    .order('name', { ascending: true })

  if (error) {
    console.error('Error fetching classes with teachers:', error)
    throw new Error(`Failed to fetch classes with teachers: ${error.message}`)
  }

  // Transform the data to match our interface
  const classesWithTeachers = (data || []).map(classData => {
    const { class_teachers, ...classInfo } = classData
    const primaryTeacher = class_teachers?.[0]?.primary_teacher || null
    
    return {
      ...classInfo,
      primary_teacher: primaryTeacher
    } as ClassWithTeacher
  })

  return classesWithTeachers
}