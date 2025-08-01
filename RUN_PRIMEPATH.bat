@echo off
title PrimePath Server
cls
echo =====================================
echo         PrimePath Server Startup
echo =====================================
echo.

cd /d "%~dp0"

REM Check if we're in the right directory
if not exist "primepath_project\manage.py" (
    echo ERROR: Cannot find primepath_project\manage.py
    echo Please run this script from the PrimePath_ directory
    pause
    exit /b 1
)

cd primepath_project

REM Check if virtual environment exists
if exist "Scripts\activate.bat" (
    echo Found virtual environment, activating...
    call Scripts\activate.bat
    echo Virtual environment activated!
    echo.
) else (
    echo No virtual environment found, using system Python
    echo.
)

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python from https://www.python.org/
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo Python found!
%PYTHON_CMD% --version
echo.

REM Check Django installation
echo Checking Django installation...
%PYTHON_CMD% -c "import django; print(f'Django {django.get_version()} is installed')" 2>nul
if errorlevel 1 (
    echo Django not found! Installing Django...
    %PYTHON_CMD% -m pip install Django==5.0.1
    if errorlevel 1 (
        echo ERROR: Failed to install Django
        echo Try running: pip install Django==5.0.1
        pause
        exit /b 1
    )
)
echo.

REM Check database
if not exist "db.sqlite3" (
    echo Database not found. Creating database...
    %PYTHON_CMD% manage.py migrate
    echo.
    echo Loading initial data...
    %PYTHON_CMD% manage.py loaddata core/fixtures/curriculum_data.json
    %PYTHON_CMD% manage.py populate_curriculum
    echo.
)

REM Check for migrations
echo Checking for pending migrations...
%PYTHON_CMD% manage.py migrate --check >nul 2>&1
if errorlevel 1 (
    echo Running migrations...
    %PYTHON_CMD% manage.py migrate
    echo.
)

REM Start the server
echo =====================================
echo Starting Django Development Server...
echo =====================================
echo.
echo Server will run at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo Opening browser...
start http://localhost:8000
echo.

%PYTHON_CMD% manage.py runserver