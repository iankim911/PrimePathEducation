#!/usr/bin/env python
"""
Script to assign classes to their appropriate programs
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models.class_model import Class

print('=== ASSIGNING CLASSES TO APPROPRIATE PROGRAMS ===')
print()

# Define class-to-program mappings
assignments = {
    'CORE': {
        'classes': ['P1', 'P2', 'PS1', 'A2', 'B2', 'B3', 'B4', 'B5', 'C2', 'C3', 'C4', 'C5', 'H1', 'H2', 'H4'],
        'subprogram': 'Sigma'
    },
    'ASCENT': {
        'classes': ['D2', 'D3', 'D4', 'S2'],
        'subprogram': 'Nova'
    },
    'EDGE': {
        'classes': ['Young-cho2', 'Young-choM', 'Chung-cho1', 'Chung-choM', 'SejongM', 'MAS', 
                    'TaejoC', 'TaejoD', 'TaejoE', 'TaejoG', 'SungjongM', 'Sungjong2', 'Sungjong3', 'Sungjong4'],
        'subprogram': 'Rise'
    },
    'PINNACLE': {
        'classes': ['High1 SaiSun 3-5', 'High1 SaiSun 5-7', 'High1V2 SaiSun 11-1', 'High1V2 SaiSun 1-3'],
        'subprogram': 'Vision'
    }
}

# Apply assignments
for program, data in assignments.items():
    print(f'\nAssigning to {program}:')
    for class_section in data['classes']:
        try:
            # Try different section formats
            cls = None
            for section_variant in [class_section, class_section.replace(' ', '_'), class_section.replace(' ', '-')]:
                try:
                    cls = Class.objects.get(section=section_variant)
                    break
                except Class.DoesNotExist:
                    continue
            
            if cls:
                old_program = cls.program
                cls.program = program
                cls.subprogram = data['subprogram']
                cls.save()
                
                if old_program != program:
                    print(f'  ✅ {cls.section} -> {program} ({data["subprogram"]})')
                else:
                    print(f'  • {cls.section} already in {program}')
            else:
                print(f'  ⚠️  {class_section} not found')
                
        except Exception as e:
            print(f'  ❌ Error with {class_section}: {e}')

print()
print('=== FINAL VERIFICATION ===')
for program in ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']:
    count = Class.objects.filter(program=program, is_active=True).count()
    print(f'{program}: {count} active classes')
    
print()
print('=== ASCENT PROGRAM CLASSES ===')
ascent_classes = Class.objects.filter(program='ASCENT', is_active=True).order_by('section')
if ascent_classes.count() > 0:
    for cls in ascent_classes:
        print(f'  - {cls.section}: {cls.name} (SubProgram: {cls.subprogram})')
else:
    print('  No classes found in ASCENT')

print()
print('=== STILL UNASSIGNED ===')
unassigned = Class.objects.filter(program__isnull=True, is_active=True)
print(f'Remaining unassigned classes: {unassigned.count()}')
if unassigned.count() > 0 and unassigned.count() <= 10:
    for cls in unassigned:
        print(f'  - {cls.section}: {cls.name}')