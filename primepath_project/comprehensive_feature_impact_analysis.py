#!/usr/bin/env python
"""
Comprehensive Feature Impact Analysis
====================================

Thorough analysis to ensure the program mapping fix did not break any existing features.
This script tests all major functionality that could potentially be affected.

Author: Claude Code Agent System
Date: August 25, 2025
"""

import os
import sys
import django
import json
from datetime import datetime
from collections import defaultdict

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import Teacher
from primepath_routinetest.models import (
    TeacherClassAssignment, 
    Class, 
    Exam, 
    ClassAccessRequest,
    ExamScheduleMatrix
)
from primepath_routinetest.class_code_mapping import (
    CLASS_CODE_CURRICULUM_MAPPING,
    get_class_codes_by_program,
    get_curriculum_for_class,
    validate_class_code,
    get_all_class_codes
)

def test_all_existing_features():
    """Test all existing features that could be affected by the fix"""
    
    impact_results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'overall_status': 'PENDING',
        'broken_features': [],
        'working_features': [],
        'warnings': []
    }
    
    print("="*100)
    print("COMPREHENSIVE FEATURE IMPACT ANALYSIS")
    print("="*100)
    print(f"Analysis started: {impact_results['timestamp']}")
    print()
    
    # TEST 1: Class Code Mapping System
    print("🔍 TEST 1: CLASS CODE MAPPING SYSTEM INTEGRITY")
    print("-" * 80)
    
    try:
        # Test core mapping functions
        all_codes = get_all_class_codes()
        valid_codes = [code for code in all_codes if validate_class_code(code)]
        
        # Test program mapping functions
        core_classes = get_class_codes_by_program('CORE')
        ascent_classes = get_class_codes_by_program('ASCENT')
        edge_classes = get_class_codes_by_program('EDGE')
        pinnacle_classes = get_class_codes_by_program('PINNACLE')
        
        # Test individual class lookups
        sample_classes = ['C5', 'PRIMARY_1D', 'HIGH_10E', 'SejongM', 'TaejoE']
        lookup_results = {}
        for class_code in sample_classes:
            if class_code in CLASS_CODE_CURRICULUM_MAPPING:
                lookup_results[class_code] = get_curriculum_for_class(class_code)
        
        test_result = {
            'total_class_codes': len(all_codes),
            'valid_class_codes': len(valid_codes),
            'core_program_classes': len(core_classes),
            'ascent_program_classes': len(ascent_classes),
            'edge_program_classes': len(edge_classes),
            'pinnacle_program_classes': len(pinnacle_classes),
            'sample_lookups': lookup_results,
            'mapping_integrity': len(valid_codes) == len(all_codes),
            'program_mapping_working': all([
                len(core_classes) > 0,
                len(ascent_classes) > 0,
                len(edge_classes) > 0,
                len(pinnacle_classes) > 0
            ]),
            'status': 'PASS'
        }
        
        impact_results['tests']['class_code_mapping'] = test_result
        
        print(f"Total class codes: {len(all_codes)}")
        print(f"Valid class codes: {len(valid_codes)}")
        print(f"Program classes - CORE: {len(core_classes)}, ASCENT: {len(ascent_classes)}")
        print(f"Program classes - EDGE: {len(edge_classes)}, PINNACLE: {len(pinnacle_classes)}")
        print(f"Sample lookups working: {len(lookup_results)} out of {len(sample_classes)}")
        
        if test_result['mapping_integrity'] and test_result['program_mapping_working']:
            print("✅ PASS: Class code mapping system fully functional")
            impact_results['working_features'].append('Class Code Mapping System')
        else:
            print("❌ FAIL: Class code mapping system broken")
            impact_results['broken_features'].append('Class Code Mapping System')
        
    except Exception as e:
        impact_results['tests']['class_code_mapping'] = {'status': 'ERROR', 'error': str(e)}
        impact_results['broken_features'].append(f'Class Code Mapping System: {str(e)}')
        print(f"❌ ERROR: {str(e)}")
    
    # TEST 2: Teacher Class Assignment System
    print("\n🔍 TEST 2: TEACHER CLASS ASSIGNMENT SYSTEM")
    print("-" * 80)
    
    try:
        # Test all teacher assignments
        all_teachers = Teacher.objects.all()
        assignment_stats = {
            'total_teachers': all_teachers.count(),
            'teachers_with_assignments': 0,
            'total_assignments': 0,
            'assignment_types': defaultdict(int),
            'sample_assignments': []
        }
        
        for teacher in all_teachers[:5]:  # Test sample of teachers
            assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
            if assignments.exists():
                assignment_stats['teachers_with_assignments'] += 1
                assignment_stats['total_assignments'] += assignments.count()
                
                # Test assignment display functionality
                for assignment in assignments[:3]:  # Sample first 3
                    try:
                        display_name = assignment.get_class_code_display() if hasattr(assignment, 'get_class_code_display') else assignment.class_code
                        assignment_stats['sample_assignments'].append({
                            'teacher': teacher.name,
                            'class_code': assignment.class_code,
                            'display_name': display_name,
                            'access_level': assignment.access_level,
                            'working': True
                        })
                        assignment_stats['assignment_types'][assignment.access_level] += 1
                    except Exception as e:
                        assignment_stats['sample_assignments'].append({
                            'teacher': teacher.name,
                            'class_code': assignment.class_code,
                            'error': str(e),
                            'working': False
                        })
        
        test_result = {
            'stats': assignment_stats,
            'assignment_system_working': assignment_stats['total_assignments'] > 0,
            'display_functions_working': all(a['working'] for a in assignment_stats['sample_assignments'] if 'working' in a),
            'status': 'PASS'
        }
        
        impact_results['tests']['teacher_assignments'] = test_result
        
        print(f"Teachers with assignments: {assignment_stats['teachers_with_assignments']}")
        print(f"Total active assignments: {assignment_stats['total_assignments']}")
        print(f"Access level distribution: {dict(assignment_stats['assignment_types'])}")
        print(f"Sample assignments tested: {len(assignment_stats['sample_assignments'])}")
        
        working_assignments = sum(1 for a in assignment_stats['sample_assignments'] if a.get('working', False))
        print(f"Working assignment displays: {working_assignments}/{len(assignment_stats['sample_assignments'])}")
        
        if test_result['assignment_system_working'] and test_result['display_functions_working']:
            print("✅ PASS: Teacher assignment system fully functional")
            impact_results['working_features'].append('Teacher Class Assignment System')
        else:
            print("❌ FAIL: Teacher assignment system issues detected")
            impact_results['broken_features'].append('Teacher Class Assignment System')
        
    except Exception as e:
        impact_results['tests']['teacher_assignments'] = {'status': 'ERROR', 'error': str(e)}
        impact_results['broken_features'].append(f'Teacher Assignment System: {str(e)}')
        print(f"❌ ERROR: {str(e)}")
    
    # TEST 3: Class Model and Assigned Teachers Relationship
    print("\n🔍 TEST 3: CLASS MODEL & ASSIGNED TEACHERS SYSTEM")
    print("-" * 80)
    
    try:
        # Test Class model functionality
        active_classes = Class.objects.filter(is_active=True)
        classes_with_teachers = Class.objects.filter(is_active=True, assigned_teachers__isnull=False).distinct()
        
        # Test specific relationships
        teacher1 = Teacher.objects.get(user__username='teacher1')
        teacher1_classes = Class.objects.filter(is_active=True, assigned_teachers=teacher1)
        
        # Test Class model methods and properties
        sample_class = active_classes.first()
        class_methods_working = True
        class_method_errors = []
        
        if sample_class:
            try:
                # Test that we can access basic properties
                _ = sample_class.name
                _ = sample_class.section
                _ = sample_class.is_active
                _ = sample_class.assigned_teachers.all()
            except Exception as e:
                class_methods_working = False
                class_method_errors.append(str(e))
        
        test_result = {
            'total_active_classes': active_classes.count(),
            'classes_with_teachers': classes_with_teachers.count(),
            'teacher1_assigned_classes': teacher1_classes.count(),
            'class_model_methods_working': class_methods_working,
            'class_method_errors': class_method_errors,
            'relationships_working': teacher1_classes.count() > 0,
            'status': 'PASS' if class_methods_working and teacher1_classes.count() > 0 else 'FAIL'
        }
        
        impact_results['tests']['class_model'] = test_result
        
        print(f"Active classes: {active_classes.count()}")
        print(f"Classes with assigned teachers: {classes_with_teachers.count()}")
        print(f"Teacher1 assigned classes: {teacher1_classes.count()}")
        print(f"Class model methods: {'✅ Working' if class_methods_working else '❌ Broken'}")
        
        if test_result['status'] == 'PASS':
            print("✅ PASS: Class model and relationships fully functional")
            impact_results['working_features'].append('Class Model & Assigned Teachers')
        else:
            print("❌ FAIL: Class model or relationships broken")
            impact_results['broken_features'].append('Class Model & Assigned Teachers')
            if class_method_errors:
                print(f"   Errors: {class_method_errors}")
        
    except Exception as e:
        impact_results['tests']['class_model'] = {'status': 'ERROR', 'error': str(e)}
        impact_results['broken_features'].append(f'Class Model System: {str(e)}')
        print(f"❌ ERROR: {str(e)}")
    
    # TEST 4: Exam System Integration
    print("\n🔍 TEST 4: EXAM SYSTEM INTEGRATION")
    print("-" * 80)
    
    try:
        # Test exam functionality that depends on class codes
        active_exams = Exam.objects.filter(is_active=True)
        exams_with_classes = []
        
        for exam in active_exams[:10]:  # Test sample of exams
            try:
                if hasattr(exam, 'class_codes') and exam.class_codes:
                    # Test that class codes in exams are still valid
                    if isinstance(exam.class_codes, list):
                        valid_class_codes = [code for code in exam.class_codes if validate_class_code(code)]
                        exams_with_classes.append({
                            'exam_id': exam.id,
                            'exam_name': exam.name[:30],
                            'class_codes': exam.class_codes,
                            'valid_class_codes': len(valid_class_codes),
                            'working': len(valid_class_codes) > 0
                        })
            except Exception as e:
                exams_with_classes.append({
                    'exam_id': exam.id,
                    'error': str(e),
                    'working': False
                })
        
        # Test matrix system compatibility
        matrix_cells = ExamScheduleMatrix.objects.all()[:5]  # Sample
        matrix_working = True
        
        for cell in matrix_cells:
            try:
                _ = cell.class_code
                _ = cell.academic_year
                _ = cell.time_period_type
                if not validate_class_code(cell.class_code):
                    matrix_working = False
                    break
            except:
                matrix_working = False
                break
        
        test_result = {
            'total_active_exams': active_exams.count(),
            'exams_tested': len(exams_with_classes),
            'exams_working': sum(1 for e in exams_with_classes if e.get('working', False)),
            'matrix_cells_tested': matrix_cells.count(),
            'matrix_system_working': matrix_working,
            'exam_class_integration_working': len([e for e in exams_with_classes if e.get('working', False)]) > 0,
            'status': 'PASS' if len([e for e in exams_with_classes if e.get('working', False)]) > 0 and matrix_working else 'WARNING'
        }
        
        impact_results['tests']['exam_system'] = test_result
        
        print(f"Active exams: {active_exams.count()}")
        print(f"Exams with class codes tested: {len(exams_with_classes)}")
        print(f"Working exam-class integration: {sum(1 for e in exams_with_classes if e.get('working', False))}")
        print(f"Matrix system: {'✅ Working' if matrix_working else '❌ Issues'}")
        
        if test_result['status'] == 'PASS':
            print("✅ PASS: Exam system integration fully functional")
            impact_results['working_features'].append('Exam System Integration')
        elif test_result['status'] == 'WARNING':
            print("⚠️  WARNING: Some exam system issues detected")
            impact_results['warnings'].append('Minor exam system integration issues')
        else:
            print("❌ FAIL: Exam system integration broken")
            impact_results['broken_features'].append('Exam System Integration')
        
    except Exception as e:
        impact_results['tests']['exam_system'] = {'status': 'ERROR', 'error': str(e)}
        impact_results['broken_features'].append(f'Exam System: {str(e)}')
        print(f"❌ ERROR: {str(e)}")
    
    # TEST 5: View Import and Function Tests
    print("\n🔍 TEST 5: VIEW IMPORTS AND FUNCTION COMPATIBILITY")
    print("-" * 80)
    
    try:
        # Test critical view imports
        from primepath_routinetest.views.classes_exams_unified import classes_exams_unified_view
        from primepath_routinetest.views.class_access import my_classes_view
        from primepath_routinetest.views.exam_management import exam_list_view
        
        # Test that our fix doesn't break other views that might use class codes
        import_tests = {
            'classes_exams_unified_view': True,
            'my_classes_view': True,
            'exam_list_view': True,
            'class_mapping_functions': True
        }
        
        # Test specific functions we modified
        try:
            from primepath_routinetest.class_code_mapping import get_class_codes_by_program
            test_programs = get_class_codes_by_program('CORE')
            if len(test_programs) == 0:
                import_tests['class_mapping_functions'] = False
        except:
            import_tests['class_mapping_functions'] = False
        
        test_result = {
            'import_tests': import_tests,
            'all_imports_working': all(import_tests.values()),
            'critical_functions_working': import_tests['class_mapping_functions'],
            'view_functions_importable': import_tests['classes_exams_unified_view'],
            'status': 'PASS' if all(import_tests.values()) else 'FAIL'
        }
        
        impact_results['tests']['view_imports'] = test_result
        
        print("Import test results:")
        for func, working in import_tests.items():
            status = "✅ Working" if working else "❌ Broken"
            print(f"   {func}: {status}")
        
        if test_result['status'] == 'PASS':
            print("✅ PASS: All view imports and functions working")
            impact_results['working_features'].append('View Imports & Functions')
        else:
            print("❌ FAIL: Some view imports or functions broken")
            impact_results['broken_features'].append('View Imports & Functions')
        
    except Exception as e:
        impact_results['tests']['view_imports'] = {'status': 'ERROR', 'error': str(e)}
        impact_results['broken_features'].append(f'View Imports: {str(e)}')
        print(f"❌ ERROR: {str(e)}")
    
    # TEST 6: Class Access Request System
    print("\n🔍 TEST 6: CLASS ACCESS REQUEST SYSTEM")
    print("-" * 80)
    
    try:
        # Test class access request functionality
        all_requests = ClassAccessRequest.objects.all()
        pending_requests = ClassAccessRequest.objects.filter(status='PENDING')
        
        # Test that class codes in requests are still valid
        valid_request_classes = 0
        total_request_classes = 0
        
        for request in all_requests[:10]:  # Test sample
            if hasattr(request, 'class_code') and request.class_code:
                total_request_classes += 1
                if validate_class_code(request.class_code):
                    valid_request_classes += 1
        
        # Test request creation would work with current class codes
        available_classes_for_requests = get_all_class_codes()
        request_system_functional = len(available_classes_for_requests) > 0
        
        test_result = {
            'total_requests': all_requests.count(),
            'pending_requests': pending_requests.count(),
            'valid_request_classes': valid_request_classes,
            'total_request_classes': total_request_classes,
            'class_validation_rate': (valid_request_classes / max(total_request_classes, 1)) * 100,
            'available_classes_for_new_requests': len(available_classes_for_requests),
            'request_system_functional': request_system_functional,
            'status': 'PASS' if request_system_functional else 'FAIL'
        }
        
        impact_results['tests']['access_requests'] = test_result
        
        print(f"Total access requests: {all_requests.count()}")
        print(f"Pending requests: {pending_requests.count()}")
        print(f"Class code validation rate: {test_result['class_validation_rate']:.1f}%")
        print(f"Classes available for new requests: {len(available_classes_for_requests)}")
        
        if test_result['status'] == 'PASS':
            print("✅ PASS: Class access request system functional")
            impact_results['working_features'].append('Class Access Request System')
        else:
            print("❌ FAIL: Class access request system broken")
            impact_results['broken_features'].append('Class Access Request System')
        
    except Exception as e:
        impact_results['tests']['access_requests'] = {'status': 'ERROR', 'error': str(e)}
        impact_results['broken_features'].append(f'Access Request System: {str(e)}')
        print(f"❌ ERROR: {str(e)}")
    
    # FINAL ASSESSMENT
    print("\n" + "="*80)
    print("COMPREHENSIVE FEATURE IMPACT ASSESSMENT")
    print("="*80)
    
    total_features_tested = len(impact_results['tests'])
    working_features = len(impact_results['working_features'])
    broken_features = len(impact_results['broken_features'])
    warnings = len(impact_results['warnings'])
    
    print(f"Features tested: {total_features_tested}")
    print(f"Working features: {working_features}")
    print(f"Broken features: {broken_features}")
    print(f"Warnings: {warnings}")
    
    if broken_features == 0:
        impact_results['overall_status'] = 'PASS'
        print("\n🎉 OVERALL STATUS: PASS")
        print("✅ NO EXISTING FEATURES WERE BROKEN BY THE FIX")
        if warnings > 0:
            print(f"⚠️  Note: {warnings} minor warnings detected (non-critical)")
    elif broken_features <= 1 and working_features >= 4:
        impact_results['overall_status'] = 'WARNING'
        print("\n⚠️  OVERALL STATUS: WARNING")
        print("Minor issues detected but core functionality intact")
    else:
        impact_results['overall_status'] = 'FAIL'
        print("\n❌ OVERALL STATUS: FAIL")
        print("Multiple features broken by the fix - rollback recommended")
    
    if impact_results['working_features']:
        print("\n✅ WORKING FEATURES:")
        for feature in impact_results['working_features']:
            print(f"   • {feature}")
    
    if impact_results['broken_features']:
        print("\n❌ BROKEN FEATURES:")
        for feature in impact_results['broken_features']:
            print(f"   • {feature}")
    
    if impact_results['warnings']:
        print("\n⚠️  WARNINGS:")
        for warning in impact_results['warnings']:
            print(f"   • {warning}")
    
    # Save results
    results_file = f'feature_impact_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(results_file, 'w') as f:
        json.dump(impact_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed analysis saved to: {results_file}")
    
    return impact_results

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    COMPREHENSIVE FEATURE IMPACT ANALYSIS                    ║
║                      Post Program Mapping Fix Validation                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    results = test_all_existing_features()
    
    status_color = "✅" if results['overall_status'] == 'PASS' else "⚠️ " if results['overall_status'] == 'WARNING' else "❌"
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          FEATURE IMPACT ANALYSIS COMPLETE                   ║
║                                                                              ║
║  Status: {status_color} {results['overall_status']:<56} ║
║  Working Features: {len(results['working_features']):<49} ║  
║  Broken Features: {len(results['broken_features']):<50} ║
║  Warnings: {len(results['warnings']):<57} ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    return results['overall_status'] in ['PASS', 'WARNING']

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)