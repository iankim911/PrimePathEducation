#!/usr/bin/env python
"""
Test to verify the preview_exam page fix for RoutineTest.
Checks that the page renders correctly with content.
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from primepath_routinetest.models import Exam
from django.contrib.auth.models import User


def test_preview_exam_fix():
    """Test that preview_exam page renders correctly."""
    print("\n" + "="*80)
    print("🔧 PREVIEW EXAM FIX VERIFICATION")
    print("="*80)
    
    client = Client()
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Login
    logged_in = client.login(username='test_admin', password='testpass123')
    print(f"\n✅ User logged in: {logged_in}")
    
    # Get a RoutineTest exam
    exam = Exam.objects.first()
    if not exam:
        print("❌ No exams found in database")
        return False
    
    print(f"\n📋 Testing with exam: {exam.name}")
    print(f"   Exam ID: {exam.id}")
    print(f"   Total Questions: {exam.total_questions}")
    
    # Test the preview_exam view
    print("\n🔍 Testing preview_exam view...")
    
    try:
        response = client.get(f'/RoutineTest/exams/{exam.id}/preview/', follow=False)
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for key elements
            checks = [
                ('Template rendered', '{% extends "routinetest_base.html" %}' not in content),  # Template should be processed
                ('Content block present', 'container-main' in content),
                ('Exam name displayed', exam.name in content),
                ('PDF section present', 'pdf-title-section' in content),
                ('Questions section present', 'Answer Keys' in content or 'answer-keys' in content),
                ('Save button present', 'Save All Answers' in content or 'save' in content.lower()),
                ('Debugging scripts added', '[PREVIEW_EXAM_DEBUG]' in content),
                ('No template errors', '{% block' not in content),  # Raw template tags shouldn't appear
            ]
            
            passed = 0
            for name, check in checks:
                if check:
                    print(f"   ✅ {name}")
                    passed += 1
                else:
                    print(f"   ❌ {name}")
            
            # Check context data
            if hasattr(response, 'context') and response.context:
                context = response.context
                print(f"\n📊 Context Data:")
                print(f"   Exam: {context.get('exam')}")
                print(f"   Questions: {context.get('questions')}")
                print(f"   Audio Files: {context.get('audio_files')}")
            else:
                print(f"\n📊 Context Data: No context available")
            
            # Check for error messages
            if 'error' in content.lower() or 'exception' in content.lower():
                print("\n⚠️ Error indicators found in response")
            
            # Check content length
            print(f"\n📏 Response size: {len(content)} bytes")
            if len(content) < 1000:
                print("   ⚠️ Response seems too small - might be an error page")
            else:
                print("   ✅ Response has substantial content")
            
            # Always save response for debugging
            with open('preview_exam_response.html', 'w') as f:
                f.write(content)
            print("   📁 Response saved to preview_exam_response.html")
            
            # Summary
            print(f"\n📊 Test Results: {passed}/{len(checks)} checks passed")
            
            if passed >= 6:
                print("\n✅ PREVIEW EXAM PAGE IS WORKING!")
                print("   The page is rendering with content")
                return True
            else:
                print("\n⚠️ PREVIEW EXAM PAGE HAS ISSUES")
                print("   Some elements are missing or not rendering")
                
                # Save response for debugging
                with open('preview_exam_response.html', 'w') as f:
                    f.write(content)
                print("   Response saved to preview_exam_response.html for inspection")
                return False
                
        elif response.status_code == 500:
            print(f"   ❌ Server Error (500)")
            print("   Check server logs for AttributeError or other exceptions")
            return False
        elif response.status_code == 404:
            print(f"   ❌ Page Not Found (404)")
            print("   Check URL patterns")
            return False
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_related_names():
    """Verify all related names are correct."""
    print("\n📋 Checking Related Names...")
    
    exam = Exam.objects.first()
    if not exam:
        print("   ❌ No exam to test")
        return False
    
    checks = []
    
    # Check routine_questions
    try:
        questions = exam.routine_questions.all()
        checks.append(('routine_questions', True))
        print(f"   ✅ exam.routine_questions works ({questions.count()} questions)")
    except AttributeError as e:
        checks.append(('routine_questions', False))
        print(f"   ❌ exam.routine_questions failed: {e}")
    
    # Check routine_audio_files
    try:
        audio_files = exam.routine_audio_files.all()
        checks.append(('routine_audio_files', True))
        print(f"   ✅ exam.routine_audio_files works ({audio_files.count()} files)")
    except AttributeError as e:
        checks.append(('routine_audio_files', False))
        print(f"   ❌ exam.routine_audio_files failed: {e}")
    
    # Check wrong names don't work
    try:
        _ = exam.questions.all()
        print(f"   ⚠️ exam.questions still works (should fail)")
    except AttributeError:
        print(f"   ✅ exam.questions correctly fails (as expected)")
    
    try:
        _ = exam.audio_files.all()
        print(f"   ⚠️ exam.audio_files still works (should fail)")
    except AttributeError:
        print(f"   ✅ exam.audio_files correctly fails (as expected)")
    
    return all(check[1] for check in checks)


if __name__ == '__main__':
    print("\n🚀 Starting Preview Exam Fix Test...")
    
    # First check related names
    related_ok = check_related_names()
    
    # Then test the view
    view_ok = test_preview_exam_fix()
    
    print("\n" + "="*80)
    if related_ok and view_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Related names are correct")
        print("✅ Preview exam page is rendering")
        print("✅ No blank page issue")
        sys.exit(0)
    else:
        print("❌ TESTS FAILED")
        if not related_ok:
            print("   Fix: Check model related_name attributes")
        if not view_ok:
            print("   Fix: Check view and template for errors")
        sys.exit(1)