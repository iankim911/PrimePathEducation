#!/usr/bin/env python
"""Quick check session detail page"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from placement_test.models import StudentSession

# Get a session
session = StudentSession.objects.first()
if not session:
    print("No sessions found")
    exit(1)

print(f"Testing session: {session.id}")
print(f"Student: {session.student_name}")

# Test session detail
client = Client()
response = client.get(reverse('PlacementTest:session_detail', kwargs={'session_id': session.id}))

print(f"Status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Check for required elements
    has_student_name = session.student_name in content
    has_exam_name = session.exam.name in content if session.exam else False
    has_score = 'score' in content.lower()
    has_status = 'status' in content.lower() or 'progress' in content.lower()
    
    print(f"Has student name: {has_student_name}")
    print(f"Has exam name: {has_exam_name}")
    print(f"Has score: {has_score}")
    print(f"Has status/progress: {has_status}")
    
    # Check what template is being used
    if hasattr(response, 'templates'):
        print(f"Templates used: {[t.name for t in response.templates if t.name]}")
    
    # Look for score more specifically
    print("\nSearching for score-related text:")
    import re
    score_patterns = [
        r'[Ss]core',
        r'[Pp]oints',
        r'[Gg]rade',
        r'[Rr]esult',
        r'[Pp]ercentage'
    ]
    
    for pattern in score_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"  Found '{pattern}': {len(matches)} times")
    
    # Show a snippet around score if found
    if 'score' in content.lower():
        idx = content.lower().index('score')
        snippet = content[max(0, idx-50):min(len(content), idx+100)]
        print(f"\nContext around 'score':\n...{snippet}...")
else:
    print(f"Error: Could not load session detail page")