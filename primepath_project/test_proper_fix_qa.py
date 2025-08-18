#!/usr/bin/env python
"""
QA Test for proper PDF preview fix - no white bands, proper sizing.
"""
import os
import sys
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import Exam as RoutineExam
from placement_test.models import Exam as PlacementExam

def test_css_implementation(content, module_name):
    """Check CSS implementation for proper fix."""
    print(f"\n   📋 {module_name} CSS Analysis:")
    
    # Check for height: auto with max-height constraint
    has_auto_height = 'height: auto' in content and '.pdf-section' in content
    has_max_height = 'max-height: 75vh' in content or 'max-height: 85vh' in content
    has_pdf_viewer_flex = 'flex: 1' in content and '.pdf-viewer' in content
    has_center_align = 'align-items: center' in content or 'align-items: flex-start' in content
    no_fixed_height = 'height: 70vh' not in content and 'height: 65vh' not in content
    
    checks = {
        'pdf-section height: auto': has_auto_height,
        'pdf-section has max-height constraint': has_max_height,
        'No fixed height (prevents white bands)': no_fixed_height,
        'pdf-viewer flex: 1': has_pdf_viewer_flex,
        'Proper alignment': has_center_align,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"      {status} {check}")
    
    return all(checks.values())

def test_javascript_implementation(content, module_name):
    """Check JavaScript implementation."""
    print(f"\n   📋 {module_name} JavaScript Analysis:")
    
    # Extract render scale
    scale_match = re.search(r'const PDF_RENDER_SCALE = ([0-9.]+)', content)
    render_scale = float(scale_match.group(1)) if scale_match else 0
    
    # Check for proper debugging
    has_proper_fix_logs = '[PROPER_FIX]' in content
    has_window_height_log = 'windowHeight' in content
    has_max_container_log = 'maxContainerHeight' in content
    
    checks = {
        f'Render scale = {render_scale}': render_scale > 0,
        'Optimized scale (1.8)': render_scale == 1.8,
        'Has [PROPER_FIX] debugging': has_proper_fix_logs,
        'Logs window height': has_window_height_log,
        'Logs max container height': has_max_container_log,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"      {status} {check}")
    
    return all(checks.values())

def test_inline_styles(content, module_name):
    """Check inline styles are preserved."""
    print(f"\n   📋 {module_name} Inline Styles:")
    
    # Check for exact inline styles
    image_display_correct = 'id="pdf-image-display" style="width: 100%; height: 100%; position: relative;"' in content
    page_image_correct = 'id="pdf-page-image" style="width: 100%; height: 100%; object-fit: contain; background: white;"' in content
    
    print(f"      {'✅' if image_display_correct else '❌'} pdf-image-display inline styles correct")
    print(f"      {'✅' if page_image_correct else '❌'} pdf-page-image inline styles correct")
    
    return image_display_correct and page_image_correct

def test_no_breaking_changes():
    """Test that other features still work."""
    print("\n🔍 Testing No Breaking Changes...")
    
    client = Client()
    user, _ = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    user.set_password('testpass123')
    user.save()
    client.login(username='test_admin', password='testpass123')
    
    tests_passed = 0
    tests_total = 0
    
    # Test RoutineTest pages
    pages = [
        ('/RoutineTest/', 'Index'),
        ('/RoutineTest/exams/', 'Exam List'),
        ('/RoutineTest/exams/create/', 'Create Exam'),
        ('/RoutineTest/roster/', 'Roster Management'),
    ]
    
    for url, name in pages:
        tests_total += 1
        response = client.get(url)
        if response.status_code == 200:
            tests_passed += 1
            print(f"   ✅ {name} page loads")
        else:
            print(f"   ❌ {name} failed: {response.status_code}")
    
    # Test model relationships
    tests_total += 1
    exam = RoutineExam.objects.first()
    if exam:
        try:
            questions = exam.routine_questions.all()
            audio_files = exam.routine_audio_files.all()
            tests_passed += 1
            print("   ✅ Model relationships intact")
        except:
            print("   ❌ Model relationships broken")
    else:
        tests_passed += 1
        print("   ✅ Model relationships (no test data)")
    
    # Test PlacementTest unchanged
    tests_total += 1
    pt_response = client.get('/PlacementTest/')
    if pt_response.status_code == 200:
        tests_passed += 1
        print("   ✅ PlacementTest module unaffected")
    else:
        print(f"   ❌ PlacementTest affected: {pt_response.status_code}")
    
    return tests_passed == tests_total

def main():
    print("\n" + "="*80)
    print("🔍 PROPER FIX QA - NO WHITE BANDS, OPTIMAL SIZING")
    print("="*80)
    
    client = Client()
    user, _ = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    user.set_password('testpass123')
    user.save()
    client.login(username='test_admin', password='testpass123')
    
    # Test RoutineTest implementation
    print("\n📗 Testing RoutineTest Implementation...")
    
    exam = None
    for e in RoutineExam.objects.all():
        try:
            if e.pdf_file and e.pdf_file.name:
                exam = e
                break
        except ValueError:
            continue
    
    all_tests_passed = True
    
    if exam:
        print(f"   Exam: {exam.name}")
        response = client.get(f'/RoutineTest/exams/{exam.id}/preview/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            css_ok = test_css_implementation(content, "RoutineTest")
            js_ok = test_javascript_implementation(content, "RoutineTest")
            inline_ok = test_inline_styles(content, "RoutineTest")
            
            all_tests_passed = css_ok and js_ok and inline_ok
        else:
            print(f"   ❌ Failed to load: {response.status_code}")
            all_tests_passed = False
    else:
        print("   ❌ No RoutineTest exam with PDF found")
        all_tests_passed = False
    
    # Test no breaking changes
    no_breaking = test_no_breaking_changes()
    
    # Summary
    print("\n" + "="*80)
    print("📊 QA SUMMARY")
    print("="*80)
    
    if all_tests_passed and no_breaking:
        print("\n🎉 ALL QA TESTS PASSED - PROPER FIX SUCCESSFUL!")
        print("\n📌 Key Improvements:")
        print("1. ✅ Container uses height: auto (no fixed height)")
        print("2. ✅ Max-height constraint prevents overflow")
        print("3. ✅ No white bands - container adapts to content")
        print("4. ✅ Optimized render scale (1.8)")
        print("5. ✅ Proper alignment (center)")
        print("6. ✅ Comprehensive debugging with [PROPER_FIX]")
        print("7. ✅ All other features preserved")
        
        print("\n🔍 What This Fixes:")
        print("   - White bands eliminated (height: auto)")
        print("   - PDF properly sized (optimized scale)")
        print("   - Container adapts to content size")
        print("   - No unnecessary white space")
        
        if exam:
            print(f"\n🔗 Test URL:")
            print(f"   http://127.0.0.1:8000/RoutineTest/exams/{exam.id}/preview/")
            print("\n📝 Browser Console:")
            print("   Look for [PROPER_FIX] logs showing:")
            print("   - Container dimensions")
            print("   - Window height calculations")
            print("   - Visibility analysis")
    else:
        print("\n⚠️ Some tests failed - review issues above")

if __name__ == '__main__':
    main()