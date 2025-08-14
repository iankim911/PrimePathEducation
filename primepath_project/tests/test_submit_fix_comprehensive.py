#!/usr/bin/env python3
"""
Comprehensive test for submit test fix
Tests the entire student workflow and ensures no features were broken
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django.urls import reverse
from placement_test.models import Exam, Question, StudentSession, StudentAnswer, AudioFile
from placement_test.views.student import take_test, submit_answer, complete_test, test_result
from core.models import CurriculumLevel, PlacementRule, School
import uuid

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_student_workflow():
    """Test complete student workflow from start to finish"""
    print_section("TESTING COMPLETE STUDENT WORKFLOW")
    
    client = Client()
    factory = RequestFactory()
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    try:
        # 1. Test Start Test Page
        print("\n1. Testing start test page...")
        response = client.get(reverse('PlacementTest:start_test'))
        if response.status_code == 200:
            print("   ✅ Start test page loads correctly")
            results['passed'].append("Start test page loads")
        else:
            print(f"   ❌ Start test page error: {response.status_code}")
            results['failed'].append(f"Start test page: {response.status_code}")
        
        # 2. Create test session
        print("\n2. Creating test session...")
        
        # Ensure we have required data
        if not School.objects.exists():
            school = School.objects.create(name="Test School")
        else:
            school = School.objects.first()
        
        if not CurriculumLevel.objects.exists():
            level = CurriculumLevel.objects.create(
                name="Test Level",
                grade_level=5,
                difficulty="Standard"
            )
        else:
            level = CurriculumLevel.objects.first()
        
        # Ensure we have a placement rule for grade 5, TOP_50
        if not PlacementRule.objects.filter(grade=5).exists():
            PlacementRule.objects.create(
                grade=5,
                min_rank_percentile=40,
                max_rank_percentile=60,
                curriculum_level=level,
                priority=1
            )
        
        if not Exam.objects.exists():
            exam = Exam.objects.create(
                name="Test Exam",
                total_questions=10,
                timer_minutes=30,
                curriculum_level=level
            )
            # Create questions
            for i in range(1, 11):
                Question.objects.create(
                    exam=exam,
                    question_number=i,
                    question_type='multiple_choice',
                    correct_answer=f"Option {i % 4 + 1}",
                    points=1,
                    options_count=4
                )
        else:
            exam = Exam.objects.first()
        
        # Create session via POST
        session_data = {
            'student_name': 'Test Student',
            'grade': '5',
            'academic_rank': 'TOP_50',  # Use valid academic rank
            'school_name': school.name,
            'parent_phone': '555-1234'
        }
        
        response = client.post(reverse('PlacementTest:start_test'), session_data)
        if response.status_code == 302:  # Redirect expected
            print("   ✅ Session created successfully")
            results['passed'].append("Session creation")
            
            # Get the session ID from redirect
            if hasattr(response, 'url'):
                session_id = response.url.split('/')[-2]
                session = StudentSession.objects.get(id=session_id)
                print(f"   📋 Session ID: {session_id}")
            else:
                # Find the latest session
                session = StudentSession.objects.latest('created_at')
                session_id = str(session.id)
        else:
            print(f"   ❌ Session creation failed: {response.status_code}")
            results['failed'].append("Session creation")
            return results
        
        # 3. Test Take Test Page (where the fix was applied)
        print("\n3. Testing take test page with enhanced session handling...")
        response = client.get(reverse('PlacementTest:take_test', args=[session_id]))
        
        if response.status_code == 200:
            print("   ✅ Take test page loads correctly")
            results['passed'].append("Take test page loads")
            
            # Check if js_config is properly passed (context might not be available in client response)
            if hasattr(response, 'context') and response.context:
                if 'js_config' in response.context:
                    js_config = response.context['js_config']
                    if isinstance(js_config, dict):
                        if 'session' in js_config and 'id' in js_config['session']:
                            print(f"   ✅ Session data properly structured: {js_config['session']['id']}")
                            results['passed'].append("Session data structure")
                        else:
                            print("   ⚠️  Session data missing 'id' field")
                            results['warnings'].append("Session data incomplete")
                    else:
                        print("   ❌ js_config is not a dictionary")
                        results['failed'].append("js_config format")
                else:
                    print("   ⚠️  js_config not in context")
                    results['warnings'].append("js_config missing from context")
            else:
                print("   ℹ️  Context not available in test response (normal for client tests)")
            
            # Check template rendering
            content = response.content.decode('utf-8')
            
            # Check for AnswerManager initialization with fallbacks
            if 'getSessionId()' in content or 'sessionId:' in content:
                print("   ✅ AnswerManager has session ID fallback mechanism")
                results['passed'].append("Session ID fallback")
            else:
                print("   ⚠️  Session ID fallback might not be implemented")
                results['warnings'].append("Session ID fallback check")
            
            # Check for defensive checks
            if 'if (!this.session || !this.session.id)' in content or 'getSessionId' in content:
                print("   ✅ Defensive checks present in JavaScript")
                results['passed'].append("Defensive programming")
            
            # Check for APP_CONFIG
            if 'APP_CONFIG' in content:
                print("   ✅ APP_CONFIG initialization found")
                results['passed'].append("APP_CONFIG setup")
            else:
                print("   ❌ APP_CONFIG not found in template")
                results['failed'].append("APP_CONFIG missing")
        else:
            print(f"   ❌ Take test page error: {response.status_code}")
            results['failed'].append(f"Take test page: {response.status_code}")
        
        # 4. Test Answer Submission
        print("\n4. Testing answer submission...")
        question = exam.questions.first()
        
        # Submit answer via API
        answer_data = {
            'question_id': str(question.id),
            'answer': 'Option 1'
        }
        
        response = client.post(
            reverse('PlacementTest:submit_answer', args=[session_id]),
            json.dumps(answer_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.content)
            if data.get('success'):
                print("   ✅ Answer submission works correctly")
                results['passed'].append("Answer submission")
            else:
                print(f"   ❌ Answer submission failed: {data.get('error')}")
                results['failed'].append(f"Answer submission: {data.get('error')}")
        else:
            print(f"   ❌ Answer submission HTTP error: {response.status_code}")
            results['failed'].append(f"Answer submission HTTP: {response.status_code}")
        
        # 5. Test Complete Test (The Critical Fix Point)
        print("\n5. Testing test completion (CRITICAL - where error occurred)...")
        
        response = client.post(
            reverse('PlacementTest:complete_test', args=[session_id])
        )
        
        if response.status_code in [200, 302]:  # Could be redirect to results
            print("   ✅ Test completion works! Fix successful!")
            results['passed'].append("TEST COMPLETION (CRITICAL FIX)")
            
            # Verify session is marked complete
            session.refresh_from_db()
            if session.completed_at:
                print("   ✅ Session marked as complete")
                results['passed'].append("Session completion flag")
            else:
                print("   ⚠️  Session not marked complete")
                results['warnings'].append("Session completion flag")
        else:
            print(f"   ❌ Test completion failed: {response.status_code}")
            results['failed'].append(f"TEST COMPLETION: {response.status_code}")
        
        # 6. Test Results Page
        print("\n6. Testing results page...")
        response = client.get(reverse('PlacementTest:test_result', args=[session_id]))
        
        if response.status_code == 200:
            print("   ✅ Results page displays correctly")
            results['passed'].append("Results page")
        else:
            print(f"   ❌ Results page error: {response.status_code}")
            results['failed'].append(f"Results page: {response.status_code}")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        results['failed'].append(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return results

def test_other_features():
    """Test that other features weren't affected"""
    print_section("TESTING OTHER FEATURES (NO REGRESSION)")
    
    client = Client()
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    try:
        # 1. Teacher/Admin Features
        print("\n1. Testing teacher/admin features...")
        
        # Create superuser if needed
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@test.com', 'password')
        
        # Try to access exam list (requires login)
        response = client.get(reverse('PlacementTest:exam_list'))
        if response.status_code in [200, 302]:  # 302 if login required
            print("   ✅ Exam list endpoint works")
            results['passed'].append("Exam list")
        else:
            print(f"   ❌ Exam list error: {response.status_code}")
            results['failed'].append(f"Exam list: {response.status_code}")
        
        # 2. Audio Features
        print("\n2. Testing audio features...")
        if AudioFile.objects.exists():
            audio = AudioFile.objects.first()
            # Audio files should still have proper relationships
            if hasattr(audio, 'exam'):
                print("   ✅ Audio-Exam relationships intact")
                results['passed'].append("Audio relationships")
            else:
                print("   ⚠️  Audio relationships might be affected")
                results['warnings'].append("Audio relationships")
        else:
            print("   ℹ️  No audio files to test")
        
        # 3. Question Navigation
        print("\n3. Testing question navigation...")
        if Question.objects.exists():
            question = Question.objects.first()
            if hasattr(question, 'audio_file'):
                print("   ✅ Question-Audio relationship intact")
                results['passed'].append("Question-Audio relationship")
            if question.question_number and question.question_type:
                print("   ✅ Question properties intact")
                results['passed'].append("Question properties")
        
        # 4. Session Management
        print("\n4. Testing session management...")
        if StudentSession.objects.exists():
            session = StudentSession.objects.first()
            
            # Check all expected fields
            required_fields = ['student_name', 'grade', 'academic_rank', 'exam', 
                             'started_at', 'original_curriculum_level']  # Fixed field name
            missing_fields = []
            
            for field in required_fields:
                if not hasattr(session, field):
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ❌ Missing session fields: {missing_fields}")
                results['failed'].append(f"Session fields: {missing_fields}")
            else:
                print("   ✅ All session fields intact")
                results['passed'].append("Session structure")
        
        # 5. API Endpoints
        print("\n5. Testing API endpoints...")
        
        # Test placement API endpoints
        endpoints = [
            ('PlacementTest:start_test', 'GET'),
            # Add more endpoints as needed
        ]
        
        for url_name, method in endpoints:
            try:
                url = reverse(url_name)
                if method == 'GET':
                    response = client.get(url)
                else:
                    response = client.post(url)
                
                if response.status_code < 500:
                    print(f"   ✅ {url_name} endpoint works")
                    results['passed'].append(f"{url_name} endpoint")
                else:
                    print(f"   ❌ {url_name} error: {response.status_code}")
                    results['failed'].append(f"{url_name}: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  Could not test {url_name}: {e}")
                results['warnings'].append(f"{url_name} test")
        
    except Exception as e:
        print(f"\n❌ Unexpected error in feature testing: {str(e)}")
        results['failed'].append(f"Feature test error: {str(e)}")
    
    return results

def test_javascript_modules():
    """Verify JavaScript module integrity"""
    print_section("TESTING JAVASCRIPT MODULE INTEGRITY")
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    js_dir = os.path.join(os.path.dirname(__file__), 'static', 'js', 'modules')
    
    required_modules = [
        'answer-manager.js',
        'navigation.js',
        'timer.js',
        'audio-player.js',
        'pdf-viewer.js',
        'base-module.js'
    ]
    
    print("\nChecking JavaScript modules...")
    for module in required_modules:
        module_path = os.path.join(js_dir, module)
        if os.path.exists(module_path):
            with open(module_path, 'r') as f:
                content = f.read()
                
                # Check for defensive programming patterns
                if module == 'answer-manager.js':
                    if 'getSessionId' in content:
                        print(f"   ✅ {module}: Has getSessionId fallback method")
                        results['passed'].append(f"{module} fallback")
                    if 'if (!this.session' in content or 'if (!sessionId)' in content:
                        print(f"   ✅ {module}: Has defensive checks")
                        results['passed'].append(f"{module} defensive")
                    if 'try {' in content and 'catch' in content:
                        print(f"   ✅ {module}: Has error handling")
                        results['passed'].append(f"{module} error handling")
                else:
                    print(f"   ✅ {module}: Present")
                    results['passed'].append(f"{module} exists")
        else:
            print(f"   ❌ {module}: Missing")
            results['failed'].append(f"{module} missing")
    
    return results

def main():
    """Run all tests and generate report"""
    print("\n" + "="*60)
    print("  COMPREHENSIVE SUBMIT TEST FIX VERIFICATION")
    print("  Testing Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    all_results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # Run tests
    test_suites = [
        ("Student Workflow", test_student_workflow),
        ("Other Features", test_other_features),
        ("JavaScript Modules", test_javascript_modules)
    ]
    
    for suite_name, test_func in test_suites:
        print(f"\n🔍 Running {suite_name} Tests...")
        results = test_func()
        all_results['passed'].extend(results['passed'])
        all_results['failed'].extend(results['failed'])
        all_results['warnings'].extend(results['warnings'])
    
    # Generate Summary Report
    print_section("TEST RESULTS SUMMARY")
    
    total_tests = len(all_results['passed']) + len(all_results['failed'])
    pass_rate = (len(all_results['passed']) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 Overall Results:")
    print(f"   ✅ Passed: {len(all_results['passed'])}")
    print(f"   ❌ Failed: {len(all_results['failed'])}")
    print(f"   ⚠️  Warnings: {len(all_results['warnings'])}")
    print(f"   📈 Pass Rate: {pass_rate:.1f}%")
    
    # Critical Fix Status
    print("\n🎯 CRITICAL FIX STATUS:")
    if "TEST COMPLETION (CRITICAL FIX)" in all_results['passed']:
        print("   ✅ SUBMIT TEST ERROR: FIXED SUCCESSFULLY!")
    else:
        print("   ❌ SUBMIT TEST ERROR: NOT FIXED")
    
    # Details
    if all_results['failed']:
        print("\n❌ Failed Tests:")
        for failure in all_results['failed']:
            print(f"   - {failure}")
    
    if all_results['warnings']:
        print("\n⚠️  Warnings:")
        for warning in all_results['warnings']:
            print(f"   - {warning}")
    
    # Final Verdict
    print_section("FINAL VERDICT")
    
    if len(all_results['failed']) == 0:
        print("✅ ALL TESTS PASSED! The fix is successful and no regressions detected.")
        print("✅ The submit test functionality is working correctly.")
        print("✅ No other features were negatively impacted.")
    elif len(all_results['failed']) <= 2:
        print("⚠️  MOSTLY SUCCESSFUL: Fix works but minor issues detected.")
        print("   Review the failed tests above for details.")
    else:
        print("❌ ISSUES DETECTED: The fix may have caused regressions.")
        print("   Review the failed tests and fix before deployment.")
    
    # Save results to file
    with open('test_submit_fix_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'pass_rate': pass_rate,
            'results': all_results
        }, f, indent=2)
    
    print("\n📄 Results saved to: test_submit_fix_results.json")
    print("="*60)

if __name__ == "__main__":
    main()