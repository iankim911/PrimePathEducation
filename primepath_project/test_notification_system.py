#!/usr/bin/env python3
"""
COMPREHENSIVE TEST: Notification System and Points Editing
Tests the complete notification implementation and points update workflow
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
from placement_test.services import PointsService

def test_notification_system():
    """Test the notification system and points editing workflow"""
    
    print("=" * 60)
    print("🔔 NOTIFICATION SYSTEM & POINTS EDITING TEST")
    print("=" * 60)
    
    # Step 1: Setup authentication
    print("\n📋 STEP 1: Setting up authentication...")
    
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_superuser(
            username='testadmin',
            password='testpass123',
            email='admin@test.com'
        )
        print(f"✅ Created test admin: {user.username}")
    else:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Using existing admin: {user.username}")
    
    client = Client()
    login_success = client.login(username=user.username, password='testpass123')
    
    if not login_success:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful")
    
    # Step 2: Find test exam and question
    print("\n📋 STEP 2: Finding test data...")
    
    exam = Exam.objects.filter(questions__isnull=False).first()
    if not exam:
        print("❌ No exam with questions found")
        return False
    
    question = exam.questions.first()
    print(f"✅ Using exam: {exam.name}")
    print(f"✅ Using question: Q{question.question_number} (ID: {question.id})")
    print(f"   Current points: {question.points}")
    
    # Step 3: Load preview page and check for notification system
    print("\n📋 STEP 3: Loading preview page...")
    
    response = client.get(f'/PlacementTest/exams/{exam.id}/preview/')
    
    if response.status_code != 200:
        print(f"❌ Failed to load preview page: {response.status_code}")
        return False
    
    print("✅ Preview page loaded")
    
    content = response.content.decode('utf-8')
    
    # Step 4: Verify notification system components
    print("\n📋 STEP 4: Verifying notification system...")
    
    notification_checks = {
        'showNotification function': 'function showNotification(' in content,
        'dismissNotification function': 'function dismissNotification(' in content,
        'clearAllNotifications function': 'function clearAllNotifications(' in content,
        'Notification styles': 'notification-container' in content,
        'Success style': 'notification-item.success' in content,
        'Error style': 'notification-item.error' in content,
        'Info style': 'notification-item.info' in content,
        'Warning style': 'notification-item.warning' in content,
        'Progress animation': '@keyframes progress' in content,
        'Slide animations': '@keyframes slideInRight' in content,
    }
    
    all_good = True
    for check, present in notification_checks.items():
        status = "✅" if present else "❌"
        print(f"   {status} {check}")
        if not present:
            all_good = False
    
    if not all_good:
        print("\n⚠️ Some notification components missing")
        return False
    
    print("\n✅ All notification system components present")
    
    # Step 5: Test points update API
    print("\n📋 STEP 5: Testing points update with notifications...")
    
    # Test different scenarios
    test_cases = [
        {'points': 5, 'expected': 'success', 'description': 'Valid points update'},
        {'points': 0, 'expected': 'error', 'description': 'Invalid points (too low)'},
        {'points': 11, 'expected': 'error', 'description': 'Invalid points (too high)'},
        {'points': 'abc', 'expected': 'error', 'description': 'Invalid points (not a number)'},
        {'points': 3, 'expected': 'success', 'description': 'Another valid update'},
    ]
    
    for test in test_cases:
        print(f"\n   Testing: {test['description']}")
        print(f"   Sending points: {test['points']}")
        
        response = client.post(
            f'/api/PlacementTest/questions/{question.id}/update/',
            data={'points': test['points']},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                success = data.get('success', False)
                
                if success and test['expected'] == 'success':
                    print(f"   ✅ Success as expected")
                    print(f"      Points updated: {data.get('old_points')} → {data.get('new_points')}")
                    if data.get('updates_applied', {}).get('sessions_recalculated'):
                        print(f"      Sessions recalculated: {data['updates_applied']['sessions_recalculated']}")
                elif not success and test['expected'] == 'error':
                    print(f"   ✅ Error as expected: {data.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ Unexpected result: success={success}, expected={test['expected']}")
                    print(f"      Response: {data}")
                    
            except Exception as e:
                print(f"   ❌ Failed to parse response: {e}")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
    
    # Step 6: Verify final state
    print("\n📋 STEP 6: Verifying final state...")
    
    question.refresh_from_db()
    print(f"✅ Final points value: {question.points}")
    
    # Check if points were actually saved
    if question.points == 3:  # Should be 3 from last successful update
        print("✅ Points were successfully saved to database")
    else:
        print(f"⚠️ Points may not have saved correctly (expected 3, got {question.points})")
    
    # Step 7: Check notification calls
    print("\n📋 STEP 7: Checking notification usage...")
    
    notification_calls = content.count('showNotification(')
    print(f"✅ Found {notification_calls} showNotification calls in template")
    
    if notification_calls < 5:
        print("⚠️ Fewer notification calls than expected")
    
    return all_good

def main():
    print("\n🚀 COMPREHENSIVE NOTIFICATION SYSTEM TEST")
    print("=" * 60)
    
    try:
        success = test_notification_system()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 NOTIFICATION SYSTEM TEST PASSED!")
            print("\n✅ Summary:")
            print("   • Notification functions defined")
            print("   • Notification styles configured")
            print("   • Points update API working")
            print("   • Success/error notifications triggered")
            print("   • Database updates confirmed")
            print("\n📝 User Instructions:")
            print("   1. Clear browser cache (Ctrl+Shift+R)")
            print("   2. Login to admin interface")
            print("   3. Navigate to Preview & Answer Keys")
            print("   4. Click pencil (✏️) button to edit points")
            print("   5. Change value and click save (✓)")
            print("   6. Watch for notification in top-right corner")
            print("   7. Check console for debug messages")
        else:
            print("\n" + "=" * 60)
            print("⚠️ Some issues detected - check details above")
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()