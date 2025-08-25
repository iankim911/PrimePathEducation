#!/usr/bin/env python
"""
Comprehensive QA After Program Mapping Fix
==========================================

QA testing to ensure the program mapping fix doesn't break other functionality
and that all class access features continue to work correctly.

Author: Claude Code Agent System
Date: August 25, 2025
"""

import os
import sys
import django
import json
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment, Class
from primepath_routinetest.class_code_mapping import get_class_codes_by_program

def comprehensive_qa_testing():
    """Run comprehensive QA testing after the program mapping fix"""
    
    qa_results = {
        'timestamp': datetime.now().isoformat(),
        'test_results': {},
        'overall_status': 'PENDING',
        'critical_issues': [],
        'warnings': [],
        'summary': {}
    }
    
    print("="*100)
    print("COMPREHENSIVE QA TESTING - AFTER PROGRAM MAPPING FIX")
    print("="*100)
    print(f"QA started: {qa_results['timestamp']}")
    print()
    
    # Test 1: Verify Teacher1 Fix (Original Issue)
    print("📋 TEST 1: VERIFY TEACHER1 CLASS MANAGEMENT FIX")
    print("-" * 80)
    
    try:
        teacher1 = Teacher.objects.get(user__username='teacher1')
        tca_count = TeacherClassAssignment.objects.filter(teacher=teacher1, is_active=True).count()
        class_count = Class.objects.filter(is_active=True, assigned_teachers=teacher1).count()
        
        # Test the program mapping logic specifically
        my_assignments = TeacherClassAssignment.objects.filter(teacher=teacher1, is_active=True)
        
        PROGRAM_MAPPING = {
            'CORE': get_class_codes_by_program('CORE'),
            'ASCENT': get_class_codes_by_program('ASCENT'), 
            'EDGE': get_class_codes_by_program('EDGE'),
            'PINNACLE': get_class_codes_by_program('PINNACLE')
        }
        
        # Simulate programs_data building (exact logic from view)
        programs_data = []
        for program_name in ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']:
            program_classes = []
            for assignment in my_assignments:
                if assignment.class_code in PROGRAM_MAPPING[program_name]:
                    program_classes.append(assignment.class_code)
            if program_classes:
                programs_data.append({
                    'name': program_name,
                    'classes': program_classes
                })
        
        qa_results['test_results']['teacher1_fix'] = {
            'teacher_name': teacher1.name,
            'tca_assignments': tca_count,
            'class_assignments': class_count,
            'programs_data_count': len(programs_data),
            'programs_populated': [p['name'] for p in programs_data],
            'total_classes_mapped': sum(len(p['classes']) for p in programs_data),
            'status': 'PASS' if len(programs_data) > 0 else 'FAIL'
        }
        
        print(f"Teacher: {teacher1.name}")
        print(f"TCA assignments: {tca_count}")
        print(f"Class assignments: {class_count}")
        print(f"Programs populated: {len(programs_data)} ({[p['name'] for p in programs_data]})")
        print(f"Total classes mapped: {sum(len(p['classes']) for p in programs_data)}")
        
        if len(programs_data) > 0:
            print("✅ PASS: Class Management should now display classes")
        else:
            print("❌ FAIL: Class Management will still show 'No classes available'")
            qa_results['critical_issues'].append("Teacher1 program mapping still broken after fix")
            
    except Exception as e:
        qa_results['test_results']['teacher1_fix'] = {'status': 'ERROR', 'error': str(e)}
        qa_results['critical_issues'].append(f"Error testing teacher1 fix: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
    
    # Test 2: System-Wide Program Mapping Integrity
    print("\n📋 TEST 2: SYSTEM-WIDE PROGRAM MAPPING INTEGRITY")
    print("-" * 80)
    
    try:
        # Test all programs have classes
        total_mapped_classes = 0
        program_stats = {}
        
        for program in ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']:
            program_classes = get_class_codes_by_program(program)
            program_stats[program] = len(program_classes)
            total_mapped_classes += len(program_classes)
            print(f"{program}: {len(program_classes)} classes")
        
        qa_results['test_results']['program_mapping_integrity'] = {
            'total_mapped_classes': total_mapped_classes,
            'program_stats': program_stats,
            'programs_with_classes': sum(1 for count in program_stats.values() if count > 0),
            'status': 'PASS' if total_mapped_classes > 0 else 'FAIL'
        }
        
        print(f"Total classes mapped across all programs: {total_mapped_classes}")
        print(f"Programs with classes: {sum(1 for count in program_stats.values() if count > 0)}/4")
        
        if total_mapped_classes > 0:
            print("✅ PASS: Program mapping system functioning")
        else:
            print("❌ FAIL: Program mapping system broken")
            qa_results['critical_issues'].append("Program mapping system completely broken")
            
    except Exception as e:
        qa_results['test_results']['program_mapping_integrity'] = {'status': 'ERROR', 'error': str(e)}
        qa_results['critical_issues'].append(f"Error testing program mapping integrity: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
    
    # Test 3: All Teachers Program Mapping
    print("\n📋 TEST 3: ALL TEACHERS PROGRAM MAPPING FUNCTIONALITY")
    print("-" * 80)
    
    try:
        all_teachers = Teacher.objects.all()
        teachers_tested = 0
        teachers_with_programs = 0
        teachers_with_assignments = 0
        
        for teacher in all_teachers:
            teachers_tested += 1
            my_assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
            
            if my_assignments.exists():
                teachers_with_assignments += 1
                
                # Test program mapping for this teacher
                PROGRAM_MAPPING = {
                    'CORE': get_class_codes_by_program('CORE'),
                    'ASCENT': get_class_codes_by_program('ASCENT'), 
                    'EDGE': get_class_codes_by_program('EDGE'),
                    'PINNACLE': get_class_codes_by_program('PINNACLE')
                }
                
                programs_data = []
                for program_name in ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']:
                    program_classes = []
                    for assignment in my_assignments:
                        if assignment.class_code in PROGRAM_MAPPING[program_name]:
                            program_classes.append(assignment.class_code)
                    if program_classes:
                        programs_data.append({
                            'name': program_name,
                            'classes': program_classes
                        })
                
                if len(programs_data) > 0:
                    teachers_with_programs += 1
        
        qa_results['test_results']['all_teachers_mapping'] = {
            'teachers_tested': teachers_tested,
            'teachers_with_assignments': teachers_with_assignments,
            'teachers_with_programs': teachers_with_programs,
            'program_mapping_success_rate': (teachers_with_programs / teachers_with_assignments * 100) if teachers_with_assignments > 0 else 0,
            'status': 'PASS' if teachers_with_programs == teachers_with_assignments else 'WARNING' if teachers_with_programs > 0 else 'FAIL'
        }
        
        print(f"Teachers tested: {teachers_tested}")
        print(f"Teachers with assignments: {teachers_with_assignments}")
        print(f"Teachers with program mapping: {teachers_with_programs}")
        
        success_rate = (teachers_with_programs / teachers_with_assignments * 100) if teachers_with_assignments > 0 else 0
        print(f"Program mapping success rate: {success_rate:.1f}%")
        
        if success_rate >= 100:
            print("✅ PASS: All teachers with assignments have program mapping")
        elif success_rate >= 80:
            print("⚠️  WARNING: Most teachers have program mapping working")
            qa_results['warnings'].append(f"Program mapping working for {success_rate:.1f}% of teachers")
        else:
            print("❌ FAIL: Program mapping broken for many teachers")
            qa_results['critical_issues'].append(f"Program mapping only working for {success_rate:.1f}% of teachers")
            
    except Exception as e:
        qa_results['test_results']['all_teachers_mapping'] = {'status': 'ERROR', 'error': str(e)}
        qa_results['critical_issues'].append(f"Error testing all teachers mapping: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
    
    # Test 4: Data Integrity Check
    print("\n📋 TEST 4: DATA INTEGRITY CHECK")
    print("-" * 80)
    
    try:
        # Verify TeacherClassAssignment <-> Class.assigned_teachers synchronization is still intact
        teacher1 = Teacher.objects.get(user__username='teacher1')
        tca_classes = set(TeacherClassAssignment.objects.filter(teacher=teacher1, is_active=True).values_list('class_code', flat=True))
        class_sections = set(Class.objects.filter(is_active=True, assigned_teachers=teacher1).values_list('section', flat=True))
        
        synchronization_intact = tca_classes == class_sections
        
        qa_results['test_results']['data_integrity'] = {
            'tca_classes_count': len(tca_classes),
            'class_sections_count': len(class_sections),
            'synchronization_intact': synchronization_intact,
            'missing_in_class_system': list(tca_classes - class_sections),
            'extra_in_class_system': list(class_sections - tca_classes),
            'status': 'PASS' if synchronization_intact else 'FAIL'
        }
        
        print(f"TCA classes: {len(tca_classes)}")
        print(f"Class sections: {len(class_sections)}")
        print(f"Synchronization intact: {synchronization_intact}")
        
        if synchronization_intact:
            print("✅ PASS: Data synchronization preserved after fix")
        else:
            print("❌ FAIL: Data synchronization broken by fix")
            print(f"   Missing in Class system: {list(tca_classes - class_sections)}")
            print(f"   Extra in Class system: {list(class_sections - tca_classes)}")
            qa_results['critical_issues'].append("Fix broke data synchronization")
            
    except Exception as e:
        qa_results['test_results']['data_integrity'] = {'status': 'ERROR', 'error': str(e)}
        qa_results['critical_issues'].append(f"Error testing data integrity: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
    
    # Test 5: View Function Import Test
    print("\n📋 TEST 5: VIEW FUNCTION IMPORT TEST") 
    print("-" * 80)
    
    try:
        # Test that the view can still import successfully
        from primepath_routinetest.class_code_mapping import get_class_codes_by_program
        from primepath_routinetest.views.classes_exams_unified import classes_exams_unified_view
        
        # Test that the function we're using exists and works
        core_classes = get_class_codes_by_program('CORE')
        test_import_success = len(core_classes) > 0
        
        qa_results['test_results']['view_imports'] = {
            'get_class_codes_by_program_works': test_import_success,
            'view_function_importable': True,
            'core_classes_count': len(core_classes),
            'status': 'PASS' if test_import_success else 'FAIL'
        }
        
        print(f"get_class_codes_by_program function: {'✅ Working' if test_import_success else '❌ Broken'}")
        print(f"View function importable: ✅ Yes")
        print(f"Core classes returned: {len(core_classes)}")
        
        if test_import_success:
            print("✅ PASS: All imports and functions working")
        else:
            print("❌ FAIL: Import or function issues detected")
            qa_results['critical_issues'].append("View function imports broken")
            
    except Exception as e:
        qa_results['test_results']['view_imports'] = {'status': 'ERROR', 'error': str(e)}
        qa_results['critical_issues'].append(f"Error testing view imports: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
    
    # Overall Assessment
    print("\n" + "="*80)
    print("QA TEST RESULTS SUMMARY")
    print("="*80)
    
    total_tests = len(qa_results['test_results'])
    passed_tests = sum(1 for test in qa_results['test_results'].values() if test.get('status') == 'PASS')
    failed_tests = sum(1 for test in qa_results['test_results'].values() if test.get('status') == 'FAIL')
    error_tests = sum(1 for test in qa_results['test_results'].values() if test.get('status') == 'ERROR')
    warning_tests = sum(1 for test in qa_results['test_results'].values() if test.get('status') == 'WARNING')
    
    qa_results['summary'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'error_tests': error_tests,
        'warning_tests': warning_tests,
        'critical_issues_count': len(qa_results['critical_issues']),
        'warnings_count': len(qa_results['warnings'])
    }
    
    print(f"Tests run: {total_tests}")
    print(f"Tests passed: {passed_tests}")
    print(f"Tests failed: {failed_tests}")
    print(f"Tests with errors: {error_tests}")
    print(f"Tests with warnings: {warning_tests}")
    print(f"Critical issues: {len(qa_results['critical_issues'])}")
    print(f"Warnings: {len(qa_results['warnings'])}")
    
    if len(qa_results['critical_issues']) == 0 and failed_tests == 0:
        qa_results['overall_status'] = 'PASS'
        print("\n🎉 OVERALL STATUS: PASS")
        print("✅ Program mapping fix successful - no critical issues detected")
        print("✅ Class Management 'No classes available' issue resolved")
        
        if len(qa_results['warnings']) > 0:
            print(f"⚠️  Note: {len(qa_results['warnings'])} warnings detected (non-critical)")
            
    elif len(qa_results['critical_issues']) == 0 and failed_tests > 0:
        qa_results['overall_status'] = 'WARNING'
        print("\n⚠️  OVERALL STATUS: WARNING")
        print("Some tests failed but no critical issues detected")
        
    else:
        qa_results['overall_status'] = 'FAIL'
        print("\n❌ OVERALL STATUS: FAIL")
        print("Critical issues detected - manual review required")
        
        if qa_results['critical_issues']:
            print("\nCritical Issues:")
            for issue in qa_results['critical_issues']:
                print(f"   • {issue}")
    
    if qa_results['warnings']:
        print("\nWarnings:")
        for warning in qa_results['warnings']:
            print(f"   • {warning}")
    
    # Save detailed results
    results_file = f'qa_program_mapping_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(results_file, 'w') as f:
        json.dump(qa_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed QA results saved to: {results_file}")
    
    return qa_results

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    COMPREHENSIVE QA TESTING SUITE                           ║
║                  Post Program Mapping Fix Validation                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    results = comprehensive_qa_testing()
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                               QA TESTING COMPLETE                           ║
║                                                                              ║
║  Status: {results['overall_status']:<60} ║
║  Critical Issues: {len(results['critical_issues']):<52} ║  
║  Warnings: {len(results['warnings']):<57} ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    return results['overall_status'] == 'PASS'

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)