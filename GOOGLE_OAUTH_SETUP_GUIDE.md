# Google OAuth2 Setup Guide for PrimePath

## Overview
This guide explains how to set up Google OAuth2 authentication for the PrimePath project.

## Prerequisites
- Django-allauth is already installed and configured
- Access to Google Cloud Console
- PrimePath project running locally

## Step 1: Google Cloud Console Setup

### 1.1 Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "PrimePath")
4. Click "Create"

### 1.2 Enable Google+ API
1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and press "Enable"

### 1.3 Create OAuth2 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen first:
   - Choose "External" user type
   - Fill in the required fields:
     - App name: PrimePath
     - User support email: your-email@domain.com
     - Developer contact: your-email@domain.com
   - Add scopes: email, profile
   - Save and continue

### 1.4 Create OAuth Client ID
1. Application type: "Web application"
2. Name: "PrimePath Local Development"
3. Authorized JavaScript origins:
   ```
   http://127.0.0.1:8000
   http://localhost:8000
   ```
4. Authorized redirect URIs:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   http://localhost:8000/accounts/google/login/callback/
   ```
5. Click "Create"
6. Save the Client ID and Client Secret

## Step 2: Django Configuration

### 2.1 Create Django Site
Run the Django shell:
```bash
cd primepath_project
../venv/bin/python manage.py shell --settings=primepath_project.settings_sqlite
```

Then execute:
```python
from django.contrib.sites.models import Site

# Update or create the site
site, created = Site.objects.get_or_create(id=1)
site.domain = '127.0.0.1:8000'
site.name = 'PrimePath Local'
site.save()

print(f"Site configured: {site.domain}")
```

### 2.2 Add Google Provider in Django Admin
1. Start the server:
   ```bash
   ../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
   ```

2. Go to Django Admin: http://127.0.0.1:8000/admin/

3. Navigate to "Social applications" under "SOCIAL ACCOUNTS"

4. Click "Add social application"

5. Fill in the form:
   - Provider: Google
   - Name: Google OAuth2
   - Client id: [Your Google Client ID from Step 1.4]
   - Secret key: [Your Google Client Secret from Step 1.4]
   - Sites: Select "127.0.0.1:8000"

6. Click "Save"

## Step 3: Environment Variables (Production)

For production, add these to your environment:
```bash
# .env file
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

## Step 4: Test the Integration

1. Go to the login page: http://127.0.0.1:8000/RoutineTest/login/

2. Click "Sign in with Google"

3. You should be redirected to Google's login page

4. After authentication, you'll be redirected back to PrimePath

## Troubleshooting

### Common Issues

#### 1. "Redirect URI mismatch" error
- Ensure the redirect URI in Google Console exactly matches Django's
- Use `127.0.0.1:8000` not `localhost:8000` or vice versa

#### 2. "Site matching query does not exist"
- Run the Django shell commands in Step 2.1 to create the site

#### 3. "Social application does not exist"
- Add the Google provider in Django Admin (Step 2.2)

#### 4. User profile not created
- Check `core/adapters.py` for proper UserProfile creation
- Verify the SocialAccountAdapter is working

### Debug Mode
To see detailed OAuth flow logs:
```python
# In settings_sqlite.py
LOGGING['loggers']['allauth'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
}
```

## Security Notes

1. **Never commit credentials** to version control
2. **Use environment variables** for production
3. **Restrict redirect URIs** to your actual domains
4. **Enable 2FA** on your Google Cloud account
5. **Regularly rotate** client secrets

## Additional Features

### Customizing User Data
The adapter in `core/adapters.py` handles:
- Creating UserProfile for new users
- Storing OAuth tokens
- Mapping Google user data to Django user fields

### Restricting to Organization
To restrict login to specific email domains:
```python
# In core/adapters.py
def pre_social_login(self, request, sociallogin):
    email = sociallogin.account.extra_data.get('email', '')
    if not email.endswith('@yourcompany.com'):
        raise ImmediateHttpResponse(
            render(request, 'error.html', {'message': 'Invalid email domain'})
        )
```

## Support
For issues, check:
1. Django server logs
2. Browser console for JavaScript errors
3. Google Cloud Console logs
4. Django Admin social account records