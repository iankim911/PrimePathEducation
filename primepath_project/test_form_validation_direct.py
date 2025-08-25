#!/usr/bin/env python
"""
Test form validation directly without HTTP
"""
import os
import django
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_student.forms import StudentRegistrationForm
from django.contrib.auth.models import User
from primepath_student.models import StudentProfile

print("=== DIRECT FORM VALIDATION TEST ===")

# Test data identical to what the browser is sending
test_data = {
    'first_name': 'Live',
    'last_name': 'Debug Test', 
    'student_id': f'live_debug_direct_{int(time.time())}',
    'phone_number': '01077777777',
    'email': f'live.debug.direct.{int(time.time())}@example.com',
    'parent1_name': 'Debug Parent',
    'parent1_phone': '01088888888', 
    'password1': 'LiveDebug123!',
    'password2': 'LiveDebug123!'
}

print(f"Testing with data: {test_data}")

# Create form
form = StudentRegistrationForm(test_data)

print(f"\nForm is valid: {form.is_valid()}")

if not form.is_valid():
    print("\n❌ FORM VALIDATION ERRORS:")
    for field, errors in form.errors.items():
        print(f"  {field}: {errors}")
        
    print(f"\nNon-field errors: {form.non_field_errors()}")
else:
    print("\n✅ Form validation passed")
    print("Attempting to save...")
    
    try:
        user = form.save()
        print(f"✅ User saved successfully: {user.username} (ID: {user.id})")
        
        # Check if student profile was created
        try:
            profile = user.primepath_student_profile
            print(f"✅ Student profile created: {profile.student_id}")
        except:
            print("❌ Student profile not found")
            
    except Exception as e:
        print(f"❌ Error saving form: {e}")
        import traceback
        traceback.print_exc()

print(f"\nDatabase state check:")
print(f"Total users: {User.objects.count()}")
print(f"Total student profiles: {StudentProfile.objects.count()}")

# Check the last few users
recent_users = User.objects.order_by('-id')[:3]
print(f"\nLast 3 users:")
for u in recent_users:
    print(f"  {u.id}: {u.username} ({u.email})")