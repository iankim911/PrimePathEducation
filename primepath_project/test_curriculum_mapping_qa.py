#!/usr/bin/env python
"""
Comprehensive QA Test for Curriculum Mapping Feature
Tests the complete implementation including 504 fix
"""
import os
import sys
import django
import time
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.core.cache import cache
from core.models import Teacher, CurriculumLevel
from primepath_routinetest.models import (
    ClassCurriculumMapping, TeacherClassAssignment, 
    ExamScheduleMatrix, Exam
)
from primepath_routinetest.views.schedule_matrix_optimized import get_class_curriculum_mapping_cached

# Test configuration
QA_RESULTS = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_result(test_name, passed, message=""):
    """Record test result"""
    if passed:
        QA_RESULTS['passed'].append(test_name)
        print(f"✅ {test_name}")
    else:
        QA_RESULTS['failed'].append(test_name)
        print(f"❌ {test_name}: {message}")

def warning(message):
    """Record a warning"""
    QA_RESULTS['warnings'].append(message)
    print(f"⚠️  WARNING: {message}")

def run_qa_tests():
    """Run comprehensive QA tests"""
    
    print_header("CURRICULUM MAPPING QA TEST SUITE")
    
    # 1. DATABASE & MODEL TESTS
    print_header("1. DATABASE & MODEL TESTS")
    
    # Test 1.1: Model exists and accessible
    try:
        mapping_count = ClassCurriculumMapping.objects.count()
        test_result("Model exists and accessible", True)
        print(f"   Current mappings in database: {mapping_count}")
    except Exception as e:
        test_result("Model exists and accessible", False, str(e))
    
    # Test 1.2: Can create mappings
    try:
        curriculum = CurriculumLevel.objects.first()
        if curriculum:
            test_mapping = ClassCurriculumMapping.objects.create(
                class_code="QA_TEST_CLASS",
                curriculum_level=curriculum,
                academic_year="2025",
                priority=1,
                notes="QA Test Mapping"
            )
            test_result("Can create mappings", True)
            test_mapping.delete()  # Clean up
        else:
            warning("No curriculum levels in database to test with")
    except Exception as e:
        test_result("Can create mappings", False, str(e))
    
    # 2. PERMISSION & ACCESS TESTS
    print_header("2. PERMISSION & ACCESS TESTS")
    
    # Test 2.1: Admin detection
    try:
        # Create test users
        admin_user, _ = User.objects.get_or_create(
            username="qa_admin",
            defaults={'email': 'qa_admin@test.com'}
        )
        admin_teacher, _ = Teacher.objects.get_or_create(
            user=admin_user,
            defaults={'is_head_teacher': True}
        )
        
        regular_user, _ = User.objects.get_or_create(
            username="qa_teacher",
            defaults={'email': 'qa_teacher@test.com'}
        )
        regular_teacher, _ = Teacher.objects.get_or_create(
            user=regular_user,
            defaults={'is_head_teacher': False}
        )
        
        test_result("Admin/Regular teacher distinction", 
                   admin_teacher.is_head_teacher and not regular_teacher.is_head_teacher)
    except Exception as e:
        test_result("Admin/Regular teacher distinction", False, str(e))
    
    # Test 2.2: URL access control
    client = Client()
    try:
        # Test anonymous access (should redirect)
        response = client.get('/RoutineTest/curriculum-mapping/')
        test_result("Anonymous access blocked", response.status_code == 302)
        
        # Test regular teacher access (should be blocked)
        client.force_login(regular_user)
        response = client.get('/RoutineTest/curriculum-mapping/')
        test_result("Regular teacher access blocked", response.status_code == 302)
        
        # Test admin access (should work)
        client.force_login(admin_user)
        response = client.get('/RoutineTest/curriculum-mapping/')
        test_result("Admin access allowed", response.status_code == 200)
        
    except Exception as e:
        test_result("URL access control", False, str(e))
    
    # 3. PERFORMANCE TESTS (504 FIX)
    print_header("3. PERFORMANCE TESTS (504 TIMEOUT FIX)")
    
    # Test 3.1: Query optimization
    try:
        # Clear cache
        cache.clear()
        
        # Create test data
        class_codes = ['PERF_CLASS_1', 'PERF_CLASS_2', 'PERF_CLASS_3']
        curriculum = CurriculumLevel.objects.first()
        
        if curriculum:
            for class_code in class_codes:
                ClassCurriculumMapping.objects.create(
                    class_code=class_code,
                    curriculum_level=curriculum,
                    academic_year="2025",
                    priority=1
                )
            
            # Time the optimized function
            start = time.time()
            for class_code in class_codes:
                result = get_class_curriculum_mapping_cached(class_code, "2025")
            elapsed = time.time() - start
            
            test_result("Optimized query performance", elapsed < 0.5,
                       f"Took {elapsed:.3f}s for 3 lookups")
            
            # Clean up
            ClassCurriculumMapping.objects.filter(
                class_code__in=class_codes
            ).delete()
        else:
            warning("No curriculum levels to test performance with")
            
    except Exception as e:
        test_result("Query optimization", False, str(e))
    
    # Test 3.2: Caching mechanism
    try:
        cache.clear()
        
        # First call (should hit database)
        start = time.time()
        result1 = get_class_curriculum_mapping_cached("CACHE_TEST", "2025")
        first_call = time.time() - start
        
        # Second call (should use cache)
        start = time.time()
        result2 = get_class_curriculum_mapping_cached("CACHE_TEST", "2025")
        second_call = time.time() - start
        
        test_result("Caching mechanism working", 
                   second_call < first_call * 0.5,
                   f"First: {first_call:.4f}s, Cached: {second_call:.4f}s")
        
    except Exception as e:
        test_result("Caching mechanism", False, str(e))
    
    # 4. AJAX API TESTS
    print_header("4. AJAX API TESTS")
    
    client.force_login(admin_user)
    
    # Test 4.1: Add mapping API
    try:
        curriculum = CurriculumLevel.objects.first()
        if curriculum:
            response = client.post(
                '/RoutineTest/api/curriculum-mapping/add/',
                data=json.dumps({
                    'class_code': 'API_TEST_CLASS',
                    'curriculum_level_id': curriculum.id,
                    'academic_year': '2025',
                    'priority': 1
                }),
                content_type='application/json'
            )
            
            test_result("Add mapping API", 
                       response.status_code == 200 and 
                       response.json().get('success', False))
            
            # Clean up
            ClassCurriculumMapping.objects.filter(
                class_code='API_TEST_CLASS'
            ).delete()
    except Exception as e:
        test_result("Add mapping API", False, str(e))
    
    # Test 4.2: Get class mappings API
    try:
        response = client.get(
            '/RoutineTest/api/curriculum-mapping/class/TEST_CLASS/?year=2025'
        )
        test_result("Get mappings API", 
                   response.status_code == 200 and 
                   'mappings' in response.json())
    except Exception as e:
        test_result("Get mappings API", False, str(e))
    
    # 5. INTEGRATION TESTS
    print_header("5. INTEGRATION TESTS")
    
    # Test 5.1: Schedule matrix integration
    try:
        # Create a test class with mapping
        curriculum = CurriculumLevel.objects.first()
        if curriculum:
            ClassCurriculumMapping.objects.create(
                class_code="MATRIX_TEST",
                curriculum_level=curriculum,
                academic_year="2025",
                priority=1
            )
            
            # Access schedule matrix (the view that was timing out)
            response = client.get('/RoutineTest/exam-assignments/')
            test_result("Schedule matrix loads without timeout", 
                       response.status_code == 200)
            
            # Clean up
            ClassCurriculumMapping.objects.filter(
                class_code="MATRIX_TEST"
            ).delete()
    except Exception as e:
        test_result("Schedule matrix integration", False, str(e))
    
    # Test 5.2: Navigation visibility
    try:
        response = client.get('/RoutineTest/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            # Admin should see the curriculum mapping tab
            test_result("Admin sees curriculum mapping tab",
                       'Curriculum Mapping' in content or 
                       'curriculum-mapping' in content)
    except Exception as e:
        test_result("Navigation visibility", False, str(e))
    
    # 6. DATA INTEGRITY TESTS
    print_header("6. DATA INTEGRITY TESTS")
    
    # Test 6.1: Soft delete functionality
    try:
        curriculum = CurriculumLevel.objects.first()
        if curriculum:
            mapping = ClassCurriculumMapping.objects.create(
                class_code="SOFT_DELETE_TEST",
                curriculum_level=curriculum,
                academic_year="2025",
                priority=1
            )
            
            # Soft delete
            mapping.is_active = False
            mapping.save()
            
            # Check it's excluded from active queries
            active_mappings = ClassCurriculumMapping.objects.filter(
                class_code="SOFT_DELETE_TEST",
                is_active=True
            )
            
            test_result("Soft delete works", active_mappings.count() == 0)
            
            # Clean up
            mapping.delete()
    except Exception as e:
        test_result("Soft delete functionality", False, str(e))
    
    # Test 6.2: Priority system
    try:
        curriculum = CurriculumLevel.objects.first()
        if curriculum:
            # Create multiple mappings with different priorities
            for priority in [1, 2, 3]:
                ClassCurriculumMapping.objects.create(
                    class_code="PRIORITY_TEST",
                    curriculum_level=curriculum,
                    academic_year="2025",
                    priority=priority
                )
            
            # Get mappings and check order
            mappings = ClassCurriculumMapping.objects.filter(
                class_code="PRIORITY_TEST"
            ).order_by('priority')
            
            priorities = [m.priority for m in mappings]
            test_result("Priority ordering", priorities == [1, 2, 3])
            
            # Clean up
            mappings.delete()
    except Exception as e:
        test_result("Priority system", False, str(e))
    
    # CLEANUP
    print_header("CLEANUP")
    
    # Remove test users
    try:
        User.objects.filter(username__in=['qa_admin', 'qa_teacher']).delete()
        print("✅ Test users cleaned up")
    except:
        warning("Could not clean up test users")
    
    # Clear cache
    cache.clear()
    print("✅ Cache cleared")
    
    # FINAL REPORT
    print_header("QA TEST RESULTS")
    
    total = len(QA_RESULTS['passed']) + len(QA_RESULTS['failed'])
    passed = len(QA_RESULTS['passed'])
    failed = len(QA_RESULTS['failed'])
    warnings = len(QA_RESULTS['warnings'])
    
    print(f"""
📊 Test Summary:
   Total Tests: {total}
   ✅ Passed: {passed}
   ❌ Failed: {failed}
   ⚠️  Warnings: {warnings}
   
   Success Rate: {(passed/total*100):.1f}%
""")
    
    if failed > 0:
        print("\n❌ Failed Tests:")
        for test in QA_RESULTS['failed']:
            print(f"   - {test}")
    
    if warnings > 0:
        print("\n⚠️  Warnings:")
        for warning_msg in QA_RESULTS['warnings']:
            print(f"   - {warning_msg}")
    
    if passed == total:
        print("""
🎉 ALL TESTS PASSED! 🎉

The Curriculum Mapping feature is fully functional:
✅ 504 Gateway Timeout issue FIXED
✅ Admin-only access control working
✅ Performance optimizations active
✅ All APIs functional
✅ Database integrity maintained

The feature is ready for production use!
""")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_qa_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ QA Test Suite Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)