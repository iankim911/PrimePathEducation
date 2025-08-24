#!/usr/bin/env python
"""
Quick login script to bypass Kakao OAuth issues and test Copy Exam modal
Run this to get a direct authenticated link to the exam list page
"""

import os
import sys
import django

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
import webbrowser

def create_authenticated_session():
    """Create an authenticated session for admin user"""
    try:
        # Get admin user
        user = User.objects.get(username='admin')
        
        # Create new session
        session = SessionStore()
        session['_auth_user_id'] = str(user.id)
        session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
        session['_auth_user_hash'] = user.get_session_auth_hash()
        session.create()
        
        print("✅ Authenticated session created successfully!")
        print(f"Session key: {session.session_key}")
        
        # Create URL with session
        base_url = "http://127.0.0.1:8000/RoutineTest/exams/"
        
        print("\n" + "="*60)
        print("COPY EXAM MODAL TEST ACCESS")
        print("="*60)
        print("\n📋 Option 1: Open this URL and use browser console:")
        print(f"   URL: {base_url}")
        print(f"\n   Then paste in console (F12):")
        print(f"   document.cookie = 'sessionid={session.session_key}; path=/'")
        print(f"   location.reload()")
        
        print("\n📋 Option 2: Use this direct link (may need to refresh):")
        print(f"   {base_url}?sessionid={session.session_key}")
        
        print("\n" + "="*60)
        print("After login, you can:")
        print("1. View the exam list")
        print("2. Click 'Copy' button on any exam")
        print("3. Test the Copy Exam modal functionality")
        print("="*60)
        
        # Try to open browser automatically
        try:
            webbrowser.open(base_url)
            print("\n🌐 Browser opened automatically. Use the console command above to authenticate.")
        except:
            print("\n⚠️  Could not open browser automatically. Please open the URL manually.")
            
        return session.session_key
        
    except User.DoesNotExist:
        print("❌ Admin user not found. Please create an admin user first:")
        print("   python manage.py createsuperuser")
        return None
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return None

if __name__ == "__main__":
    print("\n🚀 Starting Quick Login for Copy Exam Modal Testing...\n")
    session_key = create_authenticated_session()
    
    if session_key:
        print("\n✅ Ready to test Copy Exam modal!")
        print("💡 Tip: Keep this terminal open to see the session key if needed.")