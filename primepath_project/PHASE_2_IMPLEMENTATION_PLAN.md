# Phase 2 Implementation Plan: Step-by-Step Guide
## Monthly Review Tests & Quarterly Assessment Management

---

## Overview
This document provides a detailed, actionable implementation plan for Phase 2, breaking down the 10-week timeline into specific technical tasks and dependencies.

---

## Pre-Development Phase (Week 0)

### 1. Technical Preparation
- [ ] Set up development branch: `phase-2-student-portal`
- [ ] Create backup of current database
- [ ] Document current API endpoints
- [ ] Review existing models and identify extension points

### 2. OAuth Setup Requirements
- [ ] Register application with Google Developer Console
- [ ] Register application with Kakao Developers
- [ ] Obtain OAuth credentials (client ID, secret)
- [ ] Set up redirect URIs for local/production

### 3. Database Planning
```python
# New models needed:
- User (extend existing Teacher model)
- Class
- ClassEnrollment
- ClassTeacherAssignment
- TestAssignment
- StudentTestAttempt
- TestAnswer
- TestTimeTracking
```

---

## Phase 2A: Authentication & Users (Weeks 1-2)

### Week 1: User Model & Authentication Backend

#### Day 1-2: Extend User Model
```python
# Step 1: Modify core/models.py
class User(AbstractUser):
    USER_ROLES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=USER_ROLES)
    oauth_provider = models.CharField(max_length=20, null=True)
    oauth_id = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    language_preference = models.CharField(max_length=2, default='ko')
    consent_accepted = models.DateTimeField(null=True)
    created_by = models.ForeignKey('self', null=True, on_delete=SET_NULL)
```

#### Day 3-4: OAuth Integration
```bash
# Step 2: Install OAuth packages
pip install django-allauth
pip install python-social-auth
```

```python
# Step 3: Configure settings.py
INSTALLED_APPS += [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.kakao',
]

# Step 4: Create OAuth views
# core/views/auth.py
- GoogleLoginView
- KakaoLoginView
- RegistrationView with consent
```

#### Day 5: Password Recovery
```python
# Step 5: Implement recovery options
- Email recovery flow
- Phone number recovery (SMS integration)
- Social account recovery links
```

### Week 2: Registration & Role Management

#### Day 1-2: Registration Flows
```python
# Step 6: Create registration templates
templates/auth/
├── student_register.html (with parent consent option)
├── login.html (Google/Kakao/Email options)
├── consent_form.html
└── recovery.html

# Step 7: Username generation logic
def generate_username(first_name, last_name):
    base = f"{first_name.lower()}.{last_name.lower()}"
    # Add number if duplicate
```

#### Day 3-4: Role-Based Access Control
```python
# Step 8: Create permission decorators
@student_required
@teacher_required
@admin_required

# Step 9: Middleware for role checking
class RoleBasedAccessMiddleware:
    def process_request(self, request):
        # Check user role and redirect accordingly
```

#### Day 5: Testing & Validation
- [ ] Test Google OAuth flow
- [ ] Test Kakao OAuth flow
- [ ] Test email registration
- [ ] Verify role permissions
- [ ] Test account recovery

---

## Phase 2B: Class Management (Weeks 3-4)

### Week 3: Class Models & Admin Interface

#### Day 1-2: Create Class Models
```python
# Step 10: Create class models
class Class(models.Model):
    name = models.CharField(max_length=100)
    academic_year = models.IntegerField()
    quarter = models.CharField(max_length=2)  # Q1, Q2, Q3, Q4
    max_students = models.IntegerField(default=20)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ClassEnrollment(models.Model):
    class_obj = models.ForeignKey(Class)
    student = models.ForeignKey(User)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    curriculum_level = models.ForeignKey(CurriculumLevel, null=True)

class ClassTeacherAssignment(models.Model):
    class_obj = models.ForeignKey(Class)
    teacher = models.ForeignKey(User)
    assigned_at = models.DateTimeField(auto_now_add=True)
```

#### Day 3-4: Admin Class Management Interface
```python
# Step 11: Create admin views
templates/admin/
├── class_create.html
├── class_list.html
├── teacher_assignment.html
└── quarterly_reset.html

# Admin can:
- Create classes
- Assign multiple teachers
- View all classes
```

#### Day 5: Teacher Assignment Logic
```python
# Step 12: Teacher assignment functionality
def assign_teacher_to_class(class_id, teacher_id):
    # Allow multiple teachers per class
    # Handle reassignments
```

### Week 4: Student Enrollment & Teacher Tools

#### Day 1-2: Student Enrollment System
```python
# Step 13: Student enrollment views
def student_self_enrollment(request):
    # Student provides ID to teacher
    # Teacher adds to class
    
# Step 14: Bulk enrollment
def bulk_enroll_students(class_id, student_ids):
    # Add multiple students at once
```

#### Day 3-4: Teacher Class Management
```python
# Step 15: Teacher dashboard
templates/teacher/
├── my_classes.html
├── student_roster.html
├── add_students.html
└── cross_class_view.html

# Teacher can:
- View assigned classes
- Add/remove students
- See all students across classes
```

#### Day 5: Testing
- [ ] Test class creation
- [ ] Test teacher assignment
- [ ] Test student enrollment
- [ ] Test quarterly transitions

---

## Phase 2C: Enhanced Exam Management (Weeks 5-6)

### Week 5: Exam Categories & Upload

#### Day 1-2: Extend Exam Model
```python
# Step 16: Add exam categories
class Exam(models.Model):
    EXAM_TYPES = (
        ('review', 'Monthly Review'),
        ('quarterly', 'Quarterly Exam'),
        ('placement', 'Placement Test'),
    )
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    year = models.IntegerField()
    quarter = models.CharField(max_length=2)
    sequence_number = models.IntegerField()  # 1, 2, 3 for reviews
    
    class Meta:
        unique_together = ['curriculum_level', 'year', 'quarter', 'exam_type', 'sequence_number']
```

#### Day 3-4: Enhanced Upload Interface
```python
# Step 17: Modify upload interface
templates/exam/
├── upload_review.html
├── upload_quarterly.html
└── exam_matrix.html  # Shows all exams by level/quarter

# Implement naming convention validation
def validate_exam_name(name):
    # REVIEW-CORE-Phonics-L1-2025-Q1-01
    pattern = r'^(REVIEW|QUARTERLY)-\w+-\w+-L\d+-\d{4}-Q[1-4]-\w+$'
```

#### Day 5: Version Control
```python
# Step 18: Exam versioning
class ExamVersion(models.Model):
    exam = models.ForeignKey(Exam)
    version_number = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField()
```

### Week 6: Test Assignment System

#### Day 1-2: Assignment Models
```python
# Step 19: Test assignment models
class TestAssignment(models.Model):
    exam = models.ForeignKey(Exam)
    assigned_to_class = models.ForeignKey(Class, null=True)
    assigned_to_student = models.ForeignKey(User, null=True)
    assigned_by = models.ForeignKey(User, related_name='assigned_by')
    deadline = models.DateTimeField()
    allow_early_submit = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Day 3-4: Assignment Interface
```python
# Step 20: Assignment views
templates/teacher/test_assignment/
├── assign_to_class.html
├── assign_to_students.html
├── set_deadline.html
└── differentiation.html

def assign_test_to_class(request, class_id):
    # Bulk assignment
    
def assign_different_tests(request, class_id):
    # Individual student assignments
```

#### Day 5: Testing
- [ ] Test exam upload
- [ ] Test assignment to class
- [ ] Test differentiated assignment
- [ ] Test deadline enforcement

---

## Phase 2D: Student Experience (Weeks 7-8)

### Week 7: Student Dashboard & Test Interface

#### Day 1-2: Student Dashboard
```python
# Step 21: Student dashboard
templates/student/
├── dashboard.html
├── my_classes.html
├── assigned_tests.html
└── test_history.html

def student_dashboard(request):
    # Show classes, upcoming tests, scores
    assignments = TestAssignment.objects.filter(
        Q(assigned_to_student=request.user) |
        Q(assigned_to_class__students=request.user)
    )
```

#### Day 3-4: Test-Taking Interface
```python
# Step 22: Enhance test interface
templates/student/test/
├── test_start.html
├── test_questions.html (with anti-cheating)
├── test_review.html
└── test_results.html

# Step 23: Anti-cheating JavaScript
static/js/anti_cheat.js:
- Disable right-click
- Prevent copy/paste
- Detect tab switching
- Full-screen enforcement
```

#### Day 5: Auto-Save Implementation
```javascript
// Step 24: Local storage auto-save
function autoSaveAnswers() {
    const answers = collectAnswers();
    localStorage.setItem('test_answers_' + testId, JSON.stringify(answers));
    // Sync to server every minute
    syncToServer(answers);
}
setInterval(autoSaveAnswers, 60000);
```

### Week 8: Scoring & Performance Tracking

#### Day 1-2: Test Attempt Tracking
```python
# Step 25: Attempt models
class StudentTestAttempt(models.Model):
    student = models.ForeignKey(User)
    test_assignment = models.ForeignKey(TestAssignment)
    attempt_number = models.IntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    time_spent = models.IntegerField()  # seconds
    
class TestAnswer(models.Model):
    attempt = models.ForeignKey(StudentTestAttempt)
    question = models.ForeignKey(Question)
    answer = models.TextField()
    is_correct = models.BooleanField()
    time_spent = models.IntegerField()  # seconds per question
```

#### Day 3-4: Score Calculation
```python
# Step 26: Scoring logic
def calculate_score(attempt):
    # Calculate percentage
    # Track best score
    # Calculate average
    
def get_student_metrics(student, exam):
    attempts = StudentTestAttempt.objects.filter(student=student, exam=exam)
    return {
        'best_score': attempts.aggregate(Max('score')),
        'average_score': attempts.aggregate(Avg('score')),
        'attempt_count': attempts.count()
    }
```

#### Day 5: Testing
- [ ] Test student dashboard
- [ ] Test anti-cheating measures
- [ ] Test auto-save
- [ ] Test score calculation
- [ ] Test multiple attempts

---

## Phase 2E: Teacher Tools & Analytics (Weeks 9-10)

### Week 9: Reports & Analytics

#### Day 1-2: Report Models
```python
# Step 27: Analytics queries
def get_class_performance(class_id):
    return {
        'average_score': ...,
        'completion_rate': ...,
        'top_performers': ...,
        'struggling_students': ...
    }

def get_student_progress(student_id):
    return {
        'tests_taken': ...,
        'average_score': ...,
        'improvement_trend': ...,
        'time_patterns': ...
    }
```

#### Day 3-4: Export Functionality
```python
# Step 28: Export views
import csv
import xlsxwriter
from reportlab.pdfgen import canvas

def export_class_data(request, class_id, format='csv'):
    if format == 'csv':
        return export_csv(data)
    elif format == 'excel':
        return export_excel(data)
    elif format == 'pdf':
        return export_pdf(data)
```

#### Day 5: Report Templates
```python
# Step 29: Report interfaces
templates/reports/
├── class_performance.html
├── student_progress.html
├── export_options.html
└── charts.html  # Using Chart.js
```

### Week 10: Integration Testing & Polish

#### Day 1-2: End-to-End Testing
```python
# Step 30: Integration tests
class Phase2IntegrationTest(TestCase):
    def test_student_registration_flow(self):
        # Register → Get ID → Teacher assigns → Take test
    
    def test_teacher_workflow(self):
        # Create class → Add students → Assign test → View results
    
    def test_admin_quarterly_reset(self):
        # End quarter → Create new classes → Reassign
```

#### Day 3: Performance Testing
```bash
# Step 31: Load testing
# Use locust or Apache JMeter
- Test 400 concurrent users
- Test auto-save under load
- Test export with large datasets
```

#### Day 4: UI Polish
- [ ] Bilingual toggle implementation
- [ ] Mobile/tablet responsiveness
- [ ] Error message improvements
- [ ] Loading states

#### Day 5: Documentation
```markdown
# Step 32: Create documentation
docs/
├── teacher_guide.md
├── student_guide.md
├── admin_guide.md
└── api_documentation.md
```

---

## Database Migration Strategy

### Step-by-step Migration
```bash
# 1. Create migrations for new models
python manage.py makemigrations

# 2. Review migrations
python manage.py sqlmigrate core 0001

# 3. Apply migrations to test database first
python manage.py migrate --database=test

# 4. Backup production database
python manage.py dumpdata > backup.json

# 5. Apply to production
python manage.py migrate
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] OAuth credentials configured
- [ ] Database migrations tested
- [ ] Performance benchmarks met
- [ ] Security review completed

### Deployment Steps
1. Deploy authentication system
2. Enable registration for small test group
3. Create initial classes
4. Test with pilot teachers
5. Gradual rollout to all users

### Post-Deployment
- [ ] Monitor error logs
- [ ] Track registration success rate
- [ ] Gather teacher feedback
- [ ] Performance monitoring
- [ ] Quick fixes as needed

---

## Risk Mitigation Strategies

### Technical Risks
1. **OAuth Provider Issues**
   - Keep email/password as fallback
   - Cache OAuth tokens appropriately

2. **Database Performance**
   - Index foreign keys
   - Optimize queries
   - Consider read replicas

3. **Concurrent Test Load**
   - Implement queueing
   - Use caching strategically
   - Consider CDN for PDFs

### User Adoption Risks
1. **Young Student Confusion**
   - Simple registration flow
   - Clear instructions
   - Teacher assistance

2. **Teacher Training**
   - Create video tutorials
   - Hands-on training sessions
   - Quick reference guides

---

## Success Metrics Tracking

### Week-by-Week Metrics
- Week 1-2: OAuth setup complete, test logins working
- Week 3-4: Classes created, teachers assigned
- Week 5-6: Exams uploaded, assignments working
- Week 7-8: Students taking tests, scores calculating
- Week 9-10: Reports generating, exports working

### Key Performance Indicators
- Registration completion rate > 80%
- Test submission success rate > 95%
- Average page load time < 3 seconds
- Zero data loss incidents
- Teacher satisfaction score > 4/5

---

## Next Steps

1. **Immediate Actions:**
   - Set up OAuth applications (Google, Kakao)
   - Create development branch
   - Begin Week 1 tasks

2. **Preparation:**
   - Gather test PDFs for each curriculum level
   - Prepare teacher training materials
   - Set up staging environment

3. **Communication:**
   - Inform teachers about upcoming changes
   - Prepare student registration instructions
   - Schedule training sessions

---

**Document Status:** Ready for Implementation  
**Timeline:** 10 weeks from start date  
**Dependencies:** OAuth credentials, test content ready  
**First Sprint Starts:** [Insert Date]