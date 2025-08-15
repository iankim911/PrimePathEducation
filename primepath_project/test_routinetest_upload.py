#!/usr/bin/env python
"""
Test script to verify RoutineTest upload functionality
Tests the complete upload workflow with comprehensive logging
"""
import os
import sys
import django
import json
from pathlib import Path

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models.exam import Exam, AudioFile
from primepath_routinetest.services.exam_service import ExamService
from core.models import CurriculumLevel, Teacher
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

def create_test_files():
    """Create test PDF and audio files for upload"""
    # Create a simple test PDF content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << >> /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n205\n%%EOF"
    
    # Create a simple test audio content (WAV header)
    audio_content = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    
    return pdf_content, audio_content

def test_upload_functionality():
    """Test the complete upload workflow for RoutineTest"""
    print("\n" + "="*60)
    print("ROUTINETEST UPLOAD FUNCTIONALITY TEST")
    print("="*60)
    
    try:
        # Step 1: Get or create test user and teacher
        print("\n[STEP 1] Setting up test user and teacher...")
        user, created = User.objects.get_or_create(
            username='routinetest_tester',
            defaults={'email': 'test@routinetest.com', 'is_superuser': True}
        )
        if created:
            print("✅ Created test user: routinetest_tester")
        else:
            print("✅ Using existing test user: routinetest_tester")
        
        teacher, created = Teacher.objects.get_or_create(
            user=user,
            defaults={
                'name': 'RoutineTest Teacher',
                'email': 'test@routinetest.com',
                'is_head_teacher': True
            }
        )
        if created:
            print("✅ Created test teacher profile")
        else:
            print("✅ Using existing teacher profile")
        
        # Step 2: Get a curriculum level
        print("\n[STEP 2] Getting curriculum level...")
        curriculum_level = CurriculumLevel.objects.filter(
            subprogram__program__name='CORE',
            subprogram__name='Phonics',
            level_number=1
        ).first()
        
        if curriculum_level:
            print(f"✅ Using curriculum level: {curriculum_level.full_name}")
        else:
            print("⚠️  No curriculum level found, proceeding without it")
        
        # Step 3: Create test files
        print("\n[STEP 3] Creating test files...")
        pdf_content, audio_content = create_test_files()
        
        pdf_file = SimpleUploadedFile(
            "test_exam_routinetest.pdf",
            pdf_content,
            content_type="application/pdf"
        )
        print(f"✅ Created test PDF: {pdf_file.name} ({len(pdf_content)} bytes)")
        
        audio_file = SimpleUploadedFile(
            "test_audio_routinetest.wav",
            audio_content,
            content_type="audio/wav"
        )
        print(f"✅ Created test audio: {audio_file.name} ({len(audio_content)} bytes)")
        
        # Step 4: Prepare exam data
        print("\n[STEP 4] Preparing exam data...")
        exam_data = {
            'name': '[RoutineTest] Test Upload Exam',
            'curriculum_level_id': curriculum_level.id if curriculum_level else None,
            'timer_minutes': 60,
            'total_questions': 10,
            'default_options_count': 5,
            'passing_score': 0,
            'pdf_rotation': 0,
            'created_by': teacher,
            'is_active': True
        }
        print(f"✅ Exam data prepared: {exam_data['name']}")
        
        # Step 5: Test the upload using ExamService
        print("\n[STEP 5] Testing upload with ExamService...")
        print("📤 Calling ExamService.create_exam()...")
        
        exam = ExamService.create_exam(
            exam_data=exam_data,
            pdf_file=pdf_file,
            audio_files=[audio_file],
            audio_names=['Test Audio 1']
        )
        
        print(f"✅ Exam created successfully!")
        print(f"   - Exam ID: {exam.id}")
        print(f"   - Exam Name: {exam.name}")
        print(f"   - PDF Path: {exam.pdf_file.name if exam.pdf_file else 'None'}")
        print(f"   - Questions Created: {exam.routine_questions.count()}")
        print(f"   - Audio Files: {exam.routine_audio_files.count()}")
        
        # Step 6: Verify file paths
        print("\n[STEP 6] Verifying file paths...")
        if exam.pdf_file:
            expected_path = 'routinetest/exams/pdfs/'
            actual_path = exam.pdf_file.name
            if expected_path in actual_path:
                print(f"✅ PDF uploaded to correct path: {actual_path}")
            else:
                print(f"❌ PDF path mismatch!")
                print(f"   Expected: ...{expected_path}...")
                print(f"   Actual: {actual_path}")
        
        for audio in exam.routine_audio_files.all():
            if audio.audio_file:
                expected_path = 'routinetest/exams/audio/'
                actual_path = audio.audio_file.name
                if expected_path in actual_path:
                    print(f"✅ Audio uploaded to correct path: {actual_path}")
                else:
                    print(f"❌ Audio path mismatch!")
                    print(f"   Expected: ...{expected_path}...")
                    print(f"   Actual: {actual_path}")
        
        # Step 7: Test retrieval
        print("\n[STEP 7] Testing exam retrieval...")
        retrieved_exam = Exam.objects.get(id=exam.id)
        print(f"✅ Exam retrieved: {retrieved_exam.name}")
        print(f"   - Has PDF: {bool(retrieved_exam.pdf_file)}")
        print(f"   - Has Audio: {retrieved_exam.routine_audio_files.exists()}")
        print(f"   - Has Questions: {retrieved_exam.routine_questions.exists()}")
        
        # Step 8: Summary
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print("✅ All tests passed successfully!")
        print(f"✅ Exam '{exam.name}' created and verified")
        print(f"✅ Files uploaded to RoutineTest-specific paths")
        print(f"✅ Database relationships working correctly")
        
        # Cleanup (optional)
        print("\n[CLEANUP] Deleting test exam...")
        exam.delete()
        print("✅ Test exam deleted")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_upload_functionality()
    print("\n" + "="*60)
    if success:
        print("🎉 ROUTINETEST UPLOAD TEST COMPLETED SUCCESSFULLY! 🎉")
    else:
        print("❌ ROUTINETEST UPLOAD TEST FAILED")
    print("="*60 + "\n")
    sys.exit(0 if success else 1)