#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify exam creation functionality works after fixes
"""

import os
import sys
import io
import django

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import Exam, Question
from placement_test.services import ExamService
from core.models import CurriculumLevel
from django.core.files.uploadedfile import SimpleUploadedFile

def test_exam_creation():
    """Test that exam creation works without skip_first_left_half field"""
    print("Testing exam creation after fix...")
    
    try:
        # Prepare test data
        exam_data = {
            'name': 'Test Exam After Fix',
            'curriculum_level_id': None,
            'timer_minutes': 60,
            'total_questions': 10,
            'default_options_count': 5,
            'passing_score': 0,
            'created_by': None,
            'is_active': True
        }
        
        # Create a dummy PDF file
        pdf_content = b'%PDF-1.4\n%Test PDF content'
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
        
        # Try to create exam
        print("Creating exam...")
        exam = ExamService.create_exam(
            exam_data=exam_data,
            pdf_file=pdf_file,
            audio_files=None,
            audio_names=None
        )
        
        print(f"✓ Exam created successfully: {exam.name} (ID: {exam.id})")
        
        # Verify questions were created
        questions = exam.questions.count()
        print(f"✓ Questions created: {questions}/{exam.total_questions}")
        
        # Clean up test data
        exam.delete()
        print("✓ Test exam deleted")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating exam: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_fields():
    """Verify the Exam model doesn't have skip_first_left_half field"""
    print("\nChecking Exam model fields...")
    
    exam_fields = [f.name for f in Exam._meta.get_fields()]
    
    if 'skip_first_left_half' in exam_fields:
        print("✗ ERROR: skip_first_left_half field still exists in Exam model!")
        return False
    else:
        print("✓ skip_first_left_half field correctly removed from Exam model")
        return True

def main():
    print("=" * 50)
    print("EXAM CREATION FIX VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("Model Fields Check", test_model_fields),
        ("Exam Creation Test", test_exam_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        results.append(test_func())
    
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ ALL TESTS PASSED ({passed}/{total})")
        print("The exam creation fix is working correctly!")
    else:
        print(f"✗ SOME TESTS FAILED ({passed}/{total} passed)")
        print("Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    sys.exit(0 if main() else 1)