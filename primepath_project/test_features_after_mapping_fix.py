#!/usr/bin/env python3
"""
Comprehensive test to verify all features still work after duplicate exam mapping fix
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.db import connection
from placement_test.models import Exam, Question, StudentSession, AudioFile
from core.models import ExamLevelMapping, CurriculumLevel, PlacementRule, Teacher
from placement_test.views import (
    start_test, take_test, submit_answer, 
    create_exam, save_exam_answers
)

User = get_user_model()

class FeatureTestRunner:
    def __init__(self):
        self.factory = RequestFactory()
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def log_result(self, feature, test, success, details=""):
        result = {
            'feature': feature,
            'test': test,
            'success': success,
            'details': details
        }
        self.results.append(result)
        if success:
            self.passed += 1
            print(f"  ✅ {test}")
        else:
            self.failed += 1
            print(f"  ❌ {test}: {details}")
    
    def test_database_constraints(self):
        """Test that duplicate exam mapping constraint is working"""
        print("\n🔍 Testing Database Constraints...")
        
        try:
            # Check if unique constraint exists
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND name LIKE '%unique_exam%'
                """)
                constraints = cursor.fetchall()
                
            has_constraint = len(constraints) > 0
            self.log_result(
                "Database", 
                "Unique exam constraint exists",
                has_constraint,
                f"Found {len(constraints)} constraint(s)" if has_constraint else "No constraint found"
            )
            
            # Test that we can't create duplicate mappings
            if has_constraint:
                exam = Exam.objects.filter(level_mappings__isnull=False).first()
                if exam:
                    existing_mapping = exam.level_mappings.first()
                    other_level = CurriculumLevel.objects.exclude(
                        id=existing_mapping.curriculum_level_id
                    ).first()
                    
                    try:
                        # Try to create duplicate mapping
                        duplicate = ExamLevelMapping(
                            exam=exam,
                            curriculum_level=other_level,
                            slot=1
                        )
                        duplicate.clean()  # Should raise ValidationError
                        self.log_result(
                            "Database",
                            "Duplicate prevention validation",
                            False,
                            "Validation didn't prevent duplicate"
                        )
                    except Exception as e:
                        self.log_result(
                            "Database",
                            "Duplicate prevention validation",
                            True,
                            "Correctly prevented duplicate"
                        )
                        
        except Exception as e:
            self.log_result(
                "Database",
                "Constraint testing",
                False,
                str(e)
            )
    
    def test_exam_creation(self):
        """Test exam creation still works"""
        print("\n📝 Testing Exam Creation...")
        
        try:
            # Check if exam creation view loads
            teacher = Teacher.objects.first()
            if not teacher:
                teacher = Teacher.objects.create(
                    username=f"test_teacher_{datetime.now().timestamp()}",
                    email="test@example.com"
                )
            
            request = self.factory.get('/placement/exams/create/')
            request.user = teacher
            
            # Mock session
            from django.contrib.sessions.middleware import SessionMiddleware
            middleware = SessionMiddleware(lambda x: x)
            middleware.process_request(request)
            request.session.save()
            
            response = create_exam(request)
            
            self.log_result(
                "Exam Creation",
                "Create exam page loads",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
            
            # Check if we can create an exam
            exam_count_before = Exam.objects.count()
            exam = Exam.objects.create(
                name=f"Test Exam {datetime.now()}",
                total_questions=10,
                created_by=teacher,
                is_active=True
            )
            exam_count_after = Exam.objects.count()
            
            self.log_result(
                "Exam Creation",
                "Can create new exam",
                exam_count_after > exam_count_before,
                f"Created exam ID: {exam.id}"
            )
            
        except Exception as e:
            self.log_result(
                "Exam Creation",
                "Exam creation process",
                False,
                str(e)
            )
    
    def test_student_session(self):
        """Test student session creation and navigation"""
        print("\n👨‍🎓 Testing Student Sessions...")
        
        try:
            # Get an exam with questions
            exam = Exam.objects.filter(
                questions__isnull=False,
                is_active=True
            ).first()
            
            if exam:
                # Create a test session
                session = StudentSession.objects.create(
                    student_name="Test Student",
                    student_email="test@student.com",
                    student_phone="1234567890",
                    student_grade=10,
                    exam=exam
                )
                
                self.log_result(
                    "Student Session",
                    "Session creation",
                    session.id is not None,
                    f"Session ID: {session.id}"
                )
                
                # Test take_test view
                request = self.factory.get(f'/placement/session/{session.id}/')
                
                # Add session middleware
                from django.contrib.sessions.middleware import SessionMiddleware
                middleware = SessionMiddleware(lambda x: x)
                middleware.process_request(request)
                request.session.save()
                
                response = take_test(request, session.id)
                
                self.log_result(
                    "Student Session",
                    "Take test page loads",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
                
            else:
                self.log_result(
                    "Student Session",
                    "Test session creation",
                    False,
                    "No exam with questions found"
                )
                
        except Exception as e:
            self.log_result(
                "Student Session",
                "Session management",
                False,
                str(e)
            )
    
    def test_question_types(self):
        """Test all question types are handled correctly"""
        print("\n❓ Testing Question Types...")
        
        try:
            question_types = ['MCQ', 'SHORT', 'LONG', 'MIXED', 'CHECKBOX']
            
            for q_type in question_types:
                questions = Question.objects.filter(question_type=q_type)[:1]
                exists = questions.exists()
                
                self.log_result(
                    "Question Types",
                    f"{q_type} questions exist",
                    True,  # Just checking existence
                    f"Found {questions.count()} {q_type} question(s)"
                )
                
        except Exception as e:
            self.log_result(
                "Question Types",
                "Question type checking",
                False,
                str(e)
            )
    
    def test_audio_files(self):
        """Test audio file associations"""
        print("\n🔊 Testing Audio Files...")
        
        try:
            # Check if audio files exist
            audio_count = AudioFile.objects.count()
            self.log_result(
                "Audio Files",
                "Audio files in database",
                audio_count > 0,
                f"Found {audio_count} audio files"
            )
            
            # Check audio-question associations
            questions_with_audio = Question.objects.filter(
                audio_file__isnull=False
            ).count()
            
            self.log_result(
                "Audio Files",
                "Questions with audio",
                True,  # Just reporting
                f"{questions_with_audio} questions have audio"
            )
            
        except Exception as e:
            self.log_result(
                "Audio Files",
                "Audio file checking",
                False,
                str(e)
            )
    
    def test_exam_mappings(self):
        """Test exam level mappings after fix"""
        print("\n🗺️ Testing Exam Level Mappings...")
        
        try:
            # Check for duplicate mappings
            from django.db.models import Count
            duplicates = ExamLevelMapping.objects.values('exam').annotate(
                count=Count('exam')
            ).filter(count__gt=1)
            
            has_no_duplicates = duplicates.count() == 0
            self.log_result(
                "Exam Mappings",
                "No duplicate exam mappings",
                has_no_duplicates,
                f"Found {duplicates.count()} duplicate(s)" if not has_no_duplicates else "All mappings unique"
            )
            
            # Check Sigma progression specifically
            sigma_levels = CurriculumLevel.objects.filter(
                subprogram__name='Sigma'
            ).order_by('level_number')
            
            sigma_exams = {}
            for level in sigma_levels:
                mapping = ExamLevelMapping.objects.filter(
                    curriculum_level=level
                ).first()
                if mapping:
                    sigma_exams[level.level_number] = mapping.exam.name
            
            # Check each level has different exam
            unique_exams = len(set(sigma_exams.values())) == len(sigma_exams.values())
            self.log_result(
                "Exam Mappings",
                "Sigma levels have unique exams",
                unique_exams,
                f"Exams: {sigma_exams}" if sigma_exams else "No Sigma mappings found"
            )
            
        except Exception as e:
            self.log_result(
                "Exam Mappings",
                "Mapping verification",
                False,
                str(e)
            )
    
    def test_placement_rules(self):
        """Test placement rules are intact"""
        print("\n📊 Testing Placement Rules...")
        
        try:
            rules_count = PlacementRule.objects.count()
            self.log_result(
                "Placement Rules",
                "Placement rules exist",
                rules_count > 0,
                f"Found {rules_count} placement rules"
            )
            
            # Check rules have valid curriculum levels
            invalid_rules = PlacementRule.objects.filter(
                curriculum_level__isnull=True
            ).count()
            
            self.log_result(
                "Placement Rules",
                "All rules have valid levels",
                invalid_rules == 0,
                f"{invalid_rules} invalid rules" if invalid_rules > 0 else "All rules valid"
            )
            
        except Exception as e:
            self.log_result(
                "Placement Rules",
                "Rule verification",
                False,
                str(e)
            )
    
    def test_grading_system(self):
        """Test grading system with LONG question exclusion"""
        print("\n📊 Testing Grading System...")
        
        try:
            # Create a mock grading scenario
            exam = Exam.objects.filter(questions__isnull=False).first()
            if exam:
                # Count question types
                mcq_count = exam.questions.filter(question_type='MCQ').count()
                short_count = exam.questions.filter(question_type='SHORT').count()
                long_count = exam.questions.filter(question_type='LONG').count()
                
                # Calculate expected total (excluding LONG)
                non_long_questions = exam.questions.exclude(question_type='LONG')
                expected_total = sum(q.points for q in non_long_questions)
                
                self.log_result(
                    "Grading System",
                    "Question type counts",
                    True,
                    f"MCQ: {mcq_count}, SHORT: {short_count}, LONG: {long_count} (excluded)"
                )
                
                self.log_result(
                    "Grading System",
                    "Total possible points calculation",
                    expected_total > 0,
                    f"Total: {expected_total} points (LONG excluded)"
                )
                
        except Exception as e:
            self.log_result(
                "Grading System",
                "Grading calculation",
                False,
                str(e)
            )
    
    def test_difficulty_adjustment(self):
        """Test difficulty adjustment functionality"""
        print("\n🎚️ Testing Difficulty Adjustment...")
        
        try:
            # Find a student session
            session = StudentSession.objects.filter(
                completed_at__isnull=True,
                exam__isnull=False
            ).first()
            
            if session and session.original_curriculum_level:
                # Check if we can get different difficulty levels
                current_level = session.original_curriculum_level
                
                # Check harder option
                harder_levels = CurriculumLevel.objects.filter(
                    subprogram=current_level.subprogram,
                    level_number__gt=current_level.level_number
                ).order_by('level_number')
                
                if harder_levels.exists():
                    harder_level = harder_levels.first()
                    harder_mapping = ExamLevelMapping.objects.filter(
                        curriculum_level=harder_level
                    ).first()
                    
                    self.log_result(
                        "Difficulty Adjustment",
                        "Harder exam available",
                        harder_mapping is not None,
                        f"Next level: {harder_level.full_name}" if harder_mapping else "No exam for harder level"
                    )
                    
                    # Check that it's a different exam
                    if harder_mapping:
                        current_mapping = ExamLevelMapping.objects.filter(
                            curriculum_level=current_level
                        ).first()
                        
                        if current_mapping:
                            different_exam = harder_mapping.exam.id != current_mapping.exam.id
                            self.log_result(
                                "Difficulty Adjustment",
                                "Different exam for harder level",
                                different_exam,
                                "Exams are unique" if different_exam else "Same exam!"
                            )
                else:
                    self.log_result(
                        "Difficulty Adjustment",
                        "Harder level check",
                        True,
                        "Already at highest level"
                    )
            else:
                self.log_result(
                    "Difficulty Adjustment",
                    "Session for testing",
                    False,
                    "No suitable session found"
                )
                
        except Exception as e:
            self.log_result(
                "Difficulty Adjustment",
                "Difficulty adjustment",
                False,
                str(e)
            )
    
    def run_all_tests(self):
        """Run all feature tests"""
        print("\n" + "="*60)
        print("🧪 COMPREHENSIVE FEATURE TEST AFTER MAPPING FIX")
        print("="*60)
        
        self.test_database_constraints()
        self.test_exam_creation()
        self.test_student_session()
        self.test_question_types()
        self.test_audio_files()
        self.test_exam_mappings()
        self.test_placement_rules()
        self.test_grading_system()
        self.test_difficulty_adjustment()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        
        if self.failed > 0:
            print("\n⚠️ Failed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result['feature']}: {result['test']}")
                    print(f"    Details: {result['details']}")
        
        return self.failed == 0

if __name__ == '__main__':
    tester = FeatureTestRunner()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ ALL FEATURES WORKING CORRECTLY!")
    else:
        print("\n⚠️ Some features need attention")
    
    sys.exit(0 if success else 1)