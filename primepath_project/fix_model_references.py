#!/usr/bin/env python
"""
Fix Model Reference Issues from Remediation
Date: August 27, 2025
Purpose: Update string references to use new model names
"""

import os
import re
from pathlib import Path


def fix_file(file_path):
    """Fix model references in a single file."""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original = content
    
    # Replacement patterns for model references
    replacements = [
        # placement_test models
        (r"'placement_test\.Exam'", "'placement_test.PlacementExam'"),
        (r'"placement_test\.Exam"', '"placement_test.PlacementExam"'),
        (r"'placement_test\.exam'", "'placement_test.placementexam'"),
        (r'"placement_test\.exam"', '"placement_test.placementexam"'),
        
        (r"'placement_test\.AudioFile'", "'placement_test.PlacementAudioFile'"),
        (r'"placement_test\.AudioFile"', '"placement_test.PlacementAudioFile"'),
        (r"'placement_test\.audiofile'", "'placement_test.placementaudiofile'"),
        (r'"placement_test\.audiofile"', '"placement_test.placementaudiofile"'),
        
        # primepath_routinetest models
        (r"'primepath_routinetest\.Exam'", "'primepath_routinetest.RoutineExam'"),
        (r'"primepath_routinetest\.Exam"', '"primepath_routinetest.RoutineExam"'),
        (r"'primepath_routinetest\.exam'", "'primepath_routinetest.routineexam'"),
        (r'"primepath_routinetest\.exam"', '"primepath_routinetest.routineexam"'),
        
        (r"'primepath_routinetest\.AudioFile'", "'primepath_routinetest.RoutineAudioFile'"),
        (r'"primepath_routinetest\.AudioFile"', '"primepath_routinetest.RoutineAudioFile"'),
        (r"'primepath_routinetest\.audiofile'", "'primepath_routinetest.routineaudiofile'"),
        (r'"primepath_routinetest\.audiofile"', '"primepath_routinetest.routineaudiofile"'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False


def main():
    """Fix all model reference issues."""
    
    print("=" * 80)
    print("FIXING MODEL REFERENCES FROM REMEDIATION")
    print("=" * 80)
    
    # Find all Python files
    files_to_check = []
    for app in ['placement_test', 'primepath_routinetest', 'primepath_student', 'core']:
        app_path = Path(app)
        if app_path.exists():
            files_to_check.extend(app_path.rglob('*.py'))
    
    fixed_count = 0
    for file_path in files_to_check:
        if '__pycache__' in str(file_path):
            continue
        if 'migrations' in str(file_path):
            continue  # Skip migrations for now
            
        if fix_file(file_path):
            print(f"✅ Fixed: {file_path}")
            fixed_count += 1
    
    print("\n" + "=" * 80)
    print(f"Fixed {fixed_count} files")
    
    # Now fix the specific files we know have issues
    specific_files = [
        'placement_test/models/question.py',
        'placement_test/models/session.py',
        'primepath_routinetest/models/question.py',
        'primepath_routinetest/models/session.py',
        'primepath_routinetest/models/schedule.py',
        'core/models.py',
    ]
    
    print("\nFixing known problematic files...")
    for file_path in specific_files:
        if Path(file_path).exists():
            if fix_file(file_path):
                print(f"✅ Fixed: {file_path}")
    
    print("\n✅ Model reference fixes complete!")
    print("Now restart the Django server.")


if __name__ == '__main__':
    main()