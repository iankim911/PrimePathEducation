# PrimePath QC Testing Checklist

## 🔍 Quality Control Testing Guide
**Date:** August 18, 2025  
**Sprint:** Emergency RoutineTest Implementation  
**Tester:** _______________

---

## 1. USER AUTHENTICATION & ACCESS CONTROL

### Admin Access
- [ ] Login with admin credentials (`admin` / `Admin123!`)
- [ ] Verify access to both PlacementTest and RoutineTest modules
- [ ] Check Django admin panel access at `/admin/`
- [ ] Verify all menu items are visible and functional
- [ ] Test logout functionality

### Teacher Access
- [ ] Create a new teacher account through admin panel
- [ ] Login as teacher
- [ ] Verify teacher can access RoutineTest dashboard
- [ ] Check teacher can create exams
- [ ] Verify teacher can assign exams to classes
- [ ] Confirm teacher can view student results
- [ ] Test that teacher CANNOT access admin-only features

### Student Access
- [ ] Register a new student account
- [ ] Login as student
- [ ] Verify student can only see assigned exams
- [ ] Check student CANNOT access teacher/admin areas
- [ ] Test password reset functionality

---

## 2. PLACEMENT TEST MODULE (Phase 1 - Existing System)

### Core Functionality
- [ ] Navigate to `/PlacementTest/`
- [ ] Verify index page loads with exam statistics
- [ ] Check "Start Test" button functionality
- [ ] Confirm exam list displays correctly

### Exam Creation (Teacher/Admin)
- [ ] Create a new placement exam
- [ ] Upload PDF file
- [ ] Add audio files (if applicable)
- [ ] Set answer keys for questions
- [ ] Preview exam before publishing
- [ ] Verify exam appears in exam list

### Student Test Taking
- [ ] Start a placement test as student
- [ ] Navigate through questions using number buttons (1-20)
- [ ] Test answer selection (multiple choice)
- [ ] Test short answer input
- [ ] Verify audio playback (if audio questions exist)
- [ ] Check PDF viewer functionality
- [ ] Test timer display
- [ ] Submit exam
- [ ] View results page

### Critical Features to Verify
- [ ] Auto-save every 60 seconds
- [ ] Navigation buttons work correctly
- [ ] Submit confirmation dialog appears
- [ ] Results calculation is accurate
- [ ] Session data persists through page refresh

---

## 3. ROUTINE TEST MODULE (Phase 2 - New System)

### Dashboard Access
- [ ] Navigate to `/RoutineTest/`
- [ ] Verify BCG green theme (#00A65E) is applied
- [ ] Check dashboard statistics display
- [ ] Verify navigation tabs work

### Class Management
- [ ] Navigate to Classes & Exams section
- [ ] Create a new class
- [ ] Set class details (Grade 7A-10C)
- [ ] Assign teachers to classes
- [ ] Enroll students in classes
- [ ] Edit class information
- [ ] View class roster

### Exam Management
- [ ] Create a Monthly Review exam
- [ ] Create a Quarterly exam
- [ ] Select curriculum level (44 levels)
- [ ] Set time period (month or quarter)
- [ ] Upload exam PDF
- [ ] Set answer keys
- [ ] Preview exam

### Exam Assignment
- [ ] Assign exam to specific class
- [ ] Set deadline
- [ ] Configure multiple attempts (if allowed)
- [ ] Bulk assign to multiple classes
- [ ] View assignment status

### Student Experience
- [ ] Login as enrolled student
- [ ] View assigned exams
- [ ] Start an exam
- [ ] Test auto-save functionality
- [ ] Submit exam
- [ ] View results with score breakdown
- [ ] Check if retake is allowed (based on settings)

### Anti-Cheat Measures
- [ ] Test copy/paste is disabled
- [ ] Verify tab switching detection
- [ ] Check violation warnings appear
- [ ] Test automatic submission after 3 violations

---

## 4. CROSS-MODULE INTEGRATION

### Shared Components
- [ ] Teacher profiles work in both modules
- [ ] Student profiles work in both modules
- [ ] Core curriculum structure is consistent
- [ ] User can switch between modules seamlessly

### URL Routing
- [ ] `/PlacementTest/` routes correctly
- [ ] `/RoutineTest/` routes correctly
- [ ] API endpoints respond (`/api/PlacementTest/`, `/api/RoutineTest/`)
- [ ] Legacy URLs redirect properly
- [ ] No 404 errors on main navigation paths

### Database Integrity
- [ ] Create data in PlacementTest, verify it doesn't affect RoutineTest
- [ ] Create data in RoutineTest, verify it doesn't affect PlacementTest
- [ ] Shared models (Teacher, Student) work correctly in both

---

## 5. UI/UX TESTING

### Responsive Design
- [ ] Test on desktop (1920x1080)
- [ ] Test on laptop (1366x768)
- [ ] Test on tablet (iPad)
- [ ] Test on mobile (iPhone/Android)
- [ ] Verify all buttons are clickable
- [ ] Check text is readable at all sizes

### Theme Consistency
- [ ] PlacementTest maintains original theme
- [ ] RoutineTest shows BCG green theme
- [ ] Fonts are consistent
- [ ] Icons display correctly
- [ ] Loading states show appropriately

### Navigation
- [ ] All menu items work
- [ ] Breadcrumbs display correctly
- [ ] Back buttons function properly
- [ ] Tab navigation in RoutineTest works
- [ ] No broken links

---

## 6. DATA MANAGEMENT

### CRUD Operations
- [ ] Create new exams
- [ ] Read/View existing exams
- [ ] Update exam details
- [ ] Delete exams (with confirmation)
- [ ] Same for Classes, Students, Teachers

### Export/Import
- [ ] Export student results to CSV
- [ ] Export class rosters
- [ ] Generate PDF reports
- [ ] Import student lists (if applicable)

### Search & Filter
- [ ] Search students by name
- [ ] Filter exams by type (Monthly/Quarterly)
- [ ] Filter by curriculum level
- [ ] Filter by date range
- [ ] Sort results by various columns

---

## 7. PERFORMANCE TESTING

### Page Load Times
- [ ] Dashboard loads under 3 seconds
- [ ] Exam creation page loads under 2 seconds
- [ ] Student test page loads under 3 seconds
- [ ] Results calculation under 2 seconds

### Concurrent Users
- [ ] Test with 5 simultaneous users
- [ ] Test with 20 simultaneous users
- [ ] Verify no data conflicts
- [ ] Check server doesn't crash

### File Uploads
- [ ] Upload small PDF (< 1MB)
- [ ] Upload medium PDF (1-5MB)
- [ ] Upload large PDF (5-10MB)
- [ ] Verify upload progress indicator
- [ ] Check file validation works

---

## 8. ERROR HANDLING

### Form Validation
- [ ] Submit empty required fields - should show errors
- [ ] Enter invalid email format
- [ ] Enter invalid phone numbers
- [ ] Upload wrong file types
- [ ] Exceed character limits

### Permission Errors
- [ ] Try accessing admin areas as student
- [ ] Try accessing teacher areas as student
- [ ] Verify proper error messages display
- [ ] Check redirect to login when needed

### Network Issues
- [ ] Test with slow connection
- [ ] Test offline mode handling
- [ ] Verify auto-save handles connection loss
- [ ] Check reconnection recovery

---

## 9. EDGE CASES

### Exam Edge Cases
- [ ] Create exam with 0 questions
- [ ] Create exam with 100+ questions
- [ ] Submit exam with no answers
- [ ] Submit exam after deadline
- [ ] Multiple simultaneous exam attempts

### User Edge Cases
- [ ] Student enrolled in no classes
- [ ] Teacher assigned to no classes
- [ ] Class with no students
- [ ] Class with 50+ students

### Data Edge Cases
- [ ] Very long student names
- [ ] Special characters in names
- [ ] Duplicate email addresses (should fail)
- [ ] Same exam assigned twice to same class

---

## 10. SECURITY TESTING

### Authentication Security
- [ ] Test SQL injection in login form
- [ ] Test XSS in input fields
- [ ] Verify passwords are hashed
- [ ] Check session timeout works
- [ ] Test CSRF protection

### Data Security
- [ ] Students cannot see other students' scores
- [ ] Teachers can only see their classes
- [ ] Verify no sensitive data in URLs
- [ ] Check no data leaks in API responses

### File Security
- [ ] Uploaded files are validated
- [ ] File size limits enforced
- [ ] Malicious file upload rejected
- [ ] Files stored securely

---

## 11. REPORTING & ANALYTICS

### Teacher Reports
- [ ] Class performance overview
- [ ] Individual student progress
- [ ] Exam statistics
- [ ] Question difficulty analysis

### Admin Reports
- [ ] System usage statistics
- [ ] User activity logs
- [ ] Exam completion rates
- [ ] Performance trends

### Export Options
- [ ] Export to CSV works
- [ ] Export to PDF works
- [ ] Print functionality works
- [ ] Email reports (if implemented)

---

## 12. BROWSER COMPATIBILITY

### Browsers to Test
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

### Features to Verify per Browser
- [ ] PDF viewer works
- [ ] Audio playback works
- [ ] Timer displays correctly
- [ ] Forms submit properly
- [ ] No JavaScript errors in console

---

## 13. FINAL ACCEPTANCE CRITERIA

### Critical Must-Haves
- [ ] Both modules accessible and functional
- [ ] No data loss from existing PlacementTest
- [ ] Teachers can create and assign exams
- [ ] Students can take and submit exams
- [ ] Results are calculated correctly
- [ ] No security vulnerabilities
- [ ] System handles 30 teachers
- [ ] System handles 380 students

### Nice-to-Haves (If Time Permits)
- [ ] Email notifications work
- [ ] Advanced reporting features
- [ ] Bulk operations optimized
- [ ] Mobile app consideration
- [ ] API documentation complete

---

## TESTING NOTES

### Issues Found
1. _________________________________
2. _________________________________
3. _________________________________
4. _________________________________
5. _________________________________

### Recommendations
1. _________________________________
2. _________________________________
3. _________________________________

### Sign-off
- [ ] All critical tests passed
- [ ] System ready for production
- [ ] Documentation reviewed
- [ ] Backup procedures in place

**Tester Signature:** _______________  
**Date:** _______________  
**Approved By:** _______________

---

## QUICK TEST COMMANDS

```bash
# Start server
cd primepath_project
../venv/bin/python manage.py runserver --settings=primepath_project.settings_sqlite

# Run automated tests
../venv/bin/python test_all_modules_comprehensive.py

# Check database
../venv/bin/python manage.py dbshell --settings=primepath_project.settings_sqlite

# Create superuser
../venv/bin/python manage.py createsuperuser --settings=primepath_project.settings_sqlite

# Collect static files
../venv/bin/python manage.py collectstatic --settings=primepath_project.settings_sqlite
```

## TEST ACCOUNTS

### Admin
- Username: `admin`
- Password: `Admin123!`

### Test Teacher
- Username: `teacher1`
- Password: `Teacher123!`

### Test Student
- Username: `john.doe`
- Password: `Student123!`

## URLs TO TEST

- PlacementTest: http://127.0.0.1:8000/PlacementTest/
- RoutineTest: http://127.0.0.1:8000/RoutineTest/
- Admin Panel: http://127.0.0.1:8000/admin/
- API Placement: http://127.0.0.1:8000/api/PlacementTest/
- API Routine: http://127.0.0.1:8000/api/RoutineTest/

---

**Remember:** The goal is to ensure the system works reliably for ~30 teachers and ~380 students in a production environment. Focus on critical paths and user journeys first.