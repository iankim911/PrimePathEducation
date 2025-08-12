#!/usr/bin/env python
"""
Enhanced PlacementService with smart gap handling and comprehensive logging
This updates the PlacementService to handle difficulty gaps intelligently
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

ENHANCED_CODE = '''
    @staticmethod
    def find_alternate_difficulty_exam(current_level: CurriculumLevel, adjustment: int) -> Optional[Tuple[CurriculumLevel, Exam]]:
        """
        Enhanced version: Find an exam from a different difficulty tier.
        Now with smart gap handling and comprehensive logging.
        
        Args:
            current_level: Current curriculum level
            adjustment: +1 for harder, -1 for easier
            
        Returns:
            Tuple of (new_level, exam) or None if no alternate found
        """
        from core.models import ExamLevelMapping
        import json
        
        # Console logging for debugging
        console_log = {
            'action': 'find_alternate_difficulty',
            'current_level': str(current_level),
            'current_level_id': current_level.id,
            'adjustment': adjustment,
            'direction': 'harder' if adjustment > 0 else 'easier'
        }
        
        # Get current difficulty tier
        current_difficulty = current_level.internal_difficulty if hasattr(current_level, 'internal_difficulty') else None
        console_log['current_difficulty'] = current_difficulty
        
        if current_difficulty is None:
            # If no difficulty set, fall back to level-based logic
            logger.warning(
                f"No internal difficulty set for level {current_level.id}, using level-based logic"
            )
            console_log['fallback'] = 'using_level_based_logic'
            print(f"[DIFFICULTY_ADJUSTMENT] {json.dumps(console_log)}")
            return PlacementService._find_alternate_by_level(current_level, adjustment)
        
        # Smart gap handling: Find next available difficulty
        max_attempts = 10  # Prevent infinite loops
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            
            # Calculate target difficulty
            target_difficulty = current_difficulty + (adjustment * attempts)
            console_log['attempt'] = attempts
            console_log['target_difficulty'] = target_difficulty
            
            # Check boundaries
            if adjustment > 0 and target_difficulty > 44:  # Max difficulty
                logger.info(f"Reached maximum difficulty tier (44)")
                console_log['result'] = 'max_difficulty_reached'
                print(f"[DIFFICULTY_ADJUSTMENT] {json.dumps(console_log)}")
                return None
            elif adjustment < 0 and target_difficulty < 1:  # Min difficulty
                logger.info(f"Reached minimum difficulty tier (1)")
                console_log['result'] = 'min_difficulty_reached'
                print(f"[DIFFICULTY_ADJUSTMENT] {json.dumps(console_log)}")
                return None
            
            # Find levels with target difficulty
            alternate_levels = CurriculumLevel.objects.filter(
                internal_difficulty=target_difficulty
            ).exclude(id=current_level.id).select_related('subprogram__program')
            
            if not alternate_levels.exists():
                # No levels at this difficulty, try next
                logger.debug(f"No levels found at difficulty {target_difficulty}, trying next...")
                console_log[f'attempt_{attempts}_result'] = 'no_levels_found'
                continue
            
            # Try to find a level with an exam
            for level in alternate_levels:
                mappings = ExamLevelMapping.objects.filter(
                    curriculum_level=level
                ).select_related('exam')
                
                # Get active exams
                active_exams = [m.exam for m in mappings if m.exam.is_active]
                
                if active_exams:
                    # Success! Found an exam
                    import random
                    selected_exam = random.choice(active_exams)
                    
                    console_log['result'] = 'success'
                    console_log['new_level'] = str(level)
                    console_log['new_level_id'] = level.id
                    console_log['new_difficulty'] = target_difficulty
                    console_log['new_exam'] = selected_exam.name
                    console_log['difficulty_jump'] = target_difficulty - current_difficulty
                    
                    logger.info(
                        f"Found alternate difficulty exam: {selected_exam.name} "
                        f"at level {level} (difficulty {target_difficulty}, "
                        f"jump of {target_difficulty - current_difficulty})"
                    )
                    
                    print(f"[DIFFICULTY_ADJUSTMENT_SUCCESS] {json.dumps(console_log)}")
                    return (level, selected_exam)
            
            # No exams found at this difficulty level
            logger.debug(f"No exams found for difficulty tier {target_difficulty}, trying next...")
            console_log[f'attempt_{attempts}_result'] = 'no_exams_found'
        
        # Exhausted attempts
        logger.info(f"Could not find alternate exam after {max_attempts} attempts")
        console_log['result'] = 'no_alternate_found'
        console_log['attempts_exhausted'] = True
        print(f"[DIFFICULTY_ADJUSTMENT_FAILED] {json.dumps(console_log)}")
        return None
    
    @staticmethod
    def get_difficulty_info(curriculum_level: CurriculumLevel) -> dict:
        """
        Get detailed difficulty information for a curriculum level.
        Useful for frontend display and debugging.
        """
        from core.models import ExamLevelMapping
        
        difficulty = curriculum_level.internal_difficulty
        
        # Find adjacent difficulties
        easier_exists = False
        harder_exists = False
        
        if difficulty:
            # Check for easier levels with exams
            easier_levels = CurriculumLevel.objects.filter(
                internal_difficulty__lt=difficulty
            ).order_by('-internal_difficulty')
            
            for level in easier_levels[:3]:  # Check top 3 easier
                mappings = ExamLevelMapping.objects.filter(
                    curriculum_level=level,
                    exam__is_active=True
                ).exists()
                if mappings:
                    easier_exists = True
                    break
            
            # Check for harder levels with exams
            harder_levels = CurriculumLevel.objects.filter(
                internal_difficulty__gt=difficulty
            ).order_by('internal_difficulty')
            
            for level in harder_levels[:3]:  # Check top 3 harder
                mappings = ExamLevelMapping.objects.filter(
                    curriculum_level=level,
                    exam__is_active=True
                ).exists()
                if mappings:
                    harder_exists = True
                    break
        
        return {
            'current_difficulty': difficulty,
            'current_level': str(curriculum_level),
            'can_go_easier': easier_exists,
            'can_go_harder': harder_exists,
            'difficulty_range': {
                'min': 1,
                'max': 44,
                'current': difficulty
            }
        }
'''

def update_placement_service():
    """Update the PlacementService with enhanced methods"""
    import shutil
    from datetime import datetime
    
    service_file = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/placement_test/services/placement_service.py'
    
    # Backup original
    backup_file = f'{service_file}.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy(service_file, backup_file)
    print(f"✅ Created backup: {backup_file}")
    
    # Read current file
    with open(service_file, 'r') as f:
        content = f.read()
    
    # Find and replace the find_alternate_difficulty_exam method
    import re
    
    # Pattern to match the entire method
    pattern = r'(@staticmethod\s+def find_alternate_difficulty_exam.*?)(?=@staticmethod|class |$)'
    
    # Check if method exists
    if re.search(pattern, content, re.DOTALL):
        # Replace existing method
        new_content = re.sub(pattern, ENHANCED_CODE + '\n    ', content, flags=re.DOTALL)
        
        # Add the new get_difficulty_info method if it doesn't exist
        if 'def get_difficulty_info' not in new_content:
            # Find the end of the class (before adjust_difficulty method)
            adjust_pattern = r'(@staticmethod\s+def adjust_difficulty)'
            if re.search(adjust_pattern, new_content):
                # Get the get_difficulty_info method from ENHANCED_CODE
                import textwrap
                difficulty_info_method = '''
    @staticmethod
    def get_difficulty_info(curriculum_level: CurriculumLevel) -> dict:
        """
        Get detailed difficulty information for a curriculum level.
        Useful for frontend display and debugging.
        """
        from core.models import ExamLevelMapping
        
        difficulty = curriculum_level.internal_difficulty
        
        # Find adjacent difficulties
        easier_exists = False
        harder_exists = False
        
        if difficulty:
            # Check for easier levels with exams
            easier_levels = CurriculumLevel.objects.filter(
                internal_difficulty__lt=difficulty
            ).order_by('-internal_difficulty')
            
            for level in easier_levels[:3]:  # Check top 3 easier
                mappings = ExamLevelMapping.objects.filter(
                    curriculum_level=level,
                    exam__is_active=True
                ).exists()
                if mappings:
                    easier_exists = True
                    break
            
            # Check for harder levels with exams
            harder_levels = CurriculumLevel.objects.filter(
                internal_difficulty__gt=difficulty
            ).order_by('internal_difficulty')
            
            for level in harder_levels[:3]:  # Check top 3 harder
                mappings = ExamLevelMapping.objects.filter(
                    curriculum_level=level,
                    exam__is_active=True
                ).exists()
                if mappings:
                    harder_exists = True
                    break
        
        return {
            'current_difficulty': difficulty,
            'current_level': str(curriculum_level),
            'can_go_easier': easier_exists,
            'can_go_harder': harder_exists,
            'difficulty_range': {
                'min': 1,
                'max': 44,
                'current': difficulty
            }
        }
    
    '''
                new_content = re.sub(adjust_pattern, difficulty_info_method + r'\1', new_content)
        
        # Write updated content
        with open(service_file, 'w') as f:
            f.write(new_content)
        
        print("✅ Successfully updated PlacementService with enhanced methods")
        print("✅ Added smart gap handling for difficulty progression")
        print("✅ Added comprehensive console logging")
        print("✅ Added get_difficulty_info method for frontend")
        return True
    else:
        print("❌ Could not find find_alternate_difficulty_exam method")
        return False

if __name__ == "__main__":
    print("🔧 Enhancing PlacementService...")
    if update_placement_service():
        print("\n✅ Enhancement complete!")
        print("\nNew features:")
        print("  1. Smart gap handling - automatically finds next available difficulty")
        print("  2. Comprehensive console logging with [DIFFICULTY_ADJUSTMENT] tags")
        print("  3. get_difficulty_info() method for frontend feedback")
        print("  4. Handles up to 10 difficulty gaps gracefully")
    else:
        print("\n❌ Enhancement failed - check the service file structure")