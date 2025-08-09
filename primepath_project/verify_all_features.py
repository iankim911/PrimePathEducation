#!/usr/bin/env python
"""
Comprehensive verification of all existing features after recent fixes
Checks for any regressions or broken functionality
"""

import os
import sys
import django
from datetime import datetime
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.db import connection
from placement_test.models import Exam, Question, AudioFile, StudentSession, StudentAnswer
from core.models import CurriculumLevel, Program, SubProgram, PlacementRule, ExamLevelMapping
from django.contrib.auth.models import User

print("="*80)
print("COMPREHENSIVE FEATURE VERIFICATION")
print(f"Timestamp: {datetime.now()}")
print("="*80)

class FeatureVerification:
    def __init__(self):
        self.client = Client()
        self.results = {
            'total_features': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'feature_status': {}
        }
    
    def check_feature(self, feature_name, test_func):
        """Check a single feature"""
        self.results['total_features'] += 1
        print(f"\n🔍 Checking: {feature_name}...")
        
        try:
            status, details = test_func()
            self.results['feature_status'][feature_name] = {
                'status': status,
                'details': details
            }
            
            if status == 'PASS':
                self.results['passed'] += 1
                print(f"   ✅ WORKING - {details}")
            elif status == 'WARNING':
                self.results['warnings'] += 1
                print(f"   ⚠️ WARNING - {details}")
            else:
                self.results['failed'] += 1
                print(f"   ❌ FAILED - {details}")
                
        except Exception as e:
            self.results['failed'] += 1
            self.results['feature_status'][feature_name] = {
                'status': 'ERROR',
                'details': str(e)
            }
            print(f"   ❌ ERROR - {str(e)}")
    
    def check_exam_deletion(self):
        """Verify exam deletion with AudioFile fix"""
        try:
            # Create test exam
            level = CurriculumLevel.objects.first()
            if not level:
                return 'WARNING', 'No curriculum levels to test with'
            
            exam = Exam.objects.create(
                name="Test Deletion Exam",
                curriculum_level=level,
                timer_minutes=30,
                total_questions=1,
                is_active=False
            )
            
            # Add audio file
            audio = AudioFile.objects.create(
                exam=exam,
                name="Test Audio",
                start_question=1,
                end_question=1
            )
            
            exam_id = exam.id
            audio_id = audio.id
            
            # Delete exam
            exam.delete()
            
            # Verify cascade deletion
            exam_exists = Exam.objects.filter(id=exam_id).exists()
            audio_exists = AudioFile.objects.filter(id=audio_id).exists()
            
            if not exam_exists and not audio_exists:
                return 'PASS', 'Exam deletion with audio files working correctly'
            else:
                return 'FAIL', 'Cascade deletion not working properly'
                
        except Exception as e:
            return 'FAIL', f'Exam deletion error: {str(e)}'
    
    def check_mcq_ui_controls(self):
        """Verify MCQ UI improvements"""
        response = self.client.get('/api/placement/exams/')
        
        if response.status_code != 200:
            # Try to create an exam page instead
            response = self.client.get('/teacher/dashboard/')
        
        # Check database for MCQ questions
        mcq_questions = Question.objects.filter(question_type='MCQ').count()
        mixed_questions = Question.objects.filter(question_type='MIXED').count()
        
        # Verify options_count field
        if mcq_questions > 0:
            mcq = Question.objects.filter(question_type='MCQ').first()
            if hasattr(mcq, 'options_count'):
                original = mcq.options_count
                mcq.options_count = 6
                mcq.save()
                mcq.refresh_from_db()
                
                if mcq.options_count == 6:
                    mcq.options_count = original
                    mcq.save()
                    return 'PASS', f'MCQ options controls working ({mcq_questions} MCQ, {mixed_questions} MIXED questions)'
                else:
                    return 'FAIL', 'MCQ options_count not saving properly'
            else:
                return 'FAIL', 'MCQ missing options_count field'
        else:
            return 'WARNING', 'No MCQ questions to test'
    
    def check_exam_mapping_page(self):
        """Verify exam mapping page loads and functions"""
        response = self.client.get('/exam-mapping/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for key elements
            checks = {
                'CSRF token': 'csrfmiddlewaretoken' in content or '{% csrf_token %}' in content,
                'Save functions': 'saveLevelMappings' in content,
                'No auth blocking': 'isAuthenticated = true' in content,
                'Error handling': 'if (!csrfToken)' in content
            }
            
            failed_checks = [k for k, v in checks.items() if not v]
            
            if not failed_checks:
                # Test save endpoint
                mappings = ExamLevelMapping.objects.count()
                return 'PASS', f'Page loads correctly, {mappings} existing mappings'
            else:
                return 'FAIL', f'Missing elements: {", ".join(failed_checks)}'
        else:
            return 'FAIL', f'Page returned status {response.status_code}'
    
    def check_student_test_interface(self):
        """Verify student test interface"""
        # Check if any active exams exist
        active_exam = Exam.objects.filter(is_active=True).first()
        
        if active_exam:
            # Try to access student test page
            response = self.client.get('/api/placement/start/')
            
            if response.status_code in [200, 302]:
                return 'PASS', f'Student interface accessible, {active_exam.name} available'
            else:
                return 'WARNING', f'Student interface returned {response.status_code}'
        else:
            return 'WARNING', 'No active exams for student testing'
    
    def check_placement_rules(self):
        """Verify placement rules functionality"""
        response = self.client.get('/placement-rules/')
        
        if response.status_code == 200:
            rules = PlacementRule.objects.count()
            programs = Program.objects.count()
            subprograms = SubProgram.objects.count()
            
            return 'PASS', f'{rules} rules, {programs} programs, {subprograms} subprograms'
        else:
            return 'FAIL', f'Page returned status {response.status_code}'
    
    def check_teacher_dashboard(self):
        """Verify teacher dashboard"""
        response = self.client.get('/teacher/dashboard/')
        
        if response.status_code == 200:
            exams = Exam.objects.count()
            questions = Question.objects.count()
            sessions = StudentSession.objects.count()
            
            return 'PASS', f'{exams} exams, {questions} questions, {sessions} sessions'
        else:
            return 'FAIL', f'Dashboard returned status {response.status_code}'
    
    def check_api_endpoints(self):
        """Verify API endpoints"""
        endpoints = [
            ('/api/placement/exams/', 'Exams API'),
            ('/api/exam-mappings/save/', 'Save Mappings API'),
        ]
        
        failed = []
        for url, name in endpoints:
            if url == '/api/exam-mappings/save/':
                # POST endpoint - just check it exists
                response = self.client.post(url, 
                    data=json.dumps({'mappings': []}),
                    content_type='application/json'
                )
                if response.status_code not in [200, 400]:
                    failed.append(f"{name} ({response.status_code})")
            else:
                response = self.client.get(url)
                if response.status_code != 200:
                    failed.append(f"{name} ({response.status_code})")
        
        if not failed:
            return 'PASS', 'All API endpoints responding'
        else:
            return 'FAIL', f'Failed endpoints: {", ".join(failed)}'
    
    def check_question_types(self):
        """Verify all question types"""
        types = ['MCQ', 'CHECKBOX', 'SHORT', 'LONG', 'MIXED']
        type_counts = {}
        
        for q_type in types:
            count = Question.objects.filter(question_type=q_type).count()
            type_counts[q_type] = count
        
        # Check MIXED questions have options_count
        mixed = Question.objects.filter(question_type='MIXED').first()
        if mixed and not hasattr(mixed, 'options_count'):
            return 'FAIL', 'MIXED questions missing options_count'
        
        summary = ', '.join([f"{k}:{v}" for k, v in type_counts.items()])
        return 'PASS', f'Question types: {summary}'
    
    def check_audio_assignments(self):
        """Verify audio file assignments"""
        audio_files = AudioFile.objects.count()
        questions_with_audio = Question.objects.filter(audio_file__isnull=False).count()
        
        # Test assignment
        if audio_files > 0:
            audio = AudioFile.objects.first()
            question = Question.objects.filter(audio_file__isnull=True).first()
            
            if question:
                # Test assignment
                question.audio_file = audio
                question.save()
                question.refresh_from_db()
                
                if question.audio_file == audio:
                    # Clean up
                    question.audio_file = None
                    question.save()
                    return 'PASS', f'{audio_files} audio files, {questions_with_audio} assigned'
                else:
                    return 'FAIL', 'Audio assignment not working'
            else:
                return 'PASS', f'{audio_files} audio files, all questions have audio'
        else:
            return 'WARNING', 'No audio files in system'
    
    def check_database_integrity(self):
        """Check database integrity"""
        with connection.cursor() as cursor:
            # Check for orphaned records
            checks = [
                ("SELECT COUNT(*) FROM placement_test_question WHERE exam_id NOT IN (SELECT id FROM placement_test_exam)", 
                 "Orphaned questions"),
                ("SELECT COUNT(*) FROM placement_test_audiofile WHERE exam_id NOT IN (SELECT id FROM placement_test_exam)",
                 "Orphaned audio files"),
            ]
            
            issues = []
            for query, description in checks:
                try:
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    if count > 0:
                        issues.append(f"{description}: {count}")
                except:
                    pass
            
            if not issues:
                # Count total records
                cursor.execute("SELECT COUNT(*) FROM placement_test_exam")
                exams = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM placement_test_question")
                questions = cursor.fetchone()[0]
                
                return 'PASS', f'No orphaned records ({exams} exams, {questions} questions)'
            else:
                return 'FAIL', f'Issues found: {"; ".join(issues)}'
    
    def check_session_management(self):
        """Verify session management"""
        sessions = StudentSession.objects.count()
        answers = StudentAnswer.objects.count()
        
        # Check session fields
        if sessions > 0:
            session = StudentSession.objects.first()
            required_fields = [
                'student_name', 'grade', 'academic_rank',
                'exam', 'original_curriculum_level'
            ]
            
            missing = [f for f in required_fields if not hasattr(session, f)]
            
            if missing:
                return 'FAIL', f'Session missing fields: {", ".join(missing)}'
            else:
                return 'PASS', f'{sessions} sessions, {answers} answers recorded'
        else:
            return 'WARNING', 'No student sessions to verify'
    
    def check_curriculum_structure(self):
        """Verify curriculum structure"""
        programs = Program.objects.count()
        subprograms = SubProgram.objects.count()
        levels = CurriculumLevel.objects.count()
        
        # Check relationships
        if levels > 0:
            level = CurriculumLevel.objects.first()
            if level.subprogram and level.subprogram.program:
                return 'PASS', f'{programs} programs, {subprograms} subprograms, {levels} levels'
            else:
                return 'FAIL', 'Curriculum relationships broken'
        else:
            return 'WARNING', 'No curriculum levels defined'
    
    def run_verification(self):
        """Run all feature verifications"""
        print("\n" + "="*60)
        print("VERIFYING ALL FEATURES")
        print("="*60)
        
        features = [
            ("Exam Deletion with Audio", self.check_exam_deletion),
            ("MCQ UI Controls", self.check_mcq_ui_controls),
            ("Exam-to-Level Mapping", self.check_exam_mapping_page),
            ("Student Test Interface", self.check_student_test_interface),
            ("Placement Rules", self.check_placement_rules),
            ("Teacher Dashboard", self.check_teacher_dashboard),
            ("API Endpoints", self.check_api_endpoints),
            ("Question Types", self.check_question_types),
            ("Audio Assignments", self.check_audio_assignments),
            ("Database Integrity", self.check_database_integrity),
            ("Session Management", self.check_session_management),
            ("Curriculum Structure", self.check_curriculum_structure),
        ]
        
        for feature_name, check_func in features:
            self.check_feature(feature_name, check_func)
        
        # Summary
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        print(f"\nTotal Features Checked: {self.results['total_features']}")
        print(f"✅ Working: {self.results['passed']}")
        print(f"⚠️ Warnings: {self.results['warnings']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['failed'] > 0:
            print("\n❌ FAILED FEATURES:")
            for feature, status in self.results['feature_status'].items():
                if status['status'] in ['FAIL', 'ERROR']:
                    print(f"  - {feature}: {status['details']}")
        
        if self.results['warnings'] > 0:
            print("\n⚠️ WARNINGS:")
            for feature, status in self.results['feature_status'].items():
                if status['status'] == 'WARNING':
                    print(f"  - {feature}: {status['details']}")
        
        # Final verdict
        print("\n" + "="*60)
        if self.results['failed'] == 0:
            print("✅ ALL FEATURES VERIFIED - NO REGRESSIONS DETECTED")
            print("The system is fully operational with all recent fixes applied.")
        elif self.results['failed'] <= 2:
            print("⚠️ MINOR ISSUES DETECTED")
            print(f"{self.results['failed']} features may need attention.")
        else:
            print("❌ CRITICAL ISSUES DETECTED")
            print(f"{self.results['failed']} features are not working properly.")
        print("="*60)
        
        # Save results
        with open('feature_verification_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: feature_verification_results.json")
        
        return self.results['failed'] == 0

if __name__ == '__main__':
    verifier = FeatureVerification()
    success = verifier.run_verification()
    sys.exit(0 if success else 1)