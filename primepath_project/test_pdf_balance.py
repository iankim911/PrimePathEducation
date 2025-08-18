#!/usr/bin/env python
"""
Test to find the optimal balance for PDF preview.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from primepath_routinetest.models import Exam as RoutineExam

print("\n" + "="*80)
print("PDF PREVIEW BALANCE TEST")
print("="*80)

print("\nCURRENT CONFIGURATION:")
print("- Container max-height: 85vh")
print("- Render scale: 2.5")
print("- Height: auto (adapts to content)")

print("\nPOTENTIAL ISSUES:")
print("1. If PDF is still too large at 85vh:")
print("   → Reduce max-height to 70-75vh")
print("   → Keep scale at 2.5 for readability")
print("")
print("2. If text is not readable:")
print("   → Keep scale at 2.5 (or increase)")
print("   → Ensure container has enough height")

print("\nOPTIMAL BALANCE FORMULA:")
print("- Container: max-height between 70-80vh")
print("- Scale: 2.0-2.5 for good readability")
print("- Key: object-fit: contain handles aspect ratio")

print("\nRECOMMENDED TEST VALUES:")
print("Option 1: max-height: 75vh, scale: 2.5 (readable, fits most screens)")
print("Option 2: max-height: 70vh, scale: 2.5 (more compact)")
print("Option 3: max-height: 80vh, scale: 2.0 (larger view, slightly less sharp)")

# Find exam with PDF
exam = None
for e in RoutineExam.objects.all():
    try:
        if e.pdf_file and e.pdf_file.name:
            exam = e
            break
    except ValueError:
        continue

if exam:
    print(f"\n📗 Test URL:")
    print(f"   http://127.0.0.1:8000/RoutineTest/exams/{exam.id}/preview/")
    print("\n📝 Browser Testing:")
    print("   1. Check if entire PDF is visible without scrolling")
    print("   2. Check if text is readable (zoom in browser to verify)")
    print("   3. Look for [BENCHMARK_FIX] logs in console")

print("\n" + "="*80)