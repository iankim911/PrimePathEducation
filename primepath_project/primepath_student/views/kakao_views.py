"""
Kakao OAuth views for student authentication
"""
import json
import requests
import logging
from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def kakao_login(request):
    """Redirect to Kakao OAuth authorization page"""
    
    # Kakao OAuth URL
    kakao_auth_url = "https://kauth.kakao.com/oauth/authorize"
    
    # Build callback URL - use the exact URL that's registered in Kakao app
    # The Kakao app is configured with http://127.0.0.1:8000/student/kakao/callback/
    callback_url = 'http://127.0.0.1:8000/student/kakao/callback/'
    
    # OAuth parameters
    params = {
        'client_id': settings.KAKAO_REST_API_KEY,
        'redirect_uri': callback_url,
        'response_type': 'code',
        'scope': 'profile_nickname,profile_image,account_email'  # Remove phone_number - requires special approval
    }
    
    # Store the next URL in session if provided
    next_url = request.GET.get('next')
    if next_url:
        request.session['kakao_next_url'] = next_url
    
    # Redirect to Kakao
    return redirect(f"{kakao_auth_url}?{urlencode(params)}")


@csrf_exempt
@require_http_methods(["GET"])
def kakao_callback(request):
    """Handle Kakao OAuth callback"""
    
    # Get authorization code
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f"Kakao login failed: {request.GET.get('error_description', error)}")
        return redirect('primepath_student:login')
    
    if not code:
        messages.error(request, "No authorization code received from Kakao")
        return redirect('primepath_student:login')
    
    try:
        # Exchange code for access token
        token_url = "https://kauth.kakao.com/oauth/token"
        # Use the exact callback URL registered in Kakao app
        callback_url = 'http://127.0.0.1:8000/student/kakao/callback/'
        
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.KAKAO_REST_API_KEY,
            'redirect_uri': callback_url,
            'code': code
        }
        
        token_response = requests.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            logger.error(f"Failed to get access token: {token_response.text}")
            messages.error(request, "Failed to authenticate with Kakao")
            return redirect('primepath_student:login')
        
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        
        if not access_token:
            messages.error(request, "No access token received from Kakao")
            return redirect('primepath_student:login')
        
        # Authenticate user with the access token
        user = authenticate(request, kakao_access_token=access_token)
        
        if user:
            # Login successful
            login(request, user, backend='primepath_student.kakao_auth.StudentKakaoOAuth2Backend')
            messages.success(request, f"Welcome, {user.first_name}!")
            
            # Redirect to next URL or dashboard
            next_url = request.session.pop('kakao_next_url', None)
            return redirect(next_url or 'primepath_student:dashboard')
        else:
            messages.error(request, "Failed to authenticate with Kakao account")
            return redirect('primepath_student:login')
            
    except Exception as e:
        logger.error(f"Kakao callback error: {e}")
        messages.error(request, "An error occurred during Kakao login")
        return redirect('primepath_student:login')


@require_http_methods(["POST"])
def kakao_link_account(request):
    """Link existing student account with Kakao"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    if not hasattr(request.user, 'primepath_student_profile'):
        return JsonResponse({'error': 'Not a student account'}, status=403)
    
    access_token = request.POST.get('access_token')
    if not access_token:
        return JsonResponse({'error': 'No access token provided'}, status=400)
    
    try:
        # Get Kakao user info
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        response = requests.get(
            'https://kapi.kakao.com/v2/user/me',
            headers=headers
        )
        
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to get Kakao user info'}, status=400)
        
        user_info = response.json()
        kakao_id = str(user_info.get('id'))
        
        # Check if this Kakao ID is already linked
        from primepath_student.models import StudentProfile
        if StudentProfile.objects.filter(kakao_id=kakao_id).exclude(user=request.user).exists():
            return JsonResponse({'error': 'This Kakao account is already linked to another student'}, status=400)
        
        # Link the account
        student_profile = request.user.primepath_student_profile
        student_profile.kakao_id = kakao_id
        student_profile.save()
        
        messages.success(request, "Kakao account linked successfully!")
        return JsonResponse({'success': True})
        
    except Exception as e:
        logger.error(f"Failed to link Kakao account: {e}")
        return JsonResponse({'error': 'Failed to link account'}, status=500)


@require_http_methods(["POST"])
def kakao_unlink_account(request):
    """Unlink Kakao from student account"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    if not hasattr(request.user, 'primepath_student_profile'):
        return JsonResponse({'error': 'Not a student account'}, status=403)
    
    try:
        student_profile = request.user.primepath_student_profile
        student_profile.kakao_id = None
        student_profile.save()
        
        messages.success(request, "Kakao account unlinked successfully")
        return JsonResponse({'success': True})
        
    except Exception as e:
        logger.error(f"Failed to unlink Kakao account: {e}")
        return JsonResponse({'error': 'Failed to unlink account'}, status=500)