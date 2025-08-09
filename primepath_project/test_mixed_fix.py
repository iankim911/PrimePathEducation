#!/usr/bin/env python
"""
Test the MIXED MCQ options count fix
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from placement_test.models import Question
from placement_test.templatetags.grade_tags import get_mixed_components

print('='*80)
print('MIXED MCQ OPTIONS COUNT FIX TEST')
print(f'Timestamp: {datetime.now()}')
print('='*80)

client = Client()

# Test 1: Update MIXED question options_count via API
print('\n1. API UPDATE TEST')
print('-'*50)

mixed_q = Question.objects.filter(
    question_type='MIXED',
    correct_answer__contains='Multiple Choice'
).first()

if mixed_q:
    print(f'Testing Q{mixed_q.id} (#{mixed_q.question_number})')
    print(f'Original options_count: {mixed_q.options_count}')
    
    # Test API update
    response = client.post(
        f'/api/placement/questions/{mixed_q.id}/update/',
        {
            'options_count': 8,
            'correct_answer': mixed_q.correct_answer,
            'points': mixed_q.points
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f'✅ API update successful')
            
            # Refresh from database
            mixed_q.refresh_from_db()
            print(f'New options_count: {mixed_q.options_count}')
            
            if mixed_q.options_count == 8:
                print(f'✅ Options_count correctly saved to database')
            else:
                print(f'❌ Options_count not saved: got {mixed_q.options_count}, expected 8')
        else:
            print(f'❌ API returned error: {data.get("error")}')
    else:
        print(f'❌ API failed with status {response.status_code}')

# Test 2: Check template filter uses new options_count
print('\n2. TEMPLATE FILTER TEST')
print('-'*50)

if mixed_q:
    components = get_mixed_components(mixed_q)
    mcq_comps = [c for c in components if c.get('type') == 'mcq']
    
    print(f'Found {len(mcq_comps)} MCQ components')
    
    for i, comp in enumerate(mcq_comps):
        options = comp.get('options', [])
        expected = list("ABCDEFGHIJ"[:mixed_q.options_count])
        
        print(f'\nMCQ Component {i+1}:')
        print(f'  Options: {options}')
        print(f'  Expected: {expected}')
        
        if options == expected:
            print(f'  ✅ CORRECT: MCQ uses question.options_count ({mixed_q.options_count})')
        else:
            print(f'  ❌ WRONG: Expected {len(expected)} options, got {len(options)}')

print('\n' + '='*80)
print('FIX VERIFICATION COMPLETE')
print('='*80)