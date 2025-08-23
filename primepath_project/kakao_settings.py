"""
KakaoTalk OAuth Settings
Add these to your settings_sqlite.py file
"""

# KakaoTalk OAuth Configuration
KAKAO_REST_API_KEY = 'your-rest-api-key-here'  # Get from Kakao Developers Console
KAKAO_JAVASCRIPT_KEY = 'your-javascript-key-here'  # Get from Kakao Developers Console
KAKAO_CLIENT_SECRET = 'your-client-secret-if-needed'  # Optional, depends on app settings

# Add to AUTHENTICATION_BACKENDS
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default Django auth
    'core.kakao_auth.KakaoOAuth2Backend',  # KakaoTalk OAuth
]

# Update LOGIN_URL and related settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Session settings for social login
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True