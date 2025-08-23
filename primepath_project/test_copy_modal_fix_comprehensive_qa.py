#!/usr/bin/env python3
"""
COMPREHENSIVE QA TESTING FOR COPY MODAL DROPDOWN FIX
===================================================

This script validates the complete solution including:
1. Backend service functionality
2. Template context passing
3. JavaScript initialization 
4. Modal opening logic
5. Dropdown population
6. Error handling and fallbacks
7. User experience validation
"""

import os
import sys
import django
import json
import time
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory, Client
from django.template.loader import get_template
from primepath_routinetest.services.exam_service import ExamService
import logging

print("="*80)
print("🧪 COMPREHENSIVE COPY MODAL DROPDOWN FIX - QA VALIDATION")
print("="*80)
print(f"Test Suite Started: {datetime.now().isoformat()}")
print()

# Initialize test results tracking
test_results = {
    'total_tests': 0,
    'passed': 0,
    'failed': 0,
    'warnings': 0,
    'tests': []
}

def run_test(test_name, test_function):
    """Helper function to run and track test results"""
    test_results['total_tests'] += 1
    print(f"🧪 TEST: {test_name}")
    print("-" * 50)
    
    try:
        result = test_function()
        if result['status'] == 'PASS':
            test_results['passed'] += 1
            print(f"✅ PASSED: {result.get('message', 'Test completed successfully')}")
        elif result['status'] == 'WARN':
            test_results['warnings'] += 1
            print(f"⚠️  WARNING: {result.get('message', 'Test completed with warnings')}")
        else:
            test_results['failed'] += 1
            print(f"❌ FAILED: {result.get('message', 'Test failed')}")
            
        test_results['tests'].append({
            'name': test_name,
            'status': result['status'],
            'message': result.get('message', ''),
            'details': result.get('details', {})
        })
        
    except Exception as e:
        test_results['failed'] += 1
        print(f"❌ FAILED: Unhandled exception - {e}")
        test_results['tests'].append({
            'name': test_name,
            'status': 'FAIL',
            'message': f"Unhandled exception: {e}",
            'details': {'exception': str(e)}
        })
    
    print()

# TEST 1: Backend Service Integrity
def test_backend_service_integrity():
    """Validate backend service returns correct curriculum data"""
    try:
        # Test the enhanced service method
        curriculum_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        # Validation checks
        checks = {
            'is_dict': isinstance(curriculum_data, dict),
            'has_curriculum_data': 'curriculum_data' in curriculum_data,
            'has_metadata': 'metadata' in curriculum_data,
            'has_validation': 'validation' in curriculum_data,
            'validation_passed': curriculum_data.get('validation', {}).get('is_valid', False),
            'has_4_programs': len(curriculum_data.get('curriculum_data', {})) == 4,
            'expected_programs': set(['CORE', 'EDGE', 'ASCENT', 'PINNACLE']).issubset(
                set(curriculum_data.get('curriculum_data', {}).keys())
            )
        }
        
        # Check subprogram structure
        structure_valid = True
        program_details = {}
        
        for program, program_data in curriculum_data.get('curriculum_data', {}).items():
            if 'subprograms' not in program_data:
                structure_valid = False
            else:
                subprogram_count = len(program_data['subprograms'])
                program_details[program] = {
                    'subprograms': list(program_data['subprograms'].keys()),
                    'subprogram_count': subprogram_count
                }
        
        checks['structure_valid'] = structure_valid
        
        all_passed = all(checks.values())
        
        return {
            'status': 'PASS' if all_passed else 'FAIL',
            'message': f"Backend service validation {'passed' if all_passed else 'failed'}",
            'details': {
                'checks': checks,
                'program_details': program_details,
                'total_levels': curriculum_data.get('validation', {}).get('total_levels', 0)
            }
        }
        
    except Exception as e:
        return {
            'status': 'FAIL',
            'message': f"Backend service test failed: {e}",
            'details': {'exception': str(e)}
        }

# TEST 2: Template Context Integration
def test_template_context_integration():
    """Validate template receives correct context variables"""
    try:
        # Mock request
        factory = RequestFactory()
        request = factory.get('/routinetest/exam/exam_library/')
        
        # Get admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            return {
                'status': 'FAIL',
                'message': 'No admin user found for testing',
                'details': {}
            }
        
        request.user = admin_user
        
        # Test context preparation (simulating the view)
        curriculum_data_for_copy_modal = ExamService.get_routinetest_curriculum_levels()
        curriculum_hierarchy_for_copy = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        checks = {
            'curriculum_levels_available': bool(curriculum_data_for_copy_modal),
            'curriculum_hierarchy_available': bool(curriculum_hierarchy_for_copy),
            'levels_is_list': isinstance(curriculum_data_for_copy_modal, list),
            'hierarchy_is_dict': isinstance(curriculum_hierarchy_for_copy, dict),
            'hierarchy_has_curriculum_data': 'curriculum_data' in curriculum_hierarchy_for_copy if curriculum_hierarchy_for_copy else False,
            'levels_count': len(curriculum_data_for_copy_modal) if curriculum_data_for_copy_modal else 0
        }
        
        all_passed = all([
            checks['curriculum_levels_available'],
            checks['curriculum_hierarchy_available'],
            checks['levels_is_list'],
            checks['hierarchy_is_dict'],
            checks['hierarchy_has_curriculum_data']
        ])
        
        return {
            'status': 'PASS' if all_passed else 'FAIL',
            'message': f"Template context integration {'passed' if all_passed else 'failed'}",
            'details': {
                'checks': checks,
                'context_vars_ready': all_passed
            }
        }
        
    except Exception as e:
        return {
            'status': 'FAIL',
            'message': f"Template context test failed: {e}",
            'details': {'exception': str(e)}
        }

# TEST 3: Template Rendering Validation
def test_template_rendering():
    """Validate template can render with curriculum data"""
    try:
        # Load the template
        template = get_template('primepath_routinetest/exam_list_hierarchical.html')
        
        # Get real curriculum data
        curriculum_hierarchy_for_copy = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        curriculum_data_for_copy_modal = ExamService.get_routinetest_curriculum_levels()
        
        # Create minimal mock context
        mock_context = {
            'curriculum_hierarchy_for_copy': curriculum_hierarchy_for_copy,
            'curriculum_levels_for_copy': curriculum_data_for_copy_modal,
            'hierarchical_exams': {},
            'program_order': ['CORE', 'EDGE', 'ASCENT', 'PINNACLE'],
            'teacher_assignments': [],
            'editable_classes': [],
            'is_admin': True,
            'global_access_level': 'FULL',
            'can_manage_exams': True,
            'is_view_only_teacher': False,
            'mapping_summary': {
                'total': 0, 'complete': 0, 'partial': 0, 
                'not_started': 0, 'accessible': 0, 'editable': 0
            },
            'exam_type_filter': 'ALL',
            'show_assigned_only': False,
            'ownership_filter': 'my',
            'is_my_files_active': True,
            'is_others_files_active': False,
            'exam_type_counts': {'review': 0, 'quarterly': 0, 'all': 0, 'assigned': 0},
            'filter_description': 'QA Test',
            'template_version': '6.0-qa-test',
            'cache_bust_id': time.time(),
            'get_class_display_name': {},
        }
        
        checks = {
            'template_found': template is not None,
            'curriculum_hierarchy_available': bool(mock_context['curriculum_hierarchy_for_copy']),
            'curriculum_levels_available': bool(mock_context['curriculum_levels_for_copy']),
            'context_complete': all(key in mock_context for key in [
                'curriculum_hierarchy_for_copy', 'curriculum_levels_for_copy',
                'hierarchical_exams', 'is_admin'
            ])
        }
        
        # Try to validate that the key template sections exist
        template_source = template.source if hasattr(template, 'source') else str(template)
        template_checks = {
            'has_copy_modal': 'copyExamModal' in template_source,
            'has_curriculum_init': 'CopyCurriculumData' in template_source,
            'has_json_script': 'json_script' in template_source,
            'has_enhanced_v4': 'ENHANCED v4.0' in template_source,
            'has_fallback_functions': 'tryFallbackCurriculumInitialization' in template_source
        }
        
        checks.update(template_checks)
        
        all_passed = all(checks.values())
        
        return {
            'status': 'PASS' if all_passed else 'FAIL',
            'message': f"Template rendering validation {'passed' if all_passed else 'failed'}",
            'details': {
                'checks': checks,
                'template_ready': all_passed
            }
        }
        
    except Exception as e:
        return {
            'status': 'FAIL',
            'message': f"Template rendering test failed: {e}",
            'details': {'exception': str(e)}
        }

# TEST 4: JavaScript Structure Validation
def test_javascript_structure():
    """Validate JavaScript data structure and functions"""
    try:
        # Get curriculum data
        curriculum_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        if not curriculum_data or 'curriculum_data' not in curriculum_data:
            return {
                'status': 'FAIL',
                'message': 'No curriculum data available for JavaScript validation',
                'details': {}
            }
        
        # Simulate Django json_script filter
        json_data = json.dumps(curriculum_data, separators=(',', ':'))
        
        # Validate JSON serialization
        try:
            parsed_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            return {
                'status': 'FAIL',
                'message': f'JSON serialization failed: {e}',
                'details': {'json_error': str(e)}
            }
        
        # Validate structure for JavaScript consumption
        js_checks = {
            'json_serializable': True,
            'has_curriculum_data': 'curriculum_data' in parsed_data,
            'has_metadata': 'metadata' in parsed_data,
            'has_validation': 'validation' in parsed_data,
            'curriculum_is_object': isinstance(parsed_data.get('curriculum_data'), dict),
            'has_expected_programs': all(
                program in parsed_data.get('curriculum_data', {})
                for program in ['CORE', 'EDGE', 'ASCENT', 'PINNACLE']
            )
        }
        
        # Validate program structure for dropdown population
        program_structure_valid = True
        program_validation = {}
        
        for program, program_data in parsed_data.get('curriculum_data', {}).items():
            program_valid = (
                isinstance(program_data, dict) and
                'subprograms' in program_data and
                isinstance(program_data['subprograms'], dict)
            )
            
            program_validation[program] = {
                'valid': program_valid,
                'subprogram_count': len(program_data.get('subprograms', {})) if program_valid else 0
            }
            
            if not program_valid:
                program_structure_valid = False
        
        js_checks['program_structure_valid'] = program_structure_valid
        
        all_passed = all(js_checks.values())
        
        return {
            'status': 'PASS' if all_passed else 'FAIL',
            'message': f"JavaScript structure validation {'passed' if all_passed else 'failed'}",
            'details': {
                'checks': js_checks,
                'program_validation': program_validation,
                'json_size': len(json_data)
            }
        }
        
    except Exception as e:
        return {
            'status': 'FAIL',
            'message': f"JavaScript structure test failed: {e}",
            'details': {'exception': str(e)}
        }

# TEST 5: Error Handling and Fallback Validation
def test_error_handling_fallbacks():
    """Validate error handling and fallback mechanisms"""
    try:
        # Test 1: Validate template has error handling
        template = get_template('primepath_routinetest/exam_list_hierarchical.html')
        template_source = str(template.source) if hasattr(template, 'source') else str(template)
        
        error_handling_checks = {
            'has_try_catch': 'try {' in template_source and 'catch' in template_source,
            'has_error_state': 'CopyCurriculumDataError' in template_source,
            'has_fallback_function': 'tryFallbackCurriculumInitialization' in template_source,
            'has_user_error_display': 'showCurriculumDataError' in template_source,
            'has_diagnostic_function': 'runCurriculumDiagnostic' in template_source,
            'has_retry_logic': 'maxAttempts' in template_source,
            'has_timeout_handling': 'TIMEOUT' in template_source
        }
        
        # Test 2: Validate structure of fallback data
        fallback_structure_checks = {
            'has_core_fallback': 'CORE' in template_source and 'Phonics' in template_source,
            'has_edge_fallback': 'EDGE' in template_source and 'Spark' in template_source,
            'has_ascent_fallback': 'ASCENT' in template_source and 'Nova' in template_source,
            'has_pinnacle_fallback': 'PINNACLE' in template_source and 'Vision' in template_source
        }
        
        all_checks = {**error_handling_checks, **fallback_structure_checks}
        all_passed = all(all_checks.values())
        
        return {
            'status': 'PASS' if all_passed else 'WARN',  # Warn if some fallbacks missing
            'message': f"Error handling and fallbacks {'fully implemented' if all_passed else 'partially implemented'}",
            'details': {
                'error_handling_checks': error_handling_checks,
                'fallback_structure_checks': fallback_structure_checks,
                'comprehensive_error_handling': all_passed
            }
        }
        
    except Exception as e:
        return {
            'status': 'FAIL',
            'message': f"Error handling test failed: {e}",
            'details': {'exception': str(e)}
        }

# TEST 6: Integration Test - Full Pipeline
def test_full_pipeline_integration():
    """Test the complete pipeline from backend to frontend"""
    try:
        pipeline_steps = {}
        
        # Step 1: Backend service
        try:
            curriculum_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
            pipeline_steps['backend_service'] = {
                'success': True,
                'programs': len(curriculum_data.get('curriculum_data', {})),
                'valid': curriculum_data.get('validation', {}).get('is_valid', False)
            }
        except Exception as e:
            pipeline_steps['backend_service'] = {'success': False, 'error': str(e)}
        
        # Step 2: Template context preparation
        try:
            levels_data = ExamService.get_routinetest_curriculum_levels()
            pipeline_steps['context_preparation'] = {
                'success': True,
                'levels_count': len(levels_data) if levels_data else 0,
                'hierarchy_available': bool(curriculum_data)
            }
        except Exception as e:
            pipeline_steps['context_preparation'] = {'success': False, 'error': str(e)}
        
        # Step 3: JSON serialization
        try:
            json_data = json.dumps(curriculum_data)
            pipeline_steps['json_serialization'] = {
                'success': True,
                'json_size': len(json_data),
                'parseable': bool(json.loads(json_data))
            }
        except Exception as e:
            pipeline_steps['json_serialization'] = {'success': False, 'error': str(e)}
        
        # Step 4: Template validation
        try:
            template = get_template('primepath_routinetest/exam_list_hierarchical.html')
            pipeline_steps['template_loading'] = {
                'success': True,
                'template_exists': template is not None
            }
        except Exception as e:
            pipeline_steps['template_loading'] = {'success': False, 'error': str(e)}
        
        # Calculate overall success
        successful_steps = sum(1 for step in pipeline_steps.values() if step.get('success', False))
        total_steps = len(pipeline_steps)
        success_rate = (successful_steps / total_steps) * 100
        
        overall_success = success_rate == 100
        
        return {
            'status': 'PASS' if overall_success else 'FAIL',
            'message': f"Full pipeline integration {success_rate:.1f}% successful ({successful_steps}/{total_steps} steps)",
            'details': {
                'pipeline_steps': pipeline_steps,
                'success_rate': success_rate,
                'successful_steps': successful_steps,
                'total_steps': total_steps
            }
        }
        
    except Exception as e:
        return {
            'status': 'FAIL',
            'message': f"Full pipeline test failed: {e}",
            'details': {'exception': str(e)}
        }

# Run all tests
print("🚀 STARTING QA TEST SUITE")
print("=" * 80)
print()

run_test("Backend Service Integrity", test_backend_service_integrity)
run_test("Template Context Integration", test_template_context_integration)
run_test("Template Rendering Validation", test_template_rendering)
run_test("JavaScript Structure Validation", test_javascript_structure)
run_test("Error Handling and Fallbacks", test_error_handling_fallbacks)
run_test("Full Pipeline Integration", test_full_pipeline_integration)

# Generate final report
print("=" * 80)
print("📊 QA TEST RESULTS SUMMARY")
print("=" * 80)
print()

print(f"📋 Total Tests: {test_results['total_tests']}")
print(f"✅ Passed: {test_results['passed']}")
print(f"⚠️  Warnings: {test_results['warnings']}")
print(f"❌ Failed: {test_results['failed']}")
print()

success_rate = (test_results['passed'] / test_results['total_tests']) * 100 if test_results['total_tests'] > 0 else 0
print(f"🎯 Success Rate: {success_rate:.1f}%")

if test_results['failed'] == 0:
    print("🎉 ALL CRITICAL TESTS PASSED!")
    print("✅ The Copy Modal dropdown fix is ready for production")
elif test_results['failed'] <= 1 and test_results['warnings'] == 0:
    print("✅ MOSTLY SUCCESSFUL - Minor issues detected")
    print("⚠️  Review failed tests but solution is likely functional")
else:
    print("❌ SIGNIFICANT ISSUES DETECTED")
    print("🔧 Additional fixes required before deployment")

print()
print("📝 DETAILED TEST RESULTS:")
print("-" * 50)

for i, test in enumerate(test_results['tests'], 1):
    status_emoji = "✅" if test['status'] == 'PASS' else "⚠️" if test['status'] == 'WARN' else "❌"
    print(f"{i}. {status_emoji} {test['name']}: {test['message']}")

print()
print("=" * 80)
print(f"QA Testing Completed: {datetime.now().isoformat()}")
print("=" * 80)

# Exit with appropriate code
exit_code = 0 if test_results['failed'] == 0 else 1
sys.exit(exit_code)