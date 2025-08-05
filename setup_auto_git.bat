@echo off
REM Setup script for automated git commits every 3 hours
REM Run this as Administrator to set up the scheduled task

set PROJECT_PATH=%~dp0
set SCRIPT_PATH=%PROJECT_PATH%auto_git_commit.ps1

echo Setting up automated git commits every 3 hours for PrimePath project...
echo Project Path: %PROJECT_PATH%
echo Script Path: %SCRIPT_PATH%

REM Create scheduled task to run every 3 hours
schtasks /create /tn "PrimePath Auto Git Commit" /tr "powershell.exe -ExecutionPolicy Bypass -File \"%SCRIPT_PATH%\"" /sc hourly /mo 3 /st 09:00 /f

if %errorlevel% equ 0 (
    echo.
    echo ✅ Successfully created scheduled task "PrimePath Auto Git Commit"
    echo    - Runs every 3 hours starting at 9:00 AM
    echo    - Next runs: 9:00 AM, 12:00 PM, 3:00 PM, 6:00 PM, 9:00 PM, 12:00 AM, 3:00 AM, 6:00 AM
    echo.
    echo To view the task: schtasks /query /tn "PrimePath Auto Git Commit"
    echo To delete the task: schtasks /delete /tn "PrimePath Auto Git Commit" /f
    echo.
    echo Log file will be created at: %PROJECT_PATH%auto_git.log
) else (
    echo.
    echo ❌ Failed to create scheduled task. Please run as Administrator.
    echo.
)

pause