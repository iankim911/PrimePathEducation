#!/usr/bin/env python3
"""
Comprehensive debug and fix for PDF loading issue in RoutineTest Preview
"""

import uuid
import os
import sys
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

try:
    import django
    django.setup()
    
    from primepath_routinetest.models.exam import Exam
    from django.conf import settings
    from django.urls import reverse
    
    def debug_and_fix_pdf():
        print("=== PDF Loading Debug & Fix ===")
        
        # Test the problematic exam
        # Convert URL UUID to proper format
        url_uuid = "54b00626-6cf6-4fa7-98d8-6203c1397713"
        
        try:
            # Try to get the exam by UUID
            exam = Exam.objects.get(id=url_uuid)
            
            print(f"✓ Found exam: {exam.name}")
            print(f"  ID: {exam.id}")
            print(f"  PDF File: {exam.pdf_file}")
            print(f"  PDF File Path: {exam.pdf_file.path if exam.pdf_file else 'None'}")
            print(f"  PDF File URL: {exam.pdf_file.url if exam.pdf_file else 'None'}")
            
            # Check if PDF file exists on disk
            if exam.pdf_file:
                pdf_path = exam.pdf_file.path
                if os.path.exists(pdf_path):
                    print(f"✓ PDF file exists at: {pdf_path}")
                    
                    # Check file size and content
                    file_size = os.path.getsize(pdf_path)
                    print(f"  File size: {file_size} bytes")
                    
                    # Check PDF header
                    with open(pdf_path, 'rb') as f:
                        header = f.read(5)
                        if header == b'%PDF-':
                            print("✓ Valid PDF header found")
                        else:
                            print(f"✗ Invalid PDF header: {header}")
                            
                    # Test URL generation
                    try:
                        preview_url = reverse('RoutineTest:preview_exam', args=[exam.id])
                        print(f"✓ Preview URL: {preview_url}")
                    except Exception as e:
                        print(f"✗ Error generating preview URL: {e}")
                        
                else:
                    print(f"✗ PDF file does not exist at: {pdf_path}")
                    print("  This indicates a file storage/path issue")
                    
                    # Check media directory
                    media_root = settings.MEDIA_ROOT
                    print(f"  MEDIA_ROOT: {media_root}")
                    
                    if os.path.exists(media_root):
                        # Find the PDF file
                        pdf_name = os.path.basename(exam.pdf_file.name)
                        for root, dirs, files in os.walk(media_root):
                            if pdf_name in files:
                                actual_path = os.path.join(root, pdf_name)
                                print(f"  Found PDF at different location: {actual_path}")
                                break
                        else:
                            print(f"  PDF file '{pdf_name}' not found anywhere in media directory")
            else:
                print("✗ No PDF file associated with exam")
                
        except Exam.DoesNotExist:
            print(f"✗ Exam not found with UUID: {url_uuid}")
            
            # Check for similar UUIDs (maybe formatting issue)
            db_uuid_no_hyphens = url_uuid.replace('-', '')
            print(f"  Checking without hyphens: {db_uuid_no_hyphens}")
            
            # Check all recent exams
            recent_exams = Exam.objects.all().order_by('-created_at')[:10]
            print(f"  Found {recent_exams.count()} recent exams:")
            
            for i, exam in enumerate(recent_exams, 1):
                exam_uuid_str = str(exam.id)
                print(f"    {i}. {exam.name} - {exam_uuid_str}")
                if exam_uuid_str.replace('-', '') == db_uuid_no_hyphens:
                    print(f"       ⭐ MATCH FOUND! This is the correct exam")
                    # Now test with the correct UUID
                    return debug_correct_exam(exam)
                    
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            
    def debug_correct_exam(exam):
        """Debug the correct exam once found"""
        print(f"\n=== Testing Correct Exam: {exam.name} ===")
        
        # Test URL generation
        try:
            from django.test import Client
            from django.contrib.auth.models import User
            
            # Create a test client
            client = Client()
            
            # Create or get a test user
            test_user, created = User.objects.get_or_create(
                username='test_admin',
                defaults={'is_staff': True, 'is_superuser': True}
            )
            if created:
                test_user.set_password('test123')
                test_user.save()
                print("  Created test admin user")
            
            # Login as test user
            client.force_login(test_user)
            
            # Test the preview URL
            preview_url = f'/RoutineTest/exams/{exam.id}/preview/'
            print(f"  Testing URL: {preview_url}")
            
            response = client.get(preview_url)
            print(f"  Response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Preview page loads successfully")
                
                # Check if PDF URL is in the response
                content = response.content.decode('utf-8')
                if exam.pdf_file and exam.pdf_file.url in content:
                    print("✓ PDF URL found in template")
                    print(f"  PDF URL: {exam.pdf_file.url}")
                else:
                    print("✗ PDF URL not found in template")
                    if exam.pdf_file:
                        print(f"  Expected PDF URL: {exam.pdf_file.url}")
                        
            else:
                print(f"✗ Preview page failed to load: {response.status_code}")
                if hasattr(response, 'content'):
                    print(f"  Error content: {response.content.decode('utf-8')[:500]}")
                    
        except Exception as e:
            print(f"✗ Error testing correct exam: {e}")
            import traceback
            traceback.print_exc()
            
    def generate_fix_recommendations():
        print(f"\n=== Fix Recommendations ===")
        
        print("1. UUID FORMATTING ISSUE:")
        print("   - URLs use standard UUID format with hyphens")
        print("   - Ensure Django's UUID field conversion works properly")
        print("   - Check that exam IDs in URLs match database format")
        
        print("\n2. MEDIA FILE SERVING:")
        print("   - Verify MEDIA_URL and MEDIA_ROOT settings")
        print("   - Check that Django serves media files in DEBUG mode")
        print("   - Ensure PDF files have proper permissions")
        
        print("\n3. PDF.JS LOADING:")
        print("   - Check browser console for PDF.js errors")
        print("   - Verify PDF.js worker script loads properly")
        print("   - Test PDF file validity (proper PDF header)")
        
        print("\n4. TEMPLATE RENDERING:")
        print("   - Verify exam.pdf_file.url generates correct URL")
        print("   - Check that template receives correct exam object")
        print("   - Ensure no template caching issues")
        
    if __name__ == "__main__":
        debug_and_fix_pdf()
        generate_fix_recommendations()
        
except ImportError as e:
    print(f"Django not available: {e}")
    print("This script needs to be run in a Django environment")
except Exception as e:
    print(f"Setup error: {e}")
    import traceback
    traceback.print_exc()