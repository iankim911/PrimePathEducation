# Database Setup Checklist

## Required Tables for PrimePath v2

### Core Tables (should exist)
- [ ] academies
- [ ] students  
- [ ] teachers
- [ ] classes
- [ ] enrollments
- [ ] attendance

### Curriculum Tables (may need manual creation)
- [ ] curriculum_settings
- [ ] curriculum_nodes

## Quick Check Commands

**Verify all tables exist:**
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

**Expected tables:**
- academies
- attendance
- classes
- curriculum_nodes ← MUST EXIST
- curriculum_settings ← MUST EXIST  
- enrollments
- students
- users

## If curriculum tables missing, run:
1. Create tables using SQL commands in this file
2. Insert sample data
3. Restart development server
4. Test "Add New Class" form

## Red Flags
- "No curriculum structure configured" message
- Missing tables in Supabase table list
- 500 errors when saving curriculum settings

## Contact
If tables keep disappearing, check:
- Supabase project status
- Database connection settings
- .env.local file configuration