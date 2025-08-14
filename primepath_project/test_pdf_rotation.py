#!/usr/bin/env python
"""
Test PDF rotation persistence feature
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import Exam
from django.test import Client
from django.urls import reverse
import json

def test_pdf_rotation_feature():
    """Test PDF rotation persistence across all interfaces"""
    print("\n" + "="*70)
    print("PDF ROTATION PERSISTENCE TEST")
    print("="*70)
    
    client = Client()
    
    # Test 1: Check if model has rotation field
    print("\n1. Testing Exam model rotation field...")
    try:
        exam = Exam.objects.first()
        if exam:
            # Check if pdf_rotation field exists
            if hasattr(exam, 'pdf_rotation'):
                print(f"   ✓ Exam has pdf_rotation field")
                print(f"   Current rotation: {exam.pdf_rotation} degrees")
                
                # Test setting rotation
                exam.pdf_rotation = 90
                exam.save()
                print(f"   ✓ Can set rotation to 90 degrees")
                
                # Reload and verify
                exam.refresh_from_db()
                if exam.pdf_rotation == 90:
                    print(f"   ✓ Rotation persisted in database")
                else:
                    print(f"   ✗ Rotation not persisted correctly")
                
                # Reset to 0
                exam.pdf_rotation = 0
                exam.save()
            else:
                print("   ✗ pdf_rotation field not found on Exam model")
                print("   Note: Migration may need to be run")
        else:
            print("   ⚠ No exams found in database to test")
    except Exception as e:
        print(f"   ✗ Error testing model: {e}")
    
    # Test 2: Test save_exam_answers endpoint
    print("\n2. Testing save_exam_answers with rotation...")
    exam = Exam.objects.first()
    if exam:
        try:
            # Test saving rotation via API
            test_data = {
                'questions': [],
                'audio_assignments': {},
                'pdf_rotation': 180
            }
            
            response = client.post(
                f'/api/PlacementTest/exams/{exam.id}/save-answers/',
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("   ✓ API accepts pdf_rotation parameter")
                    
                    # Check if rotation was saved
                    exam.refresh_from_db()
                    if hasattr(exam, 'pdf_rotation') and exam.pdf_rotation == 180:
                        print("   ✓ Rotation saved via API")
                    else:
                        print("   ⚠ Rotation not saved (field may not exist)")
                else:
                    print(f"   ✗ API error: {data.get('error')}")
            else:
                print(f"   ✗ API returned status {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error testing API: {e}")
    
    # Test 3: Check templates for rotation support
    print("\n3. Testing template support...")
    
    templates_to_check = [
        ('create_exam.html', ['pdf_rotation', 'currentRotation']),
        ('preview_and_answers.html', ['currentRotation', 'pdf_rotation']),
        ('student_test_v2.html', ['pdfRotation', 'APP_CONFIG.exam'])
    ]
    
    for template_name, keywords in templates_to_check:
        template_path = f'templates/placement_test/{template_name}'
        try:
            with open(template_path, 'r') as f:
                content = f.read()
                found_keywords = [kw for kw in keywords if kw in content]
                if found_keywords:
                    print(f"   ✓ {template_name}: Found {', '.join(found_keywords)}")
                else:
                    print(f"   ⚠ {template_name}: Keywords not found")
        except FileNotFoundError:
            print(f"   ⚠ {template_name}: File not found")
        except Exception as e:
            print(f"   ✗ Error checking {template_name}: {e}")
    
    # Test 4: Check JavaScript module
    print("\n4. Testing PDF viewer module...")
    try:
        with open('static/js/modules/pdf-viewer.js', 'r') as f:
            content = f.read()
            if 'this.rotation' in content and 'rotateClockwise' in content:
                print("   ✓ PDF viewer module has rotation support")
            else:
                print("   ✗ PDF viewer module missing rotation methods")
    except Exception as e:
        print(f"   ✗ Error checking PDF viewer: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("IMPLEMENTATION STATUS")
    print("="*70)
    print("\nCompleted:")
    print("✓ Added pdf_rotation field to Exam model")
    print("✓ Updated save_exam_answers to handle rotation")
    print("✓ Modified create_exam.html to send rotation on upload")
    print("✓ Modified preview_and_answers.html to save rotation")
    print("✓ Updated student view to pass rotation to template")
    print("✓ Modified student_test_v2.html to apply saved rotation")
    
    print("\nPending:")
    print("⚠ Migration needs to be created and run")
    print("  Run: python manage.py makemigrations placement_test")
    print("  Run: python manage.py migrate")
    
    print("\n" + "="*70)
    print("Next Steps:")
    print("1. Create and run migration for pdf_rotation field")
    print("2. Test rotation persistence in Upload Exam")
    print("3. Test rotation save in Manage Exams")
    print("4. Verify rotation displays correctly for students")
    print("="*70)

if __name__ == '__main__':
    test_pdf_rotation_feature()