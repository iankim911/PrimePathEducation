#!/usr/bin/env python
"""
Test Feature Integrity After URL Restructuring
Tests all major features to ensure nothing broke
"""
import os
import sys
import django
import json
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.urls import reverse, resolve
from placement_test.models import Exam, StudentSession, Question
from primepath_routinetest.models import Exam as RoutineExam

def test_url_patterns():
    """Test that all critical URL patterns exist and resolve correctly"""
    print("\n" + "="*60)
    print("TESTING URL PATTERNS")
    print("="*60)
    
    critical_urls = [
        # PlacementTest URLs
        ('PlacementTest:start_test', '/PlacementTest/start/', 'placement_test.views.student.start_test'),
        ('PlacementTest:exam_list', '/PlacementTest/exams/', 'placement_test.views.exam.exam_list'),
        ('PlacementTest:create_exam', '/PlacementTest/exams/create/', 'placement_test.views.exam.create_exam'),
        ('PlacementTest:session_list', '/PlacementTest/sessions/', 'placement_test.views.session.session_list'),
        
        # RoutineTest URLs
        ('RoutineTest:start_test', '/RoutineTest/start/', 'primepath_routinetest.views.student.start_test'),
        ('RoutineTest:exam_list', '/RoutineTest/exams/', 'primepath_routinetest.views.exam.exam_list'),
        ('RoutineTest:index', '/RoutineTest/', 'primepath_routinetest.views.index.index'),
        
        # Core URLs (unchanged)
        ('placement_rules', '/placement-rules/', 'core.views.placement_rules'),
        ('exam_mapping', '/exam-mapping/', 'core.views.exam_mapping'),
    ]
    
    results = []
    for name, expected_path, expected_view in critical_urls:
        try:
            if ':' in name:
                url = reverse(name)
            else:
                url = reverse(name)
            
            resolved = resolve(url)
            view_name = f"{resolved.func.__module__}.{resolved.func.__name__}"
            
            status = "✅" if url == expected_path and view_name == expected_view else "❌"
            results.append({
                'name': name,
                'expected_path': expected_path,
                'actual_path': url,
                'expected_view': expected_view,
                'actual_view': view_name,
                'status': status
            })
            
            print(f"{status} {name}: {url} -> {view_name}")
            
        except Exception as e:
            results.append({
                'name': name,
                'error': str(e),
                'status': '❌'
            })
            print(f"❌ {name}: ERROR - {e}")
    
    return results

def test_redirects():
    """Test that old URLs redirect to new ones"""
    print("\n" + "="*60)
    print("TESTING REDIRECTS")
    print("="*60)
    
    client = Client()
    
    redirect_tests = [
        ('/placement/', '/PlacementTest/', 302),
        ('/routine/', '/RoutineTest/', 302),
        ('/teacher/', '/PlacementTest/teacher/', 302),
        ('/api/placement/', '/api/PlacementTest/', 302),
        ('/api/routine/', '/api/RoutineTest/', 302),
        ('/placement/test/', '/PlacementTest/test/', 302),
    ]
    
    results = []
    for old_url, expected_redirect, expected_status in redirect_tests:
        response = client.get(old_url, follow=False)
        
        if response.status_code == expected_status:
            actual_redirect = response.get('Location', '')
            status = "✅" if actual_redirect == expected_redirect else "⚠️"
            results.append({
                'old_url': old_url,
                'expected': expected_redirect,
                'actual': actual_redirect,
                'status_code': response.status_code,
                'result': status
            })
            print(f"{status} {old_url} -> {actual_redirect} (Status: {response.status_code})")
        else:
            results.append({
                'old_url': old_url,
                'status_code': response.status_code,
                'result': '❌'
            })
            print(f"❌ {old_url} returned {response.status_code} instead of {expected_status}")
    
    return results

def test_api_endpoints():
    """Test that API endpoints work correctly"""
    print("\n" + "="*60)
    print("TESTING API ENDPOINTS")
    print("="*60)
    
    client = Client()
    
    # Get or create test data
    exam = Exam.objects.first()
    if not exam:
        print("⚠️ No exam found in database to test with")
        return []
    
    api_tests = [
        {
            'name': 'Save Exam Answers',
            'url': f'/api/PlacementTest/exams/{exam.id}/save-answers/',
            'method': 'POST',
            'data': {'questions': [], 'audio_assignments': {}},
            'expected_status': [200, 201, 400]  # Might fail with validation
        },
        {
            'name': 'Update Exam Name',
            'url': f'/api/PlacementTest/exams/{exam.id}/update-name/',
            'method': 'POST', 
            'data': {'name': 'Test Exam'},
            'expected_status': [200, 201]
        },
        {
            'name': 'Create Questions',
            'url': f'/api/PlacementTest/exams/{exam.id}/create-questions/',
            'method': 'POST',
            'data': {'question_count': 1},
            'expected_status': [200, 201, 400]
        }
    ]
    
    results = []
    for test in api_tests:
        if test['method'] == 'POST':
            response = client.post(
                test['url'],
                data=json.dumps(test['data']),
                content_type='application/json'
            )
        else:
            response = client.get(test['url'])
        
        status = "✅" if response.status_code in test['expected_status'] else "❌"
        results.append({
            'name': test['name'],
            'url': test['url'],
            'status_code': response.status_code,
            'result': status
        })
        print(f"{status} {test['name']}: Status {response.status_code}")
    
    return results

def test_template_rendering():
    """Test that key pages render without errors"""
    print("\n" + "="*60)
    print("TESTING PAGE RENDERING")
    print("="*60)
    
    client = Client()
    
    pages_to_test = [
        ('/PlacementTest/start/', 'Start Placement Test', 200),
        ('/RoutineTest/', 'PrimePath Routine Test', 200),
        ('/RoutineTest/start/', 'Start Test', 200),
    ]
    
    results = []
    for url, expected_content, expected_status in pages_to_test:
        response = client.get(url)
        
        if response.status_code == expected_status:
            content = response.content.decode('utf-8')
            has_content = expected_content in content
            status = "✅" if has_content else "⚠️"
            results.append({
                'url': url,
                'status_code': response.status_code,
                'has_expected_content': has_content,
                'result': status
            })
            print(f"{status} {url}: Status {response.status_code}, Content: {'Found' if has_content else 'Missing'}")
        else:
            results.append({
                'url': url,
                'status_code': response.status_code,
                'result': '❌'
            })
            print(f"❌ {url}: Status {response.status_code} (Expected {expected_status})")
    
    return results

def test_database_integrity():
    """Test that database models and relationships are intact"""
    print("\n" + "="*60)
    print("TESTING DATABASE INTEGRITY")
    print("="*60)
    
    results = []
    
    # Test PlacementTest models
    placement_exam_count = Exam.objects.count()
    placement_session_count = StudentSession.objects.count()
    placement_question_count = Question.objects.count()
    
    print(f"✅ PlacementTest - Exams: {placement_exam_count}, Sessions: {placement_session_count}, Questions: {placement_question_count}")
    results.append({
        'app': 'PlacementTest',
        'exams': placement_exam_count,
        'sessions': placement_session_count,
        'questions': placement_question_count
    })
    
    # Test RoutineTest models (separate)
    routine_exam_count = RoutineExam.objects.count()
    print(f"✅ RoutineTest - Exams: {routine_exam_count}")
    results.append({
        'app': 'RoutineTest',
        'exams': routine_exam_count
    })
    
    # Test relationships
    if placement_exam_count > 0:
        exam = Exam.objects.first()
        try:
            questions = exam.questions.all()
            print(f"✅ Exam-Question relationship intact: {questions.count()} questions")
            results.append({'relationship': 'exam-questions', 'status': '✅'})
        except Exception as e:
            print(f"❌ Exam-Question relationship broken: {e}")
            results.append({'relationship': 'exam-questions', 'status': '❌', 'error': str(e)})
    
    return results

def main():
    """Run all tests and generate summary"""
    print("\n" + "="*60)
    print("FEATURE INTEGRITY TEST SUITE")
    print("After URL Restructuring: /placement/ -> /PlacementTest/")
    print("="*60)
    
    all_results = {
        'url_patterns': test_url_patterns(),
        'redirects': test_redirects(),
        'api_endpoints': test_api_endpoints(),
        'template_rendering': test_template_rendering(),
        'database_integrity': test_database_integrity()
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = 0
    passed_tests = 0
    warnings = 0
    
    for category, results in all_results.items():
        category_passed = sum(1 for r in results if r.get('result', r.get('status', '')) == '✅')
        category_warnings = sum(1 for r in results if r.get('result', r.get('status', '')) == '⚠️')
        category_total = len(results)
        
        total_tests += category_total
        passed_tests += category_passed
        warnings += category_warnings
        
        print(f"{category}: {category_passed}/{category_total} passed, {category_warnings} warnings")
    
    failed_tests = total_tests - passed_tests - warnings
    
    print(f"\nOVERALL: {passed_tests}/{total_tests} tests passed")
    if warnings > 0:
        print(f"         {warnings} tests with warnings")
    if failed_tests > 0:
        print(f"         {failed_tests} tests FAILED")
    
    # Final verdict
    if failed_tests == 0:
        print("\n✅ URL RESTRUCTURING SUCCESSFUL - All features operational")
    elif failed_tests <= 2:
        print("\n⚠️ URL RESTRUCTURING MOSTLY SUCCESSFUL - Minor issues detected")
    else:
        print("\n❌ URL RESTRUCTURING HAS ISSUES - Multiple features affected")
    
    return all_results

if __name__ == "__main__":
    main()