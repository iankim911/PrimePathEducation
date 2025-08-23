#!/bin/bash

# ============================================================================
# STABLE DJANGO SERVER STARTER
# Fixes "StatReloader exited unexpectedly" errors
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/../venv"
PORT=8000
SETTINGS="primepath_project.settings_sqlite"

echo -e "${CYAN}${BOLD}============================================${NC}"
echo -e "${CYAN}${BOLD}   PRIMEPATH STABLE SERVER LAUNCHER${NC}"
echo -e "${CYAN}${BOLD}============================================${NC}"

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%H:%M:%S')] ${message}${NC}"
}

# Function to check if port is in use
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to kill existing Django processes
cleanup_processes() {
    print_message "$YELLOW" "Cleaning up existing Django processes..."
    
    # Kill Python processes running manage.py
    pkill -f "manage.py runserver" 2>/dev/null
    
    # Kill processes on port 8000
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    
    sleep 2
}

# Function to increase file descriptor limits (fixes StatReloader)
increase_limits() {
    print_message "$BLUE" "Setting file descriptor limits..."
    
    # Increase ulimit for current session
    ulimit -n 10240 2>/dev/null
    
    # For macOS, temporarily increase limits
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sudo launchctl limit maxfiles 65536 200000 2>/dev/null
        print_message "$GREEN" "File limits increased for macOS"
    fi
}

# Function to run server with monitoring
run_server() {
    local attempt=1
    local max_attempts=10
    
    while [ $attempt -le $max_attempts ]; do
        print_message "$GREEN" "Starting Django server (Attempt #$attempt)..."
        
        # Check and clean port if needed
        if check_port; then
            print_message "$YELLOW" "Port $PORT is in use. Cleaning up..."
            cleanup_processes
        fi
        
        # Activate virtual environment and run server
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            # Windows
            PYTHON="$VENV_DIR/Scripts/python.exe"
        else
            # macOS/Linux
            PYTHON="$VENV_DIR/bin/python"
        fi
        
        print_message "$CYAN" "URL: http://127.0.0.1:$PORT/"
        print_message "$YELLOW" "Press Ctrl+C to stop"
        echo ""
        
        # Run server with --noreload to avoid StatReloader issues
        $PYTHON "$PROJECT_DIR/manage.py" runserver 127.0.0.1:$PORT \
            --settings=$SETTINGS \
            --noreload \
            2>&1 | while IFS= read -r line; do
                # Color code output
                if [[ "$line" == *"Starting development server"* ]]; then
                    echo -e "${GREEN}$line${NC}"
                elif [[ "$line" == *"Quit the server"* ]]; then
                    echo -e "${YELLOW}$line${NC}"
                elif [[ "$line" == *"Error"* ]] || [[ "$line" == *"ERROR"* ]]; then
                    echo -e "${RED}$line${NC}"
                elif [[ "$line" == *"Warning"* ]] || [[ "$line" == *"WARNING"* ]]; then
                    echo -e "${YELLOW}$line${NC}"
                else
                    echo "$line"
                fi
            done
        
        EXIT_CODE=$?
        
        if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 130 ]; then
            # 0 = normal exit, 130 = Ctrl+C
            print_message "$GREEN" "Server stopped normally"
            break
        else
            print_message "$RED" "Server crashed with exit code $EXIT_CODE"
            
            if [ $attempt -lt $max_attempts ]; then
                print_message "$YELLOW" "Restarting in 3 seconds..."
                sleep 3
                attempt=$((attempt + 1))
            else
                print_message "$RED" "Maximum restart attempts reached. Exiting."
                exit 1
            fi
        fi
    done
}

# Main execution
main() {
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Set environment variables
    export DJANGO_SETTINGS_MODULE=$SETTINGS
    export PYTHONUNBUFFERED=1
    
    # Increase file limits
    increase_limits
    
    # Initial cleanup
    cleanup_processes
    
    # Run server with auto-restart
    run_server
}

# Handle Ctrl+C gracefully
trap 'print_message "$YELLOW" "Shutting down server..."; cleanup_processes; exit 0' INT TERM

# Run main function
main