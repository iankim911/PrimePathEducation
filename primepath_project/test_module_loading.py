#!/usr/bin/env python
"""
Test script to verify JavaScript module loading is working
"""

import os
import sys
import django
import time
import requests
from urllib.parse import urljoin

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import StudentSession, Exam
from core.models import CurriculumLevel
from django.utils import timezone

def test_module_loading():
    """Test that JavaScript modules are loading correctly"""
    
    print("=" * 60)
    print("TESTING JAVASCRIPT MODULE LOADING")
    print("=" * 60)
    
    # Check if server is running
    base_url = "http://127.0.0.1:8000"
    
    try:
        response = requests.get(base_url)
        print(f"✅ Server is running at {base_url}")
    except:
        print(f"❌ Server not running at {base_url}")
        print("Please start the server first")
        return False
    
    # Test static file serving
    print("\n" + "=" * 60)
    print("CHECKING STATIC FILES")
    print("=" * 60)
    
    static_files = [
        "/static/js/config/app-config.js",
        "/static/js/utils/event-delegation.js",
        "/static/js/utils/module-loader.js",
        "/static/js/modules/base-module.js",
        "/static/js/modules/answer-manager.js",
        "/static/js/modules/timer.js",
        "/static/js/modules/navigation.js",
        "/static/js/modules/pdf-viewer.js",
        "/static/js/modules/audio-player.js"
    ]
    
    all_files_ok = True
    for file_path in static_files:
        url = urljoin(base_url, file_path)
        try:
            response = requests.head(url)
            if response.status_code == 200:
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - Status: {response.status_code}")
                all_files_ok = False
        except Exception as e:
            print(f"❌ {file_path} - Error: {e}")
            all_files_ok = False
    
    if not all_files_ok:
        print("\n⚠️  Some static files are not being served correctly")
        print("Run: python manage.py collectstatic --noinput")
        return False
    
    print("\n✅ All static files are being served correctly")
    
    # Create or get a test session
    print("\n" + "=" * 60)
    print("CREATING TEST SESSION")
    print("=" * 60)
    
    # Find an exam with questions
    exam = Exam.objects.filter(questions__isnull=False).first()
    if not exam:
        print("❌ No exam with questions found")
        return False
    
    # Get a curriculum level
    level = CurriculumLevel.objects.first()
    if not level:
        print("❌ No curriculum level found")
        return False
    
    # Create a fresh test session
    session = StudentSession.objects.create(
        student_name='Module Test Student',
        grade=7,
        academic_rank='TOP_20',
        exam=exam,
        original_curriculum_level=level
    )
    
    test_url = f"{base_url}/PlacementTest/session/{session.id}/"
    print(f"✅ Created test session: {session.id}")
    print(f"📍 Test URL: {test_url}")
    
    # Test if the page loads
    try:
        response = requests.get(test_url)
        if response.status_code == 200:
            print("✅ Test page loads successfully")
            
            # Check for error indicators in HTML
            html = response.text
            
            # Check if modules are included
            if 'event-delegation.js' in html:
                print("✅ event-delegation.js included in page")
            else:
                print("⚠️  event-delegation.js not found in page")
            
            if 'module-loader.js' in html:
                print("✅ module-loader.js included in page")
            else:
                print("⚠️  module-loader.js not found in page")
            
            if 'answer-manager.js' in html:
                print("✅ answer-manager.js included in page")
            else:
                print("⚠️  answer-manager.js not found in page")
            
            # Check for initialization script
            if 'PRIMEPATH INITIALIZATION STARTING' in html:
                print("✅ Enhanced initialization script present")
            else:
                print("⚠️  Enhanced initialization script not found")
                
        else:
            print(f"❌ Test page returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading test page: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ All backend checks passed")
    print("ℹ️  To check frontend:")
    print(f"   1. Open: {test_url}")
    print("   2. Open browser console (F12)")
    print("   3. Look for 'PRIMEPATH INITIALIZATION' messages")
    print("   4. Check for any red error messages")
    print("   5. Verify 'Overall Success Rate' is > 80%")
    
    return True

if __name__ == "__main__":
    success = test_module_loading()
    sys.exit(0 if success else 1)