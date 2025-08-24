# Kakao Student Login Fix - August 24, 2025

## Problem
Kakao login for students was failing with "Invalid Request (KOE205)" error.

## Root Cause
The redirect URI being sent to Kakao didn't match the registered redirect URI in the Kakao app settings.

## Solution Applied

### 1. Fixed Redirect URI in kakao_views.py
Changed from using `request.build_absolute_uri()` (which could generate different URLs) to hardcoded exact URL that matches Kakao app registration:
```python
callback_url = 'http://127.0.0.1:8000/student/kakao/callback/'
```

### 2. Kakao App Configuration Required
In the Kakao Developers Console (https://developers.kakao.com/):

1. **Web Platform Settings** (웹 플랫폼 설정):
   - Site Domain: `http://127.0.0.1:8000`

2. **Redirect URI** (Redirect URI 설정):
   - Add: `http://127.0.0.1:8000/student/kakao/callback/`
   
3. **Login Settings** (카카오 로그인):
   - Status: Enabled (활성화 설정: ON)
   
4. **Consent Items** (동의항목):
   Enable these permissions:
   - profile_nickname (닉네임)
   - profile_image (프로필 사진)
   - account_email (이메일) - Set as optional
   - phone_number (전화번호) - Set as optional

## API Keys Used
- REST API Key: `c2464d8e5c01f41b75b1657a5c8411ef`
- JavaScript Key: `da17030ca378a5042180c427a60b183a`

## Testing Instructions

1. Start the Django server:
```bash
cd primepath_project
../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
```

2. Navigate to student login page:
   - http://127.0.0.1:8000/student/login/

3. Click "Join/Login with Kakao" button

4. Should redirect to Kakao login page without errors

5. After Kakao authentication, should redirect back to student dashboard

## Files Modified
- `/primepath_project/primepath_student/views/kakao_views.py` - Fixed redirect URI

## Status
✅ Fixed - Redirect URI now matches Kakao app configuration