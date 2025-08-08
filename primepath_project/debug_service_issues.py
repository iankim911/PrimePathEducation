#!/usr/bin/env python
"""
Debug Service Issues - Investigate and fix the service layer problems
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from placement_test.models import Exam
import traceback


def debug_service_imports():
    """Debug service import issues"""
    print("🔍 DEBUGGING SERVICE IMPORTS")
    print("-" * 50)
    
    try:
        # Test individual service imports
        print("Testing individual imports...")
        
        from placement_test.services import ExamService
        print("✅ ExamService imported successfully")
        
        from placement_test.services import SessionService
        print("✅ SessionService imported successfully")
        
        from placement_test.services import GradingService
        print("✅ GradingService imported successfully")
        
        # Test service methods
        exam = Exam.objects.first()
        if exam:
            print(f"\nTesting with exam: {exam.name}")
            
            # Test ExamService methods
            try:
                result = ExamService.update_exam_questions(exam, [])
                print(f"✅ ExamService.update_exam_questions: {result}")
            except Exception as e:
                print(f"❌ ExamService.update_exam_questions failed: {e}")
                traceback.print_exc()
            
            try:
                result = ExamService.update_audio_assignments(exam, {})
                print(f"✅ ExamService.update_audio_assignments: {result}")
            except Exception as e:
                print(f"❌ ExamService.update_audio_assignments failed: {e}")
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Service import failed: {e}")
        traceback.print_exc()


def debug_api_endpoint():
    """Debug the failing API endpoint"""
    print("\n🔍 DEBUGGING API ENDPOINT")
    print("-" * 50)
    
    from django.test import Client
    import json
    
    client = Client()
    exam = Exam.objects.first()
    
    if exam:
        url = f'/api/placement/exams/{exam.id}/update-audio-names/'
        test_data = {'audio_names': {}}
        
        print(f"Testing: {url}")
        print(f"Data: {test_data}")
        
        try:
            response = client.post(
                url,
                json.dumps(test_data),
                content_type='application/json'
            )
            
            print(f"Status: {response.status_code}")
            print(f"Content: {response.content.decode()[:200]}...")
            
            if response.status_code == 302:
                print("ℹ️ 302 redirect - this might be normal for non-AJAX requests")
                
                # Try with AJAX header
                response2 = client.post(
                    url,
                    json.dumps(test_data),
                    content_type='application/json',
                    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
                )
                print(f"With AJAX header - Status: {response2.status_code}")
                
        except Exception as e:
            print(f"❌ API test failed: {e}")
            traceback.print_exc()


def check_modular_model_imports():
    """Verify modular model imports are working"""
    print("\n🔍 CHECKING MODULAR MODEL IMPORTS")
    print("-" * 50)
    
    try:
        # Test imports after modularization
        from placement_test.models import Exam, Question, AudioFile, StudentSession, StudentAnswer
        print("✅ All placement_test.models imported")
        
        from core.models import School, Teacher, Program, CurriculumLevel, PlacementRule
        print("✅ All core.models imported")
        
        # Test model functionality
        exam = Exam.objects.first()
        if exam:
            questions = exam.questions.all()
            audio_files = exam.audio_files.all()
            print(f"✅ Model relationships: {questions.count()} questions, {audio_files.count()} audio files")
            
            # Test __str__ methods
            exam_str = str(exam)
            print(f"✅ Model __str__: {exam_str[:50]}...")
        
    except Exception as e:
        print(f"❌ Model import/functionality failed: {e}")
        traceback.print_exc()


def main():
    """Run all debug checks"""
    print("=" * 80)
    print("DEBUGGING SERVICE AND API ISSUES")
    print("=" * 80)
    
    debug_service_imports()
    debug_api_endpoint()
    check_modular_model_imports()
    
    print("\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()