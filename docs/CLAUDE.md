# PrimePath Project - Critical Knowledge Base

## 🤖 AUTONOMOUS AGENT SYSTEM - ACTIVE

### CRITICAL: Process ALL User Requests Through Agents
**EVERY command from the user MUST be analyzed by the autonomous agent system FIRST**

### How to Process User Commands:
```bash
# For ANY user request about fixing, adding, changing, or reviewing:
# ALWAYS RUN THIS FIRST:
python /Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/PROCESS_REQUEST.py "exact user command"

# Then follow the agent recommendations that are displayed
```

### Agent Activation Keywords (Auto-triggers):
- **UI/UX Issues**: wide, narrow, layout, design, color, spacing, responsive
- **Implementation**: fix, add, change, update, implement, bug, error
- **Testing**: test, verify, check, ensure, quality
- **Performance**: slow, fast, optimize, performance, loading
- **Security**: auth, permission, vulnerability, security
- **Documentation**: document, explain, readme, guide

### Integration Check:
1. **BEFORE doing any work**, run: `python agent_system/check_agents.py`
2. **Agents will automatically**:
   - Analyze the request
   - Self-organize by expertise
   - Collaborate on solution
   - Provide consolidated results

### Example Usage:
```bash
# User says: "The curriculum column is too wide"
python -c "from agent_system.integration import process_with_agents; process_with_agents('The curriculum column is too wide')"
```

**IMPORTANT**: Do NOT manually implement fixes without running through agents first!

## 🔧 Chrome Control MCP - Working Setup

### Quick Setup (One Command!)
```bash
claude mcp add chrome-control "node" "$HOME/Library/Application Support/Claude/Claude Extensions/ant.dir.ant.anthropic.chrome-control/server/index.js"
```
Then **restart Claude** for tools to become available.

### Verify Setup
```bash
claude mcp list
# Should show: chrome-control ... ✓ Connected
```

### Available Chrome Tools
After setup, these tools work in Claude:
- `open_url` - Open URLs in Chrome
- `get_current_tab` - Get tab info
- `list_tabs` - List all tabs
- `execute_javascript` - Run JS in tabs
- `get_page_content` - Get page text

**Full Setup Guide**: See `CHROME_CONTROL_MCP_SETUP.md`

**Note**: Uses Claude's built-in Chrome extension. No browser extension needed, no DevTools required!

## 🚨 MUST READ - Server Startup Protocol

### How to Start Server (ALWAYS USE THIS)

#### Method 1: Direct Command (if in terminal)
```bash
cd primepath_project
../venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
```

#### Method 2: PowerShell Start-Process (for automation/detached process)
```powershell
powershell -Command "Start-Process cmd -ArgumentList '/k', 'cd /d C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\primepath_project && ..\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite'"
```
**Note**: Method 2 opens a new command window and keeps server running independently

### SUCCESS INDICATORS (DO NOT PANIC)
✅ **"Watching for file changes with StatReloader"** = SERVER IS RUNNING
✅ **"Starting development server at http://127.0.0.1:8000/"** = SERVER IS RUNNING  
✅ **Terminal hangs/timeout after above messages** = NORMAL BEHAVIOR (server is running)

### How to Verify Server is Actually Running
```bash
curl -I http://127.0.0.1:8000/
```
If you get `HTTP/1.1 200 OK`, the server is working. Browser issues are separate.

## 🔴 CRITICAL WARNINGS - AVOID THESE MISTAKES

### DO NOT:
1. ❌ Add debug systems to fix simple problems
2. ❌ Create multiple startup scripts
3. ❌ Modify core Django settings for UI issues
4. ❌ Assume "command timeout" means failure
5. ❌ Trust browser "connection refused" without curl test
6. ❌ Add complexity to fix complexity

### Common False Alarms
- **"Command timed out after 5s"** - If after "StatReloader", this is SUCCESS not failure
- **Browser shows "Connection Refused"** - Often just cache, server is actually running
- **"Could not find platform independent libraries"** - Warning only, ignore it

## 📋 Standard Operating Procedures

### When Browser Shows "Connection Refused"
1. **DO NOT RESTART SERVER**
2. Run: `curl -I http://127.0.0.1:8000/`
3. If curl works → Browser problem (clear cache, use incognito)
4. If curl fails → Check if Python process exists
5. Only restart server if curl actually fails

### Before Making ANY Changes
```bash
git add -A
git commit -m "CHECKPOINT: Before [describe change]"
```

### If Things Break
```bash
git reset --hard HEAD  # Return to last checkpoint
```

## ⏰ MANDATORY BACKUP PROTOCOL - EVERY HOUR

### Create Hourly Backups (YES, this is 'commit')
```bash
git add -A
git commit -m "HOURLY BACKUP: [current time]"
```

**REMINDER**: Set a timer for every hour of active development
- Even if "nothing seems broken"
- Even if "just small changes"
- ESPECIALLY when everything is working fine

### Why Hourly?
- Today's session had 4+ hours of fixes that made things worse
- Could have reverted to any hourly checkpoint
- Git commits = Time machine for your code

### Quick Backup Command (Use This Every Hour)
```bash
git add -A && git commit -m "HOURLY BACKUP: $(date '+%Y-%m-%d %H:%M')"
```

**YES, 'git commit' = 'save backup'** 
- `git add -A` = Stage all changes
- `git commit` = Create permanent backup point
- You can always return to any commit later

## 🛠️ Quick Diagnostics

### Check Server Health
```bash
# Is server responding?
curl -I http://127.0.0.1:8000/

# Is Python running?
tasklist | findstr python

# Kill all Python (if needed)
taskkill /F /IM python.exe
```

## 📁 Project Structure Notes

### Key Paths
- Virtual Environment: `C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\venv\`
- Django Project: `C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\primepath_project\`
- Settings File: `primepath_project\primepath_project\settings_sqlite.py`
- Database: `primepath_project\db.sqlite3`

### Python Version
- Python 3.13.5 (in venv)
- Django 5.0.1

## 🔄 Recovery Procedures

### Nuclear Reset (Last Resort)
```bash
# Go back to last known good state
git reset --hard 557b99d  # Aug 5 backup

# Clear everything and restart
taskkill /F /IM python.exe
cd primepath_project
../venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
```

## 📝 Lessons Learned

### From Aug 6, 2025 Session
1. **Problem**: Added debug system to fix notifications → Created JavaScript errors
2. **Lesson**: Simple problems need simple solutions
3. **Problem**: Multiple server restart attempts when server was actually running
4. **Lesson**: Always verify with curl before assuming server broken
5. **Problem**: Browser cache showed errors even after fixes
6. **Lesson**: Browser state ≠ Server state

## ✅ Testing Checklist

Before assuming anything is broken:
- [ ] Run curl test
- [ ] Check incognito browser
- [ ] Look for "StatReloader" message
- [ ] Check if Python process exists
- [ ] Clear browser cache
- [ ] Try different browser

## 🚦 Three Golden Rules

1. **"Watching for file changes with StatReloader" = SUCCESS**
2. **Always test with curl before restarting server**
3. **One problem → One fix → One test → One commit**

## 📊 Known Working Commands

These commands are tested and work:
```bash
# Start server
cd primepath_project && ../venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite

# Check Django
../venv/Scripts/python.exe -c "import django; print(django.get_version())"

# Run migrations
../venv/Scripts/python.exe manage.py migrate --settings=primepath_project.settings_sqlite

# Collect static files
../venv/Scripts/python.exe manage.py collectstatic --noinput --settings=primepath_project.settings_sqlite
```

## 🔴 REMEMBER
**Server timeout after "StatReloader" is SUCCESS, not failure!**

## 📚 CURRICULUM STRUCTURE - CRITICAL REFERENCE

### COMPLETE CURRICULUM HIERARCHY (44 Total Levels)

**PRIME CORE** (4 subprograms × 3 levels = 12 levels)
- CORE Phonics Level 1, Level 2, Level 3
- CORE Sigma Level 1, Level 2, Level 3  
- CORE Elite Level 1, Level 2, Level 3
- CORE Pro Level 1, Level 2, Level 3

**PRIME ASCENT** (4 subprograms × 3 levels = 12 levels)
- ASCENT Nova Level 1, Level 2, Level 3
- ASCENT Drive Level 1, Level 2, Level 3
- ASCENT Pro Level 1, Level 2, Level 3
- (Missing one subprogram in original list - should be 4 total)

**PRIME EDGE** (4 subprograms × 3 levels = 12 levels)
- EDGE Spark Level 1, Level 2, Level 3
- EDGE Rise Level 1, Level 2, Level 3
- EDGE Pursuit Level 1, Level 2, Level 3
- EDGE Pro Level 1, Level 2, Level 3

**PRIME PINNACLE** (4 subprograms × 2 levels = 8 levels)
- PINNACLE Vision Level 1, Level 2
- PINNACLE Endeavor Level 1, Level 2
- PINNACLE Success Level 1, Level 2
- PINNACLE Pro Level 1, Level 2

### NAMING CONVENTION
Format: `[PROGRAM] [SubProgram] Level [Number]`
- Example: "CORE Phonics Level 1" NOT "PHONICS Level 1"
- Example: "PINNACLE Vision Level 1" NOT "PINNACLE Level 1"

### KEY POINTS
- Every program has a "Pro" track as the highest subprogram
- PINNACLE has only 2 levels per subprogram (advanced tier)
- All other programs have 3 levels per subprogram
- NO standalone "PHONICS" - always "CORE Phonics"
- Total of 44 curriculum levels across all programs

## 🧹 Test Data Cleanup & Maintenance

### QA-Generated Test SubPrograms
**Issue**: Test/QA activities create test subprograms in the database that pollute the curriculum structure.

**Known Test SubPrograms to Filter**:
- Test SubProgram
- SHORT Answer Test SubProgram
- Comprehensive Test SubProgram
- Management Test SubProgram
- SHORT Display Test SubProgram
- Submit Test SubProgram
- Final Test SubProgram

**Solution Implemented** (August 12, 2025):
- Created `core/curriculum_constants.py` with valid curriculum whitelist
- Updated `placement_rules` view to filter test subprograms
- Added comprehensive console logging for debugging
- Test subprograms remain in database but are filtered from display

**Maintenance Required**:
```bash
# Check what test data exists
python test_curriculum_filtering.py

# Clean test subprograms from database (when management command is available)
python manage.py clean_test_subprograms --dry-run
python manage.py clean_test_subprograms --force
```

**Prevention**:
- Always prefix test data with "TEST_" or "QA_"
- Use fixtures for test data instead of production database
- Run cleanup regularly (weekly recommended)
- Monitor console logs for filtered items

## 📚 Major Fixes Documentation

### 1. Upload Exam Fix
**File**: `UPLOAD_EXAM_WORKING_STATE_V1_2025_08_06.md`
**Issue**: File upload functionality for exams
**Status**: ✅ Resolved

### 2. Gap Between Sections Fix
**File**: `GAP_FIX_COMPLETE_DOCUMENTATION.md`
**Issue**: Large gap between PDF Preview and Answer Keys sections
**Root Cause**: Fixed heights on containers (not spacing between them!)
**Status**: ✅ Resolved (August 7, 2025)

### 3. Student Test Navigation & Answer Selection Fix
**Date**: August 7, 2025
**Issue**: Navigation buttons (1-20) and answer selection not working
**Root Cause**: Double JSON encoding - Django view using `json.dumps()` AND template using `json_script` filter
**Error**: "Cannot read properties of undefined (reading 'id')" at APP_CONFIG.session.id
**Solution**: 
- Pass dict from view instead of JSON string (views.py line 117)
- Add defensive programming with try-catch and null checks
- Fixed initialization order (modules available before navigation init)
**Status**: ✅ Resolved

### 4. Chrome MCP Server Setup
**Date**: August 11, 2025
**File**: `chrome-mcp-troubleshooting-log.md`
**Issue**: Chrome MCP tools not connecting despite installation
**Solution**: Fixed native messaging host registration and permissions
**Status**: ✅ Resolved and documented

## 🏗️ Current Architecture

### Template System
- **V2 Templates**: ENABLED via `USE_V2_TEMPLATES` feature flag
- **Template**: `student_test_v2.html` (modular with extracted CSS)
- **Components**: Separate component templates in `components/placement_test/`

### JavaScript Module System
```
Initialization Order:
1. APP_CONFIG setup (with error handling)
2. PDF Viewer
3. Timer
4. Audio Player
5. Answer Manager (with defensive checks)
6. Global instance registration
7. Navigation Module (after dependencies available)
8. Event Delegation
```

### Data Flow
```
Django View (dict) → Template (json_script filter) → JavaScript (JSON.parse) → APP_CONFIG
```

### Key Dependencies
- **Navigation Module**: Depends on answerManager and audioPlayer
- **Answer Manager**: Requires session.id and exam.id from APP_CONFIG
- **Event Delegation**: Central event handling system for all DOM interactions

## ⚠️ Common Pitfalls to Avoid

### JavaScript Errors
1. **Always check console first** - "Cannot read properties of undefined" means data issue, not UI issue
2. **Don't double-encode JSON** - Use either Django's json.dumps() OR template's json_script, not both
3. **Initialize in correct order** - Dependencies must be available before dependent modules

### Event Handling
1. **Use onChange for inputs** - Don't add both onChange AND onClick handlers for same elements
2. **Navigation module handles its own events** - Don't duplicate in template
3. **Event delegation pattern** - Use `self` for module reference, `this` for DOM element

## 🏗️ Backend Modularization (Phase 3) - August 8, 2025

### Completed Successfully
**Status**: ✅ All functionality preserved, no breaking changes

#### What Was Added
1. **Service Layer** (core/services/)
   - CurriculumService: Curriculum and placement rule operations
   - SchoolService: School management operations
   - TeacherService: Teacher management operations

2. **Common Mixins** (common/mixins.py)
   - AjaxResponseMixin: Standardized JSON responses
   - TeacherRequiredMixin: Authentication enforcement
   - RequestValidationMixin: Data validation helpers
   - PaginationMixin, CacheMixin, LoggingMixin

3. **Base View Classes** (common/views/base.py)
   - BaseAPIView: For API endpoints
   - BaseTemplateView: For page rendering
   - BaseFormView: For form handling

#### How to Use
```python
# Import services
from core.services import CurriculumService

# Use in views
programs = CurriculumService.get_programs_with_hierarchy()

# Use mixins
class MyView(BaseAPIView):
    def get(self, request):
        return self.json_response(data={'status': 'ok'})
```

#### Test Results
- 10/10 tests passing
- No functionality broken
- Full backward compatibility

---
*Last Updated: August 8, 2025*
*This file should be read at the start of every Claude session*