#!/usr/bin/env python3
"""
COMPREHENSIVE TEMPLATE ANALYSIS FOR COPY MODAL
==============================================

This script analyzes the template rendering, JavaScript integration,
and all components of the Copy Modal dropdown fix.
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
from django.template.loader import get_template
from primepath_routinetest.services.exam_service import ExamService

print("="*100)
print("🔍 COMPREHENSIVE TEMPLATE ANALYSIS: COPY MODAL DROPDOWN")
print("="*100)
print(f"Started: {datetime.now().isoformat()}")
print()

def test_correct_url_and_template():
    """Test the correct URL and template rendering"""
    print("="*50)
    print("PHASE 2A: URL AND TEMPLATE VALIDATION")
    print("="*50)
    
    client = Client()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        print("❌ No admin user found - cannot proceed")
        return False
    
    client.force_login(admin_user)
    print(f"✅ Logged in as: {admin_user.username}")
    
    # Test the correct URL pattern
    correct_url = '/RoutineTest/exams/'
    print(f"🧪 Testing correct URL: {correct_url}")
    
    response = client.get(correct_url)
    print(f"📊 Response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Correct URL responds successfully!")
        
        # Check template context
        context = response.context
        print(f"📊 Template context keys: {list(context.keys())[:10]}...")  # First 10 keys
        
        # Check for curriculum data
        curriculum_checks = {
            'curriculum_hierarchy_for_copy': 'curriculum_hierarchy_for_copy' in context,
            'curriculum_levels_for_copy': 'curriculum_levels_for_copy' in context,
            'has_hierarchical_exams': 'hierarchical_exams' in context,
            'is_admin': context.get('is_admin', False),
            'can_manage_exams': context.get('can_manage_exams', False)
        }
        
        print("📊 Context curriculum data:")
        for key, value in curriculum_checks.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")
        
        # Deep analysis of curriculum data
        if curriculum_checks['curriculum_hierarchy_for_copy']:
            hierarchy_data = context['curriculum_hierarchy_for_copy']
            if isinstance(hierarchy_data, dict) and 'curriculum_data' in hierarchy_data:
                programs = hierarchy_data['curriculum_data'].keys()
                print(f"✅ Curriculum programs in context: {list(programs)}")
                print(f"✅ Total programs: {len(programs)}")
                
                expected_programs = ['CORE', 'EDGE', 'ASCENT', 'PINNACLE']
                missing_programs = [p for p in expected_programs if p not in programs]
                extra_programs = [p for p in programs if p not in expected_programs and not p.startswith('TEST')]
                
                if not missing_programs:
                    print("✅ All expected programs present")
                else:
                    print(f"❌ Missing programs: {missing_programs}")
                    
                if not extra_programs:
                    print("✅ No unexpected programs")
                else:
                    print(f"⚠️  Extra programs: {extra_programs}")
            else:
                print("❌ Invalid hierarchy data structure")
        
        return response.content.decode('utf-8')
    else:
        print(f"❌ URL failed with status {response.status_code}")
        return None

def analyze_template_content(content):
    """Analyze the rendered template content"""
    print("="*50)
    print("PHASE 2B: TEMPLATE CONTENT ANALYSIS")
    print("="*50)
    
    if not content:
        print("❌ No content to analyze")
        return {}
    
    print(f"📊 Template content length: {len(content)} characters")
    
    # Check for Copy Modal elements
    modal_elements = {
        'copy_modal_div': 'copyExamModal' in content,
        'copy_button': 'Copy Exam' in content,
        'program_dropdown': 'copyProgramSelect' in content,
        'subprogram_dropdown': 'copySubprogramSelect' in content,
        'level_dropdown': 'copyLevelSelect' in content,
        'modal_form': 'copyExamForm' in content,
        'modal_close': 'closeCopyModal' in content
    }
    
    print("📊 Copy Modal HTML Elements:")
    for element, present in modal_elements.items():
        status = "✅" if present else "❌"
        print(f"  {status} {element}: {present}")
    
    # Check for JavaScript curriculum initialization
    js_elements = {
        'curriculum_data_vars': 'CopyCurriculumData' in content,
        'enhanced_v4_logic': 'ENHANCED v4.0' in content,
        'json_script_element': 'copy-curriculum-hierarchy-data' in content,
        'population_function': 'populateCopyProgramDropdown' in content,
        'fallback_function': 'tryFallbackCurriculumInitialization' in content,
        'error_handling': 'CopyCurriculumDataError' in content,
        'diagnostic_function': 'runCurriculumDiagnostic' in content,
        'modal_opening_logic': 'initializeCurriculumDropdown' in content
    }
    
    print("📊 JavaScript Integration:")
    for element, present in js_elements.items():
        status = "✅" if present else "❌"
        print(f"  {status} {element}: {present}")
    
    # Check for curriculum program references
    program_references = {
        'core_phonics': 'CORE' in content and 'Phonics' in content,
        'edge_spark': 'EDGE' in content and 'Spark' in content,
        'ascent_nova': 'ASCENT' in content and 'Nova' in content,
        'pinnacle_vision': 'PINNACLE' in content and 'Vision' in content
    }
    
    print("📊 Curriculum Program References:")
    for program, present in program_references.items():
        status = "✅" if present else "❌"
        print(f"  {status} {program}: {present}")
    
    # Check for debugging features
    debug_features = {
        'console_logging': 'console.log' in content,
        'console_grouping': 'console.group' in content,
        'error_logging': 'console.error' in content,
        'debug_modal_function': 'debugCopyModal' in content,
        'comprehensive_logging': 'CURRICULUM_INIT' in content
    }
    
    print("📊 Debugging Features:")
    for feature, present in debug_features.items():
        status = "✅" if present else "❌"
        print(f"  {status} {feature}: {present}")
    
    return {
        'modal_elements': modal_elements,
        'js_elements': js_elements,
        'program_references': program_references,
        'debug_features': debug_features,
        'content_length': len(content)
    }

def validate_json_script_integration():
    """Validate Django json_script integration"""
    print("="*50)
    print("PHASE 2C: JSON SCRIPT INTEGRATION")
    print("="*50)
    
    # Get curriculum data from service
    curriculum_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
    
    if not curriculum_data:
        print("❌ No curriculum data from service")
        return False
    
    print("✅ Got curriculum data from service")
    print(f"📊 Service data keys: {list(curriculum_data.keys())}")
    
    # Test JSON serialization (simulating Django's json_script filter)
    try:
        json_string = json.dumps(curriculum_data, separators=(',', ':'))
        print(f"✅ JSON serialization successful ({len(json_string)} chars)")
        
        # Test parsing
        parsed_data = json.loads(json_string)
        print("✅ JSON parsing successful")
        
        # Validate structure for JavaScript
        if 'curriculum_data' in parsed_data:
            js_curriculum = parsed_data['curriculum_data']
            print(f"✅ curriculum_data extracted: {len(js_curriculum)} programs")
            
            # Test dropdown population structure
            dropdown_ready = True
            for program, program_data in js_curriculum.items():
                if not isinstance(program_data, dict):
                    dropdown_ready = False
                    print(f"❌ {program}: not a dict")
                elif 'subprograms' not in program_data:
                    dropdown_ready = False
                    print(f"❌ {program}: missing subprograms")
                elif not isinstance(program_data['subprograms'], dict):
                    dropdown_ready = False
                    print(f"❌ {program}: subprograms not a dict")
                else:
                    subprogram_count = len(program_data['subprograms'])
                    print(f"✅ {program}: {subprogram_count} subprograms")
            
            if dropdown_ready:
                print("✅ JSON structure ready for dropdown population")
            else:
                print("❌ JSON structure has issues")
                
            return dropdown_ready
        else:
            print("❌ Missing curriculum_data in JSON")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON serialization failed: {e}")
        return False

def test_template_inheritance():
    """Test template inheritance and base template"""
    print("="*50)
    print("PHASE 2D: TEMPLATE INHERITANCE")
    print("="*50)
    
    try:
        template = get_template('primepath_routinetest/exam_list_hierarchical.html')
        print("✅ Template found successfully")
        
        # Check if template has source
        if hasattr(template, 'source'):
            source_content = template.source
        else:
            # Try to read the file directly
            template_path = template.origin.name
            with open(template_path, 'r', encoding='utf-8') as f:
                source_content = f.read()
        
        print(f"📊 Template source length: {len(source_content)} characters")
        
        # Check template structure
        template_structure = {
            'extends_base': '{% extends' in source_content,
            'has_blocks': '{% block' in source_content,
            'has_static': '{% load static' in source_content,
            'has_copy_modal': 'copyExamModal' in source_content,
            'has_curriculum_logic': 'curriculum_hierarchy_for_copy' in source_content
        }
        
        print("📊 Template Structure:")
        for element, present in template_structure.items():
            status = "✅" if present else "❌"
            print(f"  {status} {element}: {present}")
        
        # Count key elements
        copy_modal_count = source_content.count('copyExamModal')
        curriculum_refs = source_content.count('CopyCurriculumData')
        console_logs = source_content.count('console.log')
        
        print(f"📊 Element counts:")
        print(f"  copyExamModal references: {copy_modal_count}")
        print(f"  CopyCurriculumData references: {curriculum_refs}")
        print(f"  console.log statements: {console_logs}")
        
        return template_structure
        
    except Exception as e:
        print(f"❌ Template analysis failed: {e}")
        return {}

# Run all Phase 2 tests
print("🚀 Starting Phase 2: Complete Template Analysis")
print()

# Test 2A: URL and template
content = test_correct_url_and_template()

# Test 2B: Template content
if content:
    content_analysis = analyze_template_content(content)
else:
    content_analysis = {}

# Test 2C: JSON script integration
json_ready = validate_json_script_integration()

# Test 2D: Template inheritance
template_structure = test_template_inheritance()

# Generate Phase 2 Summary
print()
print("="*100)
print("📊 PHASE 2 RESULTS SUMMARY")
print("="*100)

# Calculate success rates
url_success = bool(content)
content_success = bool(content_analysis)
json_success = bool(json_ready)
template_success = bool(template_structure)

phase2_tests = [url_success, content_success, json_success, template_success]
phase2_success_rate = (sum(phase2_tests) / len(phase2_tests)) * 100

print(f"✅ URL and Context: {'PASS' if url_success else 'FAIL'}")
print(f"✅ Content Analysis: {'PASS' if content_success else 'FAIL'}")
print(f"✅ JSON Integration: {'PASS' if json_success else 'FAIL'}")
print(f"✅ Template Structure: {'PASS' if template_success else 'FAIL'}")

print(f"\n🎯 Phase 2 Success Rate: {phase2_success_rate:.1f}%")

if phase2_success_rate >= 90:
    print("🎉 Phase 2: EXCELLENT - Template system fully functional")
elif phase2_success_rate >= 75:
    print("✅ Phase 2: GOOD - Template system mostly working")
elif phase2_success_rate >= 50:
    print("⚠️  Phase 2: NEEDS IMPROVEMENT - Template system partially working")
else:
    print("❌ Phase 2: CRITICAL ISSUES - Template system has major problems")

# Export detailed results
results = {
    'timestamp': datetime.now().isoformat(),
    'url_success': url_success,
    'content_analysis': content_analysis,
    'json_integration_success': json_ready,
    'template_structure': template_structure,
    'phase2_success_rate': phase2_success_rate
}

with open('phase2_template_analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n📄 Detailed results saved to: phase2_template_analysis_results.json")
print(f"Completed: {datetime.now().isoformat()}")
print("="*100)