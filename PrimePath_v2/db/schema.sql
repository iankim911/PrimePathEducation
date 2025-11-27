-- PrimePath LMS – Canonical Schema v1

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-----------------------------
-- 1. academies (Root tenant)
-----------------------------
CREATE TABLE IF NOT EXISTS academies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_academies_slug ON academies (slug);

-----------------------------
-- 2. users (admins & teachers)
-----------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id),

    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'teacher')),
    password_hash TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_academy_email
ON users (academy_id, email);

-----------------------------
-- 3. students
-----------------------------
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id),

    full_name VARCHAR(255) NOT NULL,
    english_name VARCHAR(255),
    student_code VARCHAR(100),
    school_name VARCHAR(255),
    grade SMALLINT,

    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'paused', 'withdrawn')),

    parent_name VARCHAR(255),
    parent_phone VARCHAR(50),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_students_academy
ON students (academy_id);

CREATE INDEX IF NOT EXISTS idx_students_academy_status
ON students (academy_id, status);

-----------------------------
-- 4. classes
-----------------------------
CREATE TABLE IF NOT EXISTS classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id),

    name VARCHAR(255) NOT NULL,
    level_label VARCHAR(100),
    target_grade SMALLINT,
    schedule_info TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_classes_academy
ON classes (academy_id);

-----------------------------
-- 5. enrollments (student ↔ class)
-----------------------------
CREATE TABLE IF NOT EXISTS enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id),

    student_id UUID NOT NULL REFERENCES students(id),
    class_id UUID NOT NULL REFERENCES classes(id),

    start_date DATE NOT NULL,
    end_date DATE,

    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'completed', 'cancelled')),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_enrollments_unique
ON enrollments (academy_id, student_id, class_id, start_date)
WHERE deleted_at IS NULL;

-----------------------------
-- 6. attendance
-----------------------------
CREATE TABLE IF NOT EXISTS attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id),

    class_id UUID NOT NULL REFERENCES classes(id),
    student_id UUID NOT NULL REFERENCES students(id),

    class_date DATE NOT NULL,

    status TEXT NOT NULL
        CHECK (status IN ('present', 'absent', 'late', 'excused')),

    note TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_attendance_academy_date
ON attendance (academy_id, class_date);

CREATE INDEX IF NOT EXISTS idx_attendance_academy_class_date
ON attendance (academy_id, class_id, class_date);

CREATE UNIQUE INDEX IF NOT EXISTS idx_attendance_unique
ON attendance (academy_id, class_id, student_id, class_date)
WHERE deleted_at IS NULL;

-----------------------------
-- 7. class_teachers (class ↔ teacher assignments)
-----------------------------
CREATE TABLE IF NOT EXISTS class_teachers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id),

    class_id UUID NOT NULL REFERENCES classes(id),
    teacher_id UUID NOT NULL REFERENCES users(id),

    role TEXT NOT NULL DEFAULT 'teacher'
        CHECK (role IN ('main', 'sub', 'native')),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_class_teachers_class
ON class_teachers (class_id);

CREATE INDEX IF NOT EXISTS idx_class_teachers_teacher
ON class_teachers (teacher_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_class_teachers_unique
ON class_teachers (academy_id, class_id, teacher_id)
WHERE deleted_at IS NULL;

-- Ensure only one primary teacher per class
CREATE UNIQUE INDEX IF NOT EXISTS idx_class_teachers_primary
ON class_teachers (academy_id, class_id)
WHERE deleted_at IS NULL AND is_primary = TRUE;