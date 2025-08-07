"""
Simple test to verify the phone field pattern attribute fix
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.urls import reverse

def test_fix():
    """Test that the problematic pattern attribute has been removed"""
    client = Client()
    
    print("\n" + "=" * 60)
    print("PHONE FIELD PATTERN ATTRIBUTE FIX VERIFICATION")
    print("=" * 60)
    
    # Get the form page
    response = client.get(reverse('placement_test:start_test'))
    
    if response.status_code != 200:
        print(f"[ERROR] Could not load form page: Status {response.status_code}")
        return False
    
    content = response.content.decode('utf-8')
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Phone field exists
    tests_total += 1
    if 'id="parent_phone"' in content:
        print("[PASS] Phone field exists in form")
        tests_passed += 1
    else:
        print("[FAIL] Phone field not found in form")
    
    # Test 2: Pattern attribute removed
    tests_total += 1
    if 'pattern="^010[-\\s]?\\d{4}[-\\s]?\\d{4}$' not in content:
        print("[PASS] Problematic pattern attribute has been removed")
        tests_passed += 1
    else:
        print("[FAIL] Pattern attribute still present")
        
    # Test 3: Check for any pattern on phone field
    tests_total += 1
    # Extract the phone field HTML
    import re
    phone_field_match = re.search(r'<input[^>]*id="parent_phone"[^>]*>', content)
    if phone_field_match:
        phone_field_html = phone_field_match.group(0)
        if 'pattern=' not in phone_field_html:
            print("[PASS] No pattern attribute on phone field")
            tests_passed += 1
        else:
            print(f"[FAIL] Pattern attribute found: {phone_field_html}")
    else:
        print("[ERROR] Could not extract phone field HTML")
    
    # Test 4: JavaScript validation still present
    tests_total += 1
    if 'formatPhoneNumber' in content:
        print("[PASS] JavaScript formatPhoneNumber function present")
        tests_passed += 1
    else:
        print("[FAIL] JavaScript validation function missing")
    
    # Test 5: Form submit validation still present
    tests_total += 1
    if "phoneValue.startsWith('010')" in content:
        print("[PASS] Form submit validation for 010 prefix present")
        tests_passed += 1
    else:
        print("[FAIL] Form submit validation missing")
    
    # Test 6: Error message element present
    tests_total += 1
    if 'id="phone-error"' in content:
        print("[PASS] Phone error message element present")
        tests_passed += 1
    else:
        print("[FAIL] Phone error message element missing")
    
    # Test 7: Required attribute still present
    tests_total += 1
    if phone_field_match:
        phone_field_html = phone_field_match.group(0)
        if 'required' in phone_field_html:
            print("[PASS] Required attribute still present")
            tests_passed += 1
        else:
            print("[FAIL] Required attribute missing")
    
    # Test 8: Student name field unaffected
    tests_total += 1
    student_field_match = re.search(r'<input[^>]*id="student_name"[^>]*>', content)
    if student_field_match:
        student_field_html = student_field_match.group(0)
        if 'pattern=' not in student_field_html:
            print("[PASS] Student name field has no pattern attribute")
            tests_passed += 1
        else:
            print(f"[FAIL] Student name field has pattern: {student_field_html}")
    
    print("\n" + "-" * 60)
    print(f"Results: {tests_passed}/{tests_total} tests passed")
    print("-" * 60)
    
    if tests_passed == tests_total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("The fix has been successfully implemented:")
        print("  - Pattern attribute removed from phone field")
        print("  - JavaScript validation still intact")
        print("  - No impact on other form fields")
        print("  - Console error should be resolved")
    else:
        print("\n[WARNING] Some tests failed")
        print("Please review the results above")
    
    print("=" * 60)
    
    return tests_passed == tests_total

if __name__ == "__main__":
    success = test_fix()
    exit(0 if success else 1)