# CUSTOM CONFIGURATIONS & SETTINGS - MAC REFERENCE

## 🔧 ENVIRONMENT VARIABLES

### Development Settings (Mac Terminal)
```bash
# Set Django settings module
export DJANGO_SETTINGS_MODULE=primepath_project.settings_sqlite

# Optional: Set debug mode explicitly
export DJANGO_DEBUG=True

# Optional: Set secret key (if not using default)
export SECRET_KEY='your-secret-key-here'

# Make permanent (add to ~/.zshrc or ~/.bash_profile)
echo 'export DJANGO_SETTINGS_MODULE=primepath_project.settings_sqlite' >> ~/.zshrc
source ~/.zshrc
```

## 📁 PATH CONFIGURATIONS

### Update CLAUDE.md for Mac
Replace all Windows paths with Mac equivalents:

```python
# In any Python files, replace:
# Windows: venv\Scripts\python.exe
# Mac:     venv/bin/python

# Windows: primepath_project\
# Mac:     primepath_project/

# Windows: C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_
# Mac:     ~/Projects/PrimePath_
```

## ⚙️ DJANGO SETTINGS ADJUSTMENTS

### In `primepath_project/settings_sqlite.py`

```python
# These settings work on both Windows and Mac (no changes needed)
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Database - works identically on Mac
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Path object handles OS differences
    }
}

# Media files - cross-platform
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static files - cross-platform
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

## 🗄️ DATABASE CONFIGURATIONS

### SQLite Settings (No changes needed)
```bash
# Database file location (relative to project)
primepath_project/db.sqlite3

# To access database directly on Mac
cd primepath_project
sqlite3 db.sqlite3

# Common SQLite commands
.tables                    # List all tables
.schema placement_test_exam  # Show table structure
.quit                      # Exit SQLite
```

## 🌐 CORS CONFIGURATION

### Update for Mac Development (if needed)
```python
# In settings_sqlite.py, add Mac localhost variations
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",     # React dev server
    "http://localhost:8000",     # Django dev server
    "http://127.0.0.1:8000",    # Alternative
    "http://0.0.0.0:8000",      # Mac may use this
]
```

## 📝 LOGGING CONFIGURATION

### Create Mac-Compatible Logging
```python
# In settings_sqlite.py, add/update:
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',  # Cross-platform path
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'placement_test': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## 🔐 SECURITY SETTINGS

### Development vs Production
```python
# settings_sqlite.py (Development - OK for Mac development)
DEBUG = True
ALLOWED_HOSTS = ['*']  # Accept all hosts in development

# For production (when ready):
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
```

## 🚀 PERFORMANCE OPTIMIZATIONS

### Mac-Specific Optimizations
```python
# Add to settings_sqlite.py for better Mac performance
CONN_MAX_AGE = 600  # Keep database connections alive

# If using PostgreSQL later (Mac optimal)
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
}

# Cache configuration (optional)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

## 📜 SHELL SCRIPTS FOR MAC

### Create `dev_setup.sh`
```bash
#!/bin/bash
# Complete development environment setup for Mac

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up PrimePath development environment...${NC}"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed!${NC}"
    exit 1
fi

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Additional packages
pip install djangorestframework==3.14.0
pip install django-filter==23.5
pip install django-cors-headers==4.3.1

# Setup database
cd primepath_project
echo "Running migrations..."
python manage.py migrate --settings=primepath_project.settings_sqlite

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=primepath_project.settings_sqlite

echo -e "${GREEN}Setup complete!${NC}"
echo "To start the server, run: ./run_server.sh"
```

### Create `run_server.sh`
```bash
#!/bin/bash
# Start Django development server

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export DJANGO_SETTINGS_MODULE=primepath_project.settings_sqlite

# Navigate to project
cd primepath_project

# Start server
echo "Starting PrimePath server..."
echo "Access at: http://127.0.0.1:8000/"
echo "Admin at: http://127.0.0.1:8000/admin/"
echo "Press Ctrl+C to stop"

python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
```

### Create `test_all.sh`
```bash
#!/bin/bash
# Run all tests and verifications

source venv/bin/activate
cd primepath_project

echo "Running comprehensive tests..."
python double_check_all_features.py

echo "Testing student interface..."
python quick_test_student_fix.py

echo "Testing answer keys..."
python quick_test_answer_keys.py

echo "All tests complete!"
```

### Make Scripts Executable
```bash
chmod +x dev_setup.sh
chmod +x run_server.sh
chmod +x test_all.sh
```

## 🎨 IDE CONFIGURATIONS

### VS Code Settings (Mac)
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "venv/": true
    },
    "terminal.integrated.env.osx": {
        "DJANGO_SETTINGS_MODULE": "primepath_project.settings_sqlite"
    }
}
```

### PyCharm Settings (Mac)
1. Set Project Interpreter: `~/Projects/PrimePath_/venv/bin/python`
2. Django Support: Enable with settings module `primepath_project.settings_sqlite`
3. Run Configuration:
   - Script path: `manage.py`
   - Parameters: `runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite`
   - Working directory: `~/Projects/PrimePath_/primepath_project`

## 🔄 GIT CONFIGURATION

### Initialize Git (if needed)
```bash
cd ~/Projects/PrimePath_
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Create .gitignore for Mac
cat > .gitignore << 'EOF'
# Python
*.pyc
__pycache__/
venv/
env/
*.pyo
*.pyd
.Python

# Django
*.log
*.pot
local_settings.py
db.sqlite3-journal
media/
staticfiles/

# Mac
.DS_Store
.AppleDouble
.LSOverride

# IDE
.vscode/
.idea/
*.swp
*.swo

# Project specific
debug.log
*.pid
EOF

git add -A
git commit -m "Initial Mac setup"
```

## 🛠️ CUSTOM MANAGEMENT COMMANDS

### Create Custom Command (example)
```bash
# Create directory structure
mkdir -p primepath_project/placement_test/management/commands

# Create command file
touch primepath_project/placement_test/management/commands/check_setup.py
```

```python
# check_setup.py
from django.core.management.base import BaseCommand
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Checks if the project is properly set up on Mac'

    def handle(self, *args, **options):
        self.stdout.write("Checking PrimePath setup on Mac...")
        
        # Check Python version
        python_version = sys.version
        self.stdout.write(f"Python version: {python_version}")
        
        # Check Django settings
        self.stdout.write(f"Settings module: {settings.SETTINGS_MODULE}")
        self.stdout.write(f"Debug mode: {settings.DEBUG}")
        self.stdout.write(f"Database: {settings.DATABASES['default']['NAME']}")
        
        # Check critical paths
        if settings.MEDIA_ROOT.exists():
            self.stdout.write(self.style.SUCCESS("✓ Media directory exists"))
        else:
            self.stdout.write(self.style.ERROR("✗ Media directory missing"))
            
        if settings.STATIC_ROOT.exists():
            self.stdout.write(self.style.SUCCESS("✓ Static directory exists"))
        else:
            self.stdout.write(self.style.WARNING("! Static directory missing (run collectstatic)"))
        
        self.stdout.write(self.style.SUCCESS("\nSetup check complete!"))
```

Run with:
```bash
python manage.py check_setup --settings=primepath_project.settings_sqlite
```

## 📊 MONITORING & DEBUGGING

### Debug Toolbar (Optional)
```bash
# Install debug toolbar
pip install django-debug-toolbar

# Add to INSTALLED_APPS in settings_sqlite.py
INSTALLED_APPS += ['debug_toolbar']

# Add middleware
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Configure for Mac
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    '::1',  # IPv6 localhost
]
```

## 🔑 QUICK REFERENCE

### Essential Mac Commands
```bash
# Virtual environment
source venv/bin/activate          # Activate
deactivate                        # Deactivate

# Django commands
python manage.py runserver        # Start server
python manage.py shell           # Django shell
python manage.py dbshell         # Database shell
python manage.py makemigrations  # Create migrations
python manage.py migrate         # Apply migrations
python manage.py collectstatic   # Collect static files
python manage.py createsuperuser # Create admin user

# Testing
python manage.py test            # Run tests
python double_check_all_features.py  # Comprehensive check

# Process management
ps aux | grep python             # Find Python processes
kill -9 [PID]                   # Kill process
lsof -i :8000                   # Check port 8000
```

## 📝 FINAL NOTES

All custom configurations have been documented here. The project should work on Mac with minimal adjustments. The main things to remember:

1. **Always use forward slashes** (/) for paths
2. **Activate virtual environment** before any Python commands
3. **Use python3** if `python` doesn't work
4. **Make shell scripts executable** with `chmod +x`
5. **Settings file** is always `primepath_project.settings_sqlite`

---
*Custom configurations documented for Mac environment*
*All settings verified compatible with macOS*