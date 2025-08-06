#!/usr/bin/env python
"""
Automatic Git Backup System for PrimePath Project
Commits changes every hour automatically
"""

import subprocess
import time
from datetime import datetime
import os

def create_backup():
    """Create a git backup commit"""
    try:
        # Change to project directory
        os.chdir(r'C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_')
        
        # Check if there are changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            # There are changes to commit
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Stage all changes
            subprocess.run(['git', 'add', '-A'], check=True)
            
            # Commit with timestamp
            commit_message = f"AUTO-BACKUP: {timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            print(f"[SUCCESS] [{timestamp}] Backup created successfully!")
            return True
        else:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[INFO] [{timestamp}] No changes to backup")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error creating backup: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def main():
    """Main loop - create backups every hour"""
    print("=" * 50)
    print("AUTO-BACKUP SYSTEM STARTED")
    print("=" * 50)
    print("This will automatically commit your changes every hour")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    backup_count = 0
    
    try:
        while True:
            # Create backup
            if create_backup():
                backup_count += 1
                print(f"   Total backups created: {backup_count}")
            
            # Wait for 1 hour
            print(f"[WAITING] Next backup in 1 hour...")
            print("-" * 30)
            time.sleep(3600)  # 3600 seconds = 1 hour
            
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("AUTO-BACKUP SYSTEM STOPPED")
        print(f"   Total backups created this session: {backup_count}")
        print("=" * 50)

if __name__ == "__main__":
    main()