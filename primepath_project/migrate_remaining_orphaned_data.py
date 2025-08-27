#!/usr/bin/env python
"""
Phase 5: Complete Migration of Remaining Orphaned Data
Date: August 26, 2025
Purpose: Migrate all remaining orphaned data to proper tables
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection, transaction
import json
from datetime import datetime


def migrate_remaining_data():
    """Migrate remaining orphaned data to appropriate tables."""
    
    cursor = connection.cursor()
    
    print("=" * 80)
    print("MIGRATING REMAINING ORPHANED DATA")
    print("=" * 80)
    
    with transaction.atomic():
        # 1. Clear out the routinetest_exam data (already migrated)
        try:
            cursor.execute("DELETE FROM routinetest_exam")
            print("✅ Cleared routinetest_exam (data already migrated)")
        except Exception as e:
            print(f"⚠️  Could not clear routinetest_exam: {e}")
        
        # 2. Migrate routinetest_class to Class model
        try:
            # First check if Class table exists
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='primepath_routinetest_class_model'")
            if cursor.fetchone()[0] == 0:
                # Try the standard Class table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS primepath_routinetest_class_model (
                        id INTEGER PRIMARY KEY,
                        section VARCHAR(100),
                        name VARCHAR(200),
                        grade_level VARCHAR(50),
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            # Copy data from old table
            cursor.execute("""
                INSERT OR IGNORE INTO primepath_routinetest_class_model 
                (id, section, name, grade_level, is_active)
                SELECT id, section, name, grade_level, 1 FROM routinetest_class
            """)
            
            cursor.execute("SELECT COUNT(*) FROM routinetest_class")
            count = cursor.fetchone()[0]
            print(f"✅ Migrated {count} classes to new table")
            
            # Clear the old table
            cursor.execute("DELETE FROM routinetest_class")
            print("✅ Cleared routinetest_class")
            
        except Exception as e:
            print(f"⚠️  Could not migrate classes: {e}")
        
        # 3. Clear routinetest_class_assigned_teachers (relationship table, can be recreated)
        try:
            cursor.execute("DELETE FROM routinetest_class_assigned_teachers")
            print("✅ Cleared routinetest_class_assigned_teachers")
        except Exception as e:
            print(f"⚠️  Could not clear teacher assignments: {e}")
    
    print("\n" + "=" * 80)
    print("REMOVING EMPTY ORPHANED TABLES")
    print("=" * 80)
    
    orphaned_tables = [
        'routinetest_exam',
        'routinetest_class',
        'routinetest_class_assigned_teachers'
    ]
    
    for table in orphaned_tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"✅ Removed {table}")
        except Exception as e:
            print(f"❌ Could not remove {table}: {e}")
    
    print("\n✅ Migration complete!")


if __name__ == '__main__':
    migrate_remaining_data()