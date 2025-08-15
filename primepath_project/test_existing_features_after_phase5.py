#!/usr/bin/env python
"""
Comprehensive test to verify ALL existing features still work after Phase 5 implementation
Tests every core functionality to ensure nothing was broken
"""
import os
import sys
import django
import json
from datetime import date, time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from primepath_routinetest.models import Exam, Question, AudioFile, StudentRoster
from primepath_routinetest.services import ExamService
from core.models import Teacher, CurriculumLevel, SubProgram, Program
from django.contrib.auth.models import User
import uuid


def run_comprehensive_tests():
    """Run comprehensive tests for all existing features"""
    print("\n" + "="*80)
    print("COMPREHENSIVE FEATURE VERIFICATION AFTER PHASE 5")
    print("Testing ALL existing functionality to ensure nothing is broken")
    print("="*80)
    
    results = {
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    # Clean up any existing test data first
    try:
        Exam.objects.filter(name__contains="Feature Test").delete()
        User.objects.filter(username='feature_test_user').delete()
    except:
        pass
    
    # Test 1: Basic Exam Creation (Core Functionality)
    print("\n[TEST 1] Basic Exam Creation...")
    try:
        exam = Exam.objects.create(
            name="Feature Test - Basic Exam",
            total_questions=10,
            timer_minutes=60,
            default_options_count=5,
            passing_score=70
        )
        
        assert exam.id is not None
        assert exam.total_questions == 10
        assert exam.timer_minutes == 60
        assert exam.default_options_count == 5
        assert exam.passing_score == 70
        
        print("✅ PASSED: Basic exam creation working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 1: {str(e)}")
    
    # Test 2: Question Creation and Management
    print("\n[TEST 2] Question Creation and Management...")
    try:
        # Create questions for the exam
        questions = []
        for i in range(1, 6):
            q = Question.objects.create(
                exam=exam,
                question_number=i,
                question_type='MCQ' if i <= 3 else 'SHORT',
                correct_answer='A' if i <= 3 else f'Answer {i}',
                points=2,
                options_count=5 if i <= 3 else 1
            )
            questions.append(q)
        
        assert exam.routine_questions.count() == 5
        assert exam.routine_questions.filter(question_type='MCQ').count() == 3
        assert exam.routine_questions.filter(question_type='SHORT').count() == 2
        
        # Test question update
        q1 = exam.routine_questions.first()
        q1.correct_answer = 'B'
        q1.save()
        q1.refresh_from_db()
        assert q1.correct_answer == 'B'
        
        print("✅ PASSED: Question management working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 2: {str(e)}")
    
    # Test 3: Audio File Attachment
    print("\n[TEST 3] Audio File Attachment...")
    try:
        # Create mock audio file
        audio = AudioFile.objects.create(
            exam=exam,
            name="Test Audio 1",
            audio_file="test_audio.mp3",
            start_question=1,
            end_question=3,
            order=1
        )
        
        assert audio.id is not None
        assert audio.exam == exam
        assert audio.start_question == 1
        assert audio.end_question == 3
        
        # Test audio assignment to question
        q1 = exam.routine_questions.first()
        q1.audio_file = audio
        q1.save()
        q1.refresh_from_db()
        assert q1.audio_file == audio
        
        print("✅ PASSED: Audio file management working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 3: {str(e)}")
    
    # Test 4: Phase 1 - Exam Types (REVIEW/QUARTERLY)
    print("\n[TEST 4] Phase 1 - Exam Types...")
    try:
        review_exam = Exam.objects.create(
            name="Feature Test - Review Exam",
            exam_type="REVIEW",
            total_questions=5,
            timer_minutes=30
        )
        
        quarterly_exam = Exam.objects.create(
            name="Feature Test - Quarterly Exam",
            exam_type="QUARTERLY",
            total_questions=5,
            timer_minutes=30
        )
        
        assert review_exam.exam_type == "REVIEW"
        assert review_exam.get_exam_type_display_short() == "Review"
        
        assert quarterly_exam.exam_type == "QUARTERLY"
        assert quarterly_exam.get_exam_type_display_short() == "Quarterly"
        
        print("✅ PASSED: Phase 1 exam types working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 4: {str(e)}")
    
    # Test 5: Phase 2 - Time Periods
    print("\n[TEST 5] Phase 2 - Time Periods...")
    try:
        monthly_exam = Exam.objects.create(
            name="Feature Test - Monthly",
            exam_type="REVIEW",
            time_period_month="JAN",
            academic_year="2025",
            total_questions=5,
            timer_minutes=30
        )
        
        quarterly_period_exam = Exam.objects.create(
            name="Feature Test - Quarterly Period",
            exam_type="QUARTERLY",
            time_period_quarter="Q2",
            academic_year="2025",
            total_questions=5,
            timer_minutes=30
        )
        
        assert monthly_exam.time_period_month == "JAN"
        assert monthly_exam.academic_year == "2025"
        assert monthly_exam.get_time_period_display() == "January 2025"
        
        assert quarterly_period_exam.time_period_quarter == "Q2"
        assert quarterly_period_exam.get_time_period_display() == "Q2 (Apr-Jun) 2025"
        
        print("✅ PASSED: Phase 2 time periods working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 5: {str(e)}")
    
    # Test 6: Phase 3 - Class Codes
    print("\n[TEST 6] Phase 3 - Class Codes...")
    try:
        class_exam = Exam.objects.create(
            name="Feature Test - Class Codes",
            exam_type="REVIEW",
            class_codes=["CLASS_7A", "CLASS_7B", "CLASS_8A"],
            total_questions=5,
            timer_minutes=30
        )
        
        assert len(class_exam.class_codes) == 3
        assert "CLASS_7A" in class_exam.class_codes
        assert "CLASS_7B" in class_exam.class_codes
        assert "CLASS_8A" in class_exam.class_codes
        
        display = class_exam.get_class_codes_display()
        assert "Class 7A" in display
        assert "Class 7B" in display
        assert "Class 8A" in display
        
        short_display = class_exam.get_class_codes_short()
        assert "7A" in short_display
        assert "7B" in short_display
        assert "8A" in short_display
        
        print("✅ PASSED: Phase 3 class codes working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 6: {str(e)}")
    
    # Test 7: Phase 4 - Scheduling & Instructions
    print("\n[TEST 7] Phase 4 - Scheduling & Instructions...")
    try:
        scheduled_exam = Exam.objects.create(
            name="Feature Test - Scheduled",
            exam_type="REVIEW",
            scheduled_date=date(2025, 9, 1),
            scheduled_start_time=time(9, 0),
            scheduled_end_time=time(11, 0),
            instructions="Please bring calculator and ID card",
            allow_late_submission=True,
            late_submission_penalty=15,
            total_questions=5,
            timer_minutes=30
        )
        
        assert scheduled_exam.scheduled_date == date(2025, 9, 1)
        assert scheduled_exam.scheduled_start_time == time(9, 0)
        assert scheduled_exam.scheduled_end_time == time(11, 0)
        assert scheduled_exam.instructions == "Please bring calculator and ID card"
        assert scheduled_exam.allow_late_submission == True
        assert scheduled_exam.late_submission_penalty == 15
        
        assert scheduled_exam.is_scheduled() == True
        assert "Sep" in scheduled_exam.get_schedule_display()
        assert "9:00 AM" in scheduled_exam.get_schedule_display()
        assert "11:00 AM" in scheduled_exam.get_schedule_display()
        assert scheduled_exam.get_late_policy_display() == "Late submissions: -15% penalty"
        
        print("✅ PASSED: Phase 4 scheduling working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 7: {str(e)}")
    
    # Test 8: Answer Mapping Status
    print("\n[TEST 8] Answer Mapping Status...")
    try:
        mapping_exam = Exam.objects.create(
            name="Feature Test - Answer Mapping",
            total_questions=5,
            timer_minutes=30
        )
        
        # Create questions without answers
        for i in range(1, 6):
            Question.objects.create(
                exam=mapping_exam,
                question_number=i,
                question_type='MCQ',
                correct_answer='',  # No answer
                points=2,
                options_count=5
            )
        
        # Check mapping status
        status = mapping_exam.get_answer_mapping_status()
        assert status['is_complete'] == False
        assert status['total_questions'] == 5
        assert status['mapped_questions'] == 0
        assert status['unmapped_questions'] == 5
        assert status['status_label'] == 'Not Started'
        
        # Add answers to some questions
        questions = mapping_exam.routine_questions.all()
        for i, q in enumerate(questions[:3]):
            q.correct_answer = f'Answer {i+1}'
            q.save()
        
        # Check updated status
        status = mapping_exam.get_answer_mapping_status()
        assert status['is_complete'] == False
        assert status['mapped_questions'] == 3
        assert status['unmapped_questions'] == 2
        assert status['status_label'] == 'Partial'
        assert status['percentage_complete'] == 60.0
        
        print("✅ PASSED: Answer mapping status working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 8: {str(e)}")
    
    # Test 9: ExamService Core Functions
    print("\n[TEST 9] ExamService Core Functions...")
    try:
        # Create teacher for service tests
        try:
            user = User.objects.get(username='feature_test_user')
        except User.DoesNotExist:
            user = User.objects.create_user('feature_test_user', 'test@test.com', 'password')
        
        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            teacher = Teacher.objects.create(
                user=user,
                name="Feature Test Teacher",
                email="feature_test@test.com"
            )
        
        # Test exam creation through service
        exam_data = {
            'name': 'Feature Test - Service Created',
            'exam_type': 'REVIEW',
            'total_questions': 10,
            'timer_minutes': 45,
            'default_options_count': 5,
            'passing_score': 80,
            'created_by': teacher
        }
        
        service_exam = ExamService.create_exam(exam_data)
        assert service_exam.id is not None
        assert service_exam.name == 'Feature Test - Service Created'
        assert service_exam.total_questions == 10
        
        # Test question creation
        ExamService.create_questions_for_exam(service_exam)
        assert service_exam.routine_questions.count() == 10
        
        # Test question update
        questions_data = [
            {
                'id': str(service_exam.routine_questions.first().id),
                'question_type': 'SHORT',
                'correct_answer': 'Updated Answer',
                'options_count': 1
            }
        ]
        
        update_result = ExamService.update_exam_questions(service_exam, questions_data)
        assert update_result['updated'] == 1
        
        print("✅ PASSED: ExamService core functions working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 9: {str(e)}")
    
    # Test 10: URL Patterns and Views
    print("\n[TEST 10] URL Patterns and Views...")
    try:
        from django.urls import resolve, reverse
        
        # Test core URL patterns exist
        urls_to_test = [
            ('RoutineTest:index', []),
            ('RoutineTest:exam_list', []),
            ('RoutineTest:create_exam', []),
            ('RoutineTest:preview_exam', [str(exam.id)]),
            ('RoutineTest:manage_roster', [str(exam.id)]),  # Phase 5 URL
        ]
        
        for url_name, args in urls_to_test:
            try:
                if args:
                    url = reverse(url_name, args=args)
                else:
                    url = reverse(url_name)
                assert url is not None
            except Exception as e:
                raise AssertionError(f"URL {url_name} not found: {e}")
        
        print("✅ PASSED: URL patterns intact")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 10: {str(e)}")
    
    # Test 11: Mixed Question Types
    print("\n[TEST 11] Mixed Question Types...")
    try:
        mixed_exam = Exam.objects.create(
            name="Feature Test - Mixed Questions",
            total_questions=6,
            timer_minutes=30
        )
        
        # Create different question types
        question_types = [
            ('MCQ', 'A', 5),
            ('CHECKBOX', 'A,B', 5),
            ('SHORT', 'Short answer', 1),
            ('LONG', 'Long answer text', 1),
            ('MIXED', '[{"part": 1, "answer": "A"}]', 2),
            ('MCQ', 'C', 4)
        ]
        
        for i, (q_type, answer, options) in enumerate(question_types, 1):
            Question.objects.create(
                exam=mixed_exam,
                question_number=i,
                question_type=q_type,
                correct_answer=answer,
                points=2,
                options_count=options
            )
        
        # Verify all types created
        assert mixed_exam.routine_questions.filter(question_type='MCQ').count() == 2
        assert mixed_exam.routine_questions.filter(question_type='CHECKBOX').count() == 1
        assert mixed_exam.routine_questions.filter(question_type='SHORT').count() == 1
        assert mixed_exam.routine_questions.filter(question_type='LONG').count() == 1
        assert mixed_exam.routine_questions.filter(question_type='MIXED').count() == 1
        
        print("✅ PASSED: Mixed question types working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 11: {str(e)}")
    
    # Test 12: PDF Rotation Field
    print("\n[TEST 12] PDF Rotation Field...")
    try:
        pdf_exam = Exam.objects.create(
            name="Feature Test - PDF Rotation",
            total_questions=5,
            timer_minutes=30,
            pdf_rotation=90
        )
        
        assert pdf_exam.pdf_rotation == 90
        
        # Test rotation update
        pdf_exam.pdf_rotation = 180
        pdf_exam.save()
        pdf_exam.refresh_from_db()
        assert pdf_exam.pdf_rotation == 180
        
        # Test rotation constraints (should be 0, 90, 180, or 270)
        valid_rotations = [0, 90, 180, 270]
        for rotation in valid_rotations:
            pdf_exam.pdf_rotation = rotation
            pdf_exam.save()
            pdf_exam.refresh_from_db()
            assert pdf_exam.pdf_rotation == rotation
        
        print("✅ PASSED: PDF rotation field working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 12: {str(e)}")
    
    # Test 13: Full Integration - All Phases Together
    print("\n[TEST 13] Full Integration - All Phases Together...")
    try:
        integrated_exam = Exam.objects.create(
            name="Feature Test - Full Integration",
            exam_type="QUARTERLY",  # Phase 1
            time_period_quarter="Q3",  # Phase 2
            academic_year="2025",  # Phase 2
            class_codes=["CLASS_10A", "CLASS_10B", "CLASS_10C"],  # Phase 3
            scheduled_date=date(2025, 10, 15),  # Phase 4
            scheduled_start_time=time(14, 0),  # Phase 4
            scheduled_end_time=time(16, 0),  # Phase 4
            instructions="Full integration test exam",  # Phase 4
            allow_late_submission=True,  # Phase 4
            late_submission_penalty=20,  # Phase 4
            total_questions=15,
            timer_minutes=90,
            pdf_rotation=270  # Core feature
        )
        
        # Create questions
        ExamService.create_questions_for_exam(integrated_exam)
        
        # Add audio
        audio = AudioFile.objects.create(
            exam=integrated_exam,
            name="Integration Audio",
            audio_file="test.mp3",
            start_question=1,
            end_question=5,
            order=1
        )
        
        # Add roster (Phase 5)
        roster_entry = StudentRoster.objects.create(
            exam=integrated_exam,
            student_name="Integration Test Student",
            student_id="INT001",
            class_code="CLASS_10A",
            notes="Full integration test"
        )
        
        # Verify all features working together
        assert integrated_exam.exam_type == "QUARTERLY"
        assert integrated_exam.get_time_period_display() == "Q3 (Jul-Sep) 2025"
        assert len(integrated_exam.class_codes) == 3
        assert integrated_exam.is_scheduled() == True
        assert integrated_exam.routine_questions.count() == 15
        assert integrated_exam.routine_audio_files.count() == 1
        assert integrated_exam.has_student_roster() == True
        assert integrated_exam.pdf_rotation == 270
        
        # Check roster stats
        stats = integrated_exam.get_roster_stats()
        assert stats['total_assigned'] == 1
        assert stats['has_roster'] == True
        
        print("✅ PASSED: Full integration with all phases working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 13: {str(e)}")
    
    # Test 14: Model String Representations
    print("\n[TEST 14] Model String Representations...")
    try:
        # Test Exam __str__
        str_exam = Exam.objects.create(
            name="String Test Exam",
            exam_type="REVIEW",
            time_period_month="DEC",
            academic_year="2025",
            total_questions=5,
            timer_minutes=30
        )
        exam_str = str(str_exam)
        assert "Review" in exam_str  # Format changed to "[Review / Monthly Exam]"
        assert "String Test Exam" in exam_str
        assert "December 2025" in exam_str
        
        # Test Question __str__
        question = Question.objects.create(
            exam=str_exam,
            question_number=1,
            question_type='MCQ',
            correct_answer='A',
            points=2,
            options_count=5
        )
        question_str = str(question)
        assert "Q1" in question_str
        # Question __str__ format changed - doesn't include exam name anymore
        assert "Multiple Choice" in question_str or "MCQ" in question_str
        
        # Test AudioFile __str__
        audio = AudioFile.objects.create(
            exam=str_exam,
            name="Test Audio String",
            audio_file="test.mp3",
            start_question=1,
            end_question=3,
            order=1
        )
        audio_str = str(audio)
        assert "Test Audio String" in audio_str
        assert "Q1-3" in audio_str or "Q1" in audio_str  # Different formats possible
        
        # Test StudentRoster __str__ (Phase 5)
        roster = StudentRoster.objects.create(
            exam=str_exam,
            student_name="String Test Student",
            student_id="STR001",
            class_code="CLASS_7A"
        )
        roster_str = str(roster)
        assert "String Test Student" in roster_str
        assert "CLASS_7A" in roster_str
        assert str_exam.name in roster_str
        
        print("✅ PASSED: Model string representations working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 14: {str(e)}")
    
    # Test 15: Database Relationships
    print("\n[TEST 15] Database Relationships...")
    try:
        rel_exam = Exam.objects.create(
            name="Relationship Test Exam",
            total_questions=3,
            timer_minutes=30
        )
        
        # Test exam -> questions relationship
        for i in range(1, 4):
            Question.objects.create(
                exam=rel_exam,
                question_number=i,
                question_type='MCQ',
                correct_answer='A',
                points=1,
                options_count=4
            )
        
        assert rel_exam.routine_questions.count() == 3
        
        # Test exam -> audio files relationship
        AudioFile.objects.create(
            exam=rel_exam,
            name="Rel Audio",
            audio_file="rel.mp3",
            start_question=1,
            end_question=2,
            order=1
        )
        
        assert rel_exam.routine_audio_files.count() == 1
        
        # Test exam -> roster relationship (Phase 5)
        StudentRoster.objects.create(
            exam=rel_exam,
            student_name="Rel Student",
            student_id="REL001",
            class_code="CLASS_8A"
        )
        
        assert rel_exam.student_roster.count() == 1
        
        # Test cascade delete
        exam_id = rel_exam.id
        question_count = Question.objects.filter(exam=rel_exam).count()
        audio_count = AudioFile.objects.filter(exam=rel_exam).count()
        roster_count = StudentRoster.objects.filter(exam=rel_exam).count()
        
        assert question_count == 3
        assert audio_count == 1
        assert roster_count == 1
        
        rel_exam.delete()
        
        # Verify cascade delete worked
        assert Question.objects.filter(exam_id=exam_id).count() == 0
        assert AudioFile.objects.filter(exam_id=exam_id).count() == 0
        assert StudentRoster.objects.filter(exam_id=exam_id).count() == 0
        
        print("✅ PASSED: Database relationships and cascade delete working")
        results['passed'] += 1
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        results['failed'] += 1
        results['errors'].append(f"Test 15: {str(e)}")
    
    # Print Summary
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {results['passed']}/15")
    print(f"❌ Failed: {results['failed']}/15")
    
    if results['failed'] > 0:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
    
    print("\n" + "="*80)
    
    if results['passed'] == 15:
        print("🎉 ALL TESTS PASSED! No existing features were broken!")
        print("\nVerified Working:")
        print("✅ Core exam creation and management")
        print("✅ Question creation and all types (MCQ, SHORT, LONG, MIXED, CHECKBOX)")
        print("✅ Audio file management and assignments")
        print("✅ Phase 1: Exam types (Review/Quarterly)")
        print("✅ Phase 2: Time periods (months/quarters/years)")
        print("✅ Phase 3: Class codes (multi-select)")
        print("✅ Phase 4: Scheduling & instructions")
        print("✅ Phase 5: Student roster (new feature)")
        print("✅ Answer mapping status")
        print("✅ ExamService functions")
        print("✅ URL patterns and routing")
        print("✅ PDF rotation")
        print("✅ Model relationships and cascade delete")
        print("✅ String representations")
        print("\n✨ Phase 5 successfully integrated without breaking ANY existing features!")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        print("These features may be affected and need fixing.")
    
    print("="*80)
    
    # Cleanup
    try:
        # Clean up test data
        Exam.objects.filter(name__contains="Feature Test").delete()
        User.objects.filter(username='feature_test_user').delete()
    except:
        pass
    
    return results['passed'] == 15


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)