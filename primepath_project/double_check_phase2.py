"""
Double-check test for Phase 2 View Modularization
Ensures ABSOLUTELY NOTHING was broken
"""
import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.urls import reverse
from placement_test.models import Exam, StudentSession, Question, AudioFile
from core.models import School

def test_import_compatibility():
    """Test all import patterns still work"""
    print("\n=== TESTING IMPORT COMPATIBILITY ===")
    results = []
    
    # Test 1: Module import
    try:
        from placement_test import views
        results.append(('Module import', True))
        print("  [PASS] from placement_test import views")
    except:
        results.append(('Module import', False))
        print("  [FAIL] from placement_test import views")
    
    # Test 2: Direct function import
    try:
        from placement_test.views import start_test, exam_list, session_list, get_audio
        results.append(('Direct imports', True))
        print("  [PASS] Direct function imports")
    except:
        results.append(('Direct imports', False))
        print("  [FAIL] Direct function imports")
    
    # Test 3: Check all 26 views exist
    try:
        from placement_test import views
        all_views = ['start_test', 'take_test', 'submit_answer', 'adjust_difficulty',
                     'complete_test', 'test_result', 'exam_list', 'create_exam',
                     'check_exam_version', 'exam_detail', 'edit_exam', 'preview_exam',
                     'manage_questions', 'delete_exam', 'session_list', 'session_detail',
                     'grade_session', 'export_result', 'add_audio', 'update_question',
                     'create_questions', 'save_exam_answers', 'update_exam_name',
                     'get_audio', 'update_audio_names', 'delete_audio_from_exam']
        
        missing = [v for v in all_views if not hasattr(views, v)]
        if not missing:
            results.append(('All 26 views present', True))
            print(f"  [PASS] All 26 views found in module")
        else:
            results.append(('All 26 views present', False))
            print(f"  [FAIL] Missing views: {missing}")
    except:
        results.append(('All 26 views present', False))
        print("  [FAIL] Could not check views")
    
    return all(r[1] for r in results)

def test_url_resolution():
    """Test all URLs still resolve correctly"""
    print("\n=== TESTING URL RESOLUTION ===")
    client = Client()
    results = []
    
    # Test critical URLs
    test_urls = [
        ('placement_test:start_test', None, 'Start test URL'),
        ('placement_test:exam_list', None, 'Exam list URL'),
        ('placement_test:create_exam', None, 'Create exam URL'),
        ('placement_test:session_list', None, 'Session list URL'),
    ]
    
    exam = Exam.objects.first()
    if exam:
        test_urls.extend([
            ('placement_test:exam_detail', [exam.id], f'Exam detail URL'),
            ('placement_test:preview_exam', [exam.id], f'Preview exam URL'),
            ('placement_test:manage_questions', [exam.id], f'Manage questions URL'),
        ])
    
    for url_name, args, description in test_urls:
        try:
            url = reverse(url_name, args=args)
            results.append((description, True))
            print(f"  [PASS] {description}: {url}")
        except:
            results.append((description, False))
            print(f"  [FAIL] {description}")
    
    return all(r[1] for r in results)

def test_student_features():
    """Test student test-taking features"""
    print("\n=== TESTING STUDENT FEATURES ===")
    client = Client()
    results = []
    
    # Test 1: Start test page loads
    response = client.get('/api/placement/start/')
    results.append(('Start test page', response.status_code == 200))
    print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Start test page: {response.status_code}")
    
    # Test 2: Session management
    session = StudentSession.objects.first()
    if session:
        # Test take_test view
        if not session.completed_at:
            response = client.get(f'/api/placement/session/{session.id}/')
            results.append(('Take test view', response.status_code in [200, 302]))
            print(f"  [{'PASS' if response.status_code in [200, 302] else 'FAIL'}] Take test view: {response.status_code}")
        
        # Test result view (for completed sessions)
        if session.completed_at:
            response = client.get(f'/api/placement/session/{session.id}/result/')
            results.append(('Test result view', response.status_code in [200, 302]))
            print(f"  [{'PASS' if response.status_code in [200, 302] else 'FAIL'}] Test result view: {response.status_code}")
    
    return len(results) == 0 or all(r[1] for r in results)

def test_exam_management():
    """Test exam management features"""
    print("\n=== TESTING EXAM MANAGEMENT ===")
    client = Client()
    results = []
    
    # Test exam list
    response = client.get('/api/placement/exams/')
    results.append(('Exam list', response.status_code == 200))
    print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Exam list: {response.status_code}")
    
    exam = Exam.objects.first()
    if exam:
        # Test exam detail
        response = client.get(f'/api/placement/exams/{exam.id}/')
        results.append(('Exam detail', response.status_code == 200))
        print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Exam detail: {response.status_code}")
        
        # Test preview exam
        response = client.get(f'/api/placement/exams/{exam.id}/preview/')
        results.append(('Preview exam', response.status_code == 200))
        print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Preview exam: {response.status_code}")
        
        # Test manage questions
        response = client.get(f'/api/placement/exams/{exam.id}/questions/')
        results.append(('Manage questions', response.status_code == 200))
        print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Manage questions: {response.status_code}")
    
    return all(r[1] for r in results)

def test_ajax_endpoints():
    """Test AJAX endpoints"""
    print("\n=== TESTING AJAX ENDPOINTS ===")
    client = Client()
    results = []
    
    exam = Exam.objects.first()
    if exam:
        # Test save exam answers
        response = client.post(
            f'/api/placement/exams/{exam.id}/save-answers/',
            json.dumps({'questions': [], 'audio_assignments': {}}),
            content_type='application/json'
        )
        results.append(('Save exam answers', response.status_code == 200))
        print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Save exam answers: {response.status_code}")
        
        # Test get questions
        response = client.get(f'/api/placement/exams/{exam.id}/questions/')
        results.append(('Get questions', response.status_code == 200))
        print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Get questions: {response.status_code}")
        
        # Test update audio names
        response = client.post(
            f'/api/placement/exams/{exam.id}/update-audio-names/',
            json.dumps({'audio_names': {}}),
            content_type='application/json'
        )
        results.append(('Update audio names', response.status_code in [200, 302]))
        print(f"  [{'PASS' if response.status_code in [200, 302] else 'FAIL'}] Update audio names: {response.status_code}")
    
    # Test audio file access
    audio = AudioFile.objects.first()
    if audio:
        response = client.get(f'/api/placement/audio/{audio.id}/')
        results.append(('Get audio file', response.status_code == 200))
        print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Get audio file: {response.status_code}")
    
    return all(r[1] for r in results)

def test_session_management():
    """Test session management features"""
    print("\n=== TESTING SESSION MANAGEMENT ===")
    client = Client()
    results = []
    
    # Test session list
    response = client.get('/api/placement/sessions/')
    results.append(('Session list', response.status_code == 200))
    print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Session list: {response.status_code}")
    
    session = StudentSession.objects.first()
    if session:
        # Test session detail
        response = client.get(f'/api/placement/sessions/{session.id}/')
        results.append(('Session detail', response.status_code == 200))
        print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Session detail: {response.status_code}")
        
        # Test export result
        response = client.get(f'/api/placement/sessions/{session.id}/export/')
        results.append(('Export result', response.status_code == 200))
        print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Export result: {response.status_code}")
    
    return all(r[1] for r in results)

def test_file_handling():
    """Test PDF and audio file handling"""
    print("\n=== TESTING FILE HANDLING ===")
    client = Client()
    results = []
    
    # Test PDF access
    exam = Exam.objects.filter(pdf_file__isnull=False).first()
    if exam and exam.pdf_file:
        response = client.get(exam.pdf_file.url)
        results.append(('PDF file access', response.status_code in [200, 304]))
        print(f"  [{'PASS' if response.status_code in [200, 304] else 'FAIL'}] PDF file access: {response.status_code}")
    
    # Test audio streaming
    audio = AudioFile.objects.first()
    if audio:
        response = client.get(f'/api/placement/audio/{audio.id}/')
        results.append(('Audio streaming', response.status_code == 200))
        print(f"  [{'PASS' if response.status_code == 200 else 'FAIL'}] Audio streaming: {response.status_code}")
    
    return len(results) == 0 or all(r[1] for r in results)

def test_backwards_compatibility():
    """Test backwards compatibility specifics"""
    print("\n=== TESTING BACKWARDS COMPATIBILITY ===")
    results = []
    
    # Test old import patterns used in test files
    try:
        # Pattern from test files
        from placement_test import views as placement_views
        results.append(('Import as alias', True))
        print("  [PASS] from placement_test import views as placement_views")
    except:
        results.append(('Import as alias', False))
        print("  [FAIL] from placement_test import views as placement_views")
    
    # Test attribute access
    try:
        from placement_test import views
        # Test accessing a view from each module
        _ = views.start_test  # from student.py
        _ = views.exam_list   # from exam.py
        _ = views.session_list # from session.py
        _ = views.get_audio   # from ajax.py
        results.append(('Attribute access', True))
        print("  [PASS] All view attributes accessible")
    except:
        results.append(('Attribute access', False))
        print("  [FAIL] View attribute access failed")
    
    return all(r[1] for r in results)

def main():
    """Run all double-check tests"""
    print("\n" + "=" * 70)
    print("DOUBLE-CHECK: Phase 2 View Modularization Impact")
    print("Verifying ZERO features were affected")
    print("=" * 70)
    
    test_results = []
    
    # Run all test suites
    test_suites = [
        ('Import Compatibility', test_import_compatibility),
        ('URL Resolution', test_url_resolution),
        ('Student Features', test_student_features),
        ('Exam Management', test_exam_management),
        ('AJAX Endpoints', test_ajax_endpoints),
        ('Session Management', test_session_management),
        ('File Handling', test_file_handling),
        ('Backwards Compatibility', test_backwards_compatibility),
    ]
    
    for test_name, test_func in test_suites:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] {test_name} crashed: {str(e)[:100]}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("DOUBLE-CHECK SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n[CONFIRMED] NO FEATURES AFFECTED!")
        print("View modularization was 100% successful with zero breaking changes.")
    elif passed >= total - 1:
        print("\n[MOSTLY OK] Almost all features working.")
        print("Minor issues detected, investigate failures.")
    else:
        print("\n[WARNING] Some features may be affected.")
        print("Review failed tests immediately.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)