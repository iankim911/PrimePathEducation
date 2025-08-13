import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings')
django.setup()

from core.models import ExamLevelMapping, CurriculumLevel
from placement_test.models import Exam
from placement_test.services import PlacementService

# Check if exam mappings exist
print("=== Checking Exam Mappings ===")
mappings = ExamLevelMapping.objects.all()
print(f"Total mappings: {mappings.count()}")

for mapping in mappings[:5]:
    print(f"Level: {mapping.curriculum_level.full_name}, Exam: {mapping.exam.name}, Slot: {mapping.slot}")

# Check PRIME CORE PHONICS - Level 1
print("\n=== Checking PRIME CORE PHONICS - Level 1 ===")
try:
    level = CurriculumLevel.objects.get(
        subprogram__name="CORE PHONICS",
        level_number=1
    )
    print(f"Found level: {level.full_name}")
    
    # Check mappings for this level
    level_mappings = ExamLevelMapping.objects.filter(curriculum_level=level)
    print(f"Mappings for this level: {level_mappings.count()}")
    
    for mapping in level_mappings:
        print(f"  - Exam: {mapping.exam.name}, Active: {mapping.exam.is_active}")
    
    # Test the service
    print("\n=== Testing PlacementService ===")
    try:
        exam = PlacementService.find_exam_for_level(level)
        print(f"Successfully found exam: {exam.name}")
    except Exception as e:
        print(f"Error finding exam: {e}")
        
except CurriculumLevel.DoesNotExist:
    print("PRIME CORE PHONICS - Level 1 not found!")

# Check placement rules
print("\n=== Checking Placement Rules ===")
from core.models import PlacementRule
rules = PlacementRule.objects.filter(grade=1)
print(f"Rules for grade 1: {rules.count()}")
for rule in rules:
    print(f"  - Grade {rule.grade}, Rank {rule.min_rank_percentile}-{rule.max_rank_percentile}% -> {rule.curriculum_level.full_name}")