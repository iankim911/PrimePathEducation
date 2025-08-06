@echo off
cd /d "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\primepath_project"
set DJANGO_SETTINGS_MODULE=primepath_project.settings_sqlite
echo Starting PrimePath Server with fresh settings...
"..\venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000 --noreload
pause