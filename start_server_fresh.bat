@echo off
cd primepath_project
echo.
echo ====================================
echo Starting PrimePath Server (Fresh)
echo ====================================
echo.
echo This will clear cache and start with fresh static files
echo.

REM Kill any existing Python processes
taskkill /F /IM python.exe 2>nul
echo Cleared any existing Python processes

REM Collect static files
echo.
echo Collecting static files...
..\venv\Scripts\python.exe manage.py collectstatic --noinput --settings=primepath_project.settings_sqlite
echo Static files collected!

REM Start server
echo.
echo Starting Django server...
echo Server will run at: http://127.0.0.1:8000/
echo.
echo IMPORTANT: Clear your browser cache (Ctrl+F5) to see the JavaScript fixes!
echo.
..\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload --settings=primepath_project.settings_sqlite