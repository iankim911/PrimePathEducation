#!/usr/bin/env python
"""
Test script to verify curriculum data is passed to template context
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from primepath_routinetest.views.exam import exam_list_hierarchical
from core.models import Teacher
import json

def test_view_context():
    """Test that view passes curriculum data to template"""
    print("\n" + "="*80)
    print("TESTING VIEW CONTEXT FOR COPY MODAL")
    print("="*80)
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/RoutineTest/')
    
    # Get or create admin user
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Using existing admin user: {admin_user.username}")
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin'
        )
        print(f"✅ Created admin user: {admin_user.username}")
    
    # Ensure teacher profile exists
    teacher, created = Teacher.objects.get_or_create(
        user=admin_user,
        defaults={'name': 'Admin Teacher', 'is_head_teacher': True}
    )
    if created:
        print(f"✅ Created teacher profile for admin")
    else:
        print(f"✅ Using existing teacher profile")
    
    request.user = admin_user
    
    # Call the view to get the response
    print("\n📋 Calling exam_list_hierarchical view...")
    response = exam_list_hierarchical(request)
    
    # Check if it's a template response
    if hasattr(response, 'context_data'):
        context = response.context_data
        print("✅ Got template response with context")
        
        # Check for curriculum data
        if 'curriculum_levels_for_copy' in context:
            curriculum_data = context['curriculum_levels_for_copy']
            print(f"\n✅ curriculum_levels_for_copy is in context")
            print(f"   Total items: {len(curriculum_data)}")
            
            # Group by program for display
            programs = {}
            for level in curriculum_data:
                program = level['program_name']
                if program not in programs:
                    programs[program] = 0
                programs[program] += 1
            
            print("\n📊 Program distribution:")
            for prog, count in programs.items():
                print(f"   - {prog}: {count} levels")
        else:
            print("\n❌ curriculum_levels_for_copy NOT found in context!")
            print("\nAvailable context keys:")
            for key in context.keys():
                print(f"   - {key}")
    else:
        print("❌ Response is not a template response")
        print(f"   Response type: {type(response)}")
        print(f"   Status code: {response.status_code}")

if __name__ == '__main__':
    test_view_context()