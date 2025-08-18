#!/usr/bin/env python
"""
Test that Exam Assignments Matrix displays exam information correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from primepath_routinetest.models import ExamScheduleMatrix, Exam

print("\n" + "="*70)
print("  EXAM ASSIGNMENTS MATRIX DISPLAY TEST")
print("="*70)

# Check what's in the database
print("\n📊 Current Data:")
cells_with_exams = ExamScheduleMatrix.objects.filter(exams__isnull=False).distinct()
print(f"Matrix cells with exams: {cells_with_exams.count()}")

for cell in cells_with_exams:
    exams = cell.exams.all()
    if exams:
        print(f"\n  {cell.class_code} - {cell.time_period_value}:")
        for exam in exams:
            print(f"    • {exam.name}")
            if exam.curriculum_level:
                print(f"      Curriculum: {exam.curriculum_level}")

# Test the view
client = Client()
client.force_login(User.objects.get(username='admin'))

print("\n📋 Testing Web View:")
response = client.get('/RoutineTest/schedule-matrix/')

if response.status_code == 200:
    print("✅ Page loads successfully")
    
    # Check context data
    context = response.context
    if context:
        monthly_matrix = context.get('monthly_matrix', {})
        
        # Check CLASS_2B for March exam
        if 'CLASS_2B' in monthly_matrix:
            march_cell = monthly_matrix['CLASS_2B']['cells'].get('MAR', {})
            if march_cell.get('exam_count', 0) > 0:
                print("\n✅ CLASS_2B March cell shows exams:")
                for exam in march_cell.get('exams', []):
                    print(f"   - {exam['name']}")
                    print(f"     {exam.get('curriculum', 'N/A')}")
            else:
                print("❌ CLASS_2B March cell shows no exams")
        
        # Check CLASS_3A for Q2 exam
        quarterly_matrix = context.get('quarterly_matrix', {})
        if 'CLASS_3A' in quarterly_matrix:
            q2_cell = quarterly_matrix['CLASS_3A']['cells'].get('Q2', {})
            if q2_cell.get('exam_count', 0) > 0:
                print("\n✅ CLASS_3A Q2 cell shows exams:")
                for exam in q2_cell.get('exams', []):
                    print(f"   - {exam['name']}")
                    print(f"     {exam.get('curriculum', 'N/A')}")
            else:
                print("❌ CLASS_3A Q2 cell shows no exams")
                
    # Check HTML content
    content = response.content.decode('utf-8')
    
    # Look for exam names in the HTML
    if 'March Review Exam' in content:
        print("\n✅ 'March Review Exam' appears in HTML")
    else:
        print("❌ 'March Review Exam' NOT in HTML")
        
    if 'Q2 Assessment' in content:
        print("✅ 'Q2 Assessment' appears in HTML")
    else:
        print("❌ 'Q2 Assessment' NOT in HTML")
        
    # Check for matrix structure
    if 'matrix-table' in content:
        print("✅ Matrix table structure present")
    if 'Monthly/Review Exams' in content:
        print("✅ Monthly tab present")
    if 'Quarterly Exams' in content:
        print("✅ Quarterly tab present")
        
else:
    print(f"❌ Page failed to load: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirected to: {response.url}")

print("\n" + "="*70)
print("If exams are in database but not showing in UI:")
print("1. Clear browser cache")
print("2. Try incognito mode")
print("3. Check browser console for JavaScript errors")
print("4. Navigate to: http://127.0.0.1:8000/RoutineTest/schedule-matrix/")
print("="*70)