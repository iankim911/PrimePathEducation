#!/usr/bin/env python3
"""
Test to see what HTML is actually being served
"""

import requests
from bs4 import BeautifulSoup

def test_actual_html():
    """Check what's actually in the HTML"""
    try:
        url = "http://127.0.0.1:8000/RoutineTest/exams/"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Server error: {response.status_code}")
            return
            
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for the exam library container
        exam_library = soup.find('div', class_='exam-library-container')
        if exam_library:
            print("✓ Found exam-library-container")
        else:
            print("❌ No exam-library-container found")
            
        # Look for exam cards
        exam_cards = soup.find_all('div', class_='exam-card')
        print(f"✓ Found {len(exam_cards)} exam cards")
        
        # Look for any button with Delete text
        all_buttons = soup.find_all('button')
        delete_buttons = [btn for btn in all_buttons if 'Delete' in (btn.text or '')]
        print(f"✓ Found {len(delete_buttons)} buttons with 'Delete' text")
        
        # Look for exam-actions divs
        exam_actions = soup.find_all('div', class_='exam-actions')
        print(f"✓ Found {len(exam_actions)} exam-actions divs")
        
        # Check first exam-actions content
        if exam_actions:
            first_actions = exam_actions[0]
            print("\nFirst exam-actions content:")
            print("  Buttons found:", len(first_actions.find_all('button')))
            print("  Links found:", len(first_actions.find_all('a')))
            
            # Print button texts
            for btn in first_actions.find_all('button'):
                print(f"    Button: {btn.text.strip()}")
            for link in first_actions.find_all('a'):
                print(f"    Link: {link.text.strip()}")
                
        # Check for the debug script
        debug_scripts = [s for s in soup.find_all('script') if 'DELETE_BUTTON_DEBUG' in str(s)]
        print(f"\n✓ Found {len(debug_scripts)} DELETE_BUTTON_DEBUG scripts")
        
        # Check for the forced visibility delete button
        forced_delete = soup.find('button', attrs={'data-exam-id': True})
        if forced_delete:
            print("✓ Found button with data-exam-id attribute")
            print(f"  Text: {forced_delete.text.strip()}")
            print(f"  Classes: {forced_delete.get('class', [])}")
        else:
            print("❌ No button with data-exam-id found")
            
        # Save a sample of the HTML for inspection
        with open('exam_page_sample.html', 'w') as f:
            f.write(html_content[:5000])
        print("\n✓ Saved first 5000 chars to exam_page_sample.html")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 Checking actual HTML content...")
    print("=" * 50)
    test_actual_html()