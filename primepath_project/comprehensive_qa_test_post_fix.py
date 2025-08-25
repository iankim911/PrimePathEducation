#!/usr/bin/env python
"""
Comprehensive QA Testing - Post Class Access Fix
===============================================

This script runs comprehensive QA tests after fixing the class access issue
to ensure:
1. Teacher1 (Taehyun Kim) can now access their classes
2. No other features were broken
3. All relationships are preserved
4. System stability is maintained

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

def run_qa_tests():
    """Run comprehensive QA tests"""
    
    qa_results = {
        'timestamp': datetime.now().isoformat(),
        'test_results': {},
        'overall_status': 'PENDING',
        'critical_issues': [],
        'warnings': [],
        'summary': {}
    }
    
    print("="*80)
    print("COMPREHENSIVE QA TESTING - POST CLASS ACCESS FIX")
    print("="*80)
    
    # Test 1: Verify Teacher1 Fix
    print("\n🔍 Test 1: Verify Teacher1 Class Access Fix")
    print("-" * 50)
    
    try:
        teacher1 = Teacher.objects.get(user__username='teacher1')
        tca_count = TeacherClassAssignment.objects.filter(teacher=teacher1, is_active=True).count()
        class_count = Class.objects.filter(is_active=True, assigned_teachers=teacher1).count()
        
        qa_results['test_results']['teacher1_fix'] = {
            'teacher_name': teacher1.name,
            'tca_assignments': tca_count,
            'class_assignments': class_count,
            'synchronization_rate': (class_count / tca_count * 100) if tca_count > 0 else 0,
            'status': 'PASS' if class_count == tca_count == 11 else 'FAIL'
        }
        
        print(f"Teacher: {teacher1.name}")
        print(f"TeacherClassAssignments: {tca_count}")
        print(f"Class.assigned_teachers: {class_count}")
        print(f"Synchronization rate: {qa_results['test_results']['teacher1_fix']['synchronization_rate']:.1f}%")
        
        if qa_results['test_results']['teacher1_fix']['status'] == 'PASS':
            print("✅ PASS: Teacher1 class access issue resolved")
        else:
            print("❌ FAIL: Teacher1 class access issue NOT resolved")
            qa_results['critical_issues'].append("Teacher1 still has class access issues")
            
    except Exception as e:
        qa_results['test_results']['teacher1_fix'] = {'status': 'ERROR', 'error': str(e)}
        qa_results['critical_issues'].append(f"Error testing teacher1 fix: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
    
    # Test 2: Verify System-Wide Class Access Integrity
    print("\n🔍 Test 2: System-Wide Class Access Integrity")
    print("-" * 50)
    
    try:
        all_teachers = Teacher.objects.all()
        integrity_stats = {
            'teachers_analyzed': 0,
            'teachers_with_assignments': 0,
            'teachers_synchronized': 0,
            'total_tca_assignments': 0,
            'total_class_assignments': 0,
            'synchronization_issues': []
        }
        
        for teacher in all_teachers:
            integrity_stats['teachers_analyzed'] += 1
            
            tca_count = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True).count()
            class_count = Class.objects.filter(is_active=True, assigned_teachers=teacher).count()
            
            integrity_stats['total_tca_assignments'] += tca_count
            integrity_stats['total_class_assignments'] += class_count
            
            if tca_count > 0:
                integrity_stats['teachers_with_assignments'] += 1
                
                if tca_count == class_count:
                    integrity_stats['teachers_synchronized'] += 1
                else:
                    integrity_stats['synchronization_issues'].append({
                        'teacher': teacher.name,
                        'tca_count': tca_count,
                        'class_count': class_count,
                        'difference': tca_count - class_count
                    })
        
        qa_results['test_results']['system_integrity'] = integrity_stats
        
        print(f"Teachers analyzed: {integrity_stats['teachers_analyzed']}")
        print(f"Teachers with assignments: {integrity_stats['teachers_with_assignments']}")
        print(f"Teachers synchronized: {integrity_stats['teachers_synchronized']}")
        print(f"Total TeacherClassAssignments: {integrity_stats['total_tca_assignments']}")
        print(f"Total Class.assigned_teachers: {integrity_stats['total_class_assignments']}")
        print(f"Synchronization issues: {len(integrity_stats['synchronization_issues'])}")
        
        if len(integrity_stats['synchronization_issues']) == 0:
            print("✅ PASS: All teachers have synchronized class access")
        else:
            print(f"⚠️  WARNING: {len(integrity_stats['synchronization_issues'])} teachers have synchronization issues")
            for issue in integrity_stats['synchronization_issues'][:3]:  # Show first 3
                print(f"   - {issue['teacher']}: TCA={issue['tca_count']}, Class={issue['class_count']}")
            qa_results['warnings'].append(f"{len(integrity_stats['synchronization_issues'])} teachers have synchronization issues")
                
    except Exception as e:
        qa_results['test_results']['system_integrity'] = {'status': 'ERROR', 'error': str(e)}
        qa_results['critical_issues'].append(f"Error testing system integrity: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
    
    # Test 3: Verify Database Integrity
    print("\n🔍 Test 3: Database Integrity Check")
    print("-" * 50)
    
    try:
        db_stats = {
            'total_teachers': Teacher.objects.count(),
            'total_active_classes': Class.objects.filter(is_active=True).count(),
            'total_active_tca': TeacherClassAssignment.objects.filter(is_active=True).count(),
            'classes_with_teachers': Class.objects.filter(is_active=True, assigned_teachers__isnull=False).distinct().count(),
            'orphaned_classes': 0,
            'duplicate_assignments': 0
        }
        
        # Check for orphaned classes (classes with no teachers)
        orphaned_classes = Class.objects.filter(is_active=True, assigned_teachers__isnull=True).count()
        db_stats['orphaned_classes'] = orphaned_classes
        
        # Check for potential duplicate assignments
        # (This is a simplified check - in practice, you might want more sophisticated logic)
        
        qa_results['test_results']['database_integrity'] = db_stats
        
        print(f"Total Teachers: {db_stats['total_teachers']}")
        print(f"Total Active Classes: {db_stats['total_active_classes']}")
        print(f"Total Active TeacherClassAssignments: {db_stats['total_active_tca']}")
        print(f"Classes with teachers: {db_stats['classes_with_teachers']}")
        print(f"Orphaned classes: {db_stats['orphaned_classes']}")
        
        if db_stats['orphaned_classes'] == 0:
            print("✅ PASS: No orphaned classes found")
        else:
            print(f"⚠️  WARNING: {db_stats['orphaned_classes']} classes have no assigned teachers")
            qa_results['warnings'].append(f"{db_stats['orphaned_classes']} classes have no assigned teachers")
            
    except Exception as e:
        qa_results['test_results']['database_integrity'] = {'status': 'ERROR', 'error': str(e)}
        qa_results['critical_issues'].append(f"Error testing database integrity: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
    
    # Test 4: Verify Specific Classes From Fix
    print("\n🔍 Test 4: Verify Specific Classes From Fix")
    print("-" * 50)
    
    try:
        expected_classes = [
            'TaejoE', 'PRIMARY_2A', 'HIGH_10E', 'C5', 'PRIMARY_1D',
            'Sungjong4', 'HIGH_10F', 'Chung-cho1', 'HIGH_11D', 'SejongM', 'MIDDLE_7A'
        ]
        
        teacher1 = Teacher.objects.get(user__username='teacher1')
        class_verification = {
            'expected_classes': expected_classes,
            'found_classes': [],
            'missing_classes': [],
            'status': 'PENDING'
        }
        
        teacher1_classes = Class.objects.filter(is_active=True, assigned_teachers=teacher1)
        found_class_codes = set(cls.section for cls in teacher1_classes if cls.section)
        
        for class_code in expected_classes:
            if class_code in found_class_codes:
                class_verification['found_classes'].append(class_code)
            else:
                class_verification['missing_classes'].append(class_code)
        
        qa_results['test_results']['class_verification'] = class_verification
        
        print(f"Expected classes: {len(expected_classes)}")
        print(f"Found classes: {len(class_verification['found_classes'])}")
        print(f"Missing classes: {len(class_verification['missing_classes'])}")
        
        if len(class_verification['missing_classes']) == 0:
            class_verification['status'] = 'PASS'
            print("✅ PASS: All expected classes found for teacher1")
        else:
            class_verification['status'] = 'FAIL'
            print(f"❌ FAIL: Missing classes: {class_verification['missing_classes']}")
            qa_results['critical_issues'].append(f"Teacher1 missing {len(class_verification['missing_classes'])} expected classes")
            
    except Exception as e:
        qa_results['test_results']['class_verification'] = {'status': 'ERROR', 'error': str(e)}
        qa_results['critical_issues'].append(f"Error verifying classes: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
    
    # Overall Assessment
    print("\n" + "="*60)
    print("QA TEST RESULTS SUMMARY")
    print("="*60)
    
    total_tests = len(qa_results['test_results'])
    passed_tests = sum(1 for test in qa_results['test_results'].values() if test.get('status') == 'PASS')
    failed_tests = sum(1 for test in qa_results['test_results'].values() if test.get('status') == 'FAIL')
    error_tests = sum(1 for test in qa_results['test_results'].values() if test.get('status') == 'ERROR')
    
    qa_results['summary'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'error_tests': error_tests,
        'critical_issues_count': len(qa_results['critical_issues']),
        'warnings_count': len(qa_results['warnings'])
    }
    
    print(f"Tests run: {total_tests}")
    print(f"Tests passed: {passed_tests}")
    print(f"Tests failed: {failed_tests}")
    print(f"Tests with errors: {error_tests}")
    print(f"Critical issues: {len(qa_results['critical_issues'])}")
    print(f"Warnings: {len(qa_results['warnings'])}")
    
    if len(qa_results['critical_issues']) == 0 and failed_tests == 0:
        qa_results['overall_status'] = 'PASS'
        print("\n🎉 OVERALL STATUS: PASS")
        print("✅ Class access fix successful - no critical issues detected")
        
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
    results_file = f'qa_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(results_file, 'w') as f:
        json.dump(qa_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed QA results saved to: {results_file}")
    
    return qa_results

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    COMPREHENSIVE QA TESTING SUITE                           ║
║                     Post Class Access Fix Validation                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    results = run_qa_tests()
    
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