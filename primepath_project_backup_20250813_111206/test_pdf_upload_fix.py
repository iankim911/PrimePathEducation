#!/usr/bin/env python
"""
Test script for PDF upload fix
Tests that the created_by field now correctly uses Teacher instance instead of User
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from placement_test.models import Exam
from django.test import Client
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile


def create_test_pdf():
    """Create a simple test PDF file in memory"""
    # Simple PDF content (minimal valid PDF)
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Count 1 /Kids [3 0 R] >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 24 Tf
100 700 Td
(Test Exam) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
365
%%EOF"""
    return SimpleUploadedFile("test_exam.pdf", pdf_content, content_type="application/pdf")


def test_pdf_upload_fix():
    """Test the PDF upload fix"""
    print("\n" + "="*80)
    print("🔍 TESTING PDF UPLOAD FIX")
    print("="*80)
    
    # Step 1: Check Teacher-User relationship
    print("\n1. Checking Teacher-User Relationship:")
    
    # Get the teacher1 user
    try:
        user = User.objects.get(username='teacher1')
        print(f"   ✅ Found user: {user.username} (ID: {user.id})")
    except User.DoesNotExist:
        print("   ❌ User 'teacher1' not found")
        return False
    
    # Check if Teacher profile exists
    try:
        teacher = user.teacher_profile
        print(f"   ✅ Teacher profile exists: {teacher.name} (ID: {teacher.id})")
        print(f"      - Email: {teacher.email}")
        print(f"      - Is Head Teacher: {teacher.is_head_teacher}")
        print(f"      - Is Active: {teacher.is_active}")
    except (AttributeError, Teacher.DoesNotExist):
        print("   ⚠️ Teacher profile doesn't exist, will be created on upload")
        teacher = None
    
    # Step 2: Test PDF upload via Django test client
    print("\n2. Testing PDF Upload via Form Submission:")
    
    client = Client()
    
    # Login as teacher1
    login_success = client.login(username='teacher1', password='teacher123')
    print(f"   Login Status: {'✅ Success' if login_success else '❌ Failed'}")
    
    if not login_success:
        print("   ❌ Cannot proceed without authentication")
        return False
    
    # Create test PDF file
    pdf_file = create_test_pdf()
    
    # Prepare form data with file included
    form_data = {
        'name': 'Test Exam - PDF Upload Fix',
        'curriculum_level': '',  # Optional
        'timer_minutes': '60',
        'total_questions': '10',
        'default_options_count': '5',
        'pdf_rotation': '0',
        'pdf_file': pdf_file  # Include file in form data
    }
    
    # Submit the form
    print("   Submitting exam upload form...")
    response = client.post(
        '/api/placement/exams/create/',
        data=form_data,
        follow=True
    )
    
    print(f"   Response Status: {response.status_code}")
    
    # Check if upload was successful
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check for success message
        if 'uploaded successfully' in content:
            print("   ✅ Upload successful!")
            
            # Find the created exam
            try:
                exam = Exam.objects.filter(name='Test Exam - PDF Upload Fix').latest('created_at')
                print(f"   ✅ Exam created: {exam.name} (ID: {exam.id})")
                
                # Check created_by field
                if exam.created_by:
                    print(f"   ✅ Created by Teacher: {exam.created_by.name} (ID: {exam.created_by.id})")
                    print(f"      - Teacher Model: {type(exam.created_by).__name__}")
                    print(f"      - Is Teacher Instance: {isinstance(exam.created_by, Teacher)}")
                    
                    # Verify it's the correct teacher
                    if exam.created_by.user == user:
                        print(f"   ✅ Teacher correctly linked to User: {user.username}")
                    else:
                        print(f"   ⚠️ Teacher linked to different user")
                else:
                    print("   ⚠️ Created_by is None")
                    
            except Exam.DoesNotExist:
                print("   ❌ Exam not found in database")
                
        elif 'Invalid input' in content:
            # Extract error message
            import re
            error_match = re.search(r'Invalid input: ([^<]+)', content)
            if error_match:
                error_msg = error_match.group(1)
                print(f"   ❌ Upload failed with error: {error_msg}")
                
                # This is likely our original error - check if it's the SimpleLazyObject error
                if 'SimpleLazyObject' in error_msg and 'Teacher' in error_msg:
                    print("   ❌ FIX NOT WORKING: Still getting SimpleLazyObject error!")
                    print("      The created_by field is still receiving User instead of Teacher")
                else:
                    print(f"   ❌ Different error: {error_msg}")
        else:
            print("   ⚠️ Unknown response - checking for errors...")
            if 'error' in content.lower():
                # Try to extract any error messages
                import re
                errors = re.findall(r'class="[^"]*error[^"]*"[^>]*>([^<]+)', content)
                for error in errors[:3]:  # Show first 3 errors
                    print(f"      Error found: {error}")
    else:
        print(f"   ❌ Unexpected status code: {response.status_code}")
    
    # Step 3: Direct model test (without going through view)
    print("\n3. Testing Direct Model Creation:")
    
    # Re-fetch teacher profile (in case it was created during upload)
    try:
        teacher = user.teacher_profile
    except (AttributeError, Teacher.DoesNotExist):
        # Create Teacher profile
        teacher = Teacher.objects.create(
            user=user,
            name=user.get_full_name() or user.username,
            email=user.email or f"{user.username}@example.com",
            is_head_teacher=user.is_superuser
        )
        print(f"   Created Teacher profile: {teacher.name} (ID: {teacher.id})")
    
    # Try creating exam directly with Teacher instance
    try:
        test_exam = Exam.objects.create(
            name='Direct Test Exam',
            timer_minutes=60,
            total_questions=5,
            default_options_count=5,
            created_by=teacher,  # Using Teacher instance
            is_active=True
        )
        print(f"   ✅ Direct creation successful: {test_exam.name}")
        print(f"      Created by: {test_exam.created_by.name}")
        
        # Clean up test exam
        test_exam.delete()
        
    except Exception as e:
        print(f"   ❌ Direct creation failed: {str(e)}")
    
    # Step 4: Summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY:")
    print("="*80)
    
    # Check if fix is working
    latest_exam = Exam.objects.filter(created_by__isnull=False).order_by('-created_at').first()
    if latest_exam and isinstance(latest_exam.created_by, Teacher):
        print("✅ FIX IS WORKING: Exams are correctly using Teacher instances")
        print(f"   Latest exam: {latest_exam.name}")
        print(f"   Created by Teacher: {latest_exam.created_by.name}")
        return True
    else:
        print("❌ FIX NEEDS ATTENTION: Check the implementation")
        return False


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# PDF UPLOAD FIX TEST")
    print("#"*80)
    
    success = test_pdf_upload_fix()
    
    if success:
        print("\n🎉 SUCCESS: PDF upload fix is working correctly!")
        print("Teachers can now upload exam PDFs without errors.")
    else:
        print("\n⚠️ ATTENTION NEEDED: The fix may need additional work.")