-- Test Management Module Schema for PrimePath LMS
-- PostgreSQL/Supabase Compatible Version
-- Created: 2024-11-28

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-----------------------------
-- 1. exam_types (Configurable exam categories per academy)
-----------------------------
CREATE TABLE IF NOT EXISTS exam_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    description TEXT,
    color_hex VARCHAR(7) DEFAULT '#6B7280',
    
    -- Defaults for this exam type
    default_time_limit INTEGER,
    default_attempts_allowed INTEGER DEFAULT 1,
    default_passing_score DECIMAL(5,2),
    
    sort_order INTEGER NOT NULL DEFAULT 0,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_exam_types_academy ON exam_types (academy_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_exam_types_academy_code ON exam_types (academy_id, code) WHERE deleted_at IS NULL;

-----------------------------
-- 2. exams (Core exam metadata and configuration)
-----------------------------
CREATE TABLE IF NOT EXISTS exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    
    -- Basic metadata
    title VARCHAR(255) NOT NULL,
    description TEXT,
    exam_type_id UUID REFERENCES exam_types(id),
    
    -- Configuration
    time_limit_minutes INTEGER,
    attempts_allowed INTEGER NOT NULL DEFAULT 1,
    passing_score DECIMAL(5,2),
    
    -- Question configuration
    total_questions INTEGER NOT NULL DEFAULT 0,
    total_points DECIMAL(8,2) NOT NULL DEFAULT 0,
    randomize_questions BOOLEAN NOT NULL DEFAULT FALSE,
    randomize_answers BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    
    -- Settings
    show_results BOOLEAN NOT NULL DEFAULT TRUE,
    allow_review BOOLEAN NOT NULL DEFAULT TRUE,
    require_webcam BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- AI-ready metadata
    difficulty_level TEXT CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    subject_tags TEXT[],
    learning_objectives TEXT[],
    metadata JSONB,
    
    -- Uploaded by
    created_by UUID REFERENCES users(id),
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_exams_academy ON exams (academy_id);
CREATE INDEX IF NOT EXISTS idx_exams_exam_type ON exams (exam_type_id);
CREATE INDEX IF NOT EXISTS idx_exams_status ON exams (academy_id, status) WHERE deleted_at IS NULL;
-- GIN index for array fields
CREATE INDEX IF NOT EXISTS idx_exams_subject_tags ON exams USING GIN (subject_tags);

-----------------------------
-- 3. exam_sections (Organize exams into logical sections)
-----------------------------
CREATE TABLE IF NOT EXISTS exam_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    
    sort_order INTEGER NOT NULL DEFAULT 0,
    time_limit_minutes INTEGER,
    
    -- AI-ready categorization
    section_type VARCHAR(50),
    skill_focus VARCHAR(50),
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_exam_sections_exam ON exam_sections (exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_sections_sort ON exam_sections (exam_id, sort_order);

-----------------------------
-- 4. exam_files (PDFs, images, audio files)
-----------------------------
CREATE TABLE IF NOT EXISTS exam_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    exam_id UUID REFERENCES exams(id) ON DELETE CASCADE,
    section_id UUID REFERENCES exam_sections(id) ON DELETE CASCADE,
    
    -- File metadata
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50) NOT NULL CHECK (file_type IN ('pdf', 'image', 'audio')),
    mime_type VARCHAR(100) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    
    -- Display configuration
    title VARCHAR(255),
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    
    -- PDF specific settings
    rotation_degrees INTEGER DEFAULT 0,
    zoom_level DECIMAL(3,2) DEFAULT 1.0,
    is_split_enabled BOOLEAN DEFAULT FALSE,
    split_orientation VARCHAR(20) DEFAULT 'vertical' CHECK (split_orientation IN ('vertical', 'horizontal')),
    split_page_1_position VARCHAR(20) DEFAULT 'left' CHECK (split_page_1_position IN ('left', 'right', 'top', 'bottom')),
    split_page_2_position VARCHAR(20) DEFAULT 'right' CHECK (split_page_2_position IN ('left', 'right', 'top', 'bottom')),
    
    -- AI-ready metadata
    ocr_text TEXT,
    audio_duration_seconds INTEGER,
    audio_transcript TEXT,
    processing_status VARCHAR(20) DEFAULT 'pending',
    
    metadata JSONB,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_exam_files_exam ON exam_files (exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_files_section ON exam_files (section_id);
CREATE INDEX IF NOT EXISTS idx_exam_files_type ON exam_files (file_type);

-----------------------------
-- 5. exam_questions (Individual questions)
-----------------------------
CREATE TABLE IF NOT EXISTS exam_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    section_id UUID REFERENCES exam_sections(id) ON DELETE CASCADE,
    
    -- Question content
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL CHECK (
        question_type IN ('multiple_choice', 'multiple_select', 'short_answer', 'long_answer', 'true_false', 'fill_blank')
    ),
    
    -- Answer configuration
    correct_answers TEXT[],
    answer_options JSONB,
    points DECIMAL(5,2) NOT NULL DEFAULT 1.0,
    
    -- Display and behavior
    sort_order INTEGER NOT NULL DEFAULT 0,
    instructions TEXT,
    explanation TEXT,
    
    -- File associations
    file_references UUID[],
    audio_start_seconds INTEGER,
    audio_end_seconds INTEGER,
    
    -- AI-ready metadata
    difficulty_estimated DECIMAL(3,2),
    difficulty_actual DECIMAL(3,2),
    bloom_taxonomy VARCHAR(20),
    cognitive_load VARCHAR(20),
    skill_tags TEXT[],
    metadata JSONB,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_exam_questions_exam ON exam_questions (exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_questions_section ON exam_questions (section_id);
CREATE INDEX IF NOT EXISTS idx_exam_questions_sort ON exam_questions (exam_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_exam_questions_type ON exam_questions (question_type);
-- GIN indexes for array fields
CREATE INDEX IF NOT EXISTS idx_exam_questions_skill_tags ON exam_questions USING GIN (skill_tags);
CREATE INDEX IF NOT EXISTS idx_exam_questions_file_refs ON exam_questions USING GIN (file_references);

-----------------------------
-- 6. exam_sessions (Live exam instances launched by teachers)
-----------------------------
CREATE TABLE IF NOT EXISTS exam_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    exam_id UUID NOT NULL REFERENCES exams(id),
    class_id UUID REFERENCES classes(id) ON DELETE SET NULL,
    teacher_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Session metadata
    title VARCHAR(255) NOT NULL,
    instructions TEXT,
    
    -- Timing
    scheduled_start TIMESTAMPTZ,
    scheduled_end TIMESTAMPTZ,
    actual_start TIMESTAMPTZ,
    actual_end TIMESTAMPTZ,
    
    -- Configuration overrides
    time_limit_override INTEGER,
    attempts_allowed_override INTEGER,
    
    -- Settings
    allow_late_entry BOOLEAN NOT NULL DEFAULT TRUE,
    shuffle_questions BOOLEAN NOT NULL DEFAULT FALSE,
    require_all_students BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK (
        status IN ('scheduled', 'active', 'paused', 'completed', 'cancelled')
    ),
    
    -- Analytics
    total_invited INTEGER NOT NULL DEFAULT 0,
    total_started INTEGER NOT NULL DEFAULT 0,
    total_completed INTEGER NOT NULL DEFAULT 0,
    average_score DECIMAL(5,2),
    
    -- AI-ready metadata
    session_type VARCHAR(20),
    metadata JSONB,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_exam_sessions_academy ON exam_sessions (academy_id);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_exam ON exam_sessions (exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_class ON exam_sessions (class_id);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_teacher ON exam_sessions (teacher_id);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_status ON exam_sessions (status);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_scheduled ON exam_sessions (scheduled_start, scheduled_end);

-----------------------------
-- 7. exam_session_participants (Track who's invited/participating)
-----------------------------
CREATE TABLE IF NOT EXISTS exam_session_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES exam_sessions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id),
    
    -- Participation tracking
    invited_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    first_accessed TIMESTAMPTZ,
    last_accessed TIMESTAMPTZ,
    
    -- Status
    participation_status TEXT NOT NULL DEFAULT 'invited' CHECK (
        participation_status IN ('invited', 'started', 'in_progress', 'submitted', 'auto_submitted', 'absent')
    ),
    
    -- Special accommodations
    extra_time_minutes INTEGER DEFAULT 0,
    special_instructions TEXT,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_session_participants_session ON exam_session_participants (session_id);
CREATE INDEX IF NOT EXISTS idx_session_participants_student ON exam_session_participants (student_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_session_participants_unique 
ON exam_session_participants (academy_id, session_id, student_id) WHERE deleted_at IS NULL;

-----------------------------
-- 8. student_exam_attempts (Individual student attempts)
-----------------------------
CREATE TABLE IF NOT EXISTS student_exam_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id),
    exam_id UUID NOT NULL REFERENCES exams(id),
    session_id UUID REFERENCES exam_sessions(id) ON DELETE SET NULL,
    participant_id UUID REFERENCES exam_session_participants(id) ON DELETE SET NULL,
    
    -- Attempt tracking
    attempt_number INTEGER NOT NULL DEFAULT 1,
    
    -- Timing
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    time_spent_seconds INTEGER,
    time_limit_seconds INTEGER,
    
    -- Progress
    current_question_id UUID REFERENCES exam_questions(id),
    questions_answered INTEGER NOT NULL DEFAULT 0,
    total_questions INTEGER NOT NULL,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'in_progress' CHECK (
        status IN ('in_progress', 'submitted', 'auto_submitted', 'abandoned')
    ),
    
    -- Scoring
    raw_score DECIMAL(8,2) DEFAULT 0,
    max_possible_score DECIMAL(8,2) NOT NULL,
    percentage_score DECIMAL(5,2),
    passed BOOLEAN,
    
    -- Security
    ip_address INET,
    user_agent TEXT,
    tab_switches INTEGER NOT NULL DEFAULT 0,
    copy_paste_attempts INTEGER NOT NULL DEFAULT 0,
    
    -- AI-ready analytics
    question_sequence INTEGER[],
    time_per_question INTEGER[],
    confidence_scores DECIMAL(3,2)[],
    difficulty_adjustments JSONB,
    behavior_metadata JSONB,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_student_attempts_student ON student_exam_attempts (student_id);
CREATE INDEX IF NOT EXISTS idx_student_attempts_exam ON student_exam_attempts (exam_id);
CREATE INDEX IF NOT EXISTS idx_student_attempts_session ON student_exam_attempts (session_id);
CREATE INDEX IF NOT EXISTS idx_student_attempts_status ON student_exam_attempts (status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_student_attempts_unique 
ON student_exam_attempts (academy_id, student_id, exam_id, attempt_number) WHERE deleted_at IS NULL;

-----------------------------
-- 9. student_answers (Individual question responses)
-----------------------------
CREATE TABLE IF NOT EXISTS student_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    attempt_id UUID NOT NULL REFERENCES student_exam_attempts(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES exam_questions(id),
    
    -- Response
    answer_text TEXT,
    selected_options INTEGER[],
    is_flagged BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Timing
    answered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    time_spent_seconds INTEGER,
    
    -- Grading
    is_correct BOOLEAN,
    points_earned DECIMAL(5,2) DEFAULT 0,
    points_possible DECIMAL(5,2) NOT NULL,
    
    -- Manual grading
    manual_override BOOLEAN NOT NULL DEFAULT FALSE,
    teacher_feedback TEXT,
    graded_by UUID REFERENCES users(id),
    graded_at TIMESTAMPTZ,
    
    -- AI-ready analytics
    confidence_level DECIMAL(3,2),
    difficulty_perceived VARCHAR(20),
    answer_pattern VARCHAR(20),
    keystroke_data JSONB,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_student_answers_attempt ON student_answers (attempt_id);
CREATE INDEX IF NOT EXISTS idx_student_answers_question ON student_answers (question_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_student_answers_unique 
ON student_answers (academy_id, attempt_id, question_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_student_answers_grading ON student_answers (is_correct, points_earned);

-----------------------------
-- 10. curriculum_exam_mappings (Link exams to curriculum levels)
-----------------------------
CREATE TABLE IF NOT EXISTS curriculum_exam_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    curriculum_node_id UUID NOT NULL REFERENCES curriculum_nodes(id),
    exam_id UUID NOT NULL REFERENCES exams(id),
    
    -- Mapping configuration
    mapping_type TEXT NOT NULL DEFAULT 'placement' CHECK (
        mapping_type IN ('placement', 'progress', 'final', 'diagnostic')
    ),
    
    slot_position INTEGER NOT NULL DEFAULT 1,
    weight DECIMAL(3,2) DEFAULT 1.0,
    
    -- Prerequisites
    min_score_required DECIMAL(5,2),
    prerequisites JSONB,
    
    -- AI-ready metadata
    difficulty_mapping DECIMAL(3,2),
    skill_alignment JSONB,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_curriculum_exam_mappings_curriculum ON curriculum_exam_mappings (curriculum_node_id);
CREATE INDEX IF NOT EXISTS idx_curriculum_exam_mappings_exam ON curriculum_exam_mappings (exam_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_curriculum_exam_mappings_unique 
ON curriculum_exam_mappings (academy_id, curriculum_node_id, exam_id, mapping_type) WHERE deleted_at IS NULL;

-----------------------------
-- 11. class_exam_assignments (Assign exams to specific classes)
-----------------------------
CREATE TABLE IF NOT EXISTS class_exam_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    class_id UUID NOT NULL REFERENCES classes(id),
    exam_id UUID NOT NULL REFERENCES exams(id),
    teacher_id UUID NOT NULL REFERENCES users(id),
    
    -- Assignment details
    assignment_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Scheduling
    assigned_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE,
    available_from TIMESTAMPTZ,
    available_until TIMESTAMPTZ,
    
    -- Configuration overrides
    attempts_allowed INTEGER,
    time_limit_minutes INTEGER,
    shuffle_questions BOOLEAN,
    show_results_immediately BOOLEAN DEFAULT TRUE,
    
    -- Grading
    weight DECIMAL(5,2) DEFAULT 1.0,
    category VARCHAR(50),
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_class_exam_assignments_class ON class_exam_assignments (class_id);
CREATE INDEX IF NOT EXISTS idx_class_exam_assignments_exam ON class_exam_assignments (exam_id);
CREATE INDEX IF NOT EXISTS idx_class_exam_assignments_teacher ON class_exam_assignments (teacher_id);
CREATE INDEX IF NOT EXISTS idx_class_exam_assignments_dates ON class_exam_assignments (assigned_date, due_date);

-----------------------------
-- Functions and Triggers for maintaining data consistency
-----------------------------

-- Update exam total_questions and total_points when questions are added/removed
CREATE OR REPLACE FUNCTION update_exam_question_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE exams 
    SET 
        total_questions = (
            SELECT COUNT(*) 
            FROM exam_questions 
            WHERE exam_id = COALESCE(NEW.exam_id, OLD.exam_id)
            AND deleted_at IS NULL
        ),
        total_points = (
            SELECT COALESCE(SUM(points), 0)
            FROM exam_questions
            WHERE exam_id = COALESCE(NEW.exam_id, OLD.exam_id)
            AND deleted_at IS NULL
        ),
        updated_at = NOW()
    WHERE id = COALESCE(NEW.exam_id, OLD.exam_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_exam_question_count
    AFTER INSERT OR UPDATE OR DELETE ON exam_questions
    FOR EACH ROW EXECUTE FUNCTION update_exam_question_count();

-- Update attempt scores when answers are graded
CREATE OR REPLACE FUNCTION update_attempt_scores()
RETURNS TRIGGER AS $$
DECLARE
    attempt_record RECORD;
    exam_record RECORD;
BEGIN
    -- Get attempt and exam info
    SELECT * INTO attempt_record 
    FROM student_exam_attempts 
    WHERE id = NEW.attempt_id;
    
    SELECT * INTO exam_record
    FROM exams
    WHERE id = attempt_record.exam_id;
    
    -- Update the attempt with new scores
    UPDATE student_exam_attempts
    SET 
        raw_score = (
            SELECT COALESCE(SUM(points_earned), 0)
            FROM student_answers 
            WHERE attempt_id = NEW.attempt_id 
            AND deleted_at IS NULL
        ),
        questions_answered = (
            SELECT COUNT(*)
            FROM student_answers 
            WHERE attempt_id = NEW.attempt_id 
            AND deleted_at IS NULL
        ),
        updated_at = NOW()
    WHERE id = NEW.attempt_id;
    
    -- Update percentage score and pass/fail status
    UPDATE student_exam_attempts
    SET 
        percentage_score = CASE 
            WHEN max_possible_score > 0 THEN (raw_score / max_possible_score * 100)
            ELSE 0 
        END,
        passed = CASE 
            WHEN max_possible_score > 0 THEN 
                (raw_score / max_possible_score * 100) >= COALESCE(exam_record.passing_score, 60)
            ELSE FALSE 
        END,
        updated_at = NOW()
    WHERE id = NEW.attempt_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_attempt_scores
    AFTER INSERT OR UPDATE ON student_answers
    FOR EACH ROW EXECUTE FUNCTION update_attempt_scores();

-- Update session statistics
CREATE OR REPLACE FUNCTION update_session_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE exam_sessions
    SET 
        total_started = (
            SELECT COUNT(*)
            FROM student_exam_attempts
            WHERE session_id = COALESCE(NEW.session_id, OLD.session_id)
            AND deleted_at IS NULL
        ),
        total_completed = (
            SELECT COUNT(*)
            FROM student_exam_attempts
            WHERE session_id = COALESCE(NEW.session_id, OLD.session_id)
            AND status IN ('submitted', 'auto_submitted')
            AND deleted_at IS NULL
        ),
        average_score = (
            SELECT AVG(percentage_score)
            FROM student_exam_attempts
            WHERE session_id = COALESCE(NEW.session_id, OLD.session_id)
            AND status IN ('submitted', 'auto_submitted')
            AND percentage_score IS NOT NULL
            AND deleted_at IS NULL
        ),
        updated_at = NOW()
    WHERE id = COALESCE(NEW.session_id, OLD.session_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_session_stats
    AFTER INSERT OR UPDATE OR DELETE ON student_exam_attempts
    FOR EACH ROW EXECUTE FUNCTION update_session_stats();

-----------------------------
-- Row Level Security (RLS) Policies for Supabase
-----------------------------

-- Enable RLS on all tables
ALTER TABLE exam_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE exams ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_session_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_exam_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE curriculum_exam_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE class_exam_assignments ENABLE ROW LEVEL SECURITY;

-- For now, we'll create permissive policies that allow all operations
-- In production, these should be tightened based on user roles

-- Exam types policies
CREATE POLICY "Allow all operations on exam_types" ON exam_types
    FOR ALL USING (true);

-- Exams policies  
CREATE POLICY "Allow all operations on exams" ON exams
    FOR ALL USING (true);

-- Exam sections policies
CREATE POLICY "Allow all operations on exam_sections" ON exam_sections
    FOR ALL USING (true);

-- Exam files policies
CREATE POLICY "Allow all operations on exam_files" ON exam_files
    FOR ALL USING (true);

-- Exam questions policies
CREATE POLICY "Allow all operations on exam_questions" ON exam_questions
    FOR ALL USING (true);

-- Exam sessions policies
CREATE POLICY "Allow all operations on exam_sessions" ON exam_sessions
    FOR ALL USING (true);

-- Exam session participants policies
CREATE POLICY "Allow all operations on exam_session_participants" ON exam_session_participants
    FOR ALL USING (true);

-- Student exam attempts policies
CREATE POLICY "Allow all operations on student_exam_attempts" ON student_exam_attempts
    FOR ALL USING (true);

-- Student answers policies
CREATE POLICY "Allow all operations on student_answers" ON student_answers
    FOR ALL USING (true);

-- Curriculum exam mappings policies
CREATE POLICY "Allow all operations on curriculum_exam_mappings" ON curriculum_exam_mappings
    FOR ALL USING (true);

-- Class exam assignments policies
CREATE POLICY "Allow all operations on class_exam_assignments" ON class_exam_assignments
    FOR ALL USING (true);