# 🚀 Claude Vibe Coding Execution Plan

**Purpose**: Feed this to Claude step-by-step for rapid modularization  
**Approach**: Fast, direct, no overthinking  
**Timeline**: 1-2 days max  

---

## 📋 How to Use This Document with Claude

```
Simply tell Claude:
"Execute Step [X] from CLAUDE_VIBE_CODING_EXECUTION.md"

Claude will:
1. Read the step
2. Implement it
3. Test it
4. Report completion
```

---

## 🎯 PHASE 1: Backend Service Extraction (2-3 hours)

### Step 1: Create Service Infrastructure (10 minutes)
**Tell Claude**: "Create the service layer infrastructure with BaseService class and all service directories"

Claude should:
```python
# Create these directories and files:
placement_test/services/
├── __init__.py
├── base.py  # BaseService with execute(), _perform(), _validate()
├── exam_service.py
├── session_service.py
├── grading_service.py
└── placement_service.py

# BaseService should have:
- execute() method with transaction wrapper
- _perform() abstract method
- _validate() for input validation
- Error handling
- Logging
```

Expected output: "✅ Service infrastructure created with BaseService and 4 service files"

---

### Step 2: Extract ALL Exam Logic (30 minutes)
**Tell Claude**: "Extract all exam-related functions from views.py into ExamService class. Move these functions: create_exam, edit_exam, delete_exam, exam_list, exam_detail, preview_exam, manage_questions, create_questions, update_question"

Claude should:
```python
# In exam_service.py, create methods:
class ExamService:
    @staticmethod
    def create_exam(exam_data, pdf_file, created_by):
        # Move lines 241-323 from views.py
        
    @staticmethod
    def get_exam_list(filters=None):
        # Move lines 215-220 from views.py
        
    @staticmethod
    def get_exam_detail(exam_id):
        # Move lines 324-336 from views.py
        
    # ... continue for all exam functions

# In views.py, replace with:
def create_exam(request):
    if request.method == 'POST':
        exam = ExamService.create_exam(
            exam_data=form.cleaned_data,
            pdf_file=request.FILES['pdf_file'],
            created_by=request.user
        )
        return redirect('exam_detail', exam.id)
```

Expected output: "✅ Extracted 10 exam functions to ExamService, views.py reduced by ~5000 lines"

---

### Step 3: Extract ALL Session Logic (30 minutes)
**Tell Claude**: "Extract all session-related functions from views.py into SessionService. Move: start_test, take_test, submit_answer, adjust_difficulty, complete_test, test_result, session_list, session_detail, grade_session"

Claude should:
```python
# In session_service.py:
class SessionService:
    @staticmethod
    def start_test(student_data, exam_id):
        # Move logic from views.py
        
    @staticmethod
    def submit_answer(session_id, question_id, answer):
        # Move logic from views.py
        
    @staticmethod
    def complete_test(session_id):
        # Calculate score, save results
        # Move lines 186-199 from views.py

# Views become thin wrappers:
def submit_answer(request, session_id):
    result = SessionService.submit_answer(
        session_id=session_id,
        question_id=request.POST['question_id'],
        answer=request.POST['answer']
    )
    return JsonResponse(result)
```

Expected output: "✅ Extracted 9 session functions to SessionService, views.py reduced by another ~5000 lines"

---

### Step 4: Extract Grading & Placement Logic (20 minutes)
**Tell Claude**: "Move all grading and placement logic to their respective services"

Claude should:
```python
# In grading_service.py:
class GradingService:
    @staticmethod
    def auto_grade_answer(question, answer):
        # MCQ grading logic
        
    @staticmethod
    def calculate_session_score(session):
        # Total score calculation

# In placement_service.py:
class PlacementService:
    @staticmethod
    def determine_placement(grade, score):
        # Placement rules logic
```

Expected output: "✅ Grading and placement logic extracted, views.py now under 5000 lines"

---

### Step 5: Quick Test & Commit (10 minutes)
**Tell Claude**: "Test that all pages still load and commit the service layer extraction"

Claude should:
```bash
# Test key pages still work
python manage.py runserver
# Visit: /api/placement/exams/
# Visit: /api/placement/start/
# Try creating an exam
# Try taking a test

# If all works:
git add -A
git commit -m "REFACTOR: Extract service layer - views.py from 27k to 5k lines"
```

Expected output: "✅ All pages working, service layer committed"

---

## 🎯 PHASE 2: View Decomposition (1 hour)

### Step 6: Split Views into Modules (30 minutes)
**Tell Claude**: "Split the remaining views.py into modular view files"

Claude should:
```python
# Create structure:
placement_test/views/
├── __init__.py  # Import all for compatibility
├── exam_views.py  # All exam-related views
├── session_views.py  # All session-related views
├── admin_views.py  # Admin/teacher views
├── api_views.py  # API endpoints
└── common_views.py  # Shared utilities

# Move functions to appropriate files
# In __init__.py:
from .exam_views import *
from .session_views import *
from .admin_views import *
from .api_views import *

# Delete old views.py or rename to views_old.py
```

Expected output: "✅ Views split into 5 modules, no more monolithic file"

---

### Step 7: Optimize Imports & Routes (15 minutes)
**Tell Claude**: "Clean up imports and ensure all URL routes still work"

Claude should:
```python
# In urls.py, update imports:
from placement_test.views import exam_views, session_views, api_views

# Update URL patterns to use specific views:
urlpatterns = [
    path('exams/', exam_views.exam_list, name='exam_list'),
    path('sessions/', session_views.session_list, name='session_list'),
    # ... etc
]

# Test all routes still resolve
```

Expected output: "✅ All routes working with modular views"

---

### Step 8: Add Smart Caching (15 minutes)
**Tell Claude**: "Add query optimization and caching to the services"

Claude should:
```python
# In exam_service.py:
from django.core.cache import cache

class ExamService:
    @staticmethod
    def get_exam_detail(exam_id):
        cache_key = f'exam_{exam_id}'
        exam = cache.get(cache_key)
        
        if not exam:
            exam = Exam.objects.select_related('curriculum_level', 'created_by')\
                              .prefetch_related('questions', 'audio_files')\
                              .get(id=exam_id)
            cache.set(cache_key, exam, 3600)  # Cache for 1 hour
        
        return exam

# Add similar optimization to all get methods
```

Expected output: "✅ Added caching and query optimization"

---

## 🎯 PHASE 3: Frontend Modularization (2-3 hours)

### Step 9: Break Up Monster Templates (45 minutes)
**Tell Claude**: "Break preview_and_answers.html (3342 lines) into components"

Claude should:
```html
<!-- Create component files: -->
templates/components/
├── exam/
│   ├── pdf_viewer.html  # Extract PDF viewer section
│   ├── audio_player.html  # Extract audio player
│   └── question_display.html  # Extract question rendering
├── answers/
│   ├── answer_form.html  # Answer input section
│   ├── answer_list.html  # Answer display
│   └── grading_display.html  # Grading section
└── common/
    ├── timer.html
    └── navigation.html

<!-- In preview_and_answers.html, replace with includes: -->
{% include 'components/exam/pdf_viewer.html' %}
{% include 'components/exam/audio_player.html' %}
{% include 'components/answers/answer_form.html' %}

<!-- Should go from 3342 lines to ~200 lines -->
```

Expected output: "✅ preview_and_answers.html reduced from 3342 to 200 lines using components"

---

### Step 10: Break Up student_test.html (30 minutes)
**Tell Claude**: "Break student_test.html (2251 lines) into components"

Claude should:
```html
<!-- Similar component extraction -->
<!-- Main template becomes just structure: -->
{% extends 'base.html' %}

{% block content %}
<div class="test-container">
    {% include 'components/common/timer.html' %}
    {% include 'components/exam/pdf_viewer.html' %}
    {% include 'components/test/question_navigator.html' %}
    {% include 'components/test/answer_panel.html' %}
</div>
{% endblock %}

{% block extra_js %}
    <!-- Use the modular JS you already created -->
    <script src="{% static 'js/modules/timer.js' %}"></script>
    <script src="{% static 'js/modules/pdf-viewer.js' %}"></script>
    <script src="{% static 'js/modules/answer-manager.js' %}"></script>
{% endblock %}
```

Expected output: "✅ student_test.html reduced from 2251 to 150 lines"

---

### Step 11: Extract Remaining Inline JavaScript (30 minutes)
**Tell Claude**: "Extract all remaining inline JavaScript from templates to external files"

Claude should:
```javascript
// Create static/js/pages/ directory
// Move inline scripts to page-specific files:

// static/js/pages/exam-create.js
window.ExamCreator = {
    init: function(config) {
        // All JS from create_exam.html
    }
};

// static/js/pages/session-list.js  
window.SessionManager = {
    init: function(config) {
        // All JS from session_list.html
    }
};

// In templates, just initialize:
<script>
ExamCreator.init({
    csrfToken: '{{ csrf_token }}',
    uploadUrl: '{% url "exam_create" %}'
});
</script>
```

Expected output: "✅ All inline JavaScript extracted to external files"

---

### Step 12: Wire Up Existing Modules (15 minutes)
**Tell Claude**: "Ensure all the modular JS files we created earlier are properly integrated"

Claude should:
```javascript
// In each template, replace old inline code with module initialization:

// For student_test.html:
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    const timer = new PrimePath.modules.Timer();
    timer.init({{ timer_seconds }}, '#timer');
    timer.start();
    
    const audioPlayer = new PrimePath.modules.AudioPlayer();
    audioPlayer.init();
    
    const answerManager = new PrimePath.modules.AnswerManager({
        sessionId: '{{ session.id }}'
    });
    answerManager.init();
    
    const pdfViewer = new PrimePath.modules.PDFViewer();
    pdfViewer.init('#pdf-viewer', '{{ exam.pdf_file.url }}');
});
</script>
```

Expected output: "✅ All modular JS properly integrated"

---

## 🎯 PHASE 4: API Standardization (1 hour)

### Step 13: Create API Response Standards (20 minutes)
**Tell Claude**: "Create standardized API response handlers"

Claude should:
```python
# placement_test/api/responses.py
class APIResponse:
    @staticmethod
    def success(data=None, message="Success", status=200):
        return JsonResponse({
            'success': True,
            'message': message,
            'data': data,
            'timestamp': timezone.now().isoformat()
        }, status=status)
    
    @staticmethod
    def error(message, errors=None, status=400):
        return JsonResponse({
            'success': False,
            'message': message,
            'errors': errors,
            'timestamp': timezone.now().isoformat()
        }, status=status)
    
    @staticmethod
    def paginated(queryset, page=1, limit=20):
        # Add pagination wrapper
        pass

# Update all JSON responses:
# Before: return JsonResponse({'result': 'ok'})
# After: return APIResponse.success(data={'result': 'ok'})
```

Expected output: "✅ Standardized API responses implemented"

---

### Step 14: Add Request Validation (20 minutes)
**Tell Claude**: "Add validation layer for all API endpoints"

Claude should:
```python
# placement_test/api/validators.py
class RequestValidator:
    @staticmethod
    def validate_exam_create(data):
        required = ['name', 'pdf_file', 'total_questions']
        errors = {}
        
        for field in required:
            if field not in data:
                errors[field] = f"{field} is required"
        
        if errors:
            raise ValidationError(errors)
        
        return data
    
    @staticmethod
    def validate_answer_submit(data):
        # Validation logic
        pass

# In views:
def create_exam(request):
    try:
        validated_data = RequestValidator.validate_exam_create(request.POST)
        exam = ExamService.create_exam(validated_data)
        return APIResponse.success(data={'exam_id': exam.id})
    except ValidationError as e:
        return APIResponse.error("Validation failed", errors=e.errors)
```

Expected output: "✅ Request validation layer added"

---

### Step 15: Create RESTful Endpoints (20 minutes)
**Tell Claude**: "Create clean RESTful API endpoints"

Claude should:
```python
# placement_test/api/v2/urls.py
urlpatterns = [
    path('exams/', ExamListAPI.as_view()),  # GET, POST
    path('exams/<uuid:id>/', ExamDetailAPI.as_view()),  # GET, PUT, DELETE
    path('sessions/', SessionListAPI.as_view()),  # GET, POST
    path('sessions/<uuid:id>/', SessionDetailAPI.as_view()),  # GET, PUT
    path('sessions/<uuid:id>/answers/', AnswerAPI.as_view()),  # POST
]

# placement_test/api/v2/exam_api.py
class ExamListAPI(View):
    def get(self, request):
        exams = ExamService.get_exam_list(filters=request.GET)
        return APIResponse.success(data=exams)
    
    def post(self, request):
        exam = ExamService.create_exam(request.POST)
        return APIResponse.success(data={'id': exam.id}, status=201)
```

Expected output: "✅ RESTful API v2 created"

---

## 🎯 PHASE 5: Final Testing & Optimization (30 minutes)

### Step 16: Performance Check (10 minutes)
**Tell Claude**: "Run performance checks and optimize slow queries"

Claude should:
```python
# Install django-debug-toolbar if not installed
# Check for N+1 queries
# Add select_related and prefetch_related where needed

# Run this check:
from django.db import connection
from django.test.utils import override_settings

@override_settings(DEBUG=True)
def check_queries():
    # Reset queries
    from django.db import reset_queries
    reset_queries()
    
    # Test exam list
    response = client.get('/api/placement/exams/')
    print(f"Exam list queries: {len(connection.queries)}")
    
    # Should be < 5 queries
    assert len(connection.queries) < 5
```

Expected output: "✅ Performance optimized, all pages load in < 200ms"

---

### Step 17: Create Tests (10 minutes)
**Tell Claude**: "Create basic tests for critical paths"

Claude should:
```python
# placement_test/tests/test_services.py
class ServiceTests(TestCase):
    def test_exam_creation(self):
        exam = ExamService.create_exam({
            'name': 'Test',
            'total_questions': 10
        })
        self.assertIsNotNone(exam)
    
    def test_session_completion(self):
        # Test session flow
        pass

# Run: python manage.py test
```

Expected output: "✅ Basic tests created and passing"

---

### Step 18: Final Cleanup & Commit (10 minutes)
**Tell Claude**: "Do final cleanup, remove commented code, and commit everything"

Claude should:
```bash
# Remove old backup files
rm placement_test/views_old.py  # If exists

# Remove commented code
# Fix any import errors
# Update requirements.txt if needed

# Final test
python manage.py runserver
# Test all critical paths work

# Commit
git add -A
git commit -m "COMPLETE: Full modularization - 27k lines to modular architecture"

# Create success tag
git tag modularization-complete
```

Expected output: "✅ Modularization complete! Views reduced from 27,782 to < 500 lines per file"

---

## 🚀 Quick Execution Commands for Claude

### Full Speed Run (Copy-paste these one by one):
```
1. "Execute Steps 1-5: Extract all services from views.py"
2. "Execute Steps 6-8: Decompose views into modules"  
3. "Execute Steps 9-12: Break up templates and wire JS modules"
4. "Execute Steps 13-15: Standardize API layer"
5. "Execute Steps 16-18: Optimize and finalize"
```

### Or Even Faster (Single Command):
```
"Execute all 18 steps from CLAUDE_VIBE_CODING_EXECUTION.md 
in rapid succession, testing after each phase"
```

---

## 🎯 Success Metrics

After execution, you should have:
- ✅ views.py: From 27,782 lines → DELETED (split into modules)
- ✅ preview_and_answers.html: From 3,342 → ~200 lines
- ✅ student_test.html: From 2,251 → ~150 lines
- ✅ Service files: 4 comprehensive services
- ✅ View modules: 5 focused view files
- ✅ Template components: 20+ reusable components
- ✅ API: Standardized v2 endpoints
- ✅ Performance: < 200ms page loads
- ✅ Tests: Basic coverage for critical paths

---

## 🔥 Vibe Check Points

After each phase, ask Claude:
- "Is everything still working?"
- "How many lines did we reduce?"
- "Show me the git diff stats"

If something breaks:
- "Fix the error and continue"
- "Roll back last change and try different approach"

---

## 💡 Pro Tips for Claude

1. **Be Direct**: "Extract all exam logic to ExamService NOW"
2. **Be Specific**: "Move lines 241-323 from views.py to exam_service.py"
3. **Test Fast**: "Quick test - does exam creation still work?"
4. **Move Fast**: "Don't overthink, just refactor and test"
5. **Commit Often**: "Commit this phase before continuing"

---

**Total Time Estimate**: 
- With Claude doing the work: 4-6 hours
- Without interruptions: 2-3 hours
- Vibe coding mode: Just keep saying "next step" until done

**Remember**: Claude has seen your entire codebase. It knows where everything is. Just point and shoot! 🎯