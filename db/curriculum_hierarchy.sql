-- Hierarchical Curriculum System Extension
-- Adds flexible curriculum hierarchy to support 1-4 level deep structures

-----------------------------
-- 1. curriculum_settings (Academy-level configuration)
-----------------------------
CREATE TABLE IF NOT EXISTS curriculum_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    
    -- Configuration
    max_depth INTEGER NOT NULL DEFAULT 4 CHECK (max_depth >= 1 AND max_depth <= 4),
    level_1_name VARCHAR(50) DEFAULT 'Category',     -- e.g., "Program", "Department"
    level_2_name VARCHAR(50) DEFAULT 'Sub-Category', -- e.g., "Track", "Focus Area"  
    level_3_name VARCHAR(50) DEFAULT 'Level',        -- e.g., "Level", "Grade"
    level_4_name VARCHAR(50) DEFAULT 'Sub-Level',    -- e.g., "Section", "Class"
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_curriculum_settings_academy
ON curriculum_settings (academy_id) WHERE deleted_at IS NULL;

-----------------------------
-- 2. curriculum_nodes (Hierarchical curriculum structure)
-----------------------------
CREATE TABLE IF NOT EXISTS curriculum_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID NOT NULL REFERENCES academies(id) ON DELETE CASCADE,
    
    -- Hierarchy
    parent_id UUID REFERENCES curriculum_nodes(id) ON DELETE CASCADE,
    level_depth INTEGER NOT NULL CHECK (level_depth >= 1 AND level_depth <= 4),
    sort_order INTEGER NOT NULL DEFAULT 0,
    
    -- Content
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),          -- Optional short code like "ELM-A1"
    description TEXT,
    
    -- Metadata
    target_grade_min INTEGER,
    target_grade_max INTEGER,
    capacity INTEGER,          -- Max students for this curriculum path
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Indexes for efficient hierarchy queries
CREATE INDEX IF NOT EXISTS idx_curriculum_nodes_academy
ON curriculum_nodes (academy_id);

CREATE INDEX IF NOT EXISTS idx_curriculum_nodes_parent
ON curriculum_nodes (parent_id);

CREATE INDEX IF NOT EXISTS idx_curriculum_nodes_level
ON curriculum_nodes (level_depth);

CREATE INDEX IF NOT EXISTS idx_curriculum_nodes_hierarchy
ON curriculum_nodes (academy_id, parent_id, level_depth, sort_order);

-- Ensure nodes don't exceed academy's max_depth setting
CREATE OR REPLACE FUNCTION validate_curriculum_depth()
RETURNS TRIGGER AS $$
DECLARE
    max_allowed_depth INTEGER;
BEGIN
    SELECT max_depth INTO max_allowed_depth
    FROM curriculum_settings 
    WHERE academy_id = NEW.academy_id AND deleted_at IS NULL;
    
    IF max_allowed_depth IS NULL THEN
        max_allowed_depth := 4; -- Default if no settings found
    END IF;
    
    IF NEW.level_depth > max_allowed_depth THEN
        RAISE EXCEPTION 'Curriculum depth % exceeds academy maximum of %', 
            NEW.level_depth, max_allowed_depth;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_curriculum_depth
    BEFORE INSERT OR UPDATE ON curriculum_nodes
    FOR EACH ROW EXECUTE FUNCTION validate_curriculum_depth();

-----------------------------
-- 3. Update classes table to link to curriculum
-----------------------------
-- Add foreign key to curriculum_nodes
ALTER TABLE classes 
ADD COLUMN IF NOT EXISTS curriculum_node_id UUID REFERENCES curriculum_nodes(id);

-- Create index for the new relationship
CREATE INDEX IF NOT EXISTS idx_classes_curriculum_node
ON classes (curriculum_node_id);

-- Migration note: existing classes will have NULL curriculum_node_id
-- They can continue to work with the legacy level_label system
-- New classes should use curriculum_node_id for hierarchical curriculum

-----------------------------
-- 4. Helper view for curriculum paths
-----------------------------
CREATE OR REPLACE VIEW curriculum_paths AS
WITH RECURSIVE curriculum_tree AS (
    -- Base case: root nodes
    SELECT 
        id,
        academy_id,
        parent_id,
        level_depth,
        name,
        code,
        name AS path_name,
        COALESCE(code, name) AS path_code,
        ARRAY[id] AS path_ids
    FROM curriculum_nodes 
    WHERE parent_id IS NULL AND deleted_at IS NULL
    
    UNION ALL
    
    -- Recursive case: child nodes
    SELECT 
        c.id,
        c.academy_id,
        c.parent_id,
        c.level_depth,
        c.name,
        c.code,
        ct.path_name || ' > ' || c.name,
        ct.path_code || '.' || COALESCE(c.code, c.name),
        ct.path_ids || c.id
    FROM curriculum_nodes c
    JOIN curriculum_tree ct ON c.parent_id = ct.id
    WHERE c.deleted_at IS NULL
)
SELECT * FROM curriculum_tree;

-----------------------------
-- 5. Default curriculum settings for existing academies
-----------------------------
INSERT INTO curriculum_settings (academy_id, max_depth, level_1_name, level_2_name, level_3_name, level_4_name)
SELECT 
    id as academy_id,
    3 as max_depth,  -- Start with 3 levels: Program > Track > Level
    'Program' as level_1_name,
    'Track' as level_2_name, 
    'Level' as level_3_name,
    'Section' as level_4_name
FROM academies 
WHERE id NOT IN (SELECT academy_id FROM curriculum_settings WHERE deleted_at IS NULL);