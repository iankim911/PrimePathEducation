#!/usr/bin/env python3
"""
Final test to verify delete button implementation
"""

import requests
from bs4 import BeautifulSoup

def test_delete_button_final():
    """Final comprehensive delete button test"""
    try:
        url = "http://127.0.0.1:8000/RoutineTest/exams/"
        response = requests.get(url, timeout=10)
        
        print(f"Server Response Code: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check for version indicator
            version_indicator = "DELETE BUTTON FIX VERSION 8.21.2025" in html_content
            print(f"✓ Version indicator present: {'YES' if version_indicator else 'NO'}")
            
            # Check for exam-library-container
            exam_library = soup.find('div', class_='exam-library-container')
            print(f"✓ Exam library container found: {'YES' if exam_library else 'NO'}")
            
            # Check for delete buttons with data-version
            versioned_buttons = soup.find_all('button', attrs={'data-version': '8.21.2025'})
            print(f"✓ Delete buttons with version 8.21.2025: {len(versioned_buttons)}")
            
            # Check for any delete buttons
            all_delete_buttons = soup.find_all('button', text=lambda x: x and 'Delete' in x)
            print(f"✓ Total delete buttons found: {len(all_delete_buttons)}")
            
            # Check if logged in (should see login page if not)
            if "Teacher Login" in soup.title.text if soup.title else "":
                print("\n⚠️ IMPORTANT: You're seeing the login page!")
                print("   Please log in as admin and refresh the Exam Library page")
                print("   URL: http://127.0.0.1:8000/RoutineTest/exams/")
            else:
                print(f"\n✓ Page title: {soup.title.text if soup.title else 'No title'}")
                
            if version_indicator:
                print("\n🎉 SUCCESS: Template has been updated with delete button fix!")
                print("   Please refresh your browser (Ctrl+F5 or Cmd+Shift+R)")
                print("   Clear browser cache if needed")
            else:
                print("\n⚠️ Template may not be updated. Try:")
                print("   1. Clear browser cache")
                print("   2. Open in incognito/private window")
                print("   3. Hard refresh (Ctrl+F5 or Cmd+Shift+R)")
                
        else:
            print(f"❌ Unexpected response code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://127.0.0.1:8000")
        print("   Please ensure Django server is running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("FINAL DELETE BUTTON VERIFICATION")
    print("=" * 60)
    test_delete_button_final()
    print("=" * 60)