#!/usr/bin/env python
"""
Phase 2 QA Validation - Post Documentation Cleanup
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

def test_models():
    """Test model imports"""
    print("🔍 Testing Model Imports...")
    try:
        from placement_test.models import Exam, Question, StudentSession
        from core.models import Teacher, CurriculumLevel
        print("  ✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Import Error: {e}")
        return False

def test_views():
    """Test view imports"""
    print("🔍 Testing View Imports...")
    try:
        from placement_test.views import exam, session, student
        from core.views import teacher_dashboard, placement_rules
        print("  ✅ All views imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Import Error: {e}")
        return False

def test_database():
    """Test database access"""
    print("🔍 Testing Database Access...")
    try:
        from placement_test.models import Exam
        exam_count = Exam.objects.count()
        print(f"  ✅ Database accessible - {exam_count} exams found")
        return True
    except Exception as e:
        print(f"  ❌ Database Error: {e}")
        return False

def test_urls():
    """Test URL configuration"""
    print("🔍 Testing URL Configuration...")
    try:
        from django.urls import reverse
        urls = ['core:teacher_dashboard', 'PlacementTest:exam_list', 'PlacementTest:create_exam']
        for url in urls:
            reverse(url)
        print("  ✅ All URLs resolved correctly")
        return True
    except Exception as e:
        print(f"  ❌ URL Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("📊 PHASE 2 QA VALIDATION")
    print("="*60)
    
    tests = {
        'Models': test_models(),
        'Views': test_views(),
        'Database': test_database(),
        'URLs': test_urls()
    }
    
    passed = sum(1 for v in tests.values() if v)
    total = len(tests)
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    
    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    if passed == total:
        print(f"\n✅ ALL TESTS PASSED ({passed}/{total}) - Safe to continue to Phase 3")
        return True
    else:
        print(f"\n⚠️ Some tests failed ({passed}/{total}) - Investigate before continuing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)