#!/usr/bin/env python3
"""
Debug script to investigate PDF loading error for exam ID: 54b00626-6cf6-4fa7-98d8-6203c1397713
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models.exam import Exam
from django.conf import settings

def debug_pdf_loading():
    print("=== PDF Loading Debug Report ===")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print()
    
    # Target exam ID from screenshot
    exam_id = "54b00626-6cf6-4fa7-98d8-6203c1397713"
    
    try:
        # Query the exam
        exam = Exam.objects.get(id=exam_id)
        print(f"✓ Found exam: {exam.name}")
        print(f"  Created: {exam.created_at}")
        print(f"  PDF File Field: {exam.pdf_file}")
        print(f"  PDF Rotation: {getattr(exam, 'pdf_rotation', 'Not set')}")
        print()
        
        # Check PDF file details
        if exam.pdf_file:
            pdf_path = exam.pdf_file.path if hasattr(exam.pdf_file, 'path') else str(exam.pdf_file)
            pdf_url = exam.pdf_file.url if hasattr(exam.pdf_file, 'url') else str(exam.pdf_file)
            
            print(f"PDF File Name: {exam.pdf_file.name}")
            print(f"PDF File Path: {pdf_path}")
            print(f"PDF File URL: {pdf_url}")
            print()
            
            # Check if file exists on disk
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"✓ PDF file exists on disk")
                print(f"  File size: {file_size} bytes ({file_size/1024:.1f} KB)")
                
                # Check file permissions
                file_stat = os.stat(pdf_path)
                print(f"  File permissions: {oct(file_stat.st_mode)[-3:]}")
                
                # Try to read first few bytes to validate PDF
                try:
                    with open(pdf_path, 'rb') as f:
                        header = f.read(5)
                        if header == b'%PDF-':
                            print(f"✓ Valid PDF header found")
                        else:
                            print(f"✗ Invalid PDF header: {header}")
                except Exception as e:
                    print(f"✗ Error reading PDF file: {e}")
                    
            else:
                print(f"✗ PDF file does not exist on disk")
                print(f"  Expected path: {pdf_path}")
                
                # Check if MEDIA_ROOT exists
                if os.path.exists(settings.MEDIA_ROOT):
                    print(f"✓ MEDIA_ROOT exists: {settings.MEDIA_ROOT}")
                    
                    # List contents of media directory
                    media_contents = []
                    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                        rel_path = os.path.relpath(root, settings.MEDIA_ROOT)
                        if rel_path == ".":
                            rel_path = ""
                        for file in files:
                            file_path = os.path.join(rel_path, file) if rel_path else file
                            media_contents.append(file_path)
                    
                    print(f"  Media directory contents ({len(media_contents)} files):")
                    for content in sorted(media_contents)[:10]:  # Show first 10
                        print(f"    {content}")
                    if len(media_contents) > 10:
                        print(f"    ... and {len(media_contents) - 10} more files")
                else:
                    print(f"✗ MEDIA_ROOT does not exist: {settings.MEDIA_ROOT}")
        else:
            print(f"✗ No PDF file associated with this exam")
        
        print()
        
        # Check recent exams with PDFs
        print("=== Recent Exams with PDFs ===")
        recent_exams = Exam.objects.exclude(pdf_file='').order_by('-created_at')[:5]
        
        if recent_exams:
            for i, exam_rec in enumerate(recent_exams, 1):
                print(f"{i}. {exam_rec.name} ({exam_rec.id})")
                if exam_rec.pdf_file:
                    pdf_exists = os.path.exists(exam_rec.pdf_file.path) if hasattr(exam_rec.pdf_file, 'path') else False
                    print(f"   PDF: {exam_rec.pdf_file.name} {'✓' if pdf_exists else '✗'}")
        else:
            print("No recent exams with PDFs found")
            
    except Exam.DoesNotExist:
        print(f"✗ Exam with ID {exam_id} not found in database")
        
        # Show available exams
        print("\nAvailable exams:")
        all_exams = Exam.objects.all().order_by('-created_at')[:10]
        for exam in all_exams:
            print(f"  {exam.id} - {exam.name} - {exam.created_at}")
            
    except Exception as e:
        print(f"✗ Error querying exam: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pdf_loading()