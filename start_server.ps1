Set-Location "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\primepath_project"
$env:DJANGO_SETTINGS_MODULE = "primepath_project.settings_sqlite"
Write-Host "Starting Django server..."
& "..\venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000 --noreload