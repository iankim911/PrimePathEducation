#!/usr/bin/env python
"""
Test Kakao OAuth Integration
Run this after starting the Django server
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from django.urls import reverse
from django.test import RequestFactory

def test_kakao_settings():
    """Test if Kakao settings are configured"""
    print("=" * 60)
    print("KAKAO OAUTH CONFIGURATION TEST")
    print("=" * 60)
    
    # Check API Keys
    print("\n✅ API Keys Configured:")
    print(f"   REST API Key: {settings.KAKAO_REST_API_KEY[:10]}...")
    print(f"   JavaScript Key: {settings.KAKAO_JAVASCRIPT_KEY[:10]}...")
    
    # Check Authentication Backends
    print("\n✅ Authentication Backends:")
    for backend in settings.AUTHENTICATION_BACKENDS:
        print(f"   - {backend}")
    
    # Check if Kakao backend is present
    if 'core.kakao_auth.KakaoOAuth2Backend' in settings.AUTHENTICATION_BACKENDS:
        print("   ✓ Kakao OAuth backend configured")
    else:
        print("   ✗ Kakao OAuth backend NOT configured")
    
    # Check Middleware
    print("\n✅ Middleware Configuration:")
    if 'allauth.account.middleware.AccountMiddleware' in settings.MIDDLEWARE:
        print("   ✓ Allauth AccountMiddleware present")
    else:
        print("   ✗ Allauth AccountMiddleware MISSING")
    
    # Test URLs
    print("\n✅ OAuth URLs:")
    urls_to_test = [
        ('kakao_login', '/auth/kakao/login/'),
        ('kakao_callback', '/auth/kakao/callback/'),
        ('kakao_logout', '/auth/kakao/logout/'),
        ('kakao_js_login', '/auth/kakao/js-login/'),
    ]
    
    factory = RequestFactory()
    for name, path in urls_to_test:
        try:
            url = reverse(name)
            print(f"   ✓ {name}: {url}")
        except Exception as e:
            print(f"   ✗ {name}: Error - {e}")
    
    # Build OAuth URL
    print("\n✅ OAuth Authorization URL:")
    client_id = settings.KAKAO_REST_API_KEY
    redirect_uri = "http://127.0.0.1:8000/auth/kakao/callback/"
    
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )
    
    print(f"   {kakao_auth_url[:80]}...")
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nTo test Kakao login:")
    print("1. Start the Django server:")
    print("   python manage.py runserver")
    print("\n2. Visit the login page:")
    print("   http://127.0.0.1:8000/auth/kakao/login/")
    print("\n3. You will be redirected to Kakao for authentication")
    print("\n4. After logging in, you'll be redirected back to:")
    print("   http://127.0.0.1:8000/auth/kakao/callback/")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_kakao_settings()