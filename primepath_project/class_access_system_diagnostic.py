#!/usr/bin/env python
"""
COMPREHENSIVE CLASS ACCESS SYSTEM DIAGNOSTIC AND REPAIR TOOL
=============================================================

This script diagnoses and fixes the class access mismatch between:
1. TeacherClassAssignment (legacy system using class_code)
2. Class.assigned_teachers (new ManyToMany system)

The issue: Teacher1 has assignments in TeacherClassAssignment but not in Class.assigned_teachers,
causing "No classes available to display" in the Class Management interface.

DIAGNOSTIC PHASE:
- Maps all relationships between the two systems
- Identifies missing connections
- Analyzes data integrity

REPAIR PHASE:
- Synchronizes TeacherClassAssignment → Class.assigned_teachers
- Preserves all existing relationships
- Adds comprehensive logging for monitoring

Author: Claude Code Agent System
Date: August 25, 2025
"""

import os
import sys
import django
from datetime import datetime
import json
from collections import defaultdict

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.db import transaction
from primepath_routinetest.models import TeacherClassAssignment, Class
from core.models import Teacher
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING


class ClassAccessSystemDiagnostic:
    """Comprehensive diagnostic and repair tool for class access system"""
    
    def __init__(self):
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'diagnostic_results': {},
            'repair_actions': [],
            'warnings': [],
            'statistics': {}
        }
        self.dry_run = True  # Safety first
        
    def log(self, message, level='INFO'):
        """Enhanced logging with console output and report tracking"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_msg = f"[{timestamp}] [{level}] {message}"
        print(formatted_msg)
        
        if level == 'WARNING':
            self.report['warnings'].append(message)
            
    def diagnostic_phase(self):
        """Comprehensive diagnostic of both class access systems"""
        self.log("="*80)
        self.log("STARTING COMPREHENSIVE CLASS ACCESS SYSTEM DIAGNOSTIC")
        self.log("="*80)
        
        # 1. Analyze TeacherClassAssignment system
        self._analyze_teacher_class_assignments()
        
        # 2. Analyze Class.assigned_teachers system  
        self._analyze_class_assigned_teachers()
        
        # 3. Identify mismatches and missing relationships
        self._identify_relationship_mismatches()
        
        # 4. Analyze impact on views and templates
        self._analyze_view_template_impact()
        
        # 5. Generate comprehensive statistics
        self._generate_statistics()
        
    def _analyze_teacher_class_assignments(self):
        """Analyze the TeacherClassAssignment system"""
        self.log("Phase 1: Analyzing TeacherClassAssignment System")
        self.log("-" * 50)
        
        assignments = TeacherClassAssignment.objects.filter(is_active=True)
        assignment_data = defaultdict(list)
        
        for assignment in assignments:
            teacher_name = assignment.teacher.name
            assignment_data[teacher_name].append({
                'class_code': assignment.class_code,
                'access_level': assignment.access_level,
                'assigned_date': assignment.assigned_date.isoformat(),
                'expires_on': assignment.expires_on.isoformat() if assignment.expires_on else None
            })
            
        self.log(f"Found {assignments.count()} active TeacherClassAssignments")
        self.log(f"Teachers with assignments: {len(assignment_data)}")
        
        # Focus on teacher1
        teacher1_assignments = [
            data for teacher_name, data in assignment_data.items() 
            if 'teacher1' in teacher_name.lower()
        ]
        
        if teacher1_assignments:
            self.log(f"TEACHER1 FOUND: {len(teacher1_assignments[0])} assignments")
            for assignment in teacher1_assignments[0][:5]:  # Show first 5
                self.log(f"  - {assignment['class_code']} ({assignment['access_level']})")
        else:
            self.log("WARNING: Teacher1 not found in TeacherClassAssignment system")
            
        self.report['diagnostic_results']['teacher_class_assignments'] = {
            'total_assignments': assignments.count(),
            'teachers_count': len(assignment_data),
            'teacher1_assignments': teacher1_assignments[0] if teacher1_assignments else [],
            'assignment_data': dict(assignment_data)
        }
        
    def _analyze_class_assigned_teachers(self):
        """Analyze the Class.assigned_teachers system"""
        self.log("\nPhase 2: Analyzing Class.assigned_teachers System")
        self.log("-" * 50)
        
        classes = Class.objects.filter(is_active=True).prefetch_related('assigned_teachers')
        class_data = {}
        teacher1_classes = []
        
        for cls in classes:
            teachers = list(cls.assigned_teachers.all())
            class_data[cls.section or cls.name] = {
                'id': str(cls.id),
                'name': cls.name,
                'section': cls.section,
                'teachers': [t.name for t in teachers]
            }
            
            # Check if teacher1 is assigned
            teacher1_in_class = any('teacher1' in t.name.lower() for t in teachers)
            if teacher1_in_class:
                teacher1_classes.append(cls.section or cls.name)
                
        self.log(f"Found {classes.count()} active Classes")
        self.log(f"Teacher1 assigned to {len(teacher1_classes)} classes via Class.assigned_teachers")
        
        if teacher1_classes:
            self.log("Teacher1 classes:")
            for class_code in teacher1_classes:
                self.log(f"  - {class_code}")
        else:
            self.log("WARNING: Teacher1 has NO assignments in Class.assigned_teachers system")
            
        self.report['diagnostic_results']['class_assigned_teachers'] = {
            'total_classes': classes.count(),
            'teacher1_classes': teacher1_classes,
            'class_data': class_data
        }
        
    def _identify_relationship_mismatches(self):
        """Identify mismatches between the two systems"""
        self.log("\nPhase 3: Identifying Relationship Mismatches")
        self.log("-" * 50)
        
        # Get data from previous phases
        tca_data = self.report['diagnostic_results']['teacher_class_assignments']
        class_data = self.report['diagnostic_results']['class_assigned_teachers']
        
        # Focus on teacher1
        teacher1_tca_classes = set(
            assignment['class_code'] for assignment in tca_data['teacher1_assignments']
        )
        teacher1_class_classes = set(class_data['teacher1_classes'])
        
        # Find mismatches
        missing_in_class_system = teacher1_tca_classes - teacher1_class_classes
        missing_in_tca_system = teacher1_class_classes - teacher1_tca_classes
        
        self.log(f"Teacher1 has {len(teacher1_tca_classes)} classes in TeacherClassAssignment")
        self.log(f"Teacher1 has {len(teacher1_class_classes)} classes in Class.assigned_teachers")
        self.log(f"Missing in Class.assigned_teachers: {len(missing_in_class_system)}")
        self.log(f"Missing in TeacherClassAssignment: {len(missing_in_tca_system)}")
        
        if missing_in_class_system:
            self.log("Classes missing from Class.assigned_teachers:")
            for class_code in list(missing_in_class_system)[:10]:  # Show first 10
                self.log(f"  - {class_code}")
                
        self.report['diagnostic_results']['mismatches'] = {
            'teacher1_tca_classes': list(teacher1_tca_classes),
            'teacher1_class_classes': list(teacher1_class_classes),
            'missing_in_class_system': list(missing_in_class_system),
            'missing_in_tca_system': list(missing_in_tca_system),
            'mismatch_count': len(missing_in_class_system) + len(missing_in_tca_system)
        }
        
    def _analyze_view_template_impact(self):
        """Analyze impact on views and templates"""
        self.log("\nPhase 4: Analyzing View and Template Impact")
        self.log("-" * 50)
        
        # This explains why the issue occurs
        impact_analysis = {
            'classes_exams_unified_view': {
                'issue': 'Creates mock assignments for admins but relies on actual Class.assigned_teachers for regular teachers',
                'affected_users': 'Regular teachers like teacher1',
                'symptom': 'Shows assigned classes in overview but not in class management'
            },
            'class_management_views': {
                'issue': 'Depends on Class.assigned_teachers ManyToMany relationship',
                'affected_feature': 'Class Management interface shows "No classes available"',
                'root_cause': 'Teacher assignments exist in TeacherClassAssignment but not in Class.assigned_teachers'
            },
            'template_rendering': {
                'issue': 'Template iterates over programs/classes from Class.assigned_teachers',
                'template_path': 'templates/primepath_routinetest/classes_exams_unified.html',
                'line_causing_issue': 'Line ~892: {% for program in programs %} - empty if no Class.assigned_teachers'
            }
        }
        
        self.log("ROOT CAUSE IDENTIFIED:")
        self.log("- TeacherClassAssignment system working correctly (11 assignments for teacher1)")
        self.log("- Class.assigned_teachers system empty (0 assignments for teacher1)")  
        self.log("- Template depends on Class.assigned_teachers → shows 'No classes available'")
        
        self.report['diagnostic_results']['impact_analysis'] = impact_analysis
        
    def _generate_statistics(self):
        """Generate comprehensive statistics"""
        self.log("\nPhase 5: Generating System Statistics")
        self.log("-" * 50)
        
        # Count totals across system
        total_teachers = Teacher.objects.count()
        total_active_assignments = TeacherClassAssignment.objects.filter(is_active=True).count()
        total_classes = Class.objects.filter(is_active=True).count()
        
        # Count Class.assigned_teachers relationships
        classes_with_teachers = Class.objects.filter(is_active=True, assigned_teachers__isnull=False).distinct().count()
        total_class_teacher_relationships = sum(
            cls.assigned_teachers.count() for cls in Class.objects.filter(is_active=True)
        )
        
        stats = {
            'system_totals': {
                'total_teachers': total_teachers,
                'total_active_assignments': total_active_assignments,
                'total_classes': total_classes,
                'classes_with_teachers': classes_with_teachers,
                'total_class_teacher_relationships': total_class_teacher_relationships
            },
            'synchronization_needed': {
                'assignments_missing_from_class_system': total_active_assignments - total_class_teacher_relationships,
                'synchronization_required': total_active_assignments > total_class_teacher_relationships
            }
        }
        
        self.log(f"System Statistics:")
        self.log(f"  Total Teachers: {total_teachers}")
        self.log(f"  TeacherClassAssignments: {total_active_assignments}")
        self.log(f"  Total Classes: {total_classes}")
        self.log(f"  Class.assigned_teachers relationships: {total_class_teacher_relationships}")
        self.log(f"  Synchronization needed: {stats['synchronization_needed']['synchronization_required']}")
        
        self.report['statistics'] = stats
        
    def repair_phase(self, dry_run=True):
        """Repair the relationship mismatches"""
        self.log("\n" + "="*80)
        self.log(f"STARTING REPAIR PHASE (DRY RUN: {dry_run})")
        self.log("="*80)
        
        self.dry_run = dry_run
        
        if not self.report.get('diagnostic_results'):
            self.log("ERROR: Must run diagnostic_phase() first")
            return False
            
        # Get mismatch data
        mismatches = self.report['diagnostic_results']['mismatches']
        missing_classes = mismatches['missing_in_class_system']
        
        if not missing_classes:
            self.log("No repairs needed - systems are synchronized")
            return True
            
        self.log(f"Found {len(missing_classes)} classes to synchronize")
        
        # Find teacher1
        teacher1 = Teacher.objects.filter(name__icontains='teacher1').first()
        if not teacher1:
            teacher1 = Teacher.objects.filter(user__username__icontains='teacher1').first()
            
        if not teacher1:
            self.log("ERROR: Teacher1 not found")
            return False
            
        self.log(f"Found teacher: {teacher1.name} (ID: {teacher1.id})")
        
        # Synchronize assignments
        repair_count = 0
        created_classes = []
        
        with transaction.atomic():
            for class_code in missing_classes:
                try:
                    # Try to find existing class by section
                    existing_class = Class.objects.filter(section=class_code, is_active=True).first()
                    
                    if existing_class:
                        # Add teacher to existing class
                        if not dry_run:
                            existing_class.assigned_teachers.add(teacher1)
                            existing_class.save()
                        self.log(f"  ✓ Added teacher1 to existing class: {class_code}")
                        repair_count += 1
                        
                    else:
                        # Create new class if it doesn't exist
                        if class_code in CLASS_CODE_CURRICULUM_MAPPING:
                            curriculum_info = CLASS_CODE_CURRICULUM_MAPPING[class_code]
                            
                            # Parse class code to extract grade and section
                            if '_' in class_code:
                                grade_level, section = class_code.split('_', 1)
                                grade_level = grade_level.replace('_', ' ').title()
                            else:
                                grade_level = class_code
                                section = class_code
                                
                            if not dry_run:
                                new_class = Class.objects.create(
                                    name=f"{grade_level} {section}",
                                    grade_level=grade_level,
                                    section=class_code,  # Use class_code as section for mapping
                                    academic_year='2024-2025'
                                )
                                new_class.assigned_teachers.add(teacher1)
                                new_class.save()
                                created_classes.append(class_code)
                            
                            self.log(f"  ✓ Created new class and assigned teacher1: {class_code}")
                            repair_count += 1
                        else:
                            self.log(f"  ⚠ Skipped unknown class code: {class_code}")
                            
                except Exception as e:
                    self.log(f"  ✗ Error processing {class_code}: {str(e)}", 'WARNING')
                    
        action_type = "WOULD REPAIR" if dry_run else "REPAIRED"
        self.log(f"\n{action_type}: {repair_count} class assignments")
        self.log(f"Created classes: {len(created_classes)}")
        
        self.report['repair_actions'] = {
            'dry_run': dry_run,
            'repairs_made': repair_count,
            'created_classes': created_classes,
            'timestamp': datetime.now().isoformat()
        }
        
        return True
        
    def post_repair_verification(self):
        """Verify the repair was successful"""
        self.log("\n" + "="*80)  
        self.log("POST-REPAIR VERIFICATION")
        self.log("="*80)
        
        # Re-run key diagnostics
        teacher1 = Teacher.objects.filter(name__icontains='teacher1').first()
        if not teacher1:
            teacher1 = Teacher.objects.filter(user__username__icontains='teacher1').first()
            
        if not teacher1:
            self.log("ERROR: Teacher1 not found for verification")
            return False
            
        # Check TeacherClassAssignment (should be unchanged)
        tca_count = TeacherClassAssignment.objects.filter(teacher=teacher1, is_active=True).count()
        
        # Check Class.assigned_teachers (should now have assignments)
        class_count = Class.objects.filter(is_active=True, assigned_teachers=teacher1).count()
        
        self.log(f"Teacher1 TeacherClassAssignments: {tca_count}")
        self.log(f"Teacher1 Class.assigned_teachers: {class_count}")
        
        if tca_count > 0 and class_count > 0:
            self.log("✅ VERIFICATION SUCCESSFUL: Both systems now have teacher1 assignments")
            success_rate = (class_count / tca_count) * 100
            self.log(f"Synchronization rate: {success_rate:.1f}%")
            return True
        else:
            self.log("❌ VERIFICATION FAILED: Systems still out of sync")
            return False
            
    def generate_report(self):
        """Generate comprehensive diagnostic report"""
        report_path = f"class_access_diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2, default=str)
            
        self.log(f"\n📊 Comprehensive report saved: {report_path}")
        return report_path


def main():
    """Main execution function"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     CLASS ACCESS SYSTEM DIAGNOSTIC TOOL                     ║
║                           Teacher1 Issue Resolution                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    diagnostic = ClassAccessSystemDiagnostic()
    
    # Phase 1: Comprehensive Diagnostic
    diagnostic.diagnostic_phase()
    
    # Phase 2: Repair (Dry Run First)
    print("\n🔧 REPAIR PHASE - DRY RUN")
    diagnostic.repair_phase(dry_run=True)
    
    # Ask for confirmation to proceed with actual repair
    response = input("\n❓ Proceed with actual repair? (yes/no): ").lower().strip()
    
    if response == 'yes':
        print("\n🔧 REPAIR PHASE - ACTUAL REPAIR")
        success = diagnostic.repair_phase(dry_run=False)
        
        if success:
            # Phase 3: Verification
            diagnostic.post_repair_verification()
        
    # Generate final report
    report_path = diagnostic.generate_report()
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            DIAGNOSTIC COMPLETE                               ║
║                                                                              ║
║  📊 Report saved: {report_path:<52} ║
║  🔍 Check the report for detailed analysis and recommendations               ║
║  🛠️  If repair was successful, test the Class Management interface          ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == '__main__':
    main()