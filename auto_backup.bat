@echo off
echo === AUTO-BACKUP SYSTEM RUNNING ===
echo This will automatically commit your changes every hour
echo Press Ctrl+C to stop
echo.

:loop
echo.
echo [%date% %time%] Creating automatic backup...
git add -A
git commit -m "AUTO-BACKUP: %date% %time%" 2>nul
if %errorlevel% == 0 (
    echo [%date% %time%] Backup created successfully!
) else (
    echo [%date% %time%] No changes to backup
)

echo Next backup in 1 hour...
echo.

REM Wait for 3600 seconds (1 hour)
timeout /t 3600 /nobreak > nul

goto loop