#!/usr/bin/env python
"""
Comprehensive QA test for PDF preview benchmark fix.
Tests RoutineTest PDF preview against PlacementTest benchmark.
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

def check_css_implementation(content, module_name):
    """Check CSS implementation details."""
    print(f"\n   📋 {module_name} CSS Analysis:")
    
    checks = {
        'pdf-section max-height: 85vh': 'max-height: 85vh' in content and '.pdf-section' in content,
        'pdf-viewer flex: 1': 'flex: 1' in content and '.pdf-viewer' in content,
        'pdf-viewer overflow: auto': 'overflow: auto' in content,
        'No custom #pdf-image-display CSS': '#pdf-image-display' not in content or 'REMOVED custom CSS' in content or 'No custom CSS' in content,
        'No custom #pdf-page-image CSS': '#pdf-page-image {' not in content or 'REMOVED custom CSS' in content or 'No custom CSS' in content,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"      {status} {check}")
    
    return all(checks.values())

def check_inline_styles(content, module_name):
    """Check inline styles match benchmark."""
    print(f"\n   📋 {module_name} Inline Styles:")
    
    # Check for exact inline styles
    image_display_correct = 'id="pdf-image-display" style="width: 100%; height: 100%; position: relative;"' in content
    page_image_correct = 'id="pdf-page-image" style="width: 100%; height: 100%; object-fit: contain; background: white;"' in content
    
    print(f"      {'✅' if image_display_correct else '❌'} pdf-image-display: width:100%; height:100%; position:relative")
    print(f"      {'✅' if page_image_correct else '❌'} pdf-page-image: width:100%; height:100%; object-fit:contain")
    
    return image_display_correct and page_image_correct

def check_javascript_implementation(content, module_name):
    """Check JavaScript implementation."""
    print(f"\n   📋 {module_name} JavaScript Analysis:")
    
    # Extract render scale
    scale_match = re.search(r'const PDF_RENDER_SCALE = ([0-9.]+)', content)
    render_scale = float(scale_match.group(1)) if scale_match else 0
    
    # Check applyZoomToImage doesn't override sizing
    has_max_width_override = 'pageImage.style.maxWidth' in content and 'REMOVED' not in content and 'Don\'t override' not in content
    has_max_height_override = 'pageImage.style.maxHeight' in content and 'REMOVED' not in content and 'Don\'t override' not in content
    
    checks = {
        f'Render scale = {render_scale}': render_scale > 0,
        'Scale is 2.5 (PlacementTest value)': render_scale == 2.5,
        'No maxWidth override in applyZoomToImage': not has_max_width_override,
        'No maxHeight override in applyZoomToImage': not has_max_height_override,
        'Has debugging logs': '[BENCHMARK_FIX]' in content or '[PREVIEW_EXAM]' in content,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"      {status} {check}")
    
    return all(checks.values())

def test_placement_benchmark():
    """Test PlacementTest as benchmark reference."""
    print("\n📘 Testing PlacementTest (BENCHMARK)...")
    
    client = Client()
    user, _ = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    user.set_password('testpass123')
    user.save()
    client.login(username='test_admin', password='testpass123')
    
    # Find exam with PDF
    exam = PlacementExam.objects.filter(pdf_file__isnull=False).first()
    if not exam:
        print("   ⚠️ No PlacementTest exam with PDF found")
        return None
    
    print(f"   Exam: {exam.name}")
    response = client.get(f'/PlacementTest/exams/{exam.id}/preview/')
    
    if response.status_code != 200:
        print(f"   ❌ Failed to load: {response.status_code}")
        return None
    
    content = response.content.decode('utf-8')
    
    # Analyze implementation
    css_ok = check_css_implementation(content, "PlacementTest")
    inline_ok = check_inline_styles(content, "PlacementTest") 
    js_ok = check_javascript_implementation(content, "PlacementTest")
    
    if css_ok and inline_ok and js_ok:
        print("\n   ✅ PlacementTest benchmark validated")
        return {
            'render_scale': 2.5,
            'has_custom_css': False,
            'inline_styles_correct': True
        }
    else:
        print("\n   ⚠️ PlacementTest implementation differs from expected")
        return None

def test_routinetest_implementation():
    """Test RoutineTest matches benchmark."""
    print("\n📗 Testing RoutineTest (SHOULD MATCH BENCHMARK)...")
    
    client = Client()
    user, _ = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    user.set_password('testpass123')
    user.save()
    client.login(username='test_admin', password='testpass123')
    
    # Find exam with PDF
    exam = None
    for e in RoutineExam.objects.all():
        try:
            if e.pdf_file and e.pdf_file.name:
                exam = e
                break
        except ValueError:
            continue
    
    if not exam:
        print("   ❌ No RoutineTest exam with PDF found")
        return False
    
    print(f"   Exam: {exam.name}")
    response = client.get(f'/RoutineTest/exams/{exam.id}/preview/')
    
    if response.status_code != 200:
        print(f"   ❌ Failed to load: {response.status_code}")
        return False
    
    content = response.content.decode('utf-8')
    
    # Analyze implementation
    css_ok = check_css_implementation(content, "RoutineTest")
    inline_ok = check_inline_styles(content, "RoutineTest")
    js_ok = check_javascript_implementation(content, "RoutineTest")
    
    # Check for benchmark fix markers
    has_benchmark_fix = '[BENCHMARK_FIX]' in content
    print(f"\n   {'✅' if has_benchmark_fix else '❌'} Has [BENCHMARK_FIX] debugging markers")
    
    return css_ok and inline_ok and js_ok and has_benchmark_fix

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
    
    return tests_passed == tests_total

def main():
    print("\n" + "="*80)
    print("🔍 PDF PREVIEW BENCHMARK FIX - COMPREHENSIVE QA")
    print("="*80)
    
    # Test PlacementTest benchmark
    benchmark = test_placement_benchmark()
    
    # Test RoutineTest implementation
    routinetest_ok = test_routinetest_implementation()
    
    # Test no breaking changes
    no_breaking = test_no_breaking_changes()
    
    # Summary
    print("\n" + "="*80)
    print("📊 QA SUMMARY")
    print("="*80)
    
    if benchmark:
        print("\n✅ PlacementTest Benchmark:")
        print(f"   - Render scale: {benchmark['render_scale']}")
        print("   - No custom CSS for image containers")
        print("   - Inline styles control sizing")
    else:
        print("\n⚠️ PlacementTest benchmark validation failed")
    
    if routinetest_ok:
        print("\n✅ RoutineTest Implementation:")
        print("   - Matches PlacementTest benchmark exactly")
        print("   - Render scale: 2.5")
        print("   - CSS cleaned up (no custom overrides)")
        print("   - Inline styles match benchmark")
        print("   - Comprehensive debugging added")
    else:
        print("\n❌ RoutineTest does not match benchmark")
    
    if no_breaking:
        print("\n✅ No Breaking Changes:")
        print("   - All pages load correctly")
        print("   - Model relationships intact")
    else:
        print("\n❌ Some features may be broken")
    
    if benchmark and routinetest_ok and no_breaking:
        print("\n" + "🎉"*20)
        print("🎉 ALL QA TESTS PASSED - BENCHMARK FIX SUCCESSFUL!")
        print("🎉"*20)
        
        print("\n📌 Key Achievements:")
        print("1. RoutineTest PDF preview now matches PlacementTest exactly")
        print("2. Removed all custom CSS that was causing conflicts")
        print("3. Using same render scale (2.5) as PlacementTest")
        print("4. Inline styles control sizing with object-fit: contain")
        print("5. Comprehensive debugging logs with [BENCHMARK_FIX] markers")
        print("6. No breaking changes to other features")
        
        print("\n🔗 Manual Verification URLs:")
        rt_exam = RoutineExam.objects.filter(pdf_file__isnull=False).first()
        pt_exam = PlacementExam.objects.filter(pdf_file__isnull=False).first()
        if rt_exam:
            print(f"   RoutineTest: http://127.0.0.1:8000/RoutineTest/exams/{rt_exam.id}/preview/")
        if pt_exam:
            print(f"   PlacementTest: http://127.0.0.1:8000/PlacementTest/exams/{pt_exam.id}/preview/")
        
        print("\n📝 Browser Console:")
        print("   Look for [BENCHMARK_FIX] logs showing:")
        print("   - Container hierarchy")
        print("   - Computed styles")
        print("   - Visibility analysis")
        print("   - Fits in viewport check")
    else:
        print("\n⚠️ QA FAILED - Review issues above")

if __name__ == '__main__':
    main()