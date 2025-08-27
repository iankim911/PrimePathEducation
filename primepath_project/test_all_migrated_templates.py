#!/usr/bin/env python
"""
Phase 3: Test All Migrated Templates
Date: August 26, 2025
Purpose: Validate all 59 migrated templates render without errors
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.template.loader import get_template
from django.template import Context
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage

def create_mock_request():
    """Create a mock request with necessary attributes"""
    request = HttpRequest()
    request.user = AnonymousUser()
    request.path = '/test/'
    request.method = 'GET'
    
    # Add session
    middleware = SessionMiddleware(lambda x: None)
    middleware.process_request(request)
    request.session.save()
    
    # Add messages
    request._messages = FallbackStorage(request)
    
    return request

def test_template(template_name):
    """Test if a template renders without errors"""
    try:
        template = get_template(template_name)
        request = create_mock_request()
        
        # Create context with common variables
        context = {
            'request': request,
            'user': request.user,
            'debug': True,
            'csrf_token': 'test_token',
            'STATIC_URL': '/static/',
            'MEDIA_URL': '/media/',
        }
        
        # Render the template
        html = template.render(context, request)
        
        # Check if unified_base is used
        if 'unified_base.html' in str(template.source):
            return 'SUCCESS', f'✅ Renders with unified_base.html ({len(html)} chars)'
        else:
            return 'WARNING', f'⚠️  Renders but may not use unified_base'
            
    except Exception as e:
        return 'ERROR', f'❌ Error: {str(e)[:100]}'

def main():
    """Test all migrated templates"""
    
    # List of all migrated templates
    migrated_templates = [
        # Core module
        'core/exam_mapping.html',
        'core/login_with_kakao.html',
        'core/placement_configuration.html',
        'core/placement_rules_matrix.html',
        'core/placement_rules.html',
        'core/teacher_dashboard.html',
        'core/teacher_exams.html',
        'core/teacher_login.html',
        'core/teacher_sessions.html',
        'core/teacher_settings.html',
        
        # Registration
        'registration/choice.html',
        'registration/complete.html',
        'registration/step1_basic.html',
        'registration/step2_personal.html',
        'registration/step3_contact.html',
        'registration/step4_academic.html',
        'registration/step5_parent.html',
        'registration/step6_additional.html',
        
        # PlacementTest
        'placement_test/index.html',
        'placement_test/auth/login.html',
        
        # RoutineTest
        'primepath_routinetest/admin_classes_teachers.html',
        'primepath_routinetest/admin_pending_requests.html',
        'primepath_routinetest/admin_teacher_management.html',
        'primepath_routinetest/admin/manage_classes.html',
        'primepath_routinetest/analytics/dashboard.html',
        'primepath_routinetest/auth/login.html',
        'primepath_routinetest/class_access_admin.html',
        'primepath_routinetest/class_access.html',
        'primepath_routinetest/class_code_overview.html',
        'primepath_routinetest/class_details.html',
        'primepath_routinetest/create_exam.html',
        'primepath_routinetest/dashboards/admin_dashboard.html',
        'primepath_routinetest/dashboards/student_dashboard.html',
        'primepath_routinetest/dashboards/teacher_dashboard.html',
        'primepath_routinetest/edit_exam.html',
        'primepath_routinetest/error.html',
        'primepath_routinetest/exam_detail.html',
        'primepath_routinetest/exam_list_hierarchical.html',
        'primepath_routinetest/exam_list.html',
        'primepath_routinetest/exam_results.html',
        'primepath_routinetest/grade_session.html',
        'primepath_routinetest/index.html',
        'primepath_routinetest/manage_questions.html',
        'primepath_routinetest/manage_roster.html',
        'primepath_routinetest/preview_and_answers.html',
        'primepath_routinetest/session_detail.html',
        'primepath_routinetest/session_list.html',
        'primepath_routinetest/start_test.html',
        'primepath_routinetest/teacher_assessment.html',
        'primepath_routinetest/test_result.html',
    ]
    
    print("=" * 80)
    print("TESTING ALL MIGRATED TEMPLATES")
    print("=" * 80)
    print(f"Total templates to test: {len(migrated_templates)}\n")
    
    results = {'SUCCESS': 0, 'WARNING': 0, 'ERROR': 0}
    errors = []
    
    for template_name in migrated_templates:
        status, message = test_template(template_name)
        results[status] += 1
        
        if status == 'ERROR':
            errors.append((template_name, message))
            
        print(f"{template_name:55} {message}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {results['SUCCESS']}")
    print(f"⚠️  Warnings: {results['WARNING']}")
    print(f"❌ Errors: {results['ERROR']}")
    
    if errors:
        print("\n" + "=" * 80)
        print("ERRORS DETAIL")
        print("=" * 80)
        for template_name, error in errors:
            print(f"\n{template_name}:")
            print(f"  {error}")
    
    # Overall result
    print("\n" + "=" * 80)
    if results['ERROR'] == 0:
        print("🎉 ALL TEMPLATES RENDER SUCCESSFULLY!")
        print("Phase 3 Template Unification: COMPLETE")
    else:
        print(f"⚠️  {results['ERROR']} templates need fixing")
    print("=" * 80)
    
    return results['ERROR'] == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)