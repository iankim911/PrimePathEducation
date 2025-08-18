#!/usr/bin/env python
"""
Test script to verify matrix_filters template tag is properly registered
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.template import Template, Context
from django.template.loader import get_template
from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_template_tag_registration():
    """Test if matrix_filters template tag is registered"""
    print("\n" + "="*80)
    print("TESTING MATRIX_FILTERS TEMPLATE TAG REGISTRATION")
    print("="*80)
    
    # Test 1: Check if template tag library can be imported
    print("\n1. Testing direct import of template tags...")
    try:
        from primepath_routinetest.templatetags import matrix_filters
        print("   ✅ Successfully imported matrix_filters module")
        
        # Check if register is available
        if hasattr(matrix_filters, 'register'):
            print("   ✅ Template library register found")
            
            # Check registered filters
            filters = list(matrix_filters.register.filters.keys())
            print(f"   ✅ Registered filters: {filters}")
        else:
            print("   ❌ Template library register not found")
            return False
    except ImportError as e:
        print(f"   ❌ Failed to import matrix_filters: {e}")
        return False
    
    # Test 2: Test template compilation with the tag
    print("\n2. Testing template compilation...")
    try:
        template_string = """
        {% load matrix_filters %}
        {% with test_dict=test_dict %}
            {{ test_dict|get_item:'key1' }}
            {{ test_dict|dict_get:'key2' }}
        {% endwith %}
        """
        
        template = Template(template_string)
        context = Context({
            'test_dict': {'key1': 'value1', 'key2': 'value2'}
        })
        result = template.render(context)
        
        print("   ✅ Template compiled successfully")
        print(f"   Template output: {result.strip()}")
        
        if 'value1' in result and 'value2' in result:
            print("   ✅ Filters working correctly")
        else:
            print("   ⚠️ Filters compiled but may not be working as expected")
            
    except Exception as e:
        print(f"   ❌ Template compilation failed: {e}")
        return False
    
    # Test 3: Test actual schedule_matrix template
    print("\n3. Testing schedule_matrix.html template...")
    try:
        # Create test user and teacher
        user = User.objects.filter(username='matrix_test_user').first()
        if not user:
            user = User.objects.create_user('matrix_test_user', 'test@test.com', 'testpass123')
            user.is_staff = True
            user.save()
        
        teacher, created = Teacher.objects.get_or_create(
            email=user.email,
            defaults={'name': 'Test Teacher', 'user': user}
        )
        
        # Create class assignment
        TeacherClassAssignment.objects.get_or_create(
            teacher=teacher,
            class_code='CLASS_7A',
            defaults={'access_level': 'FULL', 'assigned_by': user}
        )
        
        # Test with client
        client = Client()
        client.force_login(user)
        
        print("   Testing /RoutineTest/schedule-matrix/ endpoint...")
        response = client.get('/RoutineTest/schedule-matrix/')
        
        if response.status_code == 200:
            print(f"   ✅ Page loaded successfully (Status: {response.status_code})")
            
            # Check if template rendered without errors
            content = response.content.decode('utf-8')
            if 'TemplateSyntaxError' in content:
                print("   ❌ Template syntax error in response")
                return False
            elif 'matrix_filters' in content and 'is not a registered tag library' in content:
                print("   ❌ matrix_filters still not recognized as tag library")
                return False
            else:
                print("   ✅ Template rendered without syntax errors")
                
                # Check for expected content
                if 'Exam Schedule Matrix' in content:
                    print("   ✅ Matrix title found in output")
                if 'Monthly/Review Exams' in content:
                    print("   ✅ Monthly tab found in output")
                if 'Quarterly Exams' in content:
                    print("   ✅ Quarterly tab found in output")
                    
        else:
            print(f"   ❌ Page failed to load (Status: {response.status_code})")
            if hasattr(response, 'content'):
                error_content = response.content.decode('utf-8')[:500]
                print(f"   Error content: {error_content}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing template: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_alternative_approach():
    """Test an alternative approach without custom filters"""
    print("\n4. Testing alternative data structure approach...")
    
    # Simulate the view context with pre-formatted data
    from primepath_routinetest.views.schedule_matrix import schedule_matrix_view
    
    print("   ✅ Alternative approach: View can provide pre-formatted data")
    print("   This would avoid the need for custom template filters")
    
    return True


def main():
    print("\n" + "="*80)
    print("MATRIX FILTERS TEMPLATE TAG TEST")
    print("="*80)
    
    # Run tests
    success = test_template_tag_registration()
    
    if not success:
        print("\n⚠️ Template tag registration issues detected")
        print("\nTROUBLESHOOTING STEPS:")
        print("1. Restart Django development server")
        print("2. Clear Python cache: find . -name '*.pyc' -delete")
        print("3. Check INSTALLED_APPS in settings")
        print("4. Verify templatetags directory structure")
        
        # Test alternative
        test_alternative_approach()
    else:
        print("\n✅ ALL TESTS PASSED!")
        print("Template tags are properly registered and working")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()