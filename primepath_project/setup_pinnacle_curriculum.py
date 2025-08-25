"""
PINNACLE Curriculum Setup Script
Created: August 25, 2025

This script sets up the complete PINNACLE curriculum structure:
1. Creates PRIME PINNACLE program
2. Creates 4 subprograms (Vision, Endeavor, Success, Pro)
3. Creates curriculum levels (Level 1-2 for each)
4. Creates PINNACLE-specific class codes
5. Maps classes to curriculum levels
6. Provides comprehensive logging and validation

This is a production-ready implementation with error handling and rollback capabilities.
"""

import os
import sys
import django
import json
import logging
from datetime import datetime
from django.db import transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Program, SubProgram, CurriculumLevel
from primepath_routinetest.models import ClassCurriculumMapping
from primepath_routinetest.models.class_model import Class
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'pinnacle_setup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PinnacleSetup:
    """Comprehensive PINNACLE curriculum setup manager"""
    
    def __init__(self):
        self.created_items = {
            'program': None,
            'subprograms': [],
            'curriculum_levels': [],
            'classes': [],
            'mappings': []
        }
        self.errors = []
        self.warnings = []
        
    def log_section(self, title):
        """Print section separator for clarity"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80)
        logger.info(f"[SECTION] {title}")
    
    def create_pinnacle_program(self):
        """Create or get PRIME PINNACLE program"""
        self.log_section("STEP 1: CREATING PINNACLE PROGRAM")
        
        try:
            # Check if already exists
            program, created = Program.objects.get_or_create(
                name='PINNACLE',  # Use the choice value, not display name
                defaults={
                    'grade_range_start': 10,
                    'grade_range_end': 12,
                    'order': 4  # After CORE, ASCENT, EDGE
                }
            )
            
            if created:
                print(f"✅ Created PRIME PINNACLE program")
                logger.info(f"[CREATED] Program: PRIME PINNACLE (ID: {program.id})")
            else:
                print(f"✓ PRIME PINNACLE program already exists")
                logger.info(f"[EXISTS] Program: PRIME PINNACLE (ID: {program.id})")
            
            self.created_items['program'] = program
            
            # Log program details
            print(f"   - Name: {program.get_name_display()}")
            print(f"   - Grade Range: {program.grade_range_start}-{program.grade_range_end}")
            print(f"   - Order: {program.order}")
            
            return program
            
        except Exception as e:
            error_msg = f"Failed to create PINNACLE program: {str(e)}"
            self.errors.append(error_msg)
            logger.error(f"[ERROR] {error_msg}")
            print(f"❌ {error_msg}")
            raise
    
    def create_subprograms(self, program):
        """Create PINNACLE subprograms"""
        self.log_section("STEP 2: CREATING PINNACLE SUBPROGRAMS")
        
        subprogram_specs = [
            {'name': 'Vision', 'code': 'VISION', 'order': 1},
            {'name': 'Endeavor', 'code': 'ENDEAVOR', 'order': 2},
            {'name': 'Success', 'code': 'SUCCESS', 'order': 3},
            {'name': 'Pro', 'code': 'PRO', 'order': 4}
        ]
        
        created_subprograms = []
        
        for spec in subprogram_specs:
            try:
                subprogram, created = SubProgram.objects.get_or_create(
                    program=program,
                    name=spec['name'],
                    defaults={
                        'order': spec['order']  # SubProgram doesn't have 'code' field
                    }
                )
                
                if created:
                    print(f"✅ Created subprogram: {spec['name']}")
                    logger.info(f"[CREATED] SubProgram: {spec['name']} (ID: {subprogram.id})")
                else:
                    print(f"✓ Subprogram {spec['name']} already exists")
                    logger.info(f"[EXISTS] SubProgram: {spec['name']} (ID: {subprogram.id})")
                
                created_subprograms.append(subprogram)
                
            except Exception as e:
                error_msg = f"Failed to create subprogram {spec['name']}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(f"[ERROR] {error_msg}")
                print(f"❌ {error_msg}")
        
        self.created_items['subprograms'] = created_subprograms
        return created_subprograms
    
    def create_curriculum_levels(self, subprograms):
        """Create curriculum levels for each subprogram (Level 1-2 only for PINNACLE)"""
        self.log_section("STEP 3: CREATING CURRICULUM LEVELS")
        
        created_levels = []
        
        for subprogram in subprograms:
            print(f"\n  Processing {subprogram.name}:")
            
            # PINNACLE only has Level 1 and 2
            for level_num in [1, 2]:
                try:
                    level, created = CurriculumLevel.objects.get_or_create(
                        subprogram=subprogram,  # Fixed field name: subprogram not sub_program
                        level_number=level_num,
                        defaults={
                            'description': f'{subprogram.name} Level {level_num}',  # CurriculumLevel uses description, not name
                            'internal_difficulty': level_num + 9  # 10-11 for PINNACLE
                        }
                    )
                    
                    if created:
                        print(f"    ✅ Created Level {level_num}")
                        logger.info(f"[CREATED] CurriculumLevel: {subprogram.name} Level {level_num} (ID: {level.id})")
                    else:
                        print(f"    ✓ Level {level_num} already exists")
                        logger.info(f"[EXISTS] CurriculumLevel: {subprogram.name} Level {level_num} (ID: {level.id})")
                    
                    created_levels.append(level)
                    
                except Exception as e:
                    error_msg = f"Failed to create level {level_num} for {subprogram.name}: {str(e)}"
                    self.errors.append(error_msg)
                    logger.error(f"[ERROR] {error_msg}")
                    print(f"    ❌ {error_msg}")
        
        self.created_items['curriculum_levels'] = created_levels
        return created_levels
    
    def create_pinnacle_classes(self):
        """Create PINNACLE-specific class codes"""
        self.log_section("STEP 4: CREATING PINNACLE CLASSES")
        
        # Define PINNACLE class structure
        class_specs = [
            # Vision classes
            {'section': 'PINNACLE_V1', 'name': 'PINNACLE Vision Level 1', 'grade_level': '10'},
            {'section': 'PINNACLE_V2', 'name': 'PINNACLE Vision Level 2', 'grade_level': '11'},
            # Endeavor classes
            {'section': 'PINNACLE_E1', 'name': 'PINNACLE Endeavor Level 1', 'grade_level': '10'},
            {'section': 'PINNACLE_E2', 'name': 'PINNACLE Endeavor Level 2', 'grade_level': '11'},
            # Success classes
            {'section': 'PINNACLE_S1', 'name': 'PINNACLE Success Level 1', 'grade_level': '11'},
            {'section': 'PINNACLE_S2', 'name': 'PINNACLE Success Level 2', 'grade_level': '12'},
            # Pro classes
            {'section': 'PINNACLE_P1', 'name': 'PINNACLE Pro Level 1', 'grade_level': '11'},
            {'section': 'PINNACLE_P2', 'name': 'PINNACLE Pro Level 2', 'grade_level': '12'},
        ]
        
        created_classes = []
        
        # Get admin user for created_by field
        admin_user = User.objects.filter(is_superuser=True).first()
        
        for spec in class_specs:
            try:
                class_obj, created = Class.objects.get_or_create(
                    section=spec['section'],
                    defaults={
                        'name': spec['name'],
                        'grade_level': spec['grade_level'],
                        'academic_year': str(datetime.now().year),
                        'is_active': True,
                        'created_by': admin_user
                    }
                )
                
                if created:
                    print(f"✅ Created class: {spec['section']} - {spec['name']}")
                    logger.info(f"[CREATED] Class: {spec['section']} (ID: {class_obj.id})")
                else:
                    print(f"✓ Class {spec['section']} already exists")
                    logger.info(f"[EXISTS] Class: {spec['section']} (ID: {class_obj.id})")
                
                created_classes.append(class_obj)
                
            except Exception as e:
                error_msg = f"Failed to create class {spec['section']}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(f"[ERROR] {error_msg}")
                print(f"❌ {error_msg}")
        
        self.created_items['classes'] = created_classes
        return created_classes
    
    def map_classes_to_curriculum(self, classes, curriculum_levels):
        """Map PINNACLE classes to their curriculum levels"""
        self.log_section("STEP 5: MAPPING CLASSES TO CURRICULUM")
        
        # Create mapping dictionary
        mapping_dict = {
            'PINNACLE_V1': 'Vision Level 1',
            'PINNACLE_V2': 'Vision Level 2',
            'PINNACLE_E1': 'Endeavor Level 1',
            'PINNACLE_E2': 'Endeavor Level 2',
            'PINNACLE_S1': 'Success Level 1',
            'PINNACLE_S2': 'Success Level 2',
            'PINNACLE_P1': 'Pro Level 1',
            'PINNACLE_P2': 'Pro Level 2',
        }
        
        created_mappings = []
        
        for class_obj in classes:
            if class_obj.section not in mapping_dict:
                warning = f"No mapping defined for class {class_obj.section}"
                self.warnings.append(warning)
                logger.warning(f"[WARNING] {warning}")
                continue
            
            target_curriculum_name = mapping_dict[class_obj.section]
            
            # Find the corresponding curriculum level by matching subprogram name and level
            curriculum_level = None
            for level in curriculum_levels:
                # Match based on subprogram name and level number
                if (level.subprogram.name in target_curriculum_name and 
                    str(level.level_number) in target_curriculum_name):
                    curriculum_level = level
                    break
            
            if not curriculum_level:
                warning = f"Could not find curriculum level: {target_curriculum_name}"
                self.warnings.append(warning)
                logger.warning(f"[WARNING] {warning}")
                continue
            
            try:
                # Create the mapping
                mapping, created = ClassCurriculumMapping.objects.get_or_create(
                    class_code=class_obj.section,
                    curriculum_level=curriculum_level,
                    defaults={
                        'academic_year': str(datetime.now().year),
                        'priority': 1,
                        'is_active': True
                    }
                )
                
                if created:
                    print(f"✅ Mapped {class_obj.section} → {target_curriculum_name}")
                    logger.info(f"[CREATED] Mapping: {class_obj.section} → {target_curriculum_name}")
                else:
                    print(f"✓ Mapping already exists: {class_obj.section} → {target_curriculum_name}")
                    logger.info(f"[EXISTS] Mapping: {class_obj.section} → {target_curriculum_name}")
                
                created_mappings.append(mapping)
                
            except Exception as e:
                error_msg = f"Failed to map {class_obj.section}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(f"[ERROR] {error_msg}")
                print(f"❌ {error_msg}")
        
        self.created_items['mappings'] = created_mappings
        return created_mappings
    
    def update_class_code_mapping(self):
        """Update the CLASS_CODE_CURRICULUM_MAPPING dictionary"""
        self.log_section("STEP 6: UPDATING CLASS CODE MAPPING")
        
        # Path to the mapping file
        mapping_file = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/primepath_routinetest/class_code_mapping.py'
        
        print(f"📝 Updating {mapping_file}")
        
        # Add PINNACLE mappings to the dictionary
        pinnacle_mappings = {
            'PINNACLE_V1': 'PINNACLE Vision Level 1',
            'PINNACLE_V2': 'PINNACLE Vision Level 2',
            'PINNACLE_E1': 'PINNACLE Endeavor Level 1',
            'PINNACLE_E2': 'PINNACLE Endeavor Level 2',
            'PINNACLE_S1': 'PINNACLE Success Level 1',
            'PINNACLE_S2': 'PINNACLE Success Level 2',
            'PINNACLE_P1': 'PINNACLE Pro Level 1',
            'PINNACLE_P2': 'PINNACLE Pro Level 2',
        }
        
        # Note: In production, you'd update the actual file
        print("⚠️  Manual update required for class_code_mapping.py")
        print("   Add the following mappings:")
        for code, curriculum in pinnacle_mappings.items():
            print(f"    '{code}': '{curriculum}',")
        
        logger.info("[INFO] Class code mapping update required")
        
    def verify_setup(self):
        """Verify the complete PINNACLE setup"""
        self.log_section("STEP 7: VERIFICATION")
        
        print("\n📊 SETUP SUMMARY:")
        print(f"   Program: {1 if self.created_items['program'] else 0}")
        print(f"   SubPrograms: {len(self.created_items['subprograms'])}")
        print(f"   Curriculum Levels: {len(self.created_items['curriculum_levels'])}")
        print(f"   Classes: {len(self.created_items['classes'])}")
        print(f"   Mappings: {len(self.created_items['mappings'])}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        # Test query to verify
        try:
            pinnacle_classes = ClassCurriculumMapping.objects.filter(
                curriculum_level__subprogram__program__name='PINNACLE'  # Use correct field names
            ).count()
            print(f"\n✅ VERIFICATION: {pinnacle_classes} classes mapped to PINNACLE curriculum")
            logger.info(f"[VERIFIED] {pinnacle_classes} PINNACLE mappings in database")
        except Exception as e:
            print(f"\n❌ VERIFICATION FAILED: {str(e)}")
            logger.error(f"[VERIFICATION_ERROR] {str(e)}")
        
        return len(self.errors) == 0
    
    def run(self):
        """Execute the complete PINNACLE setup"""
        print("\n" + "="*80)
        print("  PINNACLE CURRICULUM SETUP - PRODUCTION IMPLEMENTATION")
        print("="*80)
        print(f"  Start Time: {datetime.now()}")
        print("="*80)
        
        try:
            with transaction.atomic():
                # Step 1: Create program
                program = self.create_pinnacle_program()
                
                # Step 2: Create subprograms
                subprograms = self.create_subprograms(program)
                
                # Step 3: Create curriculum levels
                curriculum_levels = self.create_curriculum_levels(subprograms)
                
                # Step 4: Create classes
                classes = self.create_pinnacle_classes()
                
                # Step 5: Map classes to curriculum
                self.map_classes_to_curriculum(classes, curriculum_levels)
                
                # Step 6: Update mapping file
                self.update_class_code_mapping()
                
                # Step 7: Verify
                success = self.verify_setup()
                
                if success:
                    print("\n" + "="*80)
                    print("  ✅ PINNACLE SETUP COMPLETED SUCCESSFULLY")
                    print("="*80)
                    logger.info("[SUCCESS] PINNACLE curriculum setup completed")
                else:
                    print("\n" + "="*80)
                    print("  ⚠️  PINNACLE SETUP COMPLETED WITH WARNINGS")
                    print("="*80)
                    logger.warning("[COMPLETED_WITH_WARNINGS] PINNACLE setup has some issues")
                
                return success
                
        except Exception as e:
            print("\n" + "="*80)
            print("  ❌ PINNACLE SETUP FAILED")
            print("="*80)
            print(f"  Error: {str(e)}")
            logger.error(f"[FATAL_ERROR] Setup failed: {str(e)}")
            raise


if __name__ == "__main__":
    setup = PinnacleSetup()
    try:
        success = setup.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)