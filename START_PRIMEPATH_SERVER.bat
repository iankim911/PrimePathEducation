@echo off
echo ====================================================
echo    PrimePath Django Server Starter
echo ====================================================
echo.

echo 🔧 Setting up environment...
cd /d "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\primepath_project"
set DJANGO_SETTINGS_MODULE=primepath_project.settings_sqlite

echo 📁 Current Directory: %CD%
echo ⚙️  Django Settings: %DJANGO_SETTINGS_MODULE%
echo.

echo 🧪 Testing Django installation...
"..\venv\Scripts\python.exe" manage.py --version
if errorlevel 1 (
    echo ❌ Django test failed!
    pause
    exit /b 1
)

echo.
echo 🔍 Running system checks...
"..\venv\Scripts\python.exe" manage.py check
if errorlevel 1 (
    echo ❌ System check failed!
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Django Development Server...
echo 📡 Server will be available at: http://127.0.0.1:8000
echo 🔗 Upload Page: http://127.0.0.1:8000/api/placement/exams/create/
echo 🛑 Press Ctrl+C to stop the server
echo.
echo ====================================================

"..\venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000 --noreload

echo.
echo 🛑 Server stopped.
pause