#!/usr/bin/env python
"""Configure Django Site for Google OAuth"""
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.sites.models import Site

# Update or create the site
site, created = Site.objects.get_or_create(id=1)
site.domain = '127.0.0.1:8000'
site.name = 'PrimePath Local'
site.save()

print(f'✅ Site configured successfully!')
print(f'   Domain: {site.domain}')
print(f'   Name: {site.name}')
print(f'   Site ID: {site.id}')
print(f'   Created new: {created}')
print()
print('Next steps:')
print('1. Go to Django Admin: http://127.0.0.1:8000/admin/')
print('2. Navigate to "Social applications" under "SOCIAL ACCOUNTS"')
print('3. Add your Google OAuth credentials')
print('4. See GOOGLE_OAUTH_SETUP_GUIDE.md for detailed instructions')