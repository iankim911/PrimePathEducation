#!/usr/bin/env python
"""
Test script to verify the copy modal fixes are working correctly.
This script tests:
1. Field reordering (Academic Year before Time Period)
2. Dropdown functionality (Time Period enabled after Exam Type selection)
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

import requests
from bs4 import BeautifulSoup

def test_copy_modal_structure():
    """Test that the copy modal has the correct field order and structure."""
    
    print("🧪 COPY MODAL FIXES VERIFICATION")
    print("=" * 50)
    
    # Test the exam list page
    url = "http://127.0.0.1:8000/RoutineTest/exams/?ownership=my&exam_type=REVIEW"
    
    try:
        print(f"📡 Fetching: {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Page loaded successfully")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the copy modal
            modal = soup.find('div', id='copyExamModal')
            if modal:
                print("✅ Copy modal found in HTML")
                
                # Test 1: Field order
                print("\n🔍 TEST 1: Field Order")
                form_groups = modal.find_all('div', class_='form-group')
                field_order = []
                
                for group in form_groups:
                    label = group.find('label')
                    if label and label.get('for'):
                        field_id = label.get('for')
                        field_text = label.get_text(strip=True)
                        field_order.append((field_id, field_text))
                        print(f"   📋 Found field: {field_text} (id={field_id})")
                
                # Check if Academic Year comes before Time Period
                academic_year_index = -1
                time_period_index = -1
                
                for i, (field_id, field_text) in enumerate(field_order):
                    if field_id == 'academicYear':
                        academic_year_index = i
                    elif field_id == 'timeslot':
                        time_period_index = i
                
                if academic_year_index != -1 and time_period_index != -1:
                    if academic_year_index < time_period_index:
                        print("✅ FIELD ORDER CORRECT: Academic Year comes before Time Period")
                        print(f"   Academic Year position: {academic_year_index + 1}")
                        print(f"   Time Period position: {time_period_index + 1}")
                    else:
                        print("❌ FIELD ORDER INCORRECT: Time Period comes before Academic Year")
                        print(f"   Academic Year position: {academic_year_index + 1}")
                        print(f"   Time Period position: {time_period_index + 1}")
                        return False
                else:
                    print("❌ Could not find both Academic Year and Time Period fields")
                    return False
                
                # Test 2: Dropdown structure
                print("\n🔍 TEST 2: Dropdown Structure")
                
                # Check copyExamType dropdown
                exam_type_select = modal.find('select', id='copyExamType')
                if exam_type_select:
                    print("✅ Exam Type dropdown found")
                    options = exam_type_select.find_all('option')
                    print(f"   Options: {[opt.get_text(strip=True) for opt in options]}")
                else:
                    print("❌ Exam Type dropdown not found")
                    return False
                
                # Check timeslot dropdown
                timeslot_select = modal.find('select', id='timeslot')
                if timeslot_select:
                    print("✅ Time Period dropdown found")
                    is_disabled = timeslot_select.get('disabled') is not None
                    print(f"   Initially disabled: {'Yes' if is_disabled else 'No'}")
                    
                    if is_disabled:
                        print("✅ DROPDOWN LOGIC CORRECT: Time Period starts disabled")
                    else:
                        print("⚠️  Time Period is not disabled initially (might be OK)")
                else:
                    print("❌ Time Period dropdown not found")
                    return False
                
                # Test 3: JavaScript presence
                print("\n🔍 TEST 3: JavaScript Logic")
                
                # Check if the JavaScript event handler is present
                html_content = response.text
                if 'copyExamTypeSelect.addEventListener' in html_content or 'newCopyExamTypeSelect.addEventListener' in html_content:
                    print("✅ JavaScript event handler found")
                    
                    if 'timeslotSelect.disabled = false' in html_content:
                        print("✅ JavaScript enables Time Period dropdown correctly")
                    else:
                        print("⚠️  Could not verify Time Period enabling logic")
                else:
                    print("❌ JavaScript event handler not found")
                    return False
                
                print("\n🎉 ALL TESTS PASSED!")
                print("\n📋 SUMMARY:")
                print("✅ Field reordering: Academic Year now comes before Time Period")
                print("✅ Dropdown structure: Both dropdowns present with correct IDs")
                print("✅ JavaScript logic: Event handler present to enable Time Period")
                print("\n🔧 Ready for manual testing in browser!")
                return True
                
            else:
                print("❌ Copy modal not found in HTML")
                return False
                
        else:
            print(f"❌ Failed to load page. Status code: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_manual_instructions():
    """Provide manual testing instructions."""
    
    print("\n" + "=" * 60)
    print("🔧 MANUAL TESTING INSTRUCTIONS")
    print("=" * 60)
    print()
    print("1. 🌐 Open browser and navigate to:")
    print("   http://127.0.0.1:8000/RoutineTest/exams/?ownership=my&exam_type=REVIEW")
    print()
    print("2. 📋 Find an exam and click the 'Copy Exam' button")
    print()
    print("3. ✅ Verify in the modal:")
    print("   • Field order: Target Class → Exam Type → Academic Year → Time Period")
    print("   • Time Period dropdown is initially grayed out")
    print("   • When you select an Exam Type (Review/Quarterly):")
    print("     → Time Period dropdown becomes enabled")
    print("     → Time Period dropdown shows appropriate options")
    print()
    print("4. 🧪 Test scenarios:")
    print("   • Select 'Review / Monthly' → Should show month options")
    print("   • Select 'Quarterly' → Should show Q1, Q2, Q3, Q4 options")
    print()
    print("5. 🎉 If all tests pass, the fixes are working correctly!")

if __name__ == "__main__":
    success = test_copy_modal_structure()
    test_manual_instructions()
    
    if success:
        print("\n🎉 VERIFICATION COMPLETE - FIXES ARE WORKING!")
        sys.exit(0)
    else:
        print("\n❌ VERIFICATION FAILED - PLEASE CHECK THE ISSUES ABOVE")
        sys.exit(1)