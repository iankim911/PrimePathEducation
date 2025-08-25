#\!/bin/bash

# Kill any existing Django server processes
echo "Stopping any existing Django servers..."
pkill -f "manage.py runserver" 2>/dev/null

# Wait a moment for processes to stop
sleep 2

# Navigate to project directory
cd /Users/ian/Desktop/VIBECODE/PrimePath/primepath_project

# Start the server with proper settings
echo "Starting Django server..."
../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite

# Note: If the server stops, it will show why in the terminal
