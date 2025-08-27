#!/usr/bin/env python
"""
Phase 5: Safe Orphaned Table Cleanup
Date: August 26, 2025  
Purpose: Safely handle orphaned tables without breaking FK constraints
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection


def safe_cleanup():
    """Safely handle orphaned tables."""
    
    cursor = connection.cursor()
    
    print("=" * 80)
    print("SAFE ORPHANED TABLE ANALYSIS")
    print("=" * 80)
    
    # First, disable foreign keys temporarily
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    orphaned_tables = [
        'routinetest_exam',
        'routinetest_class', 
        'routinetest_class_assigned_teachers',
        'routinetest_exam_assignment',
        'routinetest_exam_attempt',
        'routinetest_question',
        'routinetest_student_session',
    ]
    
    summary = {
        'removed': [],
        'kept': [],
        'errors': []
    }
    
    for table in orphaned_tables:
        try:
            # Check if table exists
            cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE name='{table}'")
            if cursor.fetchone()[0] == 0:
                print(f"✅ {table}: Already removed")
                continue
            
            # Check if has data
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Safe to drop
                cursor.execute(f"DROP TABLE {table}")
                print(f"✅ {table}: Removed (was empty)")
                summary['removed'].append(table)
            else:
                # Keep for now
                print(f"⚠️  {table}: Kept ({count} records need review)")
                summary['kept'].append((table, count))
                
        except Exception as e:
            print(f"❌ {table}: Error - {e}")
            summary['errors'].append((table, str(e)))
    
    # Re-enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    print("\n" + "=" * 80)
    print("CLEANUP SUMMARY")
    print("=" * 80)
    
    print(f"\nRemoved {len(summary['removed'])} empty tables:")
    for table in summary['removed']:
        print(f"  ✅ {table}")
    
    print(f"\nKept {len(summary['kept'])} tables with data:")
    for table, count in summary['kept']:
        print(f"  ⚠️  {table}: {count} records")
    
    if summary['errors']:
        print(f"\nEncountered {len(summary['errors'])} errors:")
        for table, error in summary['errors']:
            print(f"  ❌ {table}: {error}")
    
    # Check database integrity
    print("\n" + "=" * 80)
    print("DATABASE INTEGRITY CHECK")
    print("=" * 80)
    
    cursor.execute("PRAGMA integrity_check")
    result = cursor.fetchone()[0]
    if result == 'ok':
        print("✅ Database integrity: OK")
    else:
        print(f"❌ Database integrity issues: {result}")
    
    # Count total tables
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    total_tables = cursor.fetchone()[0]
    print(f"\nTotal tables in database: {total_tables}")
    
    # Show schema consolidation readiness
    print("\n" + "=" * 80)
    print("SCHEMA CONSOLIDATION READINESS")
    print("=" * 80)
    
    ready = len(summary['kept']) <= 3  # Allow some orphaned data
    if ready:
        print("✅ READY for schema consolidation")
        print("   (Minor orphaned data can be handled separately)")
    else:
        print("⚠️  NOT READY for full consolidation")
        print(f"   Still have {len(summary['kept'])} tables with data to review")
    
    return ready


if __name__ == '__main__':
    ready = safe_cleanup()
    sys.exit(0 if ready else 1)