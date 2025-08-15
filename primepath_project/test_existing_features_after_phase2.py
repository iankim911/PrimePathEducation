#!/usr/bin/env python
"""
Comprehensive test to verify existing features still work after Phase 2 implementation
Tests all critical RoutineTest functionality to ensure nothing was broken
"""
import os
import sys
import django
import json
from pathlib import Path

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models.exam import Exam, AudioFile
from primepath_routinetest.models.question import Question
from primepath_routinetest.models.session import StudentSession
from primepath_routinetest.services.exam_service import ExamService
from primepath_routinetest.services.session_service import SessionService
from core.models import Teacher, CurriculumLevel, School
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
import traceback

def test_existing_features():
    """Test all existing features to ensure Phase 2 didn't break anything"""
    print("\n" + "="*70)
    print("EXISTING FEATURES VERIFICATION TEST - POST PHASE 2")
    print("="*70)
    
    failures = []
    successes = []
    
    # Test 1: Basic exam creation WITHOUT time period fields (backward compatibility)
    print("\n[TEST 1] Testing basic exam creation WITHOUT time period fields...")
    try:
        user, _ = User.objects.get_or_create(
            username='phase2_verifier',
            defaults={'email': 'verify@phase2.com'}
        )
        teacher, _ = Teacher.objects.get_or_create(
            user=user,
            defaults={'name': 'Phase 2 Verifier', 'email': 'verify@phase2.com'}
        )
        
        # Get a curriculum level
        curriculum_level = CurriculumLevel.objects.filter(
            subprogram__program__name='CORE',
            subprogram__name='Phonics',
            level_number=1
        ).first()
        
        pdf_content = b"%PDF-1.4\ntest"
        pdf_file = SimpleUploadedFile("test_no_period.pdf", pdf_content, content_type="application/pdf")
        
        # Create exam WITHOUT time period fields (testing backward compatibility)
        exam_data = {
            'name': '[RoutineTest] Backward Compatibility Test',
            'exam_type': 'REVIEW',
            # Intentionally NOT including time_period_month, time_period_quarter, academic_year
            'curriculum_level_id': curriculum_level.id if curriculum_level else None,
            'total_questions': 15,
            'timer_minutes': 30,
            'created_by': teacher,
            'pdf_rotation': 0,
            'default_options_count': 5,
            'passing_score': 0,
            'is_active': True
        }
        
        exam = ExamService.create_exam(
            exam_data=exam_data,
            pdf_file=pdf_file
        )
        
        if exam and exam.id:
            print(f"✅ Backward compatibility works - exam created without time periods")
            print(f"   - Exam ID: {exam.id}")
            print(f"   - Exam type: {exam.exam_type}")
            print(f"   - Time period month: {exam.time_period_month} (should be None)")
            print(f"   - Time period quarter: {exam.time_period_quarter} (should be None)")
            print(f"   - Academic year: {exam.academic_year} (should be None)")
            print(f"   - Questions created: {exam.routine_questions.count()}")
            successes.append("Backward compatibility")
        else:
            failures.append("Backward compatibility - exam creation failed")
            print("❌ Backward compatibility failed")
            
    except Exception as e:
        failures.append(f"Backward compatibility: {str(e)}")
        print(f"❌ Error in backward compatibility test: {str(e)}")
        traceback.print_exc()
    
    # Test 2: Exam creation WITH time period fields (Phase 2 feature)
    print("\n[TEST 2] Testing exam creation WITH time period fields...")
    try:
        pdf_file2 = SimpleUploadedFile("test_with_period.pdf", pdf_content, content_type="application/pdf")
        
        exam_data2 = {
            'name': '[RoutineTest] Phase 2 Feature Test',
            'exam_type': 'QUARTERLY',
            'time_period_quarter': 'Q3',
            'academic_year': '2026',
            'curriculum_level_id': curriculum_level.id if curriculum_level else None,
            'total_questions': 25,
            'timer_minutes': 60,
            'created_by': teacher,
            'is_active': True
        }
        
        exam2 = ExamService.create_exam(
            exam_data=exam_data2,
            pdf_file=pdf_file2
        )
        
        if exam2 and exam2.time_period_quarter == 'Q3' and exam2.academic_year == '2026':
            print(f"✅ Phase 2 features working correctly")
            print(f"   - Exam ID: {exam2.id}")
            print(f"   - Time period: {exam2.get_time_period_display()}")
            successes.append("Phase 2 time period features")
        else:
            failures.append("Phase 2 features not working")
            print("❌ Phase 2 features failed")
            
    except Exception as e:
        failures.append(f"Phase 2 features: {str(e)}")
        print(f"❌ Error in Phase 2 features: {str(e)}")
    
    # Test 3: Audio file attachment (unchanged feature)
    print("\n[TEST 3] Testing audio file attachment...")
    try:
        audio_content = b"RIFF\x24\x00\x00\x00WAVEfmt "
        audio_file = SimpleUploadedFile("test_audio.wav", audio_content, content_type="audio/wav")
        
        audio_obj = AudioFile.objects.create(
            exam=exam,
            audio_file=audio_file,
            name="Test Audio Phase 2",
            start_question=1,
            end_question=5,
            order=1
        )
        
        if audio_obj.id:
            print(f"✅ Audio file attachment still works")
            print(f"   - Audio ID: {audio_obj.id}")
            print(f"   - Associated with exam: {audio_obj.exam.name}")
            successes.append("Audio file attachment")
        else:
            failures.append("Audio file attachment failed")
            print("❌ Audio file attachment failed")
            
    except Exception as e:
        failures.append(f"Audio attachment: {str(e)}")
        print(f"❌ Error in audio attachment: {str(e)}")
    
    # Test 4: Question management (unchanged feature)
    print("\n[TEST 4] Testing question management...")
    try:
        questions = exam.routine_questions.all()
        if questions.count() == exam.total_questions:
            print(f"✅ Questions auto-created correctly: {questions.count()}")
            
            # Update a question
            first_question = questions.first()
            first_question.question_type = 'LONG'
            first_question.correct_answer = 'Phase 2 Test Answer'
            first_question.points = 5
            first_question.save()
            
            # Verify update
            updated = Question.objects.get(id=first_question.id)
            if updated.correct_answer == 'Phase 2 Test Answer' and updated.points == 5:
                print(f"✅ Question update works")
                print(f"   - Question type: {updated.question_type}")
                print(f"   - Points: {updated.points}")
                successes.append("Question management")
            else:
                failures.append("Question update failed")
                print("❌ Question update failed")
        else:
            failures.append(f"Question count mismatch: {questions.count()} vs {exam.total_questions}")
            print(f"❌ Question count mismatch")
            
    except Exception as e:
        failures.append(f"Question management: {str(e)}")
        print(f"❌ Error in question management: {str(e)}")
    
    # Test 5: Student session creation (unchanged feature)
    print("\n[TEST 5] Testing student session creation...")
    try:
        session_data = {
            'student_name': 'Phase 2 Test Student',
            'parent_phone': '9876543210',
            'school_name': 'Phase 2 Test School',
            'grade': 9,
            'academic_rank': 'TOP_10'
        }
        
        session = SessionService.create_session(
            exam=exam,
            student_data=session_data,
            curriculum_level_id=curriculum_level.id if curriculum_level else None,
            request_meta={}
        )
        
        if session and session.id:
            print(f"✅ Student session creation works")
            print(f"   - Session ID: {session.id}")
            print(f"   - Student: {session.student_name}")
            print(f"   - Exam: {session.exam.name}")
            successes.append("Student session creation")
        else:
            failures.append("Session creation failed")
            print("❌ Session creation failed")
            
    except Exception as e:
        failures.append(f"Session creation: {str(e)}")
        print(f"❌ Error in session creation: {str(e)}")
    
    # Test 6: Model relationships
    print("\n[TEST 6] Testing model relationships...")
    try:
        # Test exam -> questions relationship
        question_count = exam.routine_questions.count()
        
        # Test exam -> audio files relationship
        audio_count = exam.routine_audio_files.count()
        
        # Test exam -> sessions relationship
        session_count = exam.routine_sessions.count()
        
        print(f"✅ Model relationships intact:")
        print(f"   - Questions: {question_count}")
        print(f"   - Audio files: {audio_count}")
        print(f"   - Sessions: {session_count}")
        successes.append("Model relationships")
        
    except Exception as e:
        failures.append(f"Model relationships: {str(e)}")
        print(f"❌ Error checking relationships: {str(e)}")
    
    # Test 7: Answer mapping status (unchanged feature)
    print("\n[TEST 7] Testing answer mapping status...")
    try:
        status = exam.get_answer_mapping_status()
        
        if isinstance(status, dict) and 'is_complete' in status:
            print(f"✅ Answer mapping status works")
            print(f"   - Total questions: {status['total_questions']}")
            print(f"   - Mapped: {status['mapped_questions']}")
            print(f"   - Status: {status['status_label']}")
            successes.append("Answer mapping status")
        else:
            failures.append("Answer mapping status failed")
            print("❌ Answer mapping status failed")
            
    except Exception as e:
        failures.append(f"Answer mapping status: {str(e)}")
        print(f"❌ Error in answer mapping: {str(e)}")
    
    # Test 8: __str__ methods with and without time periods
    print("\n[TEST 8] Testing __str__ methods...")
    try:
        str1 = str(exam)  # Exam without time period
        str2 = str(exam2)  # Exam with time period
        
        print(f"   Without time period: {str1}")
        print(f"   With time period: {str2}")
        
        # Should not error out
        if isinstance(str1, str) and isinstance(str2, str):
            print("✅ __str__ methods handle both cases")
            successes.append("String representations")
        else:
            failures.append("String representation failed")
            print("❌ String representation failed")
            
    except Exception as e:
        failures.append(f"String methods: {str(e)}")
        print(f"❌ Error in string methods: {str(e)}")
    
    # Test 9: File upload paths (unchanged feature)
    print("\n[TEST 9] Testing file upload paths...")
    try:
        pdf_path = exam.pdf_file.name if exam.pdf_file else None
        audio_path = audio_obj.audio_file.name if audio_obj and audio_obj.audio_file else None
        
        if pdf_path and 'routinetest/exams/pdfs/' in pdf_path:
            print(f"✅ PDF upload path correct: {pdf_path}")
            successes.append("PDF upload path")
        else:
            failures.append(f"PDF path incorrect: {pdf_path}")
            print(f"❌ PDF path issue: {pdf_path}")
            
        if audio_path and 'routinetest/exams/audio/' in audio_path:
            print(f"✅ Audio upload path correct: {audio_path}")
            successes.append("Audio upload path")
        else:
            failures.append(f"Audio path incorrect: {audio_path}")
            print(f"❌ Audio path issue: {audio_path}")
            
    except Exception as e:
        failures.append(f"File paths: {str(e)}")
        print(f"❌ Error checking file paths: {str(e)}")
    
    # Test 10: Database queries with new fields
    print("\n[TEST 10] Testing database queries...")
    try:
        # Test various queries including new fields
        active_exams = Exam.objects.filter(is_active=True).count()
        review_exams = Exam.objects.filter(exam_type='REVIEW').count()
        quarterly_exams = Exam.objects.filter(exam_type='QUARTERLY').count()
        exams_with_year = Exam.objects.filter(academic_year__isnull=False).count()
        exams_without_year = Exam.objects.filter(academic_year__isnull=True).count()
        
        print(f"✅ Database queries work:")
        print(f"   - Active exams: {active_exams}")
        print(f"   - Review exams: {review_exams}")
        print(f"   - Quarterly exams: {quarterly_exams}")
        print(f"   - Exams with year: {exams_with_year}")
        print(f"   - Exams without year: {exams_without_year}")
        successes.append("Database queries")
        
    except Exception as e:
        failures.append(f"Database queries: {str(e)}")
        print(f"❌ Error in queries: {str(e)}")
    
    # Test 11: Exam type feature from Phase 1
    print("\n[TEST 11] Testing Phase 1 exam type feature...")
    try:
        # Create exam with just exam_type (Phase 1 feature)
        pdf_file3 = SimpleUploadedFile("test_phase1.pdf", pdf_content, content_type="application/pdf")
        
        exam_data3 = {
            'name': '[RoutineTest] Phase 1 Check',
            'exam_type': 'REVIEW',  # Phase 1 feature
            # No time period fields - testing Phase 1 still works
            'total_questions': 10,
            'timer_minutes': 20,
            'created_by': teacher
        }
        
        exam3 = ExamService.create_exam(
            exam_data=exam_data3,
            pdf_file=pdf_file3
        )
        
        if exam3 and exam3.exam_type == 'REVIEW':
            print(f"✅ Phase 1 exam type feature still works")
            print(f"   - Exam type: {exam3.get_exam_type_display()}")
            successes.append("Phase 1 exam type feature")
        else:
            failures.append("Phase 1 exam type feature broken")
            print("❌ Phase 1 exam type feature broken")
        
        # Cleanup
        exam3.delete()
        
    except Exception as e:
        failures.append(f"Phase 1 feature: {str(e)}")
        print(f"❌ Error in Phase 1 feature: {str(e)}")
    
    # Test 12: Exam deletion cascade (unchanged feature)
    print("\n[TEST 12] Testing exam deletion cascade...")
    try:
        # Get counts before deletion
        exam_id = exam.id
        question_ids = list(exam.routine_questions.values_list('id', flat=True))
        
        # Delete exam
        exam.delete()
        
        # Check cascades
        questions_remaining = Question.objects.filter(id__in=question_ids).count()
        sessions_remaining = StudentSession.objects.filter(exam_id=exam_id).count()
        
        if questions_remaining == 0 and sessions_remaining == 0:
            print(f"✅ Deletion cascade works correctly")
            print(f"   - Questions deleted: {len(question_ids)}")
            print(f"   - Sessions deleted: Confirmed")
            successes.append("Deletion cascade")
        else:
            failures.append(f"Cascade issue: {questions_remaining} questions, {sessions_remaining} sessions remain")
            print(f"❌ Cascade deletion issue")
            
    except Exception as e:
        failures.append(f"Deletion cascade: {str(e)}")
        print(f"❌ Error in deletion: {str(e)}")
    
    # Cleanup remaining test exam
    try:
        exam2.delete()
    except:
        pass
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total_tests = len(successes) + len(failures)
    print(f"\n✅ Successful: {len(successes)}/{total_tests}")
    for success in successes:
        print(f"   • {success}")
    
    if failures:
        print(f"\n❌ Failed: {len(failures)}/{total_tests}")
        for failure in failures:
            print(f"   • {failure}")
    else:
        print("\n🎉 ALL EXISTING FEATURES WORKING PERFECTLY!")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    
    if not failures:
        print("✅ Phase 2 implementation did NOT break any existing features!")
        print("✅ Backward compatibility maintained")
        print("✅ Phase 1 features still working")
        print("✅ All core functionality intact")
        print("✅ Model relationships preserved")
        print("✅ File uploads working as expected")
        return True
    else:
        print("⚠️  Some issues detected - review failures above")
        print("Note: Some failures may be due to test data issues rather than Phase 2 changes")
        return False

if __name__ == '__main__':
    success = test_existing_features()
    sys.exit(0 if success else 1)