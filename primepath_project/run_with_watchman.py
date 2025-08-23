#!/usr/bin/env python
"""
Alternative Django runner using Watchman for file watching
More stable than StatReloader
"""

import os
import sys
import subprocess

def check_watchman():
    """Check if Watchman is installed"""
    try:
        subprocess.run(["watchman", "version"], capture_output=True, check=True)
        return True
    except:
        return False

def install_watchman():
    """Install Watchman"""
    print("📦 Installing Watchman...")
    if sys.platform == "darwin":
        try:
            subprocess.run(["brew", "install", "watchman"], check=True)
            print("✅ Watchman installed")
            return True
        except:
            print("❌ Could not install Watchman. Install manually: brew install watchman")
            return False
    else:
        print("ℹ️ Please install Watchman manually for your platform")
        return False

def main():
    # Check/install Watchman
    if not check_watchman():
        print("⚠️ Watchman not found (better file watching)")
        install_watchman()
    
    # Set Watchman as the reloader
    os.environ['DJANGO_AUTORELOAD_TYPE'] = 'watchman' if check_watchman() else 'stat'
    
    # Run Django
    os.system("../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite")

if __name__ == "__main__":
    main()
