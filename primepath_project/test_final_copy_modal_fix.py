#!/usr/bin/env python3
"""
Final comprehensive test for copy modal Program dropdown fix
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

def test_final_copy_modal_fix():
    """Final test to verify all fixes are in place"""
    print("=== FINAL COPY MODAL PROGRAM DROPDOWN FIX TEST ===")
    print()
    
    # 1. Check view passes curriculum data
    view_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/primepath_routinetest/views/exam.py'
    with open(view_path, 'r') as f:
        view_content = f.read()
    
    view_checks = []
    if 'curriculum_data_for_copy_modal = ExamService.get_routinetest_curriculum_levels()' in view_content:
        view_checks.append("✅ View loads curriculum data")
    else:
        view_checks.append("❌ View NOT loading curriculum data")
        
    if "'curriculum_levels_for_copy': curriculum_data_for_copy_modal" in view_content:
        view_checks.append("✅ View passes data to template")
    else:
        view_checks.append("❌ View NOT passing data to template")
    
    # 2. Check template initializes curriculum data  
    template_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/exam_list_hierarchical.html'
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    template_checks = []
    if 'window.CopyCurriculumData = {};' in template_content:
        template_checks.append("✅ Template initializes curriculum object")
    else:
        template_checks.append("❌ Template NOT initializing curriculum")
        
    if 'window.CopyCurriculumDataReady = true;' in template_content:
        template_checks.append("✅ Template sets ready flag")
    else:
        template_checks.append("❌ Template NOT setting ready flag")
        
    if 'populateCopyProgramDropdown()' in template_content:
        template_checks.append("✅ Template calls populate function")
    else:
        template_checks.append("❌ Template NOT calling populate function")
    
    # 3. Check JavaScript module calls populate on modal open
    js_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/static/js/routinetest/copy-exam-modal.js'
    with open(js_path, 'r') as f:
        js_content = f.read()
        
    js_checks = []
    if 'window.populateCopyProgramDropdown()' in js_content:
        js_checks.append("✅ JS module calls populate on modal open")
    else:
        js_checks.append("❌ JS module NOT calling populate")
        
    if 'Curriculum dropdown populated on modal open' in js_content:
        js_checks.append("✅ JS module has success logging")
    else:
        js_checks.append("❌ JS module missing success logging")
    
    # 4. Test curriculum data availability
    from primepath_routinetest.services.exam_service import ExamService
    curriculum_data = ExamService.get_routinetest_curriculum_levels()
    
    curriculum_checks = []
    if len(curriculum_data) > 0:
        curriculum_checks.append(f"✅ Curriculum data available: {len(curriculum_data)} levels")
    else:
        curriculum_checks.append("❌ No curriculum data available")
        
    programs = set(level['program_name'] for level in curriculum_data)
    if len(programs) == 4 and all(p in programs for p in ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']):
        curriculum_checks.append("✅ All 4 programs available")
    else:
        curriculum_checks.append(f"❌ Expected 4 programs, got {len(programs)}: {programs}")
    
    # Print results
    print("📋 VIEW LAYER:")
    for check in view_checks:
        print(f"   {check}")
        
    print("\n📋 TEMPLATE LAYER:")
    for check in template_checks:
        print(f"   {check}")
        
    print("\n📋 JAVASCRIPT LAYER:")
    for check in js_checks:
        print(f"   {check}")
        
    print("\n📋 DATA LAYER:")
    for check in curriculum_checks:
        print(f"   {check}")
    
    # Overall assessment
    all_checks = view_checks + template_checks + js_checks + curriculum_checks
    success_count = len([c for c in all_checks if c.startswith("✅")])
    total_checks = len(all_checks)
    
    print(f"\n🎯 OVERALL RESULT: {success_count}/{total_checks} checks passed ({(success_count/total_checks)*100:.0f}%)")
    
    if success_count == total_checks:
        print("\n✅ ALL FIXES IN PLACE - Program dropdown should now work!")
        print("\n📝 TESTING STEPS:")
        print("1. Open browser to: http://127.0.0.1:8000/RoutineTest/exams/")
        print("2. Click 'Copy Exam' on any exam")
        print("3. Check that Program dropdown shows: CORE, ASCENT, EDGE, PINNACLE")
        print("4. Select a program to verify cascading works")
        print("5. Check browser console for debugging messages")
        return True
    else:
        print(f"\n❌ {total_checks - success_count} issues need to be resolved")
        return False

if __name__ == '__main__':
    success = test_final_copy_modal_fix()
    sys.exit(0 if success else 1)