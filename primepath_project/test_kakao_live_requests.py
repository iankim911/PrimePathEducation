#!/usr/bin/env python
"""
Test Kakao OAuth requests directly to identify the exact issue
"""
import requests
import sys
import os
import django
from urllib.parse import urlencode, parse_qs, urlparse

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.conf import settings

def test_kakao_oauth_direct():
    """Test direct requests to Kakao OAuth endpoints"""
    print("=" * 60)
    print("🔍 DIRECT KAKAO OAUTH TEST")
    print("=" * 60)
    
    client_id = settings.KAKAO_REST_API_KEY
    
    # Test student OAuth URL (with scope)
    student_params = {
        'client_id': client_id,
        'redirect_uri': 'http://127.0.0.1:8000/student/kakao/callback/',
        'response_type': 'code',
        'scope': 'profile_nickname,profile_image,account_email'  # No phone_number
    }
    student_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(student_params)}"
    
    # Test teacher OAuth URL (no scope)
    teacher_params = {
        'client_id': client_id,
        'redirect_uri': 'http://127.0.0.1:8000/auth/kakao/callback/',
        'response_type': 'code'
    }
    teacher_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(teacher_params)}"
    
    print("🎓 Testing Student OAuth URL:")
    print(f"   URL: {student_url}")
    
    try:
        response = requests.get(student_url, allow_redirects=False, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Student OAuth URL accessible")
        elif response.status_code in [302, 301]:
            redirect_url = response.headers.get('Location', 'No location')
            print(f"   🔄 Redirected to: {redirect_url}")
        else:
            print(f"   ❌ Error: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print("\n👨‍🏫 Testing Teacher OAuth URL:")
    print(f"   URL: {teacher_url}")
    
    try:
        response = requests.get(teacher_url, allow_redirects=False, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Teacher OAuth URL accessible")
        elif response.status_code in [302, 301]:
            redirect_url = response.headers.get('Location', 'No location')
            print(f"   🔄 Redirected to: {redirect_url}")
        else:
            print(f"   ❌ Error: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def test_kakao_app_info():
    """Test Kakao app information using REST API key"""
    print("\n" + "=" * 60)
    print("🔍 KAKAO APP INFO TEST")
    print("=" * 60)
    
    # Test app info endpoint (if available)
    try:
        headers = {
            'Authorization': f'KakaoAK {settings.KAKAO_REST_API_KEY}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        # This endpoint might not exist, but let's try
        response = requests.get('https://kapi.kakao.com/v1/api/talk/profile', headers=headers, timeout=5)
        print(f"   API Test Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   API test failed (expected): {e}")

def parse_error_url():
    """Parse the error URL from browser to understand the issue"""
    print("\n" + "=" * 60)
    print("🔍 KNOWN ERROR URL ANALYSIS")
    print("=" * 60)
    
    # The URL from the browser tab that shows "Error Page"
    error_url = "https://kauth.kakao.com/oauth/authorize?client_id=c2464d8e5c01f41b75b1657a5c8411ef&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fstudent%2Fkakao%2Fcallback%2F&response_type=code&scope=profile_nickname%2Cprofile_image%2Caccount_email%2Cphone_number"
    
    parsed = urlparse(error_url)
    params = parse_qs(parsed.query)
    
    print("📋 URL Parameters:")
    for key, value in params.items():
        print(f"   {key}: {value[0] if value else 'N/A'}")
    
    # Key differences to check
    print("\n🔍 Analysis:")
    client_id = params.get('client_id', [''])[0]
    redirect_uri = params.get('redirect_uri', [''])[0]
    scope = params.get('scope', [''])[0]
    
    print(f"   Client ID: {client_id}")
    print(f"   Expected:  {settings.KAKAO_REST_API_KEY}")
    print(f"   Match: {'✅' if client_id == settings.KAKAO_REST_API_KEY else '❌'}")
    
    print(f"   Redirect URI: {redirect_uri}")
    print(f"   Expected:     http://127.0.0.1:8000/student/kakao/callback/")
    print(f"   Match: {'✅' if redirect_uri == 'http://127.0.0.1:8000/student/kakao/callback/' else '❌'}")
    
    print(f"   Scope: {scope}")
    if 'phone_number' in scope:
        print("   ⚠️  WARNING: phone_number scope requires special approval from Kakao!")
        print("   💡 SOLUTION: Remove phone_number from scope")

def check_redirect_uri_registration():
    """Check if redirect URIs might be causing issues"""
    print("\n" + "=" * 60)
    print("📋 REDIRECT URI CHECKLIST")
    print("=" * 60)
    
    expected_uris = [
        'http://127.0.0.1:8000/student/kakao/callback/',
        'http://127.0.0.1:8000/auth/kakao/callback/'
    ]
    
    print("✅ These URIs MUST be registered in Kakao Console:")
    for i, uri in enumerate(expected_uris, 1):
        print(f"   {i}. {uri}")
    
    print("\n⚠️  Common Registration Mistakes:")
    print("   • Using https instead of http")
    print("   • Missing or extra trailing slash")
    print("   • Using localhost instead of 127.0.0.1")
    print("   • Wrong port number")
    
    print("\n🔧 How to fix in Kakao Console:")
    print("   1. Go to https://developers.kakao.com/console")
    print("   2. Select your app")
    print("   3. Go to 제품 설정 > 카카오 로그인")
    print("   4. In Redirect URI section, add EXACTLY:")
    for uri in expected_uris:
        print(f"      {uri}")
    print("   5. Save and activate the app (상태: ON)")

def main():
    print("🚨 KAKAO OAUTH LIVE TEST")
    print("Testing direct requests to identify the exact issue")
    print()
    
    # Parse the error URL first to understand what's wrong
    parse_error_url()
    
    # Test direct OAuth requests
    test_kakao_oauth_direct()
    
    # Test app info
    test_kakao_app_info()
    
    # Provide checklist
    check_redirect_uri_registration()
    
    print("\n" + "=" * 60)
    print("🎯 MOST LIKELY ISSUE")
    print("=" * 60)
    print("Based on the error URL analysis:")
    print("1. ⚠️  The scope includes 'phone_number' which requires special approval")
    print("2. 🔧 Remove phone_number from scope in student views")
    print("3. 🔗 Verify redirect URIs are registered exactly as shown above")
    print("4. ✅ Ensure Kakao app is activated (상태: ON)")

if __name__ == "__main__":
    main()