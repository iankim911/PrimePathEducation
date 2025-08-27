#!/usr/bin/env python
"""
Phase 8: Comprehensive Testing of All Remediation Phases
Date: August 26, 2025
Purpose: Validate all phases are working correctly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection
from core.service_registry import ServiceRegistry, initialize_services
from pathlib import Path
import importlib


def test_phase2_model_separation():
    """Test Phase 2: Model namespace separation."""
    print("\nTesting Phase 2: Model Separation...")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test renamed models can be imported
    try:
        from placement_test.models import PlacementExam, PlacementAudioFile
        from primepath_routinetest.models import RoutineExam, RoutineAudioFile
        tests_passed += 1
        print("  ✅ Renamed models import correctly")
    except ImportError as e:
        tests_failed += 1
        print(f"  ❌ Model import failed: {e}")
    
    # Test backward compatibility
    try:
        from placement_test.models import Exam as PlacementExamAlias
        from primepath_routinetest.models import Exam as RoutineExamAlias
        tests_passed += 1
        print("  ✅ Backward compatibility aliases work")
    except ImportError:
        tests_failed += 1
        print("  ❌ Backward compatibility failed")
    
    # Test database queries
    try:
        p_count = PlacementExam.objects.count()
        r_count = RoutineExam.objects.count()
        tests_passed += 1
        print(f"  ✅ Database queries work ({p_count} placement, {r_count} routine)")
    except Exception as e:
        tests_failed += 1
        print(f"  ❌ Database query failed: {e}")
    
    return tests_passed, tests_failed


def test_phase3_template_unification():
    """Test Phase 3: Template unification."""
    print("\nTesting Phase 3: Template Unification...")
    
    tests_passed = 0
    tests_failed = 0
    
    # Check unified_base.html exists
    template_path = Path('templates/unified_base.html')
    if template_path.exists():
        tests_passed += 1
        print("  ✅ unified_base.html exists")
    else:
        tests_failed += 1
        print("  ❌ unified_base.html not found")
    
    # Check templates are migrated
    template_dirs = ['placement_test/templates', 'primepath_routinetest/templates']
    migrated_count = 0
    
    for dir_path in template_dirs:
        if Path(dir_path).exists():
            for template in Path(dir_path).rglob('*.html'):
                with open(template, 'r') as f:
                    if 'unified_base.html' in f.read():
                        migrated_count += 1
    
    if migrated_count > 0:
        tests_passed += 1
        print(f"  ✅ {migrated_count} templates migrated to unified base")
    else:
        tests_failed += 1
        print("  ⚠️  No templates using unified base (may be OK)")
    
    return tests_passed, tests_failed


def test_phase4_service_registry():
    """Test Phase 4: Service registry."""
    print("\nTesting Phase 4: Service Registry...")
    
    tests_passed = 0
    tests_failed = 0
    
    # Initialize services if not already done
    try:
        if len(ServiceRegistry.list_services()) == 0:
            initialize_services()
        tests_passed += 1
        print("  ✅ Service registry initialized")
    except Exception as e:
        tests_failed += 1
        print(f"  ❌ Service initialization failed: {e}")
    
    # Test service count
    services = ServiceRegistry.list_services()
    if len(services) >= 17:
        tests_passed += 1
        print(f"  ✅ {len(services)} services registered")
    else:
        tests_failed += 1
        print(f"  ❌ Only {len(services)} services (expected 17+)")
    
    # Test service retrieval
    try:
        curriculum = ServiceRegistry.get('curriculum')
        tests_passed += 1
        print("  ✅ Service retrieval works")
    except:
        tests_failed += 1
        print("  ❌ Service retrieval failed")
    
    return tests_passed, tests_failed


def test_phase5_schema_optimization():
    """Test Phase 5: Schema optimization."""
    print("\nTesting Phase 5: Database Schema...")
    
    tests_passed = 0
    tests_failed = 0
    
    cursor = connection.cursor()
    
    # Test orphaned tables handled
    orphaned = ['routinetest_exam_assignment', 'routinetest_exam_attempt']
    for table in orphaned:
        cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE name='{table}'")
        if cursor.fetchone()[0] == 0:
            tests_passed += 1
            print(f"  ✅ {table} removed")
        else:
            tests_failed += 1
            print(f"  ❌ {table} still exists")
    
    # Test database integrity
    cursor.execute("PRAGMA integrity_check")
    if cursor.fetchone()[0] == 'ok':
        tests_passed += 1
        print("  ✅ Database integrity OK")
    else:
        tests_failed += 1
        print("  ❌ Database integrity issues")
    
    return tests_passed, tests_failed


def test_phase7_api_unification():
    """Test Phase 7: API unification."""
    print("\nTesting Phase 7: API Unification...")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test API router exists
    api_path = Path('api/unified_router.py')
    if api_path.exists():
        tests_passed += 1
        print("  ✅ Unified API router created")
    else:
        tests_failed += 1
        print("  ❌ API router not found")
    
    # Test API router can be imported
    try:
        from api.unified_router import UnifiedAPIRouter
        tests_passed += 1
        print("  ✅ API router imports correctly")
    except ImportError:
        tests_failed += 1
        print("  ❌ API router import failed")
    
    return tests_passed, tests_failed


def main():
    """Run all phase tests."""
    
    print("=" * 80)
    print("COMPREHENSIVE PHASE TESTING")
    print("=" * 80)
    
    total_passed = 0
    total_failed = 0
    
    # Run all phase tests
    phases = [
        ('Phase 2', test_phase2_model_separation),
        ('Phase 3', test_phase3_template_unification),
        ('Phase 4', test_phase4_service_registry),
        ('Phase 5', test_phase5_schema_optimization),
        ('Phase 7', test_phase7_api_unification),
    ]
    
    for phase_name, test_func in phases:
        passed, failed = test_func()
        total_passed += passed
        total_failed += failed
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests Passed: {total_passed}")
    print(f"Total Tests Failed: {total_failed}")
    print(f"Success Rate: {total_passed / (total_passed + total_failed) * 100:.1f}%")
    
    if total_failed == 0:
        print("\n🎆 ALL PHASES VALIDATED SUCCESSFULLY! 🎆")
        print("The architectural remediation is complete and functional.")
    else:
        print(f"\n⚠️  {total_failed} tests failed - review needed")
    
    return total_failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)