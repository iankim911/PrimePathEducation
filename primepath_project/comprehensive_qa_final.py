#!/usr/bin/env python
"""
COMPREHENSIVE QA TEST - Final Verification
Tests all critical features after AudioFile field fix
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.db import connection
from placement_test.models import Exam, Question, AudioFile, StudentSession, StudentAnswer, DifficultyAdjustment
from core.models import CurriculumLevel, Program, SubProgram, PlacementRule, ExamLevelMapping
import json

print("="*80)
print("COMPREHENSIVE QA TEST - FINAL VERIFICATION")
print(f"Timestamp: {datetime.now()}")
print("="*80)

class ComprehensiveQA:
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'errors': []
        }
        self.client = Client()
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results"""
        self.results['total_tests'] += 1
        print(f"\n📝 {test_name}...")
        try:
            result = test_func()
            if result:
                self.results['passed'] += 1
                print(f"   ✅ PASSED")
                return True
            else:
                self.results['failed'] += 1
                print(f"   ❌ FAILED")
                return False
        except Exception as e:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {str(e)}")
            print(f"   ❌ ERROR: {str(e)}")
            return False
    
    def test_models_exist(self):
        """Test that all critical models exist and are accessible"""
        models = [
            Exam, Question, AudioFile, StudentSession, StudentAnswer,
            DifficultyAdjustment, CurriculumLevel, Program, SubProgram, 
            PlacementRule, ExamLevelMapping
        ]
        for model in models:
            try:
                count = model.objects.count()
                print(f"     {model.__name__}: {count} records")
            except Exception as e:
                print(f"     ❌ {model.__name__}: {e}")
                return False
        return True
    
    def test_audiofile_field_access(self):
        """Test AudioFile field is correctly accessible"""
        # Try to access an AudioFile
        audio = AudioFile.objects.first()
        if audio:
            try:
                # Correct field name
                if hasattr(audio, 'audio_file'):
                    print(f"     ✓ audio.audio_file accessible")
                else:
                    print(f"     × audio.audio_file not found")
                    return False
                
                # Incorrect field name should fail
                if hasattr(audio, 'file'):
                    print(f"     × audio.file should not exist")
                    return False
                else:
                    print(f"     ✓ audio.file correctly does not exist")
                
                return True
            except Exception as e:
                print(f"     Error: {e}")
                return False
        else:
            print(f"     ⚠️ No AudioFile records to test")
            return True
    
    def test_exam_creation(self):
        """Test exam creation with questions"""
        level = CurriculumLevel.objects.first()
        if not level:
            print(f"     ⚠️ No curriculum levels")
            return True
        
        exam = Exam.objects.create(
            name="QA Test Exam",
            curriculum_level=level,
            timer_minutes=30,
            total_questions=3,
            is_active=True
        )
        
        # Create questions
        for i in range(1, 4):
            Question.objects.create(
                exam=exam,
                question_number=i,
                question_type='MCQ',
                points=2,
                correct_answer="A"
            )
        
        success = exam.questions.count() == 3
        
        # Clean up
        exam.delete()
        
        return success
    
    def test_mixed_mcq_options(self):
        """Test MIXED MCQ options_count field"""
        mixed = Question.objects.filter(question_type='MIXED').first()
        if mixed:
            if hasattr(mixed, 'options_count'):
                original = mixed.options_count
                # Test modification
                mixed.options_count = 7
                mixed.save()
                mixed.refresh_from_db()
                success = mixed.options_count == 7
                # Restore
                mixed.options_count = original
                mixed.save()
                print(f"     ✓ MIXED MCQ options_count working")
                return success
            else:
                print(f"     × options_count field missing")
                return False
        else:
            print(f"     ⚠️ No MIXED questions found")
            return True
    
    def test_difficulty_adjustment(self):
        """Test difficulty adjustment model"""
        try:
            count = DifficultyAdjustment.objects.count()
            print(f"     ✓ DifficultyAdjustment model exists ({count} records)")
            
            # Check fields exist
            session = StudentSession.objects.first()
            if session:
                has_fields = all([
                    hasattr(session, 'original_curriculum_level'),
                    hasattr(session, 'final_curriculum_level'),
                    hasattr(session, 'difficulty_adjustments')
                ])
                if has_fields:
                    print(f"     ✓ Session tracking fields present")
                    return True
                else:
                    print(f"     × Session tracking fields missing")
                    return False
            return True
        except Exception as e:
            print(f"     × Error: {e}")
            return False
    
    def test_exam_deletion_with_audio(self):
        """Test exam deletion with audio files"""
        level = CurriculumLevel.objects.first()
        if not level:
            print(f"     ⚠️ No curriculum levels")
            return True
        
        # Create exam with audio
        exam = Exam.objects.create(
            name="Deletion Test Exam",
            curriculum_level=level,
            timer_minutes=30,
            total_questions=1,
            is_active=True
        )
        
        # Create audio file (without actual file)
        audio = AudioFile.objects.create(
            exam=exam,
            name="Test Audio",
            audio_file=None,
            start_question=1,
            end_question=1
        )
        audio_id = audio.id
        exam_id = exam.id
        
        # Delete exam
        exam.delete()
        
        # Check cascades
        exam_exists = Exam.objects.filter(id=exam_id).exists()
        audio_exists = AudioFile.objects.filter(id=audio_id).exists()
        
        if not exam_exists and not audio_exists:
            print(f"     ✓ Cascade deletion working")
            return True
        else:
            print(f"     × Cascade deletion failed")
            return False
    
    def test_api_serialization(self):
        """Test API serialization of AudioFile"""
        try:
            from api.v1.serializers import AudioFileSerializer
            
            audio = AudioFile.objects.first()
            if audio:
                serializer = AudioFileSerializer(audio)
                data = serializer.data
                
                # Check correct field is present
                if 'audio_file' in data:
                    print(f"     ✓ Serializer has correct field")
                    return True
                else:
                    print(f"     × Serializer missing audio_file field")
                    return False
            else:
                print(f"     ⚠️ No audio files to test")
                return True
        except Exception as e:
            print(f"     × Error: {e}")
            return False
    
    def test_question_audio_relationship(self):
        """Test Question -> AudioFile relationship"""
        questions_with_audio = Question.objects.filter(audio_file__isnull=False).count()
        print(f"     ✓ {questions_with_audio} questions have audio assignments")
        
        # Test assignment
        question = Question.objects.filter(audio_file__isnull=True).first()
        audio = AudioFile.objects.first()
        
        if question and audio:
            question.audio_file = audio
            question.save()
            question.refresh_from_db()
            
            success = question.audio_file == audio
            
            # Clean up
            question.audio_file = None
            question.save()
            
            if success:
                print(f"     ✓ Audio assignment working")
            else:
                print(f"     × Audio assignment failed")
            
            return success
        else:
            print(f"     ⚠️ No suitable test data")
            return True
    
    def test_student_workflow(self):
        """Test complete student workflow"""
        exam = Exam.objects.filter(is_active=True).first()
        if not exam:
            print(f"     ⚠️ No active exams")
            return True
        
        level = exam.curriculum_level or CurriculumLevel.objects.first()
        
        # Create session
        session = StudentSession.objects.create(
            student_name="QA Test Student",
            grade=5,
            academic_rank="TOP_20",
            exam=exam,
            original_curriculum_level=level,
            final_curriculum_level=level
        )
        
        # Create answer
        question = exam.questions.first()
        if question:
            answer = StudentAnswer.objects.create(
                session=session,
                question=question,
                answer="Test Answer"
            )
            
            # Complete session
            from django.utils import timezone
            session.completed_at = timezone.now()
            session.save()
            
            success = session.answers.count() > 0
            
            # Clean up
            session.delete()
            
            if success:
                print(f"     ✓ Student workflow complete")
            else:
                print(f"     × Student workflow failed")
            
            return success
        else:
            print(f"     ⚠️ No questions in exam")
            session.delete()
            return True
    
    def test_url_endpoints(self):
        """Test critical URL endpoints"""
        endpoints = [
            ('/api/placement/exams/', 'Exam API'),
            ('/teacher/dashboard/', 'Teacher Dashboard'),
            ('/placement-rules/', 'Placement Rules'),
            ('/exam-mapping/', 'Exam Mapping'),
        ]
        
        all_ok = True
        for url, name in endpoints:
            try:
                response = self.client.get(url)
                if response.status_code in [200, 302]:
                    print(f"     ✓ {name}: {response.status_code}")
                else:
                    print(f"     × {name}: {response.status_code}")
                    all_ok = False
            except Exception as e:
                print(f"     × {name}: {e}")
                all_ok = False
        
        return all_ok
    
    def test_database_integrity(self):
        """Test database integrity and relationships"""
        with connection.cursor() as cursor:
            # Check for orphaned records
            checks = [
                ("Questions without exams", 
                 "SELECT COUNT(*) FROM placement_test_question WHERE exam_id NOT IN (SELECT id FROM placement_test_exam)"),
                ("Audio files without exams",
                 "SELECT COUNT(*) FROM placement_test_audiofile WHERE exam_id NOT IN (SELECT id FROM placement_test_exam)"),
                ("Answers without sessions",
                 "SELECT COUNT(*) FROM placement_test_studentanswer WHERE session_id NOT IN (SELECT id FROM placement_test_studentsession)"),
            ]
            
            all_ok = True
            for check_name, query in checks:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                if count == 0:
                    print(f"     ✓ {check_name}: None found")
                else:
                    print(f"     × {check_name}: {count} orphaned records")
                    all_ok = False
            
            return all_ok
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("\n" + "="*60)
        print("RUNNING COMPREHENSIVE TESTS")
        print("="*60)
        
        tests = [
            ("Model Existence Check", self.test_models_exist),
            ("AudioFile Field Access", self.test_audiofile_field_access),
            ("Exam Creation", self.test_exam_creation),
            ("MIXED MCQ Options", self.test_mixed_mcq_options),
            ("Difficulty Adjustment", self.test_difficulty_adjustment),
            ("Exam Deletion with Audio", self.test_exam_deletion_with_audio),
            ("API Serialization", self.test_api_serialization),
            ("Question-Audio Relationship", self.test_question_audio_relationship),
            ("Student Workflow", self.test_student_workflow),
            ("URL Endpoints", self.test_url_endpoints),
            ("Database Integrity", self.test_database_integrity),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']} ({self.results['passed']/self.results['total_tests']*100:.1f}%)")
        print(f"Failed: {self.results['failed']}")
        print(f"Warnings: {self.results['warnings']}")
        
        if self.results['errors']:
            print("\nErrors:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        # Final verdict
        if self.results['failed'] == 0:
            print("\n" + "🎉 "*20)
            print("✅ ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL")
            print("🎉 "*20)
        else:
            print(f"\n⚠️ {self.results['failed']} tests failed - review needed")
        
        print("="*60)
        
        # Save results
        with open('comprehensive_qa_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: comprehensive_qa_results.json")
        
        return self.results['failed'] == 0

if __name__ == '__main__':
    qa = ComprehensiveQA()
    success = qa.run_all_tests()
    sys.exit(0 if success else 1)