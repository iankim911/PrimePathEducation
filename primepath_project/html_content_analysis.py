#!/usr/bin/env python
"""
Analyze the actual HTML content to understand the structure and find where VIEW ONLY badges appear
"""
import os
import sys
import django

# Add the project path to sys.path
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import re

def analyze_html_content():
    """Analyze the actual HTML to understand what's being returned"""
    
    print("="*80)
    print("HTML CONTENT ANALYSIS - UNDERSTANDING THE STRUCTURE")
    print("="*80)
    
    # Get teacher1 user and client
    user = User.objects.get(username='teacher1')
    client = Client()
    client.force_login(user)
    
    print(f"✅ Analyzing HTML content for user: {user.username}")
    print()
    
    # Test both filter states
    responses = {
        'Filter OFF': client.get('/RoutineTest/exams/', follow=True),
        'Filter ON': client.get('/RoutineTest/exams/?assigned_only=true', follow=True)
    }
    
    for state, response in responses.items():
        print(f"📄 {state.upper()} ANALYSIS")
        print("-" * 50)
        
        html = response.content.decode('utf-8')
        print(f"Response Status: {response.status_code}")
        print(f"Content Length: {len(html):,} characters")
        
        # Count different badge types with various approaches
        print("\nBadge Counts (Simple Text Search):")
        view_only_count = html.count('VIEW ONLY')
        owner_count = html.count('>OWNER<')
        full_access_count = html.count('FULL ACCESS')
        edit_count = html.count('>EDIT<')
        admin_count = html.count('>ADMIN<')
        
        print(f"  - VIEW ONLY: {view_only_count}")
        print(f"  - OWNER: {owner_count}")
        print(f"  - FULL ACCESS: {full_access_count}")
        print(f"  - EDIT: {edit_count}")
        print(f"  - ADMIN: {admin_count}")
        
        # Look for exam cards
        print("\nExam Card Analysis:")
        
        # Try different patterns for exam cards
        patterns = [
            r'<div class="exam-card"',
            r'class="exam-card"',
            r'exam-title',
            r'access-badge'
        ]
        
        for pattern in patterns:
            count = len(re.findall(pattern, html, re.IGNORECASE))
            print(f"  - Pattern '{pattern}': {count} matches")
        
        # Look for specific exam names we know exist
        print("\nSpecific Exam Search:")
        test_exams = [
            "Admin's Test Exam for Toggle Testing",
            "Test Ownership Exam",
            "PINNACLE Success",
            "ASCENT Drive",
            "EDGE Spark"
        ]
        
        for exam_name in test_exams:
            if exam_name in html:
                print(f"  ✅ Found: {exam_name}")
                
                # Find context around this exam name
                start = html.find(exam_name)
                if start != -1:
                    context_start = max(0, start - 200)
                    context_end = min(len(html), start + len(exam_name) + 200)
                    context = html[context_start:context_end]
                    
                    # Look for badge in context
                    if 'VIEW ONLY' in context:
                        print(f"     🔍 Has VIEW ONLY badge nearby")
                    elif 'OWNER' in context:
                        print(f"     👑 Has OWNER badge nearby")
                    elif 'FULL ACCESS' in context:
                        print(f"     ✅ Has FULL ACCESS badge nearby")
                    elif 'EDIT' in context:
                        print(f"     ✏️ Has EDIT badge nearby")
            else:
                print(f"  ❌ Not found: {exam_name}")
        
        # Check if page has the expected structure
        print("\nPage Structure Check:")
        structural_elements = [
            'exam-library-container',
            'hierarchical_exams',
            'filter-toggle',
            'assignedOnlyFilter',
            'show_assigned_only'
        ]
        
        for element in structural_elements:
            if element in html:
                print(f"  ✅ Found: {element}")
            else:
                print(f"  ❌ Missing: {element}")
        
        # Check for error messages or empty states
        print("\nError/State Detection:")
        error_patterns = [
            'No exams found',
            'empty-state',
            'debug',
            'error',
            'exception'
        ]
        
        for pattern in error_patterns:
            if pattern.lower() in html.lower():
                print(f"  ⚠️ Found: {pattern}")
                
                # Find context
                start = html.lower().find(pattern.lower())
                if start != -1:
                    context_start = max(0, start - 100)
                    context_end = min(len(html), start + len(pattern) + 100)
                    context = html[context_start:context_end]
                    print(f"     Context: {context[:150]}...")
        
        # Look for JavaScript debug output
        print("\nJavaScript Debug Check:")
        js_patterns = [
            'FILTER_DEBUG',
            'PAGE_LOAD_DEBUG',
            'console.log',
            'badge distribution'
        ]
        
        for pattern in js_patterns:
            count = html.lower().count(pattern.lower())
            if count > 0:
                print(f"  - {pattern}: {count} occurrences")
        
        print()
        
        # If we found some exams but our regex didn't work, let's try to understand why
        if view_only_count > 0:
            print("🔍 DETAILED VIEW ONLY ANALYSIS:")
            print("-" * 40)
            
            # Find all positions where "VIEW ONLY" appears
            positions = []
            start = 0
            while True:
                pos = html.find('VIEW ONLY', start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            print(f"Found VIEW ONLY at {len(positions)} positions:")
            for i, pos in enumerate(positions[:5]):  # Show first 5
                context_start = max(0, pos - 150)
                context_end = min(len(html), pos + 150)
                context = html[context_start:context_end]
                print(f"\n  Position {i+1} (char {pos}):")
                print(f"    Context: ...{context}...")
                
                # Look for exam name in this context
                exam_name_pattern = r'<[^>]*exam-title[^>]*>([^<]+)<'
                match = re.search(exam_name_pattern, context, re.IGNORECASE)
                if match:
                    print(f"    Exam name: {match.group(1).strip()}")
        
        print("\n" + "="*60 + "\n")
        
        # Save HTML to file for manual inspection if needed
        filename = f"/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/html_debug_{state.replace(' ', '_').lower()}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"💾 HTML saved to: {filename}")
        print()

if __name__ == '__main__':
    analyze_html_content()