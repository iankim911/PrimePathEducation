"""
Quick PINNACLE Verification Test
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import Program, SubProgram, CurriculumLevel
from primepath_routinetest.models import ClassCurriculumMapping
from primepath_routinetest.models.class_model import Class
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING

def test_pinnacle():
    print("\n=== PINNACLE QUICK TEST ===\n")
    
    # Test 1: Program exists
    try:
        program = Program.objects.get(name='PINNACLE')
        print(f"✅ PINNACLE Program exists (ID: {program.id})")
    except Program.DoesNotExist:
        print("❌ PINNACLE Program not found")
        return False
    
    # Test 2: SubPrograms count
    subprograms = SubProgram.objects.filter(program=program)
    print(f"✅ SubPrograms: {subprograms.count()} found")
    for sp in subprograms:
        print(f"   - {sp.name}")
    
    # Test 3: Curriculum levels count
    levels = CurriculumLevel.objects.filter(subprogram__program=program)
    print(f"✅ Curriculum Levels: {levels.count()} found")
    
    # Test 4: Classes count
    pinnacle_classes = Class.objects.filter(section__startswith='PINNACLE')
    print(f"✅ PINNACLE Classes: {pinnacle_classes.count()} found")
    for cls in pinnacle_classes:
        print(f"   - {cls.section}: {cls.name}")
    
    # Test 5: Mappings count
    mappings = ClassCurriculumMapping.objects.filter(class_code__startswith='PINNACLE')
    print(f"✅ Class-Curriculum Mappings: {mappings.count()} found")
    
    # Test 6: class_code_mapping.py
    pinnacle_in_mapping = sum(1 for k in CLASS_CODE_CURRICULUM_MAPPING if k.startswith('PINNACLE'))
    print(f"✅ class_code_mapping.py: {pinnacle_in_mapping} PINNACLE entries")
    
    print("\n=== SUMMARY ===")
    if (subprograms.count() == 4 and 
        levels.count() == 8 and 
        pinnacle_classes.count() == 8 and 
        mappings.count() == 8 and
        pinnacle_in_mapping == 8):
        print("✅ ALL PINNACLE COMPONENTS VERIFIED SUCCESSFULLY!")
        return True
    else:
        print("⚠️  Some components missing or incomplete")
        return False

if __name__ == "__main__":
    success = test_pinnacle()
    sys.exit(0 if success else 1)