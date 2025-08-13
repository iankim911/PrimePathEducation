#!/usr/bin/env python
"""Quick check exam list page"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse

# Test exam list
client = Client()
response = client.get(reverse('placement_test:exam_list'))

print(f"Status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Check for table
    has_table = '<table' in content
    has_exam_list_class = 'exam-list' in content
    has_manage = 'Manage' in content
    has_create = 'Create' in content or 'Upload' in content
    has_delete = 'delete' in content.lower()
    
    print(f"Has table tag: {has_table}")
    print(f"Has exam-list class: {has_exam_list_class}")
    print(f"Has Manage button: {has_manage}")
    print(f"Has Create/Upload: {has_create}")
    print(f"Has delete: {has_delete}")
    
    # Check what template is being used
    if hasattr(response, 'templates'):
        print(f"Templates used: {[t.name for t in response.templates if t.name]}")
    
    # Show first 1000 chars to see what's actually there
    print("\nFirst 1000 chars of content:")
    print(content[:1000])
else:
    print(f"Error: Could not load exam list page")