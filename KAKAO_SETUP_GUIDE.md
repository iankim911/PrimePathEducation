# 🟨 KakaoTalk Login Integration Setup Guide

## 📋 Prerequisites

### 1. Register Your Application on Kakao Developers

1. Go to [Kakao Developers Console](https://developers.kakao.com/)
2. Sign in with your Kakao account
3. Click "내 애플리케이션" (My Applications)
4. Click "애플리케이션 추가하기" (Add Application)
5. Fill in:
   - App Name: PrimePath
   - Company: Your company name
   - Category: Education

### 2. Configure Your Kakao App

#### Get Your Keys:
1. Go to your app's dashboard
2. Navigate to "앱 키" (App Keys)
3. Copy:
   - REST API Key
   - JavaScript Key
   - Admin Key (optional)

#### Set Platform:
1. Go to "플랫폼" (Platform)
2. Click "Web 플랫폼 등록" (Register Web Platform)
3. Add your domain:
   - Development: `http://localhost:8000`
   - Production: `https://yourdomain.com`

#### Configure OAuth:
1. Go to "카카오 로그인" (Kakao Login)
2. Toggle "활성화 설정" (Activation) to ON
3. Set Redirect URI:
   - Add: `http://localhost:8000/auth/kakao/callback/`
   - Add: `https://yourdomain.com/auth/kakao/callback/`

#### Set Permissions:
1. Go to "동의항목" (Consent Items)
2. Enable these scopes:
   - profile_nickname (닉네임) - Required
   - profile_image (프로필 사진) - Optional
   - account_email (이메일) - Optional but recommended

## 🔧 Installation Steps

### 1. Install Required Packages
```bash
cd /Users/ian/Desktop/VIBECODE/PrimePath
../venv/bin/pip install -r requirements_kakao.txt
```

### 2. Update Django Settings
Edit `primepath_project/primepath_project/settings_sqlite.py`:

```python
# Add at the end of the file

# KakaoTalk OAuth Configuration
KAKAO_REST_API_KEY = 'your-rest-api-key-here'  # Replace with your actual key
KAKAO_JAVASCRIPT_KEY = 'your-javascript-key-here'  # Replace with your actual key

# Update AUTHENTICATION_BACKENDS (replace the existing one)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default Django auth
    'core.kakao_auth.KakaoOAuth2Backend',  # KakaoTalk OAuth
]
```

### 3. Update URL Configuration
Edit `primepath_project/primepath_project/urls.py`:

```python
from core.kakao_urls import kakao_urlpatterns

urlpatterns = [
    # ... existing patterns ...
] + kakao_urlpatterns
```

### 4. Update Teacher Model
Edit `primepath_project/core/models.py`:

Add these fields to the Teacher model:
```python
class Teacher(models.Model):
    # ... existing fields ...
    
    # KakaoTalk OAuth fields
    is_kakao_user = models.BooleanField(default=False, help_text='User authenticated via KakaoTalk')
    profile_image_url = models.URLField(max_length=500, blank=True, null=True, help_text='Profile image from KakaoTalk')
    kakao_id = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text='KakaoTalk user ID')
```

### 5. Run Migrations
```bash
cd primepath_project
../venv/bin/python manage.py makemigrations core
../venv/bin/python manage.py migrate core
```

### 6. Update Login Template
Replace your existing login template or add the KakaoTalk button to it.

## 🎨 Customization Options

### Option 1: JavaScript SDK Login (Recommended)
- Faster, no page redirect
- Better user experience
- Uses the template provided in `login_with_kakao.html`

### Option 2: Server-side OAuth Flow
- More secure
- Better for sensitive applications
- Uses redirect flow through Kakao's servers

### Option 3: Both Options
- Provide both buttons and let users choose
- Fallback option if JavaScript is disabled

## 🧪 Testing

### 1. Test Basic OAuth Flow:
```bash
# Start the server
cd primepath_project
../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite

# Visit: http://127.0.0.1:8000/login/
# Click "Login with KakaoTalk"
```

### 2. Test JavaScript SDK:
- Click the yellow KakaoTalk button
- Should open a popup for Kakao login
- After successful login, should redirect to home page

### 3. Verify User Creation:
```python
# Django shell
../venv/bin/python manage.py shell

from django.contrib.auth.models import User
from core.models import Teacher

# Check if Kakao users were created
kakao_users = User.objects.filter(username__startswith='kakao_')
for user in kakao_users:
    print(f"User: {user.username}, Email: {user.email}")
    try:
        teacher = user.teacher_profile
        print(f"  Teacher: {teacher.name}, Kakao User: {teacher.is_kakao_user}")
    except:
        print("  No teacher profile")
```

## 🔐 Security Considerations

1. **Keep Keys Secret**: Never commit your API keys to version control
2. **Use Environment Variables**: 
   ```python
   import os
   KAKAO_REST_API_KEY = os.environ.get('KAKAO_REST_API_KEY')
   ```
3. **HTTPS in Production**: Always use HTTPS for production
4. **Validate Tokens**: Always verify tokens on the backend
5. **Session Security**: Set appropriate session timeouts

## 🐛 Troubleshooting

### "Invalid redirect URI" Error
- Check that your redirect URI in Kakao console matches exactly
- Include trailing slash if needed
- Make sure the domain is registered in Platform settings

### "KOE006" Error (Invalid client)
- Verify your REST API Key is correct
- Check if Kakao Login is activated in console

### User Not Created
- Check Django logs for errors
- Verify database migrations were run
- Check if email is required but not provided by user

### JavaScript SDK Not Working
- Check browser console for errors
- Verify JavaScript key is correct
- Make sure SDK is loaded before calling functions

## 📚 Additional Resources

- [Kakao Login Documentation](https://developers.kakao.com/docs/latest/ko/kakaologin/common)
- [REST API Reference](https://developers.kakao.com/docs/latest/ko/kakaologin/rest-api)
- [JavaScript SDK Guide](https://developers.kakao.com/docs/latest/ko/javascript/reference)

## 🎯 Next Steps

1. **Customize User Profile**: Fetch additional user info from Kakao
2. **Add Logout**: Implement proper logout that revokes Kakao token
3. **Link Existing Accounts**: Allow users to link Kakao to existing accounts
4. **Add Other Social Logins**: Naver, Google, Facebook, etc.

---

**Note**: Remember to update your Kakao app settings when moving to production!