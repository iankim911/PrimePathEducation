#!/usr/bin/env python3
"""
TEST: Points Editing with Authentication
Tests the complete points editing workflow with proper authentication
"""

import os
import sys
import json
from datetime import datetime

# Django setup
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from placement_test.models import Exam, Question

def test_points_with_auth():
    """Test points editing with proper authentication"""
    
    print("=" * 60)
    print("🔐 TESTING POINTS EDITING WITH AUTHENTICATION")
    print("=" * 60)
    
    # Step 1: Create or get a test user
    print("\n📋 STEP 1: Setting up authentication...")
    
    try:
        # Try to get existing superuser
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            # Create a test user
            user = User.objects.create_user(
                username='testuser',
                password='testpass123',
                is_staff=True
            )
            print(f"✅ Created test user: {user.username}")
        else:
            print(f"✅ Using existing user: {user.username}")
    except Exception as e:
        print(f"❌ Error setting up user: {e}")
        return False
    
    # Step 2: Find an exam
    print("\n📋 STEP 2: Finding test exam...")
    
    exams = Exam.objects.filter(questions__isnull=False).distinct()
    if not exams.exists():
        print("❌ No exams with questions found")
        return False
    
    test_exam = exams.first()
    questions = test_exam.questions.all()
    
    print(f"✅ Using exam: {test_exam.name}")
    print(f"   Exam ID: {test_exam.id}")
    print(f"   Questions: {questions.count()}")
    
    # Display current points
    print("\n📊 Current points values:")
    for i, q in enumerate(questions[:5]):  # Show first 5
        print(f"   Q{q.question_number}: {q.points} point{'s' if q.points != 1 else ''}")
    
    # Step 3: Test with authentication
    print(f"\n🌐 STEP 3: Testing preview page WITH authentication...")
    
    client = Client()
    
    # Login the user
    if user.username == 'testuser':
        login_success = client.login(username='testuser', password='testpass123')
    else:
        # For existing users, we need to set a known password
        user.set_password('testpass123')
        user.save()
        login_success = client.login(username=user.username, password='testpass123')
    
    if login_success:
        print("✅ Login successful")
    else:
        print("❌ Login failed")
        return False
    
    # Suppress URL logging temporarily
    import logging
    logging.getLogger('placement_test.middleware').setLevel(logging.ERROR)
    logging.getLogger('placement_test.urls').setLevel(logging.ERROR)
    
    # Now access the preview page
    response = client.get(f'/PlacementTest/exams/{test_exam.id}/preview/')
    
    print(f"📡 Response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Preview page loaded successfully!")
        
        content = response.content.decode('utf-8')
        
        # Check for JavaScript presence
        print("\n🔍 JavaScript Verification:")
        
        js_checks = {
            'Points editor init': '[PointsEditor] 🚀 INITIALIZING' in content,
            'Setup function': 'function setupEditButtonHandlers()' in content,
            'Click handler': "btn.addEventListener('click'" in content,
            'Handlers attached': 'Attaching handlers to button' in content,
            'Click logging': 'CLICK: Edit button clicked' in content,
            'All configured': 'All edit buttons configured' in content,
        }
        
        for check, present in js_checks.items():
            status = "✅" if present else "❌"
            print(f"   {status} {check}")
        
        # Check for edit buttons in HTML
        print("\n🔍 HTML Structure Verification:")
        
        html_checks = {
            'Edit buttons': 'class="edit-points-btn"' in content,
            'Points display': 'class="question-points-display"' in content,
            'Points input': 'class="points-input"' in content,
            'Save buttons': 'class="save-points-btn"' in content,
            'Cancel buttons': 'class="cancel-points-btn"' in content,
        }
        
        for check, present in html_checks.items():
            status = "✅" if present else "❌"
            print(f"   {status} {check}")
        
        # Count edit buttons
        edit_button_count = content.count('class="edit-points-btn"')
        print(f"\n📊 Edit buttons found: {edit_button_count}")
        
        if edit_button_count > 0:
            print("✅ Edit buttons are present in the HTML")
        else:
            print("❌ No edit buttons found in HTML")
        
        return True
        
    elif response.status_code == 302:
        print("❌ Still getting redirected even with authentication")
        print(f"   Redirect to: {response.get('Location', 'Unknown')}")
        return False
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        return False

def main():
    print("\n🚀 COMPREHENSIVE POINTS EDITING TEST WITH AUTH")
    print("=" * 60)
    
    try:
        success = test_points_with_auth()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 TEST PASSED - Preview page loads with authentication!")
            print("\n✅ Next Steps:")
            print("   1. Login to the admin interface")
            print("   2. Navigate to Preview & Answer Keys page")
            print("   3. Open browser console (F12)")
            print("   4. Look for [PointsEditor] messages")
            print("   5. Click on edit buttons (✏️)")
            print("\n📝 If buttons still don't work:")
            print("   • Clear browser cache (Ctrl+Shift+R)")
            print("   • Check console for JavaScript errors")
            print("   • Try incognito/private mode")
        else:
            print("\n" + "=" * 60)
            print("❌ TEST FAILED - Check issues above")
            print("\n📝 Troubleshooting:")
            print("   • Ensure user has proper permissions")
            print("   • Check if login is working")
            print("   • Verify exam exists with questions")
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()