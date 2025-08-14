#!/usr/bin/env python
"""Quick test to verify Answer Keys section is restored"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from placement_test.models import Exam
from django.urls import reverse

def quick_test():
    print("\n" + "="*60)
    print("QUICK TEST: Answer Keys Section Restoration")
    print("="*60 + "\n")
    
    # Get an exam to test with
    exam = Exam.objects.filter(name__contains='PlacementTest').first()
    if not exam:
        print("[FAIL] No exam found. Please create an exam first.")
        return
        
    print(f"Testing with exam: {exam.name}")
    print(f"Exam ID: {exam.id}\n")
    
    # Create test client
    client = Client()
    
    # Test the preview page
    try:
        url = reverse('PlacementTest:preview_exam', kwargs={'exam_id': exam.id})
        print(f"Testing URL: {url}")
        
        response = client.get(url)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for key sections
            checks = {
                "Page Title": "Preview & Answer Keys" in content,
                "PDF Section": "pdf-section" in content or "PDF Preview" in content,
                "Audio Section": "Audio Files" in content,
                "Answer Keys Section": "answers-section" in content or "Answer Keys Section" in content,
                "Save Button": "saveAllAnswers" in content,
                "Question Entries": "question-entry" in content,
                "Question Type Select": "question-type-select" in content,
                "MCQ Options": "selectMCQ" in content,
            }
            
            print("\nSection Checks:")
            print("-" * 40)
            
            all_passed = True
            for check_name, result in checks.items():
                symbol = "[PASS]" if result else "[FAIL]"
                print(f"{symbol} {check_name}: {'Found' if result else 'Missing'}")
                if not result:
                    all_passed = False
                    
            print("\n" + "="*60)
            if all_passed:
                print("SUCCESS! All sections are present.")
                print("The Answer Keys section has been successfully restored!")
            else:
                print("WARNING: Some sections are missing.")
                print("Please check the template being used.")
                
            # Additional check for template name
            if "preview_and_answers.html" in str(response):
                print("\n[PASS] Correct template is being used: preview_and_answers.html")
            else:
                print("\n[INFO] Check which template is being rendered")
                
        else:
            print(f"[FAIL] Failed to load page. Status: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Error during test: {str(e)}")
        
    print("="*60 + "\n")

if __name__ == "__main__":
    quick_test()