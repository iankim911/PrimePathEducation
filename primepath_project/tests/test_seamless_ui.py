#!/usr/bin/env python
"""
Comprehensive QA Test for Seamless UI Implementation
Tests all functionality after removing gaps and creating unified UI
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
from placement_test.models import PlacementExam as Exam, Question, AudioFile, StudentSession
from core.models import CurriculumLevel, PlacementRule

def run_tests():
    """Run comprehensive QA tests for seamless UI"""
    client = Client()
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': [],
        'passed': 0,
        'failed': 0
    }
    
    print("=" * 60)
    print("COMPREHENSIVE QA TEST - SEAMLESS UI IMPLEMENTATION")
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
        response = client.get('/PlacementTest/PlacementTest/teacher/dashboard/')
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
        response = client.get('/api/PlacementTest/exams/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
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
        response = client.get('/api/PlacementTest/exams/create/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        results['tests'].append({'name': 'Create Exam Page', 'status': 'PASS'})
        results['passed'] += 1
        print("   [PASS] Create exam page loads successfully")
    except Exception as e:
        results['tests'].append({'name': 'Create Exam Page', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Create exam page failed: {e}")
    
    # Test 5: Preview Exam Page - MAIN UI TEST
    print("\n5. Testing Preview Exam Page (SEAMLESS UI TEST)...")
    try:
        exam = Exam.objects.first()
        if exam:
            response = client.get(f'/api/PlacementTest/exams/{exam.id}/preview/')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            content = response.content.decode('utf-8')
            
            # Verify debug elements removed
            assert '[FIRE] TEMPLATE UPDATED' not in content, "Template updated badge still present"
            assert '[DEBUG] DEBUG INFO' not in content, "Debug section still present"
            
            # Verify seamless UI implementation
            assert 'gap: 0' in content, "Gap not set to 0"
            assert 'exam-wrapper' in content, "Unified wrapper not present"
            assert 'border-top: 1px solid #dee2e6' in content, "Border separation not implemented"
            assert 'box-shadow: 0 2px' in content, "Shadow not implemented"
            
            # Verify no excessive spacing
            assert 'margin-bottom: 0' in content, "Margins not optimized"
            assert 'border-radius: 0 0 8px 8px' in content, "Bottom radius not applied"
            
            # Verify sections are connected
            assert 'border: none' in content, "Individual borders not removed"
            assert 'section-header::before' in content, "Visual indicator not added"
            
            results['tests'].append({'name': 'Preview Exam Page - Seamless UI', 'status': 'PASS'})
            results['passed'] += 1
            print("   [PASS] Preview exam page loads successfully")
            print("   [PASS] Debug elements removed")
            print("   [PASS] Seamless UI implemented (zero gaps)")
            print("   [PASS] Visual separation using borders/shadows")
            print("   [PASS] Unified card appearance created")
        else:
            print("   [WARN] No exam found to test preview")
            results['tests'].append({'name': 'Preview Exam Page', 'status': 'SKIP', 'reason': 'No exam found'})
    except Exception as e:
        results['tests'].append({'name': 'Preview Exam Page - Seamless UI', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Preview exam page failed: {e}")
    
    # Test 6: Student Sessions
    print("\n6. Testing Student Sessions...")
    try:
        response = client.get('/api/PlacementTest/sessions/')
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
    
    # Test 9: JavaScript Functionality
    print("\n9. Testing JavaScript Functionality (via content check)...")
    try:
        exam = Exam.objects.first()
        if exam:
            response = client.get(f'/api/PlacementTest/exams/{exam.id}/preview/')
            content = response.content.decode('utf-8')
            
            # Check critical JS functions are present
            assert 'saveAllAnswers' in content, "saveAllAnswers function missing"
            assert 'selectMCQ' in content, "selectMCQ function missing"
            assert ('renderPDFPage' in content or 'pdf-viewer' in content), "PDF viewer element missing"
            assert 'addEventListener' in content, "Event listeners missing"
            
            results['tests'].append({'name': 'JavaScript Functionality', 'status': 'PASS'})
            results['passed'] += 1
            print("   [PASS] All JavaScript functions present")
    except Exception as e:
        results['tests'].append({'name': 'JavaScript Functionality', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] JavaScript functionality check failed: {e}")
    
    # Test 10: Database Integrity
    print("\n10. Testing Database Integrity...")
    try:
        exam_count = Exam.objects.count()
        question_count = Question.objects.count()
        audio_count = AudioFile.objects.count()
        session_count = StudentSession.objects.count()
        
        print(f"   - Exams: {exam_count}")
        print(f"   - Questions: {question_count}")
        print(f"   - Audio Files: {audio_count}")
        print(f"   - Student Sessions: {session_count}")
        
        # Verify exam questions relationship
        if exam_count > 0:
            exam = Exam.objects.first()
            exam_questions = exam.questions.count()
            assert exam_questions > 0, "Exam has no questions"
            print(f"   - First exam has {exam_questions} questions")
        
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
    
    # Test 11: Audio File Management
    print("\n11. Testing Audio File Management...")
    try:
        if AudioFile.objects.exists():
            audio = AudioFile.objects.first()
            response = client.get(f'/api/PlacementTest/audio/{audio.id}/')
            assert response.status_code == 200, f"Audio file retrieval failed: {response.status_code}"
            results['tests'].append({'name': 'Audio File Management', 'status': 'PASS'})
            results['passed'] += 1
            print("   [PASS] Audio file management working")
        else:
            print("   [SKIP] No audio files to test")
            results['tests'].append({'name': 'Audio File Management', 'status': 'SKIP'})
    except Exception as e:
        results['tests'].append({'name': 'Audio File Management', 'status': 'FAIL', 'error': str(e)})
        results['failed'] += 1
        print(f"   [FAIL] Audio file management failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['passed'] + results['failed']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if results['failed'] == 0:
        print("\n[SUCCESS] ALL TESTS PASSED! Seamless UI implementation is working correctly.")
        print("   - Zero gaps between sections")
        print("   - Unified card appearance")
        print("   - Visual separation using borders/shadows")
        print("   - All functionality preserved")
    else:
        print(f"\n[WARNING] {results['failed']} test(s) failed. Please review the errors above.")
    
    # Save results
    with open('qa_seamless_ui_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nTest results saved to qa_seamless_ui_results.json")
    
    return results['failed'] == 0

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)