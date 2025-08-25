#!/usr/bin/env python
"""
Debug Kakao Login Issues
Tests both Student and Teacher Kakao login flows
"""
import os
import sys
import django
import requests
from urllib.parse import urlencode, parse_qs, urlparse

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.conf import settings
from django.test import Client
from django.contrib.auth.models import User

def test_kakao_configuration():
    """Test Kakao configuration and settings"""
    print("=" * 60)
    print("🔍 KAKAO CONFIGURATION CHECK")
    print("=" * 60)
    
    # Check settings
    try:
        kakao_rest_key = settings.KAKAO_REST_API_KEY
        kakao_js_key = settings.KAKAO_JAVASCRIPT_KEY
        print(f"✅ KAKAO_REST_API_KEY: {kakao_rest_key[:10]}...")
        print(f"✅ KAKAO_JAVASCRIPT_KEY: {kakao_js_key[:10]}...")
    except AttributeError as e:
        print(f"❌ Missing Kakao settings: {e}")
        return False
    
    return True

def test_redirect_uris():
    """Test redirect URI configurations"""
    print("\n" + "=" * 60)
    print("🔍 REDIRECT URI VERIFICATION")
    print("=" * 60)
    
    # Expected redirect URIs based on code
    expected_uris = {
        'student': 'http://127.0.0.1:8000/student/kakao/callback/',
        'teacher': 'http://127.0.0.1:8000/auth/kakao/callback/'
    }
    
    print("📋 Expected Redirect URIs:")
    for app, uri in expected_uris.items():
        print(f"   {app.capitalize()}: {uri}")
    
    print("\n🔗 These URIs should be registered in Kakao Console:")
    print("   - http://127.0.0.1:8000/student/kakao/callback/")
    print("   - http://127.0.0.1:8000/auth/kakao/callback/")
    
    return expected_uris

def test_kakao_auth_urls():
    """Test Kakao authorization URL generation"""
    print("\n" + "=" * 60)
    print("🔍 KAKAO AUTH URL GENERATION TEST")
    print("=" * 60)
    
    client_id = settings.KAKAO_REST_API_KEY
    
    # Student auth URL
    student_params = {
        'client_id': client_id,
        'redirect_uri': 'http://127.0.0.1:8000/student/kakao/callback/',
        'response_type': 'code',
        'scope': 'profile_nickname,profile_image,account_email'
    }
    student_auth_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(student_params)}"
    
    # Teacher auth URL
    teacher_params = {
        'client_id': client_id,
        'redirect_uri': 'http://127.0.0.1:8000/auth/kakao/callback/',
        'response_type': 'code'
    }
    teacher_auth_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(teacher_params)}"
    
    print("🎓 Student Auth URL:")
    print(f"   {student_auth_url}")
    print(f"\n👨‍🏫 Teacher Auth URL:")
    print(f"   {teacher_auth_url}")
    
    return {
        'student': student_auth_url,
        'teacher': teacher_auth_url
    }

def test_url_routing():
    """Test URL routing for Kakao endpoints"""
    print("\n" + "=" * 60)
    print("🔍 URL ROUTING TEST")
    print("=" * 60)
    
    client = Client()
    
    # Test student Kakao URLs
    print("🎓 Student Kakao URLs:")
    test_urls = [
        '/student/kakao/login/',
        '/student/kakao/callback/',
        '/student/login/',
    ]
    
    for url in test_urls:
        try:
            response = client.get(url, follow=False)
            status = response.status_code
            if status == 302:
                location = response.get('Location', 'No location header')
                print(f"   {url:<30} → {status} (Redirect to: {location})")
            else:
                print(f"   {url:<30} → {status}")
        except Exception as e:
            print(f"   {url:<30} → ERROR: {e}")
    
    # Test teacher Kakao URLs
    print("\n👨‍🏫 Teacher Kakao URLs:")
    teacher_test_urls = [
        '/auth/kakao/login/',
        '/auth/kakao/callback/',
        '/login/',
    ]
    
    for url in teacher_test_urls:
        try:
            response = client.get(url, follow=False)
            status = response.status_code
            if status == 302:
                location = response.get('Location', 'No location header')
                print(f"   {url:<30} → {status} (Redirect to: {location})")
            else:
                print(f"   {url:<30} → {status}")
        except Exception as e:
            print(f"   {url:<30} → ERROR: {e}")

def test_kakao_api_connectivity():
    """Test connectivity to Kakao API endpoints"""
    print("\n" + "=" * 60)
    print("🔍 KAKAO API CONNECTIVITY TEST")
    print("=" * 60)
    
    # Test basic connectivity to Kakao OAuth endpoints
    test_endpoints = [
        'https://kauth.kakao.com/oauth/authorize',
        'https://kauth.kakao.com/oauth/token',
        'https://kapi.kakao.com/v2/user/me'
    ]
    
    for endpoint in test_endpoints:
        try:
            # Just test connectivity with HEAD request
            response = requests.head(endpoint, timeout=5)
            print(f"   {endpoint:<40} → {response.status_code}")
        except requests.RequestException as e:
            print(f"   {endpoint:<40} → ERROR: {e}")

def main():
    """Main debug function"""
    print("🚨 KAKAO LOGIN DEBUG TOOL")
    print("This will help diagnose Kakao login issues for both Student and Teacher sessions")
    print()
    
    # Step 1: Check configuration
    if not test_kakao_configuration():
        print("❌ Configuration issues found. Please fix settings first.")
        return
    
    # Step 2: Check redirect URIs
    expected_uris = test_redirect_uris()
    
    # Step 3: Test auth URL generation
    auth_urls = test_kakao_auth_urls()
    
    # Step 4: Test URL routing
    test_url_routing()
    
    # Step 5: Test API connectivity
    test_kakao_api_connectivity()
    
    # Summary and recommendations
    print("\n" + "=" * 60)
    print("📋 SUMMARY & RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n✅ Configuration looks correct based on code analysis")
    print("\n🔧 NEXT STEPS TO DEBUG:")
    print("1. Check Kakao Developer Console:")
    print("   - Ensure app is activated (상태: ON)")
    print("   - Verify redirect URIs exactly match:")
    print("     • http://127.0.0.1:8000/student/kakao/callback/")
    print("     • http://127.0.0.1:8000/auth/kakao/callback/")
    print("   - Check if any domain restrictions are set")
    print()
    print("2. Test in browser:")
    print("   - Open incognito/private window")
    print("   - Try student login: http://127.0.0.1:8000/student/login/")
    print("   - Try teacher login: http://127.0.0.1:8000/login/")
    print("   - Click Kakao buttons and note exact error messages")
    print()
    print("3. Check browser console:")
    print("   - Open Developer Tools (F12)")
    print("   - Look for JavaScript errors")
    print("   - Check Network tab for failed requests")
    print()
    print("4. Manual test URLs:")
    for app, url in auth_urls.items():
        print(f"   {app.capitalize()}: {url}")
    
    print("\n⚠️  COMMON ISSUES:")
    print("• Kakao app not activated in console")
    print("• Redirect URI mismatch (check trailing slashes)")
    print("• Browser cache issues (try incognito)")
    print("• REST API key changed in Kakao console")

if __name__ == "__main__":
    main()