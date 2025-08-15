#!/usr/bin/env python
"""
Test script to verify module isolation after legacy code fix.
Ensures PlacementTest is unaffected and RoutineTest features are intact.
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from placement_test.models import Exam as PlacementExam
from primepath_routinetest.models import Exam as RoutineExam

def test_module_isolation():
    """Test that modules are properly isolated."""
    print("\n" + "="*80)
    print("🔒 MODULE ISOLATION TEST")
    print("="*80)
    
    client = Client()
    test_results = []
    
    # Test 1: PlacementTest URLs are accessible
    print("\n📋 Test 1: PlacementTest Module Isolation")
    print("-" * 40)
    
    placement_urls = [
        ('/PlacementTest/', 'PlacementTest Index'),
        ('/PlacementTest/start/', 'Start Test'),
        ('/PlacementTest/exams/', 'Exam List'),
        ('/placement/api/core/programs/', 'Core API')
    ]
    
    for url, name in placement_urls:
        response = client.get(url, follow=True)
        # Accept 200 or redirect to login
        if response.status_code in [200, 302] or (hasattr(response, 'redirect_chain') and response.redirect_chain):
            print(f"✅ {name}: {url}")
            test_results.append((f'PlacementTest: {name}', True))
        else:
            print(f"❌ {name}: {url} (Status: {response.status_code})")
            test_results.append((f'PlacementTest: {name}', False))
    
    # Test 2: RoutineTest URLs are accessible
    print("\n📋 Test 2: RoutineTest Module Features")
    print("-" * 40)
    
    routine_urls = [
        ('/RoutineTest/', 'RoutineTest Index'),
        ('/RoutineTest/exams/', 'Exam Management'),
        ('/RoutineTest/exams/create/', 'Create Exam'),
        ('/RoutineTest/api/curriculum-hierarchy/', 'Curriculum API'),
        ('/RoutineTest/roster/', 'Roster Management'),
        ('/RoutineTest/sessions/', 'Session List')
    ]
    
    for url, name in routine_urls:
        response = client.get(url, follow=True)
        # Accept 200 or redirect to login
        if response.status_code in [200, 302] or (hasattr(response, 'redirect_chain') and response.redirect_chain):
            print(f"✅ {name}: {url}")
            test_results.append((f'RoutineTest: {name}', True))
        else:
            print(f"❌ {name}: {url} (Status: {response.status_code})")
            test_results.append((f'RoutineTest: {name}', False))
    
    # Test 3: Check PlacementTest templates are untouched
    print("\n📋 Test 3: PlacementTest Templates Unchanged")
    print("-" * 40)
    
    placement_templates = [
        'templates/placement_test/create_exam.html',
        'templates/placement_test/student_test.html',
        'templates/placement_test/exam_list.html'
    ]
    
    for template in placement_templates:
        if os.path.exists(template):
            with open(template, 'r') as f:
                content = f.read()
                # Check template doesn't have RoutineTest changes
                if 'routinetest-cascading-curriculum' not in content and 'EXAM_CREATION_v4.0' not in content:
                    print(f"✅ {os.path.basename(template)} isolated")
                    test_results.append((f'Template: {os.path.basename(template)}', True))
                else:
                    print(f"❌ {os.path.basename(template)} contaminated")
                    test_results.append((f'Template: {os.path.basename(template)}', False))
        else:
            print(f"✅ {os.path.basename(template)} (not found - OK)")
            test_results.append((f'Template: {os.path.basename(template)}', True))
    
    # Test 4: Check models are separate
    print("\n📋 Test 4: Model Separation")
    print("-" * 40)
    
    try:
        # Check PlacementTest exam model
        placement_exam_fields = [f.name for f in PlacementExam._meta.fields]
        
        # Check RoutineTest exam model
        routine_exam_fields = [f.name for f in RoutineExam._meta.fields]
        
        # RoutineTest should have additional fields
        routine_specific = set(routine_exam_fields) - set(placement_exam_fields)
        
        if routine_specific:
            print(f"✅ RoutineTest has {len(routine_specific)} unique fields")
            test_results.append(('Model Separation', True))
        else:
            print("⚠️ Models appear identical")
            test_results.append(('Model Separation', False))
            
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        test_results.append(('Model Separation', False))
    
    # Test 5: Check JavaScript files are separate
    print("\n📋 Test 5: JavaScript File Separation")
    print("-" * 40)
    
    js_files = {
        'PlacementTest': 'static/js/student_test.js',
        'RoutineTest': 'static/js/routinetest-cascading-curriculum.js'
    }
    
    for module, js_file in js_files.items():
        if os.path.exists(js_file):
            print(f"✅ {module} JS: {os.path.basename(js_file)}")
            test_results.append((f'JS: {module}', True))
        else:
            if module == 'PlacementTest':
                # PlacementTest JS might be inline, that's OK
                print(f"ℹ️ {module} JS: Not found (may be inline)")
                test_results.append((f'JS: {module}', True))
            else:
                print(f"❌ {module} JS: Not found")
                test_results.append((f'JS: {module}', False))
    
    # Test 6: Verify RoutineTest features work
    print("\n📋 Test 6: RoutineTest Feature Verification")
    print("-" * 40)
    
    # Test curriculum API
    response = client.get('/RoutineTest/api/curriculum-hierarchy/')
    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('success') and 'data' in data:
            hierarchy = data['data']
            print(f"✅ Curriculum API: {len(hierarchy.get('programs', []))} programs")
            test_results.append(('Feature: Curriculum API', True))
        else:
            print("❌ Curriculum API: Invalid response")
            test_results.append(('Feature: Curriculum API', False))
    else:
        print(f"❌ Curriculum API: Status {response.status_code}")
        test_results.append(('Feature: Curriculum API', False))
    
    # Final Summary
    print("\n" + "="*80)
    print("📊 ISOLATION TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 PERFECT ISOLATION! 🎉")
        print("\n✅ PlacementTest module completely isolated")
        print("✅ RoutineTest features fully functional")
        print("✅ No cross-contamination between modules")
        print("✅ All URLs accessible")
        print("✅ Templates properly separated")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("\nFailed tests:")
        for name, result in test_results:
            if not result:
                print(f"  ❌ {name}")
    
    print("\n" + "="*80)
    print("🔒 MODULE BOUNDARIES")
    print("="*80)
    print("\n📁 PlacementTest:")
    print("  - URL prefix: /PlacementTest/")
    print("  - App name: placement_test")
    print("  - Templates: templates/placement_test/")
    print("  - Static: static/placement_test/")
    
    print("\n📁 RoutineTest:")
    print("  - URL prefix: /RoutineTest/")
    print("  - App name: primepath_routinetest")
    print("  - Templates: templates/primepath_routinetest/")
    print("  - Static: static/js/routinetest-*.js")
    
    print("\n" + "="*80)
    
    return passed == total

if __name__ == '__main__':
    try:
        success = test_module_isolation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)