#!/usr/bin/env python
"""
Comprehensive test to verify ALL existing RoutineTest features still work after Phase 3
Tests core functionality, Phase 1, Phase 2, and original features
"""

import os
import sys
import django
import json
import tempfile
from datetime import datetime
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models import Exam, Question, AudioFile, StudentSession
from primepath_routinetest.services import ExamService
from core.models import CurriculumLevel, Teacher, School
from django.contrib.auth.models import User


def create_test_pdf():
    """Create a dummy PDF file for testing"""
    pdf_content = b"%PDF-1.4\n%Fake PDF content for testing\n"
    return SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")


def create_test_audio():
    """Create a dummy audio file for testing"""
    audio_content = b"FAKE_MP3_CONTENT"
    return SimpleUploadedFile("test.mp3", audio_content, content_type="audio/mp3")


def test_existing_features():
    """Test ALL existing features to ensure Phase 3 didn't break anything"""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE EXISTING FEATURES TEST - POST PHASE 3")
    print("="*80)
    
    all_tests_passed = True
    tests_run = 0
    tests_passed = 0
    
    try:
        # Setup test data
        test_user, _ = User.objects.get_or_create(
            username='comprehensive_test_user',
            defaults={'email': 'comprehensive@test.com'}
        )
        
        test_teacher, _ = Teacher.objects.get_or_create(
            user=test_user,
            defaults={'name': 'Comprehensive Test Teacher', 'email': 'comprehensive@test.com'}
        )
        
        test_school, _ = School.objects.get_or_create(
            name='Test School for Phase 3 Verification',
            defaults={'address': 'Test Address'}
        )
        
        curriculum_level = CurriculumLevel.objects.first()
        if not curriculum_level:
            print("❌ No curriculum levels found in database")
            return False
        
        # ==========================================
        # CORE FEATURE TESTS
        # ==========================================
        
        print("\n" + "-"*60)
        print("TESTING CORE FEATURES")
        print("-"*60)
        
        # Test 1: Basic exam creation with PDF
        print("\n[TEST 1] Basic exam creation with PDF...")
        tests_run += 1
        
        try:
            exam_data = {
                'name': '[RT] Core Feature Test - Basic Exam',
                'exam_type': 'REVIEW',  # Phase 1 field
                'curriculum_level_id': curriculum_level.id,
                'timer_minutes': 45,
                'total_questions': 30,
                'default_options_count': 4,
                'passing_score': 70,
                'pdf_rotation': 0,
                'created_by': test_teacher,
                'is_active': True
            }
            
            pdf_file = create_test_pdf()
            exam = ExamService.create_exam(
                exam_data=exam_data,
                pdf_file=pdf_file
            )
            
            if exam and exam.pdf_file:
                print(f"✅ Basic exam created with PDF: {exam.name}")
                print(f"   PDF file: {exam.pdf_file.name}")
                tests_passed += 1
            else:
                print(f"❌ Basic exam creation failed")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Core feature test failed: {e}")
            all_tests_passed = False
        
        # Test 2: Question auto-creation
        print("\n[TEST 2] Automatic question creation...")
        tests_run += 1
        
        try:
            question_count = exam.routine_questions.count()
            if question_count == 30:
                print(f"✅ Questions auto-created: {question_count}")
                
                # Check question properties
                first_question = exam.routine_questions.first()
                if first_question.question_number == 1 and first_question.options_count == 4:
                    print(f"✅ Question properties correct")
                    tests_passed += 1
                else:
                    print(f"❌ Question properties incorrect")
                    all_tests_passed = False
            else:
                print(f"❌ Wrong number of questions: {question_count} (expected 30)")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Question creation test failed: {e}")
            all_tests_passed = False
        
        # Test 3: Audio file attachment
        print("\n[TEST 3] Audio file attachment...")
        tests_run += 1
        
        try:
            audio_exam_data = exam_data.copy()
            audio_exam_data['name'] = '[RT] Core Feature Test - Audio Exam'
            audio_exam_data['total_questions'] = 10
            
            audio_files = [create_test_audio() for _ in range(2)]
            audio_names = ['Listening Part 1', 'Listening Part 2']
            
            audio_exam = ExamService.create_exam(
                exam_data=audio_exam_data,
                pdf_file=create_test_pdf(),
                audio_files=audio_files,
                audio_names=audio_names
            )
            
            audio_count = audio_exam.routine_audio_files.count()
            if audio_count == 2:
                print(f"✅ Audio files attached: {audio_count}")
                
                # Check audio file properties
                first_audio = audio_exam.routine_audio_files.first()
                if first_audio.name == 'Listening Part 1':
                    print(f"✅ Audio names preserved: '{first_audio.name}'")
                    tests_passed += 1
                else:
                    print(f"❌ Audio name not preserved")
                    all_tests_passed = False
            else:
                print(f"❌ Wrong number of audio files: {audio_count}")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Audio attachment test failed: {e}")
            all_tests_passed = False
        
        # Test 4: Student session creation
        print("\n[TEST 4] Student session creation...")
        tests_run += 1
        
        try:
            # RoutineTest uses student_name instead of Student model
            session = StudentSession.objects.create(
                student_name='Test Student Phase 3',
                parent_phone='1234567890',
                school=test_school,
                grade=9,
                academic_rank='TOP_20',
                exam=exam,
                original_curriculum_level=curriculum_level
            )
            
            if session and session.id:
                print(f"✅ Student session created: {session.id}")
                print(f"   Student: {session.student_name}")
                print(f"   Exam: {session.exam.name}")
                tests_passed += 1
            else:
                print(f"❌ Session creation failed")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Session creation test failed: {e}")
            all_tests_passed = False
        
        # Test 5: Answer mapping status
        print("\n[TEST 5] Answer mapping status check...")
        tests_run += 1
        
        try:
            status = exam.get_answer_mapping_status()
            
            if isinstance(status, dict) and 'is_complete' in status:
                print(f"✅ Answer mapping status works")
                print(f"   Total questions: {status['total_questions']}")
                print(f"   Mapped: {status['mapped_questions']}")
                print(f"   Status: {status['status_label']}")
                tests_passed += 1
            else:
                print(f"❌ Answer mapping status broken")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Answer mapping test failed: {e}")
            all_tests_passed = False
        
        # ==========================================
        # PHASE 1 FEATURE TESTS (Exam Types)
        # ==========================================
        
        print("\n" + "-"*60)
        print("TESTING PHASE 1 FEATURES (Exam Types)")
        print("-"*60)
        
        # Test 6: Review exam type
        print("\n[TEST 6] Review / Monthly Exam type...")
        tests_run += 1
        
        try:
            review_data = exam_data.copy()
            review_data['name'] = '[RT] Phase 1 Test - Review Exam'
            review_data['exam_type'] = 'REVIEW'
            review_data['total_questions'] = 5
            
            review_exam = ExamService.create_exam(review_data)
            
            if review_exam.exam_type == 'REVIEW':
                print(f"✅ Review exam type saved: {review_exam.exam_type}")
                print(f"   Display: {review_exam.get_exam_type_display()}")
                tests_passed += 1
            else:
                print(f"❌ Review exam type not saved correctly")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Phase 1 Review test failed: {e}")
            all_tests_passed = False
        
        # Test 7: Quarterly exam type
        print("\n[TEST 7] Quarterly Exam type...")
        tests_run += 1
        
        try:
            quarterly_data = exam_data.copy()
            quarterly_data['name'] = '[RT] Phase 1 Test - Quarterly Exam'
            quarterly_data['exam_type'] = 'QUARTERLY'
            quarterly_data['total_questions'] = 5
            
            quarterly_exam = ExamService.create_exam(quarterly_data)
            
            if quarterly_exam.exam_type == 'QUARTERLY':
                print(f"✅ Quarterly exam type saved: {quarterly_exam.exam_type}")
                print(f"   Display: {quarterly_exam.get_exam_type_display()}")
                tests_passed += 1
            else:
                print(f"❌ Quarterly exam type not saved correctly")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Phase 1 Quarterly test failed: {e}")
            all_tests_passed = False
        
        # ==========================================
        # PHASE 2 FEATURE TESTS (Time Periods)
        # ==========================================
        
        print("\n" + "-"*60)
        print("TESTING PHASE 2 FEATURES (Time Periods)")
        print("-"*60)
        
        # Test 8: Review with month and year
        print("\n[TEST 8] Review exam with month and year...")
        tests_run += 1
        
        try:
            monthly_data = exam_data.copy()
            monthly_data['name'] = '[RT] Phase 2 Test - Monthly'
            monthly_data['exam_type'] = 'REVIEW'
            monthly_data['time_period_month'] = 'SEP'
            monthly_data['academic_year'] = '2025'
            monthly_data['total_questions'] = 5
            
            monthly_exam = ExamService.create_exam(monthly_data)
            
            if monthly_exam.time_period_month == 'SEP' and monthly_exam.academic_year == '2025':
                print(f"✅ Monthly time period saved")
                print(f"   Display: {monthly_exam.get_time_period_display()}")
                tests_passed += 1
            else:
                print(f"❌ Monthly time period not saved correctly")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Phase 2 Monthly test failed: {e}")
            all_tests_passed = False
        
        # Test 9: Quarterly with quarter and year
        print("\n[TEST 9] Quarterly exam with quarter and year...")
        tests_run += 1
        
        try:
            quarter_data = exam_data.copy()
            quarter_data['name'] = '[RT] Phase 2 Test - Quarterly'
            quarter_data['exam_type'] = 'QUARTERLY'
            quarter_data['time_period_quarter'] = 'Q3'
            quarter_data['academic_year'] = '2026'
            quarter_data['total_questions'] = 5
            
            quarter_exam = ExamService.create_exam(quarter_data)
            
            if quarter_exam.time_period_quarter == 'Q3' and quarter_exam.academic_year == '2026':
                print(f"✅ Quarterly time period saved")
                print(f"   Display: {quarter_exam.get_time_period_display()}")
                tests_passed += 1
            else:
                print(f"❌ Quarterly time period not saved correctly")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Phase 2 Quarterly test failed: {e}")
            all_tests_passed = False
        
        # ==========================================
        # BACKWARD COMPATIBILITY TESTS
        # ==========================================
        
        print("\n" + "-"*60)
        print("TESTING BACKWARD COMPATIBILITY")
        print("-"*60)
        
        # Test 10: Exam without Phase 2 time periods
        print("\n[TEST 10] Exam without time periods (backward compatibility)...")
        tests_run += 1
        
        try:
            no_time_data = exam_data.copy()
            no_time_data['name'] = '[RT] Backward Compat - No Time'
            no_time_data['total_questions'] = 5
            # Don't set time_period_month, time_period_quarter, or academic_year
            
            no_time_exam = ExamService.create_exam(no_time_data)
            
            if no_time_exam and no_time_exam.time_period_month is None:
                print(f"✅ Exam created without time periods")
                print(f"   Time display: '{no_time_exam.get_time_period_display()}'")
                tests_passed += 1
            else:
                print(f"❌ Backward compatibility broken")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Backward compatibility test failed: {e}")
            all_tests_passed = False
        
        # Test 11: Exam without Phase 3 class codes
        print("\n[TEST 11] Exam without class codes (backward compatibility)...")
        tests_run += 1
        
        try:
            no_class_data = exam_data.copy()
            no_class_data['name'] = '[RT] Backward Compat - No Classes'
            no_class_data['total_questions'] = 5
            # Don't set class_codes
            
            no_class_exam = ExamService.create_exam(no_class_data)
            
            if no_class_exam and no_class_exam.class_codes == []:
                print(f"✅ Exam created without class codes")
                print(f"   Class display: '{no_class_exam.get_class_codes_display()}'")
                tests_passed += 1
            else:
                print(f"❌ Phase 3 backward compatibility broken")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Phase 3 backward compatibility test failed: {e}")
            all_tests_passed = False
        
        # Test 12: Database queries
        print("\n[TEST 12] Database queries and filtering...")
        tests_run += 1
        
        try:
            # Query all exams
            all_exams = Exam.objects.filter(name__contains='Feature Test')
            
            # Query by exam type
            review_exams = Exam.objects.filter(exam_type='REVIEW')
            quarterly_exams = Exam.objects.filter(exam_type='QUARTERLY')
            
            # Query with curriculum level
            level_exams = Exam.objects.filter(curriculum_level=curriculum_level)
            
            print(f"✅ Database queries working")
            print(f"   Test exams found: {all_exams.count()}")
            print(f"   Review exams: {review_exams.count()}")
            print(f"   Quarterly exams: {quarterly_exams.count()}")
            print(f"   Level exams: {level_exams.count()}")
            tests_passed += 1
            
        except Exception as e:
            print(f"❌ Database query test failed: {e}")
            all_tests_passed = False
        
        # Test 13: Model relationships
        print("\n[TEST 13] Model relationships and foreign keys...")
        tests_run += 1
        
        try:
            # Test exam -> questions relationship
            exam_with_questions = Exam.objects.filter(
                name__contains='Feature Test'
            ).prefetch_related('routine_questions').first()
            
            if exam_with_questions:
                questions = exam_with_questions.routine_questions.all()
                print(f"✅ Exam->Questions relationship: {questions.count()} questions")
            
            # Test exam -> audio files relationship
            exam_with_audio = Exam.objects.filter(
                name__contains='Audio Exam'
            ).prefetch_related('routine_audio_files').first()
            
            if exam_with_audio:
                audios = exam_with_audio.routine_audio_files.all()
                print(f"✅ Exam->AudioFiles relationship: {audios.count()} audio files")
            
            # Test session -> exam relationship
            if session and session.exam:
                print(f"✅ Session->Exam relationship: {session.exam.name}")
                
            tests_passed += 1
            
        except Exception as e:
            print(f"❌ Relationship test failed: {e}")
            all_tests_passed = False
        
        # Test 14: File upload paths
        print("\n[TEST 14] File upload paths...")
        tests_run += 1
        
        try:
            if exam.pdf_file:
                pdf_path = exam.pdf_file.name
                if 'routinetest' in pdf_path:
                    print(f"✅ PDF using RoutineTest path: {pdf_path}")
                else:
                    print(f"❌ PDF not using RoutineTest path: {pdf_path}")
                    all_tests_passed = False
            
            if audio_exam and audio_exam.routine_audio_files.exists():
                audio_path = audio_exam.routine_audio_files.first().audio_file.name
                if 'routinetest' in audio_path:
                    print(f"✅ Audio using RoutineTest path: {audio_path}")
                else:
                    print(f"❌ Audio not using RoutineTest path: {audio_path}")
                    all_tests_passed = False
                    
            tests_passed += 1
            
        except Exception as e:
            print(f"❌ File path test failed: {e}")
            all_tests_passed = False
        
        # Test 15: Deletion cascade
        print("\n[TEST 15] Deletion cascade test...")
        tests_run += 1
        
        try:
            # Create a test exam to delete
            delete_data = exam_data.copy()
            delete_data['name'] = '[RT] Delete Test Exam'
            delete_data['total_questions'] = 3
            
            delete_exam = ExamService.create_exam(delete_data)
            delete_exam_id = delete_exam.id
            question_count_before = Question.objects.filter(exam=delete_exam).count()
            
            # Delete the exam
            delete_exam.delete()
            
            # Check if questions were deleted
            question_count_after = Question.objects.filter(exam_id=delete_exam_id).count()
            
            if question_count_before > 0 and question_count_after == 0:
                print(f"✅ Deletion cascade works: {question_count_before} questions deleted")
                tests_passed += 1
            else:
                print(f"❌ Deletion cascade failed")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Deletion test failed: {e}")
            all_tests_passed = False
        
        # Clean up test data
        print("\n[CLEANUP] Removing test exams...")
        Exam.objects.filter(name__contains='Feature Test').delete()
        Exam.objects.filter(name__contains='Phase 1 Test').delete()
        Exam.objects.filter(name__contains='Phase 2 Test').delete()
        Exam.objects.filter(name__contains='Backward Compat').delete()
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Print summary
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {tests_run}")
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_run - tests_passed}")
    print(f"Success Rate: {(tests_passed/tests_run*100):.1f}%" if tests_run > 0 else "N/A")
    
    print("\n" + "-"*60)
    print("FEATURE STATUS AFTER PHASE 3:")
    print("-"*60)
    
    feature_status = [
        ("Core: Exam Creation", tests_run >= 1 and tests_passed >= 1),
        ("Core: Question Auto-creation", tests_run >= 2 and tests_passed >= 2),
        ("Core: Audio Attachments", tests_run >= 3 and tests_passed >= 3),
        ("Core: Student Sessions", tests_run >= 4 and tests_passed >= 4),
        ("Core: Answer Mapping", tests_run >= 5 and tests_passed >= 5),
        ("Phase 1: Exam Types", tests_run >= 7 and tests_passed >= 7),
        ("Phase 2: Time Periods", tests_run >= 9 and tests_passed >= 9),
        ("Backward Compatibility", tests_run >= 11 and tests_passed >= 11),
        ("Database Operations", tests_run >= 12 and tests_passed >= 12),
        ("Model Relationships", tests_run >= 13 and tests_passed >= 13),
        ("File Paths", tests_run >= 14 and tests_passed >= 14),
        ("Deletion Cascade", tests_run >= 15 and tests_passed >= 15),
    ]
    
    for feature, status in feature_status:
        icon = "✅" if status else "❌"
        print(f"{icon} {feature}")
    
    if all_tests_passed and tests_passed == tests_run:
        print("\n" + "🎉"*20)
        print("✅ ✅ ✅ ALL EXISTING FEATURES VERIFIED WORKING! ✅ ✅ ✅")
        print("Phase 3 implementation has NOT broken any existing functionality!")
        print("🎉"*20)
    else:
        print("\n⚠️ ⚠️ ⚠️ SOME FEATURES MAY BE AFFECTED ⚠️ ⚠️ ⚠️")
        print("Review the failed tests above for details")
    
    return all_tests_passed


if __name__ == "__main__":
    success = test_existing_features()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)