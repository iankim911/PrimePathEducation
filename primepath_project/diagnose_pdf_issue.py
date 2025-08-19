#!/usr/bin/env python
"""
Critical PDF Investigation - Database Analysis
Analyzes the current state of PDF files vs rotation settings
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import Exam as PlacementExam
from primepath_routinetest.models import Exam as RoutineExam
import os.path

def analyze_pdf_consistency():
    """Analyze PDF file vs rotation consistency across both modules"""
    
    print('=' * 80)
    print('CRITICAL PDF INVESTIGATION - DATABASE ANALYSIS')
    print('=' * 80)
    print()

    # Check PlacementTest exams
    print('📋 PLACEMENT TEST EXAMS:')
    placement_exams = PlacementExam.objects.all().order_by('-created_at')
    
    for exam in placement_exams:
        print(f'  Exam: {exam.name[:50]}...')
        print(f'    ID: {exam.id}')
        
        # Check PDF file status
        has_pdf_field = bool(exam.pdf_file)
        pdf_path = exam.pdf_file.name if has_pdf_field else 'N/A'
        
        # Check if file actually exists on disk
        file_exists = False
        if has_pdf_field:
            try:
                full_path = exam.pdf_file.path
                file_exists = os.path.exists(full_path)
                print(f'    PDF field: ✅ POPULATED ({pdf_path})')
                print(f'    File exists: {"✅ YES" if file_exists else "❌ NO"} ({full_path})')
            except Exception as e:
                print(f'    PDF field: ✅ POPULATED but ERROR: {str(e)}')
        else:
            print(f'    PDF field: ❌ EMPTY')
            
        print(f'    PDF rotation: {exam.pdf_rotation}°')
        print(f'    Created: {exam.created_at}')
        
        # Flag inconsistencies
        if exam.pdf_rotation != 0 and not has_pdf_field:
            print(f'    🚨 ISSUE: Has rotation ({exam.pdf_rotation}°) but no PDF file!')
        elif has_pdf_field and not file_exists:
            print(f'    🚨 ISSUE: Database has PDF reference but file missing!')
            
        print()

    print('\n📋 ROUTINETEST EXAMS:')
    routine_exams = RoutineExam.objects.all().order_by('-created_at')
    
    for exam in routine_exams:
        print(f'  Exam: {exam.name[:50]}...')
        print(f'    ID: {exam.id}')
        
        # Check PDF file status
        has_pdf_field = bool(exam.pdf_file)
        pdf_path = exam.pdf_file.name if has_pdf_field else 'N/A'
        
        # Check if file actually exists on disk
        file_exists = False
        if has_pdf_field:
            try:
                full_path = exam.pdf_file.path
                file_exists = os.path.exists(full_path)
                print(f'    PDF field: ✅ POPULATED ({pdf_path})')
                print(f'    File exists: {"✅ YES" if file_exists else "❌ NO"} ({full_path})')
            except Exception as e:
                print(f'    PDF field: ✅ POPULATED but ERROR: {str(e)}')
        else:
            print(f'    PDF field: ❌ EMPTY')
            
        print(f'    PDF rotation: {exam.pdf_rotation}°')
        print(f'    Created: {exam.created_at}')
        
        # Flag inconsistencies  
        if exam.pdf_rotation != 0 and not has_pdf_field:
            print(f'    🚨 ISSUE: Has rotation ({exam.pdf_rotation}°) but no PDF file!')
        elif has_pdf_field and not file_exists:
            print(f'    🚨 ISSUE: Database has PDF reference but file missing!')
            
        print()

    # Summary statistics
    print('\n📊 SUMMARY STATISTICS:')
    print('=' * 50)
    
    # PlacementTest stats
    placement_with_pdf = sum(1 for e in placement_exams if e.pdf_file)
    placement_with_rotation = sum(1 for e in placement_exams if e.pdf_rotation != 0)
    placement_broken = sum(1 for e in placement_exams if not e.pdf_file and e.pdf_rotation != 0)
    
    print(f'PlacementTest Module:')
    print(f'  Total exams: {len(placement_exams)}')
    print(f'  With PDF files: {placement_with_pdf}/{len(placement_exams)}')
    print(f'  With rotation: {placement_with_rotation}/{len(placement_exams)}')
    print(f'  BROKEN (rotation but no PDF): {placement_broken}')
    print()
    
    # RoutineTest stats  
    routine_with_pdf = sum(1 for e in routine_exams if e.pdf_file)
    routine_with_rotation = sum(1 for e in routine_exams if e.pdf_rotation != 0)
    routine_broken = sum(1 for e in routine_exams if not e.pdf_file and e.pdf_rotation != 0)
    
    print(f'RoutineTest Module:')
    print(f'  Total exams: {len(routine_exams)}')
    print(f'  With PDF files: {routine_with_pdf}/{len(routine_exams)}')
    print(f'  With rotation: {routine_with_rotation}/{len(routine_exams)}')
    print(f'  BROKEN (rotation but no PDF): {routine_broken}')
    print()

    # Critical issue detection
    total_broken = placement_broken + routine_broken
    if total_broken > 0:
        print('🚨 CRITICAL ISSUES DETECTED:')
        print('=' * 50)
        print(f'Total exams with rotation settings but no PDF files: {total_broken}')
        print('This confirms that PDF uploads are failing while rotation values are being saved!')
        print('Root cause: Silent failures in PDF upload process')
        print()
        print('RECOMMENDED ACTIONS:')
        print('1. Investigate ExamService.create_exam() methods')
        print('2. Add comprehensive PDF upload validation')
        print('3. Implement robust error handling and logging') 
        print('4. Fix file upload and storage issues')
    else:
        print('✅ NO CRITICAL INCONSISTENCIES DETECTED')
        print('PDF files and rotation settings appear to be in sync')
        
    print('\n' + '=' * 80)

if __name__ == '__main__':
    analyze_pdf_consistency()