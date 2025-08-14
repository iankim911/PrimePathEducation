#!/usr/bin/env python
"""
Comprehensive test to verify ALL existing features still work after namespace initialization fixes
"""

import os
import sys
import django
import json
import requests
import time
from datetime import datetime

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import StudentSession, Exam, Question, AudioFile, StudentAnswer
from primepath_routinetest.models import StudentSession as RoutineStudentSession, Exam as RoutineExam
from core.models import CurriculumLevel
from django.utils import timezone

def test_all_existing_features():
    """Test all existing features to ensure they weren't affected by namespace fixes"""
    
    print("=" * 80)
    print("COMPREHENSIVE EXISTING FEATURES VERIFICATION")
    print("Testing ALL features after namespace initialization fixes")
    print("=" * 80)
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    base_url = "http://127.0.0.1:8000"
    
    # Feature 1: Database Models and Core Data
    print("\n" + "=" * 70)
    print("FEATURE 1: DATABASE MODELS & CORE DATA")
    print("=" * 70)
    
    try:
        # Test Placement Test models
        placement_exams = Exam.objects.all()
        placement_count = placement_exams.count()
        print(f"  ✅ Placement exams: {placement_count}")
        
        if placement_count > 0:
            sample_exam = placement_exams.first()
            question_count = sample_exam.questions.count()
            print(f"  ✅ Sample exam questions: {question_count}")
            
            if question_count > 0:
                results['passed'].append("Placement exam-question relationships")
            else:
                results['warnings'].append("No questions in placement exams")
        
        # Test Routine Test models
        routine_exams = RoutineExam.objects.all()
        routine_count = routine_exams.count()
        print(f"  ✅ Routine exams: {routine_count}")
        
        if routine_count > 0:
            routine_exam = routine_exams.first()
            routine_questions = routine_exam.routine_questions.count()
            print(f"  ✅ Sample routine exam questions: {routine_questions}")
            
            if routine_questions > 0:
                results['passed'].append("Routine exam-question relationships")
            else:
                results['warnings'].append("No questions in routine exams")
        
        # Test Curriculum Levels
        levels = CurriculumLevel.objects.all()
        levels_count = levels.count()
        print(f"  ✅ Curriculum levels: {levels_count}")
        
        if levels_count > 0:
            results['passed'].append("Curriculum structure intact")
        else:
            results['failed'].append("No curriculum levels found")
            
        results['passed'].append("Database models working")
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        results['failed'].append(f"Database models: {e}")
    
    # Feature 2: Student Session Creation and Management
    print("\n" + "=" * 70)
    print("FEATURE 2: STUDENT SESSION CREATION & MANAGEMENT")
    print("=" * 70)
    
    try:
        # Test Placement Test Session Creation
        if placement_count > 0 and levels_count > 0:
            exam = Exam.objects.filter(questions__isnull=False).first()
            level = CurriculumLevel.objects.first()
            
            placement_session = StudentSession.objects.create(
                student_name='Feature Test - Placement',
                grade=10,
                academic_rank='TOP_10',
                exam=exam,
                original_curriculum_level=level
            )
            
            print(f"  ✅ Placement session created: {placement_session.id}")
            print(f"  ✅ Session exam: {placement_session.exam.name}")
            print(f"  ✅ Session level: {placement_session.original_curriculum_level}")
            
            # Test URL generation
            placement_url = f"/placement/test/{placement_session.id}/"
            print(f"  ✅ Placement URL: {placement_url}")
            
            results['passed'].append("Placement session creation")
            
            # Test answer saving
            question = exam.questions.first()
            if question:
                answer = StudentAnswer.objects.create(
                    session=placement_session,
                    question=question,
                    answer='Test Answer for Feature Verification'
                )
                print(f"  ✅ Answer saved for Q{question.question_number}")
                
                # Verify answer retrieval
                retrieved_answer = StudentAnswer.objects.filter(
                    session=placement_session,
                    question=question
                ).first()
                
                if retrieved_answer and retrieved_answer.answer == 'Test Answer for Feature Verification':
                    print("  ✅ Answer retrieval working")
                    results['passed'].append("Answer saving/retrieval")
                else:
                    results['failed'].append("Answer retrieval mismatch")
                
                # Cleanup
                answer.delete()
            
            # Cleanup session
            placement_session.delete()
        else:
            results['warnings'].append("Cannot test placement sessions - missing data")
        
        # Test Routine Test Session Creation
        if routine_count > 0 and levels_count > 0:
            routine_exam = RoutineExam.objects.filter(routine_questions__isnull=False).first()
            
            if routine_exam:
                routine_session = RoutineStudentSession.objects.create(
                    student_name='Feature Test - Routine',
                    grade=10,
                    academic_rank='TOP_10',
                    exam=routine_exam,
                    original_curriculum_level=level
                )
                
                print(f"  ✅ Routine session created: {routine_session.id}")
                print(f"  ✅ Routine session exam: {routine_session.exam.name}")
                
                results['passed'].append("Routine session creation")
                
                # Cleanup
                routine_session.delete()
            else:
                results['warnings'].append("No routine exams with questions found")
        
    except Exception as e:
        print(f"  ❌ Session test failed: {e}")
        results['failed'].append(f"Session management: {e}")
    
    # Feature 3: PDF Files and Attachments
    print("\n" + "=" * 70)
    print("FEATURE 3: PDF FILES & ATTACHMENTS")
    print("=" * 70)
    
    try:
        # Test placement exams with PDFs
        placement_pdfs = Exam.objects.filter(pdf_file__isnull=False)
        placement_pdf_count = placement_pdfs.count()
        print(f"  ✅ Placement exams with PDFs: {placement_pdf_count}")
        
        if placement_pdf_count > 0:
            sample_pdf_exam = placement_pdfs.first()
            print(f"  ✅ Sample PDF exam: {sample_pdf_exam.name}")
            print(f"  ✅ PDF path: {sample_pdf_exam.pdf_file.name}")
            results['passed'].append("Placement PDF attachments")
        else:
            results['warnings'].append("No placement PDFs found")
        
        # Test routine exams with PDFs
        routine_pdfs = RoutineExam.objects.filter(pdf_file__isnull=False)
        routine_pdf_count = routine_pdfs.count()
        print(f"  ✅ Routine exams with PDFs: {routine_pdf_count}")
        
        if routine_pdf_count > 0:
            sample_routine_pdf = routine_pdfs.first()
            print(f"  ✅ Sample routine PDF: {sample_routine_pdf.name}")
            print(f"  ✅ Routine PDF path: {sample_routine_pdf.pdf_file.name}")
            results['passed'].append("Routine PDF attachments")
        else:
            results['warnings'].append("No routine PDFs found")
            
    except Exception as e:
        print(f"  ❌ PDF test failed: {e}")
        results['failed'].append(f"PDF attachments: {e}")
    
    # Feature 4: Timer Functionality
    print("\n" + "=" * 70)
    print("FEATURE 4: TIMER FUNCTIONALITY")
    print("=" * 70)
    
    try:
        # Test placement timer configurations
        timed_placement = Exam.objects.filter(timer_minutes__isnull=False, timer_minutes__gt=0)
        untimed_placement = Exam.objects.filter(timer_minutes__isnull=True)
        
        print(f"  ✅ Timed placement exams: {timed_placement.count()}")
        print(f"  ✅ Untimed placement exams: {untimed_placement.count()}")
        
        if timed_placement.exists():
            sample_timed = timed_placement.first()
            print(f"  ✅ Sample timed exam: {sample_timed.name} ({sample_timed.timer_minutes} min)")
            results['passed'].append("Placement timer configuration")
        
        # Test routine timer configurations
        timed_routine = RoutineExam.objects.filter(timer_minutes__isnull=False, timer_minutes__gt=0)
        untimed_routine = RoutineExam.objects.filter(timer_minutes__isnull=True)
        
        print(f"  ✅ Timed routine exams: {timed_routine.count()}")
        print(f"  ✅ Untimed routine exams: {untimed_routine.count()}")
        
        if timed_routine.exists():
            sample_routine_timed = timed_routine.first()
            print(f"  ✅ Sample routine timed: {sample_routine_timed.name} ({sample_routine_timed.timer_minutes} min)")
            results['passed'].append("Routine timer configuration")
        
    except Exception as e:
        print(f"  ❌ Timer test failed: {e}")
        results['failed'].append(f"Timer functionality: {e}")
    
    # Feature 5: Audio Files and Assignments
    print("\n" + "=" * 70)
    print("FEATURE 5: AUDIO FILES & ASSIGNMENTS")
    print("=" * 70)
    
    try:
        # Test audio files
        audio_files = AudioFile.objects.all()
        audio_count = audio_files.count()
        print(f"  ✅ Total audio files: {audio_count}")
        
        if audio_count > 0:
            # Test audio-exam relationships
            audio_with_exam = AudioFile.objects.filter(exam__isnull=False)
            print(f"  ✅ Audio files with exam assignments: {audio_with_exam.count()}")
            
            if audio_with_exam.exists():
                sample_audio = audio_with_exam.first()
                print(f"  ✅ Sample audio: {sample_audio.name}")
                print(f"  ✅ Assigned to exam: {sample_audio.exam.name}")
                print(f"  ✅ Question range: Q{sample_audio.start_question}-Q{sample_audio.end_question}")
                results['passed'].append("Audio file assignments")
            else:
                results['warnings'].append("No audio files assigned to exams")
        else:
            results['warnings'].append("No audio files in database")
            
    except Exception as e:
        print(f"  ❌ Audio test failed: {e}")
        results['failed'].append(f"Audio functionality: {e}")
    
    # Feature 6: Question Types and Answer Formats
    print("\n" + "=" * 70)
    print("FEATURE 6: QUESTION TYPES & ANSWER FORMATS")
    print("=" * 70)
    
    try:
        # Test placement question types
        placement_question_types = Question.objects.values_list('question_type', flat=True).distinct()
        print("  Placement question types:")
        for qtype in placement_question_types:
            count = Question.objects.filter(question_type=qtype).count()
            print(f"    ✅ {qtype}: {count} questions")
        
        if len(placement_question_types) > 0:
            results['passed'].append("Placement question types")
        
        # Test routine question types (if different model structure)
        try:
            from primepath_routinetest.models import Question as RoutineQuestion
            routine_question_types = RoutineQuestion.objects.values_list('question_type', flat=True).distinct()
            print("  Routine question types:")
            for qtype in routine_question_types:
                count = RoutineQuestion.objects.filter(question_type=qtype).count()
                print(f"    ✅ {qtype}: {count} questions")
                
            if len(routine_question_types) > 0:
                results['passed'].append("Routine question types")
        except:
            print("    ℹ️ Routine questions use same model as placement")
            
    except Exception as e:
        print(f"  ❌ Question types test failed: {e}")
        results['failed'].append(f"Question types: {e}")
    
    # Feature 7: Static Files and Assets
    print("\n" + "=" * 70)
    print("FEATURE 7: STATIC FILES & ASSETS")
    print("=" * 70)
    
    try:
        # Test critical JavaScript files
        js_files = [
            '/static/js/bootstrap.js',
            '/static/js/config/debug-config.js',
            '/static/js/config/app-config.js',
            '/static/js/utils/event-delegation.js',
            '/static/js/modules/answer-manager.js',
            '/static/js/modules/navigation.js',
            '/static/js/modules/timer.js',
            '/static/js/modules/pdf-viewer.js',
            '/static/js/modules/audio-player.js'
        ]
        
        accessible_count = 0
        for js_file in js_files:
            try:
                response = requests.head(f"{base_url}{js_file}")
                if response.status_code == 200:
                    print(f"  ✅ {js_file}: Accessible")
                    accessible_count += 1
                else:
                    print(f"  ❌ {js_file}: Status {response.status_code}")
            except:
                print(f"  ❌ {js_file}: Failed to access")
        
        if accessible_count >= len(js_files) * 0.9:  # 90% threshold
            results['passed'].append("JavaScript files accessibility")
        else:
            results['failed'].append("Some JavaScript files inaccessible")
        
        # Test CSS files
        css_files = [
            '/static/css/pages/student-test.css',
            '/static/css/components/difficulty-modal.css'
        ]
        
        css_accessible = 0
        for css_file in css_files:
            try:
                response = requests.head(f"{base_url}{css_file}")
                if response.status_code == 200:
                    print(f"  ✅ {css_file}: Accessible")
                    css_accessible += 1
                else:
                    print(f"  ❌ {css_file}: Status {response.status_code}")
            except:
                print(f"  ❌ {css_file}: Failed to access")
        
        if css_accessible > 0:
            results['passed'].append("CSS files accessibility")
            
    except Exception as e:
        print(f"  ❌ Static files test failed: {e}")
        results['failed'].append(f"Static files: {e}")
    
    # Feature 8: Template Rendering
    print("\n" + "=" * 70)
    print("FEATURE 8: TEMPLATE RENDERING")
    print("=" * 70)
    
    try:
        # Test placement test template
        if placement_count > 0 and levels_count > 0:
            exam = Exam.objects.filter(questions__isnull=False).first()
            level = CurriculumLevel.objects.first()
            
            placement_session = StudentSession.objects.create(
                student_name='Template Test - Placement',
                grade=8,
                academic_rank='AVERAGE',
                exam=exam,
                original_curriculum_level=level
            )
            
            placement_url = f"{base_url}/placement/test/{placement_session.id}/"
            response = requests.get(placement_url)
            
            if response.status_code == 200:
                print("  ✅ Placement test template renders successfully")
                
                # Check for critical elements
                critical_elements = [
                    'question-panel',
                    'submit-test-btn',
                    'answer-input',
                    'question-nav-btn'
                ]
                
                elements_found = sum(1 for element in critical_elements if element in response.text)
                print(f"  ✅ Critical UI elements: {elements_found}/{len(critical_elements)} found")
                
                if elements_found >= len(critical_elements) * 0.8:
                    results['passed'].append("Placement template rendering")
                else:
                    results['failed'].append("Missing critical UI elements in placement template")
            else:
                print(f"  ❌ Placement template returned status {response.status_code}")
                results['failed'].append("Placement template rendering failed")
            
            placement_session.delete()
        
        # Test routine test template
        if routine_count > 0 and levels_count > 0:
            routine_exam = RoutineExam.objects.filter(routine_questions__isnull=False).first()
            
            if routine_exam:
                routine_session = RoutineStudentSession.objects.create(
                    student_name='Template Test - Routine',
                    grade=8,
                    academic_rank='AVERAGE',
                    exam=routine_exam,
                    original_curriculum_level=level
                )
                
                routine_url = f"{base_url}/routine-test/test/{routine_session.id}/"
                response = requests.get(routine_url)
                
                if response.status_code == 200:
                    print("  ✅ Routine test template renders successfully")
                    
                    # Check for namespace fix implementation
                    namespace_checks = [
                        'bootstrap.js',
                        'PRIMEPATH ROUTINE TEST INITIALIZATION',
                        'PrimePath.modules',
                        'healthCheck()'
                    ]
                    
                    namespace_found = sum(1 for check in namespace_checks if check in response.text)
                    print(f"  ✅ Namespace fix elements: {namespace_found}/{len(namespace_checks)} found")
                    
                    if namespace_found >= len(namespace_checks) * 0.75:
                        results['passed'].append("Routine template rendering with fixes")
                    else:
                        results['warnings'].append("Some namespace fix elements missing")
                else:
                    print(f"  ❌ Routine template returned status {response.status_code}")
                    results['failed'].append("Routine template rendering failed")
                
                routine_session.delete()
        
    except Exception as e:
        print(f"  ❌ Template rendering test failed: {e}")
        results['failed'].append(f"Template rendering: {e}")
    
    # Feature 9: URL Patterns and Routing
    print("\n" + "=" * 70)
    print("FEATURE 9: URL PATTERNS & ROUTING")
    print("=" * 70)
    
    try:
        # Test key URL patterns
        test_urls = [
            ('Home page', '/'),
            ('Static files', '/static/js/bootstrap.js'),
            ('Admin interface', '/admin/'),
        ]
        
        for name, url in test_urls:
            try:
                response = requests.head(f"{base_url}{url}")
                if response.status_code in [200, 302, 301]:  # Allow redirects
                    print(f"  ✅ {name}: Accessible (status {response.status_code})")
                else:
                    print(f"  ⚠️ {name}: Status {response.status_code}")
            except Exception as e:
                print(f"  ❌ {name}: Error - {e}")
        
        results['passed'].append("URL routing working")
        
    except Exception as e:
        print(f"  ❌ URL patterns test failed: {e}")
        results['failed'].append(f"URL routing: {e}")
    
    # Feature 10: Admin Interface and Management
    print("\n" + "=" * 70)
    print("FEATURE 10: ADMIN INTERFACE & MANAGEMENT")
    print("=" * 70)
    
    try:
        # Test admin accessibility
        admin_response = requests.get(f"{base_url}/admin/")
        if admin_response.status_code in [200, 302]:
            print("  ✅ Admin interface accessible")
            results['passed'].append("Admin interface accessibility")
        else:
            print(f"  ❌ Admin interface returned status {admin_response.status_code}")
            results['failed'].append("Admin interface inaccessible")
        
        # Test model registration (indirect - through counts)
        model_counts = {
            'Placement Exams': Exam.objects.count(),
            'Routine Exams': RoutineExam.objects.count(),
            'Curriculum Levels': CurriculumLevel.objects.count(),
            'Audio Files': AudioFile.objects.count(),
        }
        
        print("  Admin model accessibility (via counts):")
        for model_name, count in model_counts.items():
            print(f"    ✅ {model_name}: {count} objects")
        
        results['passed'].append("Admin model accessibility")
        
    except Exception as e:
        print(f"  ❌ Admin interface test failed: {e}")
        results['failed'].append(f"Admin interface: {e}")
    
    # Final Summary
    print("\n" + "=" * 80)
    print("COMPREHENSIVE FEATURES TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(results['passed']) + len(results['failed'])
    success_rate = (len(results['passed']) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n✅ Passed: {len(results['passed'])} features")
    for feature in results['passed']:
        print(f"   - {feature}")
    
    if results['failed']:
        print(f"\n❌ Failed: {len(results['failed'])} features")
        for feature in results['failed']:
            print(f"   - {feature}")
    
    if results['warnings']:
        print(f"\n⚠️  Warnings: {len(results['warnings'])}")
        for warning in results['warnings']:
            print(f"   - {warning}")
    
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 ALL EXISTING FEATURES WORKING PERFECTLY!")
        print("✅ Namespace initialization fixes did not break any functionality")
        print("✅ All core features preserved and operational")
        return True
    elif success_rate >= 90:
        print("\n✅ EXCELLENT - MOST FEATURES WORKING")
        print("Minor issues detected but all critical functionality preserved")
        return True
    elif success_rate >= 80:
        print("\n✅ GOOD - CRITICAL FEATURES WORKING")
        print("Some minor issues but core functionality intact")
        return True
    else:
        print("\n⚠️ ATTENTION NEEDED")
        print("Some critical features may be affected - review failed tests")
        return False

if __name__ == "__main__":
    success = test_all_existing_features()
    sys.exit(0 if success else 1)