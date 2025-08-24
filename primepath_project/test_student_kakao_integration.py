#!/usr/bin/env python
"""Test Student Kakao OAuth Integration"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
django.setup()

from django.test import Client
from django.urls import reverse
from django.conf import settings
from primepath_student.models import StudentProfile
from django.contrib.auth.models import User


def test_kakao_urls():
    """Test that Kakao URLs are properly configured"""
    print("\n" + "="*50)
    print("Testing Kakao URLs Configuration")
    print("="*50)
    
    client = Client()
    
    # Test Kakao login URL
    try:
        response = client.get(reverse('primepath_student:kakao_login'))
        if response.status_code == 302:  # Should redirect to Kakao
            print("✅ Kakao login URL works - redirects to Kakao OAuth")
            print(f"   Redirect URL: {response.url[:50]}...")
        else:
            print(f"❌ Kakao login URL returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing Kakao login URL: {e}")
    
    # Test callback URL exists
    try:
        response = client.get(reverse('primepath_student:kakao_callback'))
        # Should redirect to login since no auth code
        if response.status_code in [302, 200]:
            print("✅ Kakao callback URL is configured")
        else:
            print(f"❌ Kakao callback URL returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing Kakao callback URL: {e}")
    
    return True


def test_kakao_settings():
    """Test that Kakao settings are configured"""
    print("\n" + "="*50)
    print("Testing Kakao Settings")
    print("="*50)
    
    if hasattr(settings, 'KAKAO_REST_API_KEY'):
        print(f"✅ KAKAO_REST_API_KEY is configured: {settings.KAKAO_REST_API_KEY[:10]}...")
    else:
        print("❌ KAKAO_REST_API_KEY not found in settings")
    
    if hasattr(settings, 'KAKAO_JAVASCRIPT_KEY'):
        print(f"✅ KAKAO_JAVASCRIPT_KEY is configured: {settings.KAKAO_JAVASCRIPT_KEY[:10]}...")
    else:
        print("❌ KAKAO_JAVASCRIPT_KEY not found in settings")
    
    # Check authentication backends
    if 'primepath_student.kakao_auth.StudentKakaoOAuth2Backend' in settings.AUTHENTICATION_BACKENDS:
        print("✅ Student Kakao authentication backend is configured")
    else:
        print("❌ Student Kakao authentication backend not in AUTHENTICATION_BACKENDS")
    
    return True


def test_student_model_kakao_field():
    """Test that StudentProfile has kakao_id field"""
    print("\n" + "="*50)
    print("Testing Student Model Kakao Integration")
    print("="*50)
    
    # Check if kakao_id field exists
    try:
        field = StudentProfile._meta.get_field('kakao_id')
        print(f"✅ StudentProfile has kakao_id field (type: {field.__class__.__name__})")
        print(f"   - Can be null: {field.null}")
        print(f"   - Can be blank: {field.blank}")
        print(f"   - Is unique: {field.unique}")
    except Exception as e:
        print(f"❌ StudentProfile missing kakao_id field: {e}")
    
    return True


def test_template_integration():
    """Test that templates have Kakao login buttons"""
    print("\n" + "="*50)
    print("Testing Template Integration")
    print("="*50)
    
    client = Client()
    
    # Test login page
    response = client.get(reverse('primepath_student:login'))
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'kakao' in content.lower():
            print("✅ Login page has Kakao integration")
        else:
            print("⚠️  Login page might be missing Kakao button")
    else:
        print(f"❌ Could not load login page (status: {response.status_code})")
    
    # Test register page  
    response = client.get(reverse('primepath_student:register'))
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'kakao' in content.lower():
            print("✅ Register page has Kakao integration")
        else:
            print("⚠️  Register page might be missing Kakao button")
    else:
        print(f"❌ Could not load register page (status: {response.status_code})")
    
    return True


def test_kakao_auth_backend():
    """Test Kakao authentication backend"""
    print("\n" + "="*50)
    print("Testing Kakao Authentication Backend")
    print("="*50)
    
    try:
        from primepath_student.kakao_auth import StudentKakaoOAuth2Backend
        backend = StudentKakaoOAuth2Backend()
        print("✅ StudentKakaoOAuth2Backend can be instantiated")
        
        # Check required methods
        if hasattr(backend, 'authenticate'):
            print("✅ Backend has authenticate method")
        else:
            print("❌ Backend missing authenticate method")
            
        if hasattr(backend, 'get_user'):
            print("✅ Backend has get_user method")
        else:
            print("❌ Backend missing get_user method")
            
        if hasattr(backend, 'get_kakao_user_info'):
            print("✅ Backend has get_kakao_user_info method")
        else:
            print("❌ Backend missing get_kakao_user_info method")
            
    except ImportError as e:
        print(f"❌ Could not import StudentKakaoOAuth2Backend: {e}")
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🔍 STUDENT KAKAO OAUTH INTEGRATION TEST")
    print("="*60)
    
    test_kakao_settings()
    test_kakao_urls()
    test_student_model_kakao_field()
    test_kakao_auth_backend()
    test_template_integration()
    
    print("\n" + "="*60)
    print("✅ KAKAO INTEGRATION TEST COMPLETE")
    print("="*60)
    print("\nNOTE: To fully test Kakao OAuth flow:")
    print("1. Register your app at https://developers.kakao.com")
    print("2. Add redirect URI: http://127.0.0.1:8000/student/kakao/callback/")
    print("3. Update KAKAO_REST_API_KEY in settings if needed")
    print("4. Start the server and try logging in with Kakao")


if __name__ == "__main__":
    main()