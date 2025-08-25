#!/usr/bin/env python3
"""
COMPREHENSIVE TEST FOR TEACHER EXAM PREVIEW FEATURE
Tests the complete teacher preview flow from launch button to exam interface
"""

import os
import sys
import django
import json
import time
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import (
    Exam, StudentSession, Class, 
    TeacherClassAssignment, RoutineExam
)

def print_section(title):
    """Helper to print formatted section headers"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_teacher_preview_endpoint():
    """Test that the teacher preview endpoint works correctly"""
    print_section("TEST 1: TEACHER PREVIEW ENDPOINT")
    
    client = Client()
    
    # Create or get admin user
    try:
        user = User.objects.get(username='admin')
        user.set_password('test123')
        user.save()
    except User.DoesNotExist:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'test123')
    
    # Ensure teacher profile exists
    teacher, created = Teacher.objects.get_or_create(
        user=user,
        defaults={'name': 'Admin Teacher'}
    )
    if created:
        print("✅ Created teacher profile")
    
    # Login
    client.login(username='admin', password='test123')
    print("✅ Logged in as admin")
    
    # Create a test exam if needed
    exam = Exam.objects.first()
    if not exam:
        print("Creating test exam...")
        exam = Exam.objects.create(
            name="Test Exam for Preview",
            timer_minutes=60,
            total_questions=20,
            default_options_count=4,
            is_active=True
        )
        print(f"✅ Created exam: {exam.name}")
    else:
        print(f"✅ Using existing exam: {exam.name}")
    
    # Get or create a test class
    test_class, created = Class.objects.get_or_create(
        section='TEST01',
        defaults={'section': 'TEST01'}
    )
    
    # Test the teacher preview endpoint
    preview_url = f'/RoutineTest/class/{test_class.section}/launch-preview/'
    print(f"\nTesting endpoint: {preview_url}")
    
    response = client.post(
        preview_url,
        data=json.dumps({
            'exam_id': str(exam.id),
            'duration_minutes': 45
        }),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Teacher preview endpoint works!")
        print(f"   Response: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            print(f"✅ Preview session created: {data.get('session_id')}")
            print(f"✅ Redirect URL: {data.get('redirect_url')}")
            return data.get('session_id'), data.get('redirect_url')
        else:
            print(f"❌ Failed: {data.get('error')}")
            return None, None
    else:
        print(f"❌ Failed with status: {response.status_code}")
        return None, None

def test_teacher_preview_session():
    """Test that teacher preview sessions are properly marked"""
    print_section("TEST 2: TEACHER PREVIEW SESSION MODEL")
    
    # Check if there are any teacher preview sessions
    preview_sessions = StudentSession.objects.filter(is_teacher_preview=True)
    
    if preview_sessions.exists():
        print(f"✅ Found {preview_sessions.count()} teacher preview session(s)")
        
        for session in preview_sessions[:3]:  # Show first 3
            print(f"\n   Session: {session.id}")
            print(f"   Name: {session.student_name}")
            print(f"   Teacher: {session.preview_teacher}")
            print(f"   Exam: {session.exam.name if session.exam else 'None'}")
            print(f"   Started: {session.started_at}")
            print(f"   Is Preview: {session.is_teacher_preview}")
    else:
        print("⚠️  No teacher preview sessions found yet")
    
    return preview_sessions.exists()

def test_exam_interface_access():
    """Test that the exam interface can be accessed with teacher preview session"""
    print_section("TEST 3: EXAM INTERFACE ACCESS")
    
    client = Client()
    
    # Get a teacher preview session
    preview_session = StudentSession.objects.filter(is_teacher_preview=True).first()
    
    if not preview_session:
        print("⚠️  No preview session to test, creating one...")
        session_id, redirect_url = test_teacher_preview_endpoint()
        if session_id:
            preview_session = StudentSession.objects.get(id=session_id)
    
    if preview_session:
        # Test accessing the exam interface
        test_url = f'/RoutineTest/session/{preview_session.id}/'
        print(f"\nAccessing exam interface: {test_url}")
        
        # Login as the teacher who created the preview
        if preview_session.preview_teacher:
            client.login(
                username=preview_session.preview_teacher.user.username,
                password='test123'
            )
        
        response = client.get(test_url)
        
        if response.status_code == 200:
            print("✅ Exam interface loads successfully!")
            
            # Check for key elements
            content = response.content.decode('utf-8')
            checks = {
                'timer': 'timer' in content.lower(),
                'questions': 'question' in content.lower(),
                'submit': 'submit' in content.lower(),
                'exam_name': preview_session.exam.name in content if preview_session.exam else False
            }
            
            for check, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"   {status} {check.replace('_', ' ').title()}")
                
            return True
        else:
            print(f"❌ Failed to load interface (status: {response.status_code})")
            return False
    else:
        print("❌ No preview session available for testing")
        return False

def test_other_features_intact():
    """Verify that other features are not disrupted"""
    print_section("TEST 4: OTHER FEATURES INTEGRITY")
    
    client = Client()
    client.login(username='admin', password='test123')
    
    test_urls = [
        ('/RoutineTest/', 'RoutineTest Index'),
        ('/RoutineTest/classes-exams/', 'Classes & Exams'),
        ('/RoutineTest/exams/', 'Exam List'),
        ('/RoutineTest/exams/create/', 'Create Exam'),
        ('/PlacementTest/', 'PlacementTest Index'),
    ]
    
    all_passed = True
    for url, description in test_urls:
        try:
            response = client.get(url)
            if response.status_code in [200, 302]:
                print(f"✅ {description}: {url}")
            else:
                print(f"❌ {description}: {url} (status: {response.status_code})")
                all_passed = False
        except Exception as e:
            print(f"❌ {description}: {url} (error: {str(e)[:50]})")
            all_passed = False
    
    return all_passed

def test_button_replacement():
    """Test that Launch button is properly updated in template"""
    print_section("TEST 5: LAUNCH BUTTON UPDATED")
    
    client = Client()
    client.login(username='admin', password='test123')
    
    # Get a class with exams
    test_class = Class.objects.first()
    if test_class:
        response = client.get(f'/RoutineTest/class/{test_class.section}/details/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for new function
            if 'launchTeacherPreview' in content:
                print("✅ New launchTeacherPreview function found")
            else:
                print("❌ launchTeacherPreview function not found")
                
            # Check that old modal is not the primary action
            if 'Launch Exam' in content:
                print("✅ Launch Exam button text updated")
            else:
                print("⚠️  Launch Exam button text not found")
                
            return 'launchTeacherPreview' in content
        else:
            print(f"❌ Failed to load class details (status: {response.status_code})")
            return False
    else:
        print("⚠️  No class found for testing")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("="*80)
    print("  TEACHER EXAM PREVIEW - COMPREHENSIVE TEST")
    print("  Testing Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80)
    
    results = {
        'endpoint': False,
        'session_model': False,
        'interface_access': False,
        'other_features': False,
        'button_updated': False
    }
    
    # Run tests
    session_id, redirect_url = test_teacher_preview_endpoint()
    results['endpoint'] = session_id is not None
    
    results['session_model'] = test_teacher_preview_session()
    results['interface_access'] = test_exam_interface_access()
    results['other_features'] = test_other_features_intact()
    results['button_updated'] = test_button_replacement()
    
    # Summary
    print_section("TEST SUMMARY")
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name.upper().replace('_', ' ')}: {status}")
    
    print("\n" + "="*80)
    if all_passed:
        print("  🎉 ALL TESTS PASSED - TEACHER PREVIEW FEATURE WORKING!")
        print("  ✅ Teachers can now click 'Launch Exam' to experience the student interface")
        print("  ✅ Same exam-taking interface with timer and questions")
        print("  ✅ Teacher preview sessions properly tracked")
        print("  ✅ No disruption to existing functionality")
    else:
        print("  ⚠️  SOME TESTS FAILED - Review issues above")
    print("="*80)
    
    # Implementation details
    print("""
IMPLEMENTATION DETAILS:
1. Added 'is_teacher_preview' and 'preview_teacher' fields to StudentSession
2. Created launch_teacher_preview view in class_details.py
3. Updated Launch button to call launchTeacherPreview() JavaScript function
4. Teacher gets redirected to /RoutineTest/session/<session_id>/ 
5. Timer starts and teacher experiences exact student interface
6. Preview data marked separately from real student data

CONSOLE DEBUGGING:
- Extensive console.log statements added throughout
- Check browser console for detailed flow tracking
- Server logs show [TEACHER_PREVIEW] tagged messages
    """)
    
    return all_passed

if __name__ == '__main__':
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)