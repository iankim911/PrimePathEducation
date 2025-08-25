#!/usr/bin/env python3
"""
Start Credential Monitoring System
==================================

This script starts the automated credential monitoring system and keeps it running
in the background. It should be run after server startup to ensure credentials
remain stable.

Usage:
    python start_credential_monitoring.py

Author: Claude Code AI System
Date: August 25, 2025
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

def start_monitoring():
    """Start the credential monitoring system in the background."""
    print("🚀 Starting PrimePath Credential Monitoring System...")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    monitor_script = script_dir / 'automated_credential_monitor.py'
    
    if not monitor_script.exists():
        print(f"❌ Monitoring script not found: {monitor_script}")
        return False
    
    # Start the monitoring system
    try:
        process = subprocess.Popen([
            sys.executable, 
            str(monitor_script), 
            'start'
        ], 
        cwd=str(script_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
        )
        
        print(f"✅ Credential monitoring started (PID: {process.pid})")
        print("📊 Monitoring will run every 60 minutes")
        print("🔧 Auto-fix enabled for detected issues")
        print()
        print("Press Ctrl+C to stop monitoring")
        
        # Handle graceful shutdown
        def signal_handler(sig, frame):
            print("\n🛑 Stopping credential monitoring...")
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ Monitoring stopped successfully")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️  Monitoring process killed (timeout)")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Monitor the process output
        while True:
            try:
                output = process.stdout.readline()
                if output:
                    print(f"[MONITOR] {output.strip()}")
                elif process.poll() is not None:
                    # Process has terminated
                    break
                time.sleep(0.1)
            except KeyboardInterrupt:
                break
        
        # Check final status
        return_code = process.poll()
        if return_code is not None and return_code != 0:
            print(f"❌ Monitoring process exited with code: {return_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start monitoring: {e}")
        return False

def check_monitoring_status():
    """Check if monitoring is already running."""
    try:
        result = subprocess.run([
            sys.executable, 
            'automated_credential_monitor.py', 
            'status'
        ], 
        capture_output=True, 
        text=True,
        cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            import json
            status = json.loads(result.stdout)
            return status.get('is_running', False)
        return False
    except:
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("PrimePath Credential Monitoring System")
    print("=" * 60)
    
    # Check if already running
    if check_monitoring_status():
        print("⚠️  Monitoring is already running")
        print("   Run 'python automated_credential_monitor.py status' to check details")
        sys.exit(1)
    
    # Start monitoring
    success = start_monitoring()
    
    if not success:
        print("❌ Failed to start credential monitoring")
        sys.exit(1)
    
    print("✅ Credential monitoring session completed")