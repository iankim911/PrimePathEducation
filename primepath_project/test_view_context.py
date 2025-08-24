#!/usr/bin/env python
"""
Test script to verify the unified view is passing Korean class codes
"""
import os
import sys

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User

from core.models import Teacher

print("=" * 80)
print("VIEW CONTEXT VERIFICATION - KOREAN CLASS CODES")
print("=" * 80)

# Create a test client
client = Client()

# Get or create a test user
user, created = User.objects.get_or_create(
    username='admin',
    defaults={'is_staff': True, 'is_superuser': True, 'email': 'admin@example.com'}
)

if created:
    user.set_password('password')
    user.save()

# Get or create teacher profile
teacher, teacher_created = Teacher.objects.get_or_create(
    user=user,
    defaults={'name': 'Admin User', 'email': 'admin@example.com', 'is_head_teacher': True}
)

print(f"Using user: {user.username} (created: {created})")
print(f"Teacher profile: {teacher.name} (created: {teacher_created})")

# Login and test the view
client.login(username='admin', password='password')

try:
    # Test the unified view
    response = client.get('/RoutineTest/classes-exams/')
    
    print(f"\n1. VIEW RESPONSE:")
    print(f"   Status code: {response.status_code}")
    print(f"   Template used: {[t.name for t in response.templates] if hasattr(response, 'templates') else 'N/A'}")
    
    if response.status_code == 200:
        # Check if Korean class codes are in the response
        content = response.content.decode('utf-8')
        
        print(f"\n2. KOREAN CLASS CODES IN RESPONSE:")
        korean_codes = ['PS1', 'A2', 'B3', 'Young-cho2', 'TaejoC', 'High1.SatSun.3-5']
        fake_codes = ['PRIMARY_1A', 'MIDDLE_7A', 'HIGH_10A']
        
        for code in korean_codes:
            if code in content:
                print(f"   ✅ {code} found in response")
            else:
                print(f"   ❌ {code} NOT found in response")
        
        print(f"\n3. OLD FAKE CLASS CODES CHECK:")
        for code in fake_codes:
            if code in content:
                print(f"   ❌ {code} still found in response (should be removed)")
            else:
                print(f"   ✅ {code} not found (correctly removed)")
        
        # Check context if available
        if hasattr(response, 'context') and response.context:
            context = response.context
            if 'available_classes' in context:
                available_classes = context['available_classes']
                print(f"\n4. AVAILABLE_CLASSES IN CONTEXT:")
                print(f"   Total classes: {len(available_classes)}")
                for i, cls in enumerate(available_classes[:5]):
                    print(f"   {i+1}. {cls.get('class_code', 'N/A')} - {cls.get('class_name', 'N/A')}")
                if len(available_classes) > 5:
                    print(f"   ... and {len(available_classes) - 5} more")
            else:
                print(f"\n4. AVAILABLE_CLASSES: Not found in context")
        else:
            print(f"\n4. CONTEXT: Not available for inspection")
    
    else:
        print(f"   Error: View returned status {response.status_code}")
        print(f"   Content: {response.content[:500]}")

except Exception as e:
    print(f"   ❌ Error testing view: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("VIEW CONTEXT VERIFICATION COMPLETE")
print("=" * 80)