"""
Django Management Command: Synchronize Class Access Systems
===========================================================

This command fixes the class access mismatch between:
1. TeacherClassAssignment (legacy system using class_code)  
2. Class.assigned_teachers (new ManyToMany system)

PROBLEM:
- Teachers have assignments in TeacherClassAssignment but not in Class.assigned_teachers
- This causes "No classes available to display" in Class Management interface
- Systems became out of sync during codebase evolution

SOLUTION:
- Synchronizes TeacherClassAssignment → Class.assigned_teachers
- Creates missing Class records where needed
- Preserves all existing relationships and data
- Provides comprehensive logging and verification

USAGE:
    python manage.py synchronize_class_access --analyze
    python manage.py synchronize_class_access --dry-run
    python manage.py synchronize_class_access --teacher teacher1
    python manage.py synchronize_class_access --execute

Author: Claude Code Agent System  
Date: August 25, 2025
Status: Production Ready
"""

import json
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from collections import defaultdict

from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment, Class
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING


class Command(BaseCommand):
    help = 'Synchronize TeacherClassAssignment and Class.assigned_teachers systems'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Analyze synchronization status without making changes'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes'
        )
        parser.add_argument(
            '--execute',
            action='store_true',
            help='Execute the synchronization (makes actual changes)'
        )
        parser.add_argument(
            '--teacher',
            type=str,
            help='Synchronize specific teacher only'
        )
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Verify synchronization status'
        )

    def handle(self, *args, **options):
        self.sync_log = []
        self.statistics = {
            'created_classes': 0,
            'synchronized_assignments': 0,
            'errors': 0,
            'warnings': 0
        }
        
        self.stdout.write("="*80)
        self.stdout.write(self.style.SUCCESS(
            "CLASS ACCESS SYSTEM SYNCHRONIZATION TOOL"
        ))
        self.stdout.write("="*80)
        
        if options['analyze']:
            self.analyze_synchronization_status()
        elif options['verify']:
            self.verify_synchronization()
        elif options['teacher']:
            self.synchronize_teacher(options['teacher'], not options['execute'])
        elif options['dry_run'] or options['execute']:
            self.synchronize_all_teachers(not options['execute'])
        else:
            self.stdout.write(self.style.WARNING(
                "No action specified. Use --help to see available options."
            ))
            
    def log_action(self, message, level='INFO', teacher_name='', class_code=''):
        """Enhanced logging with structured data"""
        timestamp = timezone.now().strftime('%H:%M:%S')
        
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'teacher_name': teacher_name,
            'class_code': class_code
        }
        
        self.sync_log.append(log_entry)
        
        # Console output with color coding
        if level == 'ERROR':
            self.stdout.write(f"[{timestamp}] {self.style.ERROR('[ERROR]')} {message}")
        elif level == 'WARNING':
            self.stdout.write(f"[{timestamp}] {self.style.WARNING('[WARNING]')} {message}")
            self.statistics['warnings'] += 1
        elif level == 'SUCCESS':
            self.stdout.write(f"[{timestamp}] {self.style.SUCCESS('[SUCCESS]')} {message}")
        else:
            self.stdout.write(f"[{timestamp}] [INFO] {message}")
        
        if level == 'ERROR':
            self.statistics['errors'] += 1
            
    def analyze_synchronization_status(self):
        """Comprehensive analysis of synchronization status"""
        self.log_action("Starting comprehensive synchronization analysis")
        
        teachers = Teacher.objects.all()
        analysis_results = {}
        mismatches_found = 0
        
        for teacher in teachers:
            teacher_analysis = self._analyze_teacher_assignments(teacher)
            analysis_results[teacher.name] = teacher_analysis
            
            if teacher_analysis['mismatch_count'] > 0:
                mismatches_found += 1
        
        # System-wide statistics
        total_tca_assignments = TeacherClassAssignment.objects.filter(is_active=True).count()
        total_class_assignments = sum(
            cls.assigned_teachers.count() 
            for cls in Class.objects.filter(is_active=True)
        )
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("SYNCHRONIZATION STATUS ANALYSIS"))
        self.stdout.write("="*60)
        
        self.stdout.write(f"Total Teachers: {teachers.count()}")
        self.stdout.write(f"TeacherClassAssignments: {total_tca_assignments}")
        self.stdout.write(f"Class.assigned_teachers relationships: {total_class_assignments}")
        self.stdout.write(f"Synchronization gap: {total_tca_assignments - total_class_assignments}")
        self.stdout.write(f"Teachers with mismatches: {mismatches_found}")
        
        if mismatches_found > 0:
            self.stdout.write(f"\n{self.style.WARNING('SYNCHRONIZATION NEEDED')}")
            self.stdout.write("\nTeachers requiring synchronization:")
            
            for teacher_name, analysis in analysis_results.items():
                if analysis['mismatch_count'] > 0:
                    self.stdout.write(f"  • {teacher_name}:")
                    self.stdout.write(f"    - TeacherClassAssignment: {analysis['tca_assignments_count']} classes")
                    self.stdout.write(f"    - Class.assigned_teachers: {analysis['class_assignments_count']} classes")
                    self.stdout.write(f"    - Missing in Class system: {len(analysis['missing_in_class_system'])}")
                    
                    if analysis['missing_in_class_system']:
                        missing_preview = analysis['missing_in_class_system'][:5]
                        self.stdout.write(f"      Classes: {', '.join(missing_preview)}")
                        if len(analysis['missing_in_class_system']) > 5:
                            remaining = len(analysis['missing_in_class_system']) - 5
                            self.stdout.write(f"      ... and {remaining} more")
                    self.stdout.write("")
        else:
            self.log_action("✅ Systems are synchronized - no action needed", 'SUCCESS')
            
    def _analyze_teacher_assignments(self, teacher):
        """Analyze assignments for a specific teacher"""
        
        # Get TeacherClassAssignment data
        tca_assignments = TeacherClassAssignment.objects.filter(
            teacher=teacher, 
            is_active=True
        ).values_list('class_code', flat=True)
        tca_classes = set(tca_assignments)
        
        # Get Class.assigned_teachers data
        class_assignments = Class.objects.filter(
            is_active=True,
            assigned_teachers=teacher
        ).values_list('section', flat=True)
        class_classes = set(code for code in class_assignments if code)
        
        # Find mismatches
        missing_in_class_system = tca_classes - class_classes
        missing_in_tca_system = class_classes - tca_classes
        
        return {
            'tca_assignments_count': len(tca_classes),
            'class_assignments_count': len(class_classes),
            'tca_classes': list(tca_classes),
            'class_classes': list(class_classes),
            'missing_in_class_system': list(missing_in_class_system),
            'missing_in_tca_system': list(missing_in_tca_system),
            'mismatch_count': len(missing_in_class_system) + len(missing_in_tca_system),
            'needs_synchronization': len(missing_in_class_system) > 0
        }
        
    def synchronize_teacher(self, teacher_identifier, dry_run=True):
        """Synchronize assignments for a specific teacher"""
        
        try:
            teacher = Teacher.objects.get(name__icontains=teacher_identifier)
        except Teacher.DoesNotExist:
            try:
                teacher = Teacher.objects.get(user__username__icontains=teacher_identifier)
            except Teacher.DoesNotExist:
                self.log_action(f"Teacher not found: {teacher_identifier}", 'ERROR')
                return False
        
        action_type = "ANALYZING" if dry_run else "SYNCHRONIZING"
        self.log_action(f"{action_type} teacher: {teacher.name}")
        
        analysis = self._analyze_teacher_assignments(teacher)
        
        if not analysis['needs_synchronization']:
            self.log_action("No synchronization needed", 'SUCCESS', teacher.name)
            return True
        
        self.stdout.write(f"\nTeacher: {self.style.SUCCESS(teacher.name)}")
        self.stdout.write(f"TeacherClassAssignments: {analysis['tca_assignments_count']}")
        self.stdout.write(f"Class.assigned_teachers: {analysis['class_assignments_count']}")
        self.stdout.write(f"Classes to synchronize: {len(analysis['missing_in_class_system'])}")
        
        if dry_run:
            self.stdout.write(f"\n{self.style.WARNING('DRY RUN MODE - No changes will be made')}")
        
        missing_classes = analysis['missing_in_class_system']
        changes_made = 0
        classes_created = 0
        
        with transaction.atomic():
            for class_code in missing_classes:
                try:
                    result = self._synchronize_single_assignment(teacher, class_code, dry_run)
                    
                    if result['success']:
                        changes_made += 1
                        if result['class_created']:
                            classes_created += 1
                        
                        action = "WOULD CREATE" if dry_run and result['class_created'] else "WOULD ADD TO" if dry_run else "CREATED" if result['class_created'] else "ADDED TO"
                        self.log_action(
                            f"{action} class: {class_code}",
                            'SUCCESS',
                            teacher.name,
                            class_code
                        )
                        
                        if not dry_run:
                            self.statistics['synchronized_assignments'] += 1
                            if result['class_created']:
                                self.statistics['created_classes'] += 1
                    else:
                        self.log_action(
                            f"Failed to process {class_code}: {result.get('error', 'Unknown error')}",
                            'ERROR',
                            teacher.name,
                            class_code
                        )
                        
                except Exception as e:
                    self.log_action(
                        f"Error processing {class_code}: {str(e)}",
                        'ERROR',
                        teacher.name,
                        class_code
                    )
        
        action_type = "WOULD SYNCHRONIZE" if dry_run else "SYNCHRONIZED"
        self.log_action(
            f"{action_type}: {changes_made} assignments, created {classes_created} classes",
            'SUCCESS',
            teacher.name
        )
        
        return True
        
    def _synchronize_single_assignment(self, teacher, class_code, dry_run):
        """Synchronize a single class assignment"""
        
        # Try to find existing class
        existing_class = Class.objects.filter(
            section=class_code,
            is_active=True
        ).first()
        
        if existing_class:
            # Add teacher to existing class
            if not dry_run:
                existing_class.assigned_teachers.add(teacher)
                existing_class.save()
            
            return {
                'success': True,
                'class_code': class_code,
                'action': 'added_to_existing_class',
                'class_created': False,
                'class_id': str(existing_class.id)
            }
        else:
            # Create new class
            return self._create_class_from_code(teacher, class_code, dry_run)
            
    def _create_class_from_code(self, teacher, class_code, dry_run):
        """Create a new class from class code"""
        
        if class_code not in CLASS_CODE_CURRICULUM_MAPPING:
            return {
                'success': False,
                'error': f'Unknown class code: {class_code}',
                'class_code': class_code
            }
        
        # Parse class code
        grade_level, section = self._parse_class_code(class_code)
        class_name = f"{grade_level} {section}"
        
        if not dry_run:
            new_class = Class.objects.create(
                name=class_name,
                grade_level=grade_level,
                section=class_code,  # Use full class_code as section for mapping
                academic_year='2024-2025',
                is_active=True
            )
            new_class.assigned_teachers.add(teacher)
            new_class.save()
            
            class_id = str(new_class.id)
        else:
            class_id = 'dry_run'
        
        return {
            'success': True,
            'class_code': class_code,
            'action': 'created_new_class',
            'class_created': True,
            'class_name': class_name,
            'class_id': class_id
        }
        
    def _parse_class_code(self, class_code):
        """Parse class code into grade level and section"""
        
        if '_' in class_code:
            parts = class_code.split('_')
            grade_level = parts[0].replace('_', ' ').title()
            section = '_'.join(parts[1:]) if len(parts) > 2 else parts[1]
        else:
            grade_level = class_code
            section = class_code
            
        return grade_level, section
        
    def synchronize_all_teachers(self, dry_run=True):
        """Synchronize assignments for all teachers"""
        
        action_type = "ANALYZING" if dry_run else "SYNCHRONIZING"
        self.log_action(f"{action_type} all teachers")
        
        teachers = Teacher.objects.all()
        teachers_with_mismatches = 0
        total_changes = 0
        total_classes_created = 0
        
        self.stdout.write(f"\nProcessing {teachers.count()} teachers...")
        
        if dry_run:
            self.stdout.write(f"{self.style.WARNING('DRY RUN MODE - No changes will be made')}")
        
        for teacher in teachers:
            try:
                analysis = self._analyze_teacher_assignments(teacher)
                
                if analysis['needs_synchronization']:
                    teachers_with_mismatches += 1
                    
                    missing_classes = analysis['missing_in_class_system']
                    changes_made = 0
                    classes_created = 0
                    
                    with transaction.atomic():
                        for class_code in missing_classes:
                            try:
                                result = self._synchronize_single_assignment(teacher, class_code, dry_run)
                                
                                if result['success']:
                                    changes_made += 1
                                    if result['class_created']:
                                        classes_created += 1
                                        
                                    if not dry_run:
                                        self.statistics['synchronized_assignments'] += 1
                                        if result['class_created']:
                                            self.statistics['created_classes'] += 1
                                            
                            except Exception as e:
                                self.log_action(
                                    f"Error processing {class_code} for {teacher.name}: {str(e)}",
                                    'ERROR',
                                    teacher.name,
                                    class_code
                                )
                    
                    total_changes += changes_made
                    total_classes_created += classes_created
                    
                    self.log_action(
                        f"Teacher {teacher.name}: {changes_made} assignments, {classes_created} classes created",
                        teacher_name=teacher.name
                    )
                    
            except Exception as e:
                self.log_action(f"Error processing teacher {teacher.name}: {str(e)}", 'ERROR', teacher.name)
        
        # Final summary
        self.stdout.write("\n" + "="*60)
        action_type = "WOULD SYNCHRONIZE" if dry_run else "SYNCHRONIZED"
        self.stdout.write(self.style.SUCCESS(f"SYNCHRONIZATION COMPLETE"))
        self.stdout.write("="*60)
        
        self.stdout.write(f"Teachers processed: {teachers.count()}")
        self.stdout.write(f"Teachers requiring synchronization: {teachers_with_mismatches}")
        self.stdout.write(f"Total assignments {action_type.lower()}: {total_changes}")
        self.stdout.write(f"Total classes {action_type.lower() if not dry_run else 'would be created'}: {total_classes_created}")
        self.stdout.write(f"Errors: {self.statistics['errors']}")
        self.stdout.write(f"Warnings: {self.statistics['warnings']}")
        
        if dry_run and teachers_with_mismatches > 0:
            self.stdout.write(f"\n{self.style.WARNING('To execute these changes, run with --execute flag')}")
        elif not dry_run and teachers_with_mismatches > 0:
            self.stdout.write(f"\n{self.style.SUCCESS('✅ Synchronization completed successfully!')}")
            self.stdout.write("Run with --verify to confirm synchronization.")
            
    def verify_synchronization(self):
        """Verify synchronization status"""
        
        self.log_action("Verifying synchronization status")
        
        teachers = Teacher.objects.all()
        synchronized_teachers = 0
        teachers_with_mismatches = 0
        
        for teacher in teachers:
            analysis = self._analyze_teacher_assignments(teacher)
            if analysis['mismatch_count'] == 0:
                synchronized_teachers += 1
            else:
                teachers_with_mismatches += 1
        
        total_tca_assignments = TeacherClassAssignment.objects.filter(is_active=True).count()
        total_class_assignments = sum(
            cls.assigned_teachers.count() 
            for cls in Class.objects.filter(is_active=True)
        )
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("SYNCHRONIZATION VERIFICATION"))
        self.stdout.write("="*60)
        
        self.stdout.write(f"Total Teachers: {teachers.count()}")
        self.stdout.write(f"Synchronized Teachers: {synchronized_teachers}")
        self.stdout.write(f"Teachers with mismatches: {teachers_with_mismatches}")
        
        if teachers.count() > 0:
            success_rate = (synchronized_teachers / teachers.count()) * 100
            self.stdout.write(f"Synchronization rate: {success_rate:.1f}%")
        
        self.stdout.write(f"TeacherClassAssignments: {total_tca_assignments}")
        self.stdout.write(f"Class.assigned_teachers relationships: {total_class_assignments}")
        self.stdout.write(f"Synchronization gap: {total_tca_assignments - total_class_assignments}")
        
        if teachers_with_mismatches == 0:
            self.stdout.write(f"\n{self.style.SUCCESS('✅ SYNCHRONIZATION VERIFIED: Systems are in sync')}")
        else:
            self.stdout.write(f"\n{self.style.WARNING('⚠️  SYNCHRONIZATION INCOMPLETE: Issues remain')}")
            self.stdout.write("Run with --analyze to see detailed mismatch information.")