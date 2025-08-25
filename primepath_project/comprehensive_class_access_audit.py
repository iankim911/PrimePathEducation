#!/usr/bin/env python
"""
Comprehensive Class Access Audit - System-Wide Analysis
======================================================

This script performs a complete audit of ALL teacher accounts to identify
class access synchronization issues between TeacherClassAssignment and 
Class.assigned_teachers systems.

Critical Analysis Points:
1. Identify ALL teachers with synchronization gaps
2. Map the exact scope of data inconsistencies
3. Analyze patterns to find root cause
4. Generate comprehensive fix plan
5. Preserve all existing relationships

Author: Claude Code Agent System
Date: August 25, 2025
Purpose: System-wide class access fix preparation
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
from primepath_routinetest.models import TeacherClassAssignment, Class

def comprehensive_audit():
    """Perform complete system audit of class access synchronization"""
    
    audit_results = {
        'timestamp': datetime.now().isoformat(),
        'audit_summary': {
            'total_teachers': 0,
            'teachers_with_tca': 0,
            'teachers_with_class_assignments': 0,
            'teachers_synchronized': 0,
            'teachers_with_gaps': 0,
            'critical_issues': []
        },
        'teacher_analysis': {},
        'synchronization_gaps': [],
        'class_analysis': {},
        'system_integrity': {
            'total_tca_records': 0,
            'total_class_assignments': 0,
            'orphaned_classes': 0,
            'duplicate_assignments': 0
        },
        'root_cause_indicators': {},
        'recommended_actions': []
    }
    
    print("="*100)
    print("COMPREHENSIVE CLASS ACCESS AUDIT - SYSTEM-WIDE ANALYSIS")
    print("="*100)
    print(f"Audit started: {audit_results['timestamp']}")
    print()
    
    # Phase 1: Teacher-by-Teacher Analysis
    print("📋 PHASE 1: TEACHER-BY-TEACHER SYNCHRONIZATION ANALYSIS")
    print("-" * 80)
    
    all_teachers = Teacher.objects.all().order_by('name')
    audit_results['audit_summary']['total_teachers'] = all_teachers.count()
    
    for teacher in all_teachers:
        print(f"\n🔍 Analyzing: {teacher.name} (User: {teacher.user.username})")
        
        # Get TeacherClassAssignment data
        tca_assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
        tca_count = tca_assignments.count()
        tca_class_codes = set(tca_assignments.values_list('class_code', flat=True))
        
        # Get Class.assigned_teachers data
        class_assignments = Class.objects.filter(is_active=True, assigned_teachers=teacher)
        class_count = class_assignments.count()
        class_sections = set(class_assignments.values_list('section', flat=True))
        
        # Calculate synchronization metrics
        missing_in_class_system = tca_class_codes - class_sections
        extra_in_class_system = class_sections - tca_class_codes
        synchronization_rate = 0
        
        if tca_count > 0:
            audit_results['audit_summary']['teachers_with_tca'] += 1
            synchronization_rate = (class_count / tca_count) * 100
        
        if class_count > 0:
            audit_results['audit_summary']['teachers_with_class_assignments'] += 1
            
        if tca_count == class_count and len(missing_in_class_system) == 0:
            audit_results['audit_summary']['teachers_synchronized'] += 1
            status = "✅ SYNCHRONIZED"
        else:
            audit_results['audit_summary']['teachers_with_gaps'] += 1
            status = f"❌ GAPS ({len(missing_in_class_system)} missing, {len(extra_in_class_system)} extra)"
        
        # Store detailed teacher analysis
        teacher_data = {
            'name': teacher.name,
            'username': teacher.user.username,
            'teacher_id': teacher.id,
            'tca_count': tca_count,
            'class_count': class_count,
            'synchronization_rate': round(synchronization_rate, 2),
            'tca_class_codes': list(tca_class_codes),
            'class_sections': list(class_sections),
            'missing_in_class_system': list(missing_in_class_system),
            'extra_in_class_system': list(extra_in_class_system),
            'status': status,
            'needs_synchronization': len(missing_in_class_system) > 0 or len(extra_in_class_system) > 0
        }
        
        audit_results['teacher_analysis'][teacher.user.username] = teacher_data
        
        print(f"   TCA Assignments: {tca_count}")
        print(f"   Class Assignments: {class_count}")
        print(f"   Synchronization Rate: {synchronization_rate:.1f}%")
        print(f"   Status: {status}")
        
        if teacher_data['needs_synchronization']:
            gap_data = {
                'teacher': teacher.name,
                'username': teacher.user.username,
                'tca_count': tca_count,
                'class_count': class_count,
                'missing_classes': list(missing_in_class_system),
                'extra_classes': list(extra_in_class_system),
                'priority': 'HIGH' if len(missing_in_class_system) > 5 else 'MEDIUM'
            }
            audit_results['synchronization_gaps'].append(gap_data)
            
            if len(missing_in_class_system) > 0:
                print(f"   ⚠️  Missing in Class system: {missing_in_class_system}")
            if len(extra_in_class_system) > 0:
                print(f"   ⚠️  Extra in Class system: {extra_in_class_system}")
    
    # Phase 2: Class System Analysis
    print("\n\n📋 PHASE 2: CLASS SYSTEM INTEGRITY ANALYSIS")
    print("-" * 80)
    
    total_classes = Class.objects.filter(is_active=True).count()
    classes_with_teachers = Class.objects.filter(is_active=True, assigned_teachers__isnull=False).distinct().count()
    orphaned_classes = total_classes - classes_with_teachers
    
    total_tca = TeacherClassAssignment.objects.filter(is_active=True).count()
    total_class_assignments = 0
    
    # Count total class assignment relationships
    for teacher in all_teachers:
        total_class_assignments += Class.objects.filter(is_active=True, assigned_teachers=teacher).count()
    
    audit_results['system_integrity'] = {
        'total_active_classes': total_classes,
        'classes_with_teachers': classes_with_teachers,
        'orphaned_classes': orphaned_classes,
        'total_tca_records': total_tca,
        'total_class_assignments': total_class_assignments,
        'tca_to_class_ratio': round((total_class_assignments / total_tca * 100), 2) if total_tca > 0 else 0
    }
    
    print(f"Total Active Classes: {total_classes}")
    print(f"Classes with Teachers: {classes_with_teachers}")
    print(f"Orphaned Classes: {orphaned_classes}")
    print(f"Total TCA Records: {total_tca}")
    print(f"Total Class Assignments: {total_class_assignments}")
    print(f"TCA to Class Assignment Ratio: {audit_results['system_integrity']['tca_to_class_ratio']}%")
    
    # Phase 3: Root Cause Analysis
    print("\n\n📋 PHASE 3: ROOT CAUSE PATTERN ANALYSIS")
    print("-" * 80)
    
    # Analyze patterns in gaps
    gap_patterns = defaultdict(int)
    affected_usernames = []
    missing_class_frequency = defaultdict(int)
    
    for gap in audit_results['synchronization_gaps']:
        affected_usernames.append(gap['username'])
        gap_patterns[f"{gap['tca_count']}_tca_vs_{gap['class_count']}_class"] += 1
        
        for missing_class in gap['missing_classes']:
            missing_class_frequency[missing_class] += 1
    
    audit_results['root_cause_indicators'] = {
        'affected_teachers_count': len(affected_usernames),
        'affected_teachers': affected_usernames,
        'gap_patterns': dict(gap_patterns),
        'most_affected_classes': dict(sorted(missing_class_frequency.items(), key=lambda x: x[1], reverse=True)[:10]),
        'systematic_issue': len(affected_usernames) > 1,
        'severity': 'CRITICAL' if len(affected_usernames) > 5 else 'HIGH' if len(affected_usernames) > 2 else 'MEDIUM'
    }
    
    print(f"Affected Teachers: {len(affected_usernames)}")
    print(f"Gap Patterns: {dict(gap_patterns)}")
    print(f"Most Frequently Missing Classes: {dict(list(missing_class_frequency.items())[:5])}")
    print(f"Issue Classification: {audit_results['root_cause_indicators']['severity']} - {'SYSTEMATIC' if audit_results['root_cause_indicators']['systematic_issue'] else 'ISOLATED'}")
    
    # Phase 4: Generate Action Plan
    print("\n\n📋 PHASE 4: RECOMMENDED ACTION PLAN")
    print("-" * 80)
    
    high_priority_teachers = [gap['username'] for gap in audit_results['synchronization_gaps'] if gap['priority'] == 'HIGH']
    medium_priority_teachers = [gap['username'] for gap in audit_results['synchronization_gaps'] if gap['priority'] == 'MEDIUM']
    
    actions = []
    if len(high_priority_teachers) > 0:
        actions.append(f"IMMEDIATE: Synchronize {len(high_priority_teachers)} high-priority teachers")
    if len(medium_priority_teachers) > 0:
        actions.append(f"URGENT: Synchronize {len(medium_priority_teachers)} medium-priority teachers")
    if audit_results['system_integrity']['orphaned_classes'] > 0:
        actions.append(f"CLEANUP: Review {audit_results['system_integrity']['orphaned_classes']} orphaned classes")
    if audit_results['root_cause_indicators']['systematic_issue']:
        actions.append("SYSTEMATIC FIX: Identify and fix root cause in assignment creation workflow")
    
    audit_results['recommended_actions'] = actions
    
    for i, action in enumerate(actions, 1):
        print(f"{i}. {action}")
    
    # Phase 5: Critical Issues Assessment
    print("\n\n📋 PHASE 5: CRITICAL ISSUES ASSESSMENT")
    print("-" * 80)
    
    critical_issues = []
    
    if audit_results['audit_summary']['teachers_with_gaps'] > 5:
        critical_issues.append(f"WIDESPREAD SYNC ISSUES: {audit_results['audit_summary']['teachers_with_gaps']} teachers affected")
    
    if audit_results['system_integrity']['tca_to_class_ratio'] < 50:
        critical_issues.append(f"SEVERE DATA INCONSISTENCY: Only {audit_results['system_integrity']['tca_to_class_ratio']}% sync rate")
    
    if len(high_priority_teachers) > 3:
        critical_issues.append(f"MULTIPLE HIGH-PRIORITY FAILURES: {len(high_priority_teachers)} teachers severely affected")
    
    audit_results['audit_summary']['critical_issues'] = critical_issues
    
    if critical_issues:
        print("🚨 CRITICAL ISSUES IDENTIFIED:")
        for issue in critical_issues:
            print(f"   • {issue}")
    else:
        print("✅ No critical issues identified - standard synchronization needed")
    
    # Summary
    print("\n\n" + "="*60)
    print("AUDIT SUMMARY")
    print("="*60)
    print(f"Total Teachers: {audit_results['audit_summary']['total_teachers']}")
    print(f"Teachers with Gaps: {audit_results['audit_summary']['teachers_with_gaps']}")
    print(f"Synchronization Rate: {((audit_results['audit_summary']['teachers_synchronized'] / audit_results['audit_summary']['total_teachers']) * 100):.1f}%")
    print(f"Critical Issues: {len(critical_issues)}")
    print(f"Recommended Actions: {len(actions)}")
    
    # Save results
    results_file = f'class_access_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(results_file, 'w') as f:
        json.dump(audit_results, f, indent=2, default=str)
    
    print(f"\n📄 Complete audit results saved to: {results_file}")
    
    return audit_results

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    COMPREHENSIVE CLASS ACCESS AUDIT                         ║
║                        System-Wide Analysis Tool                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    results = comprehensive_audit()
    
    severity = results['root_cause_indicators']['severity']
    affected_count = len(results['synchronization_gaps'])
    critical_count = len(results['audit_summary']['critical_issues'])
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                             AUDIT COMPLETE                                  ║
║                                                                              ║
║  Severity: {severity:<59} ║
║  Teachers Affected: {affected_count:<52} ║  
║  Critical Issues: {critical_count:<54} ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    return results

if __name__ == '__main__':
    results = main()
    sys.exit(0)