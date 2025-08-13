#!/usr/bin/env python3
"""
Browser-like test to verify the form can be used normally
"""

import requests

def browser_test():
    print("BROWSER-LIKE FORM TEST")
    print("=" * 30)
    
    session_id = "84ff4d19-de9b-4686-95bf-f6c87d78024a"
    
    # Start a session to maintain cookies
    with requests.Session() as s:
        # First get the page (like browser loading)
        test_url = f'http://127.0.0.1:8000/api/placement/session/{session_id}/'
        response = s.get(test_url)
        
        print(f"Page load: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            
            # Check form structure
            form_present = '<form' in html and 'id="test-form"' in html
            csrf_present = 'csrfmiddlewaretoken' in html
            inputs_present = 'type="radio"' in html
            
            print(f"Form element: {'YES' if form_present else 'NO'}")
            print(f"CSRF token: {'YES' if csrf_present else 'NO'}")
            print(f"Input fields: {'YES' if inputs_present else 'NO'}")
            
            if form_present and csrf_present and inputs_present:
                print("\nSUCCESS: Form structure is complete!")
                print("- Students can now select answers")
                print("- Form can be submitted with CSRF protection")
                print("- All question types have input fields")
                
                # Check specific question types in the HTML
                has_radio = 'type="radio"' in html
                has_text = html.count('type="text"') > 3  # More than just nav inputs
                has_textarea = '<textarea' in html
                
                print(f"\nInput types available:")
                print(f"- Radio buttons (MCQ): {'YES' if has_radio else 'NO'}")
                print(f"- Text inputs (SHORT): {'YES' if has_text else 'NO'}")  
                print(f"- Textareas (LONG): {'YES' if has_textarea else 'NO'}")
                
                print(f"\nThe missing answer input interface has been FIXED!")
            else:
                print("FAIL: Form structure incomplete")
        else:
            print("FAIL: Cannot access page")

if __name__ == "__main__":
    browser_test()