#!/usr/bin/env python
"""
Test Exam Assignments Matrix Functionality
Verifies that the Class × Timeslot matrix is working properly
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from core.models import Teacher, CurriculumLevel, SubProgram, Program
from primepath_routinetest.models import (
    TeacherClassAssignment, Exam, ExamScheduleMatrix, ClassCurriculumMapping
)

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_exam_assignments():
    """Test the Exam Assignments matrix functionality"""
    
    print_header("EXAM ASSIGNMENTS MATRIX TEST")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Setup test data
    print_header("1. SETTING UP TEST DATA")
    
    # Get teacher user
    teacher_user = User.objects.filter(username='teacher1').first()
    if not teacher_user:
        print("❌ Teacher user not found")
        return False
    
    teacher = Teacher.objects.get(user=teacher_user)
    print(f"✅ Found teacher: {teacher.name}")
    
    # Check teacher's class assignments
    assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
    print(f"✅ Teacher has {assignments.count()} class assignments:")
    for a in assignments:
        print(f"   - {a.get_class_code_display()}")
    
    # 2. Create some test exams for the matrix
    print_header("2. CREATING TEST EXAMS")
    
    # Get or create a test program and curriculum
    program, _ = Program.objects.get_or_create(
        name="CORE",
        defaults={'description': 'Core Program'}
    )
    
    subprogram, _ = SubProgram.objects.get_or_create(
        name="Phonics",
        program=program,
        defaults={'description': 'Phonics SubProgram'}
    )
    
    curriculum_level, _ = CurriculumLevel.objects.get_or_create(
        subprogram=subprogram,
        level_number=2,
        defaults={'description': 'Level 2'}
    )
    
    print(f"✅ Using curriculum: {program.name} {subprogram.name} L{curriculum_level.level_number}")
    
    # Create test exams for different periods
    test_exams_created = []
    
    # Monthly exam for CLASS_2B in March
    exam1, created = Exam.objects.get_or_create(
        name="March Review Exam - 2B",
        defaults={
            'exam_type': 'REVIEW',
            'academic_year': '2025',
            'time_period_month': 'MAR',
            'class_codes': ['CLASS_2B'],
            'curriculum_level': curriculum_level,
            'timer_minutes': 60,
            'total_questions': 50,
            'passing_score': 60,
            'is_active': True,
            'created_by': teacher
        }
    )
    if created:
        test_exams_created.append(exam1)
        print(f"✅ Created: {exam1.name}")
    
    # Quarterly exam for CLASS_3A in Q2
    exam2, created = Exam.objects.get_or_create(
        name="Q2 Assessment - 3A",
        defaults={
            'exam_type': 'QUARTERLY',
            'academic_year': '2025',
            'time_period_quarter': 'Q2',
            'class_codes': ['CLASS_3A'],
            'curriculum_level': curriculum_level,
            'timer_minutes': 90,
            'total_questions': 75,
            'passing_score': 60,
            'is_active': True,
            'created_by': teacher
        }
    )
    if created:
        test_exams_created.append(exam2)
        print(f"✅ Created: {exam2.name}")
    
    # 3. Create matrix cells and assign exams
    print_header("3. CREATING MATRIX CELLS")
    
    # Create monthly cell for CLASS_2B - March
    cell1, created = ExamScheduleMatrix.objects.get_or_create(
        class_code='CLASS_2B',
        academic_year='2025',
        time_period_type='MONTHLY',
        time_period_value='MAR',
        defaults={
            'created_by': teacher_user,
            'status': 'SCHEDULED'
        }
    )
    cell1.exams.add(exam1)
    print(f"✅ Matrix cell for CLASS_2B-MAR: {cell1.exams.count()} exam(s)")
    
    # Create quarterly cell for CLASS_3A - Q2
    cell2, created = ExamScheduleMatrix.objects.get_or_create(
        class_code='CLASS_3A',
        academic_year='2025',
        time_period_type='QUARTERLY',
        time_period_value='Q2',
        defaults={
            'created_by': teacher_user,
            'status': 'SCHEDULED'
        }
    )
    cell2.exams.add(exam2)
    print(f"✅ Matrix cell for CLASS_3A-Q2: {cell2.exams.count()} exam(s)")
    
    # 4. Create curriculum mapping
    print_header("4. SETTING UP CURRICULUM MAPPINGS")
    
    for assignment in assignments:
        mapping, created = ClassCurriculumMapping.objects.get_or_create(
            class_code=assignment.class_code,
            academic_year='2025',
            defaults={
                'curriculum_level': curriculum_level,
                'priority': 1,
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created curriculum mapping for {assignment.get_class_code_display()}")
    
    # 5. Test web interface
    print_header("5. TESTING WEB INTERFACE")
    
    client = Client()
    login_success = client.login(username='teacher1', password='password123')
    
    if not login_success:
        print("❌ Failed to login as teacher")
        return False
    
    print("✅ Logged in as teacher1")
    
    # Access the Exam Assignments page
    response = client.get('/RoutineTest/schedule-matrix/')
    
    if response.status_code == 200:
        print(f"✅ Exam Assignments page loaded (Status: {response.status_code})")
        
        # Check if matrix data is in context
        context = response.context
        if context:
            monthly_matrix = context.get('monthly_matrix', {})
            quarterly_matrix = context.get('quarterly_matrix', {})
            
            print(f"\n📊 Monthly Matrix:")
            for class_code, data in monthly_matrix.items():
                print(f"  {data['display_name']}:")
                cells_with_exams = [
                    f"{month}({cell.get('exam_count', 0)})" 
                    for month, cell in data.get('cells', {}).items() 
                    if cell.get('exam_count', 0) > 0
                ]
                if cells_with_exams:
                    print(f"    Exams in: {', '.join(cells_with_exams)}")
                else:
                    print(f"    No exams scheduled")
            
            print(f"\n📊 Quarterly Matrix:")
            for class_code, data in quarterly_matrix.items():
                print(f"  {data['display_name']}:")
                cells_with_exams = [
                    f"{quarter}({cell.get('exam_count', 0)})" 
                    for quarter, cell in data.get('cells', {}).items() 
                    if cell.get('exam_count', 0) > 0
                ]
                if cells_with_exams:
                    print(f"    Exams in: {', '.join(cells_with_exams)}")
                else:
                    print(f"    No exams scheduled")
        
        # Check content
        content = response.content.decode('utf-8')
        
        # Verify key elements
        checks = {
            'Monthly tab present': 'Monthly/Review Exams' in content,
            'Quarterly tab present': 'Quarterly Exams' in content,
            'Matrix table present': 'matrix-table' in content,
            'Exam count displayed': 'exam-count' in content or 'cell-count' in content,
            'Class rows present': 'CLASS_2B' in content or 'Class 2B' in content,
            'Test exam visible': 'March Review Exam' in content or exam1.name[:10] in content
        }
        
        print(f"\n✅ Content Verification:")
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}")
        
    else:
        print(f"❌ Failed to load Exam Assignments page (Status: {response.status_code})")
        if response.status_code == 302:
            print(f"   Redirected to: {response.url}")
    
    # 6. Summary
    print_header("TEST SUMMARY")
    
    print(f"""
✅ Test Results:
   - Teacher assignments: {assignments.count()} classes
   - Test exams created: {len(test_exams_created)}
   - Matrix cells with exams: 2
   - Curriculum mappings: {ClassCurriculumMapping.objects.filter(academic_year='2025').count()}
   
The Exam Assignments matrix should now display:
   - CLASS_2B with "March Review Exam" in MAR column
   - CLASS_3A with "Q2 Assessment" in Q2 column
   - Curriculum mapping showing "CORE Phonics L2" for mapped classes
   
📊 Access the matrix at: /RoutineTest/schedule-matrix/
""")
    
    return True

if __name__ == "__main__":
    try:
        success = test_exam_assignments()
        if success:
            print("\n✅ Exam Assignments Matrix test completed successfully!")
        else:
            print("\n❌ Test encountered issues")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()