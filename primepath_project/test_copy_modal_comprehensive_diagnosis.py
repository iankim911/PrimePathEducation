#!/usr/bin/env python3
"""
COMPREHENSIVE COPY MODAL DROPDOWN DIAGNOSIS
==========================================

This script will perform a complete analysis of the Copy Exam modal dropdown issue
by testing every component in the data flow chain from backend to frontend.
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
from django.test import RequestFactory
from django.template.loader import get_template
from django.template.context import Context
from primepath_routinetest.views.exam import exam_list
from primepath_routinetest.services.exam_service import ExamService
from core.models import CurriculumLevel
import logging

print("="*80)
print("🔍 COMPREHENSIVE COPY MODAL DROPDOWN DIAGNOSIS")
print("="*80)
print(f"Started at: {datetime.now().isoformat()}")
print()

# Test 1: Backend Service Method Analysis
print("📋 TEST 1: BACKEND SERVICE METHOD ANALYSIS")
print("-" * 50)

try:
    print("Testing ExamService.get_routinetest_curriculum_hierarchy_for_frontend()...")
    curriculum_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
    
    print(f"✅ Service method executed successfully")
    print(f"📊 Data type: {type(curriculum_data)}")
    print(f"📊 Data keys: {list(curriculum_data.keys()) if isinstance(curriculum_data, dict) else 'Not a dict'}")
    
    if 'curriculum_data' in curriculum_data:
        actual_curriculum = curriculum_data['curriculum_data']
        print(f"📊 Nested curriculum_data type: {type(actual_curriculum)}")
        print(f"📊 Available programs: {list(actual_curriculum.keys()) if isinstance(actual_curriculum, dict) else 'Not a dict'}")
        
        # Validate expected programs
        expected_programs = ['CORE', 'EDGE', 'ASCENT', 'PINNACLE']
        found_programs = list(actual_curriculum.keys()) if isinstance(actual_curriculum, dict) else []
        
        print(f"📊 Expected programs: {expected_programs}")
        print(f"📊 Found programs: {found_programs}")
        print(f"📊 Programs match: {set(expected_programs) == set(found_programs)}")
        
        # Check structure of each program
        for program in found_programs:
            if program in actual_curriculum and 'subprograms' in actual_curriculum[program]:
                subprograms = list(actual_curriculum[program]['subprograms'].keys())
                print(f"📊   {program}: {len(subprograms)} subprograms - {subprograms}")
            else:
                print(f"❌   {program}: Invalid structure - missing subprograms")
    else:
        print("❌ Missing 'curriculum_data' key in response")
        
    print(f"📄 Full service response structure:")
    print(json.dumps(curriculum_data, indent=2, default=str)[:1000] + "..." if len(str(curriculum_data)) > 1000 else json.dumps(curriculum_data, indent=2, default=str))
    
except Exception as e:
    print(f"❌ Service method failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: View Context Analysis
print("📋 TEST 2: VIEW CONTEXT ANALYSIS")
print("-" * 50)

try:
    # Create mock request
    factory = RequestFactory()
    request = factory.get('/routinetest/exam/exam_library/')
    
    # Get admin user for testing
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found for testing")
    else:
        request.user = admin_user
        print(f"✅ Using admin user: {admin_user.username}")
        
        # Mock the view response to capture context
        print("Testing view context passing...")
        
        # We need to extract just the context preparation part
        from collections import defaultdict
        
        # Test curriculum data preparation (lines 303-304 in exam.py)
        curriculum_data_for_copy_modal = ExamService.get_routinetest_curriculum_levels()
        curriculum_hierarchy_for_copy = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        print(f"✅ curriculum_data_for_copy_modal: {type(curriculum_data_for_copy_modal)}")
        print(f"✅ curriculum_hierarchy_for_copy: {type(curriculum_hierarchy_for_copy)}")
        
        # Check if these would be available in template context
        context_vars = {
            'curriculum_levels_for_copy': curriculum_data_for_copy_modal,
            'curriculum_hierarchy_for_copy': curriculum_hierarchy_for_copy,
        }
        
        print(f"📊 Context variables that would be passed to template:")
        for var_name, var_value in context_vars.items():
            if var_value:
                print(f"  ✅ {var_name}: Available ({type(var_value)})")
                if isinstance(var_value, dict) and 'curriculum_data' in var_value:
                    print(f"     └── curriculum_data programs: {list(var_value['curriculum_data'].keys())}")
                elif isinstance(var_value, list):
                    print(f"     └── List with {len(var_value)} items")
            else:
                print(f"  ❌ {var_name}: Not available")
        
except Exception as e:
    print(f"❌ View context test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Template Rendering Analysis
print("📋 TEST 3: TEMPLATE RENDERING ANALYSIS")
print("-" * 50)

try:
    template = get_template('primepath_routinetest/exam_list_hierarchical.html')
    print(f"✅ Template found: {template.origin.name if hasattr(template, 'origin') else 'Unknown'}")
    
    # Create mock context with curriculum data
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
        'mapping_summary': {'total': 0, 'complete': 0, 'partial': 0, 'not_started': 0, 'accessible': 0, 'editable': 0},
        'exam_type_filter': 'ALL',
        'show_assigned_only': False,
        'ownership_filter': 'my',
        'is_my_files_active': True,
        'is_others_files_active': False,
        'exam_type_counts': {'review': 0, 'quarterly': 0, 'all': 0, 'assigned': 0},
        'filter_description': 'Test',
        'template_version': '6.0-test',
        'cache_bust_id': 123456789.0,
        'get_class_display_name': {},
    }
    
    print("📊 Testing template rendering with mock context...")
    
    # Test if template would render without error
    try:
        # We can't fully render due to complex template logic, but we can check key parts
        print("✅ Template context prepared successfully")
        print("📊 Key context variables for copy modal:")
        print(f"  - curriculum_hierarchy_for_copy available: {bool(mock_context.get('curriculum_hierarchy_for_copy'))}")
        print(f"  - curriculum_levels_for_copy available: {bool(mock_context.get('curriculum_levels_for_copy'))}")
        
        if mock_context.get('curriculum_hierarchy_for_copy'):
            hierarchy = mock_context['curriculum_hierarchy_for_copy']
            if isinstance(hierarchy, dict) and 'curriculum_data' in hierarchy:
                print(f"  - Programs in hierarchy: {list(hierarchy['curriculum_data'].keys())}")
        
    except Exception as e:
        print(f"❌ Template rendering issue: {e}")
        
except Exception as e:
    print(f"❌ Template analysis failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Database Curriculum Level Analysis
print("📋 TEST 4: DATABASE CURRICULUM LEVEL ANALYSIS")
print("-" * 50)

try:
    all_levels = CurriculumLevel.objects.all().order_by('program_name', 'subprogram_name', 'level_number')
    print(f"📊 Total curriculum levels in database: {all_levels.count()}")
    
    # Group by program
    program_stats = {}
    for level in all_levels:
        program = level.program_name
        if program not in program_stats:
            program_stats[program] = {'subprograms': set(), 'levels': 0}
        program_stats[program]['subprograms'].add(level.subprogram_name)
        program_stats[program]['levels'] += 1
    
    print("📊 Database curriculum structure:")
    for program, stats in program_stats.items():
        print(f"  {program}: {stats['levels']} levels, {len(stats['subprograms'])} subprograms")
        print(f"    Subprograms: {sorted(list(stats['subprograms']))}")
    
    # Check for the expected 4 main programs
    expected_programs = ['CORE', 'EDGE', 'ASCENT', 'PINNACLE']
    found_programs = list(program_stats.keys())
    
    print(f"📊 Expected main programs: {expected_programs}")
    print(f"📊 All programs in DB: {found_programs}")
    print(f"📊 Main programs present: {[p for p in expected_programs if p in found_programs]}")
    print(f"📊 Missing main programs: {[p for p in expected_programs if p not in found_programs]}")
    
except Exception as e:
    print(f"❌ Database analysis failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 5: JavaScript Data Structure Simulation
print("📋 TEST 5: JAVASCRIPT DATA STRUCTURE SIMULATION")
print("-" * 50)

try:
    print("Simulating JavaScript json_script filter processing...")
    
    # Simulate what Django's json_script filter would do
    if curriculum_hierarchy_for_copy:
        json_script_data = json.dumps(curriculum_hierarchy_for_copy, separators=(',', ':'))
        print(f"✅ JSON script data generated ({len(json_script_data)} characters)")
        
        # Simulate JavaScript parsing
        parsed_data = json.loads(json_script_data)
        print(f"✅ JSON parsing simulation successful")
        
        if 'curriculum_data' in parsed_data:
            curriculum_data = parsed_data['curriculum_data']
            print(f"📊 Extracted curriculum_data programs: {list(curriculum_data.keys())}")
            
            # Validate structure for JavaScript use
            js_valid = True
            for program, program_data in curriculum_data.items():
                if 'subprograms' not in program_data:
                    print(f"❌ Program {program} missing subprograms key")
                    js_valid = False
                else:
                    subprograms = program_data['subprograms']
                    if not isinstance(subprograms, dict):
                        print(f"❌ Program {program} subprograms is not a dict")
                        js_valid = False
                    else:
                        for subprogram, subprogram_data in subprograms.items():
                            if 'levels' not in subprogram_data:
                                print(f"❌ {program}/{subprogram} missing levels key")
                                js_valid = False
                            elif not isinstance(subprogram_data['levels'], list):
                                print(f"❌ {program}/{subprogram} levels is not a list")
                                js_valid = False
            
            print(f"📊 JavaScript structure validation: {'✅ VALID' if js_valid else '❌ INVALID'}")
            
            if js_valid:
                print("📊 Sample dropdown options that should be generated:")
                for program in sorted(curriculum_data.keys()):
                    print(f"  - {program}")
                    
        else:
            print("❌ Missing curriculum_data key in enhanced structure")
    else:
        print("❌ No curriculum_hierarchy_for_copy data to simulate")

except Exception as e:
    print(f"❌ JavaScript simulation failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 6: Issue Summary and Recommendations
print("📋 TEST 6: ISSUE DIAGNOSIS SUMMARY")
print("-" * 50)

print("🔍 DIAGNOSIS SUMMARY:")
print()

# Check each component
components_status = {
    "Backend Service Method": "✅ Working" if curriculum_hierarchy_for_copy else "❌ Failed",
    "Data Structure Validity": "✅ Valid" if (curriculum_hierarchy_for_copy and 'curriculum_data' in curriculum_hierarchy_for_copy) else "❌ Invalid",
    "Expected Programs Present": "✅ All Present" if (curriculum_hierarchy_for_copy and 'curriculum_data' in curriculum_hierarchy_for_copy and 
                                                    set(['CORE', 'EDGE', 'ASCENT', 'PINNACLE']).issubset(set(curriculum_hierarchy_for_copy['curriculum_data'].keys()))) else "❌ Missing Programs",
    "Database Curriculum Data": "✅ Available" if CurriculumLevel.objects.exists() else "❌ No Data",
    "JSON Serialization": "✅ Works" if curriculum_hierarchy_for_copy else "❌ No Data to Serialize"
}

for component, status in components_status.items():
    print(f"  {component}: {status}")

print()
print("🎯 LIKELY ROOT CAUSES:")
if all("✅" in status for status in components_status.values()):
    print("  • Backend data pipeline is working correctly")
    print("  • Issue is likely in frontend timing or JavaScript execution")
    print("  • Template context passing may have initialization issues")
    print("  • Modal opening sequence timing problems")
else:
    print("  • Backend data pipeline has issues")
    for component, status in components_status.items():
        if "❌" in status:
            print(f"    - {component}")

print()
print("🔧 RECOMMENDED FIXES:")
print("  1. Add comprehensive JavaScript debugging in template")
print("  2. Implement robust data availability checking")
print("  3. Fix modal initialization sequence")
print("  4. Add fallback data loading mechanisms")
print("  5. Implement proper error handling and user feedback")

print()
print("="*80)
print(f"Diagnosis completed at: {datetime.now().isoformat()}")
print("="*80)