#!/usr/bin/env python3
"""
Test: Program × SubProgram × Level Column in Schedule Matrix
"""

import os
import sys
import django

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from primepath_routinetest.views.schedule_matrix import get_class_curriculum_mapping, schedule_matrix_view
from primepath_routinetest.models import Exam
from core.models import Teacher, CurriculumLevel
from primepath_routinetest.models.class_access import TeacherClassAssignment

def test_curriculum_mapping():
    """Test the curriculum mapping functionality"""
    print("=" * 60)
    print("TEST: CURRICULUM COLUMN IN SCHEDULE MATRIX")
    print("=" * 60)
    print()
    
    # Test 1: Check curriculum mapping function
    print("Test 1: Testing get_class_curriculum_mapping function")
    print("-" * 40)
    
    # Get sample class codes
    test_classes = ['CLASS_7A', 'CLASS_8A', 'CLASS_9A']
    
    for class_code in test_classes:
        curriculum_info = get_class_curriculum_mapping(class_code, '2025')
        print(f"\nClass: {class_code}")
        print(f"  Review: {curriculum_info['review']['display'] if curriculum_info['review'] else 'None'}")
        print(f"  Quarterly: {curriculum_info['quarterly']['display'] if curriculum_info['quarterly'] else 'None'}")
        print(f"  Combined: {curriculum_info['combined']}")
    
    # Test 2: Check if any exams have curriculum levels assigned
    print("\n" + "=" * 60)
    print("Test 2: Exams with Curriculum Levels")
    print("-" * 40)
    
    exams_with_curriculum = Exam.objects.filter(
        curriculum_level__isnull=False
    ).select_related('curriculum_level__subprogram__program')[:5]
    
    if exams_with_curriculum:
        for exam in exams_with_curriculum:
            level = exam.curriculum_level
            print(f"\nExam: {exam.name}")
            print(f"  Type: {exam.get_exam_type_display_short()}")
            print(f"  Classes: {', '.join(exam.class_codes) if exam.class_codes else 'None'}")
            if level and level.subprogram:
                print(f"  Curriculum: {level.subprogram.program.name} × {level.subprogram.name} × Lv{level.level_number}")
            else:
                print(f"  Curriculum: Not properly linked")
    else:
        print("No exams with curriculum levels found!")
    
    # Test 3: Check view context
    print("\n" + "=" * 60)
    print("Test 3: Schedule Matrix View Context")
    print("-" * 40)
    
    # Create test user and teacher
    user, _ = User.objects.get_or_create(
        username='testteacher_curriculum',
        defaults={'password': 'testpass'}
    )
    
    teacher, _ = Teacher.objects.get_or_create(
        user=user,
        defaults={
            'name': 'Test Teacher Curriculum',
            'email': 'test_curriculum@example.com'
        }
    )
    
    # Ensure teacher has class assignments
    assignment, _ = TeacherClassAssignment.objects.get_or_create(
        teacher=teacher,
        class_code='CLASS_7A',
        defaults={
            'is_active': True,
            'access_level': 'FULL'
        }
    )
    
    # Create request
    factory = RequestFactory()
    request = factory.get('/RoutineTest/schedule-matrix/')
    request.user = user
    
    try:
        # Call the view
        response = schedule_matrix_view(request)
        
        if response.status_code == 200:
            print("✅ View rendered successfully")
            
            # Check for curriculum mapping in context
            if hasattr(response, 'context_data'):
                context = response.context_data
                if 'monthly_matrix' in context:
                    for class_code, class_data in context['monthly_matrix'].items():
                        if 'curriculum_mapping' in class_data:
                            print(f"✅ Class {class_code} has curriculum_mapping")
                            print(f"   Combined: {class_data['curriculum_mapping']['combined']}")
                            break
        else:
            print(f"❌ View returned status {response.status_code}")
    
    except Exception as e:
        print(f"Error testing view: {e}")
    
    # Cleanup
    User.objects.filter(username='testteacher_curriculum').delete()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_curriculum_mapping()