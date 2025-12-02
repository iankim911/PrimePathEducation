-- Sample Professional Curriculum Structure for Language Academy
-- Run this AFTER cleanup-test-curriculum.sql to populate with real curriculum
-- This creates a 3-level hierarchy: Program > Track > Level

-- Get the first academy ID (adjust if you have multiple academies)
DO $$
DECLARE
    v_academy_id UUID;
    v_general_english_id UUID;
    v_business_english_id UUID;
    v_test_prep_id UUID;
    v_specialized_id UUID;
BEGIN
    -- Get academy ID
    SELECT id INTO v_academy_id FROM academies WHERE deleted_at IS NULL LIMIT 1;
    
    IF v_academy_id IS NULL THEN
        RAISE EXCEPTION 'No active academy found';
    END IF;
    
    -- Check if curriculum already exists
    IF EXISTS (SELECT 1 FROM curriculum_nodes WHERE academy_id = v_academy_id AND deleted_at IS NULL) THEN
        RAISE NOTICE 'Curriculum already exists for this academy. Skipping creation.';
        RETURN;
    END IF;
    
    -- Level 1: Main Programs
    INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order, description)
    VALUES 
        (v_academy_id, NULL, 1, 'General English', 'GE', 1, 'Comprehensive English language program')
    RETURNING id INTO v_general_english_id;
    
    INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order, description)
    VALUES 
        (v_academy_id, NULL, 1, 'Business English', 'BE', 2, 'English for professional and business contexts')
    RETURNING id INTO v_business_english_id;
    
    INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order, description)
    VALUES 
        (v_academy_id, NULL, 1, 'Test Preparation', 'TP', 3, 'Standardized test preparation programs')
    RETURNING id INTO v_test_prep_id;
    
    INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order, description)
    VALUES 
        (v_academy_id, NULL, 1, 'Specialized Programs', 'SP', 4, 'Focused skill development programs')
    RETURNING id INTO v_specialized_id;
    
    -- Level 2 & 3: General English Tracks and Levels
    WITH ge_tracks AS (
        INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order, target_grade_min, target_grade_max)
        VALUES 
            (v_academy_id, v_general_english_id, 2, 'Elementary', 'GE-ELM', 1, 1, 6),
            (v_academy_id, v_general_english_id, 2, 'Middle School', 'GE-MS', 2, 7, 9),
            (v_academy_id, v_general_english_id, 2, 'High School', 'GE-HS', 3, 10, 12)
        RETURNING id, code
    )
    INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order, capacity)
    SELECT 
        v_academy_id,
        ge.id,
        3,
        levels.name,
        ge.code || '-' || levels.code,
        levels.sort_order,
        12 -- Default class capacity
    FROM ge_tracks ge
    CROSS JOIN (
        VALUES 
            ('Beginner', 'BEG', 1),
            ('Elementary', 'ELM', 2),
            ('Pre-Intermediate', 'PRE', 3),
            ('Intermediate', 'INT', 4),
            ('Upper-Intermediate', 'UPP', 5),
            ('Advanced', 'ADV', 6)
    ) AS levels(name, code, sort_order);
    
    -- Level 2 & 3: Business English Tracks and Levels
    WITH be_tracks AS (
        INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order)
        VALUES 
            (v_academy_id, v_business_english_id, 2, 'Professional Communication', 'BE-PC', 1),
            (v_academy_id, v_business_english_id, 2, 'Business Writing', 'BE-BW', 2),
            (v_academy_id, v_business_english_id, 2, 'Presentation Skills', 'BE-PS', 3)
        RETURNING id, code
    )
    INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order, capacity)
    SELECT 
        v_academy_id,
        be.id,
        3,
        levels.name,
        be.code || '-' || levels.code,
        levels.sort_order,
        10 -- Smaller class size for business English
    FROM be_tracks be
    CROSS JOIN (
        VALUES 
            ('Foundation', 'FND', 1),
            ('Intermediate', 'INT', 2),
            ('Advanced', 'ADV', 3)
    ) AS levels(name, code, sort_order);
    
    -- Level 2 & 3: Test Preparation Programs
    WITH tp_programs AS (
        INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order, description)
        VALUES 
            (v_academy_id, v_test_prep_id, 2, 'TOEFL', 'TP-TOEFL', 1, 'TOEFL iBT preparation'),
            (v_academy_id, v_test_prep_id, 2, 'TOEIC', 'TP-TOEIC', 2, 'TOEIC preparation'),
            (v_academy_id, v_test_prep_id, 2, 'IELTS', 'TP-IELTS', 3, 'IELTS Academic/General preparation')
        RETURNING id, code, name
    )
    INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order, capacity)
    SELECT 
        v_academy_id,
        tp.id,
        3,
        CASE 
            WHEN tp.name = 'TOEFL' THEN levels.toefl_name
            WHEN tp.name = 'TOEIC' THEN levels.toeic_name
            ELSE levels.ielts_name
        END,
        tp.code || '-' || levels.code,
        levels.sort_order,
        8 -- Small class size for test prep
    FROM tp_programs tp
    CROSS JOIN (
        VALUES 
            ('Basic (Score 40-60)', 'Basic (Score 400-600)', 'Band 4.0-5.0', 'BSC', 1),
            ('Intermediate (Score 60-80)', 'Intermediate (Score 600-750)', 'Band 5.5-6.5', 'INT', 2),
            ('Advanced (Score 80+)', 'Advanced (Score 750+)', 'Band 7.0+', 'ADV', 3)
    ) AS levels(toefl_name, toeic_name, ielts_name, code, sort_order);
    
    -- Level 2 & 3: Specialized Programs
    WITH sp_tracks AS (
        INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order, description)
        VALUES 
            (v_academy_id, v_specialized_id, 2, 'Speaking Focus', 'SP-SPK', 1, 'Intensive speaking and conversation'),
            (v_academy_id, v_specialized_id, 2, 'Writing Workshop', 'SP-WRT', 2, 'Academic and creative writing'),
            (v_academy_id, v_specialized_id, 2, 'Grammar Clinic', 'SP-GRM', 3, 'Focused grammar improvement')
        RETURNING id, code
    )
    INSERT INTO curriculum_nodes (academy_id, parent_id, level_depth, name, code, sort_order, capacity)
    SELECT 
        v_academy_id,
        sp.id,
        3,
        levels.name,
        sp.code || '-' || levels.code,
        levels.sort_order,
        10
    FROM sp_tracks sp
    CROSS JOIN (
        VALUES 
            ('Foundation', 'FND', 1),
            ('Intermediate', 'INT', 2),
            ('Advanced', 'ADV', 3)
    ) AS levels(name, code, sort_order);
    
    RAISE NOTICE 'Successfully created curriculum structure for academy %', v_academy_id;
    
END $$;

-- Verify the created structure
SELECT 
    'Level ' || level_depth as level,
    COUNT(*) as node_count
FROM curriculum_nodes
WHERE deleted_at IS NULL AND is_active = true
GROUP BY level_depth
ORDER BY level_depth;

-- Show sample of the hierarchy
WITH curriculum_tree AS (
    SELECT 
        cn1.name as program,
        cn2.name as track,
        cn3.name as level,
        cn3.code as level_code,
        cn3.capacity
    FROM curriculum_nodes cn1
    LEFT JOIN curriculum_nodes cn2 ON cn2.parent_id = cn1.id AND cn2.deleted_at IS NULL
    LEFT JOIN curriculum_nodes cn3 ON cn3.parent_id = cn2.id AND cn3.deleted_at IS NULL
    WHERE cn1.parent_id IS NULL 
    AND cn1.deleted_at IS NULL
    ORDER BY cn1.sort_order, cn2.sort_order, cn3.sort_order
)
SELECT * FROM curriculum_tree WHERE level IS NOT NULL LIMIT 20;