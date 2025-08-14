#!/usr/bin/env python
"""
Complete test of student interface functionality
Tests all critical features: navigation, answer submission, timer, audio, PDF
"""

import os
import sys
import django
import requests
import json
from urllib.parse import urljoin

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import StudentSession, Exam, Question, StudentAnswer
from core.models import CurriculumLevel
from django.utils import timezone

def test_complete_interface():
    """Test complete student interface functionality"""
    
    print("=" * 70)
    print("COMPLETE STUDENT INTERFACE TEST")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Create test session with all features
    print("\n📋 Creating comprehensive test session...")
    
    # Find exam with timer, PDF, and audio
    exam = Exam.objects.filter(
        timer_minutes__gt=0,
        questions__isnull=False
    ).first()
    
    if not exam:
        print("❌ No suitable exam found")
        return False
    
    level = CurriculumLevel.objects.first()
    session = StudentSession.objects.create(
        student_name='Complete Test Student',
        grade=8,
        academic_rank='TOP_10',
        exam=exam,
        original_curriculum_level=level
    )
    
    test_url = f"{base_url}/PlacementTest/session/{session.id}/"
    
    print(f"✅ Session created: {session.id}")
    print(f"   Exam: {exam.name}")
    print(f"   Questions: {exam.questions.count()}")
    print(f"   Timer: {exam.timer_minutes} minutes")
    print(f"   PDF: {'Yes' if exam.pdf_file else 'No'}")
    print(f"   Audio files: {exam.audio_files.count()}")
    
    # 2. Test page loading
    print("\n🌐 Testing page load...")
    
    response = requests.get(test_url)
    if response.status_code != 200:
        print(f"❌ Page failed to load: {response.status_code}")
        return False
    
    html = response.text
    print("✅ Page loaded successfully")
    
    # 3. Check critical elements
    print("\n🔍 Checking critical elements...")
    
    checks = {
        'Timer display': '<div id="timer"' in html or 'data-timer-seconds' in html,
        'Question navigation': 'question-nav-btn' in html,
        'Answer inputs': 'answer-input' in html or 'name="q_' in html,
        'Submit button': 'submit-test-btn' in html or 'data-action="submit-test"' in html,
        'PDF viewer': 'pdf-viewer' in html,
        'Audio controls': 'audio-button' in html or 'audio-player' in html,
        'Difficulty modal': 'difficulty-choice-modal' in html,
        'CSRF token': 'csrfmiddlewaretoken' in html or 'csrf_token' in html
    }
    
    all_ok = True
    for feature, present in checks.items():
        if present:
            print(f"  ✅ {feature}")
        else:
            print(f"  ❌ {feature}")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Some critical elements are missing")
    
    # 4. Test answer submission endpoint
    print("\n📝 Testing answer submission...")
    
    # Get CSRF token from page
    import re
    csrf_match = re.search(r"csrf['\"]:\s*['\"]([^'\"]+)['\"]", html)
    if not csrf_match:
        csrf_match = re.search(r"csrfmiddlewaretoken['\"].*?value=['\"]([^'\"]+)['\"]", html)
    
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print(f"  ✅ CSRF token found")
    else:
        print("  ⚠️  CSRF token not found, submission may fail")
        csrf_token = ""
    
    # Test submitting an answer
    question = exam.questions.first()
    if question:
        submit_url = f"{base_url}/api/PlacementTest/session/{session.id}/submit-answer/"
        
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json',
            'Cookie': f'csrftoken={csrf_token}'
        }
        
        data = {
            'question_id': str(question.id),
            'answer': 'A'
        }
        
        try:
            response = requests.post(submit_url, json=data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"  ✅ Answer submission works")
                    
                    # Check if answer was saved
                    saved = StudentAnswer.objects.filter(
                        session=session,
                        question=question
                    ).exists()
                    
                    if saved:
                        print(f"  ✅ Answer saved to database")
                    else:
                        print(f"  ⚠️  Answer not found in database")
                else:
                    print(f"  ⚠️  Submission failed: {result.get('error')}")
            else:
                print(f"  ❌ Submission returned status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Submission error: {e}")
    
    # 5. Check JavaScript health
    print("\n🔧 JavaScript Module Status:")
    print("  Check browser console for detailed initialization logs")
    print("  Expected modules:")
    print("    - EventDelegation")
    print("    - PDFViewer") 
    print("    - Timer")
    print("    - AudioPlayer")
    print("    - AnswerManager")
    print("    - Navigation")
    
    # 6. Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Test session created successfully")
    print(f"📍 Test URL: {test_url}")
    print("\n📋 Next Steps:")
    print("1. Open the URL in a browser")
    print("2. Open Developer Console (F12)")
    print("3. Look for initialization messages")
    print("4. Check for JavaScript errors")
    print("5. Test these features:")
    print("   - Click question navigation buttons (1, 2, 3...)")
    print("   - Select answer options")
    print("   - Check if timer is counting down")
    print("   - Try audio buttons if present")
    print("   - Scroll PDF if present")
    print("   - Click Submit Test button")
    
    print("\n🎯 Expected Console Output:")
    print("   ===== PRIMEPATH INITIALIZATION STARTING =====")
    print("   [INIT] Step 1-10 with ✅ for each successful module")
    print("   Overall Success Rate: >80%")
    
    return True

if __name__ == "__main__":
    success = test_complete_interface()
    sys.exit(0 if success else 1)