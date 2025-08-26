#!/usr/bin/env python3
"""
Phase 2 Step 2.3: ManagedExam to RoutineExam Data Migration Script
================================================================

This script safely migrates data from ManagedExam (exam_management.py) to the
extended RoutineExam model, converting field formats and relationships as needed.

CRITICAL: Run this with --dry-run first to preview changes!

Usage:
    python step2_3_data_migration_script.py --dry-run    # Preview only
    python step2_3_data_migration_script.py --execute   # Perform migration
    python step2_3_data_migration_script.py --status    # Check current status
"""

import os
import sys
import django
import json
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.db import transaction, connection
from primepath_routinetest.models.exam_management import ManagedExam
from primepath_routinetest.models.exam import RoutineExam
from core.models import CurriculumLevel, Teacher, School

class DataMigrationManager:
    """Manages the migration from ManagedExam to RoutineExam"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.migrated_records = []
        self.curriculum_mappings = {
            # Known ManagedExam curriculum_level values -> CurriculumLevel mapping
            "CORE Phonics Level 1": None,
            "ASCENT Nova Level 2": None,
            "EDGE Spark Level 3": None,
            "PINNACLE Vision Level 1": None,
            "Grade 5 Basic": None,  # These will need to be mapped or created
        }
        
    def analyze_existing_data(self):
        """Analyze existing data before migration"""
        print("=" * 70)
        print("📊 PHASE 2 DATA MIGRATION ANALYSIS")
        print("=" * 70)
        
        # Count records
        managed_count = ManagedExam.objects.count()
        routine_count = RoutineExam.objects.count()
        
        print(f"📋 ManagedExam records: {managed_count}")
        print(f"📋 RoutineExam records: {routine_count}")
        print()
        
        if managed_count == 0:
            print("⚠️  No ManagedExam records found - nothing to migrate")
            return False
            
        # Analyze curriculum level mappings
        print("🔍 CURRICULUM LEVEL ANALYSIS:")
        managed_curricula = ManagedExam.objects.values_list('curriculum_level', flat=True).distinct()
        
        for curriculum in managed_curricula:
            if curriculum:
                # Try to find matching CurriculumLevel by description or parsing the name
                try:
                    # First, try exact match on description
                    cl = CurriculumLevel.objects.filter(description__icontains=curriculum).first()
                    
                    # If no exact match, try parsing the curriculum name
                    if not cl:
                        # Parse "CORE Phonics Level 1" -> program="CORE", subprogram="Phonics", level=1
                        parts = curriculum.split()
                        if len(parts) >= 4 and parts[-2] == "Level":
                            try:
                                program = parts[0]
                                subprogram = parts[1]
                                level_num = int(parts[-1])
                                
                                cl = CurriculumLevel.objects.filter(
                                    subprogram__program__name=program,
                                    subprogram__name=subprogram,
                                    level_number=level_num
                                ).first()
                            except (ValueError, IndexError):
                                pass
                    
                    if cl:
                        self.curriculum_mappings[curriculum] = cl
                        print(f"  ✅ {curriculum} -> {cl}")
                    else:
                        print(f"  ❌ {curriculum} -> NO MATCHING CURRICULUM LEVEL")
                        self.errors.append(f"No CurriculumLevel found for: {curriculum}")
                except Exception as e:
                    print(f"  ❌ {curriculum} -> ERROR: {e}")
                    self.errors.append(f"Error mapping {curriculum}: {e}")
        
        print()
        
        # Analyze field mappings
        print("🔄 FIELD MAPPING PREVIEW:")
        sample_exam = ManagedExam.objects.first()
        if sample_exam:
            print(f"  Sample Exam: {sample_exam.name}")
            print(f"  curriculum_level (str): {sample_exam.curriculum_level}")
            print(f"  -> will map to CurriculumLevel FK")
            print(f"  duration (int): {sample_exam.duration}")  
            print(f"  -> will map to timer_minutes field")
            print(f"  answer_key (JSON): {len(sample_exam.answer_key) if sample_exam.answer_key else 0} keys")
            print(f"  -> will copy directly")
            print(f"  version (int): {sample_exam.version}")
            print(f"  -> will copy directly")
        
        print()
        return True
    
    def prepare_curriculum_mappings(self, dry_run=True):
        """Prepare curriculum level mappings, creating missing ones if needed"""
        print("🎯 PREPARING CURRICULUM MAPPINGS:")
        
        missing_curricula = []
        for curriculum_str, curriculum_obj in self.curriculum_mappings.items():
            if curriculum_str and not curriculum_obj:
                missing_curricula.append(curriculum_str)
        
        if missing_curricula:
            print(f"  ⚠️  Found {len(missing_curricula)} missing curriculum mappings:")
            for curriculum in missing_curricula:
                print(f"    - {curriculum}")
            
            if not dry_run:
                # For now, we'll log these as warnings
                # In a real scenario, we'd either create them or map to closest matches
                for curriculum in missing_curricula:
                    self.warnings.append(f"ManagedExam curriculum '{curriculum}' has no CurriculumLevel mapping")
                    
        return len(missing_curricula) == 0
    
    def migrate_single_record(self, managed_exam, dry_run=True):
        """Migrate a single ManagedExam record to RoutineExam"""
        
        # Check if already migrated (by name uniqueness)
        existing = RoutineExam.objects.filter(name=managed_exam.name).first()
        if existing:
            self.warnings.append(f"Exam '{managed_exam.name}' already exists in RoutineExam - skipping")
            return None
        
        # Prepare field mappings
        migration_data = {
            'name': managed_exam.name,
            'pdf_file': managed_exam.pdf_file,
            'timer_minutes': managed_exam.duration,  # duration -> timer_minutes
            'instructions': managed_exam.instructions or "",
            'created_at': managed_exam.created_at,
            'updated_at': managed_exam.updated_at,
            'is_active': managed_exam.is_active,
            
            # New fields from Phase 2 extension
            'answer_key': managed_exam.answer_key or {},
            'version': managed_exam.version or 1,
            
            # ManagedExam specific fields that need mapping
            'exam_type': managed_exam.exam_type,
            'academic_year': managed_exam.academic_year,
            'time_period_quarter': managed_exam.time_period_quarter,
            'time_period_month': managed_exam.time_period_month,
            
            # Required RoutineExam fields with defaults
            'total_questions': len(managed_exam.answer_key) if managed_exam.answer_key else 1,  # Use answer key count or default to 1
            'class_codes': [],  # Empty list for JSON field
        }
        
        # Handle curriculum_level conversion (string -> ForeignKey)
        curriculum_obj = self.curriculum_mappings.get(managed_exam.curriculum_level)
        if curriculum_obj:
            migration_data['curriculum_level'] = curriculum_obj
        else:
            self.warnings.append(f"No curriculum mapping for '{managed_exam.curriculum_level}' in exam '{managed_exam.name}'")
            # Use a default curriculum or leave null
            migration_data['curriculum_level'] = None
        
        # Handle user relationships
        if managed_exam.created_by:
            migration_data['created_by'] = managed_exam.created_by
            
        if dry_run:
            print(f"    📋 WOULD MIGRATE: {managed_exam.name}")
            print(f"       curriculum: {managed_exam.curriculum_level} -> {curriculum_obj}")
            print(f"       duration: {managed_exam.duration}min -> timer_minutes")
            print(f"       answer_key: {len(managed_exam.answer_key) if managed_exam.answer_key else 0} keys")
            return migration_data
        else:
            # Actually create the record
            try:
                new_routine_exam = RoutineExam.objects.create(**migration_data)
                self.migrated_records.append({
                    'original_id': str(managed_exam.id),
                    'new_id': str(new_routine_exam.id),
                    'name': managed_exam.name
                })
                print(f"    ✅ MIGRATED: {managed_exam.name} -> {new_routine_exam.id}")
                return new_routine_exam
            except Exception as e:
                error_msg = f"Failed to migrate '{managed_exam.name}': {e}"
                self.errors.append(error_msg)
                print(f"    ❌ ERROR: {error_msg}")
                return None
    
    def run_migration(self, dry_run=True):
        """Run the complete migration process"""
        print("=" * 70)
        if dry_run:
            print("🔍 DRY RUN MODE - NO CHANGES WILL BE MADE")
        else:
            print("⚡ EXECUTION MODE - CHANGES WILL BE APPLIED")
        print("=" * 70)
        
        # Step 1: Analyze existing data
        if not self.analyze_existing_data():
            return False
        
        # Step 2: Prepare curriculum mappings
        curriculum_ready = self.prepare_curriculum_mappings(dry_run)
        
        # Step 3: Get all ManagedExam records
        managed_exams = ManagedExam.objects.all().order_by('created_at')
        print(f"📦 Processing {managed_exams.count()} ManagedExam records:")
        print()
        
        # Step 4: Migrate each record
        if not dry_run:
            with transaction.atomic():
                for managed_exam in managed_exams:
                    self.migrate_single_record(managed_exam, dry_run=False)
        else:
            for managed_exam in managed_exams:
                self.migrate_single_record(managed_exam, dry_run=True)
        
        # Step 5: Report results
        self.print_migration_summary(dry_run)
        return len(self.errors) == 0
    
    def print_migration_summary(self, dry_run=True):
        """Print migration results summary"""
        print()
        print("=" * 70)
        if dry_run:
            print("📋 DRY RUN SUMMARY")
        else:
            print("✅ MIGRATION COMPLETED")
        print("=" * 70)
        
        print(f"📊 Records processed: {ManagedExam.objects.count()}")
        if not dry_run:
            print(f"✅ Successfully migrated: {len(self.migrated_records)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"   {error}")
        
        if not dry_run and self.migrated_records:
            print("\n📋 MIGRATED RECORDS:")
            for record in self.migrated_records:
                print(f"   {record['name']} ({record['original_id']} -> {record['new_id']})")
        
        print()
        if dry_run:
            print("🔄 To execute migration: python step2_3_data_migration_script.py --execute")
        else:
            print("🎉 Migration completed! Verify data integrity before proceeding to Step 2.4")


def check_status():
    """Check current migration status"""
    print("=" * 70)
    print("📊 MIGRATION STATUS CHECK")
    print("=" * 70)
    
    managed_count = ManagedExam.objects.count()
    routine_count = RoutineExam.objects.count()
    
    print(f"ManagedExam records: {managed_count}")
    print(f"RoutineExam records: {routine_count}")
    
    if managed_count == 0:
        print("✅ No ManagedExam records - migration may be complete")
    else:
        print("⚠️  ManagedExam records still exist - migration needed")
    
    # Check for overlapping names
    managed_names = set(ManagedExam.objects.values_list('name', flat=True))
    routine_names = set(RoutineExam.objects.values_list('name', flat=True))
    
    overlaps = managed_names.intersection(routine_names)
    if overlaps:
        print(f"🔄 Found {len(overlaps)} exams with matching names in both models:")
        for name in list(overlaps)[:5]:  # Show first 5
            print(f"   - {name}")
    else:
        print("✅ No name overlaps detected")


def main():
    """Main script entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    mode = sys.argv[1]
    
    if mode == '--status':
        check_status()
    elif mode == '--dry-run':
        migrator = DataMigrationManager()
        migrator.run_migration(dry_run=True)
    elif mode == '--execute':
        print("⚠️  EXECUTING MIGRATION - This will modify your database!")
        response = input("Are you sure you want to proceed? [y/N]: ")
        if response.lower() == 'y':
            migrator = DataMigrationManager()
            migrator.run_migration(dry_run=False)
        else:
            print("Migration cancelled")
    else:
        print("Invalid option. Use --dry-run, --execute, or --status")
        print(__doc__)


if __name__ == '__main__':
    main()