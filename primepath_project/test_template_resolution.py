#!/usr/bin/env python
"""
Test which template Django actually loads
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.template.loader import get_template
from django.template import TemplateDoesNotExist

def test_template_resolution():
    """Test which template Django actually loads"""
    
    template_names = [
        'primepath_routinetest/exam_list_hierarchical.html',
        'primepath_routinetest/exam_list.html'
    ]
    
    print("🔍 TEMPLATE RESOLUTION TEST")
    print("="*50)
    
    for template_name in template_names:
        try:
            template = get_template(template_name)
            print(f"✅ Template found: {template_name}")
            print(f"   File path: {template.origin.name if hasattr(template, 'origin') else 'Unknown'}")
            
            # Check if our fix comment is in the template
            try:
                with open(template.origin.name, 'r') as f:
                    template_source = f.read()
                if 'CRITICAL FIX: Never show VIEW ONLY badge when filter is active' in template_source:
                    print(f"   ✅ Contains our template fix comment")
                else:
                    print(f"   ❌ Missing our template fix comment")
                    
                if 'NUCLEAR_SAFETY' in template_source:
                    print(f"   ✅ Contains our JavaScript safety net")
                else:
                    print(f"   ❌ Missing our JavaScript safety net")
            except Exception as e:
                print(f"   ❓ Could not read template source: {e}")
                
        except TemplateDoesNotExist:
            print(f"❌ Template not found: {template_name}")
        
        print()
    
    # Test what happens when view requests exam_list_hierarchical.html
    print("🎯 TESTING VIEW'S TEMPLATE REQUEST")
    print("="*50)
    try:
        requested_template = get_template('primepath_routinetest/exam_list_hierarchical.html')
        print(f"✅ Django found: primepath_routinetest/exam_list_hierarchical.html")
        print(f"   Actual file: {requested_template.origin.name if hasattr(requested_template, 'origin') else 'Unknown'}")
        
        # Check if this is actually our modified template
        try:
            with open(requested_template.origin.name, 'r') as f:
                source = f.read()
            if 'CRITICAL FIX: Never show VIEW ONLY badge when filter is active' in source:
                print(f"   ✅ This IS our modified template")
            else:
                print(f"   ❌ This is NOT our modified template")
                
            # Check for JavaScript safety net
            if 'NUCLEAR_SAFETY' in source:
                print(f"   ✅ Contains our JavaScript safety net")
            else:
                print(f"   ❌ Missing our JavaScript safety net")
        except Exception as e:
            print(f"   ❓ Could not read template source: {e}")
            
    except TemplateDoesNotExist as e:
        print(f"❌ Template not found: {e}")

if __name__ == "__main__":
    test_template_resolution()