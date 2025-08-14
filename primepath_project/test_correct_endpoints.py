"""
Test existing features with CORRECT endpoint URLs
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from placement_test.models import Exam, StudentSession, Question, AudioFile
from core.models import School

def test_critical_features():
    """Test all critical features are working"""
    client = Client()
    print("\n" + "=" * 60)
    print("TESTING CRITICAL FEATURES WITH CORRECT ENDPOINTS")
    print("=" * 60)
    
    results = []
    
    # Get test data
    exam = Exam.objects.first()
    session = StudentSession.objects.first()
    
    if not exam:
        print("[ERROR] No exam found for testing")
        return False
    
    print(f"\nUsing exam: {exam.name} (ID: {exam.id})")
    if session:
        print(f"Using session: {session.student_name} (ID: {session.id})")
    
    # 1. EXAM MANAGEMENT (Traditional Django endpoints)
    print("\n1. EXAM MANAGEMENT FEATURES:")
    
    # 1.1 List exams
    response = client.get('/api/PlacementTest/exams/')
    results.append(('List exams', response.status_code == 200))
    print(f"   List exams: {response.status_code}")
    
    # 1.2 Get exam details
    response = client.get(f'/api/PlacementTest/exams/{exam.id}/')
    results.append(('Get exam details', response.status_code == 200))
    print(f"   Get exam details: {response.status_code}")
    
    # 1.3 Get exam questions
    response = client.get(f'/api/PlacementTest/exams/{exam.id}/questions/')
    results.append(('Get exam questions', response.status_code == 200))
    print(f"   Get exam questions: {response.status_code}")
    
    # 1.4 Save exam answers (teacher interface)
    response = client.post(f'/api/PlacementTest/exams/{exam.id}/save-answers/',
        json.dumps({'questions': [], 'audio_assignments': {}}),
        content_type='application/json'
    )
    results.append(('Save exam configuration', response.status_code == 200))
    print(f"   Save exam configuration: {response.status_code}")
    
    # 2. STUDENT TEST-TAKING
    print("\n2. STUDENT TEST-TAKING FEATURES:")
    
    # 2.1 Start test
    response = client.post('/api/PlacementTest/start/', {
        'student_name': 'Test Student Final Check',
        'parent_phone': '5555551234',
        'grade': 10,
        'school_name': 'Test School',
        'academic_rank': 'TOP_10',
        'exam_id': str(exam.id)
    })
    results.append(('Start test session', response.status_code == 200))
    print(f"   Start test session: {response.status_code}")
    
    if response.status_code == 200:
        new_session_data = response.json()
        new_session_id = new_session_data.get('session_id')
        
        # 2.2 Submit answer
        if new_session_id and exam.questions.exists():
            question = exam.questions.first()
            response = client.post(f'/api/PlacementTest/session/{new_session_id}/submit/', {
                'question_id': str(question.id),
                'answer': 'B'
            })
            results.append(('Submit answer', response.status_code == 200))
            print(f"   Submit answer: {response.status_code}")
    
    # 3. SESSION MANAGEMENT
    print("\n3. SESSION MANAGEMENT FEATURES:")
    
    # 3.1 List sessions
    response = client.get('/api/PlacementTest/sessions/')
    results.append(('List sessions', response.status_code == 200))
    print(f"   List sessions: {response.status_code}")
    
    # 3.2 Get session details (if session exists)
    if session:
        response = client.get(f'/api/PlacementTest/sessions/{session.id}/')
        results.append(('Get session details', response.status_code == 200))
        print(f"   Get session details: {response.status_code}")
    
    # 4. AUDIO MANAGEMENT
    print("\n4. AUDIO MANAGEMENT FEATURES:")
    
    # 4.1 Get audio (if exists)
    audio = AudioFile.objects.filter(exam=exam).first()
    if audio:
        response = client.get(f'/api/PlacementTest/audio/{audio.id}/')
        results.append(('Get audio file', response.status_code == 200))
        print(f"   Get audio file: {response.status_code}")
    
    # 4.2 Update audio names
    response = client.post(f'/api/PlacementTest/exams/{exam.id}/update-audio-names/',
        json.dumps({'audio_names': {}}),
        content_type='application/json'
    )
    results.append(('Update audio names', response.status_code == 200))
    print(f"   Update audio names: {response.status_code}")
    
    # 5. PDF FUNCTIONALITY
    print("\n5. PDF FUNCTIONALITY:")
    
    # 5.1 Check if PDF accessible
    if exam.pdf_file:
        response = client.get(exam.pdf_file.url)
        results.append(('Access PDF file', response.status_code in [200, 304]))
        print(f"   Access PDF file: {response.status_code}")
    
    # 6. NEW DRF API ENDPOINTS (should also work)
    print("\n6. NEW DRF API ENDPOINTS:")
    
    # 6.1 DRF Exams endpoint
    response = client.get('/api/v1/exams/')
    results.append(('DRF Exams API', response.status_code == 200))
    print(f"   DRF Exams API: {response.status_code}")
    
    # 6.2 DRF Sessions endpoint
    response = client.get('/api/v1/sessions/')
    results.append(('DRF Sessions API', response.status_code == 200))
    print(f"   DRF Sessions API: {response.status_code}")
    
    # 6.3 DRF Schools endpoint
    response = client.get('/api/v1/schools/')
    results.append(('DRF Schools API', response.status_code == 200))
    print(f"   DRF Schools API: {response.status_code}")
    
    # SUMMARY
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] ALL FEATURES WORKING!")
        print("DRF and Celery installation did NOT affect any existing functionality.")
    elif passed >= total * 0.9:
        print("\n[MOSTLY OK] Most features working correctly.")
        print("Minor issues detected but core functionality preserved.")
    elif passed >= total * 0.7:
        print("\n[WARNING] Some features may have issues.")
    else:
        print("\n[CRITICAL] Multiple features affected!")
    
    return passed == total

if __name__ == "__main__":
    success = test_critical_features()
    exit(0 if success else 1)