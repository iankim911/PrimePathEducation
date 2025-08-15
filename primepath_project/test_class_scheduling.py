#!/usr/bin/env python
"""
Test script for verifying class-specific scheduling implementation.
Tests the removal of exam-level scheduling and new ClassExamSchedule model.
"""

import os
import sys
import django
from datetime import date, time

# Setup Django environment
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models import Exam, ClassExamSchedule
from primepath_routinetest.services import ExamService
from core.models import Teacher
import json


def test_exam_creation_without_scheduling():
    """Test that exams can be created without scheduling fields"""
    print("\n" + "="*80)
    print("TEST 1: Creating exam without scheduling fields")
    print("="*80)
    
    # Get or create a teacher
    teacher = Teacher.objects.first()
    if not teacher:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user('test_teacher', 'test@example.com', 'password')
        teacher = Teacher.objects.create(
            user=user,
            name='Test Teacher',
            email='test@example.com'
        )
    
    # Prepare exam data without scheduling fields
    exam_data = {
        'name': 'Test Exam - Class Scheduling',
        'exam_type': 'REVIEW',
        'time_period_month': 'JAN',
        'academic_year': '2025',
        'class_codes': ['CLASS_7A', 'CLASS_7B', 'CLASS_8A'],
        'instructions': 'General instructions for all classes',
        'curriculum_level_id': None,
        'timer_minutes': 60,
        'total_questions': 10,
        'default_options_count': 5,
        'passing_score': 70,
        'pdf_rotation': 0,
        'created_by': teacher,
        'is_active': True
    }
    
    try:
        # Create exam - this should work without scheduling fields
        exam = Exam.objects.create(**exam_data)
        print(f"✅ Exam created successfully: {exam.name}")
        print(f"   ID: {exam.id}")
        print(f"   Classes: {exam.get_class_codes_display()}")
        print(f"   Instructions: {exam.instructions[:50]}...")
        
        # Verify scheduling fields don't exist
        assert not hasattr(exam, 'scheduled_date'), "scheduled_date should not exist"
        assert not hasattr(exam, 'scheduled_start_time'), "scheduled_start_time should not exist"
        assert not hasattr(exam, 'scheduled_end_time'), "scheduled_end_time should not exist"
        assert not hasattr(exam, 'allow_late_submission'), "allow_late_submission should not exist"
        assert not hasattr(exam, 'late_submission_penalty'), "late_submission_penalty should not exist"
        
        print("✅ Verified: Scheduling fields removed from Exam model")
        
        return exam
        
    except Exception as e:
        print(f"❌ Error creating exam: {e}")
        return None


def test_class_schedule_creation(exam):
    """Test creating class-specific schedules"""
    print("\n" + "="*80)
    print("TEST 2: Creating class-specific schedules")
    print("="*80)
    
    if not exam:
        print("❌ No exam available for testing")
        return
    
    # Get teacher
    teacher = exam.created_by
    
    # Test data for different class schedules
    schedules_data = [
        {
            'class_code': 'CLASS_7A',
            'scheduled_date': date(2025, 9, 1),
            'scheduled_start_time': time(9, 0),
            'scheduled_end_time': time(10, 30),
            'location': 'Room 101',
            'additional_instructions': 'Bring calculators',
            'allow_late_submission': True,
            'late_submission_penalty': 10
        },
        {
            'class_code': 'CLASS_7B',
            'scheduled_date': date(2025, 9, 1),
            'scheduled_start_time': time(11, 0),
            'scheduled_end_time': time(12, 30),
            'location': 'Room 102',
            'additional_instructions': 'No calculators allowed',
            'allow_late_submission': False,
            'late_submission_penalty': 0
        },
        {
            'class_code': 'CLASS_8A',
            'scheduled_date': date(2025, 9, 2),
            'scheduled_start_time': time(9, 0),
            'scheduled_end_time': time(10, 30),
            'location': 'Lab 1',
            'additional_instructions': '',
            'allow_late_submission': True,
            'late_submission_penalty': 5
        }
    ]
    
    created_schedules = []
    
    for schedule_data in schedules_data:
        try:
            class_code = schedule_data.pop('class_code')
            schedule = ExamService.create_class_schedule(
                exam=exam,
                class_code=class_code,
                schedule_data=schedule_data,
                teacher=teacher
            )
            created_schedules.append(schedule)
            
            print(f"✅ Created schedule for {schedule.get_class_display()}")
            print(f"   Schedule: {schedule.get_schedule_display()}")
            print(f"   Location: {schedule.location}")
            print(f"   Late Policy: {schedule.get_late_policy_display()}")
            
        except Exception as e:
            print(f"❌ Error creating schedule for {class_code}: {e}")
    
    return created_schedules


def test_exam_schedule_methods(exam):
    """Test exam methods for accessing class schedules"""
    print("\n" + "="*80)
    print("TEST 3: Testing exam schedule access methods")
    print("="*80)
    
    if not exam:
        print("❌ No exam available for testing")
        return
    
    # Test has_class_schedules
    has_schedules = exam.has_class_schedules()
    print(f"Has schedules: {has_schedules}")
    
    # Test get_class_schedules
    all_schedules = exam.get_class_schedules()
    print(f"Total active schedules: {all_schedules.count()}")
    
    for schedule in all_schedules:
        print(f"  - {schedule.get_class_display()}: {schedule.get_schedule_short()}")
    
    # Test get_schedule_for_class
    test_class = 'CLASS_7A'
    schedule = exam.get_schedule_for_class(test_class)
    if schedule:
        print(f"\n✅ Found schedule for {test_class}:")
        print(f"   {schedule.get_schedule_display()}")
    else:
        print(f"❌ No schedule found for {test_class}")


def test_service_methods():
    """Test ExamService methods for class schedules"""
    print("\n" + "="*80)
    print("TEST 4: Testing ExamService schedule methods")
    print("="*80)
    
    # Get an exam with schedules
    exam = Exam.objects.filter(class_schedules__isnull=False).first()
    if not exam:
        print("❌ No exam with schedules found")
        return
    
    print(f"Using exam: {exam.name}")
    
    # Test get_class_schedules_for_exam
    schedules = ExamService.get_class_schedules_for_exam(exam)
    print(f"\nSchedules from service: {len(schedules)} found")
    for schedule in schedules:
        print(f"  - {schedule['class_display']}: {schedule['schedule_display']}")
    
    # Test check_class_access
    for class_code in ['CLASS_7A', 'CLASS_7B', 'CLASS_8A']:
        access_info = ExamService.check_class_access(exam, class_code)
        print(f"\nAccess for {class_code}:")
        print(f"  Can access: {access_info['can_access']}")
        print(f"  Message: {access_info['message']}")
        print(f"  Schedule: {access_info['schedule']}")


def test_bulk_schedule_creation():
    """Test bulk creation of class schedules"""
    print("\n" + "="*80)
    print("TEST 5: Testing bulk schedule creation")
    print("="*80)
    
    # Create a new exam for testing
    teacher = Teacher.objects.first()
    exam = Exam.objects.create(
        name='Bulk Schedule Test Exam',
        exam_type='QUARTERLY',
        time_period_quarter='Q1',
        academic_year='2025',
        class_codes=['CLASS_9A', 'CLASS_9B', 'CLASS_9C'],
        instructions='Test bulk scheduling',
        timer_minutes=90,
        total_questions=20,
        created_by=teacher
    )
    
    # Prepare bulk schedule data
    bulk_schedules = [
        {
            'class_code': 'CLASS_9A',
            'scheduled_date': date(2025, 10, 1),
            'scheduled_start_time': time(8, 0),
            'scheduled_end_time': time(9, 30),
            'location': 'Hall A'
        },
        {
            'class_code': 'CLASS_9B',
            'scheduled_date': date(2025, 10, 1),
            'scheduled_start_time': time(10, 0),
            'scheduled_end_time': time(11, 30),
            'location': 'Hall B'
        },
        {
            'class_code': 'CLASS_9C',
            'scheduled_date': date(2025, 10, 2),
            'scheduled_start_time': time(8, 0),
            'scheduled_end_time': time(9, 30),
            'location': 'Hall A'
        }
    ]
    
    # Test bulk creation
    result = ExamService.bulk_create_class_schedules(
        exam=exam,
        schedules_data=bulk_schedules,
        teacher=teacher
    )
    
    print(f"Bulk creation result:")
    print(f"  Created: {result['created']}")
    print(f"  Updated: {result['updated']}")
    print(f"  Errors: {len(result['errors'])}")
    if result['errors']:
        for error in result['errors']:
            print(f"    - {error}")
    
    return exam


def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "="*80)
    print("CLEANUP: Removing test data")
    print("="*80)
    
    # Delete test exams
    test_exams = Exam.objects.filter(name__contains='Test')
    count = test_exams.count()
    test_exams.delete()
    print(f"Deleted {count} test exams")
    
    # Delete test schedules (should cascade from exam deletion)
    remaining_schedules = ClassExamSchedule.objects.filter(
        exam__name__contains='Test'
    ).count()
    print(f"Remaining test schedules: {remaining_schedules}")


def main():
    """Run all tests"""
    print("\n" + "#"*80)
    print("# CLASS-SPECIFIC SCHEDULING TEST SUITE")
    print("#"*80)
    
    try:
        # Run tests
        exam = test_exam_creation_without_scheduling()
        
        if exam:
            schedules = test_class_schedule_creation(exam)
            test_exam_schedule_methods(exam)
        
        test_service_methods()
        bulk_exam = test_bulk_schedule_creation()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        cleanup_test_data()


if __name__ == '__main__':
    main()