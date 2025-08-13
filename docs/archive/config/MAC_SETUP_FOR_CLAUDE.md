# 🍎 MAC SETUP GUIDE FOR CLAUDE - PRIMEPATH PROJECT

## 🚨 CRITICAL: READ THIS FIRST
This document contains **EVERYTHING** Claude needs to know to set up and continue development of the PrimePath project on Mac. The project was developed on Windows and is being migrated to Mac. This guide ensures zero loss of functionality and seamless continuation of work.

## 📋 PROJECT STATE AS OF MIGRATION (August 8, 2025)

### Current Working Features (All Verified ✅)
1. **Student Registration & Test Taking** - Fully functional
2. **Exam Management System** - Create, edit, preview exams
3. **Answer Keys Section** - Restored and working
4. **Audio File Management** - Assignment to questions works
5. **PDF Viewer** - Displays exam papers correctly
6. **Grading System** - New template created and functional
7. **Session Management** - Track student progress
8. **AJAX Endpoints** - All API calls working
9. **Template System** - Consolidated from 17 to 13 templates
10. **JavaScript Modules** - All modules functional, no errors

### Recent Fixes Applied
- Fixed missing "Answer Keys" section in exam preview
- Fixed broken student test interface (JSON encoding issue)
- Completed template consolidation (removed 4 orphaned templates)
- Removed feature flag complexity
- Created missing `grade_session.html` template
- 100% test pass rate achieved

## 🛠️ STEP-BY-STEP MAC SETUP INSTRUCTIONS

### Step 1: Initial Project Extraction
```bash
# Navigate to your preferred projects directory
cd ~/Projects  # or wherever you want to store the project

# If you received a ZIP file
unzip PrimePath.zip

# If cloning from git
git clone [repository-url] PrimePath_

# Enter the project directory
cd PrimePath_
```

### Step 2: Verify Project Structure
```bash
# The directory structure should look like this:
ls -la

# You should see:
# - primepath_project/     (main Django project)
# - requirements.txt       (Python dependencies)
# - CLAUDE.md             (critical project knowledge)
# - MAC_SETUP_FOR_CLAUDE.md (this file)
# - Various .md documentation files
```

### Step 3: Python Environment Setup

#### Check Python Installation
```bash
# Check if Python 3 is installed
python3 --version

# Should show Python 3.11.x or higher
# If not installed, install it:
```

#### Install Python (if needed)
```bash
# Option 1: Using Homebrew (recommended)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11

# Option 2: Download from python.org
# Visit https://www.python.org/downloads/macos/
```

#### Create Virtual Environment
```bash
# IMPORTANT: Must be in PrimePath_ directory
pwd  # Should show /path/to/PrimePath_

# Create new virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Your prompt should now show (venv) prefix
# If it doesn't, the activation failed
```

### Step 4: Install Dependencies

```bash
# Ensure virtual environment is activated
which python
# Should show: /path/to/PrimePath_/venv/bin/python

# Upgrade pip first
pip install --upgrade pip

# Install core requirements
pip install -r requirements.txt

# Install additional packages that were in use
pip install djangorestframework==3.14.0
pip install django-filter==23.5
pip install django-cors-headers==4.3.1
pip install celery==5.3.4
pip install redis==5.0.1

# Verify Django installation
python -c "import django; print(f'Django {django.get_version()} installed successfully')"
```

### Step 5: Database Setup

```bash
# Navigate to Django project directory
cd primepath_project

# Check if database exists
ls -la db.sqlite3
# If it exists, you have all the data from Windows

# Run migrations to ensure database schema is current
python manage.py migrate --settings=primepath_project.settings_sqlite

# If you get any migration errors, try:
python manage.py migrate --fake-initial --settings=primepath_project.settings_sqlite
```

### Step 6: Static Files Configuration

```bash
# Still in primepath_project directory
# Collect all static files
python manage.py collectstatic --noinput --settings=primepath_project.settings_sqlite

# This will collect files to staticfiles/ directory
# You should see: "X static files copied to '/path/to/staticfiles'"
```

### Step 7: Create Superuser (Optional)

```bash
# Only if you need admin access and don't have existing superuser
python manage.py createsuperuser --settings=primepath_project.settings_sqlite

# Follow prompts to create admin user
# You'll need this to access /admin/ panel
```

### Step 8: Test Server Startup

```bash
# Start the development server
python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite

# You should see:
# Watching for file changes with StatReloader
# Performing system checks...
# System check identified no issues (0 silenced).
# Django version 5.0.1, using settings 'primepath_project.settings_sqlite'
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CONTROL-C.
```

### Step 9: Verify in Browser

1. Open Safari/Chrome/Firefox
2. Navigate to: `http://127.0.0.1:8000/`
3. You should see the PrimePath application
4. Test key pages:
   - `/admin/` - Admin panel
   - `/api/placement/` - Student registration
   - `/api/placement/exams/` - Exam management

## 🔄 CONVERTING WINDOWS COMMANDS TO MAC

### Critical Path Conversions

| Windows Path | Mac Path |
|-------------|----------|
| `venv\Scripts\python.exe` | `venv/bin/python` |
| `venv\Scripts\activate` | `source venv/bin/activate` |
| `..\venv\Scripts\python.exe` | `../venv/bin/python` |
| `C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_` | `~/Projects/PrimePath_` |

### Command Equivalents

```bash
# Windows: Run server
..\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite

# Mac: Run server
../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite

# Or if venv is activated, simply:
python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
```

## 🧪 VERIFICATION TESTS

### Run Comprehensive Test Suite

```bash
# Navigate to project root
cd ~/Projects/PrimePath_/primepath_project

# Ensure venv is activated
source ../venv/bin/activate

# Run the comprehensive test
python double_check_all_features.py
```

**Expected Output:**
```
============================================================
DOUBLE-CHECK: ALL EXISTING FEATURES
============================================================
[PASS] Student Registration - Registration form intact
[PASS] Student Test Interface - All components present
[PASS] Exam Management - Exam management working
[PASS] Exam Preview (All Sections) - All preview sections present
[PASS] Session Management - Session management working
[PASS] Grading Functionality - Grading page functional
[PASS] AJAX Endpoints - All AJAX endpoints accessible
[PASS] Curriculum Data - All curriculum data present
[PASS] JavaScript Health - No JavaScript errors detected
[PASS] Feature Flags - Feature flags properly simplified
[PASS] Template Files - Template structure correct

Success Rate: 100.0%
```

### Quick Functionality Tests

```bash
# Test student interface
python quick_test_student_fix.py

# Test answer keys
python quick_test_answer_keys.py

# Test exam list
python quick_check_exam_list.py
```

## 📁 PROJECT STRUCTURE REFERENCE

```
PrimePath_/
├── primepath_project/          # Main Django project
│   ├── manage.py              # Django management script
│   ├── db.sqlite3             # SQLite database (contains all data)
│   ├── primepath_project/     # Settings directory
│   │   ├── settings_sqlite.py # Main settings file (USE THIS)
│   │   └── urls.py           # URL configuration
│   ├── placement_test/        # Main app
│   │   ├── models.py         # Data models
│   │   ├── views/            # Modularized views
│   │   │   ├── student.py    # Student-related views
│   │   │   ├── exam.py       # Exam management views
│   │   │   └── session.py    # Session management views
│   │   └── services/         # Service layer
│   ├── templates/             # HTML templates
│   │   └── placement_test/   # App templates
│   ├── static/               # Static files (CSS, JS)
│   └── media/                # User uploads (PDFs, audio)
├── requirements.txt           # Python dependencies
├── CLAUDE.md                 # Critical knowledge base
└── venv/                     # Virtual environment (Mac-created)
```

## ⚙️ CRITICAL SETTINGS & CONFIGURATIONS

### Django Settings
- **Settings file**: `primepath_project/settings_sqlite.py`
- **Database**: SQLite (`db.sqlite3`)
- **Debug mode**: `DEBUG = True` (development)
- **Secret key**: Development key (change in production)
- **Media files**: `media/` directory
- **Static files**: `static/` and `staticfiles/`

### Feature Flags (in settings_sqlite.py)
```python
FEATURE_FLAGS = {
    'USE_SERVICE_LAYER': True,
    'USE_JS_MODULES': True,
    'ENABLE_CACHING': True,
    'ENABLE_API_V2': True,
}
```
Note: `USE_MODULAR_TEMPLATES` and `USE_V2_TEMPLATES` have been removed (consolidation complete)

### Active Templates (13 total)
- Student flow: `start_test.html`, `student_test_v2.html`, `test_result.html`
- Exam management: `exam_list.html`, `create_exam.html`, `preview_and_answers.html`
- Session management: `session_list.html`, `session_detail.html`, `grade_session.html`

## 🐛 TROUBLESHOOTING GUIDE

### Issue: "ModuleNotFoundError: No module named 'django'"
```bash
# Solution: Virtual environment not activated or packages not installed
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "django.db.utils.OperationalError: no such table"
```bash
# Solution: Run migrations
python manage.py migrate --settings=primepath_project.settings_sqlite
```

### Issue: "Static files not loading (404 errors)"
```bash
# Solution: Collect static files
python manage.py collectstatic --noinput --settings=primepath_project.settings_sqlite
```

### Issue: "Permission denied" when running scripts
```bash
# Solution: Make scripts executable
chmod +x script_name.sh
```

### Issue: "Address already in use" when starting server
```bash
# Solution: Kill existing process or use different port
lsof -i :8000
kill -9 [PID]
# Or use different port
python manage.py runserver 127.0.0.1:8001 --settings=primepath_project.settings_sqlite
```

### Issue: Server runs but can't access in browser
```bash
# Check if server is actually running
curl -I http://127.0.0.1:8000/

# If curl works but browser doesn't:
# 1. Clear browser cache
# 2. Try incognito/private mode
# 3. Try different browser
```

## 🎯 QUICK COMMAND REFERENCE

```bash
# Activate virtual environment
source ~/Projects/PrimePath_/venv/bin/activate

# Navigate to project
cd ~/Projects/PrimePath_/primepath_project

# Start server
python manage.py runserver --settings=primepath_project.settings_sqlite

# Run migrations
python manage.py migrate --settings=primepath_project.settings_sqlite

# Create superuser
python manage.py createsuperuser --settings=primepath_project.settings_sqlite

# Collect static files
python manage.py collectstatic --noinput --settings=primepath_project.settings_sqlite

# Run tests
python double_check_all_features.py

# Check Django version
python -c "import django; print(django.get_version())"

# List installed packages
pip list

# Deactivate virtual environment
deactivate
```

## 📝 IMPORTANT NOTES FOR CLAUDE

### When User Asks to Start Server
Always use this exact command:
```bash
python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
```

### When Making Code Changes
1. Always check current working directory first
2. Ensure virtual environment is activated
3. Use forward slashes (/) for all paths
4. Test changes immediately after making them

### Current Working State
- All features verified working on Windows (August 8, 2025)
- Template consolidation complete (17→13 templates)
- No known bugs or issues
- 100% test pass rate achieved

### Project Philosophy
- Modular architecture (views split into logical modules)
- Service layer pattern for business logic
- Component-based templates
- No unnecessary complexity

## ✅ SETUP COMPLETION CHECKLIST

- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] All packages installed from requirements.txt
- [ ] Additional packages installed
- [ ] Database migrated
- [ ] Static files collected
- [ ] Server starts without errors
- [ ] Can access http://127.0.0.1:8000/
- [ ] Admin panel accessible at /admin/
- [ ] Student registration page works
- [ ] Exam management page works
- [ ] All tests pass (100% success rate)

## 🚀 READY TO CONTINUE DEVELOPMENT!

Once all checklist items are complete, the project is ready for continued development on Mac. All functionality from Windows has been preserved, and you can pick up exactly where you left off.

### Next Development Tasks (Optional)
1. Performance optimization
2. Add unit tests
3. Implement lazy loading
4. Add end-to-end tests
5. Create API documentation

---
*Document created: August 8, 2025*
*Purpose: Ensure seamless Windows-to-Mac migration with zero functionality loss*
*For: Claude AI assistant on Mac to continue development*