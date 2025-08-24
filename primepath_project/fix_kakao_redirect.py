#!/usr/bin/env python
"""
Fix Kakao OAuth redirect URI issue
The redirect URI must match EXACTLY what's registered in Kakao app
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings

print("=" * 60)
print("KAKAO REDIRECT URI TROUBLESHOOTING")
print("=" * 60)

print("\n1. Current Configuration:")
print(f"   REST API Key: {settings.KAKAO_REST_API_KEY[:10]}...")

print("\n2. Registered Redirect URIs in Kakao App:")
print("   According to your setup, you registered:")
print("   - http://localhost:3000/auth/kakao/callback")
print("   - http://localhost:5173/auth/kakao/callback")  
print("   - http://localhost:8080/auth/kakao/callback")
print("   - http://localhost:8000/auth/kakao/callback (need to add this)")

print("\n3. What Django is trying to use:")
print("   - http://127.0.0.1:8000/auth/kakao/callback/")

print("\n❌ PROBLEM IDENTIFIED:")
print("   Django is using '127.0.0.1' but Kakao app has 'localhost'")
print("   Also Django adds trailing slash but Kakao doesn't expect it")

print("\n✅ SOLUTIONS:")
print("\nOption 1: Add to Kakao App (RECOMMENDED):")
print("   Go to Kakao Developers Console and add:")
print("   - http://127.0.0.1:8000/auth/kakao/callback")
print("   - http://127.0.0.1:8000/auth/kakao/callback/")

print("\nOption 2: Force Django to use localhost:")
print("   Access the app via http://localhost:8000 instead of 127.0.0.1")

print("\n" + "=" * 60)
print("IMMEDIATE FIX - Update your Kakao app:")
print("=" * 60)
print("\n1. Go to: https://developers.kakao.com/")
print("2. Select your app (ID: 1300582)")
print("3. Go to '카카오 로그인' → 'Redirect URI'")
print("4. Add these URIs:")
print("   - http://127.0.0.1:8000/auth/kakao/callback")
print("   - http://127.0.0.1:8000/auth/kakao/callback/")
print("   - http://localhost:8000/auth/kakao/callback")
print("   - http://localhost:8000/auth/kakao/callback/")
print("\n5. Save changes")
print("\nThen try logging in again!")
print("=" * 60)