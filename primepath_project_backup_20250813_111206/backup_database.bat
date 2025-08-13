@echo off
echo Creating database backup...
cd /d "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\primepath_project"
copy db.sqlite3 db_backup_2025_08_02.sqlite3
echo.
echo Backup created successfully as db_backup_2025_08_02.sqlite3
echo.
pause