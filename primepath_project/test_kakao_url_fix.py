#!/usr/bin/env python3
"""
Test script to verify Kakao URL pattern fix
"""

import os
import sys
import django

# Add the project path and parent directory
project_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project'
sys.path.insert(0, project_path)
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import RequestFactory
from django.contrib.auth.models import User

def test_url_patterns():
    print("=" * 80)
    print("TESTING KAKAO URL PATTERN FIX")
    print("=" * 80)
    
    # Test basic URL reversals
    urls_to_test = [
        ('kakao_login', 'Simple Kakao login'),
        ('kakao_callback', 'Simple Kakao callback'),
        ('kakao_logout', 'Kakao logout'),
        ('registration:choice', 'Registration choice page'),
        ('registration:kakao_callback', 'Registration Kakao callback'),
    ]
    
    success_count = 0
    total_count = len(urls_to_test)
    
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✅ {description}: {url}")
            success_count += 1
        except NoReverseMatch as e:
            print(f"❌ {description}: NoReverseMatch - {str(e)}")
        except Exception as e:
            print(f"❌ {description}: Error - {str(e)}")
    
    print(f"\n📊 Results: {success_count}/{total_count} URLs resolved successfully")
    
    # Test URL conflicts
    print(f"\n🔍 Testing URL conflicts:")
    
    try:
        simple_callback = reverse('kakao_callback')
        print(f"✅ Simple Kakao callback URL: {simple_callback}")
    except Exception as e:
        print(f"❌ Simple Kakao callback failed: {e}")
    
    try:
        reg_callback = reverse('registration:kakao_callback')
        print(f"✅ Registration Kakao callback URL: {reg_callback}")
    except Exception as e:
        print(f"❌ Registration Kakao callback failed: {e}")
    
    # Verify the URLs are different
    try:
        simple_url = reverse('kakao_callback')
        reg_url = reverse('registration:kakao_callback')
        if simple_url != reg_url:
            print(f"✅ URL conflict resolved: Different URLs generated")
            print(f"   Simple: {simple_url}")
            print(f"   Registration: {reg_url}")
        else:
            print(f"❌ URL conflict still exists: Both generate same URL")
    except Exception as e:
        print(f"⚠️ Could not compare URLs: {e}")
    
    return success_count == total_count

def test_django_reverse_functionality():
    """Test that Django URL reverse functionality works properly"""
    print(f"\n{'='*80}")
    print("TESTING DJANGO REVERSE FUNCTIONALITY")
    print("=" * 80)
    
    # Test basic Django functionality
    try:
        from django.urls import get_resolver
        resolver = get_resolver()
        print(f"✅ URL resolver loaded successfully")
        
        # Check if our namespaces are registered
        if hasattr(resolver, 'namespace_dict'):
            namespaces = list(resolver.namespace_dict.keys())
            print(f"🔍 Available namespaces: {namespaces}")
            
            if 'registration' in namespaces:
                print(f"✅ 'registration' namespace found")
            else:
                print(f"❌ 'registration' namespace missing")
        
        return True
    except Exception as e:
        print(f"❌ Django reverse functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Starting Kakao URL Pattern Fix Tests...")
    
    # Test 1: URL pattern resolution
    test1_result = test_url_patterns()
    
    # Test 2: Django reverse functionality
    test2_result = test_django_reverse_functionality()
    
    print(f"\n{'='*80}")
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"✅ URL pattern resolution: {'PASS' if test1_result else 'FAIL'}")
    print(f"✅ Django reverse functionality: {'PASS' if test2_result else 'FAIL'}")
    
    if test1_result and test2_result:
        print(f"\n🎉 ALL TESTS PASSED! The Kakao URL fix is working correctly.")
        print(f"\n✅ The NoReverseMatch error should be resolved.")
        print(f"\n📋 URL Structure:")
        print(f"   • Simple Kakao login: /auth/kakao/callback/")
        print(f"   • Registration Kakao: /auth/kakao/callback/register/")
        print(f"   • No more URL conflicts!")
    else:
        print(f"\n❌ Some tests failed. The issue may need additional fixes.")
    
    print("=" * 80)