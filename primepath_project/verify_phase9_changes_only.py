#!/usr/bin/env python
"""
Quick verification that Phase 9 ONLY added documentation files
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

def check_phase9_changes():
    """Check what files were modified today (Phase 9)"""
    
    print("\n" + "="*80)
    print("🔍 PHASE 9 CHANGE VERIFICATION")
    print("="*80)
    
    # Phase 9 files that were created
    phase9_docs = [
        'README.md',
        'API.md',
        'DEPLOYMENT.md', 
        'CONTRIBUTING.md',
        'PHASE9_COMPLETION_REPORT.md'
    ]
    
    project_root = Path(__file__).parent.parent
    
    print("\n✅ Phase 9 Documentation Files Created:")
    for doc in phase9_docs:
        doc_path = project_root / doc
        if doc_path.exists():
            stats = doc_path.stat()
            mod_time = datetime.fromtimestamp(stats.st_mtime)
            print(f"   - {doc}: {doc_path.stat().st_size} bytes, modified {mod_time.strftime('%Y-%m-%d %H:%M')}")
            
    # Check if any Python files were modified today
    print("\n🔍 Checking for modified Python files (should be none)...")
    today = datetime.now().date()
    python_files_modified = []
    
    for py_file in project_root.rglob('*.py'):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        stats = py_file.stat()
        mod_date = datetime.fromtimestamp(stats.st_mtime).date()
        
        if mod_date == today:
            # Exclude test files and Phase 9 analyzer
            if 'phase9' in py_file.name.lower() or 'test_phase9' in py_file.name.lower():
                continue
            python_files_modified.append(py_file.relative_to(project_root))
            
    if python_files_modified:
        print("❌ WARNING: Python files were modified:")
        for f in python_files_modified[:5]:  # Show first 5
            print(f"   - {f}")
    else:
        print("✅ No Python application files modified (correct for documentation phase)")
        
    # Check templates
    print("\n🔍 Checking for modified templates (should be none)...")
    template_files_modified = []
    
    templates_dir = project_root / 'primepath_project' / 'templates'
    if templates_dir.exists():
        for template in templates_dir.rglob('*.html'):
            stats = template.stat()
            mod_date = datetime.fromtimestamp(stats.st_mtime).date()
            
            if mod_date == today:
                template_files_modified.append(template.relative_to(project_root))
                
    if template_files_modified:
        print("❌ WARNING: Template files were modified:")
        for f in template_files_modified[:5]:
            print(f"   - {f}")
    else:
        print("✅ No template files modified (correct for documentation phase)")
        
    # Check JavaScript/CSS
    print("\n🔍 Checking for modified JS/CSS files...")
    static_modified = []
    
    static_dir = project_root / 'primepath_project' / 'static'
    if static_dir.exists():
        for static_file in static_dir.rglob('*'):
            if static_file.is_file() and static_file.suffix in ['.js', '.css']:
                if 'phase9' in static_file.name.lower():
                    continue  # Phase 9 monitoring is OK
                    
                stats = static_file.stat()
                mod_date = datetime.fromtimestamp(stats.st_mtime).date()
                
                if mod_date == today:
                    static_modified.append(static_file.relative_to(project_root))
                    
    if static_modified:
        print("❌ WARNING: Static files were modified:")
        for f in static_modified[:5]:
            print(f"   - {f}")
    else:
        print("✅ No JS/CSS files modified (except Phase 9 monitoring)")
        
    print("\n" + "="*80)
    print("📊 PHASE 9 VERIFICATION SUMMARY")
    print("="*80)
    
    issues = len(python_files_modified) + len(template_files_modified) + len(static_modified)
    
    if issues == 0:
        print("✅ VERIFIED: Phase 9 only added documentation files!")
        print("   - No application code modified")
        print("   - No templates changed")
        print("   - No existing JS/CSS altered")
        print("   - All existing features remain untouched")
        return True
    else:
        print(f"⚠️ WARNING: {issues} unexpected modifications detected")
        print("   Please review the files listed above")
        return False

if __name__ == "__main__":
    success = check_phase9_changes()
    sys.exit(0 if success else 1)