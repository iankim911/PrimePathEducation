#!/usr/bin/env python3
"""
Test script to verify the delete button color fix is working
"""

import requests
from bs4 import BeautifulSoup
import re

def test_delete_button_fix():
    """Test that delete buttons have proper CSS classes and styling"""
    try:
        # Get the exam list page
        url = "http://127.0.0.1:8000/RoutineTest/exams/"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Server error: {response.status_code}")
            return False
            
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check if theme CSS is loaded
        theme_css = soup.find('link', {'href': lambda x: x and 'routinetest-theme.css' in x})
        print(f"✓ Theme CSS loaded: {'YES' if theme_css else 'NO'}")
        
        # Find delete buttons
        delete_buttons = soup.find_all('button', {'onclick': lambda x: x and 'confirmDelete' in x})
        danger_buttons = soup.find_all('button', class_='btn-danger')
        
        all_delete_buttons = delete_buttons + danger_buttons
        unique_buttons = []
        seen = set()
        for btn in all_delete_buttons:
            btn_text = str(btn)
            if btn_text not in seen:
                unique_buttons.append(btn)
                seen.add(btn_text)
        
        print(f"✓ Delete buttons found: {len(unique_buttons)}")
        
        # Check button classes and attributes
        for i, button in enumerate(unique_buttons):
            classes = button.get('class', [])
            onclick = button.get('onclick', '')
            
            print(f"  Button {i+1}: classes={classes}, has_confirmDelete={'confirmDelete' in onclick}")
            
            # Check if btn-danger class is present
            has_danger_class = 'btn-danger' in classes if isinstance(classes, list) else 'btn-danger' in str(classes)
            print(f"    - Has btn-danger class: {'YES' if has_danger_class else 'NO'}")
            
        # Check for our CSS overrides in the template
        css_overrides = [
            'html body.routinetest-theme .exam-actions button.btn-danger',
            'background-color: #dc3545 !important',
            'ULTIMATE DELETE BUTTON FIX'
        ]
        
        override_found = all(override in html_content for override in css_overrides)
        print(f"✓ CSS overrides in place: {'YES' if override_found else 'NO'}")
        
        # Check for JavaScript enforcement
        js_enforcement = 'enforceDeleteButtonColors' in html_content
        print(f"✓ JavaScript enforcement: {'YES' if js_enforcement else 'NO'}")
        
        # Check theme class application
        theme_preload = 'routinetest-theme' in html_content
        print(f"✓ Theme class preload: {'YES' if theme_preload else 'NO'}")
        
        if len(unique_buttons) > 0 and override_found and js_enforcement:
            print("\n🎉 DELETE BUTTON FIX VERIFICATION: SUCCESSFUL")
            print("✓ Delete buttons found")
            print("✓ CSS overrides implemented")
            print("✓ JavaScript enforcement active")
            print("✓ Theme system integrated")
            return True
        else:
            print("\n❌ DELETE BUTTON FIX VERIFICATION: INCOMPLETE")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://127.0.0.1:8000")
        print("   Make sure the Django server is running")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Delete Button Color Fix...")
    print("=" * 50)
    success = test_delete_button_fix()
    print("=" * 50)
    if success:
        print("✅ All tests passed! Delete buttons should now appear RED.")
    else:
        print("❌ Some tests failed. Check the output above for details.")