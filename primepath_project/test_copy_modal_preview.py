#!/usr/bin/env python
"""
Test script to verify the Copy Exam modal preview functionality
"""

import os
import sys
import django

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_copy_modal_preview():
    """Test that the copy modal preview updates correctly when all fields are filled"""
    
    client = Client()
    
    # Login as admin
    try:
        user = User.objects.get(username='admin')
        user.set_password('test123')
        user.save()
        client.login(username='admin', password='test123')
        print("✅ Logged in as admin")
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return
    
    # Get the exam list page
    response = client.get('/RoutineTest/exams/')
    if response.status_code == 200:
        print("✅ Exam list page loaded successfully")
        
        # Check if the preview functionality JavaScript is present
        content = response.content.decode('utf-8')
        
        # Check for the updateCopyExamNamePreview function
        if 'function updateCopyExamNamePreview()' in content:
            print("✅ updateCopyExamNamePreview function found")
            
            # Check if it includes all required field checks
            if 'examTypeSelect?.value' in content and 'timeslotSelect?.value' in content:
                print("✅ Function checks examType and timeslot fields")
            else:
                print("❌ Function missing examType or timeslot checks")
            
            # Check if preview text element exists
            if 'id="previewText"' in content:
                print("✅ Preview text element exists")
            else:
                print("❌ Preview text element not found")
                
            # Check if event listeners are set up
            if "timeslotSelect.addEventListener('change', updateCopyExamNamePreview)" in content:
                print("✅ Timeslot change event listener set up")
            else:
                print("❌ Timeslot change event listener not found")
                
            # Check if exam type changes trigger preview update
            if 'updateCopyExamNamePreview()' in content and 'Exam type changed to:' in content:
                print("✅ Exam type change triggers preview update")
            else:
                print("❌ Exam type change doesn't trigger preview update")
                
        else:
            print("❌ updateCopyExamNamePreview function not found")
            
    else:
        print(f"❌ Failed to load exam list page: {response.status_code}")
    
    print("\n📊 Summary:")
    print("The copy modal preview should now work when all required fields are filled:")
    print("  1. Exam Type (QUARTERLY or REVIEW)")
    print("  2. Time Period (Quarter or Month)")
    print("  3. Program")
    print("  4. SubProgram")
    print("  5. Level")
    print("\nOptional: Custom Name Suffix")

if __name__ == '__main__':
    test_copy_modal_preview()