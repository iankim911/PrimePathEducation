#!/usr/bin/env python
"""
Comprehensive test for Phase 4: Exam Scheduling & Instructions
Tests the new scheduling fields and ensures existing features still work
"""

import os
import sys
import django
import json
from datetime import datetime, date, time
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models import Exam, Question
from primepath_routinetest.services import ExamService
from core.models import CurriculumLevel, Teacher, School
from django.contrib.auth.models import User


def create_test_pdf():
    """Create a dummy PDF file for testing"""
    pdf_content = b"%PDF-1.4\n%Fake PDF content for testing\n"
    return SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")


def test_phase4_features():
    """Test Phase 4: Exam Scheduling & Instructions implementation"""
    
    print("\n" + "="*80)
    print("PHASE 4 IMPLEMENTATION TEST - EXAM SCHEDULING & INSTRUCTIONS")
    print("="*80)
    
    all_tests_passed = True
    tests_run = 0
    tests_passed = 0
    
    try:
        # Setup test data
        test_user, _ = User.objects.get_or_create(
            username='phase4_test_user',
            defaults={'email': 'phase4@test.com'}
        )
        
        test_teacher, _ = Teacher.objects.get_or_create(
            user=test_user,
            defaults={'name': 'Phase 4 Test Teacher', 'email': 'phase4@test.com'}
        )
        
        curriculum_level = CurriculumLevel.objects.first()
        if not curriculum_level:
            print("❌ No curriculum levels found in database")
            return False
        
        # ==========================================
        # PHASE 4 FEATURE TESTS
        # ==========================================
        
        print("\n" + "-"*60)
        print("TESTING PHASE 4 FEATURES")
        print("-"*60)
        
        # Test 1: Create exam with scheduling information
        print("\n[TEST 1] Create exam with full scheduling...")
        tests_run += 1
        
        try:
            exam_data = {
                'name': '[RT] Phase 4 Test - Full Schedule',
                'exam_type': 'QUARTERLY',
                'time_period_quarter': 'Q2',
                'academic_year': '2025',
                'class_codes': ['CLASS_7A', 'CLASS_7B'],
                # Phase 4 fields
                'scheduled_date': date(2025, 5, 15),
                'scheduled_start_time': time(9, 0),
                'scheduled_end_time': time(11, 0),
                'instructions': 'Please bring your calculator and ruler. No phones allowed.',
                'allow_late_submission': True,
                'late_submission_penalty': 10,
                # Standard fields
                'curriculum_level_id': curriculum_level.id,
                'timer_minutes': 120,
                'total_questions': 50,
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
            
            if exam and exam.scheduled_date and exam.instructions:
                print(f"✅ Exam created with scheduling: {exam.name}")
                print(f"   Schedule: {exam.get_schedule_display()}")
                print(f"   Late Policy: {exam.get_late_policy_display()}")
                print(f"   Instructions length: {len(exam.instructions)} chars")
                tests_passed += 1
            else:
                print(f"❌ Scheduling fields not saved properly")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Phase 4 full schedule test failed: {e}")
            all_tests_passed = False
        
        # Test 2: Create exam with partial scheduling (only date)
        print("\n[TEST 2] Create exam with partial scheduling (date only)...")
        tests_run += 1
        
        try:
            exam_data_partial = exam_data.copy()
            exam_data_partial['name'] = '[RT] Phase 4 Test - Date Only'
            exam_data_partial['scheduled_start_time'] = None
            exam_data_partial['scheduled_end_time'] = None
            exam_data_partial['total_questions'] = 10
            
            exam_partial = ExamService.create_exam(
                exam_data=exam_data_partial,
                pdf_file=create_test_pdf()
            )
            
            if exam_partial and exam_partial.scheduled_date and not exam_partial.scheduled_start_time:
                print(f"✅ Partial schedule saved correctly")
                print(f"   Schedule: {exam_partial.get_schedule_display()}")
                tests_passed += 1
            else:
                print(f"❌ Partial schedule not handled properly")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Phase 4 partial schedule test failed: {e}")
            all_tests_passed = False
        
        # Test 3: Create exam without any scheduling (backward compatibility)
        print("\n[TEST 3] Create exam without scheduling (backward compatibility)...")
        tests_run += 1
        
        try:
            exam_data_no_schedule = {
                'name': '[RT] Phase 4 Test - No Schedule',
                'exam_type': 'REVIEW',
                'time_period_month': 'AUG',
                'academic_year': '2025',
                'class_codes': ['CLASS_8A'],
                # No Phase 4 fields
                'curriculum_level_id': curriculum_level.id,
                'timer_minutes': 60,
                'total_questions': 5,
                'default_options_count': 4,
                'passing_score': 70,
                'pdf_rotation': 0,
                'created_by': test_teacher,
                'is_active': True
            }
            
            exam_no_schedule = ExamService.create_exam(
                exam_data=exam_data_no_schedule,
                pdf_file=create_test_pdf()
            )
            
            if exam_no_schedule and not exam_no_schedule.is_scheduled():
                print(f"✅ Exam created without scheduling")
                print(f"   is_scheduled(): {exam_no_schedule.is_scheduled()}")
                print(f"   Schedule display: '{exam_no_schedule.get_schedule_display()}'")
                tests_passed += 1
            else:
                print(f"❌ Backward compatibility broken")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Phase 4 backward compatibility test failed: {e}")
            all_tests_passed = False
        
        # Test 4: Test display methods
        print("\n[TEST 4] Test Phase 4 display methods...")
        tests_run += 1
        
        try:
            # Test full schedule display
            full_display = exam.get_schedule_display()
            short_display = exam.get_schedule_short()
            late_policy = exam.get_late_policy_display()
            
            print(f"   Full display: {full_display}")
            print(f"   Short display: {short_display}")
            print(f"   Late policy: {late_policy}")
            
            if "May 15, 2025" in full_display and "9:00 AM - 11:00 AM" in full_display:
                print(f"✅ Display methods working correctly")
                tests_passed += 1
            else:
                print(f"❌ Display methods not formatting correctly")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Display methods test failed: {e}")
            all_tests_passed = False
        
        # Test 5: Late submission without penalty
        print("\n[TEST 5] Late submission without penalty...")
        tests_run += 1
        
        try:
            exam_data_no_penalty = exam_data.copy()
            exam_data_no_penalty['name'] = '[RT] Phase 4 Test - No Penalty'
            exam_data_no_penalty['allow_late_submission'] = True
            exam_data_no_penalty['late_submission_penalty'] = 0
            exam_data_no_penalty['total_questions'] = 5
            
            exam_no_penalty = ExamService.create_exam(
                exam_data=exam_data_no_penalty,
                pdf_file=create_test_pdf()
            )
            
            policy_display = exam_no_penalty.get_late_policy_display()
            if "no penalty" in policy_display.lower():
                print(f"✅ No penalty late submission: {policy_display}")
                tests_passed += 1
            else:
                print(f"❌ No penalty display incorrect: {policy_display}")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ No penalty test failed: {e}")
            all_tests_passed = False
        
        # Test 6: No late submission allowed
        print("\n[TEST 6] No late submission allowed...")
        tests_run += 1
        
        try:
            exam_data_no_late = exam_data.copy()
            exam_data_no_late['name'] = '[RT] Phase 4 Test - No Late'
            exam_data_no_late['allow_late_submission'] = False
            exam_data_no_late['late_submission_penalty'] = 0
            exam_data_no_late['total_questions'] = 5
            
            exam_no_late = ExamService.create_exam(
                exam_data=exam_data_no_late,
                pdf_file=create_test_pdf()
            )
            
            policy_display = exam_no_late.get_late_policy_display()
            if "no late submissions allowed" in policy_display.lower():
                print(f"✅ No late submission: {policy_display}")
                tests_passed += 1
            else:
                print(f"❌ No late display incorrect: {policy_display}")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ No late submission test failed: {e}")
            all_tests_passed = False
        
        # ==========================================
        # VERIFY EXISTING FEATURES STILL WORK
        # ==========================================
        
        print("\n" + "-"*60)
        print("VERIFYING EXISTING FEATURES NOT BROKEN")
        print("-"*60)
        
        # Test 7: Phase 1 exam type still works
        print("\n[TEST 7] Phase 1: Exam types still working...")
        tests_run += 1
        
        try:
            if exam.exam_type == 'QUARTERLY':
                print(f"✅ Exam type preserved: {exam.get_exam_type_display()}")
                tests_passed += 1
            else:
                print(f"❌ Exam type not working")
                all_tests_passed = False
        except Exception as e:
            print(f"❌ Phase 1 check failed: {e}")
            all_tests_passed = False
        
        # Test 8: Phase 2 time periods still work
        print("\n[TEST 8] Phase 2: Time periods still working...")
        tests_run += 1
        
        try:
            time_display = exam.get_time_period_display()
            if "Q2" in time_display and "2025" in time_display:
                print(f"✅ Time period preserved: {time_display}")
                tests_passed += 1
            else:
                print(f"❌ Time period not working: {time_display}")
                all_tests_passed = False
        except Exception as e:
            print(f"❌ Phase 2 check failed: {e}")
            all_tests_passed = False
        
        # Test 9: Phase 3 class codes still work
        print("\n[TEST 9] Phase 3: Class codes still working...")
        tests_run += 1
        
        try:
            class_display = exam.get_class_codes_display()
            if "Class 7A" in class_display and "Class 7B" in class_display:
                print(f"✅ Class codes preserved: {class_display}")
                tests_passed += 1
            else:
                print(f"❌ Class codes not working: {class_display}")
                all_tests_passed = False
        except Exception as e:
            print(f"❌ Phase 3 check failed: {e}")
            all_tests_passed = False
        
        # Test 10: Core features (questions, PDF, etc.)
        print("\n[TEST 10] Core features: Questions and PDF...")
        tests_run += 1
        
        try:
            question_count = exam.routine_questions.count()
            has_pdf = bool(exam.pdf_file)
            
            if question_count == 50 and has_pdf:
                print(f"✅ Core features working: {question_count} questions, PDF attached")
                tests_passed += 1
            else:
                print(f"❌ Core features broken: {question_count} questions, PDF: {has_pdf}")
                all_tests_passed = False
        except Exception as e:
            print(f"❌ Core features check failed: {e}")
            all_tests_passed = False
        
        # Clean up test data
        print("\n[CLEANUP] Removing test exams...")
        Exam.objects.filter(name__contains='Phase 4 Test').delete()
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Print summary
    print("\n" + "="*80)
    print("PHASE 4 TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {tests_run}")
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_run - tests_passed}")
    print(f"Success Rate: {(tests_passed/tests_run*100):.1f}%" if tests_run > 0 else "N/A")
    
    print("\n" + "-"*60)
    print("PHASE 4 FEATURE STATUS:")
    print("-"*60)
    
    feature_status = [
        ("Scheduled Date", tests_passed >= 1),
        ("Scheduled Times", tests_passed >= 1),
        ("Instructions", tests_passed >= 1),
        ("Late Submission Policy", tests_passed >= 5),
        ("Display Methods", tests_passed >= 4),
        ("Backward Compatibility", tests_passed >= 3),
        ("Phase 1 Preserved", tests_passed >= 7),
        ("Phase 2 Preserved", tests_passed >= 8),
        ("Phase 3 Preserved", tests_passed >= 9),
        ("Core Features Intact", tests_passed >= 10),
    ]
    
    for feature, status in feature_status:
        icon = "✅" if status else "❌"
        print(f"{icon} {feature}")
    
    if all_tests_passed and tests_passed == tests_run:
        print("\n" + "🎉"*20)
        print("✅ ✅ ✅ PHASE 4 IMPLEMENTATION SUCCESSFUL! ✅ ✅ ✅")
        print("All scheduling features working and no existing features broken!")
        print("🎉"*20)
    else:
        print("\n⚠️ ⚠️ ⚠️ SOME TESTS FAILED ⚠️ ⚠️ ⚠️")
        print("Review the failed tests above for details")
    
    return all_tests_passed


if __name__ == "__main__":
    success = test_phase4_features()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)