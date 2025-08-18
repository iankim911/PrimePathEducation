#!/usr/bin/env python
"""
Comprehensive Mode Toggle Debug Script
Tests all possible sources of "function:" text issue
"""
import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from primepath_routinetest.context_processors import routinetest_context
from primepath_routinetest.views.classes_exams_unified import classes_exams_unified_view
from core.models import Teacher

User = get_user_model()

def test_context_processor():
    """Test if context processor is returning correct values"""
    print("\n" + "="*80)
    print("TESTING CONTEXT PROCESSOR")
    print("="*80)
    
    factory = RequestFactory()
    request = factory.get('/RoutineTest/classes-exams/')
    
    # Add session
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    # Test with different session values
    test_values = [
        None,
        'Teacher',
        'Admin',
        lambda: 'Teacher Mode',  # Function that returns string
        'function: Teacher Mode'  # String with "function:" prefix
    ]
    
    for value in test_values:
        request.session['view_mode'] = value
        context = routinetest_context(request)
        
        print(f"\nSession value: {repr(value)}")
        print(f"Type: {type(value)}")
        print(f"Context returned: {repr(context.get('current_view_mode'))}")
        print(f"Is callable: {callable(value)}")
        
        # Check if the context processor is accidentally calling the function
        if callable(value):
            print(f"If called, returns: {value()}")

def test_view_context():
    """Test what the view is actually passing to template"""
    print("\n" + "="*80)
    print("TESTING VIEW CONTEXT")
    print("="*80)
    
    client = Client()
    
    # Create test user
    user = User.objects.filter(username='admin').first()
    if not user:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    
    # Create teacher profile if needed
    teacher, _ = Teacher.objects.get_or_create(
        user=user,
        defaults={'name': 'Admin Teacher', 'email': 'admin@test.com'}
    )
    
    client.force_login(user)
    
    # Test different session values
    test_cases = [
        ('Teacher', 'Normal Teacher mode'),
        ('Admin', 'Admin mode'),
        (lambda: 'Teacher Mode', 'Function object (error case)'),
    ]
    
    for value, description in test_cases:
        print(f"\n\nTest Case: {description}")
        print(f"Setting session['view_mode'] = {repr(value)}")
        
        # Set session
        session = client.session
        session['view_mode'] = value
        session.save()
        
        # Make request
        response = client.get('/RoutineTest/classes-exams/')
        
        if response.status_code == 200:
            # Check context
            if hasattr(response, 'context'):
                context = response.context
                if context:
                    view_mode = context.get('current_view_mode', 'NOT_FOUND')
                    view_mode_session = context.get('view_mode', 'NOT_FOUND')
                    
                    print(f"Context['current_view_mode']: {repr(view_mode)}")
                    print(f"Context['view_mode']: {repr(view_mode_session)}")
                    print(f"Type: {type(view_mode)}")
                    
                    # Check if accidentally stringified
                    if 'function' in str(view_mode).lower():
                        print("⚠️ WARNING: 'function' found in view_mode string!")
                    
                    # Check rendered content
                    content = response.content.decode('utf-8')
                    if 'function:' in content:
                        print("⚠️ WARNING: 'function:' found in rendered HTML!")
                        # Find occurrences
                        import re
                        matches = re.findall(r'.{20}function:.{20}', content)
                        for match in matches[:3]:
                            print(f"  Found: ...{match}...")
            else:
                print("No context available in response")
        else:
            print(f"Response status: {response.status_code}")

def check_template_variables():
    """Check if any template is using wrong variable"""
    print("\n" + "="*80)
    print("CHECKING TEMPLATE VARIABLES")
    print("="*80)
    
    import glob
    template_dir = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest'
    
    patterns_to_check = [
        'current_view_mode',
        'view_mode',
        'mode',
        'request.session.view_mode',
        'session.view_mode'
    ]
    
    for pattern in patterns_to_check:
        print(f"\nSearching for: {pattern}")
        for template_file in glob.glob(f"{template_dir}/**/*.html", recursive=True):
            with open(template_file, 'r') as f:
                content = f.read()
                if pattern in content:
                    # Check context around the pattern
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line:
                            print(f"  {template_file}:{i+1}: {line.strip()}")

def check_middleware_or_processors():
    """Check if any middleware or processor is modifying context"""
    print("\n" + "="*80)
    print("CHECKING MIDDLEWARE AND PROCESSORS")
    print("="*80)
    
    from django.conf import settings
    
    print("\nInstalled Middleware:")
    for middleware in settings.MIDDLEWARE:
        print(f"  - {middleware}")
        if 'routinetest' in middleware.lower():
            print("    ⚠️ RoutineTest-specific middleware found!")
    
    print("\nContext Processors:")
    for processor in settings.TEMPLATES[0]['OPTIONS']['context_processors']:
        print(f"  - {processor}")
        if 'routinetest' in processor.lower():
            print("    ⚠️ RoutineTest-specific processor found!")
            
            # Test the processor directly
            if processor == 'primepath_routinetest.context_processors.routinetest_context':
                print("\n    Testing processor output:")
                factory = RequestFactory()
                request = factory.get('/test/')
                middleware = SessionMiddleware(lambda x: None)
                middleware.process_request(request)
                request.session['view_mode'] = 'Teacher'
                request.session.save()
                
                from primepath_routinetest.context_processors import routinetest_context
                context = routinetest_context(request)
                for key, value in context.items():
                    if 'mode' in key.lower():
                        print(f"      {key}: {repr(value)} (type: {type(value).__name__})")

def main():
    """Run all diagnostic tests"""
    print("\n" + "="*80)
    print("MODE TOGGLE DEBUG DIAGNOSTIC")
    print("Finding source of 'function:' text issue")
    print("="*80)
    
    try:
        test_context_processor()
    except Exception as e:
        print(f"Error in context processor test: {e}")
    
    try:
        test_view_context()
    except Exception as e:
        print(f"Error in view context test: {e}")
    
    try:
        check_template_variables()
    except Exception as e:
        print(f"Error checking templates: {e}")
    
    try:
        check_middleware_or_processors()
    except Exception as e:
        print(f"Error checking middleware: {e}")
    
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()