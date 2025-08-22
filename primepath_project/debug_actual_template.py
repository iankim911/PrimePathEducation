#!/usr/bin/env python
"""
Find out which template is ACTUALLY being served
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Test with logged in user
client = Client()
teacher1 = User.objects.get(username='teacher1')
teacher1.set_password('teacher123')
teacher1.save()

login = client.login(username='teacher1', password='teacher123')
print(f"Logged in: {login}")

# Make request with filter ON
response = client.get('/RoutineTest/exams/?assigned_only=true')
print(f"Status: {response.status_code}")

# Check what template was used
if hasattr(response, 'template_name'):
    print(f"Template used: {response.template_name}")
elif hasattr(response, 'templates'):
    for template in response.templates:
        print(f"Template used: {template.name}")

# Check the actual HTML content for our fixes
content = response.content.decode('utf-8')

# Look for our template fixes
if 'CRITICAL FIX: Never show VIEW ONLY badge when filter is active' in content:
    print("✅ Our template fix comment is in the HTML")
else:
    print("❌ Our template fix comment is NOT in the HTML")

if 'NUCLEAR_SAFETY' in content:
    print("✅ Our JavaScript safety net is in the HTML") 
else:
    print("❌ Our JavaScript safety net is NOT in the HTML")

# Check if filter checkbox exists
if 'assignedOnlyFilter' in content:
    print("✅ Filter checkbox exists in HTML")
else:
    print("❌ Filter checkbox does NOT exist in HTML")

# Look for VIEW ONLY badges in the raw HTML
import re
badge_matches = re.findall(r'<span[^>]*class="badge"[^>]*>([^<]*)</span>', content)
view_only_badges = [badge for badge in badge_matches if 'VIEW' in badge.upper()]

print(f"Total badges in HTML: {len(badge_matches)}")
print(f"VIEW ONLY badges in HTML: {len(view_only_badges)}")
if view_only_badges:
    print("❌ HTML CONTAINS VIEW ONLY BADGES:")
    for badge in view_only_badges:
        print(f"   - {badge.strip()}")
else:
    print("✅ No VIEW ONLY badges found in HTML")

print("\nFirst 500 chars of response:")
print(content[:500])