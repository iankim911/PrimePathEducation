#!/usr/bin/env python
"""
Phase 4: Migrate Views to Use Service Registry
Date: August 26, 2025
Purpose: Update all views to use the unified service registry
"""

import os
import re
from pathlib import Path


# Mapping of old imports to new registry calls
SERVICE_MAPPINGS = {
    # Placement Test
    'from placement_test.services import ExamService': 'from core.service_registry import ServiceRegistry',
    'ExamService()': "ServiceRegistry.get('placement.exam')",
    'from placement_test.services import GradingService': 'from core.service_registry import ServiceRegistry',
    'GradingService()': "ServiceRegistry.get('placement.grading')",
    'from placement_test.services import SessionService': 'from core.service_registry import ServiceRegistry',
    'SessionService()': "ServiceRegistry.get('placement.session')",
    'from placement_test.services import PlacementService': 'from core.service_registry import ServiceRegistry',
    'PlacementService()': "ServiceRegistry.get('placement.rules')",
    
    # Routine Test
    'from primepath_routinetest.services import ExamService': 'from core.service_registry import ServiceRegistry',
    'from primepath_routinetest.services import GradingService': 'from core.service_registry import ServiceRegistry',
    'from primepath_routinetest.services import SessionService': 'from core.service_registry import ServiceRegistry',
    
    # Core services
    'from core.services import CurriculumService': 'from core.service_registry import ServiceRegistry',
    'CurriculumService()': "ServiceRegistry.get('curriculum')",
    'from core.services import TeacherService': 'from core.service_registry import ServiceRegistry',
    'TeacherService()': "ServiceRegistry.get('teacher')",
    'from core.services import SchoolService': 'from core.service_registry import ServiceRegistry',
    'SchoolService()': "ServiceRegistry.get('school')",
}


def migrate_file(file_path):
    """Migrate a single file to use service registry."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Apply mappings
    for old_pattern, new_pattern in SERVICE_MAPPINGS.items():
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            changes_made.append(f"  ✓ Replaced: {old_pattern[:50]}...")
    
    # Add service registry initialization if services are used
    if 'ServiceRegistry.get(' in content and 'initialize_services()' not in content:
        # Add initialization in appropriate place
        if 'def ready(self)' in content:
            # In app config
            content = re.sub(
                r'(def ready\(self\):.*?)(\n)',
                r'\1\n        from core.service_registry import initialize_services\n        initialize_services()\2',
                content,
                flags=re.DOTALL
            )
            changes_made.append("  ✓ Added service initialization in ready()")
    
    if content != original_content:
        return content, changes_made
    return None, []


def main():
    """Migrate all Python files to use service registry."""
    print("=" * 80)
    print("SERVICE REGISTRY MIGRATION")
    print("=" * 80)
    
    # Find all Python files in views
    view_files = []
    for app_dir in ['placement_test', 'primepath_routinetest', 'primepath_student', 'core']:
        app_path = Path(app_dir)
        if app_path.exists():
            view_files.extend(app_path.glob('**/views*.py'))
            view_files.extend(app_path.glob('views/*.py'))
    
    print(f"\nFound {len(view_files)} view files to check\n")
    
    migrated_count = 0
    
    for file_path in view_files:
        new_content, changes = migrate_file(file_path)
        if new_content:
            print(f"📄 {file_path}")
            for change in changes:
                print(change)
            
            # Write the changes
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            migrated_count += 1
            print()
    
    print("=" * 80)
    print(f"✅ Migrated {migrated_count} files to use service registry")
    print("=" * 80)
    
    # Create app initialization if needed
    create_app_initializers()


def create_app_initializers():
    """Create apps.py ready() methods to initialize services."""
    
    apps_configs = {
        'placement_test': 'PlacementTestConfig',
        'primepath_routinetest': 'PrimepathRoutinetestConfig',
        'core': 'CoreConfig',
    }
    
    for app_name, config_class in apps_configs.items():
        apps_file = Path(app_name) / 'apps.py'
        if apps_file.exists():
            with open(apps_file, 'r') as f:
                content = f.read()
            
            if 'def ready(' not in content and config_class in content:
                # Add ready method
                content = re.sub(
                    f'(class {config_class}.*?\n)',
                    f'''\\1
    def ready(self):
        """Initialize services when app is ready."""
        from core.service_registry import initialize_services
        try:
            initialize_services()
        except Exception:
            pass  # Services may already be initialized
\n''',
                    content,
                    flags=re.DOTALL
                )
                
                with open(apps_file, 'w') as f:
                    f.write(content)
                
                print(f"✅ Added service initialization to {apps_file}")


if __name__ == '__main__':
    main()