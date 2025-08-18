#!/usr/bin/env python
"""
Ultra-deep analysis of PDF rendering issue in RoutineTest.
Tests PDF file existence, accessibility, and rendering setup.
"""
import os
import sys
import django
import json
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import Exam as RoutineExam
from placement_test.models import Exam as PlacementExam
from django.conf import settings


def check_pdf_files_exist():
    """Check if PDF files actually exist on disk."""
    print("\n" + "="*80)
    print("📁 CHECKING PDF FILES ON DISK")
    print("="*80)
    
    results = []
    
    # Check RoutineTest PDFs
    print("\n📗 RoutineTest PDFs:")
    rt_exams = RoutineExam.objects.filter(pdf_file__isnull=False)
    for exam in rt_exams:
        if exam.pdf_file:
            file_path = exam.pdf_file.path if hasattr(exam.pdf_file, 'path') else None
            file_exists = os.path.exists(file_path) if file_path else False
            file_size = os.path.getsize(file_path) if file_exists else 0
            
            print(f"\n   Exam: {exam.name[:50]}...")
            print(f"   PDF Field: {exam.pdf_file.name}")
            print(f"   Full Path: {file_path}")
            print(f"   File Exists: {'✅ YES' if file_exists else '❌ NO'}")
            if file_exists:
                print(f"   File Size: {file_size:,} bytes")
            print(f"   URL: {exam.pdf_file.url}")
            
            results.append(('RoutineTest PDF', file_exists))
    
    # Check PlacementTest PDFs
    print("\n📘 PlacementTest PDFs:")
    pt_exams = PlacementExam.objects.filter(pdf_file__isnull=False)
    for exam in pt_exams[:3]:  # Check first 3
        if exam.pdf_file:
            file_path = exam.pdf_file.path if hasattr(exam.pdf_file, 'path') else None
            file_exists = os.path.exists(file_path) if file_path else False
            file_size = os.path.getsize(file_path) if file_exists else 0
            
            print(f"\n   Exam: {exam.name[:50]}...")
            print(f"   PDF Field: {exam.pdf_file.name}")
            print(f"   Full Path: {file_path}")
            print(f"   File Exists: {'✅ YES' if file_exists else '❌ NO'}")
            if file_exists:
                print(f"   File Size: {file_size:,} bytes")
            print(f"   URL: {exam.pdf_file.url}")
            
            results.append(('PlacementTest PDF', file_exists))
    
    return results


def check_media_settings():
    """Check Django media settings."""
    print("\n" + "="*80)
    print("⚙️ MEDIA SETTINGS CONFIGURATION")
    print("="*80)
    
    print(f"\nMEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    
    # Check if media directory exists
    media_exists = os.path.exists(settings.MEDIA_ROOT)
    print(f"\nMedia Root Exists: {'✅ YES' if media_exists else '❌ NO'}")
    
    if media_exists:
        # Check subdirectories
        pdfs_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        audio_dir = os.path.join(settings.MEDIA_ROOT, 'audio')
        
        print(f"PDFs Directory: {'✅ EXISTS' if os.path.exists(pdfs_dir) else '❌ MISSING'}")
        print(f"Audio Directory: {'✅ EXISTS' if os.path.exists(audio_dir) else '❌ MISSING'}")
        
        if os.path.exists(pdfs_dir):
            pdf_count = len([f for f in os.listdir(pdfs_dir) if f.endswith('.pdf')])
            print(f"PDF Files in directory: {pdf_count}")
    
    return media_exists


def test_pdf_url_access():
    """Test if PDF URLs are accessible via HTTP."""
    print("\n" + "="*80)
    print("🌐 TESTING PDF URL ACCESSIBILITY")
    print("="*80)
    
    client = Client()
    user, _ = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    user.set_password('testpass123')
    user.save()
    client.login(username='test_admin', password='testpass123')
    
    results = []
    
    # Test RoutineTest PDF access
    rt_exam = RoutineExam.objects.filter(pdf_file__isnull=False).first()
    if rt_exam and rt_exam.pdf_file:
        pdf_url = rt_exam.pdf_file.url
        print(f"\n📗 Testing RoutineTest PDF URL: {pdf_url}")
        
        response = client.get(pdf_url, follow=True)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Type: {response.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            print(f"   ✅ PDF accessible via URL")
            # Handle FileResponse which uses streaming_content
            if hasattr(response, 'streaming_content'):
                content_size = sum(len(chunk) for chunk in response.streaming_content)
                print(f"   Response Size: {content_size:,} bytes")
            elif hasattr(response, 'content'):
                print(f"   Response Size: {len(response.content):,} bytes")
            results.append(('RoutineTest PDF URL', True))
        else:
            print(f"   ❌ PDF not accessible (Status: {response.status_code})")
            results.append(('RoutineTest PDF URL', False))
    
    # Test PlacementTest PDF access
    pt_exam = PlacementExam.objects.filter(pdf_file__isnull=False).first()
    if pt_exam and pt_exam.pdf_file:
        pdf_url = pt_exam.pdf_file.url
        print(f"\n📘 Testing PlacementTest PDF URL: {pdf_url}")
        
        response = client.get(pdf_url, follow=True)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Type: {response.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            print(f"   ✅ PDF accessible via URL")
            # Handle FileResponse which uses streaming_content
            if hasattr(response, 'streaming_content'):
                content_size = sum(len(chunk) for chunk in response.streaming_content)
                print(f"   Response Size: {content_size:,} bytes")
            elif hasattr(response, 'content'):
                print(f"   Response Size: {len(response.content):,} bytes")
            results.append(('PlacementTest PDF URL', True))
        else:
            print(f"   ❌ PDF not accessible (Status: {response.status_code})")
            results.append(('PlacementTest PDF URL', False))
    
    return results


def test_preview_page_pdf_context():
    """Test if PDF context is being passed to template."""
    print("\n" + "="*80)
    print("📄 TESTING PREVIEW PAGE PDF CONTEXT")
    print("="*80)
    
    client = Client()
    client.login(username='test_admin', password='testpass123')
    
    # Test RoutineTest preview page - specifically get one with a PDF
    rt_exam = None
    for exam in RoutineExam.objects.all():
        try:
            if exam.pdf_file and exam.pdf_file.name:
                rt_exam = exam
                break
        except ValueError:
            continue
    
    if rt_exam:
        print(f"\n📗 Testing RoutineTest Preview Page")
        print(f"   Exam: {rt_exam.name}")
        print(f"   Has PDF: {bool(rt_exam.pdf_file)}")
        
        response = client.get(f'/RoutineTest/exams/{rt_exam.id}/preview/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for PDF-related elements
            checks = [
                ('PDF.js library', 'pdf.js' in content.lower()),
                ('Canvas element', 'pdf-canvas' in content),
                ('PDF controls', 'pdf-controls' in content),
                ('PDF loading section', 'pdf-loading' in content),
                ('Download PDF button', 'Download PDF' in content),
            ]
            
            # Only check for PDF URL if exam has a PDF
            if rt_exam.pdf_file:
                try:
                    actual_url = rt_exam.pdf_file.url
                    checks.append(('PDF URL in template', actual_url in content))
                except ValueError:
                    checks.append(('PDF URL in template', False))
            
            for name, check in checks:
                print(f"   {name}: {'✅ YES' if check else '❌ NO'}")
    
    return True


def analyze_pdf_js_setup():
    """Analyze PDF.js setup in template."""
    print("\n" + "="*80)
    print("📚 ANALYZING PDF.JS CONFIGURATION")
    print("="*80)
    
    template_path = 'templates/primepath_routinetest/preview_and_answers.html'
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Check for PDF.js CDN
    if 'cdnjs.cloudflare.com/ajax/libs/pdf.js' in content:
        print("✅ PDF.js CDN link found")
        # Extract version
        import re
        version_match = re.search(r'pdf\.js/([0-9.]+)/', content)
        if version_match:
            print(f"   Version: {version_match.group(1)}")
    else:
        print("❌ PDF.js CDN link NOT found")
    
    # Check for worker configuration
    if 'pdf.worker' in content:
        print("✅ PDF.js worker configured")
    else:
        print("❌ PDF.js worker NOT configured")
    
    # Check for canvas element
    if 'id="pdf-canvas"' in content:
        print("✅ PDF canvas element present")
    else:
        print("❌ PDF canvas element NOT found")
    
    # Check for error handling
    if 'catch' in content and 'pdf' in content.lower():
        print("✅ PDF error handling present")
    else:
        print("⚠️ Limited PDF error handling")
    
    return True


def main():
    """Run comprehensive PDF analysis."""
    print("\n" + "🔍"*40)
    print("🔍 ULTRA-DEEP PDF RENDERING ANALYSIS")
    print("🔍"*40)
    
    all_results = []
    
    # 1. Check media settings
    media_ok = check_media_settings()
    all_results.append(('Media Settings', media_ok))
    
    # 2. Check if PDF files exist
    pdf_results = check_pdf_files_exist()
    all_results.extend(pdf_results)
    
    # 3. Test PDF URL access
    url_results = test_pdf_url_access()
    all_results.extend(url_results)
    
    # 4. Test preview page context
    context_ok = test_preview_page_pdf_context()
    all_results.append(('Preview Context', context_ok))
    
    # 5. Analyze PDF.js setup
    pdfjs_ok = analyze_pdf_js_setup()
    all_results.append(('PDF.js Setup', pdfjs_ok))
    
    # Summary
    print("\n" + "="*80)
    print("📊 ANALYSIS SUMMARY")
    print("="*80)
    
    for name, passed in all_results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    # Diagnosis
    print("\n" + "="*80)
    print("🔬 DIAGNOSIS")
    print("="*80)
    
    pdf_files_exist = any(r[1] for r in all_results if 'PDF' in r[0] and 'URL' not in r[0])
    urls_accessible = any(r[1] for r in all_results if 'URL' in r[0])
    
    if not pdf_files_exist:
        print("❌ CRITICAL: PDF files don't exist on disk")
        print("   Solution: Re-upload PDF files")
    elif not urls_accessible:
        print("❌ CRITICAL: PDFs exist but URLs not accessible")
        print("   Solution: Check media URL configuration")
    elif not media_ok:
        print("❌ CRITICAL: Media directory issues")
        print("   Solution: Create media directories")
    else:
        print("⚠️ PDFs exist and accessible, likely JavaScript issue")
        print("   Solution: Fix PDF.js initialization/rendering")
    
    return all(r[1] for r in all_results)


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)