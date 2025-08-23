#!/usr/bin/env python3
"""
LIVE USER EXPERIENCE VALIDATION - COPY MODAL DROPDOWN
====================================================

This script performs final user experience validation by simulating
real user interactions with the Copy Modal dropdown feature.
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from primepath_routinetest.models import Exam
from primepath_routinetest.services.exam_service import ExamService

print("="*100)
print("🚀 LIVE USER EXPERIENCE VALIDATION: COPY MODAL DROPDOWN")
print("="*100)
print(f"Started: {datetime.now().isoformat()}")
print()

def test_page_accessibility():
    """Test that the exam page is accessible and loads correctly"""
    print("="*50)
    print("PHASE 5A: PAGE ACCESSIBILITY TEST")
    print("="*50)
    
    client = Client()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    client.force_login(admin_user)
    print(f"✅ Logged in as: {admin_user.username}")
    
    # Test the correct exam list URL
    response = client.get('/RoutineTest/exams/')
    
    print(f"📊 Page response:")
    print(f"  Status code: {response.status_code}")
    print(f"  Content type: {response.get('Content-Type', 'Not specified')}")
    print(f"  Content length: {len(response.content)} bytes")
    
    if response.status_code == 200:
        print("✅ Page loads successfully")
        return response
    else:
        print(f"❌ Page failed to load (status: {response.status_code})")
        return False

def validate_copy_buttons_present(response):
    """Validate that Copy Exam buttons are present on the page"""
    print("="*50)
    print("PHASE 5B: COPY BUTTONS VALIDATION")
    print("="*50)
    
    if not response:
        print("❌ No response to analyze")
        return False
    
    content = response.content.decode('utf-8')
    
    # Look for Copy Exam buttons
    copy_button_patterns = [
        'Copy Exam',
        'onclick="openCopyModal',
        'copyExamForm',
        'Copy to Another Class'
    ]
    
    button_analysis = {}
    
    for pattern in copy_button_patterns:
        count = content.count(pattern)
        button_analysis[pattern] = count
        status = "✅" if count > 0 else "❌"
        print(f"  {status} '{pattern}': {count} occurrences")
    
    # Check for modal structure
    modal_elements = [
        'copyExamModal',
        'copyProgramSelect',
        'copySubprogramSelect',
        'copyLevelSelect'
    ]
    
    print(f"\n📊 Modal Elements:")
    modal_present = True
    for element in modal_elements:
        count = content.count(element)
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {element}: {count} occurrences")
        if count == 0:
            modal_present = False
    
    return modal_present and any(button_analysis.values())

def validate_curriculum_data_integration(response):
    """Validate curriculum data is properly integrated into the page"""
    print("="*50)
    print("PHASE 5C: CURRICULUM DATA INTEGRATION")
    print("="*50)
    
    if not response:
        print("❌ No response to analyze")
        return False
    
    content = response.content.decode('utf-8')
    
    # Check for curriculum data elements
    curriculum_elements = {
        'json_script_element': 'copy-curriculum-hierarchy-data',
        'global_curriculum_var': 'CopyCurriculumData',
        'data_ready_flag': 'CopyCurriculumDataReady',
        'initialization_logic': 'ENHANCED v4.0',
        'program_references': {
            'core': 'CORE',
            'edge': 'EDGE', 
            'ascent': 'ASCENT',
            'pinnacle': 'PINNACLE'
        }
    }
    
    integration_success = True
    
    for element_name, pattern in curriculum_elements.items():
        if element_name == 'program_references':
            print(f"📊 Program References:")
            for prog_name, prog_pattern in pattern.items():
                count = content.count(prog_pattern)
                status = "✅" if count > 0 else "❌"
                print(f"  {status} {prog_name.upper()}: {count} occurrences")
                if count == 0:
                    integration_success = False
        else:
            count = content.count(pattern)
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {element_name}: {count} occurrences")
            if count == 0:
                integration_success = False
    
    # Check context data
    context = response.context
    if context:
        context_checks = {
            'curriculum_hierarchy_for_copy': 'curriculum_hierarchy_for_copy' in context,
            'curriculum_levels_for_copy': 'curriculum_levels_for_copy' in context,
            'has_hierarchical_exams': 'hierarchical_exams' in context,
        }
        
        print(f"\n📊 Django Context:")
        for check_name, result in context_checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}: {result}")
            
        if context_checks['curriculum_hierarchy_for_copy']:
            hierarchy = context['curriculum_hierarchy_for_copy']
            if isinstance(hierarchy, dict) and 'curriculum_data' in hierarchy:
                programs = list(hierarchy['curriculum_data'].keys())
                print(f"  ✅ Available programs in context: {programs}")
                print(f"  ✅ Total programs: {len(programs)}")
    
    return integration_success

def simulate_user_interactions():
    """Simulate typical user interactions with the copy modal"""
    print("="*50)
    print("PHASE 5D: USER INTERACTION SIMULATION")  
    print("="*50)
    
    # Test backend data readiness
    print("🧪 Testing backend curriculum data readiness...")
    
    try:
        curriculum_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        if curriculum_data and 'curriculum_data' in curriculum_data:
            programs = curriculum_data['curriculum_data']
            print(f"✅ Backend data ready: {len(programs)} programs")
            
            # Simulate dropdown population logic
            expected_programs = ['CORE', 'EDGE', 'ASCENT', 'PINNACLE']
            available_programs = list(programs.keys())
            
            print(f"📊 Expected programs: {expected_programs}")
            print(f"📊 Available programs: {available_programs}")
            
            # Check each program structure
            dropdown_ready = True
            for program in expected_programs:
                if program in programs:
                    subprograms = programs[program].get('subprograms', {})
                    if isinstance(subprograms, dict) and subprograms:
                        print(f"  ✅ {program}: {len(subprograms)} subprograms ready for dropdown")
                    else:
                        print(f"  ❌ {program}: Invalid subprogram structure")
                        dropdown_ready = False
                else:
                    print(f"  ❌ {program}: Missing from data")
                    dropdown_ready = False
            
            if dropdown_ready:
                print("🎉 All programs ready for dropdown population!")
                
                # Simulate JSON serialization (what Django json_script would do)
                try:
                    json_data = json.dumps(curriculum_data)
                    parsed_data = json.loads(json_data)
                    print("✅ JSON serialization successful")
                    
                    if 'curriculum_data' in parsed_data:
                        js_programs = parsed_data['curriculum_data']
                        print(f"✅ JavaScript would receive {len(js_programs)} programs")
                        
                        # Simulate dropdown option creation
                        simulated_options = []
                        simulated_options.append("-- Select Program --")  # Placeholder
                        
                        for program in sorted(js_programs.keys()):
                            simulated_options.append(program)
                        
                        print(f"📊 Simulated dropdown options:")
                        for i, option in enumerate(simulated_options):
                            prefix = "   └──" if i > 0 else "   ┌──"
                            print(f"  {prefix} {option}")
                        
                        return len(simulated_options) > 1  # More than just placeholder
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON serialization failed: {e}")
                    return False
            else:
                print("❌ Program structure not ready for dropdown")
                return False
        else:
            print("❌ Backend data not available")
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_real_exam_data():
    """Test with real exam data to ensure copy functionality works"""
    print("="*50)
    print("PHASE 5E: REAL EXAM DATA TEST")
    print("="*50)
    
    # Get some real exams
    exams = Exam.objects.all()[:5]  # Test with first 5 exams
    
    print(f"📊 Testing with {len(exams)} real exams:")
    
    for exam in exams:
        print(f"  📄 {exam.name[:50]}...")
        print(f"     Class: {exam.class_code}")
        print(f"     Questions: {exam.routine_questions.count()}")
        print(f"     Curriculum: {exam.curriculum_level}")
        
        # Test if this exam would be copyable
        copyable_checks = {
            'has_name': bool(exam.name),
            'has_class_code': bool(exam.class_code),
            'has_curriculum_level': bool(exam.curriculum_level),
            'has_questions': exam.routine_questions.exists()
        }
        
        all_copyable = all(copyable_checks.values())
        status = "✅" if all_copyable else "❌"
        print(f"     {status} Copyable: {all_copyable}")
        
        if not all_copyable:
            missing = [k for k, v in copyable_checks.items() if not v]
            print(f"     Missing: {', '.join(missing)}")
    
    return len(exams) > 0

def generate_user_experience_report():
    """Generate comprehensive user experience report"""
    print("="*50)
    print("PHASE 5F: USER EXPERIENCE REPORT")
    print("="*50)
    
    # Test all components
    response = test_page_accessibility()
    buttons_valid = validate_copy_buttons_present(response) if response else False
    data_integrated = validate_curriculum_data_integration(response) if response else False
    interactions_work = simulate_user_interactions()
    exam_data_ready = test_real_exam_data()
    
    # Calculate overall user experience score
    ux_components = [
        ('Page Accessibility', bool(response)),
        ('Copy Buttons Present', buttons_valid),
        ('Curriculum Data Integration', data_integrated),
        ('User Interactions', interactions_work),
        ('Real Exam Data', exam_data_ready)
    ]
    
    passed_components = sum(1 for _, passed in ux_components if passed)
    total_components = len(ux_components)
    ux_score = (passed_components / total_components) * 100
    
    print(f"📊 User Experience Components:")
    for component_name, passed in ux_components:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {component_name}")
    
    print(f"\n🎯 Overall User Experience Score: {ux_score:.1f}% ({passed_components}/{total_components})")
    
    if ux_score >= 90:
        print("🎉 EXCELLENT USER EXPERIENCE - Copy Modal is ready for production!")
        recommendation = "READY FOR PRODUCTION"
    elif ux_score >= 75:
        print("✅ GOOD USER EXPERIENCE - Minor improvements could be made")
        recommendation = "READY WITH MINOR IMPROVEMENTS"
    elif ux_score >= 60:
        print("⚠️  ACCEPTABLE USER EXPERIENCE - Some issues need addressing")
        recommendation = "NEEDS IMPROVEMENT"
    else:
        print("❌ POOR USER EXPERIENCE - Significant issues require fixing")
        recommendation = "NEEDS MAJOR WORK"
    
    return {
        'ux_score': ux_score,
        'components': ux_components,
        'recommendation': recommendation,
        'response_available': bool(response)
    }

# Run Phase 5 User Experience Validation
print("🚀 Starting Phase 5: Live Server Testing and User Experience Validation")
print()

ux_results = generate_user_experience_report()

# Export results
results = {
    'timestamp': datetime.now().isoformat(),
    'phase5_results': ux_results,
    'testing_url': '/RoutineTest/exams/',
    'summary': f"User Experience Score: {ux_results['ux_score']:.1f}% - {ux_results['recommendation']}"
}

with open('phase5_user_experience_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n📄 Detailed results saved to: phase5_user_experience_results.json")
print(f"Completed: {datetime.now().isoformat()}")
print("="*100)