# User Testing Plan - RoutineTest

## Quick Start Testing Guide

### 1. Start the Development Server
```bash
cd primepath_project
../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
```

### 2. Access the Application
Open browser: http://127.0.0.1:8000/RoutineTest/

### 3. Test Accounts to Create

#### Admin Account
```python
python manage.py createsuperuser
Username: admin
Email: admin@school.com
Password: Admin123!
```

#### Teacher Accounts
```python
python manage.py shell
from django.contrib.auth.models import User
from core.models import Teacher

# Teacher 1
user1 = User.objects.create_user('teacher1', 'teacher1@school.com', 'Teacher123!')
Teacher.objects.create(user=user1, name='Ms. Smith', email='teacher1@school.com')

# Teacher 2
user2 = User.objects.create_user('teacher2', 'teacher2@school.com', 'Teacher123!')
Teacher.objects.create(user=user2, name='Mr. Johnson', email='teacher2@school.com')
```

#### Student Accounts
```python
from core.models import Student

# Students (no user account needed initially)
Student.objects.create(name='John Doe', current_grade_level='Grade 5')
Student.objects.create(name='Jane Smith', current_grade_level='Grade 5')
Student.objects.create(name='Bob Wilson', current_grade_level='Grade 6')
```

### 4. Test Scenarios

#### Scenario 1: Admin Creates Classes
1. Login as admin
2. Navigate to Class Management
3. Create classes:
   - "Grade 5 - Section A"
   - "Grade 5 - Section B"
   - "Grade 6 - Section A"
4. Assign teachers to classes

#### Scenario 2: Teacher Enrolls Students
1. Login as teacher1
2. View assigned classes
3. Enroll students:
   - Add John Doe to Grade 5-A
   - Add Jane Smith to Grade 5-A
   - Add Bob Wilson to Grade 6-A

#### Scenario 3: Upload and Assign Exam
1. Login as admin
2. Upload exam PDF:
   - Name: "Q1 Monthly Review - Math"
   - Type: Monthly Review
   - Curriculum: CORE Phonics Level 1
   - Quarter: Q1
3. Set answer key:
   ```json
   {
     "1": "A",
     "2": "B", 
     "3": "C",
     "4": "D",
     "5": "addition"
   }
   ```
4. Login as teacher
5. Assign exam to Grade 5-A
6. Set deadline: 7 days from now

#### Scenario 4: Student Takes Exam
1. Create student user account
2. Login as student
3. View assigned exams
4. Start exam
5. Answer questions
6. Test auto-save (wait 60 seconds)
7. Submit exam
8. View results

#### Scenario 5: Teacher Reviews Results
1. Login as teacher
2. View class results
3. Export to CSV
4. Check individual student scores

### 5. Testing Checklist

#### Authentication ✓
- [ ] Admin can login
- [ ] Teacher can login
- [ ] Student can login
- [ ] Logout works
- [ ] Session persists

#### Class Management ✓
- [ ] Create class
- [ ] Assign teacher
- [ ] Remove teacher
- [ ] View all classes
- [ ] Edit class details

#### Student Management ✓
- [ ] Enroll student
- [ ] Bulk enroll
- [ ] Unenroll student
- [ ] View class roster
- [ ] Search students

#### Exam Management ✓
- [ ] Upload PDF
- [ ] Set answer key
- [ ] Edit exam details
- [ ] Clone exam
- [ ] Delete exam

#### Exam Assignment ✓
- [ ] Assign to class
- [ ] Individual assignment
- [ ] Set deadline
- [ ] Extend deadline
- [ ] View assignments

#### Student Experience ✓
- [ ] View exams
- [ ] Start exam
- [ ] Answer questions
- [ ] Auto-save works
- [ ] Submit exam
- [ ] View score
- [ ] View history

#### Results & Reports ✓
- [ ] Calculate scores
- [ ] Show results
- [ ] Track attempts
- [ ] Export CSV
- [ ] Class statistics

### 6. Bug Report Template

```markdown
## Bug Report

**Date**: 
**Tester**: 
**Module**: [Authentication/Classes/Students/Exams/Results]

**Description**:
[What happened?]

**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**:
[What should happen?]

**Actual Behavior**:
[What actually happened?]

**Error Messages**:
```
[Paste any error messages]
```

**Screenshot**:
[Attach if applicable]

**Severity**: [Critical/High/Medium/Low]
```

### 7. Performance Testing

#### Load Test Scenarios
1. **Concurrent Users**
   - 30 teachers login simultaneously
   - 100 students take exam at same time
   - Multiple file uploads

2. **Data Volume**
   - Create 50 classes
   - Enroll 400 students
   - Upload 100 exams
   - Generate 1000 attempts

3. **Response Times**
   - Login: < 2 seconds
   - Page load: < 3 seconds
   - Exam submit: < 5 seconds
   - Export: < 10 seconds

### 8. Feedback Collection

#### Teacher Feedback Form
- Ease of use (1-10)
- Missing features
- Confusing areas
- Improvement suggestions

#### Student Feedback Form
- Test-taking experience (1-10)
- Technical issues
- UI/UX feedback
- Feature requests

#### Admin Feedback Form
- Management capabilities
- Reporting needs
- Integration requirements
- Training needs

---
**Ready to Begin Testing!**