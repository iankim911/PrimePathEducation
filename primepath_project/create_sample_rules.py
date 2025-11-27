import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings')
django.setup()

from core.models import PlacementRule, CurriculumLevel

# Sample placement rules based on PRD curriculum mapping
rules_data = [
    # Grade 1-2 (CORE PHONICS)
    (1, 0, 30, "CORE PHONICS", 1),
    (1, 30, 60, "CORE PHONICS", 2),
    (1, 60, 100, "CORE PHONICS", 3),
    (2, 0, 30, "CORE PHONICS", 2),
    (2, 30, 60, "CORE PHONICS", 3),
    (2, 60, 100, "CORE SIGMA", 1),
    
    # Grade 3-4 (CORE SIGMA/ELITE)
    (3, 0, 30, "CORE SIGMA", 1),
    (3, 30, 60, "CORE SIGMA", 2),
    (3, 60, 100, "CORE SIGMA", 3),
    (4, 0, 30, "CORE SIGMA", 3),
    (4, 30, 60, "CORE ELITE", 1),
    (4, 60, 100, "CORE ELITE", 2),
    
    # Grade 5-6 (ASCENT)
    (5, 0, 30, "ASCENT NOVA", 1),
    (5, 30, 60, "ASCENT NOVA", 2),
    (5, 60, 100, "ASCENT NOVA", 3),
    (6, 0, 30, "ASCENT NOVA", 3),
    (6, 30, 60, "ASCENT DRIVE", 1),
    (6, 60, 100, "ASCENT DRIVE", 2),
    
    # Grade 7-9 (EDGE)
    (7, 0, 30, "EDGE SPARK", 1),
    (7, 30, 60, "EDGE SPARK", 2),
    (7, 60, 100, "EDGE SPARK", 3),
    (8, 0, 30, "EDGE RISE", 1),
    (8, 30, 60, "EDGE RISE", 2),
    (8, 60, 100, "EDGE RISE", 3),
    (9, 0, 30, "EDGE PURSUIT", 1),
    (9, 30, 60, "EDGE PURSUIT", 2),
    (9, 60, 100, "EDGE PURSUIT", 3),
    
    # Grade 10-12 (PINNACLE)
    (10, 0, 30, "PINNACLE VISION", 1),
    (10, 30, 60, "PINNACLE VISION", 2),
    (10, 60, 100, "PINNACLE VISION", 3),
    (11, 0, 30, "PINNACLE ENDEAVOR", 1),
    (11, 30, 60, "PINNACLE ENDEAVOR", 2),
    (11, 60, 100, "PINNACLE ENDEAVOR", 3),
    (12, 0, 30, "PINNACLE SUCCESS", 1),
    (12, 30, 60, "PINNACLE SUCCESS", 2),
    (12, 60, 100, "PINNACLE SUCCESS", 3),
]

print("Creating placement rules...")
created_count = 0

for grade, min_rank, max_rank, subprogram_name, level_num in rules_data:
    try:
        # Find the curriculum level
        curriculum_level = CurriculumLevel.objects.get(
            subprogram__name=subprogram_name,
            level_number=level_num
        )
        
        # Create or update the rule
        rule, created = PlacementRule.objects.get_or_create(
            grade=grade,
            min_rank_percentile=min_rank,
            max_rank_percentile=max_rank,
            defaults={
                'curriculum_level': curriculum_level,
                'priority': 1
            }
        )
        
        if created:
            created_count += 1
            print(f"Created: Grade {grade}, Top {max_rank}% -> {subprogram_name} Level {level_num}")
        
    except CurriculumLevel.DoesNotExist:
        print(f"Warning: Could not find {subprogram_name} Level {level_num}")

print(f"\nTotal rules created: {created_count}")
print("\nPlacement rules are now set up!")
print("Students will be automatically matched to appropriate curriculum levels based on their grade and English ranking.")