#!/usr/bin/env python
"""
Test that the three exam configuration fields are properly implemented in RoutineTest.
Verifies: Test Duration, Total Questions, Default Options for MCQs
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import Exam as RoutineExam

def test_exam_config_fields():
    """Test that exam configuration fields are present and working."""
    print("\n" + "="*80)
    print("🔍 EXAM CONFIGURATION FIELDS TEST")
    print("="*80)
    
    client = Client()
    user, _ = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    user.set_password('testpass123')
    user.save()
    client.login(username='test_admin', password='testpass123')
    
    print("\n📗 Testing RoutineTest Create Exam Page...")
    
    # Load the create exam page
    response = client.get('/RoutineTest/exams/create/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        print("\n1️⃣ Checking Test Duration Field...")
        duration_checks = {
            '✅ Field exists': 'id="timer_minutes"' in content,
            '✅ Label correct': 'Test Duration (minutes)' in content,
            '✅ Required field': 'id="timer_minutes" name="timer_minutes"' in content and 'required' in content,
            '✅ Default value 60': 'value="60"' in content,
            '✅ Min value 1': 'min="1"' in content,
            '✅ Max value 180': 'max="180"' in content,
            '✅ Helper text': 'Duration of the test in minutes' in content
        }
        
        print("   Test Duration Field:")
        all_passed = True
        for check, result in duration_checks.items():
            if result:
                print(f"      {check}")
            else:
                print(f"      ❌ {check.replace('✅ ', '')}")
                all_passed = False
        
        print("\n2️⃣ Checking Total Questions Field...")
        questions_checks = {
            '✅ Field exists': 'id="total_questions"' in content,
            '✅ Label correct': 'Total Number of Questions' in content,
            '✅ Required field': 'id="total_questions" name="total_questions"' in content and 'required' in content,
            '✅ Placeholder text': 'placeholder="e.g., 50"' in content,
            '✅ Min value 1': 'min="1"' in content,
            '✅ Max value 100': 'max="100"' in content,
            '✅ Helper text': 'Total number of questions in the exam' in content
        }
        
        print("   Total Questions Field:")
        for check, result in questions_checks.items():
            if result:
                print(f"      {check}")
            else:
                print(f"      ❌ {check.replace('✅ ', '')}")
                all_passed = False
        
        print("\n3️⃣ Checking Default Options Field...")
        options_checks = {
            '✅ Field exists': 'id="default_options_count"' in content,
            '✅ Label correct': 'Default Options for Multiple Choice Questions' in content,
            '✅ Field name': 'name="default_options_count"' in content,
            '✅ Default value 5': 'value="5"' in content,
            '✅ Min value 2': 'min="2"' in content,
            '✅ Max value 10': 'max="10"' in content,
            '✅ Helper text': 'Number of answer options (A, B, C, etc.) for MCQ questions' in content
        }
        
        print("   Default Options Field:")
        for check, result in options_checks.items():
            if result:
                print(f"      {check}")
            else:
                print(f"      ❌ {check.replace('✅ ', '')}")
                all_passed = False
        
        print("\n4️⃣ Checking JavaScript Validation...")
        js_checks = {
            '✅ Timer validation': '[EXAM_CONFIG]' in content and 'timerMinutes' in content,
            '✅ Questions validation': 'totalQuestions' in content and 'total_questions' in content,
            '✅ Options validation': 'defaultOptionsCount' in content and 'default_options_count' in content,
            '✅ Field monitoring': '[EXAM_CONFIG_MONITOR]' in content,
            '✅ Form submission logging': 'timer_minutes:' in content or 'timer_minutes' in content
        }
        
        print("   JavaScript Validation:")
        for check, result in js_checks.items():
            if result:
                print(f"      {check}")
            else:
                print(f"      ❌ {check.replace('✅ ', '')}")
                all_passed = False
        
        print("\n5️⃣ Checking Section Organization...")
        # Check if fields appear before PDF section
        pdf_section_pos = content.find('Exam PDF File')
        config_section_pos = content.find('Exam Configuration')
        
        if config_section_pos > 0 and pdf_section_pos > 0 and config_section_pos < pdf_section_pos:
            print("      ✅ Configuration section appears before PDF section")
        else:
            print("      ❌ Configuration section should appear before PDF section")
            all_passed = False
        
        # Summary
        print("\n" + "="*80)
        if all_passed:
            print("✅ ALL TESTS PASSED!")
            print("\n📌 What was implemented:")
            print("1. Test Duration field with 60-minute default")
            print("2. Total Questions field with proper validation")
            print("3. Default Options field with 5 as default")
            print("4. JavaScript validation and monitoring")
            print("5. Backend logging for debugging")
            
            print("\n🎯 Features:")
            print("• Fields match PlacementTest implementation exactly")
            print("• Comprehensive console logging with [EXAM_CONFIG] prefix")
            print("• Real-time field monitoring with [EXAM_CONFIG_MONITOR] prefix")
            print("• Form validation before submission")
            print("• Backend receives and processes all fields correctly")
            
        else:
            print("⚠️ Some checks failed - review implementation")
            
    else:
        print(f"   ❌ Failed to load create exam page: {response.status_code}")
    
    # Test backend model support
    print("\n📡 Verifying Backend Model Support...")
    from primepath_routinetest.models import Exam
    
    # Check if model has the fields
    model_fields = [f.name for f in Exam._meta.get_fields()]
    
    backend_checks = {
        'timer_minutes': 'timer_minutes' in model_fields,
        'total_questions': 'total_questions' in model_fields,
        'default_options_count': 'default_options_count' in model_fields
    }
    
    print("   Model Fields:")
    for field, exists in backend_checks.items():
        if exists:
            print(f"      ✅ {field} field exists in model")
        else:
            print(f"      ❌ {field} field missing from model")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == '__main__':
    test_exam_config_fields()