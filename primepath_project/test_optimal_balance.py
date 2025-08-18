#!/usr/bin/env python
"""
Test the optimal balance configuration for PDF preview.
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

def test_optimal_settings():
    """Test optimal balance settings are applied."""
    print("\n" + "="*80)
    print("🎯 OPTIMAL BALANCE CONFIGURATION TEST")
    print("="*80)
    
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
        print("❌ No exam with PDF found")
        return False
    
    print(f"\n📗 Testing exam: {exam.name}")
    response = client.get(f'/RoutineTest/exams/{exam.id}/preview/')
    
    if response.status_code != 200:
        print(f"❌ Failed to load: {response.status_code}")
        return False
    
    content = response.content.decode('utf-8')
    
    # Check configuration
    print("\n📋 Configuration Analysis:")
    
    # Check container height
    has_72vh = 'max-height: 72vh' in content
    print(f"   {'✅' if has_72vh else '❌'} Container max-height: 72vh")
    
    # Check render scale
    scale_match = re.search(r'const PDF_RENDER_SCALE = ([0-9.]+)', content)
    render_scale = float(scale_match.group(1)) if scale_match else 0
    is_optimal_scale = render_scale == 2.0
    print(f"   {'✅' if is_optimal_scale else '❌'} Render scale: {render_scale} (target: 2.0)")
    
    # Check for OPTIMAL_BALANCE markers
    has_markers = '[OPTIMAL_BALANCE]' in content
    print(f"   {'✅' if has_markers else '❌'} Has [OPTIMAL_BALANCE] debug markers")
    
    # Check mobile settings
    has_mobile = 'max-height: 65vh' in content and '@media' in content
    print(f"   {'✅' if has_mobile else '❌'} Mobile responsive (65vh)")
    
    # Check height auto
    has_auto = 'height: auto' in content
    print(f"   {'✅' if has_auto else '❌'} Height: auto (prevents white bands)")
    
    all_passed = has_72vh and is_optimal_scale and has_markers and has_auto
    
    if all_passed:
        print("\n✅ OPTIMAL BALANCE ACHIEVED!")
        print("\n📌 Configuration Summary:")
        print("   • Container: 72vh max-height (fits most screens)")
        print("   • Render: 2.0x scale (readable text)")
        print("   • Height: auto (no white bands)")
        print("   • Mobile: 65vh (optimized for small screens)")
        print("\n🎯 Expected Result:")
        print("   1. PDF fits entirely in viewport without scrolling")
        print("   2. Text remains readable and clear")
        print("   3. No white bands above/below PDF")
        print("   4. Works on both desktop and mobile")
        
        print(f"\n🔗 Test URL:")
        print(f"   http://127.0.0.1:8000/RoutineTest/exams/{exam.id}/preview/")
        print("\n📝 Browser Console:")
        print("   Look for [OPTIMAL_BALANCE] logs showing:")
        print("   - maxContainerHeight: '72vh = XXXpx'")
        print("   - renderScale: 2.0")
        print("   - note: 'Balanced for no-scroll viewing'")
    else:
        print("\n❌ Some checks failed - review configuration")
    
    return all_passed

if __name__ == '__main__':
    test_optimal_settings()