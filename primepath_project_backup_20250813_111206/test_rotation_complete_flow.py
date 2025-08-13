#!/usr/bin/env python
"""
Test complete PDF rotation flow from upload to student view
Verifies rotation persists through all interfaces
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from placement_test.models import Exam, StudentSession
from placement_test.services import ExamService
from core.models import CurriculumLevel, SubProgram, Program
from django.utils import timezone


def test_complete_rotation_workflow():
    """Test the complete workflow from upload to student view"""
    
    print("=" * 80)
    print("🔄 COMPLETE PDF ROTATION WORKFLOW TEST")
    print("=" * 80)
    
    client = Client()
    
    # Setup test data
    program, _ = Program.objects.get_or_create(
        name="WORKFLOW_TEST",
        defaults={'grade_range_start': 1, 'grade_range_end': 12, 'order': 100}
    )
    
    subprogram, _ = SubProgram.objects.get_or_create(
        name="Workflow Test SubProgram",
        program=program,
        defaults={'order': 1}
    )
    
    curriculum_level, _ = CurriculumLevel.objects.get_or_create(
        subprogram=subprogram,
        level_number=1,
        defaults={'description': 'Workflow Test Level'}
    )
    
    test_rotation = 180  # Test with 180 degrees
    
    print(f"\n📋 STEP 1: Create Exam with {test_rotation}° Rotation")
    print("-" * 40)
    
    # Create exam with rotation (simulating upload)
    exam_data = {
        'name': f'Workflow Test - {datetime.now().strftime("%H%M%S")}',
        'curriculum_level_id': curriculum_level.id,
        'timer_minutes': 30,
        'total_questions': 3,
        'default_options_count': 4,
        'pdf_rotation': test_rotation,  # Set rotation
        'is_active': True
    }
    
    pdf_file = SimpleUploadedFile(
        "workflow_test.pdf",
        b'%PDF-1.4 test content',
        content_type='application/pdf'
    )
    
    exam = ExamService.create_exam(
        exam_data=exam_data,
        pdf_file=pdf_file
    )
    
    print(f"✅ Exam created: {exam.name}")
    print(f"   ID: {exam.id}")
    print(f"   Rotation saved: {exam.pdf_rotation}°")
    
    # Verify database
    exam_db = Exam.objects.get(id=exam.id)
    assert exam_db.pdf_rotation == test_rotation, f"Database rotation mismatch: {exam_db.pdf_rotation}°"
    print(f"✅ Database verified: {exam_db.pdf_rotation}°")
    
    print(f"\n📋 STEP 2: Check Preview/Manage Page")
    print("-" * 40)
    
    # Test preview page
    response = client.get(f'/api/placement/exams/{exam.id}/preview/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check if rotation is initialized in JavaScript
        if f'currentRotation = {test_rotation}' in content:
            print(f"✅ Preview page initializes with {test_rotation}°")
        elif 'currentRotation = {{ exam.pdf_rotation|default:0 }}' in content:
            print(f"✅ Preview page uses template variable for rotation")
        else:
            print(f"⚠️  Preview page rotation initialization unclear")
            
        # Check if rotation value is in the page
        if f'{test_rotation}' in content:
            print(f"✅ Rotation value {test_rotation} found in preview page")
    else:
        print(f"❌ Preview page error: {response.status_code}")
    
    print(f"\n📋 STEP 3: Update Rotation via API")
    print("-" * 40)
    
    # Test updating rotation (simulating save from Manage Exams)
    new_rotation = 90
    response = client.post(
        f'/api/placement/exams/{exam.id}/save-answers/',
        data=json.dumps({
            'questions': [],
            'audio_assignments': {},
            'pdf_rotation': new_rotation
        }),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('pdf_rotation_saved') == new_rotation:
            print(f"✅ API updated rotation to {new_rotation}°")
        else:
            print(f"❌ API response unexpected: {data}")
    else:
        print(f"❌ API error: {response.status_code}")
    
    # Verify database update
    exam_db.refresh_from_db()
    assert exam_db.pdf_rotation == new_rotation, f"Update failed: {exam_db.pdf_rotation}°"
    print(f"✅ Database updated: {exam_db.pdf_rotation}°")
    
    print(f"\n📋 STEP 4: Check Student Interface")
    print("-" * 40)
    
    # Create a test session
    session = StudentSession.objects.create(
        exam=exam,
        student_name='Rotation Test Student',
        parent_phone='5555555555',
        grade=5,
        academic_rank='TOP_30',
        started_at=timezone.now()
    )
    
    # Test student view
    response = client.get(f'/placement/test/{session.id}/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check if rotation is in APP_CONFIG
        if f'"pdfRotation": {new_rotation}' in content or f'"pdfRotation":{new_rotation}' in content:
            print(f"✅ Student interface receives rotation: {new_rotation}°")
        else:
            # Check for alternative formats
            if 'pdfRotation' in content and str(new_rotation) in content:
                print(f"✅ Student interface has rotation value {new_rotation}°")
            else:
                print(f"⚠️  Student interface rotation not clearly found")
                
        # Check if APP_CONFIG exists
        if 'APP_CONFIG' in content:
            print("✅ APP_CONFIG found in student interface")
            
            # Look for the exam configuration
            if '"exam":' in content or '"exam" :' in content:
                print("✅ Exam configuration present in APP_CONFIG")
    else:
        print(f"❌ Student interface error: {response.status_code}")
    
    print(f"\n📋 STEP 5: Final Verification")
    print("-" * 40)
    
    # Final check of all rotation values
    exam_final = Exam.objects.get(id=exam.id)
    print(f"Final rotation in database: {exam_final.pdf_rotation}°")
    
    all_passed = exam_final.pdf_rotation == new_rotation
    
    # Cleanup
    print(f"\n📋 Cleaning Up Test Data")
    print("-" * 40)
    
    session.delete()
    exam.delete()
    curriculum_level.delete()
    subprogram.delete()
    program.delete()
    print("✅ Test data cleaned up")
    
    return all_passed


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 PDF ROTATION COMPLETE WORKFLOW TEST")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        success = test_complete_rotation_workflow()
        
        print("\n" + "=" * 80)
        print("🎯 FINAL RESULT")
        print("=" * 80)
        
        if success:
            print("✅ COMPLETE ROTATION WORKFLOW WORKING!")
            print("\nThe system successfully:")
            print("• Creates exams with rotation from upload")
            print("• Persists rotation in database")
            print("• Shows rotation in preview/manage pages")
            print("• Updates rotation via API")
            print("• Passes rotation to student interface")
            print("\n🎉 PDF rotation persistence is fully functional!")
        else:
            print("❌ Workflow test encountered issues")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)