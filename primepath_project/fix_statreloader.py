#!/usr/bin/env python
"""
Fix for Django StatReloader issues
Run this once to configure your system properly
"""

import os
import sys
import subprocess
import platform

def fix_macos_limits():
    """Fix file descriptor limits on macOS"""
    print("🔧 Fixing macOS file descriptor limits...")
    
    # Create or update shell profile
    home = os.path.expanduser("~")
    profiles = [
        os.path.join(home, ".zshrc"),
        os.path.join(home, ".bash_profile"),
        os.path.join(home, ".bashrc")
    ]
    
    ulimit_line = "\n# Fix for Django StatReloader\nulimit -n 10240\n"
    
    for profile in profiles:
        if os.path.exists(profile):
            with open(profile, 'r') as f:
                content = f.read()
            
            if "ulimit -n" not in content:
                with open(profile, 'a') as f:
                    f.write(ulimit_line)
                print(f"✅ Updated {profile}")
            else:
                print(f"ℹ️ {profile} already configured")
    
    # Create launchd plist for permanent fix
    plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>limit.maxfiles</string>
    <key>ProgramArguments</key>
    <array>
        <string>launchctl</string>
        <string>limit</string>
        <string>maxfiles</string>
        <string>65536</string>
        <string>200000</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""
    
    plist_path = "/Library/LaunchDaemons/limit.maxfiles.plist"
    temp_plist = "/tmp/limit.maxfiles.plist"
    
    try:
        with open(temp_plist, 'w') as f:
            f.write(plist_content)
        
        print("📝 Creating system configuration...")
        subprocess.run(["sudo", "cp", temp_plist, plist_path], check=True)
        subprocess.run(["sudo", "chown", "root:wheel", plist_path], check=True)
        subprocess.run(["sudo", "chmod", "644", plist_path], check=True)
        subprocess.run(["sudo", "launchctl", "load", "-w", plist_path], capture_output=True)
        print("✅ System configuration updated")
    except subprocess.CalledProcessError:
        print("⚠️ Could not update system configuration (requires sudo)")
    except Exception as e:
        print(f"⚠️ Error updating system configuration: {e}")
    
    # Apply immediately for current session
    try:
        subprocess.run(["ulimit", "-n", "10240"], shell=True)
        print("✅ Applied limits for current session")
    except:
        pass

def create_django_config():
    """Create Django configuration to handle StatReloader issues"""
    print("\n🔧 Creating Django configuration...")
    
    config_content = '''"""
Django Server Configuration for StatReloader stability
Add this to your settings file or create as a separate module
"""

import os
import sys

# Disable auto-reload in development if having issues
if 'runserver' in sys.argv:
    # Option 1: Use StatReloader with increased checks
    DJANGO_AUTORELOAD_TYPE = 'stat'
    
    # Option 2: Disable autoreload completely (most stable)
    # os.environ['DJANGO_AUTORELOAD'] = 'false'
    
    # Option 3: Use WatchmanReloader if installed (best option)
    # DJANGO_AUTORELOAD_TYPE = 'watchman'

# Increase file watcher limits
if sys.platform == 'darwin':
    # macOS specific settings
    import resource
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (10240, 10240))
    except:
        pass

# Add to your settings.py:
# from . import statreloader_config  # noqa
'''
    
    config_path = "primepath_project/statreloader_config.py"
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Created {config_path}")
    print("ℹ️ Add this line to your settings_sqlite.py:")
    print("   from . import statreloader_config  # noqa")

def create_alternative_runner():
    """Create an alternative runner using watchman if available"""
    print("\n🔧 Creating alternative runner with Watchman...")
    
    runner_content = '''#!/usr/bin/env python
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
'''
    
    runner_path = "run_with_watchman.py"
    with open(runner_path, 'w') as f:
        f.write(runner_content)
    
    os.chmod(runner_path, 0o755)
    print(f"✅ Created {runner_path}")

def main():
    print("=" * 60)
    print("DJANGO STATRELOADER FIX UTILITY")
    print("=" * 60)
    
    system = platform.system()
    print(f"🖥️ Detected system: {system}")
    
    if system == "Darwin":
        fix_macos_limits()
    elif system == "Linux":
        print("ℹ️ On Linux, add to /etc/security/limits.conf:")
        print("   * soft nofile 10240")
        print("   * hard nofile 10240")
    
    create_django_config()
    create_alternative_runner()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\n📚 How to use:")
    print("1. RECOMMENDED: Use the stable server starter:")
    print("   ./start_server.sh")
    print("\n2. Or use Python runner with auto-restart:")
    print("   python run_server_stable.py")
    print("\n3. Or use Watchman runner (if installed):")
    print("   python run_with_watchman.py")
    print("\n4. To use normal Django but with --noreload:")
    print("   ../venv/bin/python manage.py runserver --noreload")
    print("\n⚠️ NOTE: You may need to restart your terminal for limits to apply")

if __name__ == "__main__":
    main()