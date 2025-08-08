#!/usr/bin/env python
"""Quick test to verify Student Interface fix"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from placement_test.models import Exam, StudentSession
from django.urls import reverse

def quick_test():
    print("\n" + "="*60)
    print("QUICK TEST: Student Test Interface Fix")
    print("="*60 + "\n")
    
    # Get or create a test session
    exam = Exam.objects.filter(name__contains='PlacementTest').first()
    if not exam:
        print("[FAIL] No exam found. Please create an exam first.")
        return
        
    print(f"Using exam: {exam.name}\n")
    
    # Get or create session
    session = StudentSession.objects.filter(
        exam=exam,
        completed_at__isnull=True  # Session not completed if completed_at is null
    ).first()
    
    if not session:
        session = StudentSession.objects.create(
            student_name="Test Student",
            parent_phone="0101234567",
            school_name_manual="Test School",
            grade=5,
            academic_rank="top",
            exam=exam,
            original_curriculum_level=exam.curriculum_level,
            ip_address="127.0.0.1"
        )
    
    print(f"Session ID: {session.id}")
    
    # Create test client
    client = Client()
    
    # Test the take_test page
    try:
        url = reverse('placement_test:take_test', kwargs={'session_id': session.id})
        print(f"Testing URL: {url}\n")
        
        response = client.get(url)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for key components
            checks = {
                "PDF Viewer": "pdf-viewer" in content or "pdf-canvas" in content,
                "PDF URL": "data-pdf-url" in content or "pdfUrl" in content,
                "Answer Inputs": "answer-input" in content or "answer-option" in content,
                "Question Panels": "question-panel" in content or "question-section" in content,
                "Test Form": "test-form" in content,
                "Timer": "timer" in content.lower(),
                "Navigation": "question-nav" in content or "navigation" in content,
                "JSON Config": 'id="django-js-config"' in content,
            }
            
            # Special check for JSON encoding
            json_properly_encoded = False
            if 'id="django-js-config"' in content:
                import re
                match = re.search(r'<script[^>]*id="django-js-config"[^>]*>(.*?)</script>', content, re.DOTALL)
                if match:
                    try:
                        json_data = match.group(1)
                        parsed = json.loads(json_data)
                        if 'session' in parsed and 'exam' in parsed:
                            json_properly_encoded = True
                            print("[PASS] JSON is properly single-encoded")
                        else:
                            print("[FAIL] JSON missing required fields")
                    except json.JSONDecodeError:
                        print("[FAIL] JSON decode error - likely double-encoded")
                else:
                    print("[FAIL] Could not extract JSON data")
            
            print("\nComponent Checks:")
            print("-" * 40)
            
            all_passed = True
            for check_name, result in checks.items():
                symbol = "[PASS]" if result else "[FAIL]"
                print(f"{symbol} {check_name}: {'Found' if result else 'Missing'}")
                if not result:
                    all_passed = False
                    
            # Check template being used
            from django.conf import settings
            use_v2 = getattr(settings, 'FEATURE_FLAGS', {}).get('USE_V2_TEMPLATES', False)
            print(f"\n[INFO] V2 Templates enabled: {use_v2}")
            
            if use_v2 and "student_test_v2.html" in str(response):
                print("[PASS] Using V2 template as expected")
            elif not use_v2 and "student_test.html" in str(response):
                print("[PASS] Using standard template as expected")
            else:
                print("[INFO] Template selection to verify")
                
            print("\n" + "="*60)
            if all_passed and json_properly_encoded:
                print("SUCCESS! Student interface is working properly.")
                print("- PDF viewer component present")
                print("- Answer input modules present")
                print("- JSON properly encoded (not double-encoded)")
                print("- All critical components found")
            else:
                print("WARNING: Some components are missing or broken.")
                print("Please check the results above.")
                
        else:
            print(f"[FAIL] Failed to load page. Status: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Error during test: {str(e)}")
        
    print("="*60 + "\n")

if __name__ == "__main__":
    quick_test()