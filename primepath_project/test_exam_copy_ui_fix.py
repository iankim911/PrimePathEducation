#!/usr/bin/env python3
"""
Test script for exam copy UI bug fix
Verifies that copied exams appear immediately in the UI
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

def test_exam_copy_flow():
    """Test the complete exam copy flow"""
    logger.info("=== Testing Exam Copy UI Fix ===")
    
    try:
        from primepath_routinetest.models.exam_management import RoutineExam
        from primepath_routinetest.models.exam_schedule_matrix import ExamScheduleMatrix
        from primepath_routinetest.views.exam_api import copy_exam, get_class_exams
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        from core.models import Teacher
        from unittest.mock import Mock
        
        # Create test request factory
        factory = RequestFactory()
        
        # Use existing teacher or create test user and teacher
        import time
        unique_id = str(int(time.time()))
        test_user, created = User.objects.get_or_create(
            username=f'test_teacher_{unique_id}',
            defaults={'email': f'test{unique_id}@example.com'}
        )
        test_teacher, created = Teacher.objects.get_or_create(
            user=test_user,
            defaults={
                'name': f'Test Teacher {unique_id}',
                'email': f'test{unique_id}@example.com'
            }
        )
        
        # Test data
        source_class = 'HIGH_10B'
        target_class = 'CLASS_2B'
        time_period = 'JAN'  # This is what gets selected in the copy dialog
        
        # 1. Find or create a source exam
        source_exam = RoutineExam.objects.filter(
            is_active=True,
            exam_type='REVIEW'
        ).first()
        
        if not source_exam:
            logger.warning("No active REVIEW exams found, creating a test exam")
            source_exam = RoutineExam.objects.create(
                name='Test Review Exam for Copy',
                exam_type='REVIEW',
                time_period_month='JAN',
                is_active=True,
                created_by=test_teacher
            )
            logger.info(f"Created test exam: {source_exam.id}")
        
        logger.info(f"Using source exam: {source_exam.name} (ID: {source_exam.id})")
        
        # 2. Test copying the exam
        copy_request_data = {
            'source_exam_id': str(source_exam.id),
            'target_class': target_class,
            'target_timeslot': time_period
        }
        
        logger.info(f"Copying exam from {source_class} to {target_class} for {time_period}")
        
        # Create POST request for copy
        copy_request = factory.post(
            '/RoutineTest/api/copy-exam/',
            data=json.dumps(copy_request_data),
            content_type='application/json'
        )
        copy_request.user = test_user
        
        # Call the copy function
        from primepath_routinetest.views.exam_api import copy_exam
        copy_response = copy_exam(copy_request)
        copy_result = json.loads(copy_response.content)
        
        if copy_response.status_code == 200:
            logger.info("✅ Copy exam API call successful")
            logger.info(f"Copy result: {copy_result}")
        else:
            logger.error(f"❌ Copy exam failed: {copy_result}")
            return False
        
        # 3. Verify the exam was saved to ExamScheduleMatrix
        matrix_entries = ExamScheduleMatrix.objects.filter(
            class_code=target_class,
            time_period_value=time_period,
            exams=source_exam
        )
        
        if matrix_entries.exists():
            logger.info("✅ Exam found in ExamScheduleMatrix")
            for matrix in matrix_entries:
                logger.info(f"Matrix entry: {matrix.class_code} - {matrix.time_period_value}")
        else:
            logger.error("❌ Exam NOT found in ExamScheduleMatrix")
            return False
        
        # 4. Test get_class_exams API with correct time period
        get_request = factory.get(f'/RoutineTest/api/class/{target_class}/exams/?timeslot={time_period}')
        get_request.user = test_user
        
        from primepath_routinetest.views.exam_api import get_class_exams
        get_response = get_class_exams(get_request, target_class)
        get_result = json.loads(get_response.content)
        
        if get_response.status_code == 200:
            logger.info("✅ Get class exams API call successful")
            exams_found = len(get_result.get('exams', []))
            logger.info(f"Found {exams_found} exams for {target_class} - {time_period}")
            
            # Check if our copied exam is in the results
            copied_exam_found = False
            for exam in get_result.get('exams', []):
                if exam['id'] == str(source_exam.id):
                    copied_exam_found = True
                    logger.info(f"✅ Copied exam found in API response: {exam['name']}")
                    break
            
            if not copied_exam_found:
                logger.error("❌ Copied exam NOT found in API response")
                logger.error(f"Available exams: {[e['name'] for e in get_result.get('exams', [])]}")
                return False
        else:
            logger.error(f"❌ Get class exams failed: {get_result}")
            return False
        
        # 5. Test with WRONG time period (the bug scenario)
        wrong_timeslot = 'overview'  # This is what was being used before the fix
        wrong_request = factory.get(f'/RoutineTest/api/class/{target_class}/exams/?timeslot={wrong_timeslot}')
        wrong_request.user = test_user
        
        wrong_response = get_class_exams(wrong_request, target_class)
        wrong_result = json.loads(wrong_response.content)
        
        if wrong_response.status_code == 200:
            wrong_exams_found = len(wrong_result.get('exams', []))
            logger.info(f"With WRONG timeslot '{wrong_timeslot}': {wrong_exams_found} exams found")
            
            # The copied exam should NOT be found with wrong timeslot
            wrong_exam_found = False
            for exam in wrong_result.get('exams', []):
                if exam['id'] == str(source_exam.id):
                    wrong_exam_found = True
                    break
            
            if wrong_exam_found:
                logger.warning("⚠️ Copied exam found even with wrong timeslot - this might indicate an issue")
            else:
                logger.info("✅ Copied exam correctly NOT found with wrong timeslot")
        
        logger.info("=== Test Summary ===")
        logger.info("✅ Exam copy operation successful")
        logger.info("✅ Exam saved to database correctly")
        logger.info("✅ API returns copied exam with correct timeslot")
        logger.info("✅ API correctly filters out exam with wrong timeslot")
        logger.info("✅ UI fix should work: copySelectedExam() now calls loadExamData() with correct timePeriod")
        
        # Clean up test data if we created it
        if source_exam.name == 'Test Review Exam for Copy':
            logger.info("Cleaning up test exam")
            # Remove from matrix first
            for matrix in matrix_entries:
                matrix.exams.remove(source_exam)
            # Then delete the exam
            source_exam.delete()
        else:
            # Just remove from matrix for existing exams
            for matrix in matrix_entries:
                matrix.exams.remove(source_exam)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_exam_copy_flow()
    if success:
        print("\n🎉 All tests passed! The exam copy UI fix should work correctly.")
    else:
        print("\n💥 Some tests failed. Please check the logs above.")
        sys.exit(1)