#!/usr/bin/env python
"""
Comprehensive test for audio playback system.
Tests the audio file relationships, URLs, and rendering.
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client, RequestFactory
from django.urls import reverse
from django.template.loader import get_template
from placement_test.models import Exam, Question, AudioFile, StudentSession
from placement_test.views import get_audio


def test_audio_models():
    """Test audio model relationships."""
    print("\n" + "="*60)
    print("TESTING AUDIO MODEL RELATIONSHIPS")
    print("="*60)
    
    try:
        # Get an exam with audio files
        exam = Exam.objects.filter(audio_files__isnull=False).first()
        
        if not exam:
            print("  ⚠️ No exam with audio files found")
            return False
        
        print(f"\nExam: {exam.name}")
        audio_files = exam.audio_files.all()
        print(f"Audio files: {audio_files.count()}")
        
        for audio in audio_files:
            print(f"\n  Audio ID: {audio.id}")
            print(f"  Name: {audio.name}")
            print(f"  File: {audio.audio_file.name if audio.audio_file else 'NO FILE'}")
            print(f"  Questions: {audio.start_question}-{audio.end_question}")
            
            # Check if audio file actually exists
            if audio.audio_file:
                file_exists = os.path.exists(audio.audio_file.path)
                print(f"  File exists on disk: {'YES' if file_exists else 'NO'}")
            
            # Check question assignments
            questions_with_audio = Question.objects.filter(
                exam=exam,
                audio_file=audio
            )
            print(f"  Assigned to {questions_with_audio.count()} questions")
            
            if questions_with_audio.exists():
                q_nums = [q.question_number for q in questions_with_audio]
                print(f"    Question numbers: {q_nums}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_audio_urls():
    """Test audio URL generation and access."""
    print("\n" + "="*60)
    print("TESTING AUDIO URL GENERATION")
    print("="*60)
    
    try:
        client = Client()
        
        # Get an audio file
        audio = AudioFile.objects.filter(audio_file__isnull=False).first()
        
        if not audio:
            print("  ⚠️ No audio files found")
            return False
        
        print(f"\nTesting audio ID: {audio.id}")
        
        # Test URL generation
        url = reverse('PlacementTest:get_audio', args=[audio.id])
        print(f"Generated URL: {url}")
        
        # Test accessing the URL
        response = client.get(url)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Content-Type: {response.get('Content-Type', 'Not set')}")
            print(f"Content-Length: {response.get('Content-Length', 'Not set')}")
            print("✅ Audio URL working correctly")
            return True
        else:
            print(f"❌ Audio URL failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_audio_template_rendering():
    """Test audio player template rendering."""
    print("\n" + "="*60)
    print("TESTING AUDIO PLAYER TEMPLATE")
    print("="*60)
    
    try:
        # Get audio file with question
        question = Question.objects.filter(audio_file__isnull=False).first()
        
        if not question:
            print("  ⚠️ No questions with audio found")
            return False
        
        audio_file = question.audio_file
        print(f"\nQuestion {question.question_number} has audio: {audio_file.name}")
        
        # Load and render the audio player template
        template = get_template('components/placement_test/audio_player.html')
        context = {
            'audio_file': audio_file
        }
        
        html = template.render(context)
        
        # Check for required elements
        checks = [
            (f'id="audio-element-{audio_file.id}"', 'Audio element'),
            (f'id="audio-play-{audio_file.id}"', 'Play button'),
            (f'data-audio-play="{audio_file.id}"', 'Audio play data attribute'),
            ('audio-icon', 'Audio icon'),
            ('/api/PlacementTest/audio/', 'Audio URL'),
        ]
        
        all_passed = True
        for check, description in checks:
            if check in html:
                print(f"  ✅ {description}: Found")
            else:
                print(f"  ❌ {description}: Not found")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_student_interface_audio():
    """Test audio in student interface."""
    print("\n" + "="*60)
    print("TESTING STUDENT INTERFACE AUDIO")
    print("="*60)
    
    try:
        client = Client()
        
        # Get a session with audio questions
        session = StudentSession.objects.filter(
            exam__questions__audio_file__isnull=False
        ).first()
        
        if not session:
            print("  ⚠️ No sessions with audio questions found")
            return False
        
        print(f"\nSession: {session.id}")
        print(f"Exam: {session.exam.name}")
        
        # Get the student test page
        url = reverse('PlacementTest:take_test', args=[session.id])
        response = client.get(url)
        
        if response.status_code == 200:
            print(f"Student interface loaded: OK")
            
            # Check if audio player script is loaded
            content = str(response.content)
            checks = [
                ('audio-player.js', 'Audio player script'),
                ('AudioPlayer', 'AudioPlayer class'),
                ('audio-element-', 'Audio elements'),
                ('data-audio-play', 'Audio play buttons'),
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"  ✅ {description}: Found")
                else:
                    print(f"  ❌ {description}: Not found")
            
            return True
        else:
            print(f"❌ Student interface failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_javascript_initialization():
    """Test JavaScript audio player initialization."""
    print("\n" + "="*60)
    print("TESTING JAVASCRIPT INITIALIZATION")
    print("="*60)
    
    print("\nChecking JavaScript components:")
    
    js_files = [
        'static/js/modules/audio-player.js',
        'static/js/utils/event-delegation.js',
        'static/js/modules/base-module.js',
    ]
    
    all_exist = True
    for js_file in js_files:
        full_path = os.path.join(os.path.dirname(__file__), js_file)
        if os.path.exists(full_path):
            print(f"  ✅ {js_file}: Exists")
            
            # Check for specific patterns
            with open(full_path, 'r') as f:
                content = f.read()
                
            if 'audio-player.js' in js_file:
                if 'AudioPlayer' in content and 'play(' in content:
                    print("    - AudioPlayer class defined")
                    print("    - play() method defined")
                else:
                    print("    ❌ Missing AudioPlayer class or play method")
                    all_exist = False
        else:
            print(f"  ❌ {js_file}: Not found")
            all_exist = False
    
    return all_exist


def run_all_tests():
    """Run all audio system tests."""
    print("\n" + "#"*60)
    print("# AUDIO SYSTEM COMPREHENSIVE TEST")
    print("#"*60)
    
    results = []
    
    tests = [
        ("Model Relationships", test_audio_models),
        ("URL Generation", test_audio_urls),
        ("Template Rendering", test_audio_template_rendering),
        ("Student Interface", test_student_interface_audio),
        ("JavaScript Files", test_javascript_initialization),
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Audio system is working correctly.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Audio system needs attention.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)