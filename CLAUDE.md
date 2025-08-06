# PrimePath Project - Critical Knowledge Base

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

---
*Last Updated: August 7, 2025*
*This file should be read at the start of every Claude session*