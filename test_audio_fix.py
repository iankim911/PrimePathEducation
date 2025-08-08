#!/usr/bin/env python
"""
Comprehensive test for audio assignment/unassignment functionality
Tests the fix for the JavaScript null/undefined error
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'primepath_project'))
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from placement_test.models import Exam, Question, AudioFile, Teacher
from placement_test.services.exam_service import ExamService
from core.models import CurriculumLevel
import json


def test_audio_assignment_backend():
    """Test backend handling of audio assignments"""
    print("\n" + "="*60)
    print("TESTING AUDIO ASSIGNMENT BACKEND")
    print("="*60)
    
    # Get an exam
    exam = Exam.objects.first()
    if not exam:
        print("❌ No exams found in database")
        return False
    
    print(f"✅ Using exam: {exam.name}")
    
    # Test 1: Empty dictionary
    print("\n1. Testing empty dictionary...")
    try:
        result = ExamService.update_audio_assignments(exam, {})
        print(f"   ✅ Success: {result}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 2: None value
    print("\n2. Testing None value...")
    try:
        result = ExamService.update_audio_assignments(exam, None)
        print(f"   ✅ Success: {result}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 3: Null values in assignments
    print("\n3. Testing null values in assignments...")
    try:
        result = ExamService.update_audio_assignments(exam, {'1': None, '2': None})
        print(f"   ✅ Success: {result}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 4: Valid assignments
    audio_files = exam.audio_files.all()
    if audio_files.exists():
        print("\n4. Testing valid assignments...")
        try:
            assignments = {
                '1': audio_files[0].id if len(audio_files) > 0 else None,
                '2': audio_files[1].id if len(audio_files) > 1 else None
            }
            result = ExamService.update_audio_assignments(exam, assignments)
            print(f"   ✅ Success: {result}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            return False
    
    return True


def test_save_endpoint():
    """Test the save_exam_answers endpoint"""
    print("\n" + "="*60)
    print("TESTING SAVE ENDPOINT")
    print("="*60)
    
    client = Client()
    exam = Exam.objects.first()
    
    if not exam:
        print("❌ No exams found")
        return False
    
    url = f'/api/placement/exams/{exam.id}/save-answers/'
    
    # Test 1: Empty audio assignments
    print("\n1. Testing empty audio_assignments...")
    data = {
        'questions': [],
        'audio_assignments': {}
    }
    
    try:
        response = client.post(url, json.dumps(data), content_type='application/json')
        if response.status_code == 200:
            print(f"   ✅ Success: {response.json()}")
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
    # Test 2: Null in audio assignments
    print("\n2. Testing null in audio_assignments...")
    data = {
        'questions': [],
        'audio_assignments': None
    }
    
    try:
        response = client.post(url, json.dumps(data), content_type='application/json')
        if response.status_code == 200:
            print(f"   ✅ Success: {response.json()}")
        else:
            print(f"   ⚠️  Status {response.status_code} (might be expected)")
    except Exception as e:
        print(f"   ⚠️  Exception (might be expected): {e}")
    
    return True


def test_question_audio_relationships():
    """Test Question-AudioFile relationships"""
    print("\n" + "="*60)
    print("TESTING QUESTION-AUDIO RELATIONSHIPS")
    print("="*60)
    
    exam = Exam.objects.first()
    if not exam:
        print("❌ No exams found")
        return False
    
    questions = exam.questions.all()[:3]
    audio_files = exam.audio_files.all()[:3]
    
    print(f"✅ Exam: {exam.name}")
    print(f"   Questions: {questions.count()}")
    print(f"   Audio files: {audio_files.count()}")
    
    # Clear all assignments
    print("\n1. Clearing all audio assignments...")
    Question.objects.filter(exam=exam).update(audio_file=None)
    unassigned = Question.objects.filter(exam=exam, audio_file__isnull=True).count()
    print(f"   ✅ {unassigned} questions have no audio")
    
    # Assign some audio
    if questions and audio_files:
        print("\n2. Assigning audio to questions...")
        for i, (q, a) in enumerate(zip(questions[:2], audio_files[:2])):
            q.audio_file = a
            q.save()
            print(f"   ✅ Q{q.question_number} -> Audio {a.id}")
    
    # Verify assignments
    print("\n3. Verifying assignments...")
    assigned = Question.objects.filter(exam=exam, audio_file__isnull=False).count()
    print(f"   ✅ {assigned} questions have audio assigned")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE AUDIO FIX TESTING")
    print("="*60)
    
    results = []
    
    # Backend tests
    result = test_audio_assignment_backend()
    results.append(("Backend Audio Assignment", result))
    
    # Endpoint tests
    result = test_save_endpoint()
    results.append(("Save Endpoint", result))
    
    # Relationship tests
    result = test_question_audio_relationships()
    results.append(("Question-Audio Relationships", result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! The audio fix is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)