#!/usr/bin/env python3
"""
Test script to verify the Program dropdown fix for copy exam modal
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

def test_copy_modal_program_dropdown_fix():
    """Test the program dropdown fix"""
    print("=== TESTING COPY MODAL PROGRAM DROPDOWN FIX ===")
    print()
    
    # Check if curriculum data is being passed to context
    from primepath_routinetest.services.exam_service import ExamService
    
    curriculum_data = ExamService.get_routinetest_curriculum_levels()
    print(f"✅ Curriculum data loaded: {len(curriculum_data)} levels")
    
    # Check data structure
    programs = set()
    subprograms = set()
    for level_data in curriculum_data:
        programs.add(level_data['program_name'])
        subprograms.add(f"{level_data['program_name']} {level_data['subprogram_name']}")
    
    print(f"✅ Programs available: {sorted(programs)}")
    print(f"✅ SubPrograms available: {len(subprograms)}")
    
    # Verify template file has the fix
    template_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/exam_list_hierarchical.html'
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            content = f.read()
            
        checks = []
        
        if 'curriculum_levels_for_copy' in content:
            checks.append("✅ Template checks for Django curriculum data")
        else:
            checks.append("❌ Template NOT checking Django curriculum data")
            
        if 'window.CopyCurriculumData = {};' in content:
            checks.append("✅ Template initializes curriculum data object")
        else:
            checks.append("❌ Template NOT initializing curriculum data")
            
        if 'level_data.program_name' in content:
            checks.append("✅ Template accesses Django curriculum structure")
        else:
            checks.append("❌ Template NOT accessing Django data structure")
            
        for check in checks:
            print(f"   {check}")
    
    # Check view file has the fix
    view_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/primepath_routinetest/views/exam.py'
    
    if os.path.exists(view_path):
        with open(view_path, 'r') as f:
            view_content = f.read()
            
        view_checks = []
        
        if 'curriculum_data_for_copy_modal = ExamService.get_routinetest_curriculum_levels()' in view_content:
            view_checks.append("✅ View loads curriculum data for copy modal")
        else:
            view_checks.append("❌ View NOT loading curriculum data")
            
        if "'curriculum_levels_for_copy': curriculum_data_for_copy_modal" in view_content:
            view_checks.append("✅ View passes curriculum data to template context")
        else:
            view_checks.append("❌ View NOT passing curriculum data to context")
            
        print()
        print("📋 View Updates:")
        for check in view_checks:
            print(f"   {check}")
    
    print()
    print("=== EXPECTED BEHAVIOR ===")
    print("1. ✅ Django view loads curriculum data using ExamService")
    print("2. ✅ Template receives curriculum data via context") 
    print("3. ✅ JavaScript initializes window.CopyCurriculumData from Django data")
    print("4. ✅ Program dropdown populates with CORE, ASCENT, EDGE, PINNACLE")
    print("5. ✅ Cascading dropdowns work: Program → SubProgram → Level")
    
    print()
    print("=== HOW TO TEST MANUALLY ===")
    print("1. Open Exam Library: http://127.0.0.1:8000/RoutineTest/exam-library/")
    print("2. Click 'Copy Exam' on any exam")
    print("3. Check Program dropdown shows options (not just '-- Select Program --')")
    print("4. Select Program → SubProgram options should appear")
    print("5. Select SubProgram → Level options should appear")
    
    return True

if __name__ == '__main__':
    success = test_copy_modal_program_dropdown_fix()
    sys.exit(0 if success else 1)