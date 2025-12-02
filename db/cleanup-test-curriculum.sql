-- Script to Clean Up Test Curriculum Data
-- This removes test/dummy curriculum entries while preserving real curriculum data
-- Run this in Supabase SQL Editor

-- First, let's see what curriculum nodes exist (for verification)
-- Uncomment to run:
-- SELECT id, name, level_depth, parent_id 
-- FROM curriculum_nodes 
-- WHERE academy_id IN (SELECT id FROM academies)
-- ORDER BY level_depth, name;

-- Delete test curriculum nodes (cascading will handle children)
-- These are identified by obvious test names
DELETE FROM curriculum_nodes 
WHERE name IN (
    'Test Category',
    'Test Program',
    'Test Level',
    'Dummy Program',
    'Dummy Level',
    'Sample Category',
    'Demo Level',
    'Testing',
    'test',
    'TEST'
) 
AND deleted_at IS NULL;

-- Alternative: Mark test nodes as deleted (safer approach)
-- UPDATE curriculum_nodes 
-- SET deleted_at = NOW(), is_active = false
-- WHERE name IN (
--     'Test Category',
--     'Test Program', 
--     'Test Level',
--     'Dummy Program',
--     'Dummy Level',
--     'Sample Category',
--     'Demo Level',
--     'Testing',
--     'test',
--     'TEST'
-- )
-- AND deleted_at IS NULL;

-- Clean up any orphaned nodes (nodes whose parents were deleted)
-- This ensures hierarchical integrity
WITH RECURSIVE node_tree AS (
    -- Find all nodes with valid parents or no parents (root nodes)
    SELECT id, parent_id, name, level_depth
    FROM curriculum_nodes
    WHERE (parent_id IS NULL OR parent_id IN (
        SELECT id FROM curriculum_nodes WHERE deleted_at IS NULL
    ))
    AND deleted_at IS NULL
    
    UNION
    
    -- Recursively include all children of valid nodes
    SELECT c.id, c.parent_id, c.name, c.level_depth
    FROM curriculum_nodes c
    INNER JOIN node_tree nt ON c.parent_id = nt.id
    WHERE c.deleted_at IS NULL
)
-- Mark orphaned nodes as deleted
UPDATE curriculum_nodes
SET deleted_at = NOW(), is_active = false
WHERE id NOT IN (SELECT id FROM node_tree)
AND deleted_at IS NULL;

-- Verify cleanup results
SELECT 
    'Active Curriculum Nodes' as status,
    COUNT(*) as count
FROM curriculum_nodes
WHERE deleted_at IS NULL AND is_active = true

UNION ALL

SELECT 
    'Deleted Curriculum Nodes' as status,
    COUNT(*) as count
FROM curriculum_nodes
WHERE deleted_at IS NOT NULL OR is_active = false;

-- Show remaining active curriculum structure
SELECT 
    cn.name,
    cn.level_depth,
    cn.code,
    CASE 
        WHEN cn.parent_id IS NULL THEN 'Root Level'
        ELSE parent.name
    END as parent_name
FROM curriculum_nodes cn
LEFT JOIN curriculum_nodes parent ON cn.parent_id = parent.id
WHERE cn.deleted_at IS NULL 
AND cn.is_active = true
ORDER BY cn.level_depth, cn.sort_order, cn.name;