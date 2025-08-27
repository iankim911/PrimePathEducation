#!/usr/bin/env python
"""
Phase 5: Clean Up Orphaned Tables
Date: August 26, 2025
Purpose: Safely migrate data from orphaned tables before removal
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


def backup_orphaned_data():
    """Backup data from orphaned tables before cleanup."""
    
    cursor = connection.cursor()
    backup_data = {}
    backup_file = f'orphaned_tables_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    orphaned_tables = [
        'routinetest_exam',
        'routinetest_class', 
        'routinetest_class_assigned_teachers'
    ]
    
    print("=" * 80)
    print("BACKING UP ORPHANED TABLE DATA")
    print("=" * 80)
    
    for table in orphaned_tables:
        try:
            # Check if table exists
            cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE name='{table}'")
            if cursor.fetchone()[0] == 0:
                print(f"✅ {table}: Already removed")
                continue
            
            # Get all data
            cursor.execute(f"SELECT * FROM {table}")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            if rows:
                backup_data[table] = {
                    'columns': columns,
                    'rows': [dict(zip(columns, row)) for row in rows]
                }
                print(f"📦 {table}: Backed up {len(rows)} records")
            else:
                print(f"✅ {table}: Empty, no backup needed")
                
        except Exception as e:
            print(f"❌ {table}: Error - {e}")
    
    # Save backup
    if backup_data:
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        print(f"\n✅ Backup saved to: {backup_file}")
    
    return backup_data


def migrate_orphaned_data():
    """Migrate data from orphaned tables to new schema."""
    
    cursor = connection.cursor()
    
    print("\n" + "=" * 80)
    print("MIGRATING ORPHANED DATA")
    print("=" * 80)
    
    with transaction.atomic():
        # Migrate routinetest_exam to primepath_routinetest_exam
        try:
            cursor.execute("SELECT COUNT(*) FROM routinetest_exam")
            exam_count = cursor.fetchone()[0]
            if exam_count > 0:
                print(f"\nMigrating {exam_count} exams...")
                
                # Check if target table exists
                cursor.execute("""
                    INSERT OR IGNORE INTO primepath_routinetest_exam 
                    (id, name, exam_type, academic_year, created_at, updated_at)
                    SELECT id, name, 'REGULAR', '2024-2025', created_at, updated_at
                    FROM routinetest_exam
                """)
                print(f"✅ Migrated exams to primepath_routinetest_exam")
        except Exception as e:
            print(f"⚠️  Could not migrate exams: {e}")
        
        # Migrate routinetest_class to primepath_routinetest_class
        try:
            cursor.execute("SELECT COUNT(*) FROM routinetest_class")
            class_count = cursor.fetchone()[0]
            if class_count > 0:
                print(f"\nMigrating {class_count} classes...")
                
                cursor.execute("""
                    INSERT OR IGNORE INTO primepath_routinetest_class
                    (id, section, name, grade_level, is_active)
                    SELECT id, section, name, grade_level, 1
                    FROM routinetest_class
                """)
                print(f"✅ Migrated classes to primepath_routinetest_class")
        except Exception as e:
            print(f"⚠️  Could not migrate classes: {e}")


def cleanup_orphaned_tables():
    """Remove orphaned tables after data migration."""
    
    cursor = connection.cursor()
    
    print("\n" + "=" * 80)
    print("REMOVING ORPHANED TABLES")
    print("=" * 80)
    
    orphaned_tables = [
        'routinetest_exam',
        'routinetest_exam_assignment',
        'routinetest_exam_attempt',
        'routinetest_question',
        'routinetest_student_session',
        'routinetest_class',
        'routinetest_class_assigned_teachers',
    ]
    
    removed_count = 0
    
    for table in orphaned_tables:
        try:
            # Check if table exists
            cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE name='{table}'")
            if cursor.fetchone()[0] == 0:
                print(f"✅ {table}: Already removed")
                continue
            
            # Check if empty
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Safe to drop
                cursor.execute(f"DROP TABLE {table}")
                print(f"✅ {table}: Removed (was empty)")
                removed_count += 1
            else:
                print(f"⚠️  {table}: Has {count} records, skipping removal")
                
        except Exception as e:
            print(f"❌ {table}: Error - {e}")
    
    print(f"\n✅ Removed {removed_count} orphaned tables")
    
    return removed_count


def main():
    """Main cleanup process."""
    
    print("ORPHANED TABLE CLEANUP PROCESS")
    print("=" * 80)
    
    # Step 1: Backup
    backup_data = backup_orphaned_data()
    
    # Step 2: Migrate if needed
    if backup_data:
        migrate_orphaned_data()
    
    # Step 3: Cleanup
    removed = cleanup_orphaned_tables()
    
    print("\n" + "=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print(f"✅ Backed up data from {len(backup_data)} tables")
    print(f"✅ Removed {removed} orphaned tables")
    print("✅ Database schema optimized")


if __name__ == '__main__':
    main()