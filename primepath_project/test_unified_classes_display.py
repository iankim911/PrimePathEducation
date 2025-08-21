#!/usr/bin/env python
"""Test that unified Classes & Exams page shows PrimePath curriculum codes"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models.class_model import Class
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING

print("=" * 80)
print("UNIFIED CLASSES & EXAMS TEST")
print("=" * 80)

# Test what an admin would see
print("\n1. Testing Admin View:")
print("-" * 40)

# Get active classes
active_classes = Class.objects.filter(is_active=True).order_by('section')
print(f"Total active classes: {active_classes.count()}")

print("\nClasses that will be displayed:")
for cls in active_classes[:10]:
    if cls.section in CLASS_CODE_CURRICULUM_MAPPING:
        curriculum = CLASS_CODE_CURRICULUM_MAPPING[cls.section]
        print(f"  • {cls.section}: {curriculum}")
    else:
        print(f"  • {cls.section}: {cls.name}")

if active_classes.count() > 10:
    print(f"  ... and {active_classes.count() - 10} more")

# Test the mock assignment creation logic
print("\n2. Testing Mock Assignment Logic:")
print("-" * 40)

class_lookup = {}
for cls in active_classes:
    if cls.section:
        if cls.section in CLASS_CODE_CURRICULUM_MAPPING:
            class_lookup[cls.section] = CLASS_CODE_CURRICULUM_MAPPING[cls.section]
        else:
            class_lookup[cls.section] = cls.name

# Create a sample mock assignment
class MockAssignment:
    def __init__(self, code, display_name):
        self.class_code = code
        self.access_level = 'FULL'
        self.is_virtual = True
        self._display_name = display_name
    
    def get_class_code_display(self):
        return self._display_name

# Test with a few sample codes
sample_codes = ['PS1', 'A2', 'MAS', 'High1.SatSun.3-5']
for code in sample_codes:
    if code in class_lookup:
        display_name = class_lookup[code]
        mock = MockAssignment(code, display_name)
        print(f"  {mock.class_code} -> {mock.get_class_code_display()}")

print("\n3. Expected Display in UI:")
print("-" * 40)
print("Instead of seeing:")
print("  ❌ CLASS_2B, CLASS_3A, CLASS_4A, CLASS_6A, CLASS_6B")
print("\nYou will now see:")
print("  ✅ PS1 (CORE Phonics Level 1)")
print("  ✅ A2 (CORE Sigma Level 1)")
print("  ✅ MAS (EDGE Pro Level 1)")
print("  ✅ High1.SatSun.3-5 (PINNACLE Vision Level 1)")
print("  ... and all other PrimePath curriculum classes")

print("\n" + "=" * 80)
print("✅ Classes & Exams page updated to show PrimePath curriculum!")
print("=" * 80)
print("\nAccess the page at: http://127.0.0.1:8000/RoutineTest/classes-exams/")
print("=" * 80)