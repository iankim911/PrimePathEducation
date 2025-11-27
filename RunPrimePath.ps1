# PrimePath PowerShell Startup Script

Write-Host "=========================================" -ForegroundColor Green
Write-Host "     PrimePath Server Startup" -ForegroundColor Green  
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Set location to script directory
Set-Location $PSScriptRoot
Set-Location "primepath_project"

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonCmd = $null

# Try py command first
try {
    $pyVersion = & py --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $pythonCmd = "py"
        Write-Host "Found Python: $pyVersion" -ForegroundColor Green
    }
} catch {}

# Try python command
if (-not $pythonCmd) {
    try {
        $pythonVersion = & python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            # Test if it's real Python or MS Store stub
            $testOutput = & python -c "print('test')" 2>$null
            if ($LASTEXITCODE -eq 0) {
                $pythonCmd = "python"
                Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
            }
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "ERROR: Python is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# Install Django if needed
Write-Host ""
Write-Host "Checking Django..." -ForegroundColor Yellow
$djangoCheck = & $pythonCmd -c "import django; print(django.get_version())" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Django..." -ForegroundColor Yellow
    & $pythonCmd -m pip install Django==5.0.1
}

# Check database
Write-Host ""
Write-Host "Checking database..." -ForegroundColor Yellow
if (-not (Test-Path "db.sqlite3")) {
    Write-Host "Creating database..." -ForegroundColor Yellow
    & $pythonCmd manage.py migrate
}

# Start server
Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Starting server at http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Open browser
Start-Process "http://localhost:8000"

# Run server
& $pythonCmd manage.py runserver