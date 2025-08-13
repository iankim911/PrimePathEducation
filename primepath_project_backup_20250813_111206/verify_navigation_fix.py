#!/usr/bin/env python
"""
Final Verification Script for Navigation Fix
This confirms the navigation names are correct
"""
import sys
import time

def verify_fix():
    print("=" * 60)
    print("🔍 NAVIGATION FIX VERIFICATION")
    print("=" * 60)
    
    # Check template file
    print("\n1. Checking template file...")
    with open('templates/base.html', 'r') as f:
        content = f.read()
    
    template_ok = (
        '>Level Exams</a>' in content and 
        '>Student Levels</a>' in content and
        '>Exam-to-Level Mapping</a>' not in content and
        '>Placement Rules</a>' not in content
    )
    
    if template_ok:
        print("   ✅ Template file is correct")
    else:
        print("   ❌ Template file needs fixing")
    
    # Check server response
    print("\n2. Checking server response...")
    try:
        import requests
        response = requests.get(
            'http://127.0.0.1:8000/', 
            params={'_v': int(time.time())}
        )
        html = response.text
        
        server_ok = (
            '>Level Exams</a>' in html and
            '>Student Levels</a>' in html and
            '>Exam-to-Level Mapping</a>' not in html and
            '>Placement Rules</a>' not in html
        )
        
        if server_ok:
            print("   ✅ Server is returning correct names")
        else:
            print("   ❌ Server still returning old names")
            print("      (Restart server if this fails)")
    except Exception as e:
        print(f"   ⚠️ Could not reach server: {e}")
        print("      Make sure server is running")
    
    # Final result
    print("\n" + "=" * 60)
    if template_ok and server_ok:
        print("✅ NAVIGATION FIX VERIFIED - ALL CORRECT!")
        print("\nYou should now see:")
        print("  • 'Level Exams' (instead of 'Exam-to-Level Mapping')")
        print("  • 'Student Levels' (instead of 'Placement Rules')")
        print("\nIf browser still shows old names:")
        print("  1. Clear browser cache (Cmd+Shift+R)")
        print("  2. Or use incognito mode")
    else:
        print("⚠️ FIX NOT COMPLETE - Check issues above")
    print("=" * 60)

if __name__ == "__main__":
    verify_fix()