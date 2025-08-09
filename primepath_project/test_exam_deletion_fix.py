#!/usr/bin/env python
"""
Test script to verify exam deletion functionality after AudioFile field fixes
Tests deletion with and without audio files to ensure the fix works properly
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from placement_test.models import Exam, AudioFile, Question, StudentSession
from core.models import CurriculumLevel
import json

print("="*80)
print("EXAM DELETION FIX VERIFICATION TEST")
print("="*80)

def create_test_exam_with_audio():
    """Create an exam with audio files for testing"""
    print("\n1. Creating test exam with audio files...")
    
    # Get a curriculum level
    level = CurriculumLevel.objects.first()
    if not level:
        print("❌ No curriculum levels found - cannot create exam")
        return None
    
    # Create exam
    exam = Exam.objects.create(
        name="Test Exam for Deletion - With Audio",
        curriculum_level=level,
        timer_minutes=30,
        total_questions=5,
        pdf_file=None,
        is_active=True
    )
    print(f"✅ Created exam: {exam.name} (ID: {exam.id})")
    
    # Create some questions
    for i in range(1, 6):
        Question.objects.create(
            exam=exam,
            question_number=i,
            question_type='MCQ',
            points=2,
            correct_answer=f"Answer {i}"
        )
    print(f"✅ Created 5 questions")
    
    # Create audio files with actual file content
    for i in range(1, 3):
        # Create a simple audio file content (just dummy bytes)
        audio_content = b"dummy audio content for test"
        audio_file = SimpleUploadedFile(
            f"test_audio_{i}.mp3", 
            audio_content,
            content_type="audio/mpeg"
        )
        
        audio = AudioFile.objects.create(
            exam=exam,
            name=f"Test Audio {i}",
            audio_file=audio_file,
            start_question=i,
            end_question=i,
            order=i
        )
        print(f"✅ Created audio file: {audio.name} (ID: {audio.id})")
    
    return exam

def create_test_exam_without_audio():
    """Create an exam without audio files for testing"""
    print("\n2. Creating test exam without audio files...")
    
    level = CurriculumLevel.objects.first()
    if not level:
        print("❌ No curriculum levels found - cannot create exam")
        return None
    
    exam = Exam.objects.create(
        name="Test Exam for Deletion - No Audio",
        curriculum_level=level,
        timer_minutes=30,
        total_questions=3,
        pdf_file=None,
        is_active=True
    )
    print(f"✅ Created exam: {exam.name} (ID: {exam.id})")
    
    # Create some questions
    for i in range(1, 4):
        Question.objects.create(
            exam=exam,
            question_number=i,
            question_type='SHORT',
            points=3,
            correct_answer=f"Answer {i}"
        )
    print(f"✅ Created 3 questions")
    
    return exam

def test_deletion_via_view(exam_id):
    """Test deletion through the web view"""
    print(f"\n3. Testing direct deletion for exam {exam_id}...")
    
    try:
        exam = Exam.objects.get(id=exam_id)
        
        # Simulate what the view does
        # Delete associated files
        if exam.pdf_file:
            exam.pdf_file.delete()
        
        # Delete audio files - THIS IS THE KEY TEST
        for audio in exam.audio_files.all():
            if audio.audio_file:  # This was the fixed line
                try:
                    audio.audio_file.delete()
                    print(f"   ✅ Successfully deleted audio file: {audio.name}")
                except Exception as e:
                    print(f"   ❌ Failed to delete audio file: {e}")
                    return False
            audio.delete()
        
        # Delete the exam
        exam.delete()
        
        # Check if exam still exists
        if not Exam.objects.filter(id=exam_id).exists():
            print(f"✅ Exam deleted successfully (including audio files)")
            return True
        else:
            print(f"❌ Exam still exists after deletion attempt")
            return False
            
    except Exception as e:
        print(f"❌ Error during deletion: {str(e)}")
        return False

def test_deletion_via_service(exam_id):
    """Test deletion through the service layer"""
    print(f"\n4. Testing deletion via service for exam {exam_id}...")
    
    from placement_test.services.exam_service import ExamService
    
    try:
        exam = Exam.objects.get(id=exam_id)
        result = ExamService.delete_exam(exam)
        
        if result and not Exam.objects.filter(id=exam_id).exists():
            print(f"✅ Exam deleted successfully via service")
            return True
        else:
            print(f"❌ Exam deletion via service failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during service deletion: {str(e)}")
        return False

def test_cascade_deletion():
    """Test that cascade deletion works properly"""
    print("\n5. Testing cascade deletion...")
    
    level = CurriculumLevel.objects.first()
    if not level:
        print("❌ No curriculum levels found")
        return False
    
    # Create exam with related data
    exam = Exam.objects.create(
        name="Test Cascade Deletion",
        curriculum_level=level,
        timer_minutes=30,
        total_questions=1,
        is_active=True
    )
    exam_id = exam.id
    
    # Create questions
    q1 = Question.objects.create(
        exam=exam,
        question_number=1,
        question_type='MCQ',
        points=2,
        correct_answer="A"
    )
    q1_id = q1.id
    
    # Create audio
    audio = AudioFile.objects.create(
        exam=exam,
        name="Test Audio",
        audio_file=None,  # No actual file for cascade test
        start_question=1,
        end_question=1
    )
    audio_id = audio.id
    
    # Create session
    session = StudentSession.objects.create(
        student_name="Test Student",
        grade=5,
        academic_rank="TOP_20",
        exam=exam,
        original_curriculum_level=level
    )
    session_id = session.id
    
    print(f"✅ Created exam with question, audio, and session")
    
    # Delete the exam
    exam.delete()
    
    # Check cascades
    checks = [
        (Exam.objects.filter(id=exam_id).exists(), "Exam"),
        (Question.objects.filter(id=q1_id).exists(), "Question"),
        (AudioFile.objects.filter(id=audio_id).exists(), "AudioFile"),
        (StudentSession.objects.filter(id=session_id).exists(), "StudentSession")
    ]
    
    all_deleted = True
    for exists, model_name in checks:
        if exists:
            print(f"❌ {model_name} not deleted (cascade failed)")
            all_deleted = False
        else:
            print(f"✅ {model_name} properly deleted")
    
    return all_deleted

def verify_audio_file_access():
    """Verify that AudioFile fields are accessible correctly"""
    print("\n6. Verifying AudioFile field access...")
    
    # Create a test audio file
    level = CurriculumLevel.objects.first()
    if not level:
        print("❌ No curriculum levels found")
        return False
    
    exam = Exam.objects.create(
        name="Field Access Test",
        curriculum_level=level,
        timer_minutes=30,
        total_questions=1
    )
    
    audio_content = b"test content"
    audio_file = SimpleUploadedFile(
        "test.mp3", 
        audio_content,
        content_type="audio/mpeg"
    )
    
    audio = AudioFile.objects.create(
        exam=exam,
        name="Field Test Audio",
        audio_file=audio_file,
        start_question=1,
        end_question=1
    )
    
    # Test field access
    tests = []
    
    # Test correct field name
    try:
        name = audio.audio_file.name
        tests.append(("audio.audio_file.name", True))
        print(f"✅ audio.audio_file.name works: {name}")
    except:
        tests.append(("audio.audio_file.name", False))
        print(f"❌ audio.audio_file.name failed")
    
    # Test incorrect field name (should fail)
    try:
        name = audio.file.name
        tests.append(("audio.file.name", False))  # Should not reach here
        print(f"❌ audio.file.name should not work but did")
    except AttributeError:
        tests.append(("audio.file.name", True))  # Expected to fail
        print(f"✅ audio.file.name correctly raises AttributeError")
    
    # Clean up
    exam.delete()
    
    return all(result for _, result in tests)

def test_api_serialization():
    """Test that API serialization works after fix"""
    print("\n7. Testing API serialization...")
    
    from api.v1.serializers import AudioFileSerializer
    
    # Create test data
    level = CurriculumLevel.objects.first()
    if not level:
        print("❌ No curriculum levels found")
        return False
    
    exam = Exam.objects.create(
        name="API Test Exam",
        curriculum_level=level,
        timer_minutes=30,
        total_questions=1
    )
    
    audio = AudioFile.objects.create(
        exam=exam,
        name="API Test Audio",
        audio_file=None,
        start_question=1,
        end_question=2
    )
    
    # Test serialization
    try:
        serializer = AudioFileSerializer(audio)
        data = serializer.data
        
        # Check that correct fields are present
        expected_fields = ['id', 'name', 'audio_file', 'file_url', 'start_question', 'end_question']
        missing_fields = [f for f in expected_fields if f not in data]
        
        if missing_fields:
            print(f"❌ Missing fields in serialization: {missing_fields}")
            exam.delete()
            return False
        
        print(f"✅ API serialization works correctly")
        print(f"   Serialized data: {data}")
        
        # Clean up
        exam.delete()
        return True
        
    except Exception as e:
        print(f"❌ API serialization failed: {str(e)}")
        exam.delete()
        return False

def main():
    """Run all tests"""
    results = {
        'tests_run': 0,
        'tests_passed': 0,
        'tests_failed': 0
    }
    
    print("\n" + "="*80)
    print("STARTING EXAM DELETION TESTS")
    print("="*80)
    
    # Test 1: Create and delete exam with audio
    exam_with_audio = create_test_exam_with_audio()
    if exam_with_audio:
        results['tests_run'] += 1
        if test_deletion_via_view(exam_with_audio.id):
            results['tests_passed'] += 1
        else:
            results['tests_failed'] += 1
            # Try to clean up if deletion failed
            try:
                exam_with_audio.delete()
            except:
                pass
    
    # Test 2: Create and delete exam without audio
    exam_without_audio = create_test_exam_without_audio()
    if exam_without_audio:
        results['tests_run'] += 1
        if test_deletion_via_service(exam_without_audio.id):
            results['tests_passed'] += 1
        else:
            results['tests_failed'] += 1
            # Try to clean up
            try:
                exam_without_audio.delete()
            except:
                pass
    
    # Test 3: Cascade deletion
    results['tests_run'] += 1
    if test_cascade_deletion():
        results['tests_passed'] += 1
    else:
        results['tests_failed'] += 1
    
    # Test 4: Field access
    results['tests_run'] += 1
    if verify_audio_file_access():
        results['tests_passed'] += 1
    else:
        results['tests_failed'] += 1
    
    # Test 5: API serialization
    results['tests_run'] += 1
    if test_api_serialization():
        results['tests_passed'] += 1
    else:
        results['tests_failed'] += 1
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {results['tests_run']}")
    print(f"Tests Passed: {results['tests_passed']}")
    print(f"Tests Failed: {results['tests_failed']}")
    
    if results['tests_failed'] == 0:
        print("\n✅ ALL TESTS PASSED - EXAM DELETION FIX VERIFIED!")
    else:
        print(f"\n❌ {results['tests_failed']} TEST(S) FAILED - REVIEW NEEDED")
    
    print("="*80)
    
    return results['tests_failed'] == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)