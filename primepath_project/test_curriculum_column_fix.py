#!/usr/bin/env python3
"""
Test to verify the Curriculum column fix
"""
import os
import sys
import django

# Add the Django project path
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

# Initialize Django
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from core.models import Teacher
import json

def test_curriculum_column_fix():
    """Test that the curriculum column now appears in the matrix"""
    print("🔍 TESTING: Curriculum Column Fix")
    print("=" * 60)
    
    try:
        client = Client()
        
        # Create admin user for authentication
        user, created = User.objects.get_or_create(
            username='admin_test_curriculum',
            defaults={'password': 'admin123', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            user.set_password('admin123')
            user.save()
        
        # Create teacher record
        teacher, created = Teacher.objects.get_or_create(
            user=user,
            defaults={'name': 'Admin Test Teacher'}
        )
        
        # Login
        client.force_login(user)
        print(f"✓ Logged in as: {user.username}")
        
        # Test the original schedule-matrix URL (which redirects)
        response = client.get('/RoutineTest/schedule-matrix/')
        print(f"✓ Response status: {response.status_code}")
        
        # Follow the redirect
        if response.status_code == 302:
            redirect_url = response.url
            print(f"✓ Redirected to: {redirect_url}")
            
            response = client.get(redirect_url)
            print(f"✓ Final response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for curriculum header in HTML
            curriculum_headers = content.count('<th>Curriculum</th>')
            print(f"✓ Found {curriculum_headers} '<th>Curriculum</th>' in HTML")
            
            # Check for curriculum-mapping class
            curriculum_cells = content.count('class="curriculum-mapping"')
            print(f"✓ Found {curriculum_cells} 'class=\"curriculum-mapping\"' in HTML")
            
            # Check for curriculum-badge
            curriculum_badges = content.count('curriculum-badge')
            print(f"✓ Found {curriculum_badges} 'curriculum-badge' in HTML")
            
            # Show table structure
            if '<thead>' in content:
                thead_start = content.find('<thead>')
                thead_end = content.find('</thead>') + 8
                thead_content = content[thead_start:thead_end]
                print(f"\n📋 Table header structure:")
                print("    " + thead_content.replace('\n', '\n    ')[:500])
            
            # Show first row structure
            if '<tbody>' in content and '<tr>' in content:
                tbody_start = content.find('<tbody>')
                first_tr_start = content.find('<tr>', tbody_start)
                first_tr_end = content.find('</tr>', first_tr_start) + 5
                first_row = content[first_tr_start:first_tr_end]
                print(f"\n📋 First table row structure:")
                print("    " + first_row.replace('\n', '\n    ')[:500])
            
            print(f"\n🎯 SUMMARY:")
            if curriculum_headers > 0 and curriculum_cells > 0:
                print("✅ SUCCESS: Curriculum column is now present in the matrix!")
                print("✅ Both header and content cells are working correctly")
                return True
            else:
                print("❌ FAILED: Curriculum column is still missing")
                print(f"   Headers: {curriculum_headers}, Cells: {curriculum_cells}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: Failed to load page")
            return False
            
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_curriculum_column_fix()
    print(f"\n{'='*60}")
    print(f"TEST RESULT: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"{'='*60}")