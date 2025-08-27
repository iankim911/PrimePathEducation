#!/usr/bin/env python
"""
Phase 5: Test Schema Consolidation Plan
Date: August 26, 2025
Purpose: Validate schema consolidation strategy
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.schema_consolidation import SchemaConsolidation
from django.db import connection


def test_consolidation_plan():
    """Test the schema consolidation plan."""
    
    print("=" * 80)
    print("SCHEMA CONSOLIDATION PLAN")
    print("=" * 80)
    
    # Get the migration plan
    plan = SchemaConsolidation.get_migration_plan()
    
    print("\nMIGRATION STEPS:")
    for step in plan:
        print(f"\nStep {step['step']}: {step['action']}")
        print(f"  Description: {step['description']}")
        if 'models' in step:
            print(f"  Models: {', '.join(step['models'])}")
        if 'tables' in step:
            print(f"  Tables: {', '.join(step['tables'][:3])}...")
    
    # Validate current schema
    print("\n" + "=" * 80)
    print("SCHEMA VALIDATION")
    print("=" * 80)
    
    is_valid, issues = SchemaConsolidation.validate_schema()
    if is_valid:
        print("✅ Schema is ready for consolidation")
    else:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    
    # Calculate benefits
    print("\n" + "=" * 80)
    print("CONSOLIDATION BENEFITS")
    print("=" * 80)
    
    benefits = SchemaConsolidation.get_benefits()
    for key, value in benefits.items():
        if isinstance(value, int) and value > 1000:
            # Format large numbers
            print(f"{key.replace('_', ' ').title()}: {value:,}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Check current duplicate data
    print("\n" + "=" * 80)
    print("DUPLICATE DATA ANALYSIS")
    print("=" * 80)
    
    cursor = connection.cursor()
    
    # Check duplicate questions
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM placement_test_question) as placement_q,
            (SELECT COUNT(*) FROM primepath_routinetest_question) as routine_q
    """)
    p_q, r_q = cursor.fetchone()
    print(f"Questions: {p_q} in placement_test, {r_q} in primepath_routinetest")
    
    # Check duplicate sessions
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM placement_test_studentsession) as placement_s,
            (SELECT COUNT(*) FROM primepath_routinetest_studentsession) as routine_s
    """)
    result = cursor.fetchone()
    if result:
        p_s, r_s = result
        print(f"Sessions: {p_s or 0} in placement_test, {r_s or 0} in primepath_routinetest")
    
    # Check orphaned tables
    print("\nOrphaned Tables Check:")
    for table in SchemaConsolidation.ORPHANED_TABLES[:5]:
        cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE name='{table}'")
        exists = cursor.fetchone()[0] > 0
        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records {'⚠️ ' if count > 0 else '✅ empty'}")
        else:
            print(f"  {table}: ✅ already removed")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    if is_valid:
        print("✅ SAFE TO PROCEED with schema consolidation")
        print("Benefits:")
        print(f"  • Remove {benefits['duplicate_models_removed']} duplicate models")
        print(f"  • Reduce tables from {benefits['current_tables']} to {benefits['after_consolidation']}")
        print(f"  • Save ~{benefits['size_reduction_percent']}% database size")
        print(f"  • Improve query performance and maintenance")
    else:
        print("⚠️  RESOLVE ISSUES before proceeding with consolidation")
        print("Issues to fix:")
        for issue in issues[:3]:
            print(f"  • {issue}")
    
    return is_valid


if __name__ == '__main__':
    success = test_consolidation_plan()
    sys.exit(0 if success else 1)