-- Real-time Exam System Schema Extension
-- Adds tables for exam management and real-time session functionality

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-----------------------------
-- 1. exams (Exam definitions)
-----------------------------
CREATE TABLE IF NOT EXISTS exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    academy_id UUID NOT NULL REFERENCES academies(id),
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_minutes INTEGER NOT NULL DEFAULT 60,
    total_questions INTEGER NOT NULL DEFAULT 0,
    passing_score INTEGER, -- Percentage (0-100)
    instructions TEXT,
    
    -- Exam content (could be stored as JSON or linked to separate questions table)
    questions JSONB, -- Array of question objects
    answer_key JSONB, -- Answer keys for automatic grading
    
    -- Status and metadata
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by UUID NOT NULL REFERENCES users(id),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_exams_academy ON exams (academy_id);
CREATE INDEX IF NOT EXISTS idx_exams_active ON exams (academy_id, is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_exams_created_by ON exams (created_by);

-----------------------------
-- 2. exam_sessions (Live exam instances)
-----------------------------
CREATE TABLE IF NOT EXISTS exam_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    academy_id UUID NOT NULL REFERENCES academies(id),
    exam_id UUID NOT NULL REFERENCES exams(id),
    teacher_id UUID NOT NULL REFERENCES users(id),
    
    -- Session timing and status
    status TEXT NOT NULL DEFAULT 'preparing' 
        CHECK (status IN ('preparing', 'active', 'paused', 'completed', 'terminated')),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    duration_minutes INTEGER NOT NULL,
    
    -- Enrolled students and configuration
    enrolled_students JSONB NOT NULL DEFAULT '[]'::JSONB, -- Array of student UUIDs
    session_config JSONB, -- Additional configuration (time warnings, etc.)
    
    -- Real-time metadata
    active_connections JSONB DEFAULT '{}'::JSONB, -- Currently connected students
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exam_sessions_academy ON exam_sessions (academy_id);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_teacher ON exam_sessions (teacher_id);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_exam ON exam_sessions (exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_status ON exam_sessions (academy_id, status);
CREATE INDEX IF NOT EXISTS idx_exam_sessions_active ON exam_sessions (academy_id, teacher_id, status) 
    WHERE status IN ('preparing', 'active', 'paused');

-----------------------------
-- 3. student_sessions (Individual student participation)
-----------------------------
CREATE TABLE IF NOT EXISTS student_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    academy_id UUID NOT NULL REFERENCES academies(id),
    session_id UUID NOT NULL REFERENCES exam_sessions(id),
    student_id UUID NOT NULL REFERENCES students(id),
    
    -- Session participation
    joined_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Progress tracking
    progress INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    current_question INTEGER,
    time_spent INTEGER NOT NULL DEFAULT 0, -- in seconds
    
    -- Answer storage
    answers JSONB NOT NULL DEFAULT '{}'::JSONB, -- question_id: {answer, submitted_at, is_auto_save}
    auto_saves JSONB NOT NULL DEFAULT '{}'::JSONB, -- question_id: {answer, saved_at}
    
    -- Real-time connection state
    connection_status TEXT DEFAULT 'disconnected' 
        CHECK (connection_status IN ('connected', 'disconnected', 'reconnecting')),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Unique constraint: one session per student per exam session
CREATE UNIQUE INDEX IF NOT EXISTS idx_student_sessions_unique 
    ON student_sessions (session_id, student_id, academy_id);

CREATE INDEX IF NOT EXISTS idx_student_sessions_academy ON student_sessions (academy_id);
CREATE INDEX IF NOT EXISTS idx_student_sessions_student ON student_sessions (student_id);
CREATE INDEX IF NOT EXISTS idx_student_sessions_session ON student_sessions (session_id);
CREATE INDEX IF NOT EXISTS idx_student_sessions_active ON student_sessions (session_id, is_active);
CREATE INDEX IF NOT EXISTS idx_student_sessions_progress ON student_sessions (session_id, progress);

-----------------------------
-- 4. session_events (Real-time event log)
-----------------------------
CREATE TABLE IF NOT EXISTS session_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    academy_id UUID NOT NULL REFERENCES academies(id),
    session_id UUID NOT NULL REFERENCES exam_sessions(id),
    
    -- Event details
    event_type VARCHAR(50) NOT NULL, -- 'student_joined', 'answer_submitted', 'exam_launched', etc.
    user_id UUID, -- Student or teacher who triggered the event
    user_type VARCHAR(20), -- 'student' or 'teacher'
    
    -- Event data
    event_data JSONB, -- Flexible event data storage
    metadata JSONB, -- Additional metadata (IP, user agent, etc.)
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_session_events_session ON session_events (session_id);
CREATE INDEX IF NOT EXISTS idx_session_events_academy ON session_events (academy_id);
CREATE INDEX IF NOT EXISTS idx_session_events_type ON session_events (session_id, event_type);
CREATE INDEX IF NOT EXISTS idx_session_events_user ON session_events (user_id);
CREATE INDEX IF NOT EXISTS idx_session_events_created ON session_events (session_id, created_at);

-----------------------------
-- 5. websocket_connections (Connection tracking)
-----------------------------
CREATE TABLE IF NOT EXISTS websocket_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    academy_id UUID NOT NULL REFERENCES academies(id),
    
    -- Connection details
    user_id UUID NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('teacher', 'student')),
    session_id UUID REFERENCES exam_sessions(id), -- NULL if not in a session
    
    -- Connection metadata
    connection_id VARCHAR(255) NOT NULL UNIQUE, -- WebSocket connection identifier
    ip_address INET,
    user_agent TEXT,
    
    -- Timing
    connected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    disconnected_at TIMESTAMPTZ,
    last_ping TIMESTAMPTZ DEFAULT NOW(),
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_websocket_connections_academy ON websocket_connections (academy_id);
CREATE INDEX IF NOT EXISTS idx_websocket_connections_user ON websocket_connections (user_id);
CREATE INDEX IF NOT EXISTS idx_websocket_connections_session ON websocket_connections (session_id);
CREATE INDEX IF NOT EXISTS idx_websocket_connections_active ON websocket_connections (academy_id, is_active) 
    WHERE is_active = TRUE;

-----------------------------
-- 6. Triggers for updated_at fields
-----------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to relevant tables
DROP TRIGGER IF EXISTS update_exams_updated_at ON exams;
CREATE TRIGGER update_exams_updated_at 
    BEFORE UPDATE ON exams 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_exam_sessions_updated_at ON exam_sessions;
CREATE TRIGGER update_exam_sessions_updated_at 
    BEFORE UPDATE ON exam_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_student_sessions_updated_at ON student_sessions;
CREATE TRIGGER update_student_sessions_updated_at 
    BEFORE UPDATE ON student_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-----------------------------
-- 7. Sample data for testing
-----------------------------
-- Insert sample exam (only if no exams exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM exams LIMIT 1) THEN
        -- Get first academy and teacher for sample data
        INSERT INTO exams (academy_id, title, description, duration_minutes, total_questions, created_by, questions, answer_key)
        SELECT 
            a.id as academy_id,
            'Sample English Assessment' as title,
            'A comprehensive English language assessment covering grammar, vocabulary, and reading comprehension.' as description,
            45 as duration_minutes,
            20 as total_questions,
            u.id as created_by,
            '[
                {
                    "id": "q1",
                    "type": "multiple_choice",
                    "question": "What is the correct form of the verb? ''I ____ to school every day.''",
                    "options": ["go", "goes", "going", "gone"],
                    "correct_answer": "go"
                },
                {
                    "id": "q2", 
                    "type": "multiple_choice",
                    "question": "Choose the correct preposition: ''The book is ____ the table.''",
                    "options": ["in", "on", "at", "under"],
                    "correct_answer": "on"
                }
            ]'::JSONB as questions,
            '{
                "q1": "go",
                "q2": "on"
            }'::JSONB as answer_key
        FROM academies a 
        CROSS JOIN users u 
        WHERE u.role = 'teacher' AND u.academy_id = a.id
        LIMIT 1;
    END IF;
END $$;

-----------------------------
-- 8. Views for common queries
-----------------------------

-- Active exam sessions with details
CREATE OR REPLACE VIEW active_exam_sessions AS
SELECT 
    es.*,
    e.title as exam_title,
    e.total_questions,
    u.full_name as teacher_name,
    (
        SELECT COUNT(*)::INTEGER 
        FROM student_sessions ss 
        WHERE ss.session_id = es.id AND ss.is_active = TRUE
    ) as connected_students,
    (
        SELECT AVG(ss.progress)::INTEGER
        FROM student_sessions ss 
        WHERE ss.session_id = es.id AND ss.is_active = TRUE
    ) as average_progress
FROM exam_sessions es
JOIN exams e ON es.exam_id = e.id
JOIN users u ON es.teacher_id = u.id
WHERE es.status IN ('preparing', 'active', 'paused');

-- Student session details with student info
CREATE OR REPLACE VIEW student_session_details AS
SELECT 
    ss.*,
    s.full_name as student_name,
    s.english_name as student_english_name,
    s.student_code,
    es.status as session_status,
    e.title as exam_title,
    e.duration_minutes as exam_duration
FROM student_sessions ss
JOIN students s ON ss.student_id = s.id
JOIN exam_sessions es ON ss.session_id = es.id
JOIN exams e ON es.exam_id = e.id;

-----------------------------
-- 9. Functions for common operations
-----------------------------

-- Function to get session statistics
CREATE OR REPLACE FUNCTION get_session_stats(session_uuid UUID)
RETURNS TABLE (
    total_students INTEGER,
    connected_students INTEGER,
    completed_students INTEGER,
    average_progress DECIMAL,
    time_elapsed_minutes INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(jsonb_array_length(es.enrolled_students), 0)::INTEGER as total_students,
        COUNT(CASE WHEN ss.is_active = TRUE THEN 1 END)::INTEGER as connected_students,
        COUNT(CASE WHEN ss.completed_at IS NOT NULL THEN 1 END)::INTEGER as completed_students,
        COALESCE(AVG(ss.progress), 0)::DECIMAL as average_progress,
        CASE 
            WHEN es.start_time IS NOT NULL 
            THEN EXTRACT(EPOCH FROM (NOW() - es.start_time))::INTEGER / 60
            ELSE 0
        END as time_elapsed_minutes
    FROM exam_sessions es
    LEFT JOIN student_sessions ss ON es.id = ss.session_id
    WHERE es.id = session_uuid
    GROUP BY es.id, es.start_time, es.enrolled_students;
END;
$$ LANGUAGE plpgsql;

-- Function to cleanup old WebSocket connections
CREATE OR REPLACE FUNCTION cleanup_old_websocket_connections()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Mark connections as inactive if last ping was more than 5 minutes ago
    UPDATE websocket_connections 
    SET is_active = FALSE, disconnected_at = NOW()
    WHERE is_active = TRUE 
    AND (last_ping IS NULL OR last_ping < NOW() - INTERVAL '5 minutes');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Delete very old inactive connections (older than 24 hours)
    DELETE FROM websocket_connections
    WHERE is_active = FALSE 
    AND disconnected_at < NOW() - INTERVAL '24 hours';
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled cleanup (requires pg_cron extension in production)
-- This is commented out as pg_cron may not be available in all environments
-- SELECT cron.schedule('cleanup-websocket-connections', '*/15 * * * *', 'SELECT cleanup_old_websocket_connections();');