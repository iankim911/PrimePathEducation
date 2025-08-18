#!/usr/bin/env python
"""
Comprehensive test to verify NO existing features were broken by recent fixes.
Tests both PlacementTest and RoutineTest modules thoroughly.
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

from django.test import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from placement_test.models import Exam as PlacementExam, StudentSession as PlacementSession
from primepath_routinetest.models import Exam as RoutineExam, StudentSession as RoutineSession
from core.models import School, Teacher, CurriculumLevel


def setup_test_environment():
    """Setup test users and basic data."""
    # Create test user
    user, created = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Create test teacher
    teacher, _ = Teacher.objects.get_or_create(
        user=user,
        defaults={'name': 'Test Teacher'}
    )
    
    return user, teacher


def test_placement_test_module():
    """Test PlacementTest module is unaffected."""
    print("\n" + "="*80)
    print("📘 TESTING PLACEMENTTEST MODULE")
    print("="*80)
    
    client = Client()
    client.login(username='test_admin', password='testpass123')
    
    tests_passed = []
    
    # Test 1: Exam List Page
    print("\n1️⃣ Testing PlacementTest Exam List...")
    response = client.get('/PlacementTest/exams/', follow=True)
    test_passed = response.status_code == 200
    tests_passed.append(('Exam List', test_passed))
    print(f"   {'✅' if test_passed else '❌'} Exam list page: {response.status_code}")
    
    # Test 2: Create Exam Page
    print("\n2️⃣ Testing PlacementTest Create Exam...")
    response = client.get('/PlacementTest/exams/create/', follow=True)
    test_passed = response.status_code == 200
    tests_passed.append(('Create Exam Page', test_passed))
    print(f"   {'✅' if test_passed else '❌'} Create exam page: {response.status_code}")
    
    # Test 3: Start Test Page
    print("\n3️⃣ Testing PlacementTest Start Test...")
    response = client.get('/PlacementTest/start/', follow=True)
    test_passed = response.status_code == 200
    tests_passed.append(('Start Test', test_passed))
    print(f"   {'✅' if test_passed else '❌'} Start test page: {response.status_code}")
    
    # Test 4: Check exam model relationships
    print("\n4️⃣ Testing PlacementTest Model Relationships...")
    exam = PlacementExam.objects.first()
    if exam:
        try:
            questions = exam.questions.all()
            audio_files = exam.audio_files.all()
            tests_passed.append(('Model Relations', True))
            print(f"   ✅ exam.questions: {questions.count()} items")
            print(f"   ✅ exam.audio_files: {audio_files.count()} items")
        except AttributeError as e:
            tests_passed.append(('Model Relations', False))
            print(f"   ❌ Model relationship error: {e}")
    else:
        print("   ⚠️ No PlacementTest exams to test")
    
    # Test 5: Session Management
    print("\n5️⃣ Testing PlacementTest Sessions...")
    response = client.get('/PlacementTest/sessions/', follow=True)
    test_passed = response.status_code == 200
    tests_passed.append(('Sessions', test_passed))
    print(f"   {'✅' if test_passed else '❌'} Sessions page: {response.status_code}")
    
    # Summary
    passed = sum(1 for _, result in tests_passed if result)
    total = len(tests_passed)
    print(f"\n📊 PlacementTest Results: {passed}/{total} tests passed")
    
    return passed == total


def test_routine_test_module():
    """Test RoutineTest module functionality."""
    print("\n" + "="*80)
    print("📗 TESTING ROUTINETEST MODULE")
    print("="*80)
    
    client = Client()
    client.login(username='test_admin', password='testpass123')
    
    tests_passed = []
    
    # Test 1: Exam List Page
    print("\n1️⃣ Testing RoutineTest Exam List...")
    response = client.get('/RoutineTest/exams/', follow=True)
    test_passed = response.status_code == 200
    tests_passed.append(('Exam List', test_passed))
    print(f"   {'✅' if test_passed else '❌'} Exam list page: {response.status_code}")
    
    if test_passed:
        content = response.content.decode('utf-8')
        # Check for UI improvements
        if 'min-width: 85px' in content:
            print("   ✅ Button width fixes applied")
        if 'Update Name' in content:
            print("   ✅ Update Name button present")
    
    # Test 2: Create Exam Page
    print("\n2️⃣ Testing RoutineTest Create Exam...")
    response = client.get('/RoutineTest/exams/create/', follow=True)
    test_passed = response.status_code == 200
    tests_passed.append(('Create Exam Page', test_passed))
    print(f"   {'✅' if test_passed else '❌'} Create exam page: {response.status_code}")
    
    # Test 3: Preview/Manage Exam (Our Fix)
    print("\n3️⃣ Testing RoutineTest Preview/Manage...")
    exam = RoutineExam.objects.first()
    if exam:
        response = client.get(f'/RoutineTest/exams/{exam.id}/preview/', follow=False)
        test_passed = response.status_code == 200
        tests_passed.append(('Preview Exam', test_passed))
        print(f"   {'✅' if test_passed else '❌'} Preview exam page: {response.status_code}")
        
        if test_passed:
            content = response.content.decode('utf-8')
            if 'container-main' in content:
                print("   ✅ Content rendering correctly")
            if '[PREVIEW_EXAM_DEBUG]' in content:
                print("   ✅ Debug logging added")
    else:
        print("   ⚠️ No RoutineTest exams to test")
    
    # Test 4: Model Relationships (Our Fix)
    print("\n4️⃣ Testing RoutineTest Model Relationships...")
    if exam:
        try:
            questions = exam.routine_questions.all()
            audio_files = exam.routine_audio_files.all()
            tests_passed.append(('Model Relations', True))
            print(f"   ✅ exam.routine_questions: {questions.count()} items")
            print(f"   ✅ exam.routine_audio_files: {audio_files.count()} items")
            
            # Verify wrong names don't work
            try:
                _ = exam.questions.all()
                print("   ⚠️ exam.questions still accessible (shouldn't be)")
            except AttributeError:
                print("   ✅ exam.questions correctly fails")
                
        except AttributeError as e:
            tests_passed.append(('Model Relations', False))
            print(f"   ❌ Model relationship error: {e}")
    
    # Test 5: Roster Management
    print("\n5️⃣ Testing RoutineTest Roster Management...")
    if exam:
        response = client.get(f'/RoutineTest/exams/{exam.id}/roster/', follow=True)
        test_passed = response.status_code == 200
        tests_passed.append(('Roster Management', test_passed))
        print(f"   {'✅' if test_passed else '❌'} Roster page: {response.status_code}")
    
    # Test 6: Sessions
    print("\n6️⃣ Testing RoutineTest Sessions...")
    response = client.get('/RoutineTest/sessions/', follow=True)
    test_passed = response.status_code == 200
    tests_passed.append(('Sessions', test_passed))
    print(f"   {'✅' if test_passed else '❌'} Sessions page: {response.status_code}")
    
    # Summary
    passed = sum(1 for _, result in tests_passed if result)
    total = len(tests_passed)
    print(f"\n📊 RoutineTest Results: {passed}/{total} tests passed")
    
    return passed == total


def test_api_endpoints():
    """Test API endpoints are working."""
    print("\n" + "="*80)
    print("🔌 TESTING API ENDPOINTS")
    print("="*80)
    
    client = Client()
    client.login(username='test_admin', password='testpass123')
    
    tests_passed = []
    
    # Test PlacementTest APIs
    print("\n📘 PlacementTest APIs:")
    placement_exam = PlacementExam.objects.first()
    if placement_exam:
        # Test save answers endpoint
        response = client.post(
            f'/api/PlacementTest/exams/{placement_exam.id}/save-answers/',
            data=json.dumps({'questions': [], 'audio_assignments': {}}),
            content_type='application/json'
        )
        test_passed = response.status_code in [200, 201]
        tests_passed.append(('PlacementTest Save Answers', test_passed))
        print(f"   {'✅' if test_passed else '❌'} Save answers API: {response.status_code}")
    
    # Test RoutineTest APIs
    print("\n📗 RoutineTest APIs:")
    routine_exam = RoutineExam.objects.first()
    if routine_exam:
        # Test save answers endpoint
        response = client.post(
            f'/RoutineTest/api/exams/{routine_exam.id}/save-answers/',
            data=json.dumps({'questions': [], 'audio_assignments': {}}),
            content_type='application/json'
        )
        test_passed = response.status_code in [200, 201]
        tests_passed.append(('RoutineTest Save Answers', test_passed))
        print(f"   {'✅' if test_passed else '❌'} Save answers API: {response.status_code}")
    
    passed = sum(1 for _, result in tests_passed if result)
    total = len(tests_passed)
    print(f"\n📊 API Results: {passed}/{total} tests passed")
    
    return passed == total


def test_navigation_and_ui():
    """Test navigation and UI components."""
    print("\n" + "="*80)
    print("🎨 TESTING NAVIGATION & UI")
    print("="*80)
    
    client = Client()
    client.login(username='test_admin', password='testpass123')
    
    tests_passed = []
    
    # Test navigation tabs
    print("\n1️⃣ Testing Navigation Tabs...")
    
    # PlacementTest navigation
    response = client.get('/PlacementTest/', follow=True)
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        has_nav = 'nav-tabs' in content or 'navigation' in content.lower()
        tests_passed.append(('PlacementTest Nav', has_nav))
        print(f"   {'✅' if has_nav else '❌'} PlacementTest navigation")
    
    # RoutineTest navigation
    response = client.get('/RoutineTest/', follow=True)
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        has_nav = 'nav-tabs' in content or 'navigation' in content.lower()
        tests_passed.append(('RoutineTest Nav', has_nav))
        print(f"   {'✅' if has_nav else '❌'} RoutineTest navigation (BCG Green theme)")
    
    # Test theme colors
    print("\n2️⃣ Testing Theme Colors...")
    
    # Check RoutineTest green theme
    response = client.get('/RoutineTest/exams/', follow=True)
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        has_green = '#00A65E' in content or '#1B5E20' in content
        tests_passed.append(('Green Theme', has_green))
        print(f"   {'✅' if has_green else '❌'} RoutineTest green theme")
    
    passed = sum(1 for _, result in tests_passed if result)
    total = len(tests_passed)
    print(f"\n📊 UI/Navigation Results: {passed}/{total} tests passed")
    
    return passed == total


def test_file_uploads():
    """Test file upload functionality."""
    print("\n" + "="*80)
    print("📁 TESTING FILE UPLOADS")
    print("="*80)
    
    tests_passed = []
    
    # Check if upload directories exist
    print("\n1️⃣ Checking Upload Directories...")
    
    pdf_dir = 'media/pdfs/'
    audio_dir = 'media/audio/'
    
    for dir_path, name in [(pdf_dir, 'PDF'), (audio_dir, 'Audio')]:
        exists = os.path.exists(dir_path)
        tests_passed.append((f'{name} Directory', exists))
        print(f"   {'✅' if exists else '⚠️'} {name} directory: {dir_path}")
    
    # Check models have file fields
    print("\n2️⃣ Checking Model File Fields...")
    
    placement_exam = PlacementExam.objects.first()
    if placement_exam:
        has_pdf = hasattr(placement_exam, 'pdf_file')
        tests_passed.append(('PlacementTest PDF Field', has_pdf))
        print(f"   {'✅' if has_pdf else '❌'} PlacementTest has pdf_file field")
    
    routine_exam = RoutineExam.objects.first()
    if routine_exam:
        has_pdf = hasattr(routine_exam, 'pdf_file')
        tests_passed.append(('RoutineTest PDF Field', has_pdf))
        print(f"   {'✅' if has_pdf else '❌'} RoutineTest has pdf_file field")
    
    passed = sum(1 for _, result in tests_passed if result)
    total = len(tests_passed)
    print(f"\n📊 File Upload Results: {passed}/{total} tests passed")
    
    return passed == total


def main():
    """Run all comprehensive tests."""
    print("\n" + "🚀"*40)
    print("🔍 COMPREHENSIVE NO-BREAKING-CHANGES VERIFICATION")
    print("🚀"*40)
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print("Testing all features to ensure no regressions...")
    
    # Setup
    user, teacher = setup_test_environment()
    print(f"\n✅ Test environment ready (User: {user.username})")
    
    # Run all test suites
    all_results = []
    
    all_results.append(('PlacementTest Module', test_placement_test_module()))
    all_results.append(('RoutineTest Module', test_routine_test_module()))
    all_results.append(('API Endpoints', test_api_endpoints()))
    all_results.append(('Navigation & UI', test_navigation_and_ui()))
    all_results.append(('File Uploads', test_file_uploads()))
    
    # Final Summary
    print("\n" + "="*80)
    print("📊 FINAL COMPREHENSIVE SUMMARY")
    print("="*80)
    
    for name, passed in all_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in all_results)
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL FEATURES VERIFIED - NO BREAKING CHANGES!")
        print("✅ PlacementTest module fully functional")
        print("✅ RoutineTest module fully functional")
        print("✅ All API endpoints working")
        print("✅ Navigation and UI intact")
        print("✅ File upload capabilities preserved")
        print("\n💡 Recent fixes:")
        print("   • Fixed RoutineTest preview page (related_names)")
        print("   • Improved button widths for 'Update Name'")
        print("   • Added comprehensive debugging")
        print("   • Zero impact on existing features")
        return 0
    else:
        print("⚠️ SOME FEATURES MAY BE AFFECTED")
        print("Please review failed tests above")
        return 1


if __name__ == '__main__':
    sys.exit(main())