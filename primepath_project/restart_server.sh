#!/bin/bash

# Server restart script for multiple short answer fix
echo "========================================"
echo "RESTARTING SERVER WITH CACHE CLEAR"
echo "========================================"

# Kill any existing Python processes
echo "\nStopping any existing servers..."
pkill -f "python.*manage.py.*runserver" 2>/dev/null
sleep 2

# Clear Python cache (if permissions allow)
echo "\nAttempting to clear Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || echo "Note: Some cache files could not be removed"

# Touch template files to force reload
echo "\nForcing template reload..."
touch placement_test/templatetags/__init__.py
touch placement_test/templatetags/grade_tags.py
touch templates/components/placement_test/question_panel.html

# Start the server
echo "\nStarting Django development server..."
echo "Server will be available at: http://127.0.0.1:8000/"
echo "\n⚠️  IMPORTANT: Clear your browser cache (Cmd+Shift+R) or use incognito mode!"
echo ""

../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite