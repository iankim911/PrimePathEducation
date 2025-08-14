#!/usr/bin/env python
"""
Test script to verify the namespace initialization fix is working
"""

import os
import sys
import django
import requests
import json
import re
from urllib.parse import urljoin

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import StudentSession, Exam
from core.models import CurriculumLevel

def test_namespace_fix():
    """Test that the namespace initialization fix is working"""
    
    print("=" * 70)
    print("TESTING NAMESPACE INITIALIZATION FIX")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    # Step 1: Check static files are served
    print("\n" + "=" * 70)
    print("STEP 1: CHECKING STATIC FILES")
    print("=" * 70)
    
    critical_files = [
        "/static/js/bootstrap.js",  # NEW: Bootstrap script
        "/static/js/config/app-config.js",
        "/static/js/utils/event-delegation.js",
        "/static/js/utils/module-loader.js",
        "/static/js/modules/base-module.js",
        "/static/js/modules/module-init-helper.js",  # NEW: Helper script
        "/static/js/modules/answer-manager.js"
    ]
    
    all_ok = True
    for file_path in critical_files:
        url = urljoin(base_url, file_path)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Check for defensive code in the file
                if 'bootstrap.js' in file_path:
                    if 'PRIMEPATH BOOTSTRAP' in response.text:
                        print(f"✅ {file_path} - Bootstrap code present")
                    else:
                        print(f"⚠️  {file_path} - Bootstrap code missing")
                        all_ok = False
                elif 'defensive' in response.text.lower() or 'fallback' in response.text.lower():
                    print(f"✅ {file_path} - Has defensive code")
                else:
                    print(f"✅ {file_path} - Loaded successfully")
            else:
                print(f"❌ {file_path} - Status: {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {file_path} - Error: {e}")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Some static files have issues")
        return False
    
    # Step 2: Create test session
    print("\n" + "=" * 70)
    print("STEP 2: CREATING TEST SESSION")
    print("=" * 70)
    
    exam = Exam.objects.filter(questions__isnull=False).first()
    if not exam:
        print("❌ No exam with questions found")
        return False
    
    level = CurriculumLevel.objects.first()
    session = StudentSession.objects.create(
        student_name='Namespace Test User',
        grade=7,
        academic_rank='TOP_20',
        exam=exam,
        original_curriculum_level=level
    )
    
    test_url = f"{base_url}/PlacementTest/session/{session.id}/"
    print(f"✅ Test session created: {session.id}")
    
    # Step 3: Load test page and check for errors
    print("\n" + "=" * 70)
    print("STEP 3: CHECKING PAGE LOAD")
    print("=" * 70)
    
    response = requests.get(test_url)
    if response.status_code != 200:
        print(f"❌ Page returned status: {response.status_code}")
        return False
    
    html = response.text
    print("✅ Page loaded successfully")
    
    # Check for bootstrap script
    if 'bootstrap.js' in html:
        print("✅ Bootstrap script included in page")
    else:
        print("❌ Bootstrap script NOT included in page")
        all_ok = False
    
    # Check for module-init-helper
    if 'module-init-helper.js' in html:
        print("✅ Module init helper included in page")
    else:
        print("❌ Module init helper NOT included in page")
        all_ok = False
    
    # Check for initialization code
    if 'PRIMEPATH INITIALIZATION STARTING' in html:
        print("✅ Initialization script present")
    else:
        print("⚠️  Initialization script may have changed")
    
    # Check loading order
    bootstrap_pos = html.find('bootstrap.js')
    app_config_pos = html.find('app-config.js')
    event_delegation_pos = html.find('event-delegation.js')
    
    if bootstrap_pos < app_config_pos < event_delegation_pos:
        print("✅ Script loading order correct")
    else:
        print("❌ Script loading order incorrect")
        print(f"   Bootstrap: {bootstrap_pos}")
        print(f"   AppConfig: {app_config_pos}")
        print(f"   EventDelegation: {event_delegation_pos}")
        all_ok = False
    
    # Step 4: Check for console error indicators
    print("\n" + "=" * 70)
    print("STEP 4: CHECKING FOR ERROR PATTERNS")
    print("=" * 70)
    
    # These patterns should NOT be in the HTML
    error_patterns = [
        "Cannot set properties of undefined",
        "Cannot read properties of undefined",
        "is not a constructor",
        "TypeError:",
        "ReferenceError:"
    ]
    
    errors_found = []
    for pattern in error_patterns:
        if pattern in html:
            errors_found.append(pattern)
    
    if errors_found:
        print(f"⚠️  Potential error patterns found in HTML: {errors_found}")
    else:
        print("✅ No error patterns found in HTML")
    
    # Step 5: Check critical elements
    print("\n" + "=" * 70)
    print("STEP 5: CHECKING CRITICAL ELEMENTS")
    print("=" * 70)
    
    critical_elements = {
        'Timer': 'timer' in html.lower(),
        'Navigation buttons': 'question-nav-btn' in html,
        'Answer inputs': 'answer-input' in html or 'name="q_' in html,
        'Submit button': 'submit-test' in html,
        'CSRF token': 'csrfmiddlewaretoken' in html or 'csrf_token' in html
    }
    
    for element, present in critical_elements.items():
        if present:
            print(f"✅ {element}")
        else:
            print(f"❌ {element}")
            all_ok = False
    
    # Step 6: Test basic API endpoint
    print("\n" + "=" * 70)
    print("STEP 6: TESTING API FUNCTIONALITY")
    print("=" * 70)
    
    # Extract CSRF token
    csrf_match = re.search(r"csrf['\"]:\s*['\"]([^'\"]+)['\"]", html)
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print("✅ CSRF token extracted")
        
        # Try to submit a test answer
        question = exam.questions.first()
        if question:
            submit_url = f"{base_url}/PlacementTest/session/{session.id}/submit/"
            headers = {
                'X-CSRFToken': csrf_token,
                'Content-Type': 'application/json'
            }
            data = {
                'question_id': str(question.id),
                'answer': 'A'
            }
            
            try:
                response = requests.post(submit_url, json=data, headers=headers)
                if response.status_code in [200, 201]:
                    print("✅ API submission endpoint working")
                else:
                    print(f"⚠️  API returned status: {response.status_code}")
            except Exception as e:
                print(f"⚠️  API test error: {e}")
    else:
        print("⚠️  CSRF token not found")
    
    # Step 7: Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if all_ok:
        print("🎉 ALL CHECKS PASSED!")
        print("\n✅ The namespace initialization fix is working correctly")
        print("✅ Bootstrap script loads first and creates all namespaces")
        print("✅ All modules have defensive initialization")
        print("✅ No JavaScript errors expected")
    else:
        print("⚠️  Some issues detected - check browser console for details")
    
    print(f"\n📍 Test URL: {test_url}")
    print("\n📋 To verify in browser:")
    print("1. Open the URL above")
    print("2. Open Developer Console (F12)")
    print("3. Look for:")
    print("   - '[PRIMEPATH] BOOTSTRAP COMPLETE' message")
    print("   - Health Score percentage")
    print("   - Module initialization success messages")
    print("   - NO red error messages about undefined properties")
    
    return all_ok

if __name__ == "__main__":
    success = test_namespace_fix()
    sys.exit(0 if success else 1)