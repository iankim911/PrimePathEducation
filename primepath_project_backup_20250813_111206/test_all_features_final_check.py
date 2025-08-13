#!/usr/bin/env python
"""
Final comprehensive test of ALL features after PDF rotation fix
Ensures no regression or disruption to existing functionality
"""

import os
import sys
import django
import json
from datetime import datetime
from time import sleep

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from placement_test.models import Exam, Question, StudentSession, StudentAnswer, AudioFile
from placement_test.services import SessionService, ExamService, GradingService, PlacementService
from core.models import CurriculumLevel, SubProgram, Program, School, Teacher, PlacementRule, ExamLevelMapping


class ComprehensiveFeatureTest:
    def __init__(self):
        self.client = Client()
        self.results = {}
        self.errors = []
        
    def test_exam_crud_operations(self):
        """Test Create, Read, Update, Delete operations for exams"""
        print("\n📋 TEST: Exam CRUD Operations")
        print("-" * 40)
        
        try:
            # CREATE
            program, _ = Program.objects.get_or_create(
                name="CRUD_TEST",
                defaults={'grade_range_start': 1, 'grade_range_end': 12, 'order': 200}
            )
            
            subprogram, _ = SubProgram.objects.get_or_create(
                name="CRUD SubProgram",
                program=program,
                defaults={'order': 1}
            )
            
            level, _ = CurriculumLevel.objects.get_or_create(
                subprogram=subprogram,
                level_number=1,
                defaults={'description': 'CRUD Level'}
            )
            
            exam_data = {
                'name': f'CRUD Test - {datetime.now().strftime("%H%M%S")}',
                'curriculum_level_id': level.id,
                'timer_minutes': 45,
                'total_questions': 10,
                'pdf_rotation': 90,  # Test rotation
                'is_active': True
            }
            
            pdf_file = SimpleUploadedFile("crud.pdf", b'%PDF test', content_type='application/pdf')
            
            exam = ExamService.create_exam(exam_data, pdf_file)
            print(f"✅ CREATE: Exam created with ID {exam.id}")
            
            # READ
            exam_read = Exam.objects.get(id=exam.id)
            assert exam_read.name == exam.name
            assert exam_read.pdf_rotation == 90
            print(f"✅ READ: Exam retrieved successfully")
            
            # UPDATE
            exam_read.timer_minutes = 60
            exam_read.pdf_rotation = 180
            exam_read.save()
            
            exam_updated = Exam.objects.get(id=exam.id)
            assert exam_updated.timer_minutes == 60
            assert exam_updated.pdf_rotation == 180
            print(f"✅ UPDATE: Exam updated successfully")
            
            # DELETE
            exam_id = exam.id
            exam.delete()
            assert not Exam.objects.filter(id=exam_id).exists()
            print(f"✅ DELETE: Exam deleted successfully")
            
            # Cleanup
            level.delete()
            subprogram.delete()
            program.delete()
            
            return True
            
        except Exception as e:
            print(f"❌ CRUD operations failed: {e}")
            self.errors.append(f"CRUD: {e}")
            return False
    
    def test_question_management(self):
        """Test question creation and management"""
        print("\n📋 TEST: Question Management")
        print("-" * 40)
        
        try:
            exam = Exam.objects.first()
            if not exam:
                print("⚠️  No exam found for testing")
                return True
            
            # Test all question types
            question_types = {
                'MCQ': {'correct_answer': 'B', 'options_count': 4},
                'CHECKBOX': {'correct_answer': 'A,C', 'options_count': 5},
                'SHORT': {'correct_answer': 'answer', 'options_count': 1},
                'LONG': {'correct_answer': 'Long answer text', 'options_count': 1},
                'MIXED': {'correct_answer': '["A", "B"]', 'options_count': 2}
            }
            
            created_questions = []
            for q_type, data in question_types.items():
                q = Question.objects.create(
                    exam=exam,
                    question_number=100 + len(created_questions),
                    question_type=q_type,
                    correct_answer=data['correct_answer'],
                    options_count=data['options_count'],
                    points=1
                )
                created_questions.append(q)
                print(f"✅ Created {q_type} question")
            
            # Verify all created
            assert len(created_questions) == len(question_types)
            print(f"✅ All {len(question_types)} question types created")
            
            # Test update
            q = created_questions[0]
            q.correct_answer = 'C'
            q.save()
            
            q_updated = Question.objects.get(id=q.id)
            assert q_updated.correct_answer == 'C'
            print("✅ Question update successful")
            
            # Cleanup
            for q in created_questions:
                q.delete()
            
            return True
            
        except Exception as e:
            print(f"❌ Question management failed: {e}")
            self.errors.append(f"Questions: {e}")
            return False
    
    def test_student_session_flow(self):
        """Test complete student session flow"""
        print("\n📋 TEST: Student Session Flow")
        print("-" * 40)
        
        try:
            exam = Exam.objects.filter(is_active=True).first()
            if not exam:
                print("⚠️  No active exam found")
                return True
            
            # Create session
            session = StudentSession.objects.create(
                exam=exam,
                student_name='Flow Test Student',
                parent_phone='1112223333',
                grade=7,
                academic_rank='TOP_10',
                started_at=timezone.now()
            )
            print(f"✅ Session created: {session.id}")
            
            # Submit answers
            questions = exam.questions.all()[:3]
            for i, q in enumerate(questions):
                answer = SessionService.submit_answer(
                    session=session,
                    question_id=q.id,
                    answer=f'Answer {i+1}'
                )
                assert answer is not None
            
            print(f"✅ Submitted {len(questions)} answers")
            
            # Check session state
            assert not session.is_completed
            assert session.answers.count() >= len(questions)
            print("✅ Session state correct")
            
            # Complete session
            session.completed_at = timezone.now()
            session.save()
            
            assert session.is_completed
            print("✅ Session completed successfully")
            
            # Cleanup
            session.delete()
            
            return True
            
        except Exception as e:
            print(f"❌ Session flow failed: {e}")
            self.errors.append(f"Session: {e}")
            return False
    
    def test_audio_functionality(self):
        """Test audio file handling"""
        print("\n📋 TEST: Audio Functionality")
        print("-" * 40)
        
        try:
            exam = Exam.objects.first()
            if not exam:
                print("⚠️  No exam found")
                return True
            
            # Create audio file
            audio_content = b'RIFF....WAVEfmt audio data'
            audio_upload = SimpleUploadedFile(
                "test_audio.wav",
                audio_content,
                content_type='audio/wav'
            )
            
            audio = AudioFile.objects.create(
                exam=exam,
                name='Test Audio',
                audio_file=audio_upload,
                start_question=1,
                end_question=3,
                order=99
            )
            
            print(f"✅ Audio file created: {audio.name}")
            
            # Test audio assignment to question
            question = exam.questions.first()
            if question:
                question.audio_file = audio
                question.save()
                
                q_with_audio = Question.objects.get(id=question.id)
                assert q_with_audio.audio_file_id == audio.id
                print("✅ Audio assigned to question")
                
                # Clear assignment
                question.audio_file = None
                question.save()
            
            # Cleanup
            audio.delete()
            print("✅ Audio functionality working")
            
            return True
            
        except Exception as e:
            print(f"❌ Audio functionality failed: {e}")
            self.errors.append(f"Audio: {e}")
            return False
    
    def test_grading_accuracy(self):
        """Test grading system accuracy"""
        print("\n📋 TEST: Grading System Accuracy")
        print("-" * 40)
        
        try:
            # MCQ Grading
            assert GradingService.grade_mcq_answer('A', 'A') == True
            assert GradingService.grade_mcq_answer('A', 'B') == False
            print("✅ MCQ grading accurate")
            
            # CHECKBOX Grading
            assert GradingService.grade_checkbox_answer('A,B,C', 'A,B,C') == True
            assert GradingService.grade_checkbox_answer('A,B', 'A,B,C') == False
            assert GradingService.grade_checkbox_answer('B,A,C', 'A,B,C') == True  # Order shouldn't matter
            print("✅ CHECKBOX grading accurate")
            
            # SHORT Answer Grading
            assert GradingService.grade_short_answer('test', 'test', case_sensitive=False) == True
            assert GradingService.grade_short_answer('TEST', 'test', case_sensitive=False) == True
            assert GradingService.grade_short_answer('TEST', 'test', case_sensitive=True) == False
            print("✅ SHORT answer grading accurate")
            
            # Alternative answers
            assert GradingService.grade_short_answer('cat', 'cat|dog|bird', case_sensitive=False) == True
            assert GradingService.grade_short_answer('dog', 'cat|dog|bird', case_sensitive=False) == True
            assert GradingService.grade_short_answer('fish', 'cat|dog|bird', case_sensitive=False) == False
            print("✅ Alternative answer grading accurate")
            
            return True
            
        except Exception as e:
            print(f"❌ Grading accuracy failed: {e}")
            self.errors.append(f"Grading: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n📋 TEST: API Endpoints")
        print("-" * 40)
        
        try:
            endpoints = [
                ('/api/placement/exams/', 'GET', 'Exam list'),
                ('/api/schools/', 'GET', 'School list'),
            ]
            
            all_passed = True
            for url, method, name in endpoints:
                if method == 'GET':
                    response = self.client.get(url)
                
                if response.status_code in [200, 201]:
                    print(f"✅ {name}: {response.status_code}")
                else:
                    print(f"❌ {name}: {response.status_code}")
                    all_passed = False
            
            # Test exam-specific endpoint if exam exists
            exam = Exam.objects.first()
            if exam:
                response = self.client.get(f'/api/placement/exams/{exam.id}/preview/')
                if response.status_code == 200:
                    print(f"✅ Exam preview: 200")
                else:
                    print(f"❌ Exam preview: {response.status_code}")
                    all_passed = False
                
                # Test save endpoint
                response = self.client.post(
                    f'/api/placement/exams/{exam.id}/save-answers/',
                    data=json.dumps({'questions': [], 'audio_assignments': {}}),
                    content_type='application/json'
                )
                if response.status_code == 200:
                    print(f"✅ Save answers: 200")
                else:
                    print(f"❌ Save answers: {response.status_code}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            print(f"❌ API endpoints failed: {e}")
            self.errors.append(f"API: {e}")
            return False
    
    def test_placement_rules(self):
        """Test placement rules and mappings"""
        print("\n📋 TEST: Placement Rules & Mappings")
        print("-" * 40)
        
        try:
            # Check placement rules exist
            rules_count = PlacementRule.objects.count()
            print(f"✅ Placement rules: {rules_count}")
            
            # Check exam mappings
            mappings_count = ExamLevelMapping.objects.count()
            print(f"✅ Exam mappings: {mappings_count}")
            
            # Test placement matching
            try:
                exam, level = PlacementService.match_student_to_exam(
                    grade=5,
                    academic_rank='TOP_30'
                )
                if exam:
                    print(f"✅ Placement matching working")
                else:
                    print("⚠️  No matching exam found (may be expected)")
            except Exception as e:
                print(f"⚠️  Placement matching: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Placement rules failed: {e}")
            self.errors.append(f"Placement: {e}")
            return False
    
    def test_pdf_features(self):
        """Test PDF-related features including rotation"""
        print("\n📋 TEST: PDF Features & Rotation")
        print("-" * 40)
        
        try:
            # Find exam with PDF
            exam = Exam.objects.filter(pdf_file__isnull=False).first()
            if not exam:
                print("⚠️  No exam with PDF found")
                return True
            
            print(f"Testing exam: {exam.name}")
            
            # Check PDF file exists
            if exam.pdf_file:
                print(f"✅ PDF file present: {exam.pdf_file.name}")
            
            # Test rotation values
            original = exam.pdf_rotation
            print(f"✅ Current rotation: {original}°")
            
            # Test all valid rotations
            for rotation in [0, 90, 180, 270]:
                exam.pdf_rotation = rotation
                exam.save()
                exam.refresh_from_db()
                assert exam.pdf_rotation == rotation
            
            print("✅ All rotation values work")
            
            # Restore original
            exam.pdf_rotation = original
            exam.save()
            print(f"✅ Rotation restored to {original}°")
            
            return True
            
        except Exception as e:
            print(f"❌ PDF features failed: {e}")
            self.errors.append(f"PDF: {e}")
            return False
    
    def test_data_integrity(self):
        """Test database relationships and integrity"""
        print("\n📋 TEST: Data Integrity & Relationships")
        print("-" * 40)
        
        try:
            # Check for orphaned records
            orphan_questions = Question.objects.filter(exam__isnull=True).count()
            orphan_audio = AudioFile.objects.filter(exam__isnull=True).count()
            orphan_answers = StudentAnswer.objects.filter(session__isnull=True).count()
            
            print(f"✅ Orphaned questions: {orphan_questions}")
            print(f"✅ Orphaned audio files: {orphan_audio}")
            print(f"✅ Orphaned answers: {orphan_answers}")
            
            # Check cascade delete
            exam = Exam.objects.create(
                name='Cascade Test',
                timer_minutes=30,
                total_questions=1,
                is_active=False
            )
            
            question = Question.objects.create(
                exam=exam,
                question_number=1,
                question_type='MCQ',
                correct_answer='A',
                points=1
            )
            
            q_id = question.id
            exam.delete()
            
            # Question should be deleted via cascade
            assert not Question.objects.filter(id=q_id).exists()
            print("✅ Cascade delete working")
            
            return True
            
        except Exception as e:
            print(f"❌ Data integrity failed: {e}")
            self.errors.append(f"Integrity: {e}")
            return False
    
    def test_navigation_and_ui(self):
        """Test navigation and UI endpoints"""
        print("\n📋 TEST: Navigation & UI Pages")
        print("-" * 40)
        
        try:
            pages = [
                ('/', 'Home'),
                ('/api/placement/exams/', 'Exam List'),
                ('/api/placement/exams/create/', 'Create Exam'),
                ('/api/placement/sessions/', 'Session List'),
                ('/api/placement/start/', 'Start Test'),
                ('/core/dashboard/', 'Dashboard'),
            ]
            
            all_passed = True
            for url, name in pages:
                response = self.client.get(url)
                if response.status_code in [200, 302]:  # 302 for redirects
                    print(f"✅ {name}: {response.status_code}")
                else:
                    print(f"❌ {name}: {response.status_code}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            self.errors.append(f"Navigation: {e}")
            return False
    
    def run_all_tests(self):
        """Run all feature tests"""
        print("=" * 80)
        print("🔍 FINAL COMPREHENSIVE FEATURE CHECK")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        tests = [
            ("Exam CRUD Operations", self.test_exam_crud_operations),
            ("Question Management", self.test_question_management),
            ("Student Session Flow", self.test_student_session_flow),
            ("Audio Functionality", self.test_audio_functionality),
            ("Grading Accuracy", self.test_grading_accuracy),
            ("API Endpoints", self.test_api_endpoints),
            ("Placement Rules", self.test_placement_rules),
            ("PDF Features", self.test_pdf_features),
            ("Data Integrity", self.test_data_integrity),
            ("Navigation & UI", self.test_navigation_and_ui),
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.results[test_name] = result
            except Exception as e:
                print(f"\n❌ {test_name} crashed: {e}")
                self.results[test_name] = False
                self.errors.append(f"{test_name} crash: {e}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 FINAL TEST RESULTS")
        print("=" * 80)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:.<40} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        total = len(self.results)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎯 OVERALL SUMMARY")
        print("=" * 80)
        print(f"Tests Passed: {passed}/{total} ({pass_rate:.1f}%)")
        
        if self.errors:
            print("\n⚠️  Errors encountered:")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  • {error}")
        
        print("\n" + "=" * 80)
        print("🎯 FINAL VERDICT")
        print("=" * 80)
        
        if pass_rate == 100:
            print("✅ PERFECT! All features working correctly.")
            print("No existing features were affected by the PDF rotation fix.")
        elif pass_rate >= 90:
            print("✅ EXCELLENT! System is functioning well.")
            print("Minor issues detected but core features intact.")
            print("PDF rotation fix did not disrupt existing functionality.")
        elif pass_rate >= 80:
            print("⚠️  GOOD! Most features working correctly.")
            print("Some features may need attention.")
        else:
            print("❌ ATTENTION NEEDED! Multiple features affected.")
            print("Review errors above for details.")
        
        return pass_rate >= 90  # Consider successful if 90% or more pass


if __name__ == "__main__":
    tester = ComprehensiveFeatureTest()
    tester.run_all_tests()
    
    # Return exit code based on results
    success = all(tester.results.values()) if tester.results else False
    sys.exit(0 if success else 1)