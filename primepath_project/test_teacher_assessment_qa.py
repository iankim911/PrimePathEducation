#!/usr/bin/env python
"""
QA Test: Teacher Assessment Module
Comprehensive testing of admin-only Teacher Class Assessment features

Created: August 18, 2025
"""
import os
import sys
import django
import json
from datetime import datetime, timedelta

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from core.models import Teacher
from primepath_routinetest.models import (
    TeacherClassAssignment,
    ClassAccessRequest,
    AccessAuditLog
)

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")

def print_test(test_name, result, details=""):
    if result:
        status = f"{Colors.OKGREEN}✅ PASS{Colors.ENDC}"
    else:
        status = f"{Colors.FAIL}❌ FAIL{Colors.ENDC}"
    
    print(f"  {status} - {test_name}")
    if details:
        print(f"        {Colors.OKCYAN}{details}{Colors.ENDC}")

def test_teacher_assessment_module():
    """Comprehensive QA testing of Teacher Assessment module"""
    
    print_header("TEACHER ASSESSMENT MODULE - QA TEST SUITE")
    print(f"Test Started: {datetime.now()}")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    client = Client()
    
    # Test 1: Check if URLs are registered
    print(f"\n{Colors.BOLD}[TEST GROUP 1] URL Registration{Colors.ENDC}")
    
    try:
        url = reverse('RoutineTest:teacher_assessment')
        test_result = True
        details = f"URL: {url}"
    except:
        test_result = False
        details = "URL not found"
    
    print_test("Teacher Assessment URL registered", test_result, details)
    results['total'] += 1
    if test_result:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 2: Check admin access requirement
    print(f"\n{Colors.BOLD}[TEST GROUP 2] Access Control{Colors.ENDC}")
    
    # Test as anonymous user
    response = client.get('/RoutineTest/assessment/dashboard/')
    test_result = response.status_code == 302  # Should redirect
    print_test("Anonymous user blocked", test_result, f"Status: {response.status_code}")
    results['total'] += 1
    if test_result:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test as regular teacher (non-admin)
    regular_teacher = Teacher.objects.filter(is_head_teacher=False).first()
    if regular_teacher and regular_teacher.user:
        client.force_login(regular_teacher.user)
        response = client.get('/RoutineTest/assessment/dashboard/')
        test_result = response.status_code in [302, 403]  # Should be blocked
        print_test("Regular teacher blocked", test_result, f"Status: {response.status_code}")
        results['total'] += 1
        if test_result:
            results['passed'] += 1
        else:
            results['failed'] += 1
        client.logout()
    
    # Test 3: Admin access with proper mode
    print(f"\n{Colors.BOLD}[TEST GROUP 3] Admin Access{Colors.ENDC}")
    
    admin = User.objects.filter(is_superuser=True).first()
    if admin:
        client.force_login(admin)
        
        # Set admin mode in session
        session = client.session
        session['view_mode'] = 'Admin'
        session.save()
        
        response = client.get('/RoutineTest/assessment/dashboard/')
        test_result = response.status_code == 200
        print_test("Admin can access in Admin mode", test_result, f"Status: {response.status_code}")
        results['total'] += 1
        if test_result:
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Test in Teacher mode (should redirect)
        session['view_mode'] = 'Teacher'
        session.save()
        
        response = client.get('/RoutineTest/assessment/dashboard/')
        test_result = response.status_code == 302
        print_test("Admin blocked in Teacher mode", test_result, f"Status: {response.status_code}")
        results['total'] += 1
        if test_result:
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Switch back to Admin mode for remaining tests
        session['view_mode'] = 'Admin'
        session.save()
    
    # Test 4: Data integrity checks
    print(f"\n{Colors.BOLD}[TEST GROUP 4] Data Integrity{Colors.ENDC}")
    
    # Check teachers exist
    teacher_count = Teacher.objects.count()
    test_result = teacher_count >= 20
    print_test("20+ teachers created", test_result, f"Found: {teacher_count}")
    results['total'] += 1
    if test_result:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Check assignments exist
    assignment_count = TeacherClassAssignment.objects.filter(is_active=True).count()
    test_result = assignment_count > 0
    print_test("Class assignments exist", test_result, f"Found: {assignment_count}")
    results['total'] += 1
    if test_result:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Check pending requests exist
    request_count = ClassAccessRequest.objects.filter(status='PENDING').count()
    test_result = request_count > 0
    print_test("Pending requests exist", test_result, f"Found: {request_count}")
    results['total'] += 1
    if test_result:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 5: Approval workflow
    print(f"\n{Colors.BOLD}[TEST GROUP 5] Approval/Denial Workflow{Colors.ENDC}")
    
    if admin:
        # Get a pending request
        pending_request = ClassAccessRequest.objects.filter(status='PENDING').first()
        
        if pending_request:
            request_id = str(pending_request.id)
            
            # Test approval endpoint
            response = client.post(
                f'/RoutineTest/assessment/approve/{request_id}/',
                content_type='application/json'
            )
            
            test_result = response.status_code == 200
            if test_result:
                data = json.loads(response.content)
                test_result = data.get('success', False)
            
            print_test("Request approval works", test_result, f"Request ID: {request_id[:8]}...")
            results['total'] += 1
            if test_result:
                results['passed'] += 1
                # Check if assignment was created
                pending_request.refresh_from_db()
                test_result = pending_request.status == 'APPROVED'
                print_test("Request status updated", test_result, f"Status: {pending_request.status}")
                results['total'] += 1
                if test_result:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
            else:
                results['failed'] += 1
        
        # Test denial endpoint
        pending_request = ClassAccessRequest.objects.filter(status='PENDING').first()
        if pending_request:
            request_id = str(pending_request.id)
            
            response = client.post(
                f'/RoutineTest/assessment/deny/{request_id}/',
                json.dumps({'reason': 'Test denial'}),
                content_type='application/json'
            )
            
            test_result = response.status_code == 200
            if test_result:
                data = json.loads(response.content)
                test_result = data.get('success', False)
            
            print_test("Request denial works", test_result, f"Request ID: {request_id[:8]}...")
            results['total'] += 1
            if test_result:
                results['passed'] += 1
            else:
                results['failed'] += 1
    
    # Test 6: Direct assignment
    print(f"\n{Colors.BOLD}[TEST GROUP 6] Direct Assignment{Colors.ENDC}")
    
    if admin:
        # Find a teacher without certain class
        teacher = Teacher.objects.first()
        available_classes = ['CLASS_10C', 'CLASS_10B']
        
        for class_code in available_classes:
            existing = TeacherClassAssignment.objects.filter(
                teacher=teacher,
                class_code=class_code,
                is_active=True
            ).exists()
            
            if not existing:
                response = client.post(
                    '/RoutineTest/assessment/direct-assign/',
                    json.dumps({
                        'teacher_id': teacher.id,
                        'class_code': class_code,
                        'access_level': 'FULL',
                        'notes': 'QA test assignment'
                    }),
                    content_type='application/json'
                )
                
                test_result = response.status_code == 200
                if test_result:
                    data = json.loads(response.content)
                    test_result = data.get('success', False)
                
                print_test("Direct assignment works", test_result, f"{teacher.name} → {class_code}")
                results['total'] += 1
                if test_result:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                break
    
    # Test 7: Revocation
    print(f"\n{Colors.BOLD}[TEST GROUP 7] Access Revocation{Colors.ENDC}")
    
    if admin:
        # Get an active assignment
        assignment = TeacherClassAssignment.objects.filter(is_active=True).first()
        
        if assignment:
            response = client.post(
                '/RoutineTest/assessment/revoke/',
                json.dumps({
                    'assignment_id': str(assignment.id),
                    'reason': 'QA test revocation'
                }),
                content_type='application/json'
            )
            
            test_result = response.status_code == 200
            if test_result:
                data = json.loads(response.content)
                test_result = data.get('success', False)
            
            print_test("Access revocation works", test_result, f"Assignment: {str(assignment.id)[:8]}...")
            results['total'] += 1
            if test_result:
                results['passed'] += 1
                # Check if assignment was deactivated
                assignment.refresh_from_db()
                test_result = not assignment.is_active
                print_test("Assignment deactivated", test_result, f"Active: {assignment.is_active}")
                results['total'] += 1
                if test_result:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
            else:
                results['failed'] += 1
    
    # Test 8: Audit logging
    print(f"\n{Colors.BOLD}[TEST GROUP 8] Audit Logging{Colors.ENDC}")
    
    recent_logs = AccessAuditLog.objects.filter(
        timestamp__gte=timezone.now() - timedelta(minutes=5)
    ).count()
    
    test_result = recent_logs > 0
    print_test("Audit logs created", test_result, f"Recent logs: {recent_logs}")
    results['total'] += 1
    if test_result:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 9: Navigation visibility
    print(f"\n{Colors.BOLD}[TEST GROUP 9] Navigation Visibility{Colors.ENDC}")
    
    if admin:
        response = client.get('/RoutineTest/classes-exams/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check if Teacher Assessment tab is visible in Admin mode
            test_result = 'Teacher Assessment' in content and 'teacher-assessment-tab' in content
            print_test("Teacher Assessment tab visible in Admin mode", test_result)
            results['total'] += 1
            if test_result:
                results['passed'] += 1
            else:
                results['failed'] += 1
            
            # Switch to Teacher mode and check
            session = client.session
            session['view_mode'] = 'Teacher'
            session.save()
            
            response = client.get('/RoutineTest/classes-exams/')
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                test_result = 'teacher-assessment-tab' not in content or 'display: none' in content
                print_test("Teacher Assessment tab hidden in Teacher mode", test_result)
                results['total'] += 1
                if test_result:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
    
    # Test 10: Template rendering
    print(f"\n{Colors.BOLD}[TEST GROUP 10] Template Rendering{Colors.ENDC}")
    
    if admin:
        # Switch back to Admin mode
        session = client.session
        session['view_mode'] = 'Admin'
        session.save()
        
        response = client.get('/RoutineTest/assessment/dashboard/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check key elements
            elements = [
                ('Statistics bar', 'stats-bar'),
                ('Teacher list', 'teacher-list'),
                ('Request cards', 'request-card' if request_count > 0 else 'empty-state'),
                ('Class matrix', 'class-matrix'),
                ('Admin badge', 'admin-badge'),
            ]
            
            for element_name, element_id in elements:
                test_result = element_id in content
                print_test(f"{element_name} rendered", test_result)
                results['total'] += 1
                if test_result:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
    
    # Summary
    print_header("TEST SUMMARY")
    print(f"{Colors.BOLD}Total Tests:{Colors.ENDC} {results['total']}")
    print(f"{Colors.OKGREEN}Passed:{Colors.ENDC} {results['passed']}")
    print(f"{Colors.FAIL}Failed:{Colors.ENDC} {results['failed']}")
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    
    if success_rate == 100:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Success Rate: {success_rate:.1f}%{Colors.ENDC}")
    elif success_rate >= 80:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️ MOSTLY PASSED. Success Rate: {success_rate:.1f}%{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ TESTS FAILED. Success Rate: {success_rate:.1f}%{Colors.ENDC}")
    
    # Save results
    results['timestamp'] = datetime.now().isoformat()
    results['success_rate'] = success_rate
    
    with open('qa_teacher_assessment_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{Colors.OKCYAN}Results saved to: qa_teacher_assessment_results.json{Colors.ENDC}")
    print(f"{Colors.BOLD}Test Completed: {datetime.now()}{Colors.ENDC}")
    
    return success_rate >= 80

if __name__ == '__main__':
    success = test_teacher_assessment_module()
    sys.exit(0 if success else 1)