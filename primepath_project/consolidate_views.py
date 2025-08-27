#!/usr/bin/env python
"""
Phase 6: View Layer Consolidation
Date: August 26, 2025
Purpose: Update all views to use the unified service registry
"""

import os
import re
from pathlib import Path


def consolidate_view_imports(file_path):
    """Update a view file to use the service registry."""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # Pattern replacements for service imports
    replacements = [
        # Direct service imports to registry
        (r'from placement_test\.services\.exam_service import ExamService',
         'from core.service_registry import ServiceRegistry\n# ExamService = ServiceRegistry.get("placement.exam")',
         'placement exam service'),
        
        (r'from primepath_routinetest\.services\.exam_service import ExamService',
         'from core.service_registry import ServiceRegistry\n# ExamService = ServiceRegistry.get("routine.exam")',
         'routine exam service'),
        
        (r'from core\.services import CurriculumService',
         'from core.service_registry import ServiceRegistry\n# CurriculumService = ServiceRegistry.get("curriculum")',
         'curriculum service'),
        
        # Update service usage patterns
        (r'ExamService\(\)\.', 'ServiceRegistry.get("placement.exam").', 'exam service calls'),
        (r'CurriculumService\(\)\.', 'ServiceRegistry.get("curriculum").', 'curriculum service calls'),
        (r'GradingService\(\)\.', 'ServiceRegistry.get("placement.grading").', 'grading service calls'),
    ]
    
    for pattern, replacement, description in replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes.append(description)
    
    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True, changes
    return False, []


def main():
    """Consolidate all view files."""
    
    print("=" * 80)
    print("VIEW LAYER CONSOLIDATION")
    print("=" * 80)
    
    view_dirs = [
        'placement_test/views',
        'primepath_routinetest/views',
        'primepath_student/views',
        'core/views',
    ]
    
    total_files = 0
    updated_files = 0
    all_changes = []
    
    for dir_path in view_dirs:
        if not os.path.exists(dir_path):
            continue
        
        print(f"\nProcessing {dir_path}...")
        
        for file_path in Path(dir_path).rglob('*.py'):
            if '__pycache__' in str(file_path):
                continue
            
            total_files += 1
            updated, changes = consolidate_view_imports(file_path)
            
            if updated:
                updated_files += 1
                all_changes.extend(changes)
                print(f"  ✅ Updated: {file_path.name}")
                for change in changes:
                    print(f"     - {change}")
    
    print("\n" + "=" * 80)
    print("CONSOLIDATION COMPLETE")
    print("=" * 80)
    print(f"Total files processed: {total_files}")
    print(f"Files updated: {updated_files}")
    print(f"Service references consolidated: {len(set(all_changes))}")
    
    if updated_files > 0:
        print("\n✅ View layer successfully consolidated to use service registry")
    else:
        print("\n✅ No view updates needed (already using registry or no service usage)")


if __name__ == '__main__':
    main()