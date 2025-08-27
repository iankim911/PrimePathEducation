#!/usr/bin/env python
"""
Phase 3: Test Batch 1 Templates
Date: August 27, 2025
Purpose: Test the 5 migrated Batch 1 templates
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

# Batch 1 templates
BATCH_1_TEMPLATES = [
    'core/auth/login.html',
    'core/index.html',
    'core/auth/profile.html',
    'core/auth/logout_confirm.html',
    'core/base_clean.html',  # Legacy adapter
]

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

def test_template_rendering(template_name):
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
        
        # Special context for specific templates
        if 'login' in template_name:
            context['next'] = '/dashboard/'
        
        # Render the template
        html = template.render(context, request)
        
        # Check if unified_base is used by looking at template content
        template_content = ''
        try:
            # Try to get the template source content
            if hasattr(template, 'source'):
                template_content = str(template.source)
            elif hasattr(template, 'template'):
                template_content = str(template.template)
            else:
                # Fallback - read the template file directly
                import os
                template_file = os.path.join('templates', template_name)
                if os.path.exists(template_file):
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_content = f.read()
        except Exception as e:
            template_content = ''
        
        if 'unified_base.html' in template_content or 'extends "unified_base.html"' in template_content:
            return {
                'status': 'SUCCESS',
                'message': f'✅ Renders with unified_base.html ({len(html)} chars)',
                'uses_unified': True,
                'html_length': len(html)
            }
        else:
            return {
                'status': 'WARNING', 
                'message': f'⚠️  Renders but may not use unified_base ({len(html)} chars)',
                'uses_unified': False,
                'html_length': len(html)
            }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'message': f'❌ Error: {str(e)[:100]}',
            'uses_unified': False,
            'html_length': 0
        }

def check_template_migration_status():
    """Check which templates are in the middleware MIGRATED_TEMPLATES"""
    try:
        from primepath_project.template_compatibility import TemplateCompatibilityMiddleware
        migrated_set = TemplateCompatibilityMiddleware.MIGRATED_TEMPLATES
        
        batch1_migrated = [t for t in BATCH_1_TEMPLATES if t in migrated_set]
        batch1_not_migrated = [t for t in BATCH_1_TEMPLATES if t not in migrated_set]
        
        return batch1_migrated, batch1_not_migrated
    except ImportError as e:
        print(f"⚠️  Could not import middleware: {e}")
        return [], BATCH_1_TEMPLATES

def main():
    """Test all Batch 1 templates"""
    
    print("=" * 80)
    print("PHASE 3: BATCH 1 TEMPLATE TESTING")
    print("=" * 80)
    print(f"Testing {len(BATCH_1_TEMPLATES)} migrated templates\n")
    
    # Check migration status in middleware
    migrated, not_migrated = check_template_migration_status()
    
    if migrated:
        print("📋 Templates marked as migrated in middleware:")
        for template in migrated:
            print(f"  ✅ {template}")
    
    if not_migrated:
        print("📋 Templates NOT yet marked as migrated:")
        for template in not_migrated:
            print(f"  ⏳ {template}")
    
    print("\n" + "-" * 80)
    print("TEMPLATE RENDERING TESTS")
    print("-" * 80)
    
    results = {'SUCCESS': 0, 'WARNING': 0, 'ERROR': 0}
    test_results = []
    
    for template_name in BATCH_1_TEMPLATES:
        print(f"Testing: {template_name:<35}", end=" ")
        result = test_template_rendering(template_name)
        results[result['status']] += 1
        test_results.append((template_name, result))
        print(result['message'])
    
    # Summary
    print("\n" + "=" * 80)
    print("BATCH 1 TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {results['SUCCESS']}")
    print(f"⚠️  Warnings: {results['WARNING']}")
    print(f"❌ Errors: {results['ERROR']}")
    
    # Detailed analysis
    unified_count = sum(1 for _, result in test_results if result['uses_unified'])
    print(f"📊 Using unified_base.html: {unified_count}/{len(BATCH_1_TEMPLATES)}")
    
    # Show errors if any
    errors = [(name, result) for name, result in test_results if result['status'] == 'ERROR']
    if errors:
        print("\n" + "=" * 80)
        print("ERRORS DETAIL")
        print("=" * 80)
        for template_name, result in errors:
            print(f"\n{template_name}:")
            print(f"  {result['message']}")
    
    # Next steps
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    
    if results['ERROR'] == 0:
        print("🎉 All Batch 1 templates render successfully!")
        if not_migrated:
            print("📝 TODO: Update TemplateCompatibilityMiddleware to mark these as migrated:")
            for template in not_migrated:
                print(f"     '{template}',")
        print("✅ Ready to proceed with Batch 2 migration")
    else:
        print(f"⚠️  {results['ERROR']} templates have errors - fix before proceeding")
        print("🔧 Review errors above and fix template issues")
    
    return results['ERROR'] == 0

if __name__ == '__main__':
    success = main()
    
    if success:
        print("\n🚀 Batch 1 testing completed successfully!")
        print("Ready for Batch 2 migration...")
    else:
        print("\n❌ Batch 1 testing failed - fix errors before proceeding")
    
    sys.exit(0 if success else 1)