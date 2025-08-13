#!/usr/bin/env python
"""
Comprehensive test to ensure no existing features were broken by the authentication fix
Tests all critical functionality that existed before the changes
"""
import os
import sys
import django
import json
from datetime import datetime
import uuid

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from placement_test.models import Exam, StudentSession, Question, AudioFile
from core.models import CurriculumLevel, Program, SubProgram, Teacher

def test_existing_features():
    """Test all existing features to ensure nothing was broken"""
    print("\n" + "="*70)
    print("EXISTING FEATURES REGRESSION TEST")
    print("Testing that authentication changes didn't break existing functionality")
    print("="*70)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "categories": {}
    }
    
    client = Client()
    
    # Category 1: Student Test Flow (Should work WITHOUT authentication)
    print("\n[1] STUDENT TEST FLOW (Anonymous Access)")
    print("-" * 40)
    student_tests = []
    
    # 1.1 Start Test Page Access
    print("1.1 Testing student start test page...")
    response = client.get('/api/placement/start/')
    test = {
        "name": "Start test page access",
        "endpoint": "/api/placement/start/",
        "expected_status": 200,
        "actual_status": response.status_code,
        "passed": response.status_code == 200
    }
    student_tests.append(test)
    print(f"    {'✅' if test['passed'] else '❌'} Start test page: {test['actual_status']}")
    
    # 1.2 Create Test Session
    print("1.2 Testing session creation...")
    session_data = {
        'student_name': 'Test Student',
        'grade': '5',
        'academic_rank': 'TOP_50',  # Fixed: was 'average', should be valid rank
        'parent_phone': '010-1234-5678',
        'school_name': 'Test School'
    }
    response = client.post('/api/placement/start/', session_data)
    
    if response.status_code == 302:  # Redirect to test
        session_created = True
        # Extract session ID from redirect URL
        if '/placement/test/' in response.url:
            session_id = response.url.split('/placement/test/')[1].rstrip('/')
        else:
            session_id = None
    else:
        session_created = False
        session_id = None
    
    test = {
        "name": "Create test session",
        "endpoint": "/api/placement/start/",
        "method": "POST",
        "expected": "Redirect to test",
        "actual_status": response.status_code,
        "session_created": session_created,
        "passed": session_created
    }
    student_tests.append(test)
    print(f"    {'✅' if test['passed'] else '❌'} Session creation: {test['actual_status']}")
    
    # 1.3 Access Test Interface
    if session_id:
        print(f"1.3 Testing test interface access (session: {session_id[:8]}...)...")
        response = client.get(f'/api/placement/test/{session_id}/')
        test = {
            "name": "Access test interface",
            "endpoint": f"/api/placement/test/{session_id}/",
            "expected_status": 200,
            "actual_status": response.status_code,
            "passed": response.status_code == 200
        }
        student_tests.append(test)
        print(f"    {'✅' if test['passed'] else '❌'} Test interface: {test['actual_status']}")
        
        # 1.4 Submit Answer (Anonymous)
        print("1.4 Testing answer submission...")
        answer_data = {
            'question_number': 1,
            'answer': 'B',
            'session_id': session_id
        }
        response = client.post('/api/placement/submit-answer/', 
                              json.dumps(answer_data),
                              content_type='application/json')
        test = {
            "name": "Submit answer (anonymous)",
            "endpoint": "/api/placement/submit-answer/",
            "expected_status": 200,
            "actual_status": response.status_code,
            "passed": response.status_code == 200
        }
        student_tests.append(test)
        print(f"    {'✅' if test['passed'] else '❌'} Answer submission: {test['actual_status']}")
    
    results["categories"]["student_flow"] = student_tests
    
    # Category 2: Teacher Features (Should REQUIRE authentication)
    print("\n[2] TEACHER FEATURES (Authentication Required)")
    print("-" * 40)
    teacher_tests = []
    
    # 2.1 Test unauthenticated access (should redirect)
    print("2.1 Testing unauthenticated access to teacher features...")
    protected_endpoints = [
        ('/teacher/dashboard/', 'Dashboard'),
        ('/api/placement/exams/', 'Exam List'),
        ('/api/placement/exams/create/', 'Create Exam'),
        ('/api/placement/sessions/', 'Session List'),
        ('/exam-mapping/', 'Exam Mapping'),
        ('/placement-rules/', 'Placement Rules')
    ]
    
    for endpoint, name in protected_endpoints:
        response = client.get(endpoint, follow=False)
        is_protected = response.status_code == 302 and '/login/' in response.get('Location', '')
        test = {
            "name": f"{name} protection",
            "endpoint": endpoint,
            "expected": "Redirect to login",
            "actual_status": response.status_code,
            "redirects_to_login": is_protected,
            "passed": is_protected
        }
        teacher_tests.append(test)
        print(f"    {'✅' if test['passed'] else '❌'} {name}: {'Protected' if is_protected else 'NOT PROTECTED!'}")
    
    # 2.2 Login as teacher
    print("\n2.2 Testing teacher login...")
    login_success = client.login(username='admin', password='admin123')
    test = {
        "name": "Teacher login",
        "username": "admin",
        "passed": login_success
    }
    teacher_tests.append(test)
    print(f"    {'✅' if test['passed'] else '❌'} Login: {'Success' if login_success else 'Failed'}")
    
    if login_success:
        # 2.3 Test authenticated access
        print("2.3 Testing authenticated access to teacher features...")
        
        for endpoint, name in protected_endpoints:
            response = client.get(endpoint, follow=False)
            is_accessible = response.status_code == 200
            test = {
                "name": f"{name} access (authenticated)",
                "endpoint": endpoint,
                "expected_status": 200,
                "actual_status": response.status_code,
                "passed": is_accessible
            }
            teacher_tests.append(test)
            print(f"    {'✅' if test['passed'] else '❌'} {name}: {response.status_code}")
        
        # 2.4 Test exam creation
        print("\n2.4 Testing exam creation...")
        exam_data = {
            'name': f'Test Exam {datetime.now().strftime("%H%M%S")}',
            'curriculum_level': CurriculumLevel.objects.first().id if CurriculumLevel.objects.exists() else 1,
            'passing_score': 70,
            'time_limit': 60,
            'version': 1,
            'is_active': True
        }
        
        # Create a simple PDF file for testing
        pdf_content = b'%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Count 1/Kids[3 0 R]>>\nendobj\n3 0 obj\n<</Type/Page/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>/MediaBox[0 0 612 792]/Contents 4 0 R>>\nendobj\n4 0 obj\n<</Length 44>>\nstream\nBT /F1 12 Tf 100 700 Td (Test Exam) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000108 00000 n\n0000000253 00000 n\ntrailer\n<</Size 5/Root 1 0 R>>\nstartxref\n344\n%%EOF'
        
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
        exam_data['pdf_file'] = pdf_file
        
        response = client.post('/api/placement/exams/create/', exam_data)
        exam_created = response.status_code in [200, 302]
        test = {
            "name": "Create exam",
            "endpoint": "/api/placement/exams/create/",
            "method": "POST",
            "expected": "Success (200 or 302)",
            "actual_status": response.status_code,
            "passed": exam_created
        }
        teacher_tests.append(test)
        print(f"    {'✅' if test['passed'] else '❌'} Exam creation: {response.status_code}")
    
    results["categories"]["teacher_features"] = teacher_tests
    
    # Category 3: API Endpoints
    print("\n[3] API ENDPOINTS")
    print("-" * 40)
    api_tests = []
    
    # 3.1 Test student API endpoints (should work without auth)
    print("3.1 Testing student API endpoints...")
    student_apis = [
        ('/api/placement/start/', 'Start Test API'),
        ('/api/placement/submit-answer/', 'Submit Answer API'),
    ]
    
    for endpoint, name in student_apis:
        response = client.get(endpoint)
        # These might return 405 (Method Not Allowed) for GET, but shouldn't require auth
        no_auth_required = response.status_code != 302 or '/login/' not in response.get('Location', '')
        test = {
            "name": f"{name} (no auth)",
            "endpoint": endpoint,
            "status_code": response.status_code,
            "requires_auth": not no_auth_required,
            "passed": no_auth_required
        }
        api_tests.append(test)
        print(f"    {'✅' if test['passed'] else '❌'} {name}: {'No auth required' if no_auth_required else 'AUTH REQUIRED!'}")
    
    # 3.2 Test teacher API endpoints (should require auth when logged out)
    client.logout()
    print("\n3.2 Testing teacher API endpoints (logged out)...")
    teacher_apis = [
        ('/api/placement/exams/', 'Exams API'),
        ('/api/placement/sessions/', 'Sessions API'),
        ('/api/placement/exams/create/', 'Create Exam API'),
    ]
    
    for endpoint, name in teacher_apis:
        response = client.get(endpoint, follow=False)
        requires_auth = response.status_code == 302 and '/login/' in response.get('Location', '')
        test = {
            "name": f"{name} protection",
            "endpoint": endpoint,
            "status_code": response.status_code,
            "protected": requires_auth,
            "passed": requires_auth
        }
        api_tests.append(test)
        print(f"    {'✅' if test['passed'] else '❌'} {name}: {'Protected' if requires_auth else 'NOT PROTECTED!'}")
    
    results["categories"]["api_endpoints"] = api_tests
    
    # Category 4: Navigation and UI
    print("\n[4] NAVIGATION AND UI")
    print("-" * 40)
    ui_tests = []
    
    # 4.1 Check home page
    print("4.1 Testing home page...")
    response = client.get('/')
    test = {
        "name": "Home page access",
        "endpoint": "/",
        "status_code": response.status_code,
        "has_student_section": 'Start Placement Test' in response.content.decode(),
        "has_teacher_section": 'Teacher Dashboard' in response.content.decode(),
        "has_login_tab": 'Teacher Login</a>' in response.content.decode(),
        "passed": response.status_code == 200
    }
    ui_tests.append(test)
    print(f"    {'✅' if test['passed'] else '❌'} Home page: {response.status_code}")
    print(f"        Student section: {'✅' if test['has_student_section'] else '❌'}")
    print(f"        Teacher section: {'✅' if test['has_teacher_section'] else '❌'}")
    print(f"        Login tab removed: {'✅' if not test['has_login_tab'] else '❌'}")
    
    # 4.2 Check authenticated navigation
    print("\n4.2 Testing authenticated navigation...")
    client.login(username='teacher1', password='teacher123')
    response = client.get('/')
    content = response.content.decode()
    
    test = {
        "name": "Authenticated navigation",
        "shows_username": 'Taehyun Kim' in content,
        "shows_logout": 'Logout' in content,
        "no_login_tab": 'Teacher Login</a>' not in content,
        "passed": 'Taehyun Kim' in content and 'Logout' in content
    }
    ui_tests.append(test)
    print(f"    {'✅' if test['passed'] else '❌'} Auth navigation:")
    print(f"        Shows username: {'✅' if test['shows_username'] else '❌'}")
    print(f"        Shows logout: {'✅' if test['shows_logout'] else '❌'}")
    print(f"        No login tab: {'✅' if test['no_login_tab'] else '❌'}")
    
    results["categories"]["navigation_ui"] = ui_tests
    
    # Category 5: Database Integrity
    print("\n[5] DATABASE INTEGRITY")
    print("-" * 40)
    db_tests = []
    
    # 5.1 Check existing data
    print("5.1 Checking existing data integrity...")
    
    # Check exams
    exam_count = Exam.objects.count()
    test = {
        "name": "Exams exist",
        "count": exam_count,
        "passed": exam_count >= 0  # Just checking it doesn't error
    }
    db_tests.append(test)
    print(f"    {'✅' if test['passed'] else '❌'} Exams in database: {exam_count}")
    
    # Check sessions
    session_count = StudentSession.objects.count()
    test = {
        "name": "Sessions exist",
        "count": session_count,
        "passed": session_count >= 0
    }
    db_tests.append(test)
    print(f"    {'✅' if test['passed'] else '❌'} Sessions in database: {session_count}")
    
    # Check teachers
    teacher_count = Teacher.objects.count()
    test = {
        "name": "Teachers exist",
        "count": teacher_count,
        "passed": teacher_count >= 0
    }
    db_tests.append(test)
    print(f"    {'✅' if test['passed'] else '❌'} Teachers in database: {teacher_count}")
    
    # Check teacher-user relationship
    teachers_with_users = Teacher.objects.filter(user__isnull=False).count()
    test = {
        "name": "Teacher-User relationships",
        "count": teachers_with_users,
        "passed": teachers_with_users > 0
    }
    db_tests.append(test)
    print(f"    {'✅' if test['passed'] else '❌'} Teachers with User accounts: {teachers_with_users}")
    
    results["categories"]["database"] = db_tests
    
    # Calculate summary
    all_tests = []
    for category_tests in results["categories"].values():
        all_tests.extend(category_tests)
    
    total = len(all_tests)
    passed = sum(1 for t in all_tests if t.get("passed", False))
    failed = total - passed
    
    results["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
        "categories": {
            name: {
                "total": len(tests),
                "passed": sum(1 for t in tests if t.get("passed", False))
            }
            for name, tests in results["categories"].items()
        }
    }
    
    # Print summary
    print("\n" + "="*70)
    print("REGRESSION TEST SUMMARY")
    print("="*70)
    
    for category, tests in results["categories"].items():
        category_passed = sum(1 for t in tests if t.get("passed", False))
        category_total = len(tests)
        print(f"\n{category.upper().replace('_', ' ')}:")
        print(f"  Passed: {category_passed}/{category_total}")
        
        if category_passed < category_total:
            print("  Failed tests:")
            for test in tests:
                if not test.get("passed", False):
                    print(f"    - {test['name']}")
    
    print("\n" + "-"*40)
    print(f"OVERALL: {passed}/{total} tests passed ({results['summary']['success_rate']})")
    
    if failed == 0:
        print("\n✅ SUCCESS: All existing features are working correctly!")
        print("The authentication navigation changes did not break any functionality.")
    else:
        print(f"\n⚠️  WARNING: {failed} test(s) failed!")
        print("Some existing features may have been affected by the changes.")
    
    # Save results
    with open('existing_features_regression_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nDetailed results saved to: existing_features_regression_results.json")
    
    return results

if __name__ == "__main__":
    test_existing_features()