#!/usr/bin/env python
"""
Stable Django Development Server Runner
Handles StatReloader crashes and automatically restarts the server

This script solves the "StatReloader exited unexpectedly" error by:
1. Using a more stable reloader
2. Automatically restarting on crashes
3. Providing better error handling
"""

import os
import sys
import time
import subprocess
import signal
import threading
from datetime import datetime

# Colors for console output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(message, color=Colors.OKGREEN):
    """Print colored message to console"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{color}[{timestamp}] {message}{Colors.ENDC}")

def check_port_in_use(port=8000):
    """Check if port is already in use"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def kill_existing_django_processes():
    """Kill any existing Django processes"""
    try:
        # Kill Python processes running manage.py
        subprocess.run(['pkill', '-f', 'manage.py runserver'], capture_output=True)
        time.sleep(1)
    except:
        pass

def run_server_with_auto_restart():
    """Run Django server with automatic restart on failure"""
    
    # Set up paths
    project_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_dir, '..', 'venv', 'Scripts', 'python.exe')
    
    # Use unix-style path if on Mac/Linux
    if not os.path.exists(venv_python):
        venv_python = os.path.join(project_dir, '..', 'venv', 'bin', 'python')
    
    manage_py = os.path.join(project_dir, 'manage.py')
    
    # Server command with --noreload to avoid StatReloader issues
    cmd = [
        venv_python,
        manage_py,
        'runserver',
        '127.0.0.1:8000',
        '--settings=primepath_project.settings_sqlite',
        '--noreload'  # Disable auto-reload to prevent StatReloader crashes
    ]
    
    restart_count = 0
    max_quick_restarts = 5
    quick_restart_times = []
    
    print_colored("=" * 60, Colors.HEADER)
    print_colored("STABLE DJANGO SERVER RUNNER", Colors.HEADER)
    print_colored("=" * 60, Colors.HEADER)
    print_colored(f"Project: {project_dir}", Colors.OKCYAN)
    print_colored(f"Python: {venv_python}", Colors.OKCYAN)
    print_colored("Auto-reload: DISABLED (for stability)", Colors.WARNING)
    print_colored("Auto-restart: ENABLED", Colors.OKGREEN)
    print_colored("=" * 60, Colors.HEADER)
    
    while True:
        try:
            # Check for rapid restart loop
            current_time = time.time()
            quick_restart_times = [t for t in quick_restart_times if current_time - t < 60]
            
            if len(quick_restart_times) >= max_quick_restarts:
                print_colored("Too many quick restarts! Waiting 30 seconds...", Colors.FAIL)
                time.sleep(30)
                quick_restart_times = []
            
            # Kill any existing processes
            if restart_count > 0:
                print_colored("Cleaning up old processes...", Colors.WARNING)
                kill_existing_django_processes()
                time.sleep(2)
            
            # Check if port is in use
            if check_port_in_use(8000):
                print_colored("Port 8000 is in use. Attempting to free it...", Colors.WARNING)
                kill_existing_django_processes()
                time.sleep(2)
                
                if check_port_in_use(8000):
                    print_colored("Port 8000 still in use! Please free it manually.", Colors.FAIL)
                    print_colored("Try: lsof -i :8000 | grep LISTEN", Colors.WARNING)
                    time.sleep(5)
                    continue
            
            # Start server
            restart_count += 1
            if restart_count > 1:
                print_colored(f"\n🔄 Restart attempt #{restart_count}", Colors.WARNING)
                quick_restart_times.append(current_time)
            
            print_colored("\n🚀 Starting Django development server...", Colors.OKGREEN)
            print_colored("URL: http://127.0.0.1:8000/", Colors.OKCYAN)
            print_colored("Press Ctrl+C to stop\n", Colors.WARNING)
            
            # Run the server
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor output
            server_started = False
            for line in process.stdout:
                # Color code the output
                if 'Watching for file changes' in line:
                    print_colored(line.strip(), Colors.OKGREEN)
                    server_started = True
                elif 'Starting development server' in line:
                    print_colored(line.strip(), Colors.OKGREEN)
                    server_started = True
                elif 'Quit the server' in line:
                    print_colored(line.strip(), Colors.WARNING)
                elif 'Error' in line or 'ERROR' in line:
                    print_colored(line.strip(), Colors.FAIL)
                elif 'Warning' in line or 'WARNING' in line:
                    print_colored(line.strip(), Colors.WARNING)
                else:
                    print(line.strip())
            
            # Wait for process to complete
            return_code = process.wait()
            
            if return_code == 0:
                print_colored("\n✅ Server stopped normally", Colors.OKGREEN)
                break
            else:
                print_colored(f"\n❌ Server crashed with code {return_code}", Colors.FAIL)
                
                if "StatReloader" in str(process.stdout):
                    print_colored("StatReloader issue detected. Restarting with --noreload...", Colors.WARNING)
                
                print_colored("Restarting in 3 seconds...", Colors.WARNING)
                time.sleep(3)
                
        except KeyboardInterrupt:
            print_colored("\n\n🛑 Server stopped by user", Colors.WARNING)
            if 'process' in locals():
                process.terminate()
            break
        except Exception as e:
            print_colored(f"\n❌ Unexpected error: {e}", Colors.FAIL)
            print_colored("Restarting in 5 seconds...", Colors.WARNING)
            time.sleep(5)

def main():
    """Main entry point"""
    try:
        # Change to project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        # Set environment variables
        os.environ['DJANGO_SETTINGS_MODULE'] = 'primepath_project.settings_sqlite'
        os.environ['PYTHONUNBUFFERED'] = '1'
        
        # Run server with auto-restart
        run_server_with_auto_restart()
        
    except Exception as e:
        print_colored(f"Fatal error: {e}", Colors.FAIL)
        sys.exit(1)

if __name__ == '__main__':
    main()