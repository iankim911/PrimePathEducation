"""
Test admin assignments in the view
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment
from primepath_routinetest.models.class_model import Class
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING, get_class_codes_by_program

def test_admin_assignments():
    print("\n=== TESTING ADMIN ASSIGNMENTS ===\n")
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return
    
    print(f"Admin user: {admin_user.username}")
    
    # Get teacher profile
    try:
        teacher = Teacher.objects.get(user=admin_user)
        print(f"Teacher profile: {teacher.name}")
        print(f"Is head teacher: {teacher.is_head_teacher}")
    except Teacher.DoesNotExist:
        print("❌ No teacher profile for admin")
        return
    
    # Check if admin mode would be activated
    is_admin = teacher.is_head_teacher
    print(f"\nWould be in admin mode: {is_admin}")
    
    if is_admin:
        # Simulate admin logic from view
        print("\n=== SIMULATING ADMIN MODE ===")
        
        # Get all active classes
        active_classes = Class.objects.filter(is_active=True).order_by('section')
        all_class_codes = [cls.section for cls in active_classes if cls.section]
        
        print(f"All active classes: {len(all_class_codes)}")
        
        # Check PINNACLE classes
        pinnacle_in_all = [c for c in all_class_codes if c.startswith('PINNACLE')]
        print(f"PINNACLE classes in all_class_codes: {len(pinnacle_in_all)}")
        print(f"  {pinnacle_in_all}")
        
        # Create mock assignments (like the view does)
        my_assignments = []
        class_lookup = {}
        
        for cls in active_classes:
            if cls.section:
                if cls.section in CLASS_CODE_CURRICULUM_MAPPING:
                    class_lookup[cls.section] = CLASS_CODE_CURRICULUM_MAPPING[cls.section]
                else:
                    class_lookup[cls.section] = cls.name
        
        for class_code in all_class_codes:
            class MockAssignment:
                def __init__(self, code, display_name):
                    self.class_code = code
                    self.access_level = 'FULL'
                    self.is_virtual = True
                    self._display_name = display_name
                
                def get_class_code_display(self):
                    return self._display_name
            
            display_name = class_lookup.get(class_code, class_code)
            mock_assignment = MockAssignment(class_code, display_name)
            my_assignments.append(mock_assignment)
        
        print(f"\nMock assignments created: {len(my_assignments)}")
        
        # Check PINNACLE assignments
        pinnacle_assignments = [a for a in my_assignments if a.class_code.startswith('PINNACLE')]
        print(f"PINNACLE in mock assignments: {len(pinnacle_assignments)}")
        for pa in pinnacle_assignments:
            print(f"  {pa.class_code}: {pa.get_class_code_display()}")
        
        # Now test program mapping
        print("\n=== TESTING PROGRAM MAPPING ===")
        PROGRAM_MAPPING = {
            'CORE': get_class_codes_by_program('CORE'),
            'ASCENT': get_class_codes_by_program('ASCENT'),
            'EDGE': get_class_codes_by_program('EDGE'),
            'PINNACLE': get_class_codes_by_program('PINNACLE')
        }
        
        print(f"PINNACLE in PROGRAM_MAPPING: {len(PROGRAM_MAPPING['PINNACLE'])} classes")
        print(f"  {PROGRAM_MAPPING['PINNACLE']}")
        
        # Test the matching logic
        print("\n=== TESTING MATCHING LOGIC ===")
        
        # First, show what the first 20 assignments are
        print(f"First 20 assignments (what the view checks):")
        for i, assignment in enumerate(my_assignments[:20]):
            print(f"  {i+1}. {assignment.class_code}")
        
        print("\n=== PROGRAM MATCHING ===")
        for program_name in ['PINNACLE']:
            program_classes = []
            for assignment in my_assignments[:20]:  # Same limit as view
                if assignment.class_code in PROGRAM_MAPPING[program_name]:
                    program_classes.append(assignment.class_code)
                    print(f"  ✅ {assignment.class_code} matches {program_name}")
            
            print(f"{program_name}: {len(program_classes)} classes matched")
            if program_classes:
                print(f"  Matched: {program_classes[:5]}...")
        
    else:
        print("Not in admin mode, checking regular assignments...")
        assignments = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        )
        print(f"Teacher assignments: {assignments.count()}")
        pinnacle_assignments = assignments.filter(class_code__startswith='PINNACLE')
        print(f"PINNACLE assignments: {pinnacle_assignments.count()}")

if __name__ == "__main__":
    test_admin_assignments()