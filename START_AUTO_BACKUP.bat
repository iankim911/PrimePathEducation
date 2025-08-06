@echo off
echo ====================================
echo     AUTO-BACKUP SYSTEM
echo ====================================
echo.
echo This will save your work every hour
echo Press Ctrl+C to stop
echo.

:backup_loop
echo [%date% %time%] Creating backup...

REM Add all changes
git add -A 2>nul

REM Create commit
git commit -m "AUTO-BACKUP: %date% %time%" >nul 2>&1

if %errorlevel% == 0 (
    echo [%date% %time%] BACKUP SAVED!
    echo.
) else (
    echo [%date% %time%] No changes to backup
    echo.
)

echo Waiting 1 hour for next backup...
echo Press Ctrl+C to stop
echo ====================================

REM Wait 1 hour (3600 seconds)
timeout /t 3600 /nobreak >nul

goto backup_loop