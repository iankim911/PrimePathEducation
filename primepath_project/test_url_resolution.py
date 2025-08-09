#!/usr/bin/env python

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.urls import reverse, NoReverseMatch

print("Testing URL resolution...")

try:
    url = reverse('core:get_placement_rules')
    print(f"✅ core:get_placement_rules resolves to: {url}")
except NoReverseMatch as e:
    print(f"❌ core:get_placement_rules failed: {e}")

try:
    url = reverse('core:save_placement_rules')
    print(f"✅ core:save_placement_rules resolves to: {url}")
except NoReverseMatch as e:
    print(f"❌ core:save_placement_rules failed: {e}")

# Also test existing URLs
try:
    url = reverse('core:create_placement_rule')
    print(f"✅ core:create_placement_rule resolves to: {url}")
except NoReverseMatch as e:
    print(f"❌ core:create_placement_rule failed: {e}")

try:
    url = reverse('core:placement_rules')
    print(f"✅ core:placement_rules resolves to: {url}")
except NoReverseMatch as e:
    print(f"❌ core:placement_rules failed: {e}")