#!/usr/bin/env python
"""
Critical Investigation: PDF Rotation Persistence Failure
Investigating why PDF files uploaded in one module don't appear in the other module
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models import Exam as RoutineTestExam
from placement_test.models import Exam as PlacementTestExam
import uuid

def main():
    print("=" * 80)
    print("CRITICAL INVESTIGATION: PDF ROTATION PERSISTENCE FAILURE")
    print("=" * 80)
    
    # The problematic exam ID from the issue report
    exam_id = '62d88d79-820b-4a17-8e05-fb0da1413e9d'
    print(f"\nInvestigating exam ID: {exam_id}")
    
    print("\n" + "-" * 50)
    print("1. CHECKING ROUTINETEST MODULE")
    print("-" * 50)
    
    # Check RoutineTest module
    try:
        rt_exam = RoutineTestExam.objects.get(id=exam_id)
        print(f"✅ FOUND in RoutineTest module")
        print(f"   Name: {rt_exam.name}")
        print(f"   PDF file field: {rt_exam.pdf_file}")
        print(f"   PDF file path: {rt_exam.pdf_file.name if rt_exam.pdf_file else 'None'}")
        print(f"   PDF file exists on disk: {rt_exam.pdf_file.name and os.path.exists(os.path.join('media', rt_exam.pdf_file.name))}")
        print(f"   PDF rotation: {rt_exam.pdf_rotation}")
        print(f"   Created by: {rt_exam.created_by}")
        print(f"   Upload path: routinetest/exams/pdfs/")
        
        if rt_exam.pdf_file:
            full_path = os.path.join('media', rt_exam.pdf_file.name)
            print(f"   Full disk path: {full_path}")
            if os.path.exists(full_path):
                print(f"   File size: {os.path.getsize(full_path)} bytes")
            else:
                print(f"   ❌ FILE MISSING FROM DISK!")
        
        rt_found = True
    except RoutineTestExam.DoesNotExist:
        print("❌ NOT FOUND in RoutineTest module")
        rt_found = False
    
    print("\n" + "-" * 50)
    print("2. CHECKING PLACEMENT TEST MODULE")
    print("-" * 50)
    
    # Check PlacementTest module  
    try:
        pt_exam = PlacementTestExam.objects.get(id=exam_id)
        print(f"✅ FOUND in PlacementTest module")
        print(f"   Name: {pt_exam.name}")
        print(f"   PDF file field: {pt_exam.pdf_file}")
        print(f"   PDF file path: {pt_exam.pdf_file.name if pt_exam.pdf_file else 'None'}")
        print(f"   PDF file exists on disk: {pt_exam.pdf_file.name and os.path.exists(os.path.join('media', pt_exam.pdf_file.name))}")
        print(f"   PDF rotation: {pt_exam.pdf_rotation}")
        print(f"   Created by: {pt_exam.created_by}")
        print(f"   Upload path: exams/pdfs/")
        
        if pt_exam.pdf_file:
            full_path = os.path.join('media', pt_exam.pdf_file.name)
            print(f"   Full disk path: {full_path}")
            if os.path.exists(full_path):
                print(f"   File size: {os.path.getsize(full_path)} bytes")
            else:
                print(f"   ❌ FILE MISSING FROM DISK!")
        
        pt_found = True
    except PlacementTestExam.DoesNotExist:
        print("❌ NOT FOUND in PlacementTest module")
        pt_found = False
    
    print("\n" + "=" * 80)
    print("3. ROOT CAUSE ANALYSIS")
    print("=" * 80)
    
    if rt_found and pt_found:
        print("🔍 ISSUE: Exam exists in BOTH modules with same ID - UUID collision!")
        print("   This should not happen - UUIDs should be unique across modules")
    elif rt_found and not pt_found:
        print("🔍 ISSUE: Exam exists ONLY in RoutineTest module")
        print("   User uploaded via RoutineTest but trying to access via RoutineTest preview")
        print("   This is normal behavior - each module has separate tables")
    elif pt_found and not rt_found:
        print("🔍 ISSUE: Exam exists ONLY in PlacementTest module")
        print("   User uploaded via PlacementTest but trying to access via RoutineTest")
        print("   URL /RoutineTest/exams/.../preview/ should look in RoutineTest module only")
    else:
        print("🔍 ISSUE: Exam NOT FOUND in either module")
        print("   The exam may have been deleted or the ID is incorrect")
    
    # Additional analysis - check recent uploads in both modules
    print("\n" + "-" * 50)
    print("4. RECENT UPLOADS ANALYSIS")
    print("-" * 50)
    
    print("\nRoutineTest Recent Uploads:")
    rt_recent = RoutineTestExam.objects.all().order_by('-created_at')[:5]
    if rt_recent:
        for exam in rt_recent:
            has_pdf = "✅" if exam.pdf_file else "❌"
            print(f"   {has_pdf} {exam.id} - {exam.name} - {exam.created_at}")
    else:
        print("   No exams found in RoutineTest")
    
    print("\nPlacementTest Recent Uploads:")
    pt_recent = PlacementTestExam.objects.all().order_by('-created_at')[:5]
    if pt_recent:
        for exam in pt_recent:
            has_pdf = "✅" if exam.pdf_file else "❌"
            print(f"   {has_pdf} {exam.id} - {exam.name} - {exam.created_at}")
    else:
        print("   No exams found in PlacementTest")
    
    print("\n" + "=" * 80)
    print("5. DIRECTORY STRUCTURE ANALYSIS")
    print("=" * 80)
    
    # Check media directories
    media_dirs = [
        'media/exams/pdfs',  # PlacementTest
        'media/routinetest/exams/pdfs',  # RoutineTest
        'media/routine_exams',  # Legacy?
    ]
    
    for dir_path in media_dirs:
        print(f"\nDirectory: {dir_path}")
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"   Files: {len(files)}")
            if files:
                print(f"   Recent files: {files[-3:] if len(files) > 3 else files}")
        else:
            print(f"   ❌ Directory does not exist")
    
    print("\n" + "=" * 80)
    print("6. RECOMMENDED SOLUTION")
    print("=" * 80)
    
    if rt_found and not pt_found:
        print("✅ SOLUTION: The exam exists in RoutineTest module and the URL is correct.")
        print("   The issue is likely in the template or view logic.")
        print("   Check if exam.pdf_file is being checked properly in the template.")
        
        # Get the actual exam to check its state
        rt_exam = RoutineTestExam.objects.get(id=exam_id)
        if not rt_exam.pdf_file:
            print(f"   ❌ FOUND THE ISSUE: exam.pdf_file is empty/None!")
            print(f"   PDF was not properly saved during upload process")
        elif not os.path.exists(os.path.join('media', rt_exam.pdf_file.name)):
            print(f"   ❌ FOUND THE ISSUE: PDF file missing from disk!")
            print(f"   File was deleted or never saved: {rt_exam.pdf_file.name}")
        else:
            print(f"   ✅ PDF file exists: {rt_exam.pdf_file.name}")
            print(f"   Check template logic for PDF display")
            
    elif pt_found and not rt_found:
        print("❌ SOLUTION: User uploaded exam in PlacementTest but accessing via RoutineTest URL")
        print("   Change URL from /RoutineTest/exams/.../preview/ to /PlacementTest/exams/.../preview/")
    else:
        print("❌ SOLUTION: Exam not found - check if it was deleted or ID is wrong")
    
    print("\n" + "=" * 80)
    print("INVESTIGATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()