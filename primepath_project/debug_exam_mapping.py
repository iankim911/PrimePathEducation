#!/usr/bin/env python
"""
Debug the exam mapping page to identify potential issues
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from core.models import CurriculumLevel, ExamLevelMapping
from placement_test.models import Exam

def debug_exam_mapping_page():
    """Debug the exam mapping page"""
    
    print("=== Debugging Exam Mapping Page ===\n")
    
    # 1. Check if we have required data
    print("1. Checking database data...")
    exams = Exam.objects.all()
    levels = CurriculumLevel.objects.all()
    mappings = ExamLevelMapping.objects.all()
    
    print(f"   - Exams: {exams.count()}")
    print(f"   - Curriculum Levels: {levels.count()}")
    print(f"   - Existing Mappings: {mappings.count()}")
    
    if exams.count() == 0:
        print("   ⚠️  WARNING: No exams found! Users won't be able to create mappings.")
        return
    
    if levels.count() == 0:
        print("   ⚠️  WARNING: No curriculum levels found! No levels to map to.")
        return
    
    # 2. Test the exam mapping view
    print("\n2. Testing exam mapping view...")
    client = Client()
    
    try:
        url = reverse('core:exam_mapping')
        print(f"   URL: {url}")
        
        response = client.get(url)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Page loads successfully")
            
            # Check if template renders without errors
            content = response.content.decode('utf-8')
            
            # Look for JavaScript errors in the template
            if 'window.ExamMapping' in content:
                print("   ✅ JavaScript ExamMapping object found")
            else:
                print("   ❌ JavaScript ExamMapping object NOT found")
            
            # Check if data is properly passed to template
            if 'availableExams[' in content:
                print("   ✅ Available exams data found in template")
            else:
                print("   ❌ Available exams data NOT found in template")
                
        else:
            print(f"   ❌ Page failed to load with status {response.status_code}")
            print(f"   Response: {response.content}")
            
    except Exception as e:
        print(f"   ❌ Error testing view: {e}")
    
    # 3. Test the save API endpoint
    print("\n3. Testing save API endpoint...")
    try:
        save_url = reverse('core:save_exam_mappings')
        print(f"   URL: {save_url}")
        
        # Test with empty data
        response = client.post(save_url, 
                             data='{"mappings": []}',
                             content_type='application/json')
        print(f"   Status Code (empty): {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Save endpoint responds correctly")
        else:
            print(f"   ❌ Save endpoint error: {response.content}")
            
    except Exception as e:
        print(f"   ❌ Error testing save endpoint: {e}")
    
    # 4. Check URL patterns
    print("\n4. Checking URL patterns...")
    try:
        from django.urls import get_resolver
        resolver = get_resolver()
        
        # Check if core URLs are properly configured
        core_patterns = []
        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'app_name') and pattern.app_name == 'core':
                core_patterns.extend([str(p.pattern) for p in pattern.url_patterns])
        
        print(f"   Core URL patterns found: {len(core_patterns)}")
        
        exam_mapping_found = any('exam-mapping' in pattern for pattern in core_patterns)
        save_mapping_found = any('save' in pattern for pattern in core_patterns)
        
        if exam_mapping_found:
            print("   ✅ Exam mapping URL pattern found")
        else:
            print("   ❌ Exam mapping URL pattern NOT found")
            
        if save_mapping_found:
            print("   ✅ Save mapping URL pattern found")
        else:
            print("   ❌ Save mapping URL pattern NOT found")
            
    except Exception as e:
        print(f"   ❌ Error checking URL patterns: {e}")
    
    # 5. Sample data inspection
    print("\n5. Sample data inspection...")
    
    if exams.exists():
        sample_exam = exams.first()
        print(f"   Sample exam: {sample_exam.name}")
        print(f"   Exam ID: {sample_exam.id} (type: {type(sample_exam.id)})")
        print(f"   Has PDF: {bool(sample_exam.pdf_file)}")
    
    if levels.exists():
        sample_level = levels.first()
        print(f"   Sample level: {sample_level}")
        print(f"   Level ID: {sample_level.id} (type: {type(sample_level.id)})")
    
    # 6. Test JavaScript data structure
    print("\n6. Testing JavaScript data preparation...")
    
    try:
        from core.views import exam_mapping  # Import the view function
        from django.http import HttpRequest
        
        # Create a mock request
        request = HttpRequest()
        request.method = 'GET'
        
        # Get the context data that would be passed to template
        # This is a bit complex since we can't easily call the view directly
        print("   (Context inspection would require more complex setup)")
        
    except Exception as e:
        print(f"   ❌ Error testing context: {e}")
    
    print("\n=== Debug Complete ===")

if __name__ == '__main__':
    debug_exam_mapping_page()