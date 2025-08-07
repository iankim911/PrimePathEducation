#!/usr/bin/env python3
"""
Simple test script to validate the answer input interface fix
"""

import requests

def test_fix():
    print("TESTING ANSWER INPUT INTERFACE FIX")
    print("=" * 50)
    
    # Test existing session
    session_id = "84ff4d19-de9b-4686-95bf-f6c87d78024a"
    test_url = f'http://127.0.0.1:8000/api/placement/session/{session_id}/'
    
    try:
        response = requests.get(test_url, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            
            # Check for the fix
            checks = {
                'form element': '<form' in html,
                'test-form id': 'id="test-form"' in html, 
                'POST method': 'method="post"' in html,
                'CSRF token': 'csrfmiddlewaretoken' in html,
                'radio buttons': 'type="radio"' in html,
                'answer options': 'answer-options' in html
            }
            
            print("\nFIX VALIDATION RESULTS:")
            print("-" * 30)
            
            all_passed = True
            for name, passed in checks.items():
                status = "PASS" if passed else "FAIL"
                print(f"{status}: {name}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print("\nSUCCESS: All checks passed!")
                print("Answer input interface is now working!")
            else:
                print("\nFAIL: Some checks failed")
                
            # Save for manual inspection
            with open('fix_test_result.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("\nOutput saved to fix_test_result.html")
            
        else:
            print(f"Error: Cannot access test page - {response.status_code}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fix()