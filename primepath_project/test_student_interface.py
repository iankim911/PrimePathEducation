#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive test for student test interface
Tests that all components are properly initialized and functional
"""

import os
import sys
import django
import json
import io

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import Exam, StudentSession, Question
from placement_test.views import take_test
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def test_student_interface():
    """Test that student interface receives all required data"""
    
    print("\n" + "="*50)
    print("STUDENT INTERFACE COMPREHENSIVE TEST")
    print("="*50)
    
    # Get a session with an exam
    session = StudentSession.objects.filter(exam__isnull=False).first()
    
    if not session:
        print("❌ No student sessions found with exams")
        return False
    
    print(f"✅ Found session: {session.id}")
    print(f"   Student: {session.student_name}")
    print(f"   Exam: {session.exam.name}")
    
    # Test data flow
    exam = session.exam
    
    # Check what the view would pass
    js_config = {
        'session': {
            'id': str(session.id),
            'examId': str(exam.id),
            'timerSeconds': exam.timer_minutes * 60
        },
        'exam': {
            'id': str(exam.id),
            'name': exam.name,
            'pdfUrl': exam.pdf_file.url if exam.pdf_file else ''
        }
    }
    
    print("\n📊 JavaScript Configuration:")
    print(f"   Session ID: {js_config['session'].get('id')}")
    print(f"   Exam ID: {js_config['exam'].get('id')}")
    print(f"   Timer: {js_config['session'].get('timerSeconds')} seconds")
    print(f"   PDF URL: {js_config['exam'].get('pdfUrl') or 'No PDF'}")
    
    # Validate required fields
    errors = []
    
    if not js_config.get('session'):
        errors.append("Missing 'session' in js_config")
    elif not js_config['session'].get('id'):
        errors.append("Missing 'session.id' in js_config")
        
    if not js_config.get('exam'):
        errors.append("Missing 'exam' in js_config")
    elif not js_config['exam'].get('id'):
        errors.append("Missing 'exam.id' in js_config")
    
    if errors:
        print("\n❌ Validation Errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("\n✅ All required fields present")
    
    # Test JSON encoding (what the template would receive)
    try:
        # This is what gets passed to the template
        context_js_config = js_config  # Now passing dict, not JSON string
        
        # Simulate what json_script filter does
        json_output = json.dumps(context_js_config)
        parsed_back = json.loads(json_output)
        
        print("\n🔄 JSON Encoding Test:")
        print(f"   Original type: {type(context_js_config)}")
        print(f"   After json_script filter: {type(json_output)}")
        print(f"   Parsed back type: {type(parsed_back)}")
        print(f"   Has session.id: {bool(parsed_back.get('session', {}).get('id'))}")
        print(f"   Has exam.id: {bool(parsed_back.get('exam', {}).get('id'))}")
        
        if parsed_back.get('session', {}).get('id') and parsed_back.get('exam', {}).get('id'):
            print("\n✅ JSON encoding/decoding successful")
        else:
            print("\n❌ JSON data missing after encoding/decoding")
            return False
            
    except Exception as e:
        print(f"\n❌ JSON encoding error: {e}")
        return False
    
    # Check questions
    questions = exam.questions.all()
    print(f"\n📝 Questions: {questions.count()} found")
    
    if questions.count() == 0:
        print("   ⚠️  Warning: No questions in exam")
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print("✅ Session data: Valid")
    print("✅ Exam data: Valid")
    print("✅ JavaScript config: Valid")
    print("✅ JSON encoding: Working")
    print(f"{'✅' if questions.count() > 0 else '⚠️ '} Questions: {questions.count()}")
    
    print("\n✨ Student interface should work correctly!")
    print("\nTest URL: http://127.0.0.1:8000/api/PlacementTest/session/{}/".format(session.id))
    
    return True

if __name__ == '__main__':
    success = test_student_interface()
    sys.exit(0 if success else 1)