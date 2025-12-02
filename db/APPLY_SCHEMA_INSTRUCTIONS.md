# How to Apply Test Management Schema to Supabase

## Steps to Apply the Schema:

### 1. Open Supabase Dashboard
- Go to your Supabase project dashboard
- Navigate to the **SQL Editor** tab on the left sidebar

### 2. Apply the Schema
- Open the file `db/test-management-schema.sql` in this project
- Copy the entire contents of the file
- Paste it into the Supabase SQL Editor
- Click **Run** to execute the SQL

### 3. Verify Tables Were Created
After running the SQL, you should see these new tables in your database:

**Test Management Tables:**
- `exam_types` - Exam categories (Quiz, Midterm, Final, etc.)
- `exams` - Main exam records
- `exam_sections` - Exam sections (Reading, Listening, etc.)
- `exam_files` - PDF, image, and audio files
- `exam_questions` - Individual test questions
- `exam_sessions` - Live exam instances
- `exam_session_participants` - Student participation tracking
- `student_exam_attempts` - Student test attempts
- `student_answers` - Individual question responses
- `curriculum_exam_mappings` - Links exams to curriculum
- `class_exam_assignments` - Assigns exams to classes

### 4. Check for Errors
If you get any errors when running the schema:

**Common Issues:**
1. **Table already exists**: If you've run this before, you may need to drop the existing tables first
2. **Missing references**: Make sure your existing tables (academies, users, students, classes, curriculum_nodes) exist
3. **UUID extension**: The schema tries to create the UUID extension, but it should already exist in Supabase

### 5. Verify in Table Editor
- Go to the **Table Editor** tab in Supabase
- You should see all the new exam-related tables
- Check that the relationships are properly set up

### 6. Test the Tables
You can run this test query to verify everything is working:

```sql
-- Test query to verify tables exist
SELECT 
    tablename 
FROM 
    pg_tables 
WHERE 
    schemaname = 'public' 
    AND tablename LIKE 'exam%'
ORDER BY 
    tablename;
```

This should return all the exam-related tables.

## If You Need to Reset/Restart

If you need to drop all test management tables and start fresh:

```sql
-- WARNING: This will delete all test management data!
DROP TABLE IF EXISTS student_answers CASCADE;
DROP TABLE IF EXISTS student_exam_attempts CASCADE;
DROP TABLE IF EXISTS exam_session_participants CASCADE;
DROP TABLE IF EXISTS exam_sessions CASCADE;
DROP TABLE IF EXISTS class_exam_assignments CASCADE;
DROP TABLE IF EXISTS curriculum_exam_mappings CASCADE;
DROP TABLE IF EXISTS exam_questions CASCADE;
DROP TABLE IF EXISTS exam_files CASCADE;
DROP TABLE IF EXISTS exam_sections CASCADE;
DROP TABLE IF EXISTS exams CASCADE;
DROP TABLE IF EXISTS exam_types CASCADE;
```

Then you can run the schema file again.

## Next Steps

After successfully applying the schema:
1. Continue with creating the service layer files
2. Build the API endpoints
3. Create the UI components

The tables are now ready to store all test management data!