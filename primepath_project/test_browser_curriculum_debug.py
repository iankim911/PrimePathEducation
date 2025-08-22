#!/usr/bin/env python3
"""
Test script to debug curriculum data loading in browser
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_browser_curriculum_debug():
    """Test what's actually being rendered in the browser"""
    print("=== DEBUGGING CURRICULUM DATA IN BROWSER ===")
    print()
    
    # Create test client
    client = Client()
    
    # Try to get or create a test user
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ Admin user not found. Please create admin user first.")
        return False
    
    # Login as admin
    client.force_login(user)
    
    # Get the exam list page
    response = client.get('/RoutineTest/exams/')
    
    if response.status_code == 200:
        print("✅ Successfully loaded exam list page")
        
        # Check if curriculum data is in the response
        content = response.content.decode()
        
        # Look for our curriculum data
        if 'window.CopyCurriculumData = {};' in content:
            print("✅ CopyCurriculumData initialization found in HTML")
        else:
            print("❌ CopyCurriculumData initialization NOT found")
            
        if 'curriculum_levels_for_copy' in content:
            print("✅ Django template variable found")
        else:
            print("❌ Django template variable NOT found")
            
        # Look for program names
        programs = ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']
        for program in programs:
            count = content.count(f"'{program}'")
            if count > 0:
                print(f"✅ {program} found {count} times in HTML")
            else:
                print(f"❌ {program} NOT found in HTML")
        
        # Look for the populateCopyProgramDropdown function call
        if 'populateCopyProgramDropdown()' in content:
            print("✅ populateCopyProgramDropdown() call found")
        else:
            print("❌ populateCopyProgramDropdown() call NOT found")
            
        # Check if initialization function is called
        if 'initializeCopyCurriculumCascading()' in content:
            print("✅ initializeCopyCurriculumCascading() call found")
        else:
            print("❌ initializeCopyCurriculumCascading() call NOT found")
            
        # Save a snippet for manual inspection
        # Find the curriculum data section
        start = content.find('window.CopyCurriculumData = null;')
        if start > -1:
            end = content.find('function initializeCopyCurriculumCascading()', start)
            if end > -1:
                curriculum_section = content[start:end]
                print("\n📋 Curriculum Data Section (first 500 chars):")
                print(curriculum_section[:500])
            
    else:
        print(f"❌ Failed to load exam list page: {response.status_code}")
        return False
    
    return True

if __name__ == '__main__':
    success = test_browser_curriculum_debug()
    sys.exit(0 if success else 1)