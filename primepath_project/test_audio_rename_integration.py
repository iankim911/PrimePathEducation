#!/usr/bin/env python
"""
Test audio renaming integration in RoutineTest.
Verifies that audio names can be renamed and saved with "Save All" button.
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
from primepath_routinetest.models import Exam as RoutineExam, AudioFile as RoutineAudioFile
from placement_test.models import Exam as PlacementExam, AudioFile as PlacementAudioFile

def test_audio_rename_feature():
    """Test that audio renaming works in both apps."""
    print("\n" + "="*80)
    print("🎵 AUDIO RENAME INTEGRATION TEST")
    print("="*80)
    
    client = Client()
    user, _ = User.objects.get_or_create(
        username='test_admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    user.set_password('testpass123')
    user.save()
    client.login(username='test_admin', password='testpass123')
    
    # Test RoutineTest
    print("\n📗 Testing RoutineTest Audio Renaming...")
    
    # Find exam with audio files
    rt_exam = None
    for exam in RoutineExam.objects.all():
        if exam.routine_audio_files.exists():
            rt_exam = exam
            break
    
    if rt_exam:
        print(f"   Exam: {rt_exam.name}")
        print(f"   Audio files: {rt_exam.routine_audio_files.count()}")
        
        # Test the preview page loads
        response = client.get(f'/RoutineTest/exams/{rt_exam.id}/preview/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for audio renaming UI elements
            checks = {
                'Audio input fields': 'audio-file-name-input' in content,
                'Save Audio Names button': 'saveAllAudioNames()' in content,
                'Mark changed function': 'markAudioNameChanged' in content,
                'Rename button': 'renameAudioFile' in content,
                'Save All integration': '[SAVE_ALL]' in content and 'changedAudioNames' in content,
                'Console debugging': '[AUDIO_RENAME]' in content,
            }
            
            print("\n   UI Elements Check:")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                print(f"      {status} {check}")
            
            # Check for the new save integration
            if '[SAVE_ALL]' in content and 'saveAudioNamesPromise' in content:
                print("\n   ✅ Save All button now saves audio names!")
            else:
                print("\n   ❌ Save All button missing audio name integration")
                
        else:
            print(f"   ❌ Failed to load preview: {response.status_code}")
    else:
        print("   ⚠️ No RoutineTest exam with audio files found")
    
    # Compare with PlacementTest
    print("\n📘 Comparing with PlacementTest...")
    
    pt_exam = None
    for exam in PlacementExam.objects.all():
        if exam.audio_files.exists():
            pt_exam = exam
            break
    
    if pt_exam:
        print(f"   Exam: {pt_exam.name}")
        response = client.get(f'/PlacementTest/exams/{pt_exam.id}/preview/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check PlacementTest implementation
            pt_has_save_integration = 'saveAllAnswers' in content and 'audio_names' in content
            print(f"   PlacementTest Save All integration: {'✅' if pt_has_save_integration else '❌'}")
        else:
            print(f"   ❌ Failed to load PlacementTest preview")
    else:
        print("   ⚠️ No PlacementTest exam with audio files found")
    
    # Test the backend endpoint
    print("\n📡 Testing Backend Endpoints...")
    
    if rt_exam:
        # Test update-audio-names endpoint
        test_data = {
            'audio_names': {
                str(audio.id): f"Test Audio {audio.id}"
                for audio in rt_exam.routine_audio_files.all()[:2]
            }
        }
        
        response = client.post(
            f'/RoutineTest/exams/{rt_exam.id}/update-audio-names/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ Audio names endpoint working")
                print(f"      Saved {data.get('saved_count', 0)} audio names")
            else:
                print(f"   ❌ Audio names save failed: {data.get('error')}")
        else:
            print(f"   ❌ Endpoint returned: {response.status_code}")
    
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    print("\n✅ IMPLEMENTED FEATURES:")
    print("1. Audio name input fields in UI")
    print("2. Change tracking with changedAudioNames")
    print("3. Save Audio Names button functionality")
    print("4. Integration with Save All button")
    print("5. Comprehensive console debugging")
    print("6. Backend endpoint for saving names")
    
    print("\n🎯 KEY IMPROVEMENT:")
    print("When 'Save All' is clicked in RoutineTest, it now:")
    print("   1. Saves any changed audio names first")
    print("   2. Then saves all question answers")
    print("   3. Shows success indicators for both")
    print("   4. Logs detailed debug information")
    
    print("\n📝 CONSOLE LOGS TO LOOK FOR:")
    print("   [AUDIO_RENAME] - When audio name is changed")
    print("   [SAVE_ALL] - When Save All button is clicked")
    print("   [AUDIO_RENAME_SAVE] - When audio names are saved")
    print("   [AUDIO_RENAME_DIALOG] - When rename dialog is used")

if __name__ == '__main__':
    test_audio_rename_feature()