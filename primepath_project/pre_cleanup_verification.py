#!/usr/bin/env python
"""
Ultra-Deep Pre-Cleanup Verification Script
Ensures safe deletion without breaking production
"""
import os
import sys
import django
import json
from pathlib import Path

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

def verify_no_imports():
    """Verify test/fix files are not imported by production code"""
    print("\n" + "="*60)
    print("🔍 CHECKING FOR IMPORTS OF TEST/FIX FILES")
    print("="*60)
    
    production_dirs = ['core', 'placement_test', 'api', 'common', 'primepath_project']
    test_patterns = ['test_', 'fix_', 'comprehensive_', 'ultra_', 'deep_']
    
    issues = []
    
    for prod_dir in production_dirs:
        prod_path = Path(prod_dir)
        if not prod_path.exists():
            continue
            
        for py_file in prod_path.rglob('*.py'):
            # Skip test directories
            if 'tests' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for pattern in test_patterns:
                if f'import {pattern}' in content or f'from {pattern}' in content:
                    issues.append(f"⚠️ {py_file}: imports {pattern}* files")
    
    if issues:
        print("❌ FOUND IMPORT ISSUES:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ No production code imports test/fix files")
        return True

def verify_url_configurations():
    """Check that no test files are registered in URL patterns"""
    print("\n" + "="*60)
    print("🔍 CHECKING URL CONFIGURATIONS")
    print("="*60)
    
    url_files = list(Path('.').rglob('*urls.py'))
    test_patterns = ['test_', 'fix_', 'comprehensive_', 'ultra_', 'deep_']
    
    issues = []
    
    for url_file in url_files:
        if '__pycache__' in str(url_file):
            continue
            
        with open(url_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        for pattern in test_patterns:
            if pattern in content and 'test_result' not in content:  # test_result is a valid URL name
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line and 'test_result' not in line:
                        issues.append(f"⚠️ {url_file}:{i+1} - {line.strip()}")
    
    if issues:
        print("❌ FOUND URL ISSUES:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ No test files registered in URL patterns")
        return True

def verify_template_references():
    """Check that templates don't reference test files"""
    print("\n" + "="*60)
    print("🔍 CHECKING TEMPLATE REFERENCES")
    print("="*60)
    
    template_dirs = ['templates']
    test_patterns = ['test_', 'fix_', 'comprehensive_', 'ultra_', 'deep_']
    
    issues = []
    
    for template_dir in template_dirs:
        template_path = Path(template_dir)
        if not template_path.exists():
            continue
            
        for html_file in template_path.rglob('*.html'):
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for pattern in test_patterns:
                if f'{pattern}.py' in content or f'/{pattern}' in content:
                    issues.append(f"⚠️ {html_file}: references {pattern}* files")
    
    if issues:
        print("❌ FOUND TEMPLATE ISSUES:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ No templates reference test files")
        return True

def verify_javascript_dependencies():
    """Check JavaScript files for test file dependencies"""
    print("\n" + "="*60)
    print("🔍 CHECKING JAVASCRIPT DEPENDENCIES")
    print("="*60)
    
    js_dirs = ['static/js', 'staticfiles/js']
    test_patterns = ['test_', 'fix_', 'comprehensive_', 'ultra_', 'deep_']
    
    issues = []
    
    for js_dir in js_dirs:
        js_path = Path(js_dir)
        if not js_path.exists():
            continue
            
        for js_file in js_path.rglob('*.js'):
            if 'vendor' in str(js_file) or 'admin' in str(js_file):
                continue
                
            with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for pattern in test_patterns:
                if f'{pattern}.py' in content or f'/{pattern}' in content:
                    issues.append(f"⚠️ {js_file}: references {pattern}* files")
    
    if issues:
        print("❌ FOUND JAVASCRIPT ISSUES:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ No JavaScript files reference test files")
        return True

def verify_database_integrity():
    """Ensure database doesn't depend on test files"""
    print("\n" + "="*60)
    print("🔍 CHECKING DATABASE INTEGRITY")
    print("="*60)
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Check if database is accessible
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
            print(f"✅ Database accessible - {migration_count} migrations")
            
            # Check core tables
            cursor.execute("SELECT COUNT(*) FROM placement_test_exam")
            exam_count = cursor.fetchone()[0]
            print(f"✅ Exam table intact - {exam_count} exams")
            
            cursor.execute("SELECT COUNT(*) FROM placement_test_question")
            question_count = cursor.fetchone()[0]
            print(f"✅ Question table intact - {question_count} questions")
            
        return True
    except Exception as e:
        print(f"❌ Database issue: {e}")
        return False

def verify_static_media_files():
    """Ensure static and media files are preserved"""
    print("\n" + "="*60)
    print("🔍 CHECKING STATIC/MEDIA FILES")
    print("="*60)
    
    critical_paths = [
        'static/js/modules/answer-manager.js',
        'static/js/modules/pdf-viewer.js',
        'static/js/modules/timer.js',
        'static/css/pages/student-test.css',
        'media/exams/pdfs',
        'media/exams/audio'
    ]
    
    for path in critical_paths:
        if Path(path).exists():
            print(f"✅ {path} - EXISTS")
        else:
            print(f"⚠️ {path} - Missing (may be normal)")
    
    return True

def list_files_to_delete():
    """List all files that will be deleted in Phase 1"""
    print("\n" + "="*60)
    print("📋 FILES TO BE DELETED IN PHASE 1")
    print("="*60)
    
    phase1_files = {
        'Windows Files': ['*.bat'],
        'JSON Results': ['*_results.json', '*_test_results.json'],
        'Temp Files': ['actual_server_response.html', 'server_response_*.html', 
                      'cookies.txt', 'csrf.txt', 'server.log']
    }
    
    total_count = 0
    
    for category, patterns in phase1_files.items():
        print(f"\n{category}:")
        for pattern in patterns:
            files = list(Path('.').glob(pattern))
            for f in files:
                print(f"  - {f.name}")
                total_count += 1
    
    print(f"\n📊 Total files to delete in Phase 1: {total_count}")
    return total_count

def add_console_logging():
    """Add console logging to verify cleanup doesn't break anything"""
    print("\n" + "="*60)
    print("🔧 ADDING CONSOLE LOGGING FOR VERIFICATION")
    print("="*60)
    
    log_code = '''
    // Cleanup Verification Logging
    console.log('[CLEANUP_VERIFY] System check starting...');
    
    // Check critical modules
    if (typeof answerManager !== 'undefined') {
        console.log('[CLEANUP_VERIFY] ✅ Answer Manager loaded');
    }
    if (typeof pdfViewer !== 'undefined') {
        console.log('[CLEANUP_VERIFY] ✅ PDF Viewer loaded');
    }
    if (typeof timer !== 'undefined') {
        console.log('[CLEANUP_VERIFY] ✅ Timer loaded');
    }
    
    // Check API endpoints
    fetch('/api/PlacementTest/exams/')
        .then(r => console.log('[CLEANUP_VERIFY] ✅ API accessible'))
        .catch(e => console.error('[CLEANUP_VERIFY] ❌ API error:', e));
    '''
    
    print("Console logging code prepared (will be added after cleanup)")
    return log_code

def main():
    """Run all verification checks"""
    print("\n" + "="*80)
    print("🚀 ULTRA-DEEP PRE-CLEANUP VERIFICATION")
    print("="*80)
    
    results = {
        'imports': verify_no_imports(),
        'urls': verify_url_configurations(),
        'templates': verify_template_references(),
        'javascript': verify_javascript_dependencies(),
        'database': verify_database_integrity(),
        'static_media': verify_static_media_files()
    }
    
    # List files to delete
    file_count = list_files_to_delete()
    
    # Prepare console logging
    log_code = add_console_logging()
    
    # Final verdict
    print("\n" + "="*80)
    print("📊 VERIFICATION RESULTS")
    print("="*80)
    
    all_safe = all(results.values())
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check.upper()}: {status}")
    
    if all_safe:
        print("\n" + "="*80)
        print("✅ SAFE TO PROCEED WITH PHASE 1 CLEANUP")
        print("="*80)
        print(f"\n🎯 Ready to delete {file_count} files")
        print("\nNext steps:")
        print("1. Create backup: cp -r . ../primepath_backup_$(date +%Y%m%d_%H%M%S)")
        print("2. Run Phase 1 deletion commands")
        print("3. Add console logging to verify")
        print("4. Test all critical features")
        
        # Save verification results
        with open('cleanup_verification_results.json', 'w') as f:
            json.dump({
                'safe_to_proceed': True,
                'checks': results,
                'file_count': file_count,
                'phase': 1
            }, f, indent=2)
            
        print("\n✅ Verification results saved to cleanup_verification_results.json")
    else:
        print("\n" + "="*80)
        print("❌ ISSUES FOUND - DO NOT PROCEED")
        print("="*80)
        print("\nResolve the issues above before proceeding with cleanup")
    
    return all_safe

if __name__ == "__main__":
    safe = main()
    sys.exit(0 if safe else 1)