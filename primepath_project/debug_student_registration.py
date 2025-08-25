#!/usr/bin/env python
"""
Debug student registration form validation
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_student.forms import StudentRegistrationForm

# Test the exact same data our test is using
test_data = {
    'first_name': 'Test',
    'last_name': 'Student Auth Fix',
    'student_id': 'test_auth_fix_001',
    'phone_number': '01012345678',
    'email': 'test.auth.fix@example.com',
    'parent1_name': 'Test Parent',
    'parent1_phone': '01098765432',
    'password1': 'TestAuth123!',
    'password2': 'TestAuth123!'
}

print("=== DEBUGGING STUDENT REGISTRATION FORM ===")
print(f"Test data: {test_data}")
print()

# Create and validate form
form = StudentRegistrationForm(test_data)
print(f"Form is valid: {form.is_valid()}")
print()

if not form.is_valid():
    print("=== FORM VALIDATION ERRORS ===")
    for field, errors in form.errors.items():
        print(f"Field '{field}': {errors}")
    print()
    
    print("=== CLEANED DATA ===")
    try:
        cleaned_data = form.cleaned_data
        print(f"Cleaned data: {cleaned_data}")
    except Exception as e:
        print(f"Error getting cleaned data: {e}")
else:
    print("✅ Form is valid! Attempting to save...")
    try:
        user = form.save()
        print(f"✅ User created successfully: {user.username}")
        print(f"   User ID: {user.id}")
        print(f"   Email: {user.email}")
        
        # Check if student profile was created
        if hasattr(user, 'primepath_student_profile'):
            profile = user.primepath_student_profile
            print(f"   Student profile created: {profile.student_id}")
        else:
            print("   ❌ Student profile not created")
            
    except Exception as e:
        print(f"❌ Error saving user: {e}")