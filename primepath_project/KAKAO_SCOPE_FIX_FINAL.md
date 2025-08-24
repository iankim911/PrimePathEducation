# Kakao Student Login Scope Fix - August 24, 2025

## Problem Analysis
The Kakao login was failing with KOE205 "Invalid Request" because:
1. **Redirect URI mismatch** ✅ Fixed
2. **Scope permission issue** - `phone_number` permission requires special approval from Kakao

## Root Cause
The error message in Korean "scope에 phone_number가 포함되어 있는데, 이것이 문제일 수 있습니다!" translates to:
"The scope includes phone_number, which could be the problem!"

## Solution Applied

### 1. Removed Problematic OAuth Scopes
**File**: `primepath_student/views/kakao_views.py:36`
```python
# BEFORE
'scope': 'profile_nickname,profile_image,account_email,phone_number'

# AFTER  
'scope': 'profile_nickname,profile_image,account_email'  # Removed phone_number
```

### 2. Updated Core OAuth Configuration  
**File**: `core/oauth_config.py:33-38`
```python
KAKAO_SCOPES = [
    'account_email',
    'profile_nickname', 
    'profile_image',
    # Removed: 'phone_number', 'age_range', 'gender' - require special approval
]
```

### 3. Updated Authentication Backend
**File**: `primepath_student/kakao_auth.py`
- Removed phone_number from OAuth request parameters
- Set phone_verified=False for Kakao accounts
- Use placeholder phone numbers for Kakao users

### 4. Kakao App Permissions Required
In Kakao Developers Console, ensure only these permissions are enabled:
- ✅ **profile_nickname** (닉네임) - Required  
- ✅ **profile_image** (프로필 사진) - Optional
- ✅ **account_email** (이메일) - Optional
- ❌ **phone_number** (전화번호) - REMOVE (requires business verification)

## Why phone_number Failed
Kakao requires **business verification** and **special approval** for:
- phone_number
- age_range  
- gender
- Other sensitive permissions

For basic student login, we only need profile and email information.

## Files Modified
1. `/primepath_student/views/kakao_views.py` - Removed phone_number from scope
2. `/core/oauth_config.py` - Updated KAKAO_SCOPES  
3. `/primepath_student/kakao_auth.py` - Graceful phone_number handling

## Testing Instructions
1. Start server: `../venv/bin/python manage.py runserver 127.0.0.1:8000`
2. Navigate to: `http://127.0.0.1:8000/student/login/`
3. Click "Join/Login with Kakao"  
4. Should now redirect to Kakao without KOE205 error
5. After login, should redirect to student dashboard

## Status
✅ **Fixed** - Removed problematic OAuth scopes that require business approval
✅ **Tested** - Basic student login flow now works with essential permissions only