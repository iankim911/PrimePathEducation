# 📇 Daily Execution Cards - Modularization Sprint

**Start Date**: ____________  
**Developer**: ____________  
**Instructions**: Print this document. Check off each item as completed. Stop if any test fails.

---

## 📅 DAY 1: Service Infrastructure Setup

### ⏰ Morning (2 hours)
#### Card 1.1: Safety Setup
- [ ] Create backup: `git checkout -b backup-$(date +%Y%m%d-%H%M)`
- [ ] Commit current state: `git add -A && git commit -m "BACKUP: Day 1 start"`
- [ ] Tag working state: `git tag working-day1-start`
- [ ] Test server starts: `python manage.py runserver`
- [ ] Test can create exam in browser
- [ ] Test can take test in browser
- [ ] Create work branch: `git checkout -b day1-service-infrastructure`

**STOP CHECK**: Did all tests pass? ✅ Continue | ❌ Restore and investigate

#### Card 1.2: Create Service Directories
```bash
# Run these commands:
mkdir -p placement_test/services/api
mkdir -p placement_test/services/business  
mkdir -p placement_test/services/validators
mkdir -p core/services
touch placement_test/services/__init__.py
touch placement_test/services/api/__init__.py
touch placement_test/services/business/__init__.py
touch placement_test/services/validators/__init__.py
touch core/services/__init__.py
```
- [ ] All directories created
- [ ] All __init__.py files created
- [ ] Run: `python manage.py runserver` (should still work)

**Checkpoint**: `git add -A && git commit -m "Day 1.2: Create service directories"`

### ☀️ Afternoon (3 hours)
#### Card 1.3: Create Base Service Class
Create file: `placement_test/services/base.py`
```python
import logging
from typing import Any, Dict, Optional
from django.db import transaction

logger = logging.getLogger(__name__)

class BaseService:
    """Base service class with common functionality"""
    
    @classmethod
    def execute(cls, *args, **kwargs):
        """Main execution method with error handling"""
        logger.info(f"Executing {cls.__name__}")
        try:
            with transaction.atomic():
                result = cls._perform(*args, **kwargs)
                cls._after_perform(result)
                return result
        except Exception as e:
            logger.error(f"{cls.__name__} failed: {str(e)}")
            return cls._handle_error(e)
    
    @classmethod
    def _perform(cls, *args, **kwargs):
        """Override this in child classes"""
        raise NotImplementedError(f"{cls.__name__} must implement _perform")
    
    @classmethod
    def _after_perform(cls, result):
        """Hook for post-processing"""
        pass
    
    @classmethod
    def _handle_error(cls, error):
        """Common error handling"""
        raise error
    
    @classmethod
    def _validate(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Override for validation"""
        return data
```
- [ ] File created
- [ ] No syntax errors: `python -m py_compile placement_test/services/base.py`
- [ ] Server still runs: `python manage.py runserver`

**Checkpoint**: `git add -A && git commit -m "Day 1.3: Create BaseService class"`

#### Card 1.4: Create First Service
Create file: `placement_test/services/business/exam_service_v2.py`
```python
from ..base import BaseService
from placement_test.models import Exam, Question
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ExamCreationServiceV2(BaseService):
    """Service for creating exams - parallel to existing code"""
    
    @classmethod
    def _validate(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate exam data"""
        required = ['name', 'pdf_file', 'total_questions']
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if data['total_questions'] < 1:
            raise ValueError("Total questions must be at least 1")
        
        return data
    
    @classmethod
    def _perform(cls, exam_data: Dict[str, Any], created_by=None):
        """Create exam with all related data"""
        # Validate
        exam_data = cls._validate(exam_data)
        
        # Create exam
        exam = Exam.objects.create(
            name=exam_data['name'],
            curriculum_level_id=exam_data.get('curriculum_level'),
            pdf_file=exam_data['pdf_file'],
            timer_minutes=exam_data.get('timer_minutes', 60),
            total_questions=exam_data['total_questions'],
            default_options_count=exam_data.get('default_options_count', 5),
            created_by=created_by,
            is_active=True
        )
        
        logger.info(f"Created exam: {exam.id}")
        
        # Create placeholder questions
        cls._create_placeholder_questions(exam)
        
        return exam
    
    @classmethod
    def _create_placeholder_questions(cls, exam):
        """Create placeholder questions for the exam"""
        questions = []
        for i in range(1, exam.total_questions + 1):
            questions.append(Question(
                exam=exam,
                question_number=i,
                question_type='MCQ',
                correct_answer='',
                points=1,
                options_count=exam.default_options_count
            ))
        
        Question.objects.bulk_create(questions)
        logger.info(f"Created {len(questions)} placeholder questions")
```
- [ ] File created
- [ ] No syntax errors: `python -m py_compile placement_test/services/business/exam_service_v2.py`
- [ ] Server still runs

**Checkpoint**: `git add -A && git commit -m "Day 1.4: Create ExamCreationServiceV2"`

### 🌙 Evening (1 hour)
#### Card 1.5: Add Service Toggle
Edit: `primepath_project/settings_sqlite.py` (add at bottom)
```python
# Modularization Feature Flags
MODULARIZATION_FEATURES = {
    'use_exam_service': False,  # Set to True to test new service
    'use_session_service': False,
    'use_new_views': False,
    'use_api_v2': False,
}

# Service Layer Settings
USE_SERVICE_LAYER = False  # Master switch
SERVICE_LOG_LEVEL = 'INFO'
```
- [ ] Settings added
- [ ] Server restarts successfully

Edit: `placement_test/views.py` (around line 241 in create_exam function)
```python
def create_exam(request):
    if request.method == 'POST':
        # ... existing form validation ...
        
        # ADD THIS BLOCK - Feature flag for new service
        use_service = getattr(settings, 'MODULARIZATION_FEATURES', {}).get('use_exam_service', False)
        if use_service or request.GET.get('use_service') == 'true':
            from placement_test.services.business.exam_service_v2 import ExamCreationServiceV2
            try:
                logger.info("Using new ExamCreationServiceV2")
                exam = ExamCreationServiceV2.execute(
                    exam_data=form.cleaned_data,
                    created_by=request.user if request.user.is_authenticated else None
                )
                messages.success(request, 'Exam created successfully using new service!')
                return redirect('placement_test:exam_detail', exam_id=exam.id)
            except Exception as e:
                logger.error(f"Service failed, falling back: {e}")
                # Fall through to existing code
        
        # KEEP ALL EXISTING CODE BELOW THIS
        # ... existing exam creation code ...
```
- [ ] Code added (DO NOT remove existing code)
- [ ] Test old path: Create exam normally (should work)
- [ ] Test new path: Create exam with `?use_service=true` in URL (should work)

**Checkpoint**: `git add -A && git commit -m "Day 1.5: Add service feature toggle"`

### 📊 Day 1 Completion Checklist
- [ ] Both paths (old and new) can create exams
- [ ] No errors in console
- [ ] All tests pass: `python manage.py test placement_test.tests`
- [ ] Final commit: `git add -A && git commit -m "Day 1 COMPLETE: Service infrastructure ready"`
- [ ] Create Day 1 completion tag: `git tag day1-complete`

**Day 1 Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

---

## 📅 DAY 2: Session Service Implementation

### ⏰ Morning (2 hours)
#### Card 2.1: Morning Setup
- [ ] Checkout yesterday's work: `git checkout day1-complete`
- [ ] Create today's branch: `git checkout -b day2-session-service`
- [ ] Verify server works: `python manage.py runserver`
- [ ] Test exam creation still works (both paths)
- [ ] Create backup tag: `git tag day2-start`

#### Card 2.2: Create Session Service
Create file: `placement_test/services/business/session_service_v2.py`
```python
from ..base import BaseService
from placement_test.models import StudentSession, StudentAnswer, Question
from django.utils import timezone
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SessionServiceV2(BaseService):
    """Service for managing test sessions"""
    
    @classmethod
    def _perform(cls, action: str, **kwargs):
        """Route to appropriate action"""
        actions = {
            'save_answer': cls._save_answer,
            'complete_session': cls._complete_session,
            'get_progress': cls._get_progress,
        }
        
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        
        return actions[action](**kwargs)
    
    @classmethod
    def _save_answer(cls, session_id: str, question_id: int, answer: str) -> Dict:
        """Save a student's answer"""
        try:
            session = StudentSession.objects.get(id=session_id)
            
            # Check if session is still active
            if session.completed_at:
                raise ValueError("Session already completed")
            
            # Get or create answer
            student_answer, created = StudentAnswer.objects.update_or_create(
                session=session,
                question_id=question_id,
                defaults={
                    'answer': answer,
                    'answered_at': timezone.now()
                }
            )
            
            logger.info(f"Answer saved for session {session_id}, question {question_id}")
            
            return {
                'success': True,
                'created': created,
                'answer_id': student_answer.id,
                'message': 'Answer saved successfully'
            }
            
        except StudentSession.DoesNotExist:
            raise ValueError(f"Session {session_id} not found")
        except Exception as e:
            logger.error(f"Failed to save answer: {e}")
            raise
    
    @classmethod
    def _complete_session(cls, session_id: str) -> Dict:
        """Complete a test session"""
        try:
            session = StudentSession.objects.get(id=session_id)
            
            if session.completed_at:
                return {
                    'success': False,
                    'message': 'Session already completed'
                }
            
            # Mark as completed
            session.completed_at = timezone.now()
            session.time_spent_seconds = int(
                (session.completed_at - session.started_at).total_seconds()
            )
            
            # Calculate score
            from placement_test.services.grading_service import GradingService
            score_data = GradingService.calculate_session_score(session)
            session.score = score_data['score']
            session.percentage_score = score_data['percentage']
            
            session.save()
            
            logger.info(f"Session {session_id} completed with score {session.score}")
            
            return {
                'success': True,
                'score': session.score,
                'percentage': float(session.percentage_score),
                'redirect_url': f'/api/placement/session/{session_id}/result/'
            }
            
        except StudentSession.DoesNotExist:
            raise ValueError(f"Session {session_id} not found")
    
    @classmethod  
    def _get_progress(cls, session_id: str) -> Dict:
        """Get session progress"""
        session = StudentSession.objects.get(id=session_id)
        total = session.exam.total_questions
        answered = session.answers.exclude(answer='').count()
        
        return {
            'total_questions': total,
            'answered': answered,
            'remaining': total - answered,
            'percentage': round((answered / total) * 100, 1)
        }
```
- [ ] File created
- [ ] No syntax errors
- [ ] Server still runs

**Checkpoint**: `git add -A && git commit -m "Day 2.2: Create SessionServiceV2"`

### ☀️ Afternoon (3 hours)
#### Card 2.3: Integrate Session Service
Edit: `placement_test/views.py` (around line 115 - submit_answer function)
```python
def submit_answer(request, session_id):
    """Submit answer for a question"""
    if request.method == 'POST':
        # ADD: Service toggle
        use_service = getattr(settings, 'MODULARIZATION_FEATURES', {}).get('use_session_service', False)
        if use_service or request.GET.get('use_service') == 'true':
            from placement_test.services.business.session_service_v2 import SessionServiceV2
            try:
                result = SessionServiceV2.execute(
                    action='save_answer',
                    session_id=session_id,
                    question_id=request.POST.get('question_id'),
                    answer=request.POST.get('answer', '')
                )
                return JsonResponse(result)
            except Exception as e:
                logger.error(f"SessionServiceV2 failed: {e}")
                # Fall through to existing code
        
        # KEEP EXISTING CODE
        # ... existing submit_answer code ...
```

Edit: `placement_test/views.py` (around line 186 - complete_test function)
```python
def complete_test(request, session_id):
    """Complete test and calculate results"""
    if request.method == 'POST':
        # ADD: Service toggle
        use_service = getattr(settings, 'MODULARIZATION_FEATURES', {}).get('use_session_service', False)
        if use_service or request.GET.get('use_service') == 'true':
            from placement_test.services.business.session_service_v2 import SessionServiceV2
            try:
                result = SessionServiceV2.execute(
                    action='complete_session',
                    session_id=session_id
                )
                return JsonResponse(result)
            except Exception as e:
                logger.error(f"SessionServiceV2 failed: {e}")
                # Fall through to existing code
        
        # KEEP EXISTING CODE
        # ... existing complete_test code ...
```
- [ ] Code added to both functions
- [ ] Test answer submission (old path)
- [ ] Test answer submission with `?use_service=true`
- [ ] Test session completion (both paths)

**Checkpoint**: `git add -A && git commit -m "Day 2.3: Integrate SessionServiceV2"`

### 🌙 Evening (1 hour)
#### Card 2.4: Testing & Validation
Create test file: `placement_test/tests/test_services.py`
```python
from django.test import TestCase
from placement_test.services.business.exam_service_v2 import ExamCreationServiceV2
from placement_test.services.business.session_service_v2 import SessionServiceV2
from placement_test.models import Exam, StudentSession
from django.core.files.uploadedfile import SimpleUploadedFile

class ServiceTests(TestCase):
    def test_exam_creation_service(self):
        """Test exam creation through service"""
        pdf_file = SimpleUploadedFile("test.pdf", b"PDF content", content_type="application/pdf")
        
        exam_data = {
            'name': 'Test Exam',
            'pdf_file': pdf_file,
            'total_questions': 10,
            'timer_minutes': 60
        }
        
        exam = ExamCreationServiceV2.execute(exam_data=exam_data)
        
        self.assertIsNotNone(exam)
        self.assertEqual(exam.name, 'Test Exam')
        self.assertEqual(exam.questions.count(), 10)
    
    def test_session_service_save_answer(self):
        """Test saving answer through service"""
        # Setup test data
        exam = self._create_test_exam()
        session = self._create_test_session(exam)
        question = exam.questions.first()
        
        # Save answer
        result = SessionServiceV2.execute(
            action='save_answer',
            session_id=session.id,
            question_id=question.id,
            answer='A'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(session.answers.filter(answer='A').count(), 1)
    
    def _create_test_exam(self):
        pdf_file = SimpleUploadedFile("test.pdf", b"PDF", content_type="application/pdf")
        return ExamCreationServiceV2.execute(exam_data={
            'name': 'Test',
            'pdf_file': pdf_file,
            'total_questions': 5
        })
    
    def _create_test_session(self, exam):
        return StudentSession.objects.create(
            student_name='Test Student',
            grade=10,
            academic_rank='TOP_10',
            exam=exam
        )
```
- [ ] Test file created
- [ ] Run tests: `python manage.py test placement_test.tests.test_services`
- [ ] All tests pass

**Checkpoint**: `git add -A && git commit -m "Day 2.4: Add service tests"`

### 📊 Day 2 Completion Checklist
- [ ] Session service works for saving answers
- [ ] Session service works for completing tests
- [ ] Both old and new paths work
- [ ] All tests pass
- [ ] Final commit: `git add -A && git commit -m "Day 2 COMPLETE: Session service implemented"`
- [ ] Create completion tag: `git tag day2-complete`

**Day 2 Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

---

## 📅 DAY 3: View Decomposition Start

### ⏰ Morning (2 hours)
#### Card 3.1: Setup View Structure
- [ ] Checkout: `git checkout day2-complete`
- [ ] New branch: `git checkout -b day3-view-decomposition`
- [ ] Create directories:
```bash
mkdir -p placement_test/views
touch placement_test/views/__init__.py
touch placement_test/views/exam_views.py
touch placement_test/views/session_views.py
touch placement_test/views/api_views.py
```

#### Card 3.2: Create First Modular View
Create: `placement_test/views/exam_views.py`
```python
"""
Modular views for exam management
Gradually migrating from monolithic views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from placement_test.models import Exam, Question, AudioFile
from placement_test.forms import ExamForm
import logging

logger = logging.getLogger(__name__)

def exam_list_v2(request):
    """List all active exams - modular version"""
    exams = Exam.objects.select_related('curriculum_level').filter(is_active=True)
    
    # Add search
    search = request.GET.get('search')
    if search:
        exams = exams.filter(name__icontains=search)
    
    # Add sorting
    sort = request.GET.get('sort', '-created_at')
    exams = exams.order_by(sort)
    
    context = {
        'exams': exams,
        'search': search,
        'sort': sort
    }
    
    return render(request, 'placement_test/exam_list.html', context)

def exam_detail_v2(request, exam_id):
    """Show exam details - modular version"""
    exam = get_object_or_404(
        Exam.objects.select_related('curriculum_level', 'created_by')
                    .prefetch_related('questions', 'audio_files'),
        id=exam_id
    )
    
    context = {
        'exam': exam,
        'questions': exam.questions.all(),
        'audio_files': exam.audio_files.all(),
        'stats': {
            'total_questions': exam.total_questions,
            'total_audio': exam.audio_files.count(),
            'total_sessions': exam.sessions.count(),
            'completed_sessions': exam.sessions.filter(completed_at__isnull=False).count()
        }
    }
    
    return render(request, 'placement_test/exam_detail.html', context)
```
- [ ] File created
- [ ] No syntax errors

**Checkpoint**: `git add -A && git commit -m "Day 3.2: Create modular exam views"`

### ☀️ Afternoon (3 hours)
#### Card 3.3: Wire Up Parallel Routes
Edit: `placement_test/urls.py`
```python
from django.urls import path
from . import views  # Keep old import
from .views import exam_views  # Add new import

app_name = 'placement_test'

urlpatterns = [
    # NEW MODULAR ROUTES (v2) - Add these FIRST
    path('v2/exams/', exam_views.exam_list_v2, name='exam_list_v2'),
    path('v2/exams/<uuid:exam_id>/', exam_views.exam_detail_v2, name='exam_detail_v2'),
    
    # EXISTING ROUTES - Keep all of these
    path('start/', views.start_test, name='start_test'),
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/<uuid:exam_id>/', views.exam_detail, name='exam_detail'),
    # ... rest of existing patterns ...
]
```
- [ ] Routes added
- [ ] Test old route: `/api/placement/exams/`
- [ ] Test new route: `/api/placement/v2/exams/`
- [ ] Both should work

**Checkpoint**: `git add -A && git commit -m "Day 3.3: Add parallel v2 routes"`

### 🌙 Evening (1 hour)  
#### Card 3.4: Gradual Migration
Edit: `placement_test/views/__init__.py`
```python
"""
Gradual migration controller
This file manages the transition from monolithic to modular views
"""
from django.conf import settings

# Import from monolithic views.py for backward compatibility
from ..views import *

# Import new modular views
from .exam_views import exam_list_v2, exam_detail_v2

# Override old functions if feature flag is set
if getattr(settings, 'MODULARIZATION_FEATURES', {}).get('use_new_views', False):
    # Replace old with new
    exam_list = exam_list_v2
    exam_detail = exam_detail_v2
    # Log the replacement
    import logging
    logging.info("Using modular views for exams")
```
- [ ] Migration controller created
- [ ] Test with flag off (uses old views)
- [ ] Test with flag on (uses new views)

**Checkpoint**: `git add -A && git commit -m "Day 3.4: Add migration controller"`

### 📊 Day 3 Completion Checklist
- [ ] Modular view structure created
- [ ] Parallel routes working
- [ ] Can toggle between old and new views
- [ ] No functionality broken
- [ ] Final commit: `git commit -m "Day 3 COMPLETE: View decomposition started"`
- [ ] Tag: `git tag day3-complete`

**Day 3 Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete | ❌ Failed

---

## 🔄 Quick Recovery Procedures

### If Build Fails
```bash
# Quick revert
git reset --hard HEAD~1
python manage.py runserver  # Test immediately
```

### If Feature Breaks
```python
# In settings_sqlite.py, disable feature
MODULARIZATION_FEATURES = {
    'use_exam_service': False,  # Turn off
    'use_session_service': False,  # Turn off  
    'use_new_views': False,  # Turn off
}
```

### If Completely Stuck
```bash
# Go back to last known good
git checkout day[N]-complete  # Where N is last working day
git checkout -b recovery
# Continue from there
```

---

## 📈 Progress Tracking

### Daily Status Board
| Day | Sprint | Status | Tests Pass | Rollback Tested | Notes |
|-----|--------|--------|------------|-----------------|-------|
| 1 | Service Infrastructure | ⬜ | ⬜ | ⬜ | |
| 2 | Session Service | ⬜ | ⬜ | ⬜ | |
| 3 | View Decomposition | ⬜ | ⬜ | ⬜ | |
| 4 | More Views | ⬜ | ⬜ | ⬜ | |
| 5 | Service Testing | ⬜ | ⬜ | ⬜ | |
| 6-10 | View Migration | ⬜ | ⬜ | ⬜ | |
| 11-15 | Frontend Templates | ⬜ | ⬜ | ⬜ | |
| 16-20 | API Layer | ⬜ | ⬜ | ⬜ | |
| 21-25 | Database & Testing | ⬜ | ⬜ | ⬜ | |

### Success Metrics
- Lines in views.py: Start: 27,782 | Current: _____ | Target: <1,000
- Number of services: Start: 4 | Current: _____ | Target: 20
- Test coverage: Start: 0% | Current: _____ | Target: 80%
- Template components: Start: 0 | Current: _____ | Target: 50

---

## 🎯 Remember

1. **One card at a time** - Don't skip ahead
2. **Test after each checkpoint** - Catch issues early
3. **Commit frequently** - Easy rollback
4. **Document issues** - Add notes to cards
5. **Ask for help early** - Don't struggle alone

**Your safety net**: At any point, you can `git checkout day[N]-complete` to return to a working state.

---

**Print Date**: ____________  
**Sprint Start**: ____________  
**Sprint End Target**: ____________  
**Actual End**: ____________  
**Final Status**: ⬜ Success | ⬜ Partial | ⬜ Rolled Back