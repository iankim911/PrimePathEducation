"""
KakaoTalk OAuth Views
Handles KakaoTalk login flow
"""
import requests
import logging
import json
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .kakao_auth import KakaoOAuth2Backend

logger = logging.getLogger(__name__)


def kakao_login(request):
    """
    Redirect to Kakao authorization page
    """
    client_id = settings.KAKAO_REST_API_KEY
    
    # Force localhost redirect URI to match what's registered in Kakao
    # This avoids issues with 127.0.0.1 vs localhost mismatch
    if request.get_host().startswith('127.0.0.1'):
        redirect_uri = 'http://127.0.0.1:8000/auth/kakao/callback/'
    elif request.get_host().startswith('localhost'):
        redirect_uri = 'http://localhost:8000/auth/kakao/callback/'
    else:
        redirect_uri = request.build_absolute_uri('/auth/kakao/callback/')
        # Remove double slashes if present
        if redirect_uri.endswith('//'):
            redirect_uri = redirect_uri[:-1]
    
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )
    
    logger.info(f"[KAKAO_LOGIN] Redirecting to: {kakao_auth_url}")
    logger.info(f"[KAKAO_LOGIN] Using redirect_uri: {redirect_uri}")
    
    return redirect(kakao_auth_url)


def kakao_callback(request):
    """
    Handle callback from Kakao after authorization
    """
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f'KakaoTalk login failed: {error}')
        return redirect('/login/')
    
    if not code:
        messages.error(request, 'No authorization code received')
        return redirect('/login/')
    
    try:
        # Exchange code for access token
        access_token = get_kakao_access_token(request, code)
        
        if not access_token:
            messages.error(request, 'Failed to get access token')
            return redirect('/login/')
        
        # Authenticate user with access token
        backend = KakaoOAuth2Backend()
        user = backend.authenticate(request, kakao_access_token=access_token)
        
        if user:
            # Login user
            login(request, user, backend='core.kakao_auth.KakaoOAuth2Backend')
            messages.success(request, f'Welcome {user.first_name or user.username}!')
            
            # Store access token in session for future API calls
            request.session['kakao_access_token'] = access_token
            
            # Redirect to main page or next URL
            next_url = request.session.get('next_url', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Authentication failed')
            return redirect('/login/')  # Use absolute path instead of named URL
            
    except Exception as e:
        logger.error(f"Kakao callback error: {e}")
        messages.error(request, 'An error occurred during login')
        return redirect('/login/')


def get_kakao_access_token(request, code):
    """
    Exchange authorization code for access token
    """
    token_url = 'https://kauth.kakao.com/oauth/token'
    
    # Use same redirect URI logic as login to ensure consistency
    if request.get_host().startswith('127.0.0.1'):
        redirect_uri = 'http://127.0.0.1:8000/auth/kakao/callback/'
    elif request.get_host().startswith('localhost'):
        redirect_uri = 'http://localhost:8000/auth/kakao/callback/'
    else:
        redirect_uri = request.build_absolute_uri('/auth/kakao/callback/')
        # Remove trailing slash if present
        if redirect_uri.endswith('//'):
            redirect_uri = redirect_uri[:-1]
    
    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.KAKAO_REST_API_KEY,
        'redirect_uri': redirect_uri,
        'code': code,
    }
    
    # Add client secret if configured (not needed for REST API)
    if hasattr(settings, 'KAKAO_CLIENT_SECRET'):
        data['client_secret'] = settings.KAKAO_CLIENT_SECRET
    
    # Log the request details for debugging
    logger.info(f"[KAKAO_TOKEN] Requesting token with redirect_uri: {redirect_uri}")
    logger.info(f"[KAKAO_TOKEN] Client ID: {settings.KAKAO_REST_API_KEY[:10]}...")
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        logger.info(f"[KAKAO_TOKEN] Successfully got access token")
        return access_token
    else:
        logger.error(f"[KAKAO_TOKEN] Failed to get access token: Status {response.status_code}")
        logger.error(f"[KAKAO_TOKEN] Response: {response.text}")
        logger.error(f"[KAKAO_TOKEN] Request data: redirect_uri={redirect_uri}, code={code[:10]}...")
        return None


def kakao_logout(request):
    """
    Logout from Kakao (optional - revoke token)
    """
    access_token = request.session.get('kakao_access_token')
    
    if access_token:
        # Optionally revoke token at Kakao
        logout_url = 'https://kapi.kakao.com/v1/user/logout'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.post(logout_url, headers=headers)
            if response.status_code == 200:
                logger.info(f"Kakao logout successful for user {request.user}")
        except Exception as e:
            logger.error(f"Kakao logout error: {e}")
    
    # Clear session
    request.session.flush()
    return redirect('/login/')


@csrf_exempt
def kakao_javascript_login(request):
    """
    Handle login from Kakao JavaScript SDK
    Used when implementing login with JavaScript
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        access_token = data.get('access_token')
        
        if not access_token:
            return JsonResponse({'error': 'No access token provided'}, status=400)
        
        # Authenticate user
        backend = KakaoOAuth2Backend()
        user = backend.authenticate(request, kakao_access_token=access_token)
        
        if user:
            login(request, user, backend='core.kakao_auth.KakaoOAuth2Backend')
            request.session['kakao_access_token'] = access_token
            
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.first_name
                }
            })
        else:
            return JsonResponse({'error': 'Authentication failed'}, status=401)
            
    except Exception as e:
        logger.error(f"JavaScript login error: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)