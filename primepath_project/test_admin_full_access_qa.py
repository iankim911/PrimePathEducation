#!/usr/bin/env python
"""
Comprehensive QA Test for Admin Full Access Fix
Tests that admins have automatic access to ALL classes without needing to request
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.test import Client, RequestFactory
from django.urls import reverse
from core.models import Teacher
from primepath_routinetest.models import (
    TeacherClassAssignment, ClassAccessRequest, 
    Exam, StudentRoster
)
from primepath_routinetest.views.class_access import (
    is_admin_or_head_teacher, check_admin_access
)

# Test configuration
TEST_RESULTS = {
    'passed': [],
    'failed': [],
    'warnings': [],
    'timestamp': datetime.now().isoformat()
}

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")

def test_result(test_name, passed, details=""):
    """Record test result"""
    result = {
        'test': test_name,
        'passed': passed,
        'details': details,
        'timestamp': datetime.now().isoformat()
    }
    
    if passed:
        TEST_RESULTS['passed'].append(result)
        print(f"✅ {test_name}")
        if details:
            print(f"   {details}")
    else:
        TEST_RESULTS['failed'].append(result)
        print(f"❌ {test_name}")
        if details:
            print(f"   ERROR: {details}")

def warning(message):
    """Record a warning"""
    TEST_RESULTS['warnings'].append({
        'message': message,
        'timestamp': datetime.now().isoformat()
    })
    print(f"⚠️  WARNING: {message}")

def run_admin_access_qa():
    """Run comprehensive QA tests for admin access"""
    
    print_header("ADMIN FULL ACCESS QA TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. ADMIN USER SETUP
    print_header("1. ADMIN USER VERIFICATION")
    
    try:
        # Get admin user
        admin_user = User.objects.get(username='admin')
        test_result("Admin user exists", True, f"Username: {admin_user.username}")
        
        # Verify admin privileges
        test_result("Admin is superuser", admin_user.is_superuser)
        test_result("Admin is staff", admin_user.is_staff)
        
        # Check teacher profile
        try:
            admin_teacher = Teacher.objects.get(user=admin_user)
            test_result("Admin has teacher profile", True, 
                       f"Is head teacher: {admin_teacher.is_head_teacher}")
        except Teacher.DoesNotExist:
            test_result("Admin has teacher profile", False, 
                       "No teacher profile found")
            
    except User.DoesNotExist:
        test_result("Admin user exists", False, "User 'admin' not found")
        print("\n⚠️  Cannot continue tests without admin user")
        return False
    
    # 2. ADMIN DETECTION FUNCTION TEST
    print_header("2. ADMIN DETECTION FUNCTION")
    
    try:
        is_admin, teacher = is_admin_or_head_teacher(admin_user)
        test_result("is_admin_or_head_teacher() works", is_admin,
                   f"Detected as admin: {is_admin}")
        
        if teacher:
            test_result("Function returns teacher object", True,
                       f"Teacher: {teacher.name}")
        else:
            test_result("Function returns teacher object", False,
                       "No teacher object returned")
            
    except Exception as e:
        test_result("is_admin_or_head_teacher() works", False, str(e))
    
    # 3. CLASS ACCESS CHECK
    print_header("3. ADMIN CLASS ACCESS VERIFICATION")
    
    try:
        # Get all class codes
        all_class_codes = [choice[0] for choice in 
                          TeacherClassAssignment._meta.get_field('class_code').choices]
        
        print(f"   Testing access to {len(all_class_codes)} classes...")
        
        # Test admin access to each class
        access_results = []
        for class_code in all_class_codes:
            has_access = check_admin_access(admin_user, class_code)
            access_results.append(has_access)
            if not has_access:
                print(f"   ❌ No access to {class_code}")
        
        all_access = all(access_results)
        test_result("Admin has access to ALL classes", all_access,
                   f"Access to {sum(access_results)}/{len(all_class_codes)} classes")
        
    except Exception as e:
        test_result("Admin class access check", False, str(e))
    
    # 4. WEB INTERFACE TEST
    print_header("4. WEB INTERFACE TEST")
    
    client = Client()
    factory = RequestFactory()
    
    try:
        # Login as admin
        login_success = client.login(username='admin', password='admin123')
        test_result("Admin can login", login_success)
        
        if login_success:
            # Test class access page
            response = client.get('/RoutineTest/access/my-classes/')
            test_result("Class access page loads", response.status_code == 200,
                       f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for admin indicators
                has_admin_banner = 'ADMIN MODE' in content or 'FULL ACCESS' in content
                test_result("Admin banner displayed", has_admin_banner)
                
                # Check that "No Classes Assigned" is NOT shown
                no_classes_shown = 'No Classes Assigned Yet' in content
                test_result("'No Classes Assigned' NOT shown", not no_classes_shown,
                           "Admin should see all classes, not 'No Classes'")
                
                # Check for switch view option
                has_switch = 'Switch to' in content
                test_result("Switch view option available", has_switch)
                
                # Count classes shown
                class_count = content.count('class-card') or content.count('admin-class-card')
                test_result("Classes are displayed", class_count > 0,
                           f"Found {class_count} class cards")
                
    except Exception as e:
        test_result("Web interface test", False, str(e))
    
    # 5. ADMIN VIEW MODE TEST
    print_header("5. ADMIN VIEW MODE TEST")
    
    try:
        # Test with admin_view=true
        response = client.get('/RoutineTest/access/my-classes/?admin_view=true')
        test_result("Admin view mode loads", response.status_code == 200)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            has_full_access = 'ADMIN FULL ACCESS' in content or 'FULL ACCESS' in content
            test_result("Full access indicator shown", has_full_access)
        
        # Test with admin_view=false (teacher mode)
        response = client.get('/RoutineTest/access/my-classes/?admin_view=false')
        test_result("Teacher view mode loads", response.status_code == 200)
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            has_teacher_mode = 'TEACHER MODE' in content or 'Teacher View' in content
            test_result("Teacher mode indicator shown", has_teacher_mode)
            
    except Exception as e:
        test_result("View mode test", False, str(e))
    
    # 6. CONSOLE LOGGING TEST
    print_header("6. CONSOLE LOGGING VERIFICATION")
    
    try:
        # Check if logging is working by examining the response
        response = client.get('/RoutineTest/access/my-classes/?debug=true')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for debug elements
            has_debug = 'DEBUG MODE' in content or 'debug-info' in content
            test_result("Debug mode works", has_debug)
            
            # Check for console logging scripts
            has_console_logs = 'console.log' in content or 'console.group' in content
            test_result("Console logging included", has_console_logs)
            
            # Check for tracking scripts
            has_tracker = 'AdminAccessTracker' in content
            test_result("Admin action tracking included", has_tracker)
            
    except Exception as e:
        test_result("Console logging test", False, str(e))
    
    # 7. REGULAR TEACHER COMPARISON
    print_header("7. REGULAR TEACHER COMPARISON")
    
    try:
        # Create or get a regular teacher
        regular_user, created = User.objects.get_or_create(
            username='test_teacher_qa',
            defaults={'email': 'teacher@test.com'}
        )
        
        if created:
            regular_user.set_password('test123')
            regular_user.save()
        
        # Create teacher profile
        regular_teacher, _ = Teacher.objects.get_or_create(
            user=regular_user,
            defaults={
                'email': regular_user.email,
                'name': 'Test Teacher',
                'is_head_teacher': False
            }
        )
        
        # Login as regular teacher
        client.logout()
        client.login(username='test_teacher_qa', password='test123')
        
        response = client.get('/RoutineTest/access/my-classes/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Regular teacher should NOT see admin options
            has_admin_features = 'ADMIN MODE' in content or 'Switch to Admin View' in content
            test_result("Regular teacher doesn't see admin features", 
                       not has_admin_features)
            
            # Should see request access section
            has_request_section = 'Request' in content or 'Available Classes' in content
            test_result("Regular teacher sees request section", has_request_section)
            
        # Clean up
        if created:
            regular_user.delete()
            
    except Exception as e:
        test_result("Regular teacher comparison", False, str(e))
    
    # 8. PERFORMANCE TEST
    print_header("8. PERFORMANCE TEST")
    
    try:
        import time
        
        # Login as admin again
        client.logout()
        client.login(username='admin', password='admin123')
        
        # Time the admin view load
        start = time.time()
        response = client.get('/RoutineTest/access/my-classes/')
        load_time = time.time() - start
        
        test_result("Page loads within 2 seconds", load_time < 2.0,
                   f"Load time: {load_time:.3f}s")
        
        # Check response size is reasonable
        if response.status_code == 200:
            content_size = len(response.content)
            test_result("Response size reasonable", content_size < 500000,
                       f"Size: {content_size/1024:.1f}KB")
            
    except Exception as e:
        test_result("Performance test", False, str(e))
    
    # FINAL REPORT
    print_header("QA TEST RESULTS SUMMARY")
    
    total = len(TEST_RESULTS['passed']) + len(TEST_RESULTS['failed'])
    passed = len(TEST_RESULTS['passed'])
    failed = len(TEST_RESULTS['failed'])
    warnings_count = len(TEST_RESULTS['warnings'])
    
    print(f"""
📊 Test Summary:
   Total Tests: {total}
   ✅ Passed: {passed}
   ❌ Failed: {failed}
   ⚠️  Warnings: {warnings_count}
   
   Success Rate: {(passed/total*100):.1f}%
   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    if failed > 0:
        print("\n❌ Failed Tests:")
        for test in TEST_RESULTS['failed']:
            print(f"   - {test['test']}: {test['details']}")
    
    if warnings_count > 0:
        print("\n⚠️  Warnings:")
        for warning_item in TEST_RESULTS['warnings']:
            print(f"   - {warning_item['message']}")
    
    # Write results to JSON file
    results_file = f"qa_results_admin_access_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(TEST_RESULTS, f, indent=2)
    print(f"\n📄 Results saved to: {results_file}")
    
    if passed == total:
        print("""
🎉 ALL TESTS PASSED! 🎉

✅ Admin Full Access Fix is WORKING:
   - Admin automatically has access to ALL classes
   - No need to request access
   - Proper UI showing full access
   - Switch between admin and teacher views
   - Console logging working
   - Performance acceptable

The admin access issue is COMPLETELY FIXED!
""")
    else:
        print(f"""
⚠️  SOME TESTS FAILED

Please review the failed tests above.
The admin access fix may need additional adjustments.
""")
    
    return passed == total

if __name__ == "__main__":
    try:
        print("\n" + "="*80)
        print("  STARTING ADMIN FULL ACCESS QA TEST")
        print("="*80)
        
        success = run_admin_access_qa()
        
        if success:
            print("\n✅ QA PASSED - Admin access fix is working correctly!")
            sys.exit(0)
        else:
            print("\n⚠️  QA FAILED - Some issues detected")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ QA Test Suite Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)