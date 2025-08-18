# RoutineTest Administrator Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [System Overview](#system-overview)
3. [User Management](#user-management)
4. [Class Management](#class-management)
5. [Exam Management](#exam-management)
6. [Reports & Analytics](#reports-analytics)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Login
1. Navigate to: http://your-domain.com/RoutineTest/
2. Click "Admin Login"
3. Enter credentials:
   - Username: admin
   - Password: [provided by IT]

### Dashboard Overview
Upon login, you'll see:
- Total users count
- Active classes
- Pending exams
- Recent activity

## System Overview

### User Hierarchy
```
Admin (You)
├── Teachers (Manage classes)
│   └── Students (Take exams)
```

### Key Responsibilities
- Create and manage classes
- Assign teachers to classes
- Upload exam content
- Set answer keys
- Monitor system usage
- Generate reports

## User Management

### Creating Teacher Accounts

#### Method 1: Django Admin
1. Go to `/admin/`
2. Click "Users" → "Add User"
3. Enter username and password
4. Save and continue editing
5. Check "Staff status"
6. Go to "Teachers" → "Add Teacher"
7. Link to user account

#### Method 2: Bulk Import
```python
# Use the management command:
python manage.py import_teachers teachers.csv
```

CSV Format:
```csv
name,email,username
Ms. Smith,smith@school.edu,teacher.smith
Mr. Johnson,johnson@school.edu,teacher.johnson
```

### Managing Student Accounts
Students self-register, then teachers assign them to classes.

To view all students:
1. Go to "Students" section
2. Filter by grade level
3. Search by name

## Class Management

### Creating a New Class

1. Navigate to "Classes" → "Create New"
2. Enter details:
   - **Name**: e.g., "Mathematics 5A"
   - **Grade Level**: Select from dropdown
   - **Section**: A, B, C, etc.
   - **Academic Year**: 2024-2025
3. Click "Create Class"

### Assigning Teachers

1. Go to class details
2. Click "Assign Teachers"
3. Select teachers from list
4. Click "Save"

**Note**: Multiple teachers can be assigned to one class.

### Class Settings

- **Max Students**: 20 (default)
- **Status**: Active/Inactive
- **Quarter**: Q1, Q2, Q3, Q4

## Exam Management

### Uploading Exams

1. Go to "Exams" → "Upload New"
2. Fill in details:
   - **Name**: Clear, descriptive name
   - **Type**: Monthly Review or Quarterly
   - **Curriculum Level**: Select from 44 levels
   - **Quarter**: Q1-Q4
   - **PDF File**: Upload exam PDF
3. Click "Upload"

### Setting Answer Keys

1. Find exam in list
2. Click "Set Answer Key"
3. Enter answers:
   ```json
   {
     "1": "A",
     "2": "B",
     "3": "C",
     "4": "addition",
     "5": "D"
   }
   ```
4. Save answer key

### Answer Key Format
- Multiple choice: "A", "B", "C", "D"
- Short answer: exact text match
- Case-insensitive for text answers

### Managing Exam Assignments

View all assignments:
1. Go to "Exam Assignments"
2. Filter by:
   - Class
   - Teacher
   - Status
   - Deadline

## Reports & Analytics

### Available Reports

#### 1. Class Performance Report
Shows:
- Average scores by class
- Completion rates
- Top performers

#### 2. Student Progress Report
Shows:
- Individual student scores
- Attempt history
- Improvement trends

#### 3. Exam Statistics Report
Shows:
- Question difficulty analysis
- Common wrong answers
- Time spent per question

### Exporting Data

1. Navigate to "Reports"
2. Select report type
3. Choose format:
   - CSV (Excel compatible)
   - PDF (for printing)
   - JSON (for developers)
4. Click "Export"

### Scheduling Reports

Set up automated reports:
1. Go to "Report Schedule"
2. Select frequency (Daily/Weekly/Monthly)
3. Choose recipients
4. Save schedule

## System Administration

### Backup Procedures

Daily backups recommended:
```bash
# Database backup
python manage.py dbbackup

# Media files backup
tar -czf media_backup.tar.gz media/
```

### User Permissions

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| Admin | Everything | N/A |
| Teacher | Manage assigned classes | Create classes, Delete exams |
| Student | Take exams, View scores | Access other students' data |

### Security Settings

1. **Password Requirements**:
   - Minimum 8 characters
   - Mix of letters and numbers
   - Change every 90 days

2. **Session Management**:
   - Auto-logout after 30 minutes
   - Single session per user

3. **Data Protection**:
   - All data encrypted in transit
   - Daily backups
   - Access logs maintained

## Troubleshooting

### Common Issues

#### Issue: Teacher cannot see assigned class
**Solution**:
1. Check teacher-class assignment
2. Verify teacher account is active
3. Clear browser cache

#### Issue: Exam PDF not displaying
**Solution**:
1. Check file upload completed
2. Verify PDF is not corrupted
3. Try re-uploading

#### Issue: Scores not calculating
**Solution**:
1. Verify answer key is set
2. Check answer format matches
3. Review attempt data

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Permission Denied" | User lacks access | Check user role |
| "Class Full" | Max students reached | Increase limit or create new section |
| "Invalid Answer Key" | Format error | Review JSON format |
| "Deadline Passed" | Exam expired | Extend deadline |

### Getting Help

1. **Check Logs**:
   ```bash
   tail -f logs/routinetest.log
   ```

2. **Contact Support**:
   - Email: support@primepath.edu
   - Phone: 555-0100
   - Hours: Mon-Fri 8am-5pm

3. **Emergency Contacts**:
   - IT Director: ext. 101
   - Database Admin: ext. 102
   - Security Team: ext. 103

## Best Practices

### Daily Tasks
- [ ] Check system health dashboard
- [ ] Review pending teacher requests
- [ ] Monitor active exams
- [ ] Check error logs

### Weekly Tasks
- [ ] Generate performance reports
- [ ] Review user activity
- [ ] Clean up old sessions
- [ ] Update exam content

### Monthly Tasks
- [ ] Full system backup
- [ ] User audit
- [ ] Performance review
- [ ] Update documentation

### Quarterly Tasks
- [ ] Reset classes for new quarter
- [ ] Archive old data
- [ ] Security audit
- [ ] Teacher training

## Appendix

### Curriculum Levels (44 Total)

**PRIME CORE** (12 levels)
- CORE Phonics Level 1, 2, 3
- CORE Sigma Level 1, 2, 3
- CORE Elite Level 1, 2, 3
- CORE Pro Level 1, 2, 3

**PRIME ASCENT** (12 levels)
- ASCENT Nova Level 1, 2, 3
- ASCENT Drive Level 1, 2, 3
- ASCENT Pro Level 1, 2, 3
- [Fourth subprogram] Level 1, 2, 3

**PRIME EDGE** (12 levels)
- EDGE Spark Level 1, 2, 3
- EDGE Rise Level 1, 2, 3
- EDGE Pursuit Level 1, 2, 3
- EDGE Pro Level 1, 2, 3

**PRIME PINNACLE** (8 levels)
- PINNACLE Vision Level 1, 2
- PINNACLE Endeavor Level 1, 2
- PINNACLE Success Level 1, 2
- PINNACLE Pro Level 1, 2

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Save |
| Ctrl+N | New item |
| Ctrl+F | Search |
| Esc | Cancel |
| F1 | Help |

---
**Version**: 1.0
**Last Updated**: August 18, 2025
**Next Review**: September 2025