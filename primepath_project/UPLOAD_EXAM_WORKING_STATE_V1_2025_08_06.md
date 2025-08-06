# Upload Exam Tab - Working Setup Documentation V1
**Date: August 6, 2025**  
**Git Commit: 89203e6**  
**Status: FULLY FUNCTIONAL ✅**

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [File Structure](#file-structure)
4. [Endpoint Documentation](#endpoint-documentation)
5. [Critical Code Components](#critical-code-components)
6. [Database State](#database-state)
7. [Dependencies](#dependencies)
8. [Testing Procedures](#testing-procedures)
9. [Known Issues Fixed](#known-issues-fixed)
10. [Recovery Procedures](#recovery-procedures)

---

## Overview

The Upload Exam feature allows teachers to upload placement test PDFs with optional audio files. The system automatically generates questions, handles versioning, and integrates with the placement rules system.

### Key Features Working:
- ✅ PDF file upload with validation
- ✅ Audio file upload (multiple files)
- ✅ Automatic exam naming with versioning
- ✅ PDF preview using PDF.js
- ✅ Form validation (frontend and backend)
- ✅ Automatic question generation
- ✅ Integration with curriculum levels

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
├─────────────────────────────────────────────────────────────┤
│  create_exam.html                                            │
│  ├── Form (id="examForm")                                    │
│  ├── PDF Upload (id="pdf_file")                             │
│  ├── Audio Upload (id="audio_files")                        │
│  ├── JavaScript Validation                                   │
│  └── PDF.js Preview Integration                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    POST /api/placement/exams/create/
                              │
┌─────────────────────────────────────────────────────────────┐
│                        Backend                               │
├─────────────────────────────────────────────────────────────┤
│  placement_test.views.create_exam                           │
│  ├── @handle_errors decorator                               │
│  ├── Validation (name, total_questions, pdf_file)          │
│  ├── ExamService.create_exam()                             │
│  └── Redirect on success                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                            │
├─────────────────────────────────────────────────────────────┤
│  ExamService.create_exam()                                  │
│  ├── Create Exam instance                                   │
│  ├── Create placeholder questions                           │
│  └── Attach audio files                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Database                               │
├─────────────────────────────────────────────────────────────┤
│  Models:                                                     │
│  ├── Exam (WITHOUT skip_first_left_half)                    │
│  ├── Question                                               │
│  ├── AudioFile                                              │
│  └── CurriculumLevel                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure

### Frontend Files
```
primepath_project/templates/placement_test/create_exam.html
├── Lines 361-365: PDF.js library loading with safety check
├── Lines 379-386: PDF file input with label
├── Lines 499-503: Timer minutes input
├── Lines 505-509: Total questions input
├── Lines 579-654: PDF file change event handler
├── Lines 774-793: PDF navigation buttons
├── Lines 1048-1074: generateVersionedName() function
├── Lines 1072-1110: Form submission handler
```

### Backend Files
```
primepath_project/placement_test/
├── views.py
│   └── Lines 240-299: create_exam() view function
├── services/exam_service.py
│   └── Lines 19-64: create_exam() service method
├── models.py
│   └── Lines 7-35: Exam model (NO skip_first_left_half field)
├── urls.py
│   └── Line 15: path('exams/create/', views.create_exam, name='create_exam')
```

### Migration Files
```
primepath_project/placement_test/migrations/
├── 0011_remove_skip_first_left_half.py  # Critical: Removes the field
```

---

## Endpoint Documentation

### POST /api/placement/exams/create/

#### Request Flow:
1. **URL Pattern**: `path('exams/create/', views.create_exam, name='create_exam')`
2. **View Function**: `placement_test.views.create_exam`
3. **Decorator**: `@handle_errors(template_name='placement_test/create_exam.html')`

#### Required POST Parameters:
```python
{
    'name': str,                    # Exam name (generated or custom)
    'curriculum_level': str,        # Optional curriculum level ID
    'timer_minutes': int,           # Default: 60
    'total_questions': int,         # Required, no default
    'default_options_count': int,   # Default: 5
    'pdf_file': File,              # Required PDF file
    'audio_files': FileList,       # Optional audio files
    'audio_names[]': List[str]     # Optional audio names
}
```

#### Validation Chain:
1. **Frontend JavaScript** (lines 1072-1110 in create_exam.html):
   - Checks PDF file exists
   - Validates exam name is set
   - Creates hidden 'name' field dynamically

2. **Backend Python** (lines 243-286 in views.py):
   - Validates exam_name not empty
   - Validates total_questions exists
   - Validates PDF file exists
   - Handles ValueError and ValidationException

---

## Critical Code Components

### 1. JavaScript Name Generation (create_exam.html)
```javascript
// Lines 1048-1074 - CRITICAL: Prevents race condition
function generateVersionedName() {
    const selectedOption = presetSelect.options[presetSelect.selectedIndex];
    if (selectedOption.value) {
        // Set default name IMMEDIATELY to prevent race condition
        const baseName = selectedOption.getAttribute('data-level-name');
        finalExamName = `[PlacementTest] ${baseName}_v_a`; // Default
        
        // Then fetch actual version
        fetch(`/api/placement/exams/check-version/?curriculum_level=${selectedOption.value}`)
            .then(response => response.json())
            .then(data => {
                const version = data.next_version || 'a';
                finalExamName = `[PlacementTest] ${baseName}_v_${version}`;
                // Update UI...
            })
            .catch(error => {
                // Fallback already set above
            });
    }
}
```

### 2. Form Submission Handler (create_exam.html)
```javascript
// Lines 1072-1110 - CRITICAL: Dynamic name field creation
document.getElementById('examForm')?.addEventListener('submit', function(e) {
    // Validate PDF file
    const pdfFile = document.getElementById('pdf_file').files[0];
    if (!pdfFile) {
        e.preventDefault();
        alert('Please select a PDF file before uploading.');
        return;
    }
    
    // Create hidden name field
    if (presetNameRadio.checked) {
        let nameInput = document.createElement('input');
        nameInput.type = 'hidden';
        nameInput.name = 'name';
        nameInput.value = finalExamName;
        this.appendChild(nameInput);
    }
    // ...
});
```

### 3. Backend View (views.py)
```python
# Lines 240-286 - CRITICAL: Validation and error handling
@handle_errors(template_name='placement_test/create_exam.html')
def create_exam(request):
    if request.method == 'POST':
        try:
            # Validate required fields
            exam_name = request.POST.get('name')
            if not exam_name:
                raise ValidationException("Exam name is required", code="MISSING_NAME")
            
            total_questions = request.POST.get('total_questions')
            if not total_questions:
                raise ValidationException("Total number of questions is required", code="MISSING_QUESTIONS")
            
            # Create exam data
            exam_data = {
                'name': exam_name,
                'curriculum_level_id': request.POST.get('curriculum_level', '').strip() or None,
                'timer_minutes': int(request.POST.get('timer_minutes', 60)),
                'total_questions': int(total_questions),
                'default_options_count': int(request.POST.get('default_options_count', 5)),
                'passing_score': 0,
                'created_by': None,
                'is_active': True
            }
            
            # Validate PDF
            pdf_file = request.FILES.get('pdf_file')
            if not pdf_file:
                raise ValidationException("PDF file is required", code="MISSING_PDF")
            
            # Create exam
            exam = ExamService.create_exam(
                exam_data=exam_data,
                pdf_file=pdf_file,
                audio_files=request.FILES.getlist('audio_files'),
                audio_names=request.POST.getlist('audio_names[]')
            )
            
            messages.success(request, f'Exam "{exam.name}" uploaded successfully!')
            return redirect('placement_test:create_exam')
            
        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
        except ValidationException as e:
            messages.error(request, e.message)
```

### 4. Service Layer (exam_service.py)
```python
# Lines 38-49 - CRITICAL: NO skip_first_left_half field
exam = Exam.objects.create(
    name=exam_data['name'],
    curriculum_level_id=exam_data.get('curriculum_level_id'),
    pdf_file=pdf_file,
    timer_minutes=exam_data.get('timer_minutes', 60),
    total_questions=exam_data['total_questions'],
    default_options_count=exam_data.get('default_options_count', DEFAULT_OPTIONS_COUNT),
    passing_score=exam_data.get('passing_score', 0),
    created_by=exam_data.get('created_by'),
    is_active=exam_data.get('is_active', True)
    # NO skip_first_left_half field here!
)
```

---

## Database State

### Current Exam Model Fields (models.py lines 7-23):
```python
class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    curriculum_level = models.ForeignKey(CurriculumLevel, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    pdf_file = models.FileField(upload_to='exams/pdfs/', validators=[FileExtensionValidator(['pdf'])])
    timer_minutes = models.IntegerField(default=60, validators=[MinValueValidator(1)])
    total_questions = models.IntegerField(validators=[MinValueValidator(1)])
    default_options_count = models.IntegerField(default=5, validators=[MinValueValidator(2), MaxValueValidator(10)])
    passing_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    # NO skip_first_left_half field!
```

### Applied Migrations:
```
0001_initial.py through 0011_remove_skip_first_left_half.py
```

---

## Dependencies

### External Libraries:
```javascript
// PDF.js for preview (create_exam.html lines 361-363)
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
```

### Django Apps:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'placement_test',
    'core',
]
```

### Python Packages:
```
Django==5.0.1
```

---

## Testing Procedures

### Manual Testing Steps:
1. Navigate to `/api/placement/exams/create/`
2. Select "Choose from pre-designed names"
3. Select any curriculum level
4. Enter total questions (e.g., 50)
5. Keep timer at 60 minutes
6. Upload a PDF file
7. Optionally add audio files
8. Click "Upload Exam"
9. Should see success message and page refresh

### Automated Test Commands:
```bash
cd primepath_project
../venv/Scripts/python.exe test_exam_creation.py
../venv/Scripts/python.exe comprehensive_qa_test.py
```

### Verification Checklist:
- [ ] No 500 error on form submission
- [ ] PDF preview displays after file selection
- [ ] Form validates missing fields
- [ ] Success message appears after upload
- [ ] Exam appears in exam list
- [ ] Questions are auto-generated

---

## Known Issues Fixed

### 1. 500 Internal Server Error on Form Submission
**Cause**: `skip_first_left_half` field removed from database but still referenced in code  
**Fix**: Removed all references from:
- `exam_service.py` line 49
- `preview_and_answers.html` lines 896, 1526, 2028, 2036

### 2. Race Condition in Name Generation
**Cause**: Async fetch for version could complete after form submission  
**Fix**: Set default name immediately in `generateVersionedName()` function

### 3. Missing Form Validation
**Cause**: No validation for required fields  
**Fix**: Added comprehensive validation in views.py lines 243-268

---

## Recovery Procedures

### If Upload Exam Breaks:

#### Option 1: Revert to This Commit
```bash
git checkout 89203e6
```

#### Option 2: Cherry-pick Specific Fixes
```bash
# Get the exam service fix
git cherry-pick 89203e6

# Or manually apply changes:
# 1. Remove skip_first_left_half from exam_service.py line 49
# 2. Add validation to views.py create_exam function
# 3. Fix JavaScript name generation race condition
```

#### Option 3: Compare Against This Documentation
```bash
# Check what changed
git diff 89203e6 -- primepath_project/placement_test/services/exam_service.py
git diff 89203e6 -- primepath_project/placement_test/views.py
git diff 89203e6 -- primepath_project/templates/placement_test/create_exam.html
```

### Critical Files to Never Break:
1. `placement_test/services/exam_service.py` - Line 49 must NOT have skip_first_left_half
2. `placement_test/views.py` - Lines 243-286 must have validation
3. `templates/placement_test/create_exam.html` - Lines 1048-1074 must set default name

---

## Change Log

### August 6, 2025 - Version 1
- Fixed 500 error by removing skip_first_left_half references
- Added comprehensive form validation
- Fixed JavaScript race condition
- Added error handling for missing fields
- Created this documentation

---

## Quick Reference Commands

```bash
# Start server
cd primepath_project
../venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite

# Test upload functionality
curl -I http://127.0.0.1:8000/api/placement/exams/create/

# Run tests
../venv/Scripts/python.exe test_exam_creation.py
```

---

**END OF DOCUMENTATION**  
**This represents the STABLE, WORKING state of Upload Exam feature as of August 6, 2025**