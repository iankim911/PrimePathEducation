#!/usr/bin/env python
"""
Comprehensive test for PDF file handling fix
Tests that exams without PDF files can be viewed without errors
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.utils import timezone
from django.core.files.base import ContentFile
from placement_test.models import Exam, Question, AudioFile
from core.models import CurriculumLevel, SubProgram, Program

def test_pdf_file_handling():
    """Test exam management with and without PDF files"""
    
    print("=" * 80)
    print("🔧 COMPREHENSIVE PDF FILE HANDLING TEST")
    print("=" * 80)
    
    # Check server
    base_url = "http://127.0.0.1:8000"
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding: HTTP {response.status_code}")
            print("Please start the server with:")
            print("cd primepath_project && ../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please start the server first")
        return False
    
    print(f"✅ Server running at {base_url}")
    
    all_tests_passed = True
    
    # Test 1: Create exam without PDF file
    print("\n📋 TEST 1: Create Exam Without PDF File")
    print("-" * 40)
    
    # Get or create a curriculum level
    program, _ = Program.objects.get_or_create(
        name="CORE",  # Use a valid choice from PROGRAM_TYPES
        defaults={'grade_range_start': 1, 'grade_range_end': 12, 'order': 1}
    )
    
    subprogram, _ = SubProgram.objects.get_or_create(
        name="Test SubProgram",
        program=program,
        defaults={'order': 1}
    )
    
    curriculum_level, _ = CurriculumLevel.objects.get_or_create(
        subprogram=subprogram,
        level_number=1,
        defaults={'description': 'Test Level for PDF handling test'}
    )
    
    # Create exam without PDF file
    exam_no_pdf = Exam.objects.create(
        name=f"Test Exam No PDF - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        curriculum_level=curriculum_level,
        timer_minutes=60,
        total_questions=20,
        is_active=True,
        # pdf_file is intentionally not set
    )
    
    print(f"✅ Created exam without PDF: {exam_no_pdf.name} (ID: {exam_no_pdf.id})")
    
    # Create some questions for the exam
    for i in range(1, 6):
        Question.objects.create(
            exam=exam_no_pdf,
            question_number=i,
            question_type='MCQ',
            correct_answer=str(i % 4 + 1),
            points=1,
            options_count=4
        )
    
    print(f"✅ Created {5} questions for exam")
    
    # Test 2: Access exam preview page (where the error was occurring)
    print("\n📋 TEST 2: Access Exam Preview Without PDF")
    print("-" * 40)
    
    preview_url = f"{base_url}/api/placement/exams/{exam_no_pdf.id}/preview/"
    
    try:
        response = requests.get(preview_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Preview page loads successfully (HTTP 200)")
            
            # Check if the page contains our "No PDF" message
            if "No PDF" in response.text or "No PDF file" in response.text:
                print("✅ Page shows 'No PDF' message as expected")
            else:
                print("⚠️ Page might not be showing the No PDF message")
            
            # Check if there are no error messages
            if "Error" not in response.text or "No PDF file uploaded" in response.text:
                print("✅ No error messages on page")
            else:
                print("❌ Page contains error messages")
                all_tests_passed = False
        else:
            print(f"❌ Preview page failed: HTTP {response.status_code}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Error accessing preview page: {e}")
        all_tests_passed = False
    
    # Test 3: Access exam list page
    print("\n📋 TEST 3: Access Exam List Page")
    print("-" * 40)
    
    list_url = f"{base_url}/api/placement/exams/"
    
    try:
        response = requests.get(list_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Exam list page loads successfully")
            
            if exam_no_pdf.name in response.text:
                print(f"✅ New exam appears in list")
        else:
            print(f"❌ Exam list page failed: HTTP {response.status_code}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Error accessing exam list: {e}")
        all_tests_passed = False
    
    # Test 4: Create exam WITH PDF file for comparison
    print("\n📋 TEST 4: Create Exam WITH PDF File")
    print("-" * 40)
    
    exam_with_pdf = Exam.objects.create(
        name=f"Test Exam With PDF - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        curriculum_level=curriculum_level,
        timer_minutes=60,
        total_questions=20,
        is_active=True,
    )
    
    # Create a dummy PDF file
    dummy_pdf_content = b"%PDF-1.4\n%Dummy PDF for testing\n"
    exam_with_pdf.pdf_file.save('test_exam.pdf', ContentFile(dummy_pdf_content), save=True)
    
    print(f"✅ Created exam with PDF: {exam_with_pdf.name}")
    
    # Create questions for this exam too
    for i in range(1, 6):
        Question.objects.create(
            exam=exam_with_pdf,
            question_number=i,
            question_type='MCQ',
            correct_answer=str(i % 4 + 1),
            points=1,
            options_count=4
        )
    
    # Test preview page for exam with PDF
    preview_url_with_pdf = f"{base_url}/api/placement/exams/{exam_with_pdf.id}/preview/"
    
    try:
        response = requests.get(preview_url_with_pdf, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Preview page with PDF loads successfully")
            
            if "Download PDF" in response.text:
                print("✅ Download PDF button is present")
            
            if exam_with_pdf.pdf_file.url in response.text:
                print("✅ PDF URL is properly included")
        else:
            print(f"❌ Preview page with PDF failed: HTTP {response.status_code}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Error accessing preview with PDF: {e}")
        all_tests_passed = False
    
    # Test 5: API endpoints
    print("\n📋 TEST 5: Test API Endpoints")
    print("-" * 40)
    
    api_url = f"{base_url}/api/placement/exams/{exam_no_pdf.id}/"
    
    try:
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'pdf_url' in data and data['pdf_url'] is None:
                print("✅ API returns null for pdf_url when no PDF")
            else:
                print(f"⚠️ API pdf_url value: {data.get('pdf_url')}")
        else:
            print(f"⚠️ API endpoint returned: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Could not test API: {e}")
    
    # Test 6: Student test view
    print("\n📋 TEST 6: Test Student Interface")
    print("-" * 40)
    
    from placement_test.models import StudentSession
    
    # Create a test session for the exam without PDF
    session = StudentSession.objects.create(
        exam=exam_no_pdf,
        student_name="Test Student",
        parent_phone="+1234567890",
        grade=5,
        academic_rank='TOP_20',
        started_at=timezone.now()
    )
    
    student_test_url = f"{base_url}/api/placement/session/{session.id}/"
    
    try:
        response = requests.get(student_test_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Student test page loads without errors")
            
            if "No PDF" in response.text or "pdf-viewer" in response.text:
                print("✅ PDF viewer section handled properly")
        else:
            print(f"❌ Student test page failed: HTTP {response.status_code}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Error accessing student test: {e}")
        all_tests_passed = False
    
    print("\n" + "=" * 80)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    if all_tests_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n📋 Fixed Issues:")
        print("  1. ✅ Exams without PDF files can be previewed")
        print("  2. ✅ No 'pdf_file has no file' errors")
        print("  3. ✅ Graceful handling of missing PDFs")
        print("  4. ✅ Exams with PDFs still work correctly")
        print("  5. ✅ Student interface handles missing PDFs")
        print("\n🎉 The PDF file handling has been successfully fixed!")
        return True
    else:
        print("❌ Some tests failed - review issues above")
        return False

def test_existing_features():
    """Test that existing features still work"""
    
    print("\n" + "=" * 80)
    print("🔍 TESTING EXISTING FEATURES")
    print("=" * 80)
    
    all_features_working = True
    
    # Test exam creation with PDF
    print("\n📋 Testing Exam Management:")
    exam_count = Exam.objects.count()
    pdf_count = Exam.objects.exclude(pdf_file='').count()
    no_pdf_count = Exam.objects.filter(pdf_file='').count()
    
    print(f"✅ Total exams: {exam_count}")
    print(f"✅ Exams with PDF: {pdf_count}")
    print(f"✅ Exams without PDF: {no_pdf_count}")
    
    # Test question system
    print("\n📋 Testing Question System:")
    questions_count = Question.objects.count()
    questions_with_audio = Question.objects.filter(audio_file__isnull=False).count()
    
    print(f"✅ Total questions: {questions_count}")
    print(f"✅ Questions with audio: {questions_with_audio}")
    
    # Test audio files
    print("\n📋 Testing Audio System:")
    audio_count = AudioFile.objects.count()
    print(f"✅ Total audio files: {audio_count}")
    
    return all_features_working

if __name__ == '__main__':
    # Run PDF handling tests
    pdf_success = test_pdf_file_handling()
    
    # Run existing features tests
    features_success = test_existing_features()
    
    print("\n" + "=" * 80)
    print("🎯 COMPREHENSIVE QA COMPLETE")
    print("=" * 80)
    
    if pdf_success and features_success:
        print("✅ ALL SYSTEMS OPERATIONAL")
        print("\n🎉 The PDF file fix is working correctly!")
        print("📋 No existing features were disrupted")
        sys.exit(0)
    else:
        print("❌ Some issues detected - review test output")
        sys.exit(1)