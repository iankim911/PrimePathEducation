#!/usr/bin/env python
"""
Test the existing exam with PDF loading issue
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from primepath_routinetest.models import Exam as RoutineExam
from django.template.loader import get_template
from django.template import Context
import json

print("\n" + "="*80)
print("TESTING EXISTING EXAM PDF LOADING")
print("="*80)

# Test the specific exam
exam_id = '54b00626-6cf6-4fa7-98d8-6203c1397713'

try:
    exam = RoutineExam.objects.get(id=exam_id)
    print(f"\n✅ Found exam: {exam.name}")
    print(f"   ID: {exam.id}")
    print(f"   PDF File: {exam.pdf_file}")
    print(f"   PDF URL: {exam.pdf_file.url if exam.pdf_file else 'None'}")
    print(f"   PDF Rotation: {exam.pdf_rotation}°")
    
    # Check if PDF file actually exists
    if exam.pdf_file:
        pdf_path = os.path.join('media', str(exam.pdf_file))
        if os.path.exists(pdf_path):
            size = os.path.getsize(pdf_path)
            print(f"   ✅ File exists: {pdf_path} ({size} bytes)")
            
            # Read PDF header
            with open(pdf_path, 'rb') as f:
                header = f.read(10)
                print(f"   PDF Header: {header}")
                if header.startswith(b'%PDF'):
                    print("   ✅ Valid PDF file")
                else:
                    print("   ❌ Invalid PDF file!")
        else:
            print(f"   ❌ File NOT found: {pdf_path}")
    
    # Test URL
    preview_url = f"http://127.0.0.1:8000/RoutineTest/exams/{exam.id}/preview/"
    print(f"\n📋 Preview URL: {preview_url}")
    print("\n🧪 TESTING STEPS:")
    print("1. Open Chrome browser")
    print("2. Navigate to: http://127.0.0.1:8000/login/")
    print("3. Login with admin/admin")
    print(f"4. Navigate to: {preview_url}")
    print("5. Open Developer Tools (F12)")
    print("6. Check Console tab for:")
    print("   - [PDF_LOADING_FIX] messages")
    print("   - Any JavaScript errors")
    print("   - PDF loading status")
    
    print("\n🔍 EXPECTED CONSOLE OUTPUT:")
    print("   [PDF_LOADING_FIX] Enhanced PDF initialization")
    print("   ✅ PDF URL from Django: /media/routinetest/exams/pdfs/test_x2rS0a0.pdf")
    print("   🧪 Testing PDF URL accessibility...")
    print("   🌐 PDF HEAD request status: 200")
    print("   ✅ PDF is accessible, loading with PDF.js...")
    
    print("\n⚠️ IF PDF FAILS TO LOAD:")
    print("   - Should show fallback with 'Open in New Tab' button")
    print("   - Should show iframe with native browser PDF viewer")
    print("   - Check for CORS or media serving issues")
    
except RoutineExam.DoesNotExist:
    print(f"❌ Exam not found: {exam_id}")

print("\n" + "="*80)