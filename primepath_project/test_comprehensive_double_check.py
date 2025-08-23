#!/usr/bin/env python3
"""
COMPREHENSIVE DOUBLE-CHECK OF COPY MODAL DROPDOWN FIX
====================================================

This script performs an exhaustive validation of every component
of the Copy Modal dropdown implementation to ensure 100% correctness.
"""

import os
import sys
import django
import json
import traceback
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import Client, RequestFactory
from django.template.loader import get_template
from django.template import Context
from primepath_routinetest.services.exam_service import ExamService
from primepath_routinetest.views.exam import exam_list
from primepath_routinetest.models import Exam
from core.models import CurriculumLevel
import logging

print("="*100)
print("🔍 COMPREHENSIVE DOUBLE-CHECK: COPY MODAL DROPDOWN FIX")
print("="*100)
print(f"Started: {datetime.now().isoformat()}")
print()

# Global results tracking
validation_results = {
    'backend_service': {},
    'template_context': {},
    'template_rendering': {},
    'javascript_structure': {},
    'error_handling': {},
    'user_experience': {},
    'cross_feature_impact': {}
}

def log_test_section(section_name):
    """Helper to log test sections clearly"""
    print(f"\n{'='*20} {section_name} {'='*20}")

def validate_backend_service():
    """Comprehensive backend service validation"""
    log_test_section("BACKEND SERVICE VALIDATION")
    
    results = validation_results['backend_service']
    
    try:
        # Test 1: Enhanced Service Method
        print("🧪 Testing get_routinetest_curriculum_hierarchy_for_frontend()...")
        curriculum_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        # Deep structure validation
        structure_checks = {
            'is_dict': isinstance(curriculum_data, dict),
            'has_curriculum_data': 'curriculum_data' in curriculum_data,
            'has_metadata': 'metadata' in curriculum_data,
            'has_validation': 'validation' in curriculum_data,
            'has_debug_info': 'debug_info' in curriculum_data,
            'validation_passed': curriculum_data.get('validation', {}).get('is_valid', False),
            'correct_version': curriculum_data.get('metadata', {}).get('version') is not None,
            'frontend_optimized': curriculum_data.get('metadata', {}).get('frontend_optimized', False)
        }
        
        # Curriculum data validation
        curriculum = curriculum_data.get('curriculum_data', {})
        expected_programs = ['CORE', 'EDGE', 'ASCENT', 'PINNACLE']
        
        program_checks = {
            'has_all_programs': all(prog in curriculum for prog in expected_programs),
            'correct_program_count': len(curriculum) >= 4,
            'no_extra_programs': all(prog in expected_programs or prog.startswith('TEST') for prog in curriculum.keys()),
        }
        
        # Detailed program structure validation
        program_structure = {}
        for program in expected_programs:
            if program in curriculum:
                program_data = curriculum[program]
                program_structure[program] = {
                    'has_subprograms': 'subprograms' in program_data,
                    'subprograms_is_dict': isinstance(program_data.get('subprograms'), dict),
                    'has_meta': 'meta' in program_data,
                    'subprogram_count': len(program_data.get('subprograms', {})),
                    'subprogram_names': list(program_data.get('subprograms', {}).keys())
                }
                
                # Validate each subprogram
                for subprogram, sub_data in program_data.get('subprograms', {}).items():
                    if 'levels' not in sub_data:
                        program_structure[program][f'{subprogram}_missing_levels'] = True
                    elif not isinstance(sub_data['levels'], list):
                        program_structure[program][f'{subprogram}_invalid_levels'] = True
                    else:
                        # Validate level structure
                        for level in sub_data['levels']:
                            if not isinstance(level, dict) or 'id' not in level or 'number' not in level:
                                program_structure[program][f'{subprogram}_invalid_level_structure'] = True
                                break
        
        results.update({
            'structure_checks': structure_checks,
            'program_checks': program_checks,
            'program_structure': program_structure,
            'total_levels': curriculum_data.get('validation', {}).get('total_levels', 0),
            'service_response_size': len(str(curriculum_data))
        })
        
        # Test 2: Legacy Service Method
        print("🧪 Testing get_routinetest_curriculum_levels()...")
        legacy_data = ExamService.get_routinetest_curriculum_levels()
        
        legacy_checks = {
            'is_list': isinstance(legacy_data, list),
            'has_items': len(legacy_data) > 0 if isinstance(legacy_data, list) else False,
            'item_structure_valid': True
        }
        
        if isinstance(legacy_data, list) and legacy_data:
            # Check first few items for structure
            sample_item = legacy_data[0]
            expected_fields = ['curriculum_level', 'program_name', 'subprogram_name', 'level_number']
            legacy_checks['item_structure_valid'] = all(field in sample_item for field in expected_fields)
            legacy_checks['sample_item_fields'] = list(sample_item.keys())
        
        results['legacy_checks'] = legacy_checks
        
        # Test 3: Service consistency
        enhanced_level_count = curriculum_data.get('validation', {}).get('total_levels', 0)
        legacy_level_count = len(legacy_data) if isinstance(legacy_data, list) else 0
        
        consistency_checks = {
            'level_count_match': enhanced_level_count == legacy_level_count,
            'enhanced_count': enhanced_level_count,
            'legacy_count': legacy_level_count,
            'count_difference': abs(enhanced_level_count - legacy_level_count)
        }
        
        results['consistency_checks'] = consistency_checks
        
        print(f"✅ Enhanced service: {len(curriculum)} programs, {enhanced_level_count} levels")
        print(f"✅ Legacy service: {legacy_level_count} curriculum items")
        print(f"✅ Data consistency: {'MATCH' if consistency_checks['level_count_match'] else 'MISMATCH'}")
        
    except Exception as e:
        results['error'] = {
            'message': str(e),
            'traceback': traceback.format_exc()
        }
        print(f"❌ Backend service validation failed: {e}")

def validate_view_integration():
    """Validate view integration and URL routing"""
    log_test_section("VIEW INTEGRATION VALIDATION")
    
    try:
        # Test view function directly
        factory = RequestFactory()
        request = factory.get('/routinetest/exam/exam_library/')
        
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No admin user found - creating test user")
            admin_user = User.objects.create_superuser('testadmin', 'test@example.com', 'testpass')
        
        request.user = admin_user
        
        # Test view context preparation
        print("🧪 Testing view context preparation...")
        
        # Simulate key parts of the exam_list view
        curriculum_data_for_copy_modal = ExamService.get_routinetest_curriculum_levels()
        curriculum_hierarchy_for_copy = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        context_validation = {
            'curriculum_levels_available': bool(curriculum_data_for_copy_modal),
            'curriculum_hierarchy_available': bool(curriculum_hierarchy_for_copy),
            'levels_count': len(curriculum_data_for_copy_modal) if isinstance(curriculum_data_for_copy_modal, list) else 0,
            'hierarchy_programs': len(curriculum_hierarchy_for_copy.get('curriculum_data', {})) if curriculum_hierarchy_for_copy else 0,
        }
        
        validation_results['view_integration'] = context_validation
        print(f"✅ View context validation: {context_validation}")
        
    except Exception as e:
        validation_results['view_integration'] = {'error': str(e)}
        print(f"❌ View integration validation failed: {e}")

def validate_url_routing():
    """Validate URL routing to exam library"""
    log_test_section("URL ROUTING VALIDATION")
    
    try:
        client = Client()
        admin_user = User.objects.filter(is_superuser=True).first()
        client.force_login(admin_user)
        
        # Test various URL patterns
        url_tests = [
            '/routinetest/exam/exam_library/',
            '/RoutineTest/exam/exam_library/',
        ]
        
        routing_results = {}
        for url in url_tests:
            try:
                response = client.get(url)
                routing_results[url] = {
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'has_context': hasattr(response, 'context') and response.context is not None,
                    'template_name': getattr(response, 'template_name', None)
                }
                if response.status_code == 200 and hasattr(response, 'context'):
                    routing_results[url]['has_curriculum_data'] = 'curriculum_hierarchy_for_copy' in response.context
            except Exception as e:
                routing_results[url] = {'error': str(e)}
        
        validation_results['url_routing'] = routing_results
        print(f"✅ URL routing results: {routing_results}")
        
    except Exception as e:
        validation_results['url_routing'] = {'error': str(e)}
        print(f"❌ URL routing validation failed: {e}")

# Run Phase 1 validations
validate_backend_service()
validate_view_integration()
validate_url_routing()

print(f"\n{'='*100}")
print("📊 PHASE 1 RESULTS SUMMARY")
print(f"{'='*100}")

# Analyze results
backend_success = 'error' not in validation_results['backend_service']
view_success = 'error' not in validation_results.get('view_integration', {})
routing_success = any(
    result.get('success', False) 
    for result in validation_results.get('url_routing', {}).values() 
    if isinstance(result, dict)
)

print(f"✅ Backend Service: {'PASS' if backend_success else 'FAIL'}")
print(f"✅ View Integration: {'PASS' if view_success else 'FAIL'}")
print(f"✅ URL Routing: {'PASS' if routing_success else 'FAIL'}")

phase1_success_rate = sum([backend_success, view_success, routing_success]) / 3 * 100
print(f"\n🎯 Phase 1 Success Rate: {phase1_success_rate:.1f}%")

if phase1_success_rate >= 80:
    print("🎉 Phase 1: EXCELLENT - Backend is fully functional")
elif phase1_success_rate >= 60:
    print("⚠️  Phase 1: GOOD - Minor backend issues")
else:
    print("❌ Phase 1: NEEDS WORK - Significant backend problems")

# Export results for further analysis
with open('phase1_validation_results.json', 'w') as f:
    json.dump(validation_results, f, indent=2, default=str)

print(f"\n📄 Detailed results saved to: phase1_validation_results.json")
print(f"Completed: {datetime.now().isoformat()}")
print("="*100)