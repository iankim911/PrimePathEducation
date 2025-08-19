#!/usr/bin/env python3
"""
Comprehensive test for exam copy UI fix
Tests multiple exam types, classes, and time periods
"""

import os
import sys
import django
import json
import logging
from datetime import datetime

# Set up Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_comprehensive_copy_scenarios():
    """Test comprehensive exam copy scenarios"""
    logger.info("=== Comprehensive Exam Copy UI Fix Test ===")
    
    try:
        from primepath_routinetest.models.exam_management import RoutineExam
        from primepath_routinetest.models.exam_schedule_matrix import ExamScheduleMatrix
        from primepath_routinetest.views.exam_api import copy_exam, get_class_exams
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        from core.models import Teacher
        
        # Create test request factory
        factory = RequestFactory()
        
        # Get an existing teacher or use the first available
        test_user = User.objects.first()
        if not test_user:
            logger.error("No users found in database")
            return False
        
        test_teacher = Teacher.objects.filter(user=test_user).first()
        if not test_teacher:
            logger.error("No teachers found in database")
            return False
            
        logger.info(f"Using teacher: {test_teacher.name}")
        
        # Test scenarios
        test_scenarios = [
            {
                'name': 'Review Exam - January',
                'source_class': 'HIGH_10B',
                'target_class': 'CLASS_2B',
                'time_period': 'JAN',
                'exam_type': 'REVIEW'
            },
            {
                'name': 'Review Exam - March', 
                'source_class': 'HIGH_10B',
                'target_class': 'CLASS_3A',
                'time_period': 'MAR',
                'exam_type': 'REVIEW'
            },
            {
                'name': 'Quarterly Exam - Q1',
                'source_class': 'HIGH_10B', 
                'target_class': 'CLASS_2B',
                'time_period': 'Q1',
                'exam_type': 'QUARTERLY'
            },
            {
                'name': 'Quarterly Exam - Q2',
                'source_class': 'HIGH_10B',
                'target_class': 'CLASS_4A', 
                'time_period': 'Q2',
                'exam_type': 'QUARTERLY'
            }
        ]
        
        passed_tests = 0
        total_tests = len(test_scenarios)
        
        for scenario in test_scenarios:
            logger.info(f"\n--- Testing: {scenario['name']} ---")
            
            # Find an exam of the appropriate type
            if scenario['exam_type'] == 'REVIEW':
                source_exam = RoutineExam.objects.filter(
                    is_active=True,
                    exam_type__in=['REVIEW', 'monthly_review']
                ).first()
            else:
                source_exam = RoutineExam.objects.filter(
                    is_active=True,
                    exam_type__in=['QUARTERLY', 'quarterly']
                ).first()
            
            if not source_exam:
                logger.warning(f"No {scenario['exam_type']} exam found, skipping scenario")
                continue
                
            logger.info(f"Using exam: {source_exam.name} (ID: {source_exam.id})")
            
            # Test copy operation
            copy_request_data = {
                'source_exam_id': str(source_exam.id),
                'target_class': scenario['target_class'],
                'target_timeslot': scenario['time_period']
            }
            
            copy_request = factory.post(
                '/RoutineTest/api/copy-exam/',
                data=json.dumps(copy_request_data),
                content_type='application/json'
            )
            copy_request.user = test_user
            
            # Call the copy function
            copy_response = copy_exam(copy_request)
            
            if copy_response.status_code != 200:
                copy_result = json.loads(copy_response.content)
                logger.error(f"❌ Copy failed: {copy_result}")
                continue
            
            logger.info("✅ Copy operation successful")
            
            # Test get_class_exams with CORRECT time period (our fix)
            correct_request = factory.get(
                f'/RoutineTest/api/class/{scenario["target_class"]}/exams/?timeslot={scenario["time_period"]}'
            )
            correct_request.user = test_user
            
            correct_response = get_class_exams(correct_request, scenario['target_class'])
            
            if correct_response.status_code == 200:
                correct_result = json.loads(correct_response.content)
                exams_found = len(correct_result.get('exams', []))
                
                # Check if our copied exam is present
                copied_exam_found = False
                for exam in correct_result.get('exams', []):
                    if exam['id'] == str(source_exam.id):
                        copied_exam_found = True
                        break
                
                if copied_exam_found:
                    logger.info("✅ Copied exam found with CORRECT timeslot")
                else:
                    logger.error(f"❌ Copied exam NOT found with correct timeslot")
                    logger.error(f"Found exams: {[e['name'] for e in correct_result.get('exams', [])]}")
                    continue
            else:
                logger.error("❌ Failed to get exams with correct timeslot")
                continue
            
            # Test get_class_exams with WRONG time period (the old bug)
            wrong_timeslot = 'overview'  # This is what was causing the bug
            wrong_request = factory.get(
                f'/RoutineTest/api/class/{scenario["target_class"]}/exams/?timeslot={wrong_timeslot}'
            )
            wrong_request.user = test_user
            
            wrong_response = get_class_exams(wrong_request, scenario['target_class'])
            
            if wrong_response.status_code == 200:
                wrong_result = json.loads(wrong_response.content)
                wrong_exams_found = len(wrong_result.get('exams', []))
                
                # The copied exam should NOT be found with wrong timeslot
                wrong_exam_found = False
                for exam in wrong_result.get('exams', []):
                    if exam['id'] == str(source_exam.id):
                        wrong_exam_found = True
                        break
                
                if not wrong_exam_found:
                    logger.info("✅ Copied exam correctly NOT found with wrong timeslot")
                else:
                    logger.warning("⚠️ Copied exam unexpectedly found with wrong timeslot")
            
            # Clean up - remove from matrix
            try:
                matrix_entries = ExamScheduleMatrix.objects.filter(
                    class_code=scenario['target_class'],
                    time_period_value=scenario['time_period'],
                    exams=source_exam
                )
                for matrix in matrix_entries:
                    matrix.exams.remove(source_exam)
                    logger.info("Cleaned up test data")
            except Exception as cleanup_error:
                logger.warning(f"Cleanup error: {cleanup_error}")
            
            passed_tests += 1
            logger.info(f"✅ Scenario '{scenario['name']}' PASSED")
        
        # Final results
        logger.info(f"\n=== Final Results ===")
        logger.info(f"✅ Passed: {passed_tests}/{total_tests} scenarios")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED - Exam copy UI fix is working correctly!")
            return True
        else:
            logger.warning(f"⚠️ Some tests failed ({total_tests - passed_tests} failed)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_comprehensive_copy_scenarios()
    if success:
        print("\n✅ COMPREHENSIVE TEST PASSED")
        print("The exam copy UI fix handles multiple exam types and time periods correctly.")
        print("Users will now see copied exams immediately in the UI.")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please check the logs above for details.")
        sys.exit(1)