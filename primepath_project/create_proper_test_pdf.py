#!/usr/bin/env python
"""
Create a proper test PDF with actual content for the problematic exam
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.files.base import ContentFile
from primepath_routinetest.models import Exam as RoutineExam

print("\n" + "="*80)
print("CREATING PROPER TEST PDF FOR EXAM")
print("="*80)

# Valid PDF content (minimal but complete)
VALID_PDF = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 55 >>
stream
BT
/F1 24 Tf
100 700 Td
(Test PDF Document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000068 00000 n 
0000000125 00000 n 
0000000229 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
344
%%EOF"""

# Find the problematic exam
exam_id = '54b00626-6cf6-4fa7-98d8-6203c1397713'

try:
    exam = RoutineExam.objects.get(id=exam_id)
    print(f"\n✅ Found exam: {exam.name}")
    print(f"   Current PDF: {exam.pdf_file}")
    print(f"   Rotation: {exam.pdf_rotation}°")
    
    # Check current PDF
    if exam.pdf_file:
        old_path = Path('media') / str(exam.pdf_file)
        if old_path.exists():
            old_size = old_path.stat().st_size
            print(f"   Current file size: {old_size} bytes")
            
            # Read current content
            with open(old_path, 'rb') as f:
                current_content = f.read()
                print(f"   Current content preview: {current_content[:50]}...")
    
    # Replace with proper PDF
    print("\n📝 Replacing with proper PDF content...")
    
    # Save new PDF content
    pdf_content = ContentFile(VALID_PDF)
    exam.pdf_file.save(f'fixed_test_{str(exam.id)[:8]}.pdf', pdf_content, save=True)
    
    # Verify the new file
    new_path = Path('media') / str(exam.pdf_file)
    if new_path.exists():
        new_size = new_path.stat().st_size
        print(f"✅ New PDF saved: {exam.pdf_file}")
        print(f"   New file size: {new_size} bytes")
        
        # Verify it's a valid PDF
        with open(new_path, 'rb') as f:
            header = f.read(5)
            if header == b'%PDF-':
                print("   ✅ Valid PDF header confirmed")
            else:
                print(f"   ⚠️ Unexpected header: {header}")
    
    print(f"\n📋 Test URL: http://127.0.0.1:8000/RoutineTest/exams/{exam.id}/preview/")
    print("\n✨ The PDF should now load correctly!")
    
except RoutineExam.DoesNotExist:
    print(f"❌ Exam not found: {exam_id}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)