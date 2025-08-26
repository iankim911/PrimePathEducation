#!/usr/bin/env python
"""
Phase 3, Day 2: Test Migrated Templates
Verify that migrated templates still render correctly
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.template.loader import get_template
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage


def test_migrated_template(template_name):
    """Test that a migrated template renders without errors."""
    try:
        # Create mock request with messages support
        factory = RequestFactory()
        request = factory.get('/')
        
        # Add session support
        from django.contrib.sessions.backends.db import SessionStore
        request.session = SessionStore()
        
        # Add messages framework support
        from django.contrib.messages import get_messages
        messages = get_messages(request)
        
        # Create a mock user
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        
        # Load and render template
        template = get_template(template_name)
        context = {
            'request': request,
            'user': request.user,
            'debug': True,
            'csrf_token': 'test-token',
            'messages': []
        }
        html = template.render(context)
        
        # Check for basic rendering success
        checks = [
            ('No template syntax errors', '{%' not in html and '{{' not in html),
            ('HTML structure present', '<html' in html or '<div' in html),
            ('Unified config present', 'PRIMEPATH_CONFIG' in html),
            ('No migration artifacts', '{%% comment %%}' not in html)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if not passed:
                all_passed = False
                
        return all_passed, checks
        
    except Exception as e:
        return False, str(e)


def test_batch():
    """Test a batch of migrated templates."""
    
    # Templates we've migrated so far
    migrated_templates = [
        # Registration templates
        'registration/choice.html',
        'registration/complete.html',
        'registration/step1_basic.html',
        'registration/step2_personal.html',
        'registration/step3_contact.html',
        'registration/step4_academic.html',
        'registration/step5_parent.html',
        'registration/step6_additional.html',
        
        # Core templates
        'core/login_with_kakao.html',
        'core/teacher_login.html',
        'core/teacher_dashboard.html',
        'core/teacher_exams.html',
        'core/teacher_sessions.html',
        'core/teacher_settings.html',
        'core/placement_rules.html',
        'core/placement_rules_matrix.html',
        'core/placement_configuration.html',
        'core/exam_mapping.html',
    ]
    
    print("=" * 80)
    print("TESTING MIGRATED TEMPLATES")
    print("=" * 80)
    print()
    
    results = {
        'passed': [],
        'failed': []
    }
    
    for template_name in migrated_templates:
        print(f"Testing {template_name}... ", end='')
        success, details = test_migrated_template(template_name)
        
        if success:
            print("✅ PASSED")
            results['passed'].append(template_name)
        else:
            print(f"❌ FAILED")
            if isinstance(details, str):
                print(f"  Error: {details}")
            else:
                for check_name, passed in details:
                    if not passed:
                        print(f"  ❌ {check_name}")
            results['failed'].append(template_name)
    
    print()
    print("=" * 80)
    print("MIGRATION TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {len(results['passed'])} templates")
    print(f"❌ Failed: {len(results['failed'])} templates")
    
    if results['failed']:
        print("\nFailed templates:")
        for template in results['failed']:
            print(f"  - {template}")
    
    return len(results['failed']) == 0


if __name__ == '__main__':
    success = test_batch()
    
    if success:
        print("\n🎉 All migrated templates are working correctly!")
        print("Ready to continue migration.")
    else:
        print("\n⚠️  Some templates have issues. Please investigate before continuing.")
    
    sys.exit(0 if success else 1)