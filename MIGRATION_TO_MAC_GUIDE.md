# PrimePath Project - Windows to Mac Migration Guide

## ✅ Pre-Migration Analysis Complete

### Good News! 
Your project is **migration-ready** with minimal changes needed. All dependencies are contained within the project directory.

### Verified Migration Readiness
- ✅ **Database**: SQLite database (`db.sqlite3`) is in project directory
- ✅ **Media Files**: All media stored in `media/` within project
- ✅ **Static Files**: All static files in `static/` and `staticfiles/`
- ✅ **No Hardcoded Paths**: All paths use Django's BASE_DIR (platform-agnostic)
- ✅ **Requirements File**: `requirements.txt` exists with all Python dependencies
- ✅ **Settings**: Uses relative paths throughout

## 📋 Step-by-Step Migration Process

### Step 1: Prepare on Windows (Before Migration)

1. **Create a fresh backup**:
   ```bash
   git add -A
   git commit -m "Pre-migration backup: Windows to Mac"
   ```

2. **Export current database** (optional but recommended):
   ```bash
   cd primepath_project
   python manage.py dumpdata > data_backup.json
   ```

3. **Document current Python version**:
   ```bash
   python --version
   # Note this version - you'll need similar on Mac
   ```

4. **Clean up unnecessary files**:
   ```bash
   # Remove Windows virtual environment (not portable)
   # Remove compiled Python files
   find . -type d -name "__pycache__" -exec rm -rf {} +
   find . -name "*.pyc" -delete
   ```

5. **Create migration ZIP**:
   - Exclude these folders when zipping:
     - `venv/` (Windows virtual environment)
     - `Lib/` (Windows Python libs)
     - `Scripts/` (Windows executables)
     - `serena-env/` (if exists)
     - `__pycache__/` folders
     - `.git/` (if you want fresh git history)

### Step 2: Transfer to Mac

1. **Transfer the ZIP file** via:
   - OneDrive/iCloud
   - USB drive
   - Network transfer
   - Git repository (recommended)

### Step 3: Setup on Mac

1. **Extract project**:
   ```bash
   cd ~/Projects  # or your preferred location
   unzip PrimePath.zip
   cd PrimePath_
   ```

2. **Install Python** (if not already installed):
   ```bash
   # Check if Python is installed
   python3 --version
   
   # If not, install via Homebrew
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install python@3.11  # or your preferred version
   ```

3. **Create new virtual environment**:
   ```bash
   # Create fresh virtual environment
   python3 -m venv venv
   
   # Activate it
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   # Upgrade pip first
   pip install --upgrade pip
   
   # Install project dependencies
   pip install -r requirements.txt
   
   # If you need additional packages from the complete list:
   pip install djangorestframework==3.14.0
   pip install django-filter==23.5
   pip install django-cors-headers==4.3.1
   pip install celery==5.3.4
   pip install redis==5.0.1
   ```

5. **Navigate to Django project**:
   ```bash
   cd primepath_project
   ```

6. **Run migrations** (ensure database is up to date):
   ```bash
   python manage.py migrate --settings=primepath_project.settings_sqlite
   ```

7. **Collect static files**:
   ```bash
   python manage.py collectstatic --noinput --settings=primepath_project.settings_sqlite
   ```

8. **Create superuser** (if needed):
   ```bash
   python manage.py createsuperuser --settings=primepath_project.settings_sqlite
   ```

9. **Test the server**:
   ```bash
   python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
   ```

### Step 4: Verify Everything Works

1. **Check server starts**:
   - Visit http://127.0.0.1:8000/
   - Should see your application

2. **Test key features**:
   - Student registration
   - Exam management
   - Test taking interface
   - Admin panel (http://127.0.0.1:8000/admin/)

3. **Run verification script**:
   ```bash
   python double_check_all_features.py
   ```

## 🔄 Platform-Specific Adjustments

### File Path Separators
- **Windows**: Uses `\` (backslash)
- **Mac/Linux**: Uses `/` (forward slash)
- **Django**: Handles this automatically with `os.path.join()` or `pathlib`

### Command Differences

| Task | Windows | Mac |
|------|---------|-----|
| Activate venv | `venv\Scripts\activate` | `source venv/bin/activate` |
| Python command | `python` or `py` | `python3` |
| List files | `dir` | `ls` |
| Clear screen | `cls` | `clear` |
| Environment vars | `set VAR=value` | `export VAR=value` |

### Script Conversions

Your `.bat` files need Mac equivalents:

**Windows `run_server.bat`:**
```batch
cd primepath_project
..\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
```

**Mac `run_server.sh`:**
```bash
#!/bin/bash
cd primepath_project
../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
```

Make it executable:
```bash
chmod +x run_server.sh
```

## 📝 Important Notes

### What WILL Transfer
- ✅ SQLite database (`db.sqlite3`)
- ✅ All Python source code
- ✅ HTML/CSS/JavaScript files
- ✅ Media files (PDFs, audio files)
- ✅ Static assets
- ✅ Django migrations
- ✅ Configuration files

### What WON'T Transfer
- ❌ Windows virtual environment (`venv/`)
- ❌ Compiled Python files (`*.pyc`)
- ❌ Windows-specific executables (`*.exe`, `*.bat`)
- ❌ Python cache folders (`__pycache__/`)

### What Needs Recreation
- 🔄 Virtual environment
- 🔄 Shell scripts (convert from `.bat` to `.sh`)
- 🔄 Git configuration (if needed)

## 🚀 Quick Start Commands for Mac

Once setup is complete, use these commands:

```bash
# Activate virtual environment
source ~/Projects/PrimePath_/venv/bin/activate

# Navigate to project
cd ~/Projects/PrimePath_/primepath_project

# Start development server
python manage.py runserver --settings=primepath_project.settings_sqlite

# Run tests
python double_check_all_features.py

# Create backup
git add -A && git commit -m "Backup: $(date '+%Y-%m-%d %H:%M')"
```

## 🛠️ Troubleshooting

### Issue: "Module not found" errors
**Solution**: Ensure virtual environment is activated and all packages are installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database errors
**Solution**: Run migrations
```bash
python manage.py migrate --settings=primepath_project.settings_sqlite
```

### Issue: Static files not loading
**Solution**: Collect static files
```bash
python manage.py collectstatic --noinput --settings=primepath_project.settings_sqlite
```

### Issue: Permission denied on scripts
**Solution**: Make scripts executable
```bash
chmod +x script_name.sh
```

## 📱 Using with Claude on Mac

The CLAUDE.md file will work identically on Mac. The only adjustments needed:
- Replace `venv\Scripts\python.exe` with `venv/bin/python`
- Replace backslashes with forward slashes in paths
- Use `source` instead of `call` for activation scripts

## ✅ Migration Checklist

Before migration:
- [ ] Backup current database
- [ ] Commit all changes to git
- [ ] Document current Python version
- [ ] Note any custom configurations

After migration:
- [ ] Python installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Database migrated
- [ ] Static files collected
- [ ] Server runs successfully
- [ ] All features tested
- [ ] Shell scripts created

## 🎉 Success Indicators

You'll know the migration is successful when:
1. Server starts without errors
2. You can access the application at http://127.0.0.1:8000/
3. All features work as expected
4. The verification script shows 100% pass rate

---
*Migration guide created: August 8, 2025*
*Your project is well-structured for cross-platform compatibility!*