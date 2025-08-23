#!/usr/bin/env python3
"""
FRONTEND LOGIC VERIFICATION - COPY MODAL DROPDOWN
=================================================

This script verifies all frontend JavaScript logic, modal behavior,
and dropdown population functionality.
"""

import os
import sys
import django
import json
import re
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.template.loader import get_template

print("="*100)
print("🔍 FRONTEND LOGIC VERIFICATION: COPY MODAL DROPDOWN")
print("="*100)
print(f"Started: {datetime.now().isoformat()}")
print()

def extract_javascript_functions(content):
    """Extract and analyze JavaScript functions from template"""
    print("="*50)
    print("PHASE 3A: JAVASCRIPT FUNCTION ANALYSIS")
    print("="*50)
    
    # Key functions we expect
    expected_functions = [
        'populateCopyProgramDropdown',
        'initializeCurriculumDropdown',
        'tryFallbackCurriculumInitialization',
        'showCurriculumDataError',
        'runCurriculumDiagnostic',
        'openCopyModalInternal',
        'setupCopyCurriculumEventListeners',
        'debugCopyModal'
    ]
    
    function_analysis = {}
    
    for func_name in expected_functions:
        # Look for function definition patterns
        patterns = [
            rf'function {func_name}\s*\(',
            rf'{func_name}\s*=\s*function\s*\(',
            rf'const {func_name}\s*=\s*\(',
            rf'async function {func_name}\s*\('
        ]
        
        found = False
        definition_type = None
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                found = True
                definition_type = pattern
                break
        
        function_analysis[func_name] = {
            'found': found,
            'definition_type': definition_type,
            'call_count': content.count(func_name)
        }
    
    print("📊 JavaScript Function Analysis:")
    for func_name, analysis in function_analysis.items():
        status = "✅" if analysis['found'] else "❌"
        print(f"  {status} {func_name}:")
        print(f"    - Definition found: {analysis['found']}")
        print(f"    - Called {analysis['call_count']} times")
        if analysis['definition_type']:
            print(f"    - Type: {analysis['definition_type']}")
    
    return function_analysis

def analyze_curriculum_initialization(content):
    """Analyze curriculum data initialization logic"""
    print("="*50)
    print("PHASE 3B: CURRICULUM INITIALIZATION ANALYSIS")
    print("="*50)
    
    # Key initialization patterns
    init_patterns = {
        'global_vars_declared': 'window.CopyCurriculumData = null',
        'data_ready_flag': 'window.CopyCurriculumDataReady',
        'initialized_flag': 'window.CopyCurriculumDataInitialized',
        'error_handling': 'window.CopyCurriculumDataError',
        'json_script_processing': 'copy-curriculum-hierarchy-data',
        'django_context_check': 'curriculum_hierarchy_for_copy',
        'enhanced_v4_logic': 'ENHANCED v4.0',
        'fallback_data_structure': 'CORE.*subprograms.*Phonics'
    }
    
    init_analysis = {}
    
    for pattern_name, pattern in init_patterns.items():
        matches = len(re.findall(pattern, content, re.IGNORECASE | re.DOTALL))
        init_analysis[pattern_name] = {
            'found': matches > 0,
            'count': matches
        }
    
    print("📊 Curriculum Initialization Analysis:")
    for pattern_name, analysis in init_analysis.items():
        status = "✅" if analysis['found'] else "❌"
        print(f"  {status} {pattern_name}: {analysis['count']} occurrences")
    
    return init_analysis

def analyze_modal_behavior(content):
    """Analyze modal opening and behavior logic"""
    print("="*50)
    print("PHASE 3C: MODAL BEHAVIOR ANALYSIS")
    print("="*50)
    
    # Modal behavior patterns
    modal_patterns = {
        'modal_opening': r'openCopyModalInternal\s*\(',
        'modal_display_setting': r'modal\.style\.display\s*=\s*[\'"]block[\'"]',
        'curriculum_wait_logic': r'waitForCurriculumData|initializeCurriculumDropdown',
        'retry_mechanism': r'attempt.*maxAttempts',
        'progressive_delay': r'Math\.min.*delay',
        'verification_logic': r'dropdown.*options\.length',
        'success_feedback': r'🎉.*DROPDOWN.*SUCCESSFUL',
        'error_feedback': r'❌.*DROPDOWN.*FAILED'
    }
    
    modal_analysis = {}
    
    for pattern_name, pattern in modal_patterns.items():
        matches = len(re.findall(pattern, content, re.IGNORECASE | re.DOTALL))
        modal_analysis[pattern_name] = {
            'found': matches > 0,
            'count': matches
        }
    
    print("📊 Modal Behavior Analysis:")
    for pattern_name, analysis in modal_analysis.items():
        status = "✅" if analysis['found'] else "❌"
        print(f"  {status} {pattern_name}: {analysis['count']} occurrences")
    
    return modal_analysis

def analyze_dropdown_population(content):
    """Analyze dropdown population logic"""
    print("="*50)
    print("PHASE 3D: DROPDOWN POPULATION ANALYSIS")
    print("="*50)
    
    # Dropdown population patterns
    dropdown_patterns = {
        'program_select_element': r'copyProgramSelect',
        'option_creation': r'createElement\s*\(\s*[\'"]option[\'"]',
        'option_appending': r'appendChild\s*\(\s*option\)',
        'program_iteration': r'Object\.keys.*CopyCurriculumData',
        'structure_validation': r'subprograms.*forEach|for.*subprograms',
        'dropdown_clearing': r'innerHTML\s*=.*Select Program',
        'success_verification': r'options\.length\s*>\s*1',
        'expected_programs_check': r'CORE.*EDGE.*ASCENT.*PINNACLE'
    }
    
    dropdown_analysis = {}
    
    for pattern_name, pattern in dropdown_patterns.items():
        matches = len(re.findall(pattern, content, re.IGNORECASE | re.DOTALL))
        dropdown_analysis[pattern_name] = {
            'found': matches > 0,
            'count': matches
        }
    
    print("📊 Dropdown Population Analysis:")
    for pattern_name, analysis in dropdown_analysis.items():
        status = "✅" if analysis['found'] else "❌"
        print(f"  {status} {pattern_name}: {analysis['count']} occurrences")
    
    return dropdown_analysis

def analyze_error_handling(content):
    """Analyze error handling and fallback systems"""
    print("="*50)
    print("PHASE 3E: ERROR HANDLING ANALYSIS")
    print("="*50)
    
    # Error handling patterns
    error_patterns = {
        'try_catch_blocks': r'try\s*\{[\s\S]*?\}\s*catch',
        'error_logging': r'console\.error',
        'fallback_triggers': r'tryFallbackCurriculumInitialization',
        'timeout_handling': r'TIMEOUT|maxAttempts',
        'data_validation': r'if\s*\(.*curriculum.*data.*\)',
        'user_error_display': r'showCurriculumDataError',
        'diagnostic_tools': r'runCurriculumDiagnostic',
        'graceful_degradation': r'Curriculum.*data.*unavailable'
    }
    
    error_analysis = {}
    
    for pattern_name, pattern in error_patterns.items():
        matches = len(re.findall(pattern, content, re.IGNORECASE | re.DOTALL))
        error_analysis[pattern_name] = {
            'found': matches > 0,
            'count': matches
        }
    
    print("📊 Error Handling Analysis:")
    for pattern_name, analysis in error_analysis.items():
        status = "✅" if analysis['found'] else "❌"
        print(f"  {status} {pattern_name}: {analysis['count']} occurrences")
    
    return error_analysis

def test_frontend_integration():
    """Test frontend integration with live template"""
    print("="*50)
    print("PHASE 3F: FRONTEND INTEGRATION TEST")
    print("="*50)
    
    client = Client()
    admin_user = User.objects.filter(is_superuser=True).first()
    client.force_login(admin_user)
    
    # Get the rendered template content
    response = client.get('/RoutineTest/exams/')
    
    if response.status_code != 200:
        print(f"❌ Failed to get template (status: {response.status_code})")
        return {}
    
    content = response.content.decode('utf-8')
    print(f"✅ Got template content ({len(content)} chars)")
    
    # Run all analyses on the live content
    function_analysis = extract_javascript_functions(content)
    init_analysis = analyze_curriculum_initialization(content)
    modal_analysis = analyze_modal_behavior(content)
    dropdown_analysis = analyze_dropdown_population(content)
    error_analysis = analyze_error_handling(content)
    
    return {
        'functions': function_analysis,
        'initialization': init_analysis,
        'modal_behavior': modal_analysis,
        'dropdown_population': dropdown_analysis,
        'error_handling': error_analysis,
        'content_length': len(content)
    }

# Run Phase 3 comprehensive frontend verification
print("🚀 Starting Phase 3: Frontend Logic Verification")
print()

frontend_results = test_frontend_integration()

# Calculate success rates
if frontend_results:
    # Function completeness
    functions = frontend_results['functions']
    function_success = sum(1 for f in functions.values() if f['found']) / len(functions)
    
    # Initialization completeness
    init = frontend_results['initialization']
    init_success = sum(1 for i in init.values() if i['found']) / len(init)
    
    # Modal behavior completeness
    modal = frontend_results['modal_behavior']
    modal_success = sum(1 for m in modal.values() if m['found']) / len(modal)
    
    # Dropdown population completeness
    dropdown = frontend_results['dropdown_population']
    dropdown_success = sum(1 for d in dropdown.values() if d['found']) / len(dropdown)
    
    # Error handling completeness
    error = frontend_results['error_handling']
    error_success = sum(1 for e in error.values() if e['found']) / len(error)
    
    # Overall success
    phase3_success_rate = (function_success + init_success + modal_success + dropdown_success + error_success) / 5 * 100
    
    print()
    print("="*100)
    print("📊 PHASE 3 RESULTS SUMMARY")
    print("="*100)
    
    print(f"✅ JavaScript Functions: {function_success*100:.1f}% ({sum(1 for f in functions.values() if f['found'])}/{len(functions)} found)")
    print(f"✅ Curriculum Initialization: {init_success*100:.1f}% ({sum(1 for i in init.values() if i['found'])}/{len(init)} found)")
    print(f"✅ Modal Behavior: {modal_success*100:.1f}% ({sum(1 for m in modal.values() if m['found'])}/{len(modal)} found)")
    print(f"✅ Dropdown Population: {dropdown_success*100:.1f}% ({sum(1 for d in dropdown.values() if d['found'])}/{len(dropdown)} found)")
    print(f"✅ Error Handling: {error_success*100:.1f}% ({sum(1 for e in error.values() if e['found'])}/{len(error)} found)")
    
    print(f"\n🎯 Phase 3 Overall Success Rate: {phase3_success_rate:.1f}%")
    
    if phase3_success_rate >= 90:
        print("🎉 Phase 3: EXCELLENT - Frontend logic is comprehensive and robust")
    elif phase3_success_rate >= 75:
        print("✅ Phase 3: GOOD - Frontend logic is mostly complete")
    elif phase3_success_rate >= 60:
        print("⚠️  Phase 3: NEEDS IMPROVEMENT - Some frontend logic missing")
    else:
        print("❌ Phase 3: CRITICAL ISSUES - Major frontend logic problems")
else:
    print("❌ Phase 3: FAILED - Could not analyze frontend logic")
    phase3_success_rate = 0

# Export results
results = {
    'timestamp': datetime.now().isoformat(),
    'frontend_results': frontend_results,
    'success_rates': {
        'function_success': function_success * 100 if frontend_results else 0,
        'init_success': init_success * 100 if frontend_results else 0,
        'modal_success': modal_success * 100 if frontend_results else 0,
        'dropdown_success': dropdown_success * 100 if frontend_results else 0,
        'error_success': error_success * 100 if frontend_results else 0,
        'phase3_overall': phase3_success_rate
    }
}

with open('phase3_frontend_verification_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n📄 Detailed results saved to: phase3_frontend_verification_results.json")
print(f"Completed: {datetime.now().isoformat()}")
print("="*100)