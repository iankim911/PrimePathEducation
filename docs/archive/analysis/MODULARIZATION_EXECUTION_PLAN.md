# 🎯 PrimePath Modularization - Step-by-Step Execution Plan

**Date**: August 7, 2025  
**Approach**: Incremental, Safe, Reversible  
**Principle**: Each step must work independently without breaking existing functionality  

---

## 📋 Pre-Execution Checklist

### Before Starting ANY Step:
```bash
# 1. Create a backup branch
git checkout -b backup-before-modularization-$(date +%Y%m%d)
git add -A && git commit -m "BACKUP: Before modularization step"

# 2. Tag current working state
git tag -a "working-state-$(date +%Y%m%d)" -m "Last known working state"

# 3. Test that everything works
python manage.py runserver
# Visit all main pages to confirm they work

# 4. Create work branch for the step
git checkout -b modularization-step-X
```

---

## 🚀 SPRINT 1: Backend Service Layer (Days 1-5)
*Goal: Create service layer WITHOUT touching views yet*

### Step 1.1: Create Service Infrastructure (Day 1)
**Risk Level: 🟢 Low** | **Rollback: Just delete new files**

#### Actions:
```bash
# Create service directories
mkdir -p placement_test/services/api
mkdir -p placement_test/services/business
mkdir -p placement_test/services/validators
mkdir -p core/services
```

#### Create Base Service Class:
```python
# placement_test/services/base.py
class BaseService:
    """Base service class with common functionality"""
    
    @classmethod
    def execute(cls, *args, **kwargs):
        """Main execution method"""
        try:
            return cls._perform(*args, **kwargs)
        except Exception as e:
            return cls._handle_error(e)
    
    @classmethod
    def _perform(cls, *args, **kwargs):
        """Override this in child classes"""
        raise NotImplementedError
    
    @classmethod
    def _handle_error(cls, error):
        """Common error handling"""
        import logging
        logging.error(f"Service error: {error}")
        raise
```

#### Test:
```bash
# Just run server - nothing should break
python manage.py runserver
```

#### Checkpoint:
```bash
git add -A && git commit -m "Step 1.1: Add service infrastructure"
```

---

### Step 1.2: Extract First Service Function (Day 1)
**Risk Level: 🟢 Low** | **Rollback: Comment out new code**

#### Target: Extract exam creation logic
```python
# placement_test/services/business/exam_creation_service.py
from ..base import BaseService
from placement_test.models import Exam, Question

class ExamCreationService(BaseService):
    @classmethod
    def _perform(cls, exam_data, created_by):
        """Create exam with all related data"""
        # Copy logic from views.py lines 241-323
        # But DON'T modify views.py yet
        exam = Exam.objects.create(
            name=exam_data['name'],
            curriculum_level_id=exam_data.get('curriculum_level'),
            pdf_file=exam_data['pdf_file'],
            timer_minutes=exam_data.get('timer_minutes', 60),
            total_questions=exam_data['total_questions'],
            created_by=created_by
        )
        return exam
```

#### Add Parallel Path in Views (Don't Remove Old Code):
```python
# placement_test/views.py - Around line 241
def create_exam(request):
    if request.method == 'POST':
        # ADD THIS - Feature flag to test new service
        use_new_service = request.GET.get('use_service') == 'true'
        
        if use_new_service:
            # New path - uses service
            from placement_test.services.business.exam_creation_service import ExamCreationService
            try:
                exam = ExamCreationService.execute(
                    exam_data=form.cleaned_data,
                    created_by=request.user
                )
                return redirect('placement_test:exam_detail', exam_id=exam.id)
            except Exception as e:
                # Fall back to old code
                pass
        
        # KEEP ALL EXISTING CODE UNCHANGED
        # ... existing 82 lines of code ...
```

#### Test:
```bash
# Test old path (should work)
curl http://127.0.0.1:8000/api/placement/exams/create/

# Test new path (should also work)
curl http://127.0.0.1:8000/api/placement/exams/create/?use_service=true
```

#### Checkpoint:
```bash
git add -A && git commit -m "Step 1.2: Add ExamCreationService with feature flag"
```

---

### Step 1.3: Extract Session Management Service (Day 2)
**Risk Level: 🟡 Medium** | **Rollback: Remove service calls**

#### Create Service:
```python
# placement_test/services/business/session_management_service.py
from ..base import BaseService
from placement_test.models import StudentSession, StudentAnswer

class SessionManagementService(BaseService):
    @classmethod
    def save_answer(cls, session_id, question_id, answer):
        """Save a student's answer"""
        # Extract from views.py submit_answer (lines 115-144)
        session = StudentSession.objects.get(id=session_id)
        
        if session.completed_at:
            raise ValueError("Session already completed")
        
        student_answer, created = StudentAnswer.objects.update_or_create(
            session=session,
            question_id=question_id,
            defaults={'answer': answer}
        )
        
        return {
            'success': True,
            'answer_id': student_answer.id,
            'created': created
        }
```

#### Add to Views with Safety Check:
```python
# placement_test/views.py - Line 115
def submit_answer(request, session_id):
    # ADD: Service toggle
    if settings.USE_SERVICE_LAYER:  # Add to settings
        from placement_test.services.business.session_management_service import SessionManagementService
        try:
            result = SessionManagementService.save_answer(
                session_id=session_id,
                question_id=request.POST.get('question_id'),
                answer=request.POST.get('answer')
            )
            return JsonResponse(result)
        except Exception as e:
            # Log and continue with old code
            import logging
            logging.warning(f"Service failed, using old code: {e}")
    
    # KEEP EXISTING CODE
    # ... existing code ...
```

#### Enable in Settings:
```python
# primepath_project/settings_sqlite.py
USE_SERVICE_LAYER = False  # Start with False, enable after testing
```

#### Test:
```bash
# With service disabled
python manage.py test placement_test.tests.test_session

# Enable service
# Change USE_SERVICE_LAYER = True
python manage.py test placement_test.tests.test_session
```

#### Checkpoint:
```bash
git add -A && git commit -m "Step 1.3: Add SessionManagementService with toggle"
```

---

## 🚀 SPRINT 2: View Decomposition (Days 6-10)
*Goal: Split massive views.py WITHOUT changing URLs*

### Step 2.1: Create View Structure (Day 6)
**Risk Level: 🟢 Low** | **Rollback: Just delete new files**

#### Create Directories:
```bash
mkdir -p placement_test/views
touch placement_test/views/__init__.py
```

#### Create View Files:
```python
# placement_test/views/__init__.py
"""
Gradual migration from views.py to modular views
"""
# Import everything from old views to maintain compatibility
from ..views import *

# placement_test/views/exam_views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from placement_test.models import Exam

class ExamListView:
    """Modular view for exam listing"""
    @staticmethod
    def as_view(request):
        # Move exam_list logic here (views.py lines 215-220)
        exams = Exam.objects.filter(is_active=True)
        return render(request, 'placement_test/exam_list.html', {
            'exams': exams
        })

# placement_test/views/session_views.py
class SessionListView:
    """Modular view for session listing"""
    @staticmethod
    def as_view(request):
        # Move session_list logic here (views.py lines 471-531)
        pass
```

#### Update URLs Gradually:
```python
# placement_test/urls.py
from django.urls import path
from . import views  # Keep old import
from .views import exam_views  # Add new import

urlpatterns = [
    # TESTING: Add new path alongside old
    path('exams/v2/', exam_views.ExamListView.as_view, name='exam_list_v2'),
    
    # KEEP ALL EXISTING PATHS UNCHANGED
    path('exams/', views.exam_list, name='exam_list'),
    # ... rest of URLs ...
]
```

#### Test:
```bash
# Old URL should work
curl http://127.0.0.1:8000/api/placement/exams/

# New URL should also work
curl http://127.0.0.1:8000/api/placement/exams/v2/
```

#### Checkpoint:
```bash
git add -A && git commit -m "Step 2.1: Create modular view structure"
```

---

### Step 2.2: Migrate First View Function (Day 7)
**Risk Level: 🟡 Medium** | **Rollback: Restore old import**

#### Move Complete Function:
```python
# placement_test/views/exam_views.py
def exam_list(request):
    """Fully migrated from views.py"""
    exams = Exam.objects.select_related('curriculum_level').filter(is_active=True)
    return render(request, 'placement_test/exam_list.html', {'exams': exams})

def exam_detail(request, exam_id):
    """Fully migrated from views.py"""
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all()
    audio_files = exam.audio_files.all()
    return render(request, 'placement_test/exam_detail.html', {
        'exam': exam,
        'questions': questions,
        'audio_files': audio_files
    })
```

#### Update Main Views File:
```python
# placement_test/views.py
# At the top, add:
from .views.exam_views import exam_list, exam_detail  # Re-import from new location

# DELETE the old exam_list and exam_detail functions (lines 215-336)
# But KEEP everything else
```

#### Test:
```bash
# All existing URLs should still work
python manage.py test placement_test.tests
```

#### Checkpoint:
```bash
git add -A && git commit -m "Step 2.2: Migrate exam_list and exam_detail to modular views"
```

---

## 🚀 SPRINT 3: Frontend Template Decomposition (Days 11-15)
*Goal: Break massive templates WITHOUT changing functionality*

### Step 3.1: Create Template Components (Day 11)
**Risk Level: 🟢 Low** | **Rollback: Just delete new files**

#### Create Component Structure:
```bash
mkdir -p templates/components/exam
mkdir -p templates/components/student
mkdir -p templates/components/common
```

#### Extract First Component:
```html
<!-- templates/components/common/timer.html -->
<div class="timer-component" data-seconds="{{ timer_seconds }}">
    <div class="timer-display">
        <span class="timer-label">Time Remaining:</span>
        <span id="timer" class="timer-value">--:--</span>
    </div>
</div>

<!-- templates/components/exam/pdf_viewer.html -->
<div class="pdf-viewer-component">
    <div id="pdf-container">
        <canvas id="pdf-canvas"></canvas>
    </div>
    <div class="pdf-controls">
        <button data-pdf-action="prev">Previous</button>
        <span id="page-num"></span> / <span id="page-count"></span>
        <button data-pdf-action="next">Next</button>
    </div>
</div>
```

#### Include in Main Template:
```html
<!-- templates/placement_test/student_test.html -->
<!-- Line 100 - Replace timer HTML with: -->
{% include 'components/common/timer.html' %}

<!-- Line 500 - Replace PDF viewer HTML with: -->
{% include 'components/exam/pdf_viewer.html' %}

<!-- KEEP ALL JavaScript as is for now -->
```

#### Test:
```bash
# Load student test page - timer and PDF should still work
curl http://127.0.0.1:8000/api/placement/session/[session-id]/
```

#### Checkpoint:
```bash
git add -A && git commit -m "Step 3.1: Extract timer and PDF viewer components"
```

---

### Step 3.2: Extract JavaScript to External Files (Day 12)
**Risk Level: 🟡 Medium** | **Rollback: Restore inline scripts**

#### Create JS Files:
```javascript
// static/js/pages/student-test.js
(function() {
    'use strict';
    
    // Move inline JavaScript from student_test.html here
    // But wrap in IIFE to avoid global pollution
    
    window.StudentTestController = {
        init: function(config) {
            this.config = config;
            this.setupTimer();
            this.setupPDF();
            this.setupQuestions();
        },
        
        setupTimer: function() {
            // Move timer code here (lines 1412-1426)
            let timeRemaining = this.config.timerSeconds;
            setInterval(() => {
                timeRemaining--;
                const minutes = Math.floor(timeRemaining / 60);
                const seconds = timeRemaining % 60;
                document.getElementById('timer').textContent = 
                    `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }, 1000);
        }
        // ... rest of functions ...
    };
})();
```

#### Update Template:
```html
<!-- templates/placement_test/student_test.html -->
<!-- Remove inline script (lines 1400-2250) -->
<!-- Add at bottom: -->
<script src="{% static 'js/pages/student-test.js' %}"></script>
<script>
    // Only pass configuration from Django
    StudentTestController.init({
        timerSeconds: {{ timer_seconds }},
        sessionId: '{{ session.id }}',
        examId: '{{ exam.id }}',
        pdfUrl: '{{ exam.pdf_file.url }}'
    });
</script>
```

#### Test:
```bash
# Clear browser cache
# Test all functionality still works
```

#### Checkpoint:
```bash
git add -A && git commit -m "Step 3.2: Extract JavaScript to external files"
```

---

## 🚀 SPRINT 4: API Standardization (Days 16-20)
*Goal: Create consistent API layer WITHOUT breaking existing calls*

### Step 4.1: Create API Base Classes (Day 16)
**Risk Level: 🟢 Low** | **Rollback: Just delete new files**

#### Create API Infrastructure:
```python
# placement_test/api/__init__.py
from django.http import JsonResponse
from django.views import View
import json

class BaseAPIView(View):
    """Base class for all API views"""
    
    def dispatch(self, request, *args, **kwargs):
        """Add JSON parsing and error handling"""
        try:
            if request.method in ['POST', 'PUT', 'PATCH']:
                if request.content_type == 'application/json':
                    request.json = json.loads(request.body)
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            return self.error_response(str(e))
    
    def success_response(self, data=None, message="Success"):
        return JsonResponse({
            'status': 'success',
            'message': message,
            'data': data
        })
    
    def error_response(self, message, status=400):
        return JsonResponse({
            'status': 'error',
            'message': message
        }, status=status)

# placement_test/api/exam_api.py
from .import BaseAPIView
from placement_test.models import Exam

class ExamAPIView(BaseAPIView):
    def get(self, request, exam_id=None):
        if exam_id:
            exam = Exam.objects.get(id=exam_id)
            return self.success_response({
                'id': str(exam.id),
                'name': exam.name,
                'total_questions': exam.total_questions
            })
        else:
            exams = Exam.objects.filter(is_active=True)
            return self.success_response([{
                'id': str(e.id),
                'name': e.name
            } for e in exams])
```

#### Add API URLs:
```python
# placement_test/urls.py
from .api import exam_api

urlpatterns = [
    # NEW API v2 endpoints (parallel to existing)
    path('api/v2/exams/', exam_api.ExamAPIView.as_view(), name='api_exam_list'),
    path('api/v2/exams/<uuid:exam_id>/', exam_api.ExamAPIView.as_view(), name='api_exam_detail'),
    
    # KEEP ALL EXISTING URLs
    # ... existing patterns ...
]
```

#### Test:
```bash
# Old endpoint
curl http://127.0.0.1:8000/api/placement/exams/

# New endpoint  
curl http://127.0.0.1:8000/api/placement/api/v2/exams/
```

#### Checkpoint:
```bash
git add -A && git commit -m "Step 4.1: Create standardized API base"
```

---

## 🚀 SPRINT 5: Database Optimization (Days 21-25)
*Goal: Optimize queries WITHOUT changing models*

### Step 5.1: Add Query Optimization (Day 21)
**Risk Level: 🟢 Low** | **Rollback: Remove optimizations**

#### Create Optimized Managers:
```python
# placement_test/managers.py
from django.db import models

class OptimizedExamManager(models.Manager):
    def get_queryset(self):
        """Add default optimizations"""
        return super().get_queryset().select_related(
            'curriculum_level',
            'created_by'
        ).prefetch_related(
            'questions',
            'audio_files'
        )
    
    def active(self):
        return self.get_queryset().filter(is_active=True)
    
    def for_level(self, level):
        return self.get_queryset().filter(curriculum_level=level)
```

#### Add to Model WITHOUT Breaking Changes:
```python
# placement_test/models.py
from .managers import OptimizedExamManager

class Exam(models.Model):
    # ... existing fields ...
    
    # ADD alongside default manager
    objects = models.Manager()  # Keep default
    optimized = OptimizedExamManager()  # Add optimized
```

#### Use in Views Gradually:
```python
# In views, change one at a time:
# OLD: exams = Exam.objects.filter(is_active=True)
# NEW: exams = Exam.optimized.active()
```

#### Test Query Performance:
```python
# manage.py shell
from django.db import connection
from placement_test.models import Exam

# Before
exams = Exam.objects.all()
len(connection.queries)  # Check query count

# After  
exams = Exam.optimized.all()
len(connection.queries)  # Should be fewer
```

#### Checkpoint:
```bash
git add -A && git commit -m "Step 5.1: Add optimized database managers"
```

---

## 📊 Progress Tracking Dashboard

### Create Progress Tracker:
```python
# management/commands/check_modularization.py
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    def handle(self, *args, **options):
        """Check modularization progress"""
        
        # Check service layer
        services = len(os.listdir('placement_test/services/business/'))
        self.stdout.write(f"Services created: {services}/20")
        
        # Check view decomposition
        old_views_lines = len(open('placement_test/views.py').readlines())
        self.stdout.write(f"Old views.py: {old_views_lines} lines (target: <1000)")
        
        # Check template components
        components = len(os.listdir('templates/components/'))
        self.stdout.write(f"Template components: {components}/50")
        
        # Check API endpoints
        api_files = len(os.listdir('placement_test/api/'))
        self.stdout.write(f"API modules: {api_files}/10")
        
        # Overall progress
        progress = (services*5 + (27000-old_views_lines)/270 + components*2 + api_files*10) / 4
        self.stdout.write(f"\nOVERALL PROGRESS: {progress:.1f}%")
```

Run after each sprint:
```bash
python manage.py check_modularization
```

---

## 🛟 Emergency Rollback Procedures

### If Something Breaks:

#### Level 1: Quick Fix (< 5 minutes)
```bash
# Revert last commit
git reset --hard HEAD~1

# Restart server
python manage.py runserver
```

#### Level 2: Feature Toggle (< 10 minutes)
```python
# settings.py
MODULARIZATION_FEATURES = {
    'use_services': False,
    'use_new_views': False,
    'use_components': False,
    'use_api_v2': False
}

# In code
if settings.MODULARIZATION_FEATURES.get('use_services'):
    # New code
else:
    # Old code
```

#### Level 3: Full Rollback (< 30 minutes)
```bash
# Go back to tagged working state
git checkout working-state-20250807

# Create hotfix branch
git checkout -b hotfix-rollback

# Deploy immediately
```

---

## 📅 Sprint Schedule

### Week 1 (Days 1-5): Backend Services
- ✅ Day 1: Service infrastructure + first service
- ⬜ Day 2: Session management service  
- ⬜ Day 3: Grading service
- ⬜ Day 4: Placement service
- ⬜ Day 5: Testing & validation

### Week 2 (Days 6-10): View Decomposition
- ⬜ Day 6: View structure setup
- ⬜ Day 7: Migrate exam views
- ⬜ Day 8: Migrate session views
- ⬜ Day 9: Migrate admin views
- ⬜ Day 10: Testing & cleanup

### Week 3 (Days 11-15): Frontend Templates
- ⬜ Day 11: Extract components
- ⬜ Day 12: Extract JavaScript
- ⬜ Day 13: Create page controllers
- ⬜ Day 14: Wire up modules
- ⬜ Day 15: Testing & optimization

### Week 4 (Days 16-20): API Layer
- ⬜ Day 16: API base classes
- ⬜ Day 17: Exam API
- ⬜ Day 18: Session API
- ⬜ Day 19: Analytics API
- ⬜ Day 20: Testing & documentation

### Week 5 (Days 21-25): Database & Testing
- ⬜ Day 21: Query optimization
- ⬜ Day 22: Add caching
- ⬜ Day 23: Write tests
- ⬜ Day 24: Performance testing
- ⬜ Day 25: Final validation

---

## ✅ Success Criteria per Sprint

### Sprint Success = All Tests Pass
```bash
# After each step
python manage.py test
python manage.py runserver
# Manual test critical paths:
# - Create exam
# - Take test
# - Submit answers
# - View results
```

### Sprint Completion Checklist:
- [ ] All existing features still work
- [ ] No increase in error logs
- [ ] Page load time same or better
- [ ] Can rollback in < 5 minutes
- [ ] Next sprint can build on this

---

## 🎯 Final Notes

1. **Never skip the checkpoint commits** - They're your safety net
2. **Test after EVERY step** - Don't accumulate problems
3. **Use feature flags liberally** - Better safe than sorry
4. **Keep old code until new code is proven** - Don't delete prematurely
5. **Document every deviation** - Future you will thank you

Remember: **Slow is smooth, smooth is fast**. Taking 25 days to do this right is better than breaking everything in 5 days.

---

**Document Version**: 1.0  
**Last Updated**: August 7, 2025  
**Next Review**: After Sprint 1 completion