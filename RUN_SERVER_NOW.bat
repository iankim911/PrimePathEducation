@echo off
title PrimePath Django Server
echo ============================================
echo         PrimePath Django Server
echo ============================================
echo.

cd /d "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\primepath_project"

echo Starting server on http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

"C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\venv\Scripts\python.exe" manage.py runserver

pause