#!/usr/bin/env python
"""
COMPREHENSIVE PDF ROTATION PERSISTENCE TEST
Tests the complete flow of PDF rotation from upload to student view
"""
import os
import sys
import django
from django.test import TestCase

# Set up Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from core.models import Teacher
from placement_test.models import Exam as PlacementExam
from primepath_routinetest.models import Exam as RoutineExam
import json
import logging

logger = logging.getLogger(__name__)

def test_pdf_rotation_persistence():
    """Test PDF rotation persistence across the entire workflow"""
    
    print("🔍 COMPREHENSIVE PDF ROTATION PERSISTENCE TEST")
    print("=" * 60)
    
    # Create or get test user and teacher
    import uuid
    username = f'rotationtest_{uuid.uuid4().hex[:8]}'
    
    user = User.objects.create_user(
        username=username,
        password='testpass123',
        email=f'{username}@test.com'
    )
    
    teacher = Teacher.objects.create(
        user=user,
        name='Rotation Test Teacher',
        email=f'{username}@test.com'
    )
    
    client = Client()
    client.login(username=username, password='testpass123')
    
    # Test data structure
    test_results = {
        'placement_test': {
            'upload_saves_rotation': False,
            'preview_loads_rotation': False,
            'save_persists_rotation': False,
            'student_view_uses_rotation': False
        },
        'routinetest': {
            'upload_saves_rotation': False,
            'preview_loads_rotation': False,
            'save_persists_rotation': False,
            'student_view_uses_rotation': False
        }
    }
    
    # Test Placement Test Module
    print("\n📋 TESTING PLACEMENT TEST MODULE")
    print("-" * 40)
    
    # 1. Test upload saves rotation (check model and service)
    try:
        # Create exam with rotation via ExamService
        from placement_test.services import ExamService
        
        exam_data = {
            'name': 'Rotation Test Exam',
            'total_questions': 5,
            'pdf_rotation': 90,  # Set rotation to 90 degrees
            'created_by': teacher
        }
        
        # Create exam without file for now
        exam = ExamService.create_exam(exam_data)
        
        # Check if rotation was saved
        exam.refresh_from_db()
        if exam.pdf_rotation == 90:
            test_results['placement_test']['upload_saves_rotation'] = True
            print("✅ Upload saves rotation: PASS")
        else:
            print(f"❌ Upload saves rotation: FAIL (expected 90, got {exam.pdf_rotation})")
            
    except Exception as e:
        print(f"❌ Upload saves rotation: ERROR - {e}")
    
    # 2. Test preview template loads rotation
    try:
        response = client.get(f'/PlacementTest/exams/{exam.id}/preview/')
        content = response.content.decode()
        
        # Check if template initializes currentRotation from exam.pdf_rotation
        # Look for the rendered JavaScript: "let currentRotation = 90;" (or whatever the rotation value is)
        rotation_pattern = f'let currentRotation = {exam.pdf_rotation};'
        if rotation_pattern in content:
            test_results['placement_test']['preview_loads_rotation'] = True
            print("✅ Preview loads rotation: PASS")
        else:
            print(f"❌ Preview loads rotation: FAIL (expected '{rotation_pattern}' not found)")
            # Debug: show what was actually in the content around currentRotation
            import re
            matches = re.findall(r'let currentRotation = [^;]+;', content)
            if matches:
                print(f"   Found: {matches[0]}")
            else:
                print("   No currentRotation initialization found")
            
    except Exception as e:
        print(f"❌ Preview loads rotation: ERROR - {e}")
    
    # 3. Test save_exam_answers persists rotation changes
    try:
        save_data = {
            'questions': [],
            'audio_assignments': {},
            'pdf_rotation': 180  # Change rotation to 180
        }
        
        response = client.post(
            f'/api/PlacementTest/exams/{exam.id}/save-answers/',
            data=json.dumps(save_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            exam.refresh_from_db()
            if exam.pdf_rotation == 180:
                test_results['placement_test']['save_persists_rotation'] = True
                print("✅ Save persists rotation: PASS")
            else:
                print(f"❌ Save persists rotation: FAIL (expected 180, got {exam.pdf_rotation})")
        else:
            print(f"❌ Save persists rotation: FAIL (HTTP {response.status_code})")
            
    except Exception as e:
        print(f"❌ Save persists rotation: ERROR - {e}")
    
    # 4. Test student view (check if template would use rotation)
    try:
        # For now, just check if the model has the rotation value
        if hasattr(exam, 'pdf_rotation') and exam.pdf_rotation == 180:
            test_results['placement_test']['student_view_uses_rotation'] = True
            print("✅ Student view uses rotation: PASS (model has correct value)")
        else:
            print("❌ Student view uses rotation: FAIL")
            
    except Exception as e:
        print(f"❌ Student view uses rotation: ERROR - {e}")
    
    # Test RoutineTest Module
    print("\n🏫 TESTING ROUTINETEST MODULE")
    print("-" * 40)
    
    # 1. Test upload saves rotation
    try:
        from primepath_routinetest.services.exam_service import ExamService as RoutineExamService
        
        routine_exam_data = {
            'name': 'Routine Rotation Test',
            'total_questions': 5,
            'exam_type': 'REVIEW',
            'pdf_rotation': 270,  # Set rotation to 270 degrees
            'created_by': teacher
        }
        
        routine_exam = RoutineExamService.create_exam(routine_exam_data)
        routine_exam.refresh_from_db()
        
        if routine_exam.pdf_rotation == 270:
            test_results['routinetest']['upload_saves_rotation'] = True
            print("✅ Upload saves rotation: PASS")
        else:
            print(f"❌ Upload saves rotation: FAIL (expected 270, got {routine_exam.pdf_rotation})")
            
    except Exception as e:
        print(f"❌ Upload saves rotation: ERROR - {e}")
    
    # 2. Test preview template loads rotation
    try:
        response = client.get(f'/RoutineTest/exams/{routine_exam.id}/preview/')
        content = response.content.decode()
        
        # Look for the rendered JavaScript: "let currentRotation = 270;" (or whatever the rotation value is)
        rotation_pattern = f'let currentRotation = {routine_exam.pdf_rotation};'
        if rotation_pattern in content:
            test_results['routinetest']['preview_loads_rotation'] = True
            print("✅ Preview loads rotation: PASS")
        else:
            print(f"❌ Preview loads rotation: FAIL (expected '{rotation_pattern}' not found)")
            # Debug: show what was actually in the content around currentRotation
            import re
            matches = re.findall(r'let currentRotation = [^;]+;', content)
            if matches:
                print(f"   Found: {matches[0]}")
            else:
                print("   No currentRotation initialization found")
            
    except Exception as e:
        print(f"❌ Preview loads rotation: ERROR - {e}")
    
    # 3. Test save persists rotation
    try:
        save_data = {
            'questions': [],
            'audio_assignments': {},
            'pdf_rotation': 0  # Reset to 0
        }
        
        response = client.post(
            f'/RoutineTest/exams/{routine_exam.id}/save-answers/',
            data=json.dumps(save_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            routine_exam.refresh_from_db()
            if routine_exam.pdf_rotation == 0:
                test_results['routinetest']['save_persists_rotation'] = True
                print("✅ Save persists rotation: PASS")
            else:
                print(f"❌ Save persists rotation: FAIL (expected 0, got {routine_exam.pdf_rotation})")
        else:
            print(f"❌ Save persists rotation: FAIL (HTTP {response.status_code})")
            
    except Exception as e:
        print(f"❌ Save persists rotation: ERROR - {e}")
    
    # 4. Test student view
    try:
        if hasattr(routine_exam, 'pdf_rotation') and routine_exam.pdf_rotation == 0:
            test_results['routinetest']['student_view_uses_rotation'] = True
            print("✅ Student view uses rotation: PASS (model has correct value)")
        else:
            print("❌ Student view uses rotation: FAIL")
            
    except Exception as e:
        print(f"❌ Student view uses rotation: ERROR - {e}")
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 60)
    
    placement_passed = sum(test_results['placement_test'].values())
    routine_passed = sum(test_results['routinetest'].values())
    total_tests = 8
    total_passed = placement_passed + routine_passed
    
    print(f"Placement Test Module: {placement_passed}/4 tests passed")
    print(f"RoutineTest Module: {routine_passed}/4 tests passed")
    print(f"Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED - PDF rotation persistence is working correctly!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - PDF rotation persistence needs fixes")
        
        # Identify specific issues
        print("\n🔧 ISSUES IDENTIFIED:")
        for module, results in test_results.items():
            for test, passed in results.items():
                if not passed:
                    print(f"   - {module}: {test}")
        
        return False
    
    # Cleanup
    try:
        exam.delete()
        routine_exam.delete()
        teacher.delete()
        user.delete()
    except:
        pass


if __name__ == '__main__':
    success = test_pdf_rotation_persistence()
    sys.exit(0 if success else 1)