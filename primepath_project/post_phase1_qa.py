#!/usr/bin/env python
"""
Post-Phase 1 QA Validation
Ensures system still works after cleanup
"""
import os
import sys
import django
import json
import time
from datetime import datetime

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

def test_database_connection():
    """Test database is still accessible"""
    print("\n🔍 Testing Database Connection...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM placement_test_exam")
            exam_count = cursor.fetchone()[0]
            print(f"  ✅ Database OK - {exam_count} exams found")
            
            # Add console logging
            print("  console.log('[PHASE1_QA] Database connection verified');")
            return True
    except Exception as e:
        print(f"  ❌ Database Error: {e}")
        print("  console.error('[PHASE1_QA] Database connection failed');")
        return False

def test_models_import():
    """Test that models can be imported"""
    print("\n🔍 Testing Model Imports...")
    try:
        from placement_test.models import Exam, Question, StudentSession
        from core.models import Teacher, CurriculumLevel
        print("  ✅ All models imported successfully")
        print("  console.log('[PHASE1_QA] Model imports verified');")
        return True
    except Exception as e:
        print(f"  ❌ Import Error: {e}")
        print("  console.error('[PHASE1_QA] Model import failed');")
        return False

def test_views_import():
    """Test that views can be imported"""
    print("\n🔍 Testing View Imports...")
    try:
        from placement_test.views import exam, session, student
        from core.views import teacher_dashboard, placement_rules
        print("  ✅ All views imported successfully")
        print("  console.log('[PHASE1_QA] View imports verified');")
        return True
    except Exception as e:
        print(f"  ❌ Import Error: {e}")
        print("  console.error('[PHASE1_QA] View import failed');")
        return False

def test_url_configuration():
    """Test URL configuration is intact"""
    print("\n🔍 Testing URL Configuration...")
    try:
        from django.urls import reverse
        
        urls_to_test = [
            'core:teacher_dashboard',
            'placement_test:exam_list',
            'placement_test:create_exam',
            'core:placement_rules',
            'core:exam_mapping'
        ]
        
        failed = []
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"  ✅ {url_name} -> {url}")
            except:
                failed.append(url_name)
                print(f"  ❌ {url_name} - Failed to resolve")
        
        if not failed:
            print("  console.log('[PHASE1_QA] All URLs resolved correctly');")
            return True
        else:
            print(f"  console.error('[PHASE1_QA] Failed URLs: {failed}');")
            return False
            
    except Exception as e:
        print(f"  ❌ URL Error: {e}")
        print("  console.error('[PHASE1_QA] URL configuration failed');")
        return False

def test_static_files():
    """Test critical static files exist"""
    print("\n🔍 Testing Static Files...")
    from pathlib import Path
    
    critical_files = [
        'static/js/modules/answer-manager.js',
        'static/js/modules/pdf-viewer.js',
        'static/js/modules/timer.js',
        'static/js/modules/navigation.js',
        'static/css/pages/student-test.css',
        'templates/base.html',
        'templates/placement_test/student_test_v2.html'
    ]
    
    missing = []
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            missing.append(file_path)
            print(f"  ❌ {file_path} - MISSING")
    
    if not missing:
        print("  console.log('[PHASE1_QA] All static files present');")
        return True
    else:
        print(f"  console.error('[PHASE1_QA] Missing files: {missing}');")
        return False

def test_media_files():
    """Test media directories exist"""
    print("\n🔍 Testing Media Files...")
    from pathlib import Path
    
    media_dirs = [
        'media/exams/pdfs',
        'media/exams/audio'
    ]
    
    for media_dir in media_dirs:
        path = Path(media_dir)
        if path.exists():
            file_count = len(list(path.iterdir()))
            print(f"  ✅ {media_dir} - {file_count} files")
        else:
            print(f"  ❌ {media_dir} - MISSING")
            return False
    
    print("  console.log('[PHASE1_QA] Media directories intact');")
    return True

def test_exam_functionality():
    """Test basic exam functionality"""
    print("\n🔍 Testing Exam Functionality...")
    try:
        from placement_test.models import Exam, Question
        
        # Get first exam
        exam = Exam.objects.first()
        if exam:
            question_count = exam.questions.count()
            print(f"  ✅ Exam '{exam.name}' has {question_count} questions")
            
            # Test question retrieval
            first_question = exam.questions.first()
            if first_question:
                print(f"  ✅ Question #{first_question.question_number} accessible")
            
            print("  console.log('[PHASE1_QA] Exam functionality verified');")
            return True
        else:
            print("  ⚠️ No exams in database (may be normal)")
            return True
            
    except Exception as e:
        print(f"  ❌ Exam Error: {e}")
        print("  console.error('[PHASE1_QA] Exam functionality failed');")
        return False

def verify_no_test_files():
    """Verify test files were actually deleted"""
    print("\n🔍 Verifying Test Files Deleted...")
    from pathlib import Path
    
    deleted_patterns = [
        '*.bat',
        '*_results.json',
        '*_test_results.json',
        'actual_server_response.html',
        'cookies.txt',
        'csrf.txt',
        'server.log'
    ]
    
    found_files = []
    for pattern in deleted_patterns:
        remaining = list(Path('.').glob(pattern))
        if remaining:
            found_files.extend([str(f) for f in remaining])
    
    if not found_files:
        print("  ✅ All Phase 1 files successfully deleted")
        print("  console.log('[PHASE1_QA] Cleanup verified - files deleted');")
        return True
    else:
        print(f"  ❌ Files still present: {found_files}")
        print(f"  console.error('[PHASE1_QA] Files not deleted: {found_files}');")
        return False

def generate_console_script():
    """Generate JavaScript console logging for browser testing"""
    print("\n🔧 Generating Console Logging Script...")
    
    script = """
// ===== PHASE 1 CLEANUP VERIFICATION =====
// Add this to browser console or base.html temporarily

(function() {
    console.log('%c===== PHASE 1 CLEANUP QA =====', 'color: blue; font-weight: bold');
    
    // Check critical modules
    const modules = ['answerManager', 'pdfViewer', 'timer', 'navigationModule'];
    modules.forEach(mod => {
        if (typeof window[mod] !== 'undefined') {
            console.log(`✅ ${mod} loaded`);
        } else {
            console.warn(`⚠️ ${mod} not found (check if needed)`);
        }
    });
    
    // Check API endpoints
    fetch('/api/placement/exams/')
        .then(r => {
            console.log('✅ Exam API accessible');
            return r.json();
        })
        .then(data => console.log(`  Found ${data.length || 0} exams`))
        .catch(e => console.error('❌ Exam API error:', e));
    
    // Check authentication
    if (document.querySelector('.nav-tabs')) {
        console.log('✅ Navigation loaded');
    }
    
    // Check for any 404s or errors
    const checkForErrors = () => {
        const errors = document.querySelectorAll('.error, .alert-error');
        if (errors.length > 0) {
            console.error('❌ Error messages found:', errors);
        } else {
            console.log('✅ No error messages');
        }
    };
    
    setTimeout(checkForErrors, 1000);
    
    console.log('%c===== END QA CHECK =====', 'color: blue; font-weight: bold');
})();
"""
    
    print("  Console script generated - copy to browser console")
    
    # Save to file for easy access
    with open('phase1_console_qa.js', 'w') as f:
        f.write(script)
    print("  ✅ Saved to phase1_console_qa.js")
    
    return script

def main():
    """Run all QA tests"""
    print("\n" + "="*60)
    print("🚀 POST-PHASE 1 CLEANUP QA VALIDATION")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = {
        'Files Deleted': verify_no_test_files(),
        'Database': test_database_connection(),
        'Models': test_models_import(),
        'Views': test_views_import(),
        'URLs': test_url_configuration(),
        'Static Files': test_static_files(),
        'Media Files': test_media_files(),
        'Exam Functions': test_exam_functionality()
    }
    
    # Generate console script
    console_script = generate_console_script()
    
    # Summary
    print("\n" + "="*60)
    print("📊 QA RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in tests.values() if v)
    total = len(tests)
    
    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    # Save results
    results = {
        'phase': 'Phase 1',
        'timestamp': datetime.now().isoformat(),
        'tests': tests,
        'passed': passed,
        'total': total,
        'success': passed == total
    }
    
    with open('phase1_qa_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    if passed == total:
        print("\n" + "="*60)
        print("✅ PHASE 1 CLEANUP SUCCESSFUL - SAFE TO PROCEED")
        print("="*60)
        print("\nNext steps:")
        print("1. Start the server and test manually")
        print("2. Open browser console and run phase1_console_qa.js")
        print("3. If all good, proceed to Phase 2")
        return True
    else:
        print("\n" + "="*60)
        print("❌ ISSUES DETECTED - INVESTIGATE BEFORE CONTINUING")
        print("="*60)
        print("\nTo restore:")
        print("cp -r ../primepath_project_backup_* .")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)