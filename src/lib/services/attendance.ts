import { supabase } from '@/lib/supabase'

export type AttendanceStatus = 'present' | 'absent' | 'late' | 'excused'

export interface Attendance {
  id: string
  academy_id: string
  class_id: string
  student_id: string
  class_date: string
  status: AttendanceStatus
  note?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string | null
  
  // Joined data
  student?: {
    full_name: string
    english_name?: string | null
  }
  class?: {
    name: string
  }
}

export interface AttendanceCreateInput {
  academy_id: string
  class_id: string
  student_id: string
  class_date: string
  status: AttendanceStatus
  note?: string | null
}

export interface AttendanceUpdateInput {
  status?: AttendanceStatus
  note?: string | null
}

/**
 * Get attendance for a specific class on a specific date
 */
export async function getAttendanceByClassAndDate(
  classId: string, 
  date: string, 
  academyId: string
): Promise<Attendance[]> {
  const { data, error } = await supabase
    .from('attendance')
    .select(`
      *,
      student:students!inner (full_name, english_name),
      class:classes!inner (name)
    `)
    .eq('academy_id', academyId)
    .eq('class_id', classId)
    .eq('class_date', date)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('student.full_name', { ascending: true })

  if (error) {
    console.error('Error fetching attendance:', error)
    throw error
  }

  return data || []
}

/**
 * Get all enrolled students for a class to take attendance
 */
export async function getEnrolledStudentsForAttendance(
  classId: string,
  date: string,
  academyId: string
): Promise<Array<{
  student_id: string
  student_name: string
  english_name?: string | null
  attendance?: Attendance | null
}>> {
  // First, get all enrolled students for this class
  const { data: enrollments, error: enrollmentError } = await supabase
    .from('enrollments')
    .select(`
      student_id,
      student:students!inner (id, full_name, english_name)
    `)
    .eq('academy_id', academyId)
    .eq('class_id', classId)
    .eq('status', 'active')
    .is('deleted_at', null)
    .eq('is_active', true)

  if (enrollmentError) {
    console.error('Error fetching enrollments:', enrollmentError)
    throw enrollmentError
  }

  // Then, get existing attendance records for this date
  const { data: attendanceRecords, error: attendanceError } = await supabase
    .from('attendance')
    .select('*')
    .eq('academy_id', academyId)
    .eq('class_id', classId)
    .eq('class_date', date)
    .is('deleted_at', null)
    .eq('is_active', true)

  if (attendanceError) {
    console.error('Error fetching attendance records:', attendanceError)
    throw attendanceError
  }

  // Map attendance records by student_id for quick lookup
  const attendanceMap = new Map<string, Attendance>()
  attendanceRecords?.forEach((record: any) => {
    attendanceMap.set(record.student_id, record)
  })

  // Combine enrollment and attendance data
  return enrollments?.map((enrollment: any) => ({
    student_id: enrollment.student_id,
    student_name: enrollment.student.full_name,
    english_name: enrollment.student.english_name,
    attendance: attendanceMap.get(enrollment.student_id) || null
  })) || []
}

/**
 * Mark attendance for a student
 */
export async function markAttendance(input: AttendanceCreateInput): Promise<Attendance> {
  // Check if attendance already exists
  const { data: existing, error: checkError } = await supabase
    .from('attendance')
    .select('*')
    .eq('academy_id', input.academy_id)
    .eq('class_id', input.class_id)
    .eq('student_id', input.student_id)
    .eq('class_date', input.class_date)
    .is('deleted_at', null)
    .eq('is_active', true)
    .single()

  if (checkError && checkError.code !== 'PGRST116') { // PGRST116 = no rows returned
    console.error('Error checking existing attendance:', checkError)
    throw checkError
  }

  // If exists, update it
  if (existing) {
    return updateAttendance(existing.id, input.academy_id, {
      status: input.status,
      note: input.note
    })
  }

  // Otherwise, create new record
  const { data, error } = await supabase
    .from('attendance')
    .insert(input)
    .select()
    .single()

  if (error) {
    console.error('Error marking attendance:', error)
    throw error
  }

  return data
}

/**
 * Update attendance record
 */
export async function updateAttendance(
  id: string,
  academyId: string,
  updates: AttendanceUpdateInput
): Promise<Attendance> {
  const { data, error } = await supabase
    .from('attendance')
    .update({
      ...updates,
      updated_at: new Date().toISOString()
    })
    .eq('id', id)
    .eq('academy_id', academyId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .select()
    .single()

  if (error) {
    console.error('Error updating attendance:', error)
    throw error
  }

  return data
}

/**
 * Get attendance summary for a student
 */
export async function getStudentAttendanceSummary(
  studentId: string,
  academyId: string,
  startDate?: string,
  endDate?: string
): Promise<{
  total: number
  present: number
  absent: number
  late: number
  excused: number
}> {
  let query = supabase
    .from('attendance')
    .select('status', { count: 'exact' })
    .eq('academy_id', academyId)
    .eq('student_id', studentId)
    .is('deleted_at', null)
    .eq('is_active', true)

  if (startDate) {
    query = query.gte('class_date', startDate)
  }
  if (endDate) {
    query = query.lte('class_date', endDate)
  }

  const { data, error, count } = await query

  if (error) {
    console.error('Error fetching attendance summary:', error)
    throw error
  }

  const summary = {
    total: count || 0,
    present: 0,
    absent: 0,
    late: 0,
    excused: 0
  }

  data?.forEach((record: any) => {
    summary[record.status as AttendanceStatus]++
  })

  return summary
}

/**
 * Get attendance history for a class
 */
export async function getClassAttendanceHistory(
  classId: string,
  academyId: string,
  limit: number = 30
): Promise<Array<{
  date: string
  total_students: number
  present: number
  absent: number
  late: number
  excused: number
}>> {
  const { data, error } = await supabase
    .from('attendance')
    .select('class_date, status')
    .eq('academy_id', academyId)
    .eq('class_id', classId)
    .is('deleted_at', null)
    .eq('is_active', true)
    .order('class_date', { ascending: false })

  if (error) {
    console.error('Error fetching class attendance history:', error)
    throw error
  }

  // Group by date and count statuses
  const historyMap = new Map<string, any>()
  
  data?.forEach((record: any) => {
    const date = record.class_date
    if (!historyMap.has(date)) {
      historyMap.set(date, {
        date,
        total_students: 0,
        present: 0,
        absent: 0,
        late: 0,
        excused: 0
      })
    }
    
    const dayRecord = historyMap.get(date)
    dayRecord.total_students++
    dayRecord[record.status]++
  })

  // Convert to array and limit results
  return Array.from(historyMap.values()).slice(0, limit)
}

/**
 * Delete attendance record (soft delete)
 */
export async function deleteAttendance(id: string, academyId: string): Promise<void> {
  const { error } = await supabase
    .from('attendance')
    .update({
      deleted_at: new Date().toISOString(),
      is_active: false,
      updated_at: new Date().toISOString()
    })
    .eq('id', id)
    .eq('academy_id', academyId)

  if (error) {
    console.error('Error deleting attendance:', error)
    throw error
  }
}