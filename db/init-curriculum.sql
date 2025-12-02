-- Curriculum System Initialization Script
-- Run this in Supabase SQL Editor to initialize the curriculum tables
-- This is safe to run multiple times - it uses IF NOT EXISTS checks

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-----------------------------
-- 1. curriculum_settings table
-----------------------------
CREATE TABLE IF NOT EXISTS curriculum_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    max_depth INTEGER NOT NULL DEFAULT 4 CHECK (max_depth >= 1 AND max_depth <= 4),
    level_1_name VARCHAR(50) DEFAULT 'Category',
    level_2_name VARCHAR(50) DEFAULT 'Sub-Category',
    level_3_name VARCHAR(50) DEFAULT 'Level',
    level_4_name VARCHAR(50) DEFAULT 'Sub-Level',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Create unique index for academy
CREATE UNIQUE INDEX IF NOT EXISTS idx_curriculum_settings_academy
ON curriculum_settings (academy_id) WHERE deleted_at IS NULL;

-----------------------------
-- 2. curriculum_nodes table
-----------------------------
CREATE TABLE IF NOT EXISTS curriculum_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES curriculum_nodes(id) ON DELETE CASCADE,
    level_depth INTEGER NOT NULL CHECK (level_depth >= 1 AND level_depth <= 4),
    sort_order INTEGER NOT NULL DEFAULT 0,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    description TEXT,
    target_grade_min INTEGER,
    target_grade_max INTEGER,
    capacity INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_curriculum_nodes_academy
ON curriculum_nodes (academy_id);

CREATE INDEX IF NOT EXISTS idx_curriculum_nodes_parent
ON curriculum_nodes (parent_id);

CREATE INDEX IF NOT EXISTS idx_curriculum_nodes_level
ON curriculum_nodes (level_depth);

CREATE INDEX IF NOT EXISTS idx_curriculum_nodes_hierarchy
ON curriculum_nodes (academy_id, parent_id, level_depth, sort_order);

-----------------------------
-- 3. Update classes table
-----------------------------
ALTER TABLE classes 
ADD COLUMN IF NOT EXISTS curriculum_node_id UUID REFERENCES curriculum_nodes(id);

CREATE INDEX IF NOT EXISTS idx_classes_curriculum_node
ON classes (curriculum_node_id);

-----------------------------
-- 4. Insert default settings for existing academies
-----------------------------
INSERT INTO curriculum_settings (
    academy_id, 
    max_depth, 
    level_1_name, 
    level_2_name, 
    level_3_name, 
    level_4_name
)
SELECT 
    id as academy_id,
    3 as max_depth,
    'Program' as level_1_name,
    'Track' as level_2_name, 
    'Level' as level_3_name,
    'Section' as level_4_name
FROM academies 
WHERE NOT EXISTS (
    SELECT 1 FROM curriculum_settings 
    WHERE curriculum_settings.academy_id = academies.id 
    AND curriculum_settings.deleted_at IS NULL
)
AND academies.deleted_at IS NULL;

-----------------------------
-- 5. Grant necessary permissions
-----------------------------
-- Grant permissions for authenticated users
GRANT ALL ON curriculum_settings TO authenticated;
GRANT ALL ON curriculum_nodes TO authenticated;

-- Grant permissions for anon users (if needed)
GRANT SELECT ON curriculum_settings TO anon;
GRANT SELECT ON curriculum_nodes TO anon;

-----------------------------
-- Verification Query - Run this to check if tables were created successfully
-----------------------------
-- SELECT 
--     'curriculum_settings' as table_name, 
--     COUNT(*) as row_count 
-- FROM curriculum_settings
-- UNION ALL
-- SELECT 
--     'curriculum_nodes' as table_name, 
--     COUNT(*) as row_count 
-- FROM curriculum_nodes;