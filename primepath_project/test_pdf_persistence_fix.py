#!/usr/bin/env python
"""
Comprehensive test of PDF persistence fix
Tests the entire flow: Upload -> Rotation -> Preview
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from primepath_routinetest.models import Exam as RoutineExam
from primepath_routinetest.services import ExamService
from placement_test.models import Exam as PlacementExam
from placement_test.services import ExamService as PlacementExamService
import uuid

print("\n" + "="*80)
print("PDF PERSISTENCE FIX - COMPREHENSIVE TEST")
print("="*80)

def test_routinetest_pdf_persistence():
    """Test RoutineTest module PDF persistence"""
    print("\n🧪 TESTING ROUTINETEST MODULE")
    print("-" * 40)
    
    # Create a test PDF file
    test_pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000068 00000 n\n0000000125 00000 n\n0000000229 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n344\n%%EOF'
    
    pdf_file = SimpleUploadedFile(
        f"test_pdf_{uuid.uuid4().hex[:8]}.pdf",
        test_pdf_content,
        content_type='application/pdf'
    )
    
    # Test exam data
    exam_data = {
        'name': f'PDF Persistence Test {uuid.uuid4().hex[:8]}',
        'exam_type': 'quarterly',
        'class_code': 'class_9',
        'total_points': 100,
        'points_per_question': 5,
        'allow_review': True,
        'pdf_rotation': 180  # Test with rotation
    }
    
    try:
        # Create exam using ExamService (the proper way)
        print("📝 Creating exam with PDF and rotation...")
        exam = ExamService.create_exam(
            exam_data=exam_data,
            pdf_file=pdf_file,
            audio_files=[],
            audio_names=[]
        )
        
        print(f"✅ Exam created: {exam.name}")
        print(f"   ID: {exam.id}")
        print(f"   PDF: {exam.pdf_file}")
        print(f"   Rotation: {exam.pdf_rotation}°")
        
        # Verify PDF exists
        if exam.pdf_file:
            pdf_path = Path('media') / str(exam.pdf_file)
            if pdf_path.exists():
                print(f"   ✅ PDF file exists on disk: {pdf_path}")
                print(f"   File size: {pdf_path.stat().st_size} bytes")
            else:
                print(f"   ❌ PDF file NOT found: {pdf_path}")
        else:
            print("   ❌ No PDF file saved!")
        
        # Test preview URL
        preview_url = f"http://127.0.0.1:8000/RoutineTest/exams/{exam.id}/preview/"
        print(f"\n📋 Test this URL in browser:")
        print(f"   {preview_url}")
        
        return exam
        
    except Exception as e:
        print(f"❌ Error creating exam: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_placementtest_pdf_persistence():
    """Test PlacementTest module PDF persistence"""
    print("\n🧪 TESTING PLACEMENTTEST MODULE")
    print("-" * 40)
    
    # Create a test PDF file
    test_pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000068 00000 n\n0000000125 00000 n\n0000000229 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n344\n%%EOF'
    
    pdf_file = SimpleUploadedFile(
        f"test_pdf_{uuid.uuid4().hex[:8]}.pdf",
        test_pdf_content,
        content_type='application/pdf'
    )
    
    # Test exam data
    exam_data = {
        'name': f'Placement PDF Test {uuid.uuid4().hex[:8]}',
        'num_questions': 20,
        'pdf_rotation': 90  # Test with different rotation
    }
    
    try:
        # Create exam using ExamService
        print("📝 Creating placement exam with PDF and rotation...")
        exam = PlacementExamService.create_exam(
            exam_data=exam_data,
            pdf_file=pdf_file,
            audio_files=[],
            audio_names=[]
        )
        
        print(f"✅ Exam created: {exam.name}")
        print(f"   ID: {exam.id}")
        print(f"   PDF: {exam.pdf_file}")
        print(f"   Rotation: {exam.pdf_rotation}°")
        
        # Verify PDF exists
        if exam.pdf_file:
            pdf_path = Path('media') / str(exam.pdf_file)
            if pdf_path.exists():
                print(f"   ✅ PDF file exists on disk: {pdf_path}")
                print(f"   File size: {pdf_path.stat().st_size} bytes")
            else:
                print(f"   ❌ PDF file NOT found: {pdf_path}")
        else:
            print("   ❌ No PDF file saved!")
        
        # Test preview URL
        preview_url = f"http://127.0.0.1:8000/placement/exams/{exam.id}/preview/"
        print(f"\n📋 Test this URL in browser:")
        print(f"   {preview_url}")
        
        return exam
        
    except Exception as e:
        print(f"❌ Error creating exam: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_broken_exams():
    """Check for any remaining broken exams"""
    print("\n🔍 CHECKING FOR BROKEN EXAMS")
    print("-" * 40)
    
    # Check RoutineTest exams
    routine_broken = []
    for exam in RoutineExam.objects.all():
        if exam.pdf_rotation != 0 and not exam.pdf_file:
            routine_broken.append(exam)
    
    # Check PlacementTest exams
    placement_broken = []
    for exam in PlacementExam.objects.all():
        if exam.pdf_rotation != 0 and not exam.pdf_file:
            placement_broken.append(exam)
    
    if routine_broken or placement_broken:
        print(f"⚠️ Found {len(routine_broken)} broken RoutineTest exams")
        for exam in routine_broken[:3]:  # Show first 3
            print(f"   - {exam.name} (rotation: {exam.pdf_rotation}°, no PDF)")
        
        print(f"⚠️ Found {len(placement_broken)} broken PlacementTest exams")
        for exam in placement_broken[:3]:  # Show first 3
            print(f"   - {exam.name} (rotation: {exam.pdf_rotation}°, no PDF)")
    else:
        print("✅ No broken exams found!")

def main():
    """Run all tests"""
    
    # Test RoutineTest module
    routine_exam = test_routinetest_pdf_persistence()
    
    # Test PlacementTest module
    placement_exam = test_placementtest_pdf_persistence()
    
    # Check for broken exams
    check_broken_exams()
    
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    if routine_exam and routine_exam.pdf_file:
        print("✅ RoutineTest: PDF persistence working")
    else:
        print("❌ RoutineTest: PDF persistence FAILED")
    
    if placement_exam and placement_exam.pdf_file:
        print("✅ PlacementTest: PDF persistence working")
    else:
        print("❌ PlacementTest: PDF persistence FAILED")
    
    print("\n📝 NEXT STEPS:")
    print("1. Check the browser console for the test URLs above")
    print("2. Look for [PDF_LOADING_FIX] debug messages")
    print("3. Verify PDFs load or show appropriate fallback")
    print("4. Test rotation controls work properly")
    
    print("\n🔧 If issues persist:")
    print("1. Clear browser cache")
    print("2. Check browser console for errors")
    print("3. Try opening PDF URLs directly")
    print("4. Check media files serving configuration")

if __name__ == "__main__":
    main()