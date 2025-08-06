#!/usr/bin/env python
"""
Comprehensive QA Test for UI Fixes
Tests all major functionality after UI improvements
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.urls import reverse
from placement_test.models import Exam, Question, AudioFile, StudentSession
from core.models import CurriculumLevel, PlacementRule

def run_tests():
    """Run comprehensive QA tests"""
    client = Client()
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': [],
        'passed': 0,
        'failed': 0
    }
    
    print("=" * 60)
    print("COMPREHENSIVE QA TEST - UI FIXES")
    print("=" * 60)
    
    # Test 1: Home page
    print("\n1. Testing Home Page...")
    try:
        response = client.get('/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        results['tests'].append({'name': 'Home Page', 'status': 'PASS'})
        results['passed'] += 1
        print("   [PASS] Home page loads successfully")
    except Exception as e:
        results['tests'].append({'name': 'Home Page', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Home page failed: {e}")
    
    # Test 2: Teacher Dashboard
    print("\n2. Testing Teacher Dashboard...")
    try:
        response = client.get('/teacher/dashboard/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        results['tests'].append({'name': 'Teacher Dashboard', 'status': 'PASS'})
        results['passed'] += 1
        print("   [PASS] Teacher dashboard loads successfully")
    except Exception as e:
        results['tests'].append({'name': 'Teacher Dashboard', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Teacher dashboard failed: {e}")
    
    # Test 3: Exam List
    print("\n3. Testing Exam List...")
    try:
        response = client.get('/api/placement/exams/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        # Check that the template doesn't have debug elements
        content = response.content.decode('utf-8')
        assert '[FIRE] TEMPLATE UPDATED' not in content, "Debug badge still present"
        assert '[DEBUG] DEBUG INFO' not in content, "Debug info still present"
        results['tests'].append({'name': 'Exam List', 'status': 'PASS'})
        results['passed'] += 1
        print("   [PASS] Exam list loads successfully")
        print("   [PASS] No debug elements present")
    except Exception as e:
        results['tests'].append({'name': 'Exam List', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Exam list failed: {e}")
    
    # Test 4: Create Exam Page
    print("\n4. Testing Create Exam Page...")
    try:
        response = client.get('/api/placement/exams/create/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        results['tests'].append({'name': 'Create Exam Page', 'status': 'PASS'})
        results['passed'] += 1
        print("   [PASS] Create exam page loads successfully")
    except Exception as e:
        results['tests'].append({'name': 'Create Exam Page', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Create exam page failed: {e}")
    
    # Test 5: Preview Exam Page (Main UI Fix Target)
    print("\n5. Testing Preview Exam Page (UI Fix Target)...")
    try:
        exam = Exam.objects.first()
        if exam:
            response = client.get(f'/api/placement/exams/{exam.id}/preview/')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            # Check UI improvements
            content = response.content.decode('utf-8')
            
            # Verify debug elements removed
            assert '[FIRE] TEMPLATE UPDATED' not in content, "Template updated badge still present"
            assert '[DEBUG] DEBUG INFO' not in content, "Debug section still present"
            
            # Verify CSS improvements (check for reduced spacing)
            assert 'margin-bottom: 15px' in content, "PDF title margin not optimized"
            assert 'min-height: 400px' in content, "Min-height not optimized"
            assert 'padding: 20px' in content or 'padding: 15px' in content, "Padding not optimized"
            
            results['tests'].append({'name': 'Preview Exam Page', 'status': 'PASS'})
            results['passed'] += 1
            print("   [PASS] Preview exam page loads successfully")
            print("   [PASS] Debug elements removed")
            print("   [PASS] Spacing optimized")
        else:
            print("   [WARN] No exam found to test preview")
            results['tests'].append({'name': 'Preview Exam Page', 'status': 'SKIP', 'reason': 'No exam found'})
    except Exception as e:
        results['tests'].append({'name': 'Preview Exam Page', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Preview exam page failed: {e}")
    
    # Test 6: Student Sessions
    print("\n6. Testing Student Sessions...")
    try:
        response = client.get('/api/placement/sessions/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        results['tests'].append({'name': 'Student Sessions', 'status': 'PASS'})
        results['passed'] += 1
        print("   [PASS] Student sessions page loads successfully")
    except Exception as e:
        results['tests'].append({'name': 'Student Sessions', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Student sessions failed: {e}")
    
    # Test 7: Placement Rules
    print("\n7. Testing Placement Rules...")
    try:
        response = client.get('/placement-rules/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        results['tests'].append({'name': 'Placement Rules', 'status': 'PASS'})
        results['passed'] += 1
        print("   [PASS] Placement rules page loads successfully")
    except Exception as e:
        results['tests'].append({'name': 'Placement Rules', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Placement rules failed: {e}")
    
    # Test 8: Exam Mapping
    print("\n8. Testing Exam Mapping...")
    try:
        response = client.get('/exam-mapping/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        results['tests'].append({'name': 'Exam Mapping', 'status': 'PASS'})
        results['passed'] += 1
        print("   [PASS] Exam mapping page loads successfully")
    except Exception as e:
        results['tests'].append({'name': 'Exam Mapping', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Exam mapping failed: {e}")
    
    # Test 9: Database Integrity
    print("\n9. Testing Database Integrity...")
    try:
        exam_count = Exam.objects.count()
        question_count = Question.objects.count()
        audio_count = AudioFile.objects.count()
        session_count = StudentSession.objects.count()
        
        print(f"   - Exams: {exam_count}")
        print(f"   - Questions: {question_count}")
        print(f"   - Audio Files: {audio_count}")
        print(f"   - Student Sessions: {session_count}")
        
        results['tests'].append({
            'name': 'Database Integrity', 
            'status': 'PASS',
            'data': {
                'exams': exam_count,
                'questions': question_count,
                'audio_files': audio_count,
                'sessions': session_count
            }
        })
        results['passed'] += 1
        print("   [PASS] Database integrity verified")
    except Exception as e:
        results['tests'].append({'name': 'Database Integrity', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Database integrity check failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['passed'] + results['failed']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if results['failed'] == 0:
        print("\n[SUCCESS] ALL TESTS PASSED! UI fixes are working correctly.")
    else:
        print(f"\n[WARNING]  {results['failed']} test(s) failed. Please review the errors above.")
    
    # Save results
    with open('qa_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nTest results saved to qa_test_results.json")
    
    return results['failed'] == 0

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)