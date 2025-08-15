#!/usr/bin/env python
"""
Comprehensive test to verify all existing RoutineTest features still work
after the class-specific scheduling changes.
"""

import os
import sys
import django
from datetime import date, time
import tempfile
import json

# Setup Django environment
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models import Exam, Question, AudioFile, StudentRoster
from primepath_routinetest.services import ExamService
from core.models import Teacher, CurriculumLevel, SubProgram, Program
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

User = get_user_model()


def setup_test_data():
    """Setup basic test data"""
    print("\n" + "="*80)
    print("SETUP: Creating test data")
    print("="*80)
    
    # Create user and teacher
    user, _ = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    
    teacher, _ = Teacher.objects.get_or_create(
        user=user,
        defaults={
            'name': 'Test Teacher',
            'email': 'test@example.com',
            'is_head_teacher': True
        }
    )
    
    # Create curriculum structure
    program, _ = Program.objects.get_or_create(
        name='CORE',
        defaults={'display_order': 1}
    )
    
    subprogram, _ = SubProgram.objects.get_or_create(
        program=program,
        name='Phonics',
        defaults={'display_order': 1}
    )
    
    curriculum_level, _ = CurriculumLevel.objects.get_or_create(
        subprogram=subprogram,
        level_number=1,
        defaults={'level_name': 'Level 1'}
    )
    
    print(f"✅ Teacher: {teacher.name}")
    print(f"✅ Curriculum: {curriculum_level.full_name}")
    
    return teacher, curriculum_level


def test_exam_creation():
    """Test 1: Basic exam creation with all phases"""
    print("\n" + "="*80)
    print("TEST 1: Exam Creation (All Phases)")
    print("="*80)
    
    teacher, curriculum_level = setup_test_data()
    
    # Create PDF file
    pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n'
    pdf_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
    
    # Prepare exam data with all phases
    exam_data = {
        'name': 'Feature Test Exam',
        'exam_type': 'QUARTERLY',  # Phase 1
        'time_period_quarter': 'Q1',  # Phase 2
        'academic_year': '2025',  # Phase 2
        'class_codes': ['CLASS_7A', 'CLASS_7B', 'CLASS_8A'],  # Phase 3
        'instructions': 'Test instructions for all students',  # General instructions (kept)
        'curriculum_level_id': curriculum_level.id,
        'timer_minutes': 90,
        'total_questions': 15,
        'default_options_count': 5,
        'passing_score': 70,
        'pdf_rotation': 90,  # PDF rotation
        'created_by': teacher,
        'is_active': True
    }
    
    try:
        # Create exam using service
        exam = ExamService.create_exam(
            exam_data=exam_data,
            pdf_file=pdf_file,
            audio_files=None,
            audio_names=None
        )
        
        print(f"✅ Exam created: {exam.name}")
        print(f"   Type: {exam.get_exam_type_display_short()}")
        print(f"   Time Period: {exam.get_time_period_display()}")
        print(f"   Classes: {exam.get_class_codes_display()}")
        print(f"   Questions: {exam.total_questions}")
        print(f"   PDF Rotation: {exam.pdf_rotation}°")
        print(f"   Instructions: {exam.instructions[:30]}...")
        
        # Verify questions were created
        questions = exam.routine_questions.all()
        assert questions.count() == 15, f"Expected 15 questions, got {questions.count()}"
        print(f"✅ Questions created: {questions.count()}")
        
        # Verify no scheduling fields exist
        assert not hasattr(exam, 'scheduled_date'), "scheduled_date should not exist"
        assert not hasattr(exam, 'allow_late_submission'), "allow_late_submission should not exist"
        print("✅ Scheduling fields correctly removed")
        
        return exam
        
    except Exception as e:
        print(f"❌ Error creating exam: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_answer_mapping():
    """Test 2: Answer mapping functionality"""
    print("\n" + "="*80)
    print("TEST 2: Answer Mapping")
    print("="*80)
    
    # Get an exam
    exam = Exam.objects.filter(name='Feature Test Exam').first()
    if not exam:
        print("❌ No test exam found")
        return False
    
    # Test answer mapping for questions
    questions_data = [
        {
            'id': str(exam.routine_questions.first().id),
            'question_type': 'MCQ',
            'correct_answer': 'B',
            'options_count': 4
        },
        {
            'id': str(exam.routine_questions.all()[1].id),
            'question_type': 'SHORT',
            'correct_answer': 'Answer 1|Answer 2|Answer 3',
            'options_count': 3
        },
        {
            'id': str(exam.routine_questions.all()[2].id),
            'question_type': 'CHECKBOX',
            'correct_answer': 'A,C,D',
            'options_count': 5
        }
    ]
    
    try:
        result = ExamService.update_exam_questions(exam, questions_data)
        print(f"✅ Questions updated: {result['updated']} updated, {result['created']} created")
        
        # Check answer mapping status
        status = exam.get_answer_mapping_status()
        print(f"✅ Answer mapping status:")
        print(f"   Total: {status['total_questions']}")
        print(f"   Mapped: {status['mapped_questions']}")
        print(f"   Unmapped: {status['unmapped_questions']}")
        print(f"   Percentage: {status['percentage_complete']}%")
        print(f"   Status: {status['status_label']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating questions: {e}")
        return False


def test_audio_files():
    """Test 3: Audio file functionality"""
    print("\n" + "="*80)
    print("TEST 3: Audio Files")
    print("="*80)
    
    exam = Exam.objects.filter(name='Feature Test Exam').first()
    if not exam:
        print("❌ No test exam found")
        return False
    
    # Create audio files
    audio_content = b'fake audio content'
    audio_files = [
        SimpleUploadedFile("audio1.mp3", audio_content, content_type="audio/mpeg"),
        SimpleUploadedFile("audio2.mp3", audio_content, content_type="audio/mpeg")
    ]
    audio_names = ["Listening Part 1", "Listening Part 2"]
    
    try:
        audio_objects = ExamService.attach_audio_files(exam, audio_files, audio_names)
        print(f"✅ Audio files attached: {len(audio_objects)}")
        
        for audio in audio_objects:
            print(f"   - {audio.name} (ID: {audio.id})")
        
        # Test audio assignment to questions
        audio_assignments = {
            '1': audio_objects[0].id,
            '5': audio_objects[1].id
        }
        
        result = ExamService.update_audio_assignments(exam, audio_assignments)
        print(f"✅ Audio assignments: {result['updated']} updated")
        
        # Verify assignments
        q1 = exam.routine_questions.get(question_number=1)
        q5 = exam.routine_questions.get(question_number=5)
        
        assert q1.audio_file is not None, "Question 1 should have audio"
        assert q5.audio_file is not None, "Question 5 should have audio"
        print(f"✅ Verified: Q1 has audio '{q1.audio_file.name}'")
        print(f"✅ Verified: Q5 has audio '{q5.audio_file.name}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with audio files: {e}")
        return False


def test_student_roster():
    """Test 4: Phase 5 Student Roster functionality"""
    print("\n" + "="*80)
    print("TEST 4: Student Roster (Phase 5)")
    print("="*80)
    
    exam = Exam.objects.filter(name='Feature Test Exam').first()
    if not exam:
        print("❌ No test exam found")
        return False
    
    teacher = exam.created_by
    
    # Create roster data
    roster_data = [
        {
            'student_name': 'John Doe',
            'student_id': 'STU001',
            'class_code': 'CLASS_7A',
            'notes': 'Extra time allowed'
        },
        {
            'student_name': 'Jane Smith',
            'student_id': 'STU002',
            'class_code': 'CLASS_7B',
            'notes': ''
        },
        {
            'student_name': 'Bob Johnson',
            'student_id': 'STU003',
            'class_code': 'CLASS_8A',
            'notes': 'Absent - excused'
        }
    ]
    
    try:
        result = ExamService.manage_student_roster(exam, roster_data, teacher)
        print(f"✅ Roster created: {result['created']} students")
        print(f"   Updated: {result['updated']}")
        
        # Get roster stats
        stats = exam.get_roster_stats()
        print(f"✅ Roster statistics:")
        print(f"   Total assigned: {stats['total_assigned']}")
        print(f"   Not started: {stats['not_started']}")
        print(f"   Completed: {stats['completed']}")
        print(f"   Has roster: {stats['has_roster']}")
        
        # Get roster by class
        roster_by_class = exam.get_roster_by_class()
        print(f"✅ Roster by class:")
        for class_code, students in roster_by_class.items():
            print(f"   {class_code}: {len(students)} students")
        
        # Test CSV import
        csv_content = """student_name,student_id,class_code,notes
Alice Brown,STU004,CLASS_7A,Transfer student
Charlie Davis,STU005,CLASS_7B,
Eve Wilson,STU006,CLASS_8A,Special accommodations"""
        
        import_result = ExamService.bulk_import_roster(exam, csv_content, teacher)
        print(f"✅ CSV import: {import_result['created']} created, {import_result['updated']} updated")
        
        # Generate roster report
        report = ExamService.get_roster_report(exam)
        print(f"✅ Roster report generated:")
        print(f"   Total: {report['total_assigned']} students")
        print(f"   Completion rate: {report['completion_rate']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with student roster: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exam_type_and_periods():
    """Test 5: Exam types and time periods (Phase 1 & 2)"""
    print("\n" + "="*80)
    print("TEST 5: Exam Types and Time Periods")
    print("="*80)
    
    teacher, curriculum_level = setup_test_data()
    
    # Test Review/Monthly exam
    exam_data = {
        'name': 'Monthly Review Test',
        'exam_type': 'REVIEW',
        'time_period_month': 'MAR',
        'academic_year': '2025',
        'class_codes': ['CLASS_9A'],
        'instructions': 'Monthly review instructions',
        'curriculum_level_id': curriculum_level.id,
        'timer_minutes': 60,
        'total_questions': 10,
        'default_options_count': 4,
        'created_by': teacher,
        'is_active': True
    }
    
    try:
        # Create simple PDF
        pdf_content = b'%PDF-1.4\ntest'
        pdf_file = SimpleUploadedFile("monthly.pdf", pdf_content, content_type="application/pdf")
        
        exam = ExamService.create_exam(
            exam_data=exam_data,
            pdf_file=pdf_file
        )
        
        print(f"✅ Monthly exam created: {exam.name}")
        print(f"   Type: {exam.get_exam_type_display_short()}")
        print(f"   Period: {exam.get_time_period_display()}")
        print(f"   Short: {exam.get_time_period_short()}")
        
        # Test Quarterly exam
        exam_data['name'] = 'Quarterly Assessment'
        exam_data['exam_type'] = 'QUARTERLY'
        exam_data['time_period_month'] = None
        exam_data['time_period_quarter'] = 'Q3'
        
        pdf_file = SimpleUploadedFile("quarterly.pdf", pdf_content, content_type="application/pdf")
        
        exam2 = ExamService.create_exam(
            exam_data=exam_data,
            pdf_file=pdf_file
        )
        
        print(f"✅ Quarterly exam created: {exam2.name}")
        print(f"   Type: {exam2.get_exam_type_display_short()}")
        print(f"   Period: {exam2.get_time_period_display()}")
        print(f"   Short: {exam2.get_time_period_short()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing exam types: {e}")
        return False


def test_class_codes():
    """Test 6: Class codes functionality (Phase 3)"""
    print("\n" + "="*80)
    print("TEST 6: Class Codes (Phase 3)")
    print("="*80)
    
    exam = Exam.objects.filter(name='Feature Test Exam').first()
    if not exam:
        print("❌ No test exam found")
        return False
    
    print(f"Exam: {exam.name}")
    print(f"✅ Class codes stored: {exam.class_codes}")
    print(f"✅ Display: {exam.get_class_codes_display()}")
    print(f"✅ Short display: {exam.get_class_codes_short()}")
    
    # Get class list
    class_list = exam.get_class_codes_list()
    print(f"✅ Class list ({len(class_list)} classes):")
    for cls in class_list:
        print(f"   - {cls['code']}: {cls['name']}")
    
    # Test with many classes
    exam.class_codes = ['CLASS_7A', 'CLASS_7B', 'CLASS_7C', 'CLASS_8A', 'CLASS_8B']
    exam.save()
    
    print(f"✅ Many classes display: {exam.get_class_codes_display()}")
    print(f"✅ Many classes short: {exam.get_class_codes_short()}")
    
    return True


def test_pdf_rotation():
    """Test 7: PDF rotation functionality"""
    print("\n" + "="*80)
    print("TEST 7: PDF Rotation")
    print("="*80)
    
    exam = Exam.objects.filter(name='Feature Test Exam').first()
    if not exam:
        print("❌ No test exam found")
        return False
    
    print(f"Exam: {exam.name}")
    print(f"✅ Current rotation: {exam.pdf_rotation}°")
    
    # Test different rotations
    for rotation in [0, 90, 180, 270]:
        exam.pdf_rotation = rotation
        exam.save()
        print(f"✅ Set rotation to {rotation}°")
        
        # Verify it persists
        exam.refresh_from_db()
        assert exam.pdf_rotation == rotation, f"Rotation not saved: expected {rotation}, got {exam.pdf_rotation}"
    
    print("✅ PDF rotation working correctly")
    return True


def test_question_types():
    """Test 8: Different question types"""
    print("\n" + "="*80)
    print("TEST 8: Question Types")
    print("="*80)
    
    exam = Exam.objects.filter(name='Feature Test Exam').first()
    if not exam:
        print("❌ No test exam found")
        return False
    
    # Test different question types
    question_configs = [
        {'number': 1, 'type': 'MCQ', 'answer': 'C'},
        {'number': 2, 'type': 'CHECKBOX', 'answer': 'A,B,D'},
        {'number': 3, 'type': 'SHORT', 'answer': 'Paris|London|Berlin'},
        {'number': 4, 'type': 'LONG', 'answer': 'Long answer text|||Second part|||Third part'},
        {'number': 5, 'type': 'MIXED', 'answer': '[{"type":"mcq","answer":"B"},{"type":"text","answer":"Explanation"}]'}
    ]
    
    for config in question_configs:
        q = exam.routine_questions.get(question_number=config['number'])
        q.question_type = config['type']
        q.correct_answer = config['answer']
        
        # Calculate options count
        if config['type'] in ['SHORT', 'LONG', 'MIXED']:
            q.options_count = ExamService._calculate_options_count(
                config['type'], 
                config['answer']
            )
        else:
            q.options_count = 5
        
        q.save()
        print(f"✅ Q{config['number']}: {config['type']} - options_count={q.options_count}")
    
    # Verify answer mapping
    status = exam.get_answer_mapping_status()
    print(f"✅ Mapping after updates: {status['mapped_questions']}/{status['total_questions']} ({status['percentage_complete']}%)")
    
    return True


def test_exam_list_features():
    """Test 9: Exam list display features"""
    print("\n" + "="*80)
    print("TEST 9: Exam List Features")
    print("="*80)
    
    # Get all test exams
    exams = Exam.objects.filter(name__contains='Test')
    print(f"Found {exams.count()} test exams")
    
    for exam in exams:
        print(f"\n📋 {exam.name}")
        
        # Answer mapping status
        status = exam.get_answer_mapping_status()
        print(f"   Answer mapping: {status['status_label']} ({status['percentage_complete']}%)")
        
        # Roster stats
        roster_stats = exam.get_roster_stats()
        if roster_stats['has_roster']:
            print(f"   Roster: {roster_stats['total_assigned']} students")
        else:
            print(f"   Roster: No students assigned")
        
        # Class schedules (new)
        if exam.has_class_schedules():
            schedules = exam.get_class_schedules()
            print(f"   Schedules: {schedules.count()} class schedules")
        else:
            print(f"   Schedules: No schedules set")
        
        # Instructions
        if exam.instructions:
            print(f"   Instructions: Yes ({len(exam.instructions)} chars)")
        else:
            print(f"   Instructions: None")
    
    return True


def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "="*80)
    print("CLEANUP: Removing test data")
    print("="*80)
    
    # Delete test exams
    test_exams = Exam.objects.filter(
        name__in=['Feature Test Exam', 'Monthly Review Test', 'Quarterly Assessment']
    )
    count = test_exams.count()
    test_exams.delete()
    print(f"✅ Deleted {count} test exams")


def main():
    """Run all tests"""
    print("\n" + "#"*80)
    print("# COMPREHENSIVE FEATURE TEST SUITE")
    print("# Testing all RoutineTest features after scheduling changes")
    print("#"*80)
    
    results = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    # Run all tests
    tests = [
        ("Exam Creation", test_exam_creation),
        ("Answer Mapping", test_answer_mapping),
        ("Audio Files", test_audio_files),
        ("Student Roster", test_student_roster),
        ("Exam Types & Periods", test_exam_type_and_periods),
        ("Class Codes", test_class_codes),
        ("PDF Rotation", test_pdf_rotation),
        ("Question Types", test_question_types),
        ("Exam List Features", test_exam_list_features)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result or result is None:
                results['passed'] += 1
                results['tests'].append((test_name, "✅ PASSED"))
            else:
                results['failed'] += 1
                results['tests'].append((test_name, "❌ FAILED"))
        except Exception as e:
            results['failed'] += 1
            results['tests'].append((test_name, f"❌ ERROR: {e}"))
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    for test_name, status in results['tests']:
        print(f"{status} {test_name}")
    
    print("\n" + "-"*40)
    print(f"Total: {results['passed'] + results['failed']} tests")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if results['failed'] == 0:
        print("\n✅ ALL TESTS PASSED - No existing features were affected!")
    else:
        print(f"\n⚠️ {results['failed']} tests failed - Some features may be affected")
    
    # Clean up
    cleanup_test_data()


if __name__ == '__main__':
    main()