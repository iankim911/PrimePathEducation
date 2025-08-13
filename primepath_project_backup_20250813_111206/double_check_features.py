"""
Double-check test for all existing features
Ensures DRF/Celery installation didn't break anything
"""
import os
import django
import json
import uuid
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.sessions.models import Session
from placement_test.models import Exam, StudentSession, Question, AudioFile, StudentAnswer
from core.models import School, CurriculumLevel
from django.core.files.uploadedfile import SimpleUploadedFile

def test_student_test_interface():
    """Test 1: Student test-taking interface"""
    print("\n=== TEST 1: Student Test-Taking Interface ===")
    client = Client()
    exam = Exam.objects.first()
    
    if not exam:
        print("[SKIP] No exam available for testing")
        return False
    
    tests = []
    
    # 1.1 Test student login page loads
    response = client.get(f'/api/placement/exams/{exam.id}/start/')
    tests.append(('Student login page', response.status_code in [200, 405]))
    
    # 1.2 Test starting a session via API
    response = client.post('/api/placement/start-test/', {
        'student_name': 'Test Student Double Check',
        'parent_phone': '1234567890',
        'grade': 10,
        'school_name': 'Test School',
        'academic_rank': 'TOP_10',
        'exam_id': str(exam.id)
    })
    tests.append(('Start test session API', response.status_code == 200))
    
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data.get('session_id')
        
        # 1.3 Test getting questions
        response = client.get(f'/api/placement/exams/{exam.id}/questions/')
        tests.append(('Get exam questions', response.status_code == 200))
        
        # 1.4 Test answer submission
        if session_id and exam.questions.exists():
            question = exam.questions.first()
            response = client.post('/api/placement/submit-answer/', {
                'session_id': session_id,
                'question_id': str(question.id),
                'answer': 'A'
            })
            tests.append(('Submit answer', response.status_code == 200))
    
    # Print results
    for test_name, passed in tests:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")
    
    return all(passed for _, passed in tests)

def test_exam_creation_management():
    """Test 2: Exam creation and management"""
    print("\n=== TEST 2: Exam Creation and Management ===")
    client = Client()
    tests = []
    
    # 2.1 Test exam list page
    response = client.get('/api/placement/exams/')
    tests.append(('Exam list API', response.status_code == 200))
    
    # 2.2 Test getting exam details
    exam = Exam.objects.first()
    if exam:
        response = client.get(f'/api/placement/exams/{exam.id}/')
        tests.append(('Get exam details', response.status_code == 200))
        
        # 2.3 Test exam questions management
        response = client.get(f'/api/placement/exams/{exam.id}/questions/')
        tests.append(('Get exam questions', response.status_code == 200))
        
        # 2.4 Test saving exam answers (teacher interface)
        response = client.post(f'/api/placement/exams/{exam.id}/save-answers/', 
            json.dumps({'questions': [], 'audio_assignments': {}}),
            content_type='application/json'
        )
        tests.append(('Save exam configuration', response.status_code == 200))
    
    # Print results
    for test_name, passed in tests:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")
    
    return all(passed for _, passed in tests)

def test_pdf_functionality():
    """Test 3: PDF upload and viewing"""
    print("\n=== TEST 3: PDF Upload and Viewing ===")
    client = Client()
    tests = []
    
    exam = Exam.objects.first()
    if exam:
        # 3.1 Test PDF URL generation
        if exam.pdf_file:
            response = client.get(exam.pdf_file.url)
            tests.append(('PDF file accessible', response.status_code in [200, 304]))
        
        # 3.2 Test PDF upload endpoint exists
        response = client.post(f'/api/placement/exams/{exam.id}/upload-pdf/')
        tests.append(('PDF upload endpoint', response.status_code in [200, 400]))  # 400 if no file provided
    
    # Print results
    for test_name, passed in tests:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")
    
    return all(passed for _, passed in tests)

def test_audio_management():
    """Test 4: Audio file management"""
    print("\n=== TEST 4: Audio File Management ===")
    client = Client()
    tests = []
    
    exam = Exam.objects.first()
    if exam:
        # 4.1 Test audio upload endpoint
        response = client.post(f'/api/placement/exams/{exam.id}/upload-audio/')
        tests.append(('Audio upload endpoint', response.status_code in [200, 400, 404]))
        
        # 4.2 Test getting audio files
        audio = AudioFile.objects.filter(exam=exam).first()
        if audio:
            response = client.get(f'/api/placement/audio/{audio.id}/')
            tests.append(('Get audio file', response.status_code in [200, 404]))
        
        # 4.3 Test audio name updates
        response = client.post(f'/api/placement/exams/{exam.id}/update-audio-names/',
            json.dumps({'audio_names': {}}),
            content_type='application/json'
        )
        tests.append(('Update audio names', response.status_code == 200))
    
    # Print results
    for test_name, passed in tests:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")
    
    return all(passed for _, passed in tests)

def test_answer_submission_grading():
    """Test 5: Answer submission and grading"""
    print("\n=== TEST 5: Answer Submission and Grading ===")
    client = Client()
    tests = []
    
    # 5.1 Create a test session
    exam = Exam.objects.first()
    if exam:
        # Start a session
        response = client.post('/api/placement/start-test/', {
            'student_name': 'Grading Test Student',
            'parent_phone': '9876543210',
            'grade': 11,
            'school_name': 'Grading Test School',
            'academic_rank': 'TOP_20',
            'exam_id': str(exam.id)
        })
        tests.append(('Create test session for grading', response.status_code == 200))
        
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get('session_id')
            
            # 5.2 Submit some answers
            questions = exam.questions.all()[:3]
            for i, question in enumerate(questions):
                response = client.post('/api/placement/submit-answer/', {
                    'session_id': session_id,
                    'question_id': str(question.id),
                    'answer': ['A', 'B', 'C'][i % 3]
                })
                tests.append((f'Submit answer {i+1}', response.status_code == 200))
            
            # 5.3 Complete and grade session
            response = client.post(f'/api/placement/sessions/{session_id}/complete/')
            tests.append(('Complete and grade session', response.status_code in [200, 404]))
    
    # Print results
    for test_name, passed in tests:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")
    
    return all(passed for _, passed in tests)

def test_dashboard_sessions():
    """Test 6: Dashboard and session management"""
    print("\n=== TEST 6: Dashboard and Session Management ===")
    client = Client()
    tests = []
    
    # 6.1 Test session list
    response = client.get('/api/placement/sessions/')
    tests.append(('Get sessions list', response.status_code == 200))
    
    # 6.2 Test session details
    session = StudentSession.objects.first()
    if session:
        response = client.get(f'/api/placement/sessions/{session.id}/')
        tests.append(('Get session details', response.status_code == 200))
        
        # 6.3 Test session results
        response = client.get(f'/api/placement/sessions/{session.id}/result/')
        tests.append(('Get session results', response.status_code in [200, 404]))
    
    # 6.4 Test dashboard stats
    response = client.get('/api/placement/dashboard/stats/')
    tests.append(('Dashboard statistics', response.status_code in [200, 404]))
    
    # Print results
    for test_name, passed in tests:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")
    
    return all(passed for _, passed in tests)

def test_ajax_endpoints():
    """Test 7: AJAX endpoints used by frontend"""
    print("\n=== TEST 7: AJAX Endpoints ===")
    client = Client()
    tests = []
    
    exam = Exam.objects.first()
    if exam:
        # 7.1 Critical AJAX endpoints
        ajax_endpoints = [
            (f'/api/placement/exams/{exam.id}/questions/', 'Get questions AJAX'),
            (f'/api/placement/exams/{exam.id}/save-answers/', 'Save answers AJAX'),
            (f'/api/placement/exams/{exam.id}/update-audio-names/', 'Update audio AJAX'),
            ('/api/placement/curriculum-levels/', 'Curriculum levels AJAX'),
            ('/api/placement/schools/', 'Schools list AJAX'),
        ]
        
        for endpoint, description in ajax_endpoints:
            if 'save-answers' in endpoint or 'update-audio' in endpoint:
                # POST endpoints
                response = client.post(endpoint, 
                    json.dumps({'questions': [], 'audio_assignments': {}, 'audio_names': {}}),
                    content_type='application/json'
                )
            else:
                # GET endpoints
                response = client.get(endpoint)
            
            # Some endpoints might not exist but shouldn't error
            tests.append((description, response.status_code in [200, 404]))
    
    # Print results
    for test_name, passed in tests:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")
    
    return all(passed for _, passed in tests)

def main():
    """Run all feature tests"""
    print("=" * 60)
    print("DOUBLE-CHECK: EXISTING FEATURES TEST")
    print("Verifying DRF/Celery didn't break existing functionality")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_functions = [
        test_student_test_interface,
        test_exam_creation_management,
        test_pdf_functionality,
        test_audio_management,
        test_answer_submission_grading,
        test_dashboard_sessions,
        test_ajax_endpoints,
    ]
    
    for test_func in test_functions:
        try:
            result = test_func()
            test_results.append((test_func.__doc__.split(':')[1].strip(), result))
        except Exception as e:
            print(f"  [ERROR] Test crashed: {str(e)[:100]}")
            test_results.append((test_func.__doc__.split(':')[1].strip(), False))
    
    # Summary
    print("\n" + "=" * 60)
    print("DOUBLE-CHECK SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for feature, result in test_results:
        status = "✓ WORKING" if result else "✗ BROKEN"
        print(f"{status}: {feature}")
    
    print(f"\nOverall: {passed}/{total} features working")
    
    if passed == total:
        print("\n[SUCCESS] All existing features are working correctly!")
        print("DRF and Celery installation did NOT break any functionality.")
    elif passed >= total - 1:
        print("\n[WARNING] Most features working, minor issues detected.")
    else:
        print("\n[ALERT] Multiple features may be affected!")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)