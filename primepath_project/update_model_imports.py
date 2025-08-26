#!/usr/bin/env python3
"""
Step 1.1b: Update all import statements to use new model names
Phase 1 Foundation Stabilization - Model Namespace Resolution
"""

import os
import re
import sys

def update_imports_in_file(filepath):
    """Update import statements in a single file"""
    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Pattern 1: placement_test imports
        # from placement_test.models import Exam -> from placement_test.models import PlacementExam as PlacementExam as Exam
        placement_patterns = [
            # Direct model imports
            (r'from placement_test\.models import ([^,\n]*\b)Exam(\b[^,\n]*)', 
             r'from placement_test.models import \1PlacementExam as PlacementExam as Exam\2'),
            (r'from placement_test\.models import ([^,\n]*\b)AudioFile(\b[^,\n]*)', 
             r'from placement_test.models import \1PlacementAudioFile as PlacementAudioFile as AudioFile\2'),
            
            # Multiple imports with Exam
            (r'from placement_test\.models import ([^,\n]+,\s*)Exam(\s*,\s*[^,\n]*)', 
             r'from placement_test.models import \1PlacementExam as PlacementExam as Exam\2'),
            (r'from placement_test\.models import ([^,\n]+,\s*)AudioFile(\s*,\s*[^,\n]*)', 
             r'from placement_test.models import \1PlacementAudioFile as PlacementAudioFile as AudioFile\2'),
            
            # Single model imports
            (r'from placement_test\.models import Exam\s*$', 
             r'from placement_test.models import PlacementExam as PlacementExam as Exam'),
            (r'from placement_test\.models import AudioFile\s*$', 
             r'from placement_test.models import PlacementAudioFile as PlacementAudioFile as AudioFile'),
        ]
        
        # Pattern 2: primepath_routinetest imports
        routine_patterns = [
            # Direct model imports
            (r'from primepath_routinetest\.models import ([^,\n]*\b)Exam(\b[^,\n]*)', 
             r'from primepath_routinetest.models import \1RoutineExam as RoutineExam as Exam\2'),
            (r'from primepath_routinetest\.models import ([^,\n]*\b)AudioFile(\b[^,\n]*)', 
             r'from primepath_routinetest.models import \1RoutineAudioFile as RoutineAudioFile as AudioFile\2'),
            
            # Multiple imports with Exam
            (r'from primepath_routinetest\.models import ([^,\n]+,\s*)Exam(\s*,\s*[^,\n]*)', 
             r'from primepath_routinetest.models import \1RoutineExam as RoutineExam as Exam\2'),
            (r'from primepath_routinetest\.models import ([^,\n]+,\s*)AudioFile(\s*,\s*[^,\n]*)', 
             r'from primepath_routinetest.models import \1RoutineAudioFile as RoutineAudioFile as AudioFile\2'),
            
            # Single model imports
            (r'from primepath_routinetest\.models import Exam\s*$', 
             r'from primepath_routinetest.models import RoutineExam as RoutineExam as Exam'),
            (r'from primepath_routinetest\.models import AudioFile\s*$', 
             r'from primepath_routinetest.models import RoutineAudioFile as RoutineAudioFile as AudioFile'),
        ]
        
        # Apply placement_test patterns
        for pattern, replacement in placement_patterns:
            new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
            if count > 0:
                changes_made.append(f"placement_test pattern: {count} replacements")
                content = new_content
        
        # Apply primepath_routinetest patterns
        for pattern, replacement in routine_patterns:
            new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
            if count > 0:
                changes_made.append(f"primepath_routinetest pattern: {count} replacements")
                content = new_content
        
        # Special case: Handle complex multi-line imports (more conservative approach)
        # Look for patterns like: from ..models import (\n    Exam,\n    Question\n)
        multiline_pattern = r'(from (?:placement_test|primepath_routinetest)\.models import[^(]*\([^)]*)\bExam\b([^)]*\))'
        if re.search(multiline_pattern, content, re.DOTALL):
            # This is complex - for now, flag it for manual review
            changes_made.append("MANUAL REVIEW NEEDED: Multi-line import with Exam found")
        
        # Write back if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Updated: {', '.join(changes_made)}")
            return True
        else:
            print(f"  ⏭️  No changes needed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False

def main():
    """Main function to update all Python files"""
    
    print("🔄 Step 1.1b: Updating Import Statements")
    print("="*50)
    
    # Get current directory (should be primepath_project)
    current_dir = os.getcwd()
    print(f"Working directory: {current_dir}")
    
    # Find all Python files that might have these imports
    files_to_process = []
    
    # Walk through the directory
    for root, dirs, files in os.walk('.'):
        # Skip backup directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('primepath_project_backup_') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                # Check if file contains the imports we need to update
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if ('from placement_test.models import' in content or 
                            'from primepath_routinetest.models import' in content):
                            files_to_process.append(filepath)
                except:
                    pass  # Skip files we can't read
    
    print(f"Found {len(files_to_process)} files to process")
    print()
    
    updated_count = 0
    total_files = len(files_to_process)
    
    for filepath in sorted(files_to_process):
        if update_imports_in_file(filepath):
            updated_count += 1
    
    print()
    print("="*50)
    print(f"📊 SUMMARY")
    print(f"Total files processed: {total_files}")
    print(f"Files updated: {updated_count}")
    print(f"Files unchanged: {total_files - updated_count}")
    
    if updated_count > 0:
        print()
        print("✅ Import statements updated successfully!")
        print("🔍 Please review any files marked for MANUAL REVIEW")
    else:
        print()
        print("ℹ️  No files needed updating (backward compatibility working)")

if __name__ == '__main__':
    main()