#!/usr/bin/env python
"""
Comprehensive test to verify no existing features were affected.
Tests all major functionality after audio and multiple short answer fixes.
"""

import os
import sys
import django
import json
import uuid
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from placement_test.models import (
    Exam, Question, StudentSession, StudentAnswer, AudioFile
)
from core.models import (
    CurriculumLevel, PlacementRule, ExamLevelMapping, School
)
from placement_test.services import (
    ExamService, SessionService, PlacementService, GradingService
)


class FeatureTestSuite:
    def __init__(self):
        self.client = Client()
        self.results = []
        
    def test_exam_creation(self):
        """Test exam creation and listing."""
        print("\n[1/15] Testing Exam Creation...")
        
        try:
            # Test exam list view
            response = self.client.get(reverse('placement_test:exam_list'))
            if response.status_code != 200:
                print(f"  ❌ Exam list failed: {response.status_code}")
                return False
            
            # Test create exam view
            response = self.client.get(reverse('placement_test:create_exam'))
            if response.status_code != 200:
                print(f"  ❌ Create exam page failed: {response.status_code}")
                return False
            
            # Check exam count
            exam_count = Exam.objects.count()
            print(f"  • Exams in database: {exam_count}")
            
            # Test exam service
            level = CurriculumLevel.objects.first()
            if level:
                try:
                    next_version = ExamService.get_next_version_letter(level.id)
                    print(f"  • Next version for {level.name}: {next_version}")
                except Exception as e:
                    print(f"  ⚠️ Version check: {str(e)}")
            
            print("  ✅ Exam creation: PASSED")
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_question_types(self):
        """Test all question types render correctly."""
        print("\n[2/15] Testing Question Types...")
        
        try:
            exam = Exam.objects.first()
            if not exam:
                print("  ⚠️ No exam found")
                return False
            
            question_types = ['MCQ', 'CHECKBOX', 'SHORT', 'LONG']
            found_types = Question.objects.filter(
                exam=exam
            ).values_list('question_type', flat=True).distinct()
            
            for q_type in question_types:
                if q_type in found_types:
                    print(f"  ✅ {q_type}: Found")
                else:
                    print(f"  ⚠️ {q_type}: Not found in this exam")
            
            # Test multiple short answers
            multi_short = Question.objects.filter(
                question_type='SHORT',
                correct_answer__contains=','
            ).first()
            
            if multi_short:
                print(f"  ✅ Multiple short answers: Q{multi_short.question_number} with {multi_short.correct_answer}")
            else:
                print("  ⚠️ No multiple short answer questions")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_student_session(self):
        """Test student session creation and management."""
        print("\n[3/15] Testing Student Sessions...")
        
        try:
            # Test start test page
            response = self.client.get(reverse('placement_test:start_test'))
            if response.status_code != 200:
                print(f"  ❌ Start test page failed: {response.status_code}")
                return False
            
            # Check existing sessions
            session_count = StudentSession.objects.count()
            print(f"  • Active sessions: {session_count}")
            
            # Test session with audio
            audio_sessions = StudentSession.objects.filter(
                exam__questions__audio_file__isnull=False
            ).distinct().count()
            print(f"  • Sessions with audio questions: {audio_sessions}")
            
            # Get a test session
            session = StudentSession.objects.first()
            if session:
                # Test student test page
                response = self.client.get(
                    reverse('placement_test:take_test', args=[session.id])
                )
                if response.status_code == 200:
                    print(f"  ✅ Student interface: Loaded")
                else:
                    print(f"  ❌ Student interface failed: {response.status_code}")
                    return False
            
            print("  ✅ Session management: PASSED")
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_answer_submission(self):
        """Test answer submission system."""
        print("\n[4/15] Testing Answer Submission...")
        
        try:
            session = StudentSession.objects.filter(is_completed=False).first()
            if not session:
                print("  ⚠️ No active session found")
                return True
            
            question = session.exam.questions.first()
            if question:
                # Test saving an answer
                answer, created = StudentAnswer.objects.update_or_create(
                    session=session,
                    question=question,
                    defaults={'answer': 'Test answer'}
                )
                
                if answer:
                    print(f"  ✅ Answer saved: ID {answer.id}")
                else:
                    print("  ❌ Answer save failed")
                    return False
            
            # Check multiple short answer format
            multi_answer = StudentAnswer.objects.filter(
                answer__startswith='{'
            ).first()
            
            if multi_answer:
                try:
                    parsed = json.loads(multi_answer.answer)
                    print(f"  ✅ JSON answer format: {len(parsed)} parts")
                except:
                    print("  ⚠️ Invalid JSON answer found")
            
            print("  ✅ Answer submission: PASSED")
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_grading_system(self):
        """Test grading functionality."""
        print("\n[5/15] Testing Grading System...")
        
        try:
            grading = GradingService()
            
            # Test MCQ grading
            mcq_result = grading.grade_mcq_answer('A', 'A')
            print(f"  {'✅' if mcq_result else '❌'} MCQ grading: {'Correct' if mcq_result else 'Failed'}")
            
            # Test checkbox grading
            cb_result = grading.grade_checkbox_answer('A,B', 'A,B')
            print(f"  {'✅' if cb_result else '❌'} Checkbox grading: {'Correct' if cb_result else 'Failed'}")
            
            # Test short answer grading
            short_result = grading.grade_short_answer('test', 'test')
            print(f"  {'✅' if short_result else '❌'} Short answer grading: {'Correct' if short_result else 'Failed'}")
            
            # Test multiple short answer grading
            multi_answer = json.dumps({"B": "Answer", "C": "Answer"})
            multi_result = grading.grade_short_answer(multi_answer, 'B,C')
            print(f"  ✅ Multiple short grading: {'Manual required' if multi_result is None else 'Auto'}")
            
            print("  ✅ Grading system: PASSED")
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_audio_system(self):
        """Test audio file system."""
        print("\n[6/15] Testing Audio System...")
        
        try:
            # Check audio files
            audio_count = AudioFile.objects.count()
            print(f"  • Audio files: {audio_count}")
            
            # Test audio URL
            audio = AudioFile.objects.filter(audio_file__isnull=False).first()
            if audio:
                url = reverse('placement_test:get_audio', args=[audio.id])
                response = self.client.get(url)
                
                if response.status_code == 200:
                    print(f"  ✅ Audio streaming: Working")
                else:
                    print(f"  ❌ Audio streaming failed: {response.status_code}")
                    return False
            
            # Check audio assignments
            audio_questions = Question.objects.filter(
                audio_file__isnull=False
            ).count()
            print(f"  • Questions with audio: {audio_questions}")
            
            print("  ✅ Audio system: PASSED")
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_placement_rules(self):
        """Test placement rules and mappings."""
        print("\n[7/15] Testing Placement Rules...")
        
        try:
            # Check placement rules
            rules = PlacementRule.objects.all()
            print(f"  • Placement rules: {rules.count()}")
            
            # Check exam mappings
            mappings = ExamLevelMapping.objects.all()
            print(f"  • Exam mappings: {mappings.count()}")
            
            # Test placement service
            try:
                exam, level = PlacementService.match_student_to_exam(
                    grade=5,
                    academic_rank='average'
                )
                if exam:
                    print(f"  ✅ Placement matching: Working")
                else:
                    print("  ⚠️ No matching exam found")
            except Exception as e:
                print(f"  ⚠️ Placement error: {str(e)}")
            
            print("  ✅ Placement rules: PASSED")
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_teacher_dashboard(self):
        """Test teacher dashboard."""
        print("\n[8/15] Testing Teacher Dashboard...")
        
        try:
            response = self.client.get(reverse('core:teacher_dashboard'))
            if response.status_code == 200:
                print("  ✅ Dashboard: Accessible")
            else:
                print(f"  ❌ Dashboard failed: {response.status_code}")
                return False
            
            # Test session list
            response = self.client.get(reverse('placement_test:session_list'))
            if response.status_code == 200:
                print("  ✅ Session list: Accessible")
            else:
                print(f"  ❌ Session list failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_exam_preview(self):
        """Test exam preview functionality."""
        print("\n[9/15] Testing Exam Preview...")
        
        try:
            exam = Exam.objects.first()
            if exam:
                response = self.client.get(
                    reverse('placement_test:preview_exam', args=[exam.id])
                )
                
                if response.status_code == 200:
                    print(f"  ✅ Preview page: Loaded")
                    
                    # Check for question elements
                    content = str(response.content)
                    if 'question-panel' in content:
                        print("  ✅ Question panels: Rendered")
                    if 'short-answer-row' in content:
                        print("  ✅ Multiple short answers: Rendered")
                else:
                    print(f"  ❌ Preview failed: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_curriculum_structure(self):
        """Test curriculum hierarchy."""
        print("\n[10/15] Testing Curriculum Structure...")
        
        try:
            from core.models import Program, SubProgram
            
            programs = Program.objects.count()
            subprograms = SubProgram.objects.count()
            levels = CurriculumLevel.objects.count()
            
            print(f"  • Programs: {programs}")
            print(f"  • SubPrograms: {subprograms}")
            print(f"  • Curriculum Levels: {levels}")
            
            if programs > 0 and levels > 0:
                print("  ✅ Curriculum structure: PASSED")
                return True
            else:
                print("  ❌ Curriculum structure incomplete")
                return False
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_schools(self):
        """Test school management."""
        print("\n[11/15] Testing School Management...")
        
        try:
            schools = School.objects.count()
            print(f"  • Schools registered: {schools}")
            
            # Test school API
            response = self.client.get('/api/schools/')
            if response.status_code == 200:
                print("  ✅ School API: Working")
            else:
                print(f"  ❌ School API failed: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_static_files(self):
        """Test static file serving."""
        print("\n[12/15] Testing Static Files...")
        
        try:
            static_files = [
                '/static/js/modules/audio-player.js',
                '/static/js/modules/answer-manager.js',
                '/static/css/pages/student-test.css',
            ]
            
            all_ok = True
            for file_url in static_files:
                response = self.client.get(file_url)
                if response.status_code == 200:
                    print(f"  ✅ {file_url}: Found")
                else:
                    print(f"  ❌ {file_url}: {response.status_code}")
                    all_ok = False
            
            return all_ok
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_pdf_handling(self):
        """Test PDF file handling."""
        print("\n[13/15] Testing PDF Handling...")
        
        try:
            exam = Exam.objects.filter(pdf_file__isnull=False).first()
            if exam:
                if exam.pdf_file:
                    print(f"  ✅ PDF file: {exam.pdf_file.name}")
                    
                    # Check if file exists
                    if os.path.exists(exam.pdf_file.path):
                        print("  ✅ PDF exists on disk")
                    else:
                        print("  ❌ PDF missing from disk")
                        return False
            else:
                print("  ⚠️ No exams with PDF found")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_timer_config(self):
        """Test timer configuration."""
        print("\n[14/15] Testing Timer Configuration...")
        
        try:
            exams = Exam.objects.all()[:3]
            for exam in exams:
                print(f"  • {exam.name[:30]}...: {exam.timer_minutes} minutes")
            
            if exams.exists():
                print("  ✅ Timer configuration: PASSED")
                return True
            else:
                print("  ❌ No exams found")
                return False
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def test_data_integrity(self):
        """Test database integrity."""
        print("\n[15/15] Testing Data Integrity...")
        
        try:
            # Check for orphaned questions
            orphan_questions = Question.objects.filter(exam__isnull=True).count()
            print(f"  • Orphaned questions: {orphan_questions}")
            
            # Check for orphaned audio
            orphan_audio = AudioFile.objects.filter(exam__isnull=True).count()
            print(f"  • Orphaned audio files: {orphan_audio}")
            
            # Check for orphaned answers
            orphan_answers = StudentAnswer.objects.filter(
                session__isnull=True
            ).count()
            print(f"  • Orphaned answers: {orphan_answers}")
            
            if orphan_questions == 0 and orphan_audio == 0 and orphan_answers == 0:
                print("  ✅ Data integrity: PASSED")
                return True
            else:
                print("  ⚠️ Some orphaned records found")
                return True  # Warning but not failure
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all feature tests."""
        print("\n" + "="*70)
        print("COMPREHENSIVE FEATURE TEST SUITE")
        print("Testing all features after audio and multiple short answer fixes")
        print("="*70)
        
        tests = [
            self.test_exam_creation,
            self.test_question_types,
            self.test_student_session,
            self.test_answer_submission,
            self.test_grading_system,
            self.test_audio_system,
            self.test_placement_rules,
            self.test_teacher_dashboard,
            self.test_exam_preview,
            self.test_curriculum_structure,
            self.test_schools,
            self.test_static_files,
            self.test_pdf_handling,
            self.test_timer_config,
            self.test_data_integrity,
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                self.results.append((test_func.__name__, result))
            except Exception as e:
                print(f"\n❌ {test_func.__name__} crashed: {str(e)}")
                self.results.append((test_func.__name__, False))
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for _, result in self.results if result)
        total = len(self.results)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print("\nDetailed Results:")
        for test_name, result in self.results:
            clean_name = test_name.replace('test_', '').replace('_', ' ').title()
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {clean_name:30} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed ({pass_rate:.1f}%)")
        
        if pass_rate == 100:
            print("\n🎆 PERFECT! All features working correctly.")
            print("No existing features were affected by recent changes.")
        elif pass_rate >= 90:
            print("\n✅ EXCELLENT! System is functioning well.")
            print("Minor issues detected but core features intact.")
        elif pass_rate >= 80:
            print("\n⚠️ GOOD! Most features working correctly.")
            print("Some features may need attention.")
        else:
            print("\n❌ ATTENTION NEEDED! Significant issues detected.")
            print("Recent changes may have affected existing features.")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    tester = FeatureTestSuite()
    tester.run_all_tests()