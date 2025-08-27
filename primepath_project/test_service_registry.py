#!/usr/bin/env python
"""
Phase 4: Test Service Registry
Date: August 26, 2025
Purpose: Verify all services are properly registered and accessible
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.service_registry import ServiceRegistry, initialize_services


def test_service_registry():
    """Test the service registry functionality."""
    
    print("=" * 80)
    print("TESTING SERVICE REGISTRY")
    print("=" * 80)
    
    # Initialize services
    print("\n1. Initializing services...")
    try:
        initialize_services()
        print("✅ Services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False
    
    # List all registered services
    print("\n2. Registered services:")
    services = ServiceRegistry.list_services()
    for service_name in sorted(services):
        print(f"   ✅ {service_name}")
    print(f"   Total: {len(services)} services")
    
    # Test service retrieval
    print("\n3. Testing service retrieval:")
    test_cases = [
        ('curriculum', 'CurriculumService'),
        ('placement.exam', 'PlacementExamService'),
        ('routine.exam', 'RoutineExamService'),
        ('placement.grading', 'PlacementGradingService'),
        ('routine.grading', 'RoutineGradingService'),
    ]
    
    all_passed = True
    for service_key, expected_class in test_cases:
        try:
            service = ServiceRegistry.get(service_key)
            class_name = service.__class__.__name__
            if expected_class in str(service.__class__):
                print(f"   ✅ {service_key} -> {class_name}")
            else:
                print(f"   ❌ {service_key} -> Wrong class: {class_name}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ {service_key} -> Error: {e}")
            all_passed = False
    
    # Test convenience functions
    print("\n4. Testing convenience functions:")
    from core.service_registry import get_exam_service, get_grading_service
    
    try:
        placement_exam = get_exam_service('placement')
        routine_exam = get_exam_service('routine')
        print(f"   ✅ get_exam_service('placement') -> {placement_exam.__class__.__name__}")
        print(f"   ✅ get_exam_service('routine') -> {routine_exam.__class__.__name__}")
    except Exception as e:
        print(f"   ❌ Exam service error: {e}")
        all_passed = False
    
    # Test for duplicates
    print("\n5. Checking for duplicate registrations:")
    service_classes = {}
    duplicates = []
    for service_name in services:
        service = ServiceRegistry.get(service_name)
        class_name = service.__class__.__name__
        if class_name in service_classes:
            duplicates.append(f"{service_name} and {service_classes[class_name]} -> {class_name}")
        else:
            service_classes[class_name] = service_name
    
    if duplicates:
        print("   ❌ Found duplicate service classes:")
        for dup in duplicates:
            print(f"      - {dup}")
        all_passed = False
    else:
        print("   ✅ No duplicate service classes found")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL SERVICE REGISTRY TESTS PASSED!")
        print("Phase 4 Service Layer Cleanup: COMPLETE")
    else:
        print("⚠️  Some tests failed, review needed")
    print("=" * 80)
    
    return all_passed


if __name__ == '__main__':
    success = test_service_registry()
    sys.exit(0 if success else 1)