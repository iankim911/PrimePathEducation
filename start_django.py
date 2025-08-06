#!/usr/bin/env python
"""
Simple Django server starter with error handling
"""
import os
import sys
import subprocess
from pathlib import Path

# Set up paths
BASE_DIR = Path(__file__).parent
PROJECT_DIR = BASE_DIR / "primepath_project"
VENV_PYTHON = BASE_DIR / "venv" / "Scripts" / "python.exe"

def start_django_server():
    """Start Django development server"""
    
    # Change to project directory
    os.chdir(str(PROJECT_DIR))
    
    # Set Django settings
    os.environ["DJANGO_SETTINGS_MODULE"] = "primepath_project.settings_sqlite"
    
    print("🚀 Starting PrimePath Django Server...")
    print(f"📁 Project Directory: {PROJECT_DIR}")
    print(f"🐍 Python Executable: {VENV_PYTHON}")
    print(f"⚙️  Django Settings: {os.environ['DJANGO_SETTINGS_MODULE']}")
    print("-" * 50)
    
    try:
        # Start the Django server
        cmd = [
            str(VENV_PYTHON),
            "manage.py", 
            "runserver", 
            "127.0.0.1:8000",
            "--noreload"
        ]
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        print("📡 Server will be available at: http://127.0.0.1:8000")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run the server
        process = subprocess.run(cmd, check=False)
        
        if process.returncode != 0:
            print(f"❌ Server exited with error code: {process.returncode}")
        else:
            print("✅ Server shutdown successfully")
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try running the batch file manually from the primepath_project folder")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    start_django_server()