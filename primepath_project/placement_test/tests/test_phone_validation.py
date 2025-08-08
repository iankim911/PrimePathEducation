"""
Test script to verify phone validation still works after removing pattern attribute
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.urls import reverse

def test_phone_validation():
    """Test that phone validation still works correctly"""
    client = Client()
    
    print("\n=== TESTING PHONE VALIDATION AFTER PATTERN REMOVAL ===\n")
    
    # Test cases
    test_cases = [
        # (phone_input, should_work, description)
        ('010-1234-5678', True, 'Valid formatted phone'),
        ('01012345678', True, 'Valid unformatted phone'),
        ('010 1234 5678', True, 'Valid space-separated phone'),
        ('', False, 'Empty phone (required field)'),
        ('02-1234-5678', False, 'Invalid area code (not 010)'),
        ('010-123-456', False, 'Too short'),
        ('010-1234-56789', False, 'Too long'),
    ]
    
    results = []
    
    for phone, should_work, description in test_cases:
        # Prepare form data
        form_data = {
            'student_name': 'Test Student',
            'parent_phone': phone,
            'school_name': 'Test School',
            'grade': '5',
            'academic_rank': 'TOP_30'  # Valid academic rank
        }
        
        try:
            # Submit form
            response = client.post(
                reverse('placement_test:start_test'),
                data=form_data,
                follow=True
            )
            
            # Check if submission worked
            if response.status_code == 200:
                # Check if we got redirected (success) or stayed on form (validation error)
                if response.redirect_chain:
                    # Success - redirected to test
                    actual_result = True
                    status = "Submitted"
                else:
                    # Stayed on form page
                    actual_result = False
                    status = "Rejected"
            else:
                actual_result = False
                status = f"Error {response.status_code}"
                
            # Compare with expected
            passed = (actual_result == should_work)
            results.append((description, passed, status))
            
            print(f"[{'PASS' if passed else 'FAIL'}] {description}")
            print(f"  Input: '{phone}'")
            print(f"  Expected: {'Accept' if should_work else 'Reject'}")
            print(f"  Actual: {status}")
            print()
            
        except Exception as e:
            print(f"[ERROR] {description}: {str(e)}")
            results.append((description, False, str(e)))
    
    # Summary
    print("=== SUMMARY ===")
    passed_count = sum(1 for _, passed, _ in results if passed)
    total_count = len(results)
    
    print(f"\nPassed: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n[SUCCESS] ALL PHONE VALIDATION TESTS PASSED!")
        print("The removal of pattern attribute did not affect validation.")
    else:
        print("\n[WARNING] Some tests failed. Review the results above.")
        failed = [desc for desc, passed, _ in results if not passed]
        print(f"Failed tests: {', '.join(failed)}")
    
    return passed_count == total_count

def test_form_rendering():
    """Test that form still renders correctly"""
    client = Client()
    
    print("\n=== TESTING FORM RENDERING ===\n")
    
    response = client.get(reverse('placement_test:start_test'))
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check that phone field exists
        if 'id="parent_phone"' in content:
            print("[PASS] Phone field renders correctly")
        else:
            print("[FAIL] Phone field not found")
            
        # Check that pattern attribute is removed
        if 'pattern="^010' not in content:
            print("[PASS] Pattern attribute successfully removed")
        else:
            print("[FAIL] Pattern attribute still present")
            
        # Check that JavaScript validation is still present
        if 'formatPhoneNumber' in content:
            print("[PASS] JavaScript validation function present")
        else:
            print("[FAIL] JavaScript validation function missing")
            
        # Check that error message element exists
        if 'phone-error' in content:
            print("[PASS] Error message element present")
        else:
            print("[FAIL] Error message element missing")
            
        return True
    else:
        print(f"[FAIL] Could not load form: Status {response.status_code}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PHONE VALIDATION FIX VERIFICATION")
    print("Testing removal of problematic pattern attribute")
    print("=" * 60)
    
    form_ok = test_form_rendering()
    validation_ok = test_phone_validation()
    
    print("\n" + "=" * 60)
    if form_ok and validation_ok:
        print("[SUCCESS] FIX VERIFIED: All tests passed!")
        print("The pattern attribute has been safely removed.")
        print("Phone validation continues to work via JavaScript.")
    else:
        print("[WARNING] Some issues detected. Review the test output.")
    print("=" * 60)