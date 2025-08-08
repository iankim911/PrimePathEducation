#!/usr/bin/env python
"""
Prepare PrimePath project for migration from Windows to Mac
Cleans up platform-specific files and creates migration-ready package
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def clean_project():
    """Remove files that shouldn't be migrated"""
    
    print("="*60)
    print("PRIMEPATH PROJECT - MIGRATION PREPARATION")
    print("="*60)
    
    # Directories to completely remove
    dirs_to_remove = [
        'venv',
        'Lib', 
        'Scripts',
        'serena-env',
        'serena_installation',
        '.git',  # Optional - remove if you want fresh git history
    ]
    
    # File patterns to remove
    files_to_remove = [
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.DS_Store',
        'Thumbs.db',
        '*.log',
        '*.pid',
    ]
    
    # Directories to clean (remove __pycache__)
    pycache_removed = 0
    
    print("\n1. Cleaning Python cache files...")
    for root, dirs, files in os.walk('.'):
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                pycache_removed += 1
            except Exception as e:
                print(f"   Warning: Could not remove {pycache_path}: {e}")
    
    print(f"   Removed {pycache_removed} __pycache__ directories")
    
    print("\n2. Removing platform-specific directories...")
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"   ✓ Removed: {dir_name}")
            except Exception as e:
                print(f"   ✗ Could not remove {dir_name}: {e}")
        else:
            print(f"   - {dir_name} not found (OK)")
    
    print("\n3. Removing compiled and temporary files...")
    removed_count = 0
    for root, dirs, files in os.walk('.'):
        for pattern in files_to_remove:
            if pattern.startswith('*'):
                extension = pattern[1:]
                matching_files = [f for f in files if f.endswith(extension)]
            else:
                matching_files = [f for f in files if f == pattern]
            
            for file in matching_files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    removed_count += 1
                except Exception as e:
                    pass  # Silently skip files that can't be removed
    
    print(f"   Removed {removed_count} temporary/compiled files")

def create_migration_info():
    """Create a migration info file with important details"""
    
    print("\n4. Creating migration info file...")
    
    migration_info = {
        "migration_date": datetime.now().isoformat(),
        "source_platform": "Windows",
        "target_platform": "Mac/Linux",
        "python_version_required": "3.11+",
        "django_version": "5.0.1",
        "database": "SQLite (db.sqlite3)",
        "important_notes": [
            "Create new virtual environment on Mac",
            "Run: pip install -r requirements.txt",
            "Run: python manage.py migrate --settings=primepath_project.settings_sqlite",
            "Convert .bat files to .sh scripts",
            "Server command: python manage.py runserver --settings=primepath_project.settings_sqlite"
        ],
        "directories_excluded": [
            "venv/",
            "Lib/",
            "Scripts/",
            "__pycache__/",
            ".git/"
        ]
    }
    
    with open('MIGRATION_INFO.json', 'w') as f:
        json.dump(migration_info, f, indent=2)
    
    print("   ✓ Created MIGRATION_INFO.json")

def create_mac_scripts():
    """Create Mac-equivalent shell scripts"""
    
    print("\n5. Creating Mac shell scripts...")
    
    scripts = {
        'run_server.sh': '''#!/bin/bash
# Run Django development server on Mac

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Navigate to project directory
cd primepath_project

# Run server
python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
''',
        'setup_mac.sh': '''#!/bin/bash
# Initial setup script for Mac

echo "Setting up PrimePath project on Mac..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Additional packages
echo "Installing additional packages..."
pip install djangorestframework==3.14.0
pip install django-filter==23.5
pip install django-cors-headers==4.3.1

# Navigate to project
cd primepath_project

# Run migrations
echo "Running migrations..."
python manage.py migrate --settings=primepath_project.settings_sqlite

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=primepath_project.settings_sqlite

echo "Setup complete! Run ./run_server.sh to start the server."
''',
        'test_features.sh': '''#!/bin/bash
# Test all features after migration

# Activate virtual environment
source venv/bin/activate

# Navigate to project
cd primepath_project

# Run feature tests
python double_check_all_features.py
'''
    }
    
    for script_name, content in scripts.items():
        with open(script_name, 'w', newline='\n') as f:  # Unix line endings
            f.write(content)
        print(f"   ✓ Created {script_name}")

def check_dependencies():
    """Verify all dependencies are documented"""
    
    print("\n6. Checking dependencies...")
    
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        print("   ✓ requirements.txt exists")
        print("   Current dependencies:")
        for line in requirements.strip().split('\n'):
            if line and not line.startswith('#'):
                print(f"     - {line}")
    else:
        print("   ✗ requirements.txt not found!")
        
    # Create comprehensive requirements if needed
    comprehensive_reqs = '''Django==5.0.1
Pillow==10.2.0
python-decouple==3.8
gunicorn==21.2.0
djangorestframework==3.14.0
django-filter==23.5
django-cors-headers==4.3.1
celery==5.3.4
redis==5.0.1
'''
    
    with open('requirements_full.txt', 'w') as f:
        f.write(comprehensive_reqs)
    print("   ✓ Created requirements_full.txt with all dependencies")

def create_readme():
    """Create a quick README for the migration"""
    
    print("\n7. Creating migration README...")
    
    readme = '''# PrimePath Project - Post-Migration Setup

## Quick Start on Mac

1. **Run the setup script**:
   ```bash
   chmod +x setup_mac.sh
   ./setup_mac.sh
   ```

2. **Start the server**:
   ```bash
   chmod +x run_server.sh
   ./run_server.sh
   ```

3. **Access the application**:
   - Open browser to: http://127.0.0.1:8000/

## Manual Setup (if scripts don't work)

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   cd primepath_project
   python manage.py migrate --settings=primepath_project.settings_sqlite
   ```

4. Start server:
   ```bash
   python manage.py runserver --settings=primepath_project.settings_sqlite
   ```

## Verification

Run the test script to verify everything works:
```bash
chmod +x test_features.sh
./test_features.sh
```

## Support

Refer to MIGRATION_TO_MAC_GUIDE.md for detailed instructions.
'''
    
    with open('README_MAC.md', 'w') as f:
        f.write(readme)
    
    print("   ✓ Created README_MAC.md")

def main():
    """Main execution"""
    
    # Confirm before proceeding
    print("\nThis script will:")
    print("- Remove Windows-specific files and directories")
    print("- Clean Python cache files")
    print("- Create Mac shell scripts")
    print("- Prepare the project for migration")
    print("\nNote: This will DELETE the venv folder and other Windows-specific files!")
    
    response = input("\nProceed? (yes/no): ").lower()
    if response != 'yes':
        print("Migration preparation cancelled.")
        return
    
    # Run all preparation steps
    clean_project()
    create_migration_info()
    create_mac_scripts()
    check_dependencies()
    create_readme()
    
    print("\n" + "="*60)
    print("MIGRATION PREPARATION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the changes")
    print("2. Zip the entire PrimePath_ folder")
    print("3. Transfer to Mac")
    print("4. Follow instructions in README_MAC.md")
    print("\nFiles created for Mac:")
    print("- run_server.sh")
    print("- setup_mac.sh") 
    print("- test_features.sh")
    print("- README_MAC.md")
    print("- MIGRATION_INFO.json")
    print("- requirements_full.txt")
    
    print("\n✅ Project is ready for migration to Mac!")

if __name__ == "__main__":
    main()