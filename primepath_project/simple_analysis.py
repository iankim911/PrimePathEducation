#!/usr/bin/env python3
"""
Simple test to analyze answer input interface issues
"""

import requests
import os
import sys

def analyze_interface():
    print("=" * 60)
    print("PRIMEPATH ANSWER INPUT ANALYSIS")
    print("=" * 60)
    
    # Check server
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=2)
        print(f"Server running: {response.status_code}")
    except Exception as e:
        print(f"Server not accessible: {e}")
        return
    
    # Try to access test page with correct URLs
    test_urls = [
        'http://127.0.0.1:8000/api/placement/start/',
        'http://127.0.0.1:8000/api/placement/sessions/',
        'http://127.0.0.1:8000/',
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"URL {url}: {response.status_code}")
            if response.status_code == 200:
                html = response.text
                
                # Check for input elements
                checks = {
                    'radio buttons': 'type="radio"' in html,
                    'text inputs': 'type="text"' in html,
                    'textareas': '<textarea' in html,
                    'form elements': '<form' in html,
                    'answer options': 'answer-options' in html
                }
                
                print(f"Elements found in {url}:")
                for name, found in checks.items():
                    print(f"  {name}: {'YES' if found else 'NO'}")
                    
                if url.endswith('start/'):
                    if 'student_name' in html:
                        print("  Start form detected")
                        
        except Exception as e:
            print(f"Error with {url}: {e}")
    
    print("Analysis complete")

if __name__ == "__main__":
    analyze_interface()