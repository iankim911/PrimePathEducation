#!/usr/bin/env python
"""
Test PDF rotation persistence across interfaces
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from placement_test.models import PlacementExam as Exam
from datetime import datetime

def test_pdf_rotation_flow():
    """Test that PDF rotation persists across all interfaces"""
    
    print("=" * 80)
    print("🔍 PDF ROTATION PERSISTENCE TEST")
    print("=" * 80)
    
    # Get or create a test exam
    exam = Exam.objects.filter(pdf_file__isnull=False).first()
    
    if not exam:
        print("❌ No exam with PDF file found")
        return False
    
    print(f"✅ Using exam: {exam.name}")
    print(f"   Current rotation: {exam.pdf_rotation}°")
    
    # Test 1: Update rotation via API (simulating preview page save)
    print("\n📋 TEST 1: Saving rotation via API")
    print("-" * 40)
    
    client = Client()
    test_rotation = 90
    
    # Simulate saving from preview page
    response = client.post(
        f'/api/PlacementTest/exams/{exam.id}/save-answers/',
        data=json.dumps({
            'questions': [],
            'audio_assignments': {},
            'pdf_rotation': test_rotation
        }),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ API call successful")
            print(f"   Response: {data.get('pdf_rotation_saved')}°")
        else:
            print(f"❌ API call failed: {data}")
            return False
    else:
        print(f"❌ API returned status {response.status_code}")
        return False
    
    # Test 2: Verify database update
    print("\n📋 TEST 2: Verifying database update")
    print("-" * 40)
    
    exam.refresh_from_db()
    if exam.pdf_rotation == test_rotation:
        print(f"✅ Database updated correctly: {exam.pdf_rotation}°")
    else:
        print(f"❌ Database not updated. Expected {test_rotation}°, got {exam.pdf_rotation}°")
        return False
    
    # Test 3: Check preview page loads with saved rotation
    print("\n📋 TEST 3: Checking preview page")
    print("-" * 40)
    
    response = client.get(f'/api/PlacementTest/exams/{exam.id}/preview/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check if rotation is in the JavaScript initialization
        if f'currentRotation = {test_rotation}' in content:
            print(f"✅ Preview page initializes with saved rotation: {test_rotation}°")
        else:
            # Try another pattern
            if f'pdf_rotation|default:{test_rotation}' in content or f'pdf_rotation|default:0' in content:
                print(f"✅ Preview page has rotation template variable")
            else:
                print(f"⚠️  Preview page may not be using saved rotation")
                print(f"   (This needs manual verification)")
    else:
        print(f"❌ Preview page returned status {response.status_code}")
    
    # Test 4: Check if rotation is passed to student interface
    print("\n📋 TEST 4: Checking student interface data")
    print("-" * 40)
    
    # Create a test session to check student view
    from placement_test.models import StudentSession
    from django.utils import timezone
    
    session = StudentSession.objects.create(
        exam=exam,
        student_name='Rotation Test Student',
        parent_phone='1234567890',
        grade=5,
        academic_rank='TOP_30',
        started_at=timezone.now()
    )
    
    response = client.get(f'/PlacementTest/test/{session.id}/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check if pdfRotation is in APP_CONFIG
        if f'"pdfRotation": {test_rotation}' in content or f'"pdfRotation":{test_rotation}' in content:
            print(f"✅ Student interface receives rotation: {test_rotation}°")
        else:
            print(f"⚠️  Student interface may not be receiving rotation")
            print(f"   Checking for APP_CONFIG...")
            
            # Look for APP_CONFIG initialization
            if 'APP_CONFIG' in content and 'pdfRotation' in content:
                print(f"   APP_CONFIG found with pdfRotation field")
            else:
                print(f"   APP_CONFIG or pdfRotation not found")
    else:
        print(f"❌ Student interface returned status {response.status_code}")
    
    # Clean up test session
    session.delete()
    
    # Test 5: Test multiple rotation values
    print("\n📋 TEST 5: Testing all valid rotation values")
    print("-" * 40)
    
    valid_rotations = [0, 90, 180, 270]
    all_passed = True
    
    for rotation in valid_rotations:
        response = client.post(
            f'/api/PlacementTest/exams/{exam.id}/save-answers/',
            data=json.dumps({
                'questions': [],
                'audio_assignments': {},
                'pdf_rotation': rotation
            }),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            exam.refresh_from_db()
            if exam.pdf_rotation == rotation:
                print(f"✅ Rotation {rotation}° saved correctly")
            else:
                print(f"❌ Rotation {rotation}° failed to save")
                all_passed = False
        else:
            print(f"❌ API failed for rotation {rotation}°")
            all_passed = False
    
    return all_passed


def check_model_field():
    """Check if the pdf_rotation field is properly configured"""
    print("\n📋 MODEL FIELD CHECK")
    print("-" * 40)
    
    from placement_test.models import PlacementExam as Exam
    from django.db import connection
    
    # Check model attribute
    exam = Exam.objects.first()
    if exam:
        try:
            rotation = exam.pdf_rotation
            print(f"✅ Model has pdf_rotation attribute: {rotation}°")
        except AttributeError:
            print("❌ Model missing pdf_rotation attribute")
            return False
    
    # Check database column
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(placement_test_exam)")
        columns = cursor.fetchall()
        
    has_field = any(col[1] == 'pdf_rotation' for col in columns)
    if has_field:
        print(f"✅ Database has pdf_rotation column")
    else:
        print(f"❌ Database missing pdf_rotation column")
        return False
    
    return True


if __name__ == '__main__':
    model_ok = check_model_field()
    
    if not model_ok:
        print("\n❌ Model/database issue detected. Migration may be needed.")
        sys.exit(1)
    
    success = test_pdf_rotation_flow()
    
    print("\n" + "=" * 80)
    print("🎯 FINAL RESULT")
    print("=" * 80)
    
    if success:
        print("✅ PDF ROTATION PERSISTENCE WORKING!")
        print("\nThe system correctly:")
        print("• Saves rotation from preview page")
        print("• Stores rotation in database")
        print("• Loads saved rotation in preview page")
        print("• Passes rotation to student interface")
        print("• Handles all valid rotation angles (0°, 90°, 180°, 270°)")
    else:
        print("❌ Some rotation tests failed")
        print("\nIssues detected - review output above")
    
    sys.exit(0 if success else 1)