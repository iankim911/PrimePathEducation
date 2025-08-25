#!/usr/bin/env python
"""
Test with exact same data as HTTP request
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_student.forms import StudentRegistrationForm

# Exact same data from HTTP test
test_data = {
    'first_name': 'Test',
    'last_name': 'User', 
    'student_id': 'test12345',  # 9 chars, well under limit
    'phone_number': '01099999999',
    'email': 'test12345@example.com',
    'parent1_name': 'Test Parent',
    'parent1_phone': '01088888888',
    'password1': 'Test123!',
    'password2': 'Test123!'
}

print("=== TESTING EXACT HTTP DATA ===")
print(f"Data: {test_data}")

form = StudentRegistrationForm(test_data)
print(f"\nForm is valid: {form.is_valid()}")

if not form.is_valid():
    print("\n❌ FORM ERRORS:")
    for field, errors in form.errors.items():
        print(f"  {field}: {errors}")
    print(f"Non-field errors: {form.non_field_errors()}")
    
    # Check individual field validation
    print(f"\n=== INDIVIDUAL FIELD CHECKS ===")
    print(f"student_id length: {len(test_data['student_id'])}")
    print(f"phone_number format: {test_data['phone_number']}")
    print(f"email format: {test_data['email']}")
    print(f"passwords match: {test_data['password1'] == test_data['password2']}")
    
else:
    print("\n✅ Form is valid!")
    print("Attempting save...")
    try:
        user = form.save()
        print(f"✅ Success! Created user: {user.username}")
    except Exception as e:
        print(f"❌ Error saving: {e}")
        import traceback
        traceback.print_exc()