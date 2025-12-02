-- Grade Configuration System
-- Adds configurable grade management to replace hardcoded grade dropdowns
-- This is backward compatible - existing functionality continues to work

-----------------------------
-- 1. Grade Configuration Table
-----------------------------
CREATE TABLE IF NOT EXISTS grade_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    
    -- Field customization
    field_label VARCHAR(50) NOT NULL DEFAULT 'Target Grade',
    show_all_option BOOLEAN NOT NULL DEFAULT TRUE,
    all_grades_label VARCHAR(50) NOT NULL DEFAULT 'All Grades',
    
    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Unique constraint: one configuration per academy
CREATE UNIQUE INDEX IF NOT EXISTS idx_grade_configurations_academy
ON grade_configurations (academy_id) WHERE deleted_at IS NULL;

-----------------------------
-- 2. Grade Options Table  
-----------------------------
CREATE TABLE IF NOT EXISTS grade_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    
    -- Grade details
    grade_value INTEGER NOT NULL,        -- Numeric value (1, 2, 7, 10, etc.)
    display_name VARCHAR(100) NOT NULL,  -- "Grade 1", "Middle 1", "Year 7", etc.
    short_name VARCHAR(20),              -- Optional short version "G1", "M1", etc.
    sort_order INTEGER NOT NULL DEFAULT 0,
    
    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_grade_options_academy
ON grade_options (academy_id);

CREATE INDEX IF NOT EXISTS idx_grade_options_sort
ON grade_options (academy_id, sort_order, grade_value);

-- Unique constraint: one option per grade value per academy
CREATE UNIQUE INDEX IF NOT EXISTS idx_grade_options_unique
ON grade_options (academy_id, grade_value) WHERE deleted_at IS NULL;

-----------------------------
-- 3. Default Data Population
-----------------------------
-- Insert default configuration for existing academies
INSERT INTO grade_configurations (academy_id, field_label, show_all_option, all_grades_label)
SELECT 
    id as academy_id,
    'Target Grade' as field_label,
    TRUE as show_all_option,
    'All Grades' as all_grades_label
FROM academies 
WHERE id NOT IN (
    SELECT academy_id FROM grade_configurations WHERE deleted_at IS NULL
)
AND deleted_at IS NULL;

-- Insert default grade options matching current hardcoded values
-- This ensures backward compatibility with existing data
DO $$
DECLARE
    academy_record RECORD;
    grade_data RECORD;
BEGIN
    -- For each academy that doesn't have grade options yet
    FOR academy_record IN 
        SELECT id FROM academies 
        WHERE deleted_at IS NULL 
        AND id NOT IN (
            SELECT DISTINCT academy_id FROM grade_options WHERE deleted_at IS NULL
        )
    LOOP
        -- Insert the standard grade options (matching current hardcoded values)
        INSERT INTO grade_options (academy_id, grade_value, display_name, short_name, sort_order) VALUES
            -- Elementary Grades (1-6)
            (academy_record.id, 1, 'Grade 1', 'G1', 1),
            (academy_record.id, 2, 'Grade 2', 'G2', 2),
            (academy_record.id, 3, 'Grade 3', 'G3', 3),
            (academy_record.id, 4, 'Grade 4', 'G4', 4),
            (academy_record.id, 5, 'Grade 5', 'G5', 5),
            (academy_record.id, 6, 'Grade 6', 'G6', 6),
            
            -- Middle School (7-9, displayed as Middle 1-3)
            (academy_record.id, 7, 'Middle 1', 'M1', 7),
            (academy_record.id, 8, 'Middle 2', 'M2', 8),
            (academy_record.id, 9, 'Middle 3', 'M3', 9),
            
            -- High School (10-12, displayed as High 1-3)
            (academy_record.id, 10, 'High 1', 'H1', 10),
            (academy_record.id, 11, 'High 2', 'H2', 11),
            (academy_record.id, 12, 'High 3', 'H3', 12);
            
        RAISE NOTICE 'Created default grade options for academy %', academy_record.id;
    END LOOP;
END $$;

-----------------------------
-- 4. Helper Views and Functions
-----------------------------

-- View to get formatted grade options for dropdowns
CREATE OR REPLACE VIEW grade_options_formatted AS
SELECT 
    go.id,
    go.academy_id,
    go.grade_value,
    go.display_name,
    go.short_name,
    go.sort_order,
    go.is_active,
    gc.field_label,
    gc.show_all_option,
    gc.all_grades_label
FROM grade_options go
JOIN grade_configurations gc ON go.academy_id = gc.academy_id
WHERE go.deleted_at IS NULL 
AND go.is_active = TRUE
AND gc.deleted_at IS NULL
AND gc.is_active = TRUE
ORDER BY go.academy_id, go.sort_order, go.grade_value;

-- Function to get grade display name by value
CREATE OR REPLACE FUNCTION get_grade_display_name(
    p_academy_id UUID,
    p_grade_value INTEGER
) RETURNS VARCHAR AS $$
DECLARE
    display_name VARCHAR(100);
BEGIN
    SELECT go.display_name INTO display_name
    FROM grade_options go
    WHERE go.academy_id = p_academy_id
    AND go.grade_value = p_grade_value
    AND go.deleted_at IS NULL
    AND go.is_active = TRUE;
    
    -- Fallback to generic format if not found
    IF display_name IS NULL THEN
        RETURN 'Grade ' || p_grade_value;
    END IF;
    
    RETURN display_name;
END;
$$ LANGUAGE plpgsql;

-- Function to validate grade value exists for academy
CREATE OR REPLACE FUNCTION validate_grade_value(
    p_academy_id UUID,
    p_grade_value INTEGER
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM grade_options
        WHERE academy_id = p_academy_id
        AND grade_value = p_grade_value
        AND deleted_at IS NULL
        AND is_active = TRUE
    );
END;
$$ LANGUAGE plpgsql;

-----------------------------
-- 5. Grant Permissions
-----------------------------
-- Grant permissions for authenticated users
GRANT ALL ON grade_configurations TO authenticated;
GRANT ALL ON grade_options TO authenticated;

-- Grant read access for anon users (if needed)
GRANT SELECT ON grade_configurations TO anon;
GRANT SELECT ON grade_options TO anon;
GRANT SELECT ON grade_options_formatted TO anon;

-- Grant execute on functions
GRANT EXECUTE ON FUNCTION get_grade_display_name(UUID, INTEGER) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION validate_grade_value(UUID, INTEGER) TO authenticated, anon;

-----------------------------
-- 6. Verification Queries
-----------------------------
-- Verify configuration was created
-- SELECT 
--     a.name as academy_name,
--     gc.field_label,
--     gc.show_all_option,
--     gc.all_grades_label,
--     COUNT(go.id) as grade_options_count
-- FROM academies a
-- JOIN grade_configurations gc ON a.id = gc.academy_id
-- LEFT JOIN grade_options go ON a.id = go.academy_id AND go.deleted_at IS NULL
-- WHERE a.deleted_at IS NULL 
-- AND gc.deleted_at IS NULL
-- GROUP BY a.id, a.name, gc.field_label, gc.show_all_option, gc.all_grades_label;

-- View sample grade options
-- SELECT 
--     a.name as academy_name,
--     go.grade_value,
--     go.display_name,
--     go.short_name,
--     go.sort_order
-- FROM academies a
-- JOIN grade_options go ON a.id = go.academy_id
-- WHERE a.deleted_at IS NULL 
-- AND go.deleted_at IS NULL
-- ORDER BY a.name, go.sort_order;

-- Test the helper function
-- SELECT get_grade_display_name(
--     (SELECT id FROM academies LIMIT 1), 
--     7
-- ) as middle_school_display;