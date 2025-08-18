#!/usr/bin/env python
"""
Live test of PDF rendering in RoutineTest preview page.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import Exam as RoutineExam

def main():
    print("\n" + "="*80)
    print("🔍 TESTING PDF RENDERING IN BROWSER")
    print("="*80)
    
    # Create test client
    client = Client()
    user, _ = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    user.set_password('testpass123')
    user.save()
    client.login(username='test_admin', password='testpass123')
    
    # Find exam with PDF
    rt_exam = None
    for exam in RoutineExam.objects.all():
        try:
            if exam.pdf_file and exam.pdf_file.name:
                rt_exam = exam
                break
        except ValueError:
            continue
    
    if rt_exam:
        print(f"\n✅ Found exam with PDF: {rt_exam.name}")
        print(f"   PDF file: {rt_exam.pdf_file.name}")
        print(f"   PDF URL: {rt_exam.pdf_file.url}")
        
        # Test the preview page
        response = client.get(f'/RoutineTest/exams/{rt_exam.id}/preview/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for critical elements
            checks = {
                'PDF.js library': 'pdf.js' in content.lower(),
                'Canvas element': 'pdf-canvas' in content,
                'PDF URL in page': rt_exam.pdf_file.url in content,
                'PDF controls': 'pdf-controls' in content,
                'Initialize function': 'initializePdfImageDisplay' in content,
                'Error handling': 'catch' in content and 'pdf' in content.lower(),
            }
            
            print("\n📋 Page Analysis:")
            all_passed = True
            for check, result in checks.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check}")
                if not result:
                    all_passed = False
            
            if all_passed:
                print("\n🎉 All PDF components are present!")
                print(f"\n📌 Test the PDF rendering manually:")
                print(f"   1. Start the server: ../venv/bin/python manage.py runserver")
                print(f"   2. Login as: test_admin / testpass123")
                print(f"   3. Open: http://127.0.0.1:8000/RoutineTest/exams/{rt_exam.id}/preview/")
                print(f"   4. Check browser console for any JavaScript errors")
            else:
                print("\n⚠️ Some PDF components are missing. Check the failed items above.")
                
                # Save HTML for debugging
                with open('debug_preview_page.html', 'w') as f:
                    f.write(content)
                print("\n📄 Page HTML saved to: debug_preview_page.html")
        else:
            print(f"\n❌ Preview page returned status: {response.status_code}")
    else:
        print("\n❌ No RoutineTest exams with PDF files found")
        print("   Please upload a PDF to an exam first")
    
    # Also check PlacementTest for comparison
    from placement_test.models import Exam as PlacementExam
    pt_exam = PlacementExam.objects.filter(pdf_file__isnull=False).first()
    if pt_exam:
        print(f"\n📘 PlacementTest exam with PDF: {pt_exam.name}")
        print(f"   For comparison: http://127.0.0.1:8000/PlacementTest/exams/{pt_exam.id}/preview/")

if __name__ == '__main__':
    main()