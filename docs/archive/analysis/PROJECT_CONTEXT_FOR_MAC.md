# PROJECT CONTEXT & BUSINESS LOGIC - PRIMEPATH

## 🎯 PROJECT PURPOSE
PrimePath is an **educational placement testing system** designed to assess students' academic levels and place them in appropriate curriculum levels. It's used by educational institutions to conduct standardized placement tests.

## 🏗️ SYSTEM ARCHITECTURE

### Core Components

1. **Placement Test System**
   - Students register with basic information
   - Take timed tests with multiple question types
   - System automatically grades and recommends placement level

2. **Exam Management System**
   - Administrators create/upload exams with PDF papers
   - Assign audio files for listening comprehension
   - Set answer keys and question types
   - Configure passing scores and time limits

3. **Curriculum Mapping**
   - 4 Programs: CORE, PRIME, EXCEL, HONORS
   - Each program has multiple levels (e.g., CORE has 12 levels)
   - Placement rules determine which level students are placed into

## 📊 DATA MODELS OVERVIEW

### Key Models and Their Relationships

```python
# Simplified model relationships
Exam
├── questions (1-to-many with Question)
├── audio_files (1-to-many with AudioFile)
├── curriculum_level (ForeignKey to CurriculumLevel)
└── sessions (1-to-many with StudentSession)

StudentSession
├── exam (ForeignKey to Exam)
├── answers (1-to-many with StudentAnswer)
├── original_curriculum_level
└── final_curriculum_level (determined after grading)

Question
├── exam (ForeignKey to Exam)
├── audio_file (Optional ForeignKey to AudioFile)
├── question_type (MCQ, SHORT, LONG, CHECKBOX, MIXED)
└── correct_answer

AudioFile
├── exam (ForeignKey to Exam)
├── start_question (which question it starts at)
└── end_question (which question it ends at)
```

## 🔄 CRITICAL WORKFLOWS

### 1. Student Test-Taking Flow
```
Start Test → Register Info → Take Test → Submit Answers → View Results
     ↓            ↓              ↓            ↓              ↓
[start_test] [create session] [take_test] [complete_test] [test_result]
```

### 2. Exam Creation Flow
```
Upload PDF → Create Questions → Set Answer Keys → Assign Audio → Preview
     ↓            ↓                  ↓               ↓            ↓
[create_exam] [manage_questions] [preview_and_answers] [save_exam_answers]
```

### 3. Grading Flow
```
Session Complete → Auto-Grade → Manual Review → Final Placement
        ↓              ↓             ↓              ↓
[complete_test] [GradingService] [grade_session] [placement_rules]
```

## 🔧 TECHNICAL IMPLEMENTATION DETAILS

### URL Patterns
```python
# Main URL structure
/api/placement/                    # Student registration
/api/placement/session/<id>/       # Take test
/api/placement/exams/              # Exam management
/api/placement/exams/<id>/preview/ # Preview with answer keys
/admin/                            # Django admin panel
```

### Service Layer Architecture
```python
# Services handle business logic
PlacementService    # Student-exam matching
SessionService      # Session management
ExamService        # Exam operations
GradingService     # Scoring and grading
```

### JavaScript Module System
```javascript
// Frontend modules (all in static/js/modules/)
pdf-viewer.js       // PDF rendering
timer.js           // Test timer
audio-player.js    // Audio playback
answer-manager.js  // Answer tracking
navigation.js      // Question navigation
error-handler.js   // Error management
memory-manager.js  // Memory optimization
```

## 🎨 UI/UX STRUCTURE

### Template Organization
```
templates/placement_test/
├── Student Interface
│   ├── start_test.html         # Registration form
│   ├── student_test_v2.html    # Main test interface (component-based)
│   └── test_result.html        # Results display
├── Admin Interface
│   ├── exam_list.html          # Exam management dashboard
│   ├── create_exam.html        # New exam creation
│   ├── preview_and_answers.html # Full preview with answer management
│   └── grade_session.html      # Manual grading interface
└── Components
    ├── pdf_viewer.html         # PDF display component
    ├── question_panel.html     # Question/answer component
    ├── timer.html             # Timer component
    └── audio_player.html      # Audio playback component
```

### CSS Architecture
```
static/css/
├── base/           # Reset, variables
├── components/     # Component-specific styles
├── layouts/        # Layout structures
└── pages/         # Page-specific styles
```

## 🔒 AUTHENTICATION & PERMISSIONS

- **Students**: No login required (session-based)
- **Administrators**: Django admin authentication
- **Session Security**: IP tracking, time limits, single submission

## 📈 BUSINESS RULES

### Placement Rules
1. **Grade + Academic Rank** → Initial curriculum level
2. **Test Performance** → May adjust level up/down
3. **Difficulty Adjustments** → Dynamic during test (if enabled)
4. **Final Placement** → Based on score + adjustments

### Question Types
- **MCQ**: Multiple choice (A, B, C, D)
- **SHORT**: Short text answer
- **LONG**: Essay/paragraph answer
- **CHECKBOX**: Multiple correct answers
- **MIXED**: Combination type

### Scoring System
- Each question has configurable points
- Percentage score calculated automatically
- Passing score configurable per exam
- Manual override available for grading

## 🐛 RECENT FIXES & IMPROVEMENTS

### Phase 1: Answer Keys Restoration
- **Problem**: Answer Keys section missing from exam preview
- **Solution**: Fixed template reference in `exam.py`
- **Impact**: Admins can now manage answer keys

### Phase 2: Student Interface Fix
- **Problem**: PDF not loading, answers not visible
- **Solution**: Fixed double JSON encoding issue
- **Impact**: Students can take tests properly

### Phase 3: Template Consolidation
- **Problem**: 17 templates with duplicates and orphans
- **Solution**: Reduced to 13 clean templates
- **Impact**: Cleaner, more maintainable codebase

### Phase 4: Feature Flag Cleanup
- **Problem**: Complex conditional template selection
- **Solution**: Removed USE_MODULAR_TEMPLATES and USE_V2_TEMPLATES
- **Impact**: Simplified code flow

## 💡 DEVELOPMENT GUIDELINES

### When Adding Features
1. Follow existing patterns (service layer for logic)
2. Use modular views structure
3. Create reusable components
4. Add to existing modules, don't create new ones unnecessarily

### When Fixing Bugs
1. Check `CLAUDE.md` for known issues first
2. Run `double_check_all_features.py` after fixes
3. Don't add complexity to fix complexity
4. Test with curl before assuming server issues

### When Modifying Templates
1. V2 templates are the standard (component-based)
2. Check component templates in `components/placement_test/`
3. Maintain consistent styling with existing CSS

### When Working with JavaScript
1. Use existing modules in `static/js/modules/`
2. Follow initialization order (see CLAUDE.md)
3. Use event delegation pattern
4. Handle errors gracefully

## 🔍 DEBUGGING TIPS

### Server Issues
```bash
# Always test with curl first
curl -I http://127.0.0.1:8000/

# Check for Python process
ps aux | grep python

# View server logs
python manage.py runserver --verbosity 3
```

### Database Issues
```bash
# Check database integrity
python manage.py dbshell
.tables  # SQLite command
.schema placement_test_exam

# Export data for inspection
python manage.py dumpdata placement_test --indent 2 > data.json
```

### JavaScript Issues
```javascript
// Check APP_CONFIG initialization
console.log('APP_CONFIG:', window.APP_CONFIG);

// Check module initialization
console.log('Modules loaded:', {
    pdfViewer: window.pdfViewer,
    answerManager: window.answerManager,
    navigationModule: window.navigationModule
});
```

## 📚 DOMAIN TERMINOLOGY

- **Placement Test**: Assessment to determine student's academic level
- **Curriculum Level**: Specific grade/level within a program
- **Session**: One instance of a student taking a test
- **Audio Assignment**: Linking audio files to specific questions
- **Answer Key**: Correct answers for grading
- **Manual Score**: Override score assigned by administrator

## 🎯 CURRENT PRIORITIES

1. **Stability**: System is stable, all features working
2. **Performance**: Consider optimization for large PDFs
3. **Testing**: Add automated tests for critical paths
4. **Documentation**: Keep documentation updated

## 🚀 FUTURE ENHANCEMENTS (OPTIONAL)

1. **Real-time Progress Tracking**: WebSocket updates
2. **Bulk Operations**: Upload multiple exams at once
3. **Analytics Dashboard**: Performance trends
4. **Export Features**: Results to CSV/PDF
5. **Multi-language Support**: Internationalization

## ⚠️ CRITICAL WARNINGS

1. **Never modify** `db.sqlite3` directly - use Django ORM
2. **Always use** `--settings=primepath_project.settings_sqlite`
3. **Don't remove** migration files - they track schema changes
4. **Test locally** before suggesting production changes
5. **Preserve** existing URL patterns - external systems may depend on them

## 📞 SUPPORT INFORMATION

- **Original Developer**: Windows/Claude collaboration
- **Migration Date**: August 8, 2025
- **Current Platform**: Mac (migrated from Windows)
- **Django Version**: 5.0.1
- **Python Version**: 3.11+
- **Database**: SQLite (portable)

---
*This document provides complete context for continuing development on Mac*
*All business logic and technical details preserved from Windows environment*