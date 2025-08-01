@echo off
echo Checking Django Server Status...
echo.

:: Check if port 8000 is in use
netstat -an | find ":8000" | find "LISTENING" >nul
if %ERRORLEVEL% == 0 (
    echo [✓] Django server is RUNNING on port 8000
    echo.
    echo You can access it at: http://127.0.0.1:8000
    echo.
    
    :: Show which process is using port 8000
    for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
        echo Process ID: %%a
        for /f "tokens=1" %%p in ('tasklist /FI "PID eq %%a" ^| findstr "py.exe python.exe"') do (
            echo Process Name: %%p
        )
    )
) else (
    echo [X] Django server is NOT running
    echo.
    echo To start it, run: START_SERVER_BACKGROUND.bat
)

echo.
pause