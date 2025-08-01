@echo off
echo ============================================
echo    DJANGO DEBUG - WINDOW WILL STAY OPEN
echo ============================================
echo.

:: Keep window open on error
if not defined IS_MINIMIZED set IS_MINIMIZED=1 && start "Django Debug" /min "%~dpnx0" %* && exit

:: Show current directory
echo Current directory:
echo %CD%
echo.

:: Change to project directory
C:
cd "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\primepath_project"
echo Changed to:
echo %CD%
echo.

:: Show Python location
echo Python location:
where python 2>&1
echo.

:: Try python command
echo Testing Python...
python --version 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Python command failed!
    echo Trying py command...
    py --version 2>&1
)
echo.

:: Check if manage.py exists
echo Checking for manage.py...
if exist manage.py (
    echo manage.py FOUND
) else (
    echo ERROR: manage.py NOT FOUND in %CD%
    echo.
    echo Contents of current directory:
    dir /b
)
echo.

:: Try to import Django
echo Testing Django import...
python -c "import django; print('Django imported successfully')" 2>&1
echo.

:: Try to run server with full error output
echo ============================================
echo Attempting to start Django server...
echo ============================================
python manage.py runserver 2>&1
echo.

:: If that failed, try py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo First attempt failed, trying with py command...
    py manage.py runserver 2>&1
)

echo.
echo ============================================
echo Script finished. Press any key to close...
echo ============================================
pause >nul