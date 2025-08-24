"""
OAuth Configuration for Social Login
Google and Kakao OAuth settings
"""
import os
from django.conf import settings

# Google OAuth 2.0 Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your-google-client-id.apps.googleusercontent.com')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://127.0.0.1:8000/auth/google/callback/')

GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

GOOGLE_SCOPES = [
    'openid',
    'email',
    'profile',
]

# Kakao OAuth Configuration
KAKAO_CLIENT_ID = os.environ.get('KAKAO_REST_API_KEY', 'your-kakao-rest-api-key')
KAKAO_CLIENT_SECRET = os.environ.get('KAKAO_CLIENT_SECRET', 'your-kakao-client-secret')
KAKAO_REDIRECT_URI = os.environ.get('KAKAO_REDIRECT_URI', 'http://127.0.0.1:8000/auth/kakao/callback/')

KAKAO_AUTH_URL = 'https://kauth.kakao.com/oauth/authorize'
KAKAO_TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
KAKAO_USER_INFO_URL = 'https://kapi.kakao.com/v2/user/me'
KAKAO_LOGOUT_URL = 'https://kapi.kakao.com/v1/user/logout'

KAKAO_SCOPES = [
    'account_email',
    'profile_nickname',
    'profile_image',
    # Removed: 'phone_number', 'age_range', 'gender' - require special approval from Kakao
]

# OAuth Helper Functions
def get_google_auth_url(state=None):
    """Generate Google OAuth authorization URL"""
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(GOOGLE_SCOPES),
        'access_type': 'offline',
        'prompt': 'consent',
    }
    if state:
        params['state'] = state
    
    from urllib.parse import urlencode
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

def get_kakao_auth_url(state=None):
    """Generate Kakao OAuth authorization URL"""
    params = {
        'client_id': KAKAO_CLIENT_ID,
        'redirect_uri': KAKAO_REDIRECT_URI,
        'response_type': 'code',
        'scope': ','.join(KAKAO_SCOPES),
    }
    if state:
        params['state'] = state
    
    from urllib.parse import urlencode
    return f"{KAKAO_AUTH_URL}?{urlencode(params)}"

# Production Settings Reminder
OAUTH_SETTINGS_TEMPLATE = """
# Add these to your .env file or environment variables:

# Google OAuth
GOOGLE_CLIENT_ID=your-actual-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-google-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/google/callback/

# Kakao OAuth
KAKAO_REST_API_KEY=your-actual-kakao-rest-api-key
KAKAO_CLIENT_SECRET=your-actual-kakao-client-secret
KAKAO_REDIRECT_URI=https://yourdomain.com/auth/kakao/callback/

# Security
OAUTH_STATE_SECRET_KEY=generate-a-random-secret-key-for-state-parameter
"""

# OAuth Setup Instructions
SETUP_INSTRUCTIONS = """
Google OAuth Setup:
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs
6. Copy Client ID and Client Secret

Kakao OAuth Setup:
1. Go to https://developers.kakao.com/
2. Create a new application
3. Go to 앱 설정 > 플랫폼 (App Settings > Platform)
4. Add Web platform with your domain
5. Go to 카카오 로그인 (Kakao Login)
6. Enable Kakao Login
7. Set Redirect URI
8. Go to 앱 설정 > 앱 키 (App Settings > App Keys)
9. Copy REST API Key and Client Secret
10. Set required consent items in 동의항목 (Consent Items)
"""