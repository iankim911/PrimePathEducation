@echo off
cd /d "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\primepath_project"
echo Starting PrimePath Server...
echo.
echo Server will run at: http://127.0.0.1:8000/
echo Press Ctrl+C to stop the server
echo.
"C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000 --noreload --settings=primepath_project.settings_sqlite
pause