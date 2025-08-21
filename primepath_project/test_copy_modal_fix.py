#!/usr/bin/env python
"""
Test script to verify Copy modal functionality is working
"""

import os
import sys
import django
import time
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

def test_copy_modal():
    """Test that the copy modal can be displayed"""
    print("="*50)
    print("TESTING COPY MODAL FUNCTIONALITY")
    print("="*50)
    
    # Create test client
    client = Client()
    
    # Login as admin
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    client.force_login(admin_user)
    print(f"✅ Logged in as {admin_user.username}")
    
    # Get the Answer Keys page
    response = client.get('/routinetest/answer_keys/')
    if response.status_code != 200:
        print(f"❌ Failed to load Answer Keys page: {response.status_code}")
        return False
    
    print("✅ Answer Keys page loaded successfully")
    
    # Check if modal HTML is present
    content = response.content.decode('utf-8')
    
    checks = {
        'Modal element': 'id="copyExamModal"' in content,
        'Modal content': 'class="modal-content"' in content,
        'Modal close button': 'class="modal-close"' in content,
        'Copy form': 'id="copyExamForm"' in content,
        'openCopyModal function': 'function openCopyModal' in content,
        'closeCopyModal function': 'function closeCopyModal' in content,
        'Show class CSS': '.modal.show' in content or '#copyExamModal.show' in content,
        'Copy buttons': 'onclick="openCopyModal' in content
    }
    
    print("\n📋 Modal Component Checks:")
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}: {'Present' if passed else 'Missing'}")
        if not passed:
            all_passed = False
    
    # Check CSS rules
    print("\n🎨 CSS Rules Check:")
    css_checks = {
        'Modal hidden by default': '.modal {' in content and 'display: none' in content,
        'Show class with display flex': '.show' in content and 'display: flex !important' in content,
        'High specificity rule': 'body .modal.show' in content or 'body #copyExamModal.show' in content
    }
    
    for check_name, passed in css_checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    # Final result
    print("\n" + "="*50)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Copy modal should be working!")
        print("\nTo verify in browser:")
        print("1. Go to http://127.0.0.1:8000/routinetest/answer_keys/")
        print("2. Click any 'Copy' button next to an exam")
        print("3. The modal should appear with a form to copy the exam")
    else:
        print("❌ SOME CHECKS FAILED - Modal may not work properly")
        print("\nIssues found - please review the template file")
    
    return all_passed

if __name__ == '__main__':
    success = test_copy_modal()
    sys.exit(0 if success else 1)