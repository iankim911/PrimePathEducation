#!/usr/bin/env python
"""
Manual test for exam name submission fix.
Simulates form submission with exam name.
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from primepath_routinetest.models import Exam as RoutineExam

def test_exam_submission_with_name():
    """Test that exam can be created with auto-generated name."""
    print("\n" + "="*80)
    print("🔍 MANUAL EXAM NAME SUBMISSION TEST")
    print("="*80)
    
    # Setup
    client = Client()
    user, _ = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    user.set_password('testpass123')
    user.save()
    client.login(username='test_admin', password='testpass123')
    
    # Create a minimal PDF file for testing
    pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 2\n0000000000 65535 f\n0000000009 00000 n\ntrailer\n<< /Size 2 /Root 1 0 R >>\nstartxref\n42\n%%EOF'
    pdf_file = SimpleUploadedFile('test.pdf', pdf_content, content_type='application/pdf')
    
    # Prepare form data matching what JavaScript generates
    form_data = {
        # Auto-generated name fields
        'name': '[RT] - Mar 2025 - CORE Phonics Lv1',  # Backend expects 'name'
        'final_exam_name': '[RT] - Mar 2025 - CORE Phonics Lv1',  # Frontend field
        'generated_base_name': '[RT] - Mar 2025 - CORE Phonics Lv1',
        
        # Exam configuration
        'exam_type': 'REVIEW',
        'time_period_month': 'MAR',
        'academic_year': '2025',
        'class_codes[]': ['CLASS_7A', 'CLASS_7B'],
        
        # Curriculum selection
        'curriculum_level': '47',  # CORE Phonics Level 1
        'selected_program': 'CORE',
        'selected_subprogram': 'Phonics',
        'selected_level_number': '1',
        
        # Other required fields
        'total_questions': '20',
        'default_options_count': '5',
        'timer_minutes': '60',
        'pdf_rotation': '0',
        'instructions': 'Test instructions',
    }
    
    print("\n📋 Submitting exam with auto-generated name:")
    print(f"   Name field: {form_data['name']}")
    print(f"   Exam type: {form_data['exam_type']}")
    print(f"   Time period: {form_data['time_period_month']} {form_data['academic_year']}")
    print(f"   Curriculum: {form_data['selected_program']} {form_data['selected_subprogram']} Level {form_data['selected_level_number']}")
    
    # Submit the form
    response = client.post(
        '/RoutineTest/exams/create/',
        data=form_data,
        files={'pdf_file': pdf_file}
    )
    
    print("\n📊 Response Details:")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 302:  # Redirect means success
        print("   ✅ Form submitted successfully!")
        
        # Check if exam was created
        exam = RoutineExam.objects.filter(name__contains='CORE Phonics').first()
        if exam:
            print(f"\n✅ EXAM CREATED SUCCESSFULLY!")
            print(f"   ID: {exam.id}")
            print(f"   Name: {exam.name}")
            print(f"   Type: {exam.exam_type}")
            print(f"   Questions: {exam.total_questions}")
            
            # Cleanup
            exam.delete()
            print("\n🧹 Test exam deleted")
        else:
            print("\n❌ Exam not found in database")
    else:
        # Check for error messages
        if hasattr(response, 'context') and response.context:
            if 'messages' in response.context:
                print("\n❌ Error Messages:")
                for msg in response.context['messages']:
                    print(f"   - {msg}")
        
        # Check response content for errors
        content = response.content.decode('utf-8')
        if 'Exam name is required' in content:
            print("\n❌ STILL GETTING 'Exam name is required' ERROR!")
            print("   The fix is not working properly.")
        elif 'error' in content.lower():
            print("\n❌ Other errors found in response")
            # Extract error messages
            import re
            errors = re.findall(r'<div[^>]*class="[^"]*alert[^"]*"[^>]*>(.*?)</div>', content, re.DOTALL)
            for error in errors[:3]:  # Show first 3 errors
                clean_error = re.sub(r'<[^>]+>', '', error).strip()
                if clean_error:
                    print(f"   - {clean_error[:100]}")
    
    print("\n" + "="*80)
    print("📌 Summary:")
    if response.status_code == 302:
        print("✅ Exam name submission fix is WORKING!")
        print("   The auto-generated name was accepted by the backend.")
    else:
        print("⚠️ Exam name submission may still have issues.")
        print("   Check the form field mapping and JavaScript.")
    print("="*80)

if __name__ == '__main__':
    test_exam_submission_with_name()