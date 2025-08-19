-- Fix ExamScheduleMatrix many-to-many table to reference RoutineExam instead of legacy Exam
-- This manually updates the database schema to match the model changes

BEGIN TRANSACTION;

-- 1. Drop the old many-to-many table (this will lose any existing data)
DROP TABLE IF EXISTS primepath_routinetest_examschedulematrix_exams;

-- 2. Create the new many-to-many table that references RoutineExam
CREATE TABLE primepath_routinetest_examschedulematrix_exams (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    examschedulematrix_id CHAR(32) NOT NULL REFERENCES primepath_routinetest_examschedulematrix (id) DEFERRABLE INITIALLY DEFERRED,
    routineexam_id CHAR(32) NOT NULL REFERENCES routinetest_exam (id) DEFERRABLE INITIALLY DEFERRED
);

-- 3. Create indexes
CREATE UNIQUE INDEX primepath_routinetest_examschedulematrix_exams_examschedulematrix_id_routineexam_id_uniq 
    ON primepath_routinetest_examschedulematrix_exams (examschedulematrix_id, routineexam_id);
    
CREATE INDEX primepath_routinetest_examschedulematrix_exams_examschedulematrix_id_idx 
    ON primepath_routinetest_examschedulematrix_exams (examschedulematrix_id);
    
CREATE INDEX primepath_routinetest_examschedulematrix_exams_routineexam_id_idx 
    ON primepath_routinetest_examschedulematrix_exams (routineexam_id);

COMMIT;