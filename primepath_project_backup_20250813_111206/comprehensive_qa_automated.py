#!/usr/bin/env python3
"""
Comprehensive Automated QA Process for PrimePath Level Test Tool
Date: August 11, 2025
Purpose: Full system validation including recent fixes
"""

import os
import sys
import django
import json
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.db import connection

# Import models
from placement_test.models import (
    Exam, Question, StudentSession, AudioFile, 
    StudentAnswer, DifficultyAdjustment
)
from core.models import School, Teacher, Program, SubProgram, CurriculumLevel, PlacementRule, ExamLevelMapping

class ComprehensiveQAValidator:
    """Comprehensive QA validation for all features"""
    
    def __init__(self):
        self.client = Client()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'phase_results': {},
            'critical_issues': [],
            'warnings': [],
            'success_count': 0,
            'failure_count': 0,
            'test_details': []
        }
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results['test_details'].append(result)
        
        if status == 'PASS':
            self.results['success_count'] += 1
            print(f"✅ {test_name}")
        else:
            self.results['failure_count'] += 1
            print(f"❌ {test_name}: {details}")
            if status == 'CRITICAL':
                self.results['critical_issues'].append(result)
            else:
                self.results['warnings'].append(result)
    
    def phase1_database_analysis(self):
        """Phase 1: Database and Model Analysis"""
        print("\n" + "="*60)
        print("PHASE 1: DATABASE AND MODEL ANALYSIS")
        print("="*60)
        
        phase_results = {
            'model_counts': {},
            'relationships': {},
            'integrity_checks': []
        }
        
        try:
            # Model counts
            phase_results['model_counts'] = {
                'Exams': Exam.objects.count(),
                'Questions': Question.objects.count(),
                'StudentSessions': StudentSession.objects.count(),
                'AudioFiles': AudioFile.objects.count(),
                'StudentAnswers': StudentAnswer.objects.count(),
                'DifficultyAdjustments': DifficultyAdjustment.objects.count(),
                'Schools': School.objects.count(),
                'Teachers': Teacher.objects.count(),
                'Programs': Program.objects.count(),
                'PlacementRules': PlacementRule.objects.count(),
                'ExamLevelMappings': ExamLevelMapping.objects.count()
            }
            
            for model, count in phase_results['model_counts'].items():
                self.log_test(f"Model {model}", 'PASS', f"Count: {count}")
            
            # Check relationships
            exam = Exam.objects.first()
            if exam:
                phase_results['relationships']['exam_sample'] = {
                    'name': exam.name,
                    'questions': exam.questions.count(),
                    'audio_files': exam.audio_files.count(),
                    'sessions': exam.sessions.count()
                }
                self.log_test("Exam Relationships", 'PASS', 
                            f"Exam '{exam.name}' has {exam.questions.count()} questions")
            
            # Check foreign key integrity
            orphaned_questions = Question.objects.filter(exam__isnull=True).count()
            orphaned_answers = StudentAnswer.objects.filter(session__isnull=True).count()
            
            if orphaned_questions == 0:
                self.log_test("Question Integrity", 'PASS', "No orphaned questions")
            else:
                self.log_test("Question Integrity", 'WARNING', f"{orphaned_questions} orphaned questions")
            
            if orphaned_answers == 0:
                self.log_test("Answer Integrity", 'PASS', "No orphaned answers")
            else:
                self.log_test("Answer Integrity", 'WARNING', f"{orphaned_answers} orphaned answers")
                
        except Exception as e:
            self.log_test("Database Analysis", 'FAIL', str(e))
            
        self.results['phase_results']['phase1'] = phase_results
        
    def phase2_recent_fixes_validation(self):
        """Phase 2: Validate Recent Fixes"""
        print("\n" + "="*60)
        print("PHASE 2: RECENT FIXES VALIDATION")
        print("="*60)
        
        phase_results = {
            'timer_fix': {},
            'pdf_rotation': {},
            'answer_submission': {},
            'short_answer': {}
        }
        
        # Test 1: Timer Expiry Grace Period Fix
        try:
            exam = Exam.objects.filter(time_limit__gt=0).first()
            if exam:
                session = StudentSession.objects.create(
                    exam=exam,
                    student_name="Timer Test",
                    student_email="timer@test.com",
                    student_phone="555-0001",
                    started_at=timezone.now() - timedelta(minutes=exam.time_limit + 1)
                )
                
                # Check timer methods
                is_expired = session.is_timer_expired()
                in_grace = session.is_in_grace_period()
                can_accept = session.can_accept_answers()
                
                phase_results['timer_fix'] = {
                    'expired': is_expired,
                    'in_grace_period': in_grace,
                    'can_accept_answers': can_accept
                }
                
                if is_expired and in_grace and can_accept:
                    self.log_test("Timer Grace Period", 'PASS', 
                                "Timer expired but still in grace period")
                else:
                    self.log_test("Timer Grace Period", 'FAIL', 
                                f"Expired: {is_expired}, Grace: {in_grace}, Accept: {can_accept}")
                
                session.delete()
            else:
                self.log_test("Timer Grace Period", 'SKIP', "No timed exams available")
                
        except Exception as e:
            self.log_test("Timer Grace Period", 'FAIL', str(e))
        
        # Test 2: PDF Rotation Persistence
        try:
            exam = Exam.objects.filter(pdf_file__isnull=False).first()
            if exam:
                if hasattr(exam, 'pdf_rotation'):
                    self.log_test("PDF Rotation Field", 'PASS', 
                                f"Rotation: {exam.pdf_rotation} degrees")
                    phase_results['pdf_rotation']['field_exists'] = True
                    phase_results['pdf_rotation']['value'] = exam.pdf_rotation
                else:
                    self.log_test("PDF Rotation Field", 'WARNING', 
                                "pdf_rotation field not found")
                    phase_results['pdf_rotation']['field_exists'] = False
            else:
                self.log_test("PDF Rotation", 'SKIP', "No exams with PDFs")
                
        except Exception as e:
            self.log_test("PDF Rotation", 'FAIL', str(e))
        
        # Test 3: Answer Submission
        try:
            session = StudentSession.objects.filter(completed_at__isnull=True).first()
            if session:
                # Test answer save endpoint
                response = self.client.post(
                    f'/placement/api/sessions/{session.id}/submit-answer/',
                    data=json.dumps({
                        'question_id': session.exam.questions.first().id,
                        'answer': 'Test Answer'
                    }),
                    content_type='application/json'
                )
                
                if response.status_code == 200:
                    self.log_test("Answer Submission API", 'PASS', "Answer saved successfully")
                    phase_results['answer_submission']['api_works'] = True
                else:
                    self.log_test("Answer Submission API", 'FAIL', 
                                f"Status: {response.status_code}")
                    phase_results['answer_submission']['api_works'] = False
            else:
                self.log_test("Answer Submission", 'SKIP', "No active sessions")
                
        except Exception as e:
            self.log_test("Answer Submission", 'FAIL', str(e))
        
        # Test 4: Short Answer Display
        try:
            short_answer_q = Question.objects.filter(
                question_type='SHORT'
            ).first()
            
            if short_answer_q:
                self.log_test("Short Answer Questions", 'PASS', 
                            f"Found {Question.objects.filter(question_type='SHORT').count()} SHORT questions")
                phase_results['short_answer']['exists'] = True
            else:
                self.log_test("Short Answer Questions", 'INFO', "No SHORT questions in database")
                phase_results['short_answer']['exists'] = False
                
        except Exception as e:
            self.log_test("Short Answer Display", 'FAIL', str(e))
            
        self.results['phase_results']['phase2'] = phase_results
    
    def phase3_url_endpoint_validation(self):
        """Phase 3: URL and Endpoint Validation"""
        print("\n" + "="*60)
        print("PHASE 3: URL AND ENDPOINT VALIDATION")
        print("="*60)
        
        phase_results = {
            'endpoints': [],
            'api_endpoints': []
        }
        
        # Critical URLs to test
        urls_to_test = [
            ('/', 'Homepage'),
            ('/placement/', 'Placement Test Main'),
            ('/placement/start-test/', 'Start Test'),
            ('/placement/create-exam/', 'Create Exam'),
            ('/core/', 'Core Dashboard'),
            ('/admin/', 'Admin Interface'),
            ('/api/', 'API Root'),
        ]
        
        for url, name in urls_to_test:
            try:
                response = self.client.get(url, follow=True)
                status = response.status_code
                
                result = {
                    'url': url,
                    'name': name,
                    'status_code': status,
                    'success': status in [200, 301, 302]
                }
                phase_results['endpoints'].append(result)
                
                if result['success']:
                    self.log_test(f"URL {name}", 'PASS', f"Status: {status}")
                else:
                    self.log_test(f"URL {name}", 'FAIL', f"Status: {status}")
                    
            except Exception as e:
                self.log_test(f"URL {name}", 'FAIL', str(e))
        
        # Test API endpoints
        api_endpoints = [
            ('/api/placement/exams/', 'Exams API'),
            ('/api/placement/sessions/', 'Sessions API'),
            ('/api/core/schools/', 'Schools API'),
            ('/api/core/programs/', 'Programs API'),
        ]
        
        for url, name in api_endpoints:
            try:
                response = self.client.get(url)
                status = response.status_code
                
                result = {
                    'url': url,
                    'name': name,
                    'status_code': status,
                    'success': status in [200, 201]
                }
                phase_results['api_endpoints'].append(result)
                
                if result['success']:
                    self.log_test(f"API {name}", 'PASS', f"Status: {status}")
                else:
                    self.log_test(f"API {name}", 'WARNING', f"Status: {status}")
                    
            except Exception as e:
                self.log_test(f"API {name}", 'FAIL', str(e))
        
        self.results['phase_results']['phase3'] = phase_results
    
    def phase4_feature_functionality(self):
        """Phase 4: Core Feature Functionality Testing"""
        print("\n" + "="*60)
        print("PHASE 4: CORE FEATURE FUNCTIONALITY")
        print("="*60)
        
        phase_results = {
            'exam_creation': {},
            'student_test': {},
            'difficulty_adjustment': {},
            'placement_rules': {}
        }
        
        # Test Exam Creation Flow
        try:
            # Create test user
            user = User.objects.create_user(
                username='qa_teacher',
                password='qa_pass123'
            )
            teacher = Teacher.objects.create(
                user=user,
                school=School.objects.first() or School.objects.create(name="QA School"),
                full_name="QA Teacher"
            )
            
            # Login
            self.client.login(username='qa_teacher', password='qa_pass123')
            
            # Try to create exam
            exam_data = {
                'name': 'QA Test Exam',
                'description': 'Automated QA Test',
                'time_limit': 60,
                'is_passing_mandatory': False
            }
            
            response = self.client.post('/placement/create-exam/', data=exam_data)
            
            if response.status_code in [200, 302]:
                self.log_test("Exam Creation", 'PASS', "Exam creation endpoint works")
                phase_results['exam_creation']['works'] = True
            else:
                self.log_test("Exam Creation", 'FAIL', f"Status: {response.status_code}")
                phase_results['exam_creation']['works'] = False
            
            # Cleanup
            user.delete()
            
        except Exception as e:
            self.log_test("Exam Creation", 'FAIL', str(e))
        
        # Test Difficulty Adjustment
        try:
            adjustments = DifficultyAdjustment.objects.all()
            if adjustments.exists():
                self.log_test("Difficulty Adjustments", 'PASS', 
                            f"Found {adjustments.count()} adjustments")
                phase_results['difficulty_adjustment']['exists'] = True
                
                # Check naming conventions
                sample = adjustments.first()
                if hasattr(sample, 'internal_difficulty'):
                    self.log_test("Internal Difficulty Field", 'PASS', "Field exists")
                    phase_results['difficulty_adjustment']['internal_field'] = True
                else:
                    self.log_test("Internal Difficulty Field", 'INFO', "Using standard field name")
                    phase_results['difficulty_adjustment']['internal_field'] = False
            else:
                self.log_test("Difficulty Adjustments", 'INFO', "No adjustments configured")
                
        except Exception as e:
            self.log_test("Difficulty Adjustments", 'FAIL', str(e))
        
        # Test Placement Rules
        try:
            rules = PlacementRule.objects.all()
            if rules.exists():
                self.log_test("Placement Rules", 'PASS', f"Found {rules.count()} rules")
                phase_results['placement_rules']['count'] = rules.count()
            else:
                self.log_test("Placement Rules", 'WARNING', "No placement rules configured")
                phase_results['placement_rules']['count'] = 0
                
        except Exception as e:
            self.log_test("Placement Rules", 'FAIL', str(e))
        
        self.results['phase_results']['phase4'] = phase_results
    
    def phase5_performance_validation(self):
        """Phase 5: Performance and Query Optimization"""
        print("\n" + "="*60)
        print("PHASE 5: PERFORMANCE VALIDATION")
        print("="*60)
        
        phase_results = {
            'query_counts': {},
            'response_times': [],
            'database_stats': {}
        }
        
        from django.test.utils import override_settings
        from django.db import reset_queries
        from time import time
        
        # Test query optimization for exam list
        try:
            reset_queries()
            start = time()
            
            exams = Exam.objects.prefetch_related('questions', 'audio_files').all()
            for exam in exams[:5]:  # Test first 5
                _ = exam.questions.count()
                _ = exam.audio_files.count()
            
            elapsed = time() - start
            query_count = len(connection.queries)
            
            phase_results['query_counts']['exam_list'] = query_count
            phase_results['response_times'].append({
                'operation': 'exam_list',
                'time': elapsed,
                'queries': query_count
            })
            
            if query_count < 10:  # Should be optimized
                self.log_test("Exam List Optimization", 'PASS', 
                            f"{query_count} queries in {elapsed:.2f}s")
            else:
                self.log_test("Exam List Optimization", 'WARNING', 
                            f"High query count: {query_count}")
                
        except Exception as e:
            self.log_test("Performance Testing", 'FAIL', str(e))
        
        # Database statistics
        try:
            with connection.cursor() as cursor:
                # SQLite specific stats
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
                index_count = cursor.fetchone()[0]
                
                phase_results['database_stats'] = {
                    'tables': table_count,
                    'indexes': index_count
                }
                
                self.log_test("Database Structure", 'PASS', 
                            f"{table_count} tables, {index_count} indexes")
                
        except Exception as e:
            self.log_test("Database Stats", 'WARNING', str(e))
        
        self.results['phase_results']['phase5'] = phase_results
    
    def phase6_security_validation(self):
        """Phase 6: Security and Data Integrity"""
        print("\n" + "="*60)
        print("PHASE 6: SECURITY VALIDATION")
        print("="*60)
        
        phase_results = {
            'csrf_protection': False,
            'auth_required': [],
            'data_validation': []
        }
        
        # Test CSRF protection
        try:
            response = self.client.post('/placement/create-exam/', 
                                      data={'name': 'test'}, 
                                      HTTP_X_CSRFTOKEN='invalid')
            
            if response.status_code == 403:
                self.log_test("CSRF Protection", 'PASS', "CSRF validation active")
                phase_results['csrf_protection'] = True
            else:
                self.log_test("CSRF Protection", 'WARNING', 
                            f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_test("CSRF Protection", 'FAIL', str(e))
        
        # Test authentication requirements
        auth_urls = [
            '/placement/create-exam/',
            '/core/dashboard/',
            '/api/placement/exams/'
        ]
        
        self.client.logout()  # Ensure logged out
        
        for url in auth_urls:
            try:
                response = self.client.get(url)
                if response.status_code in [302, 403, 401]:
                    self.log_test(f"Auth Required {url}", 'PASS', "Protected")
                    phase_results['auth_required'].append({'url': url, 'protected': True})
                else:
                    self.log_test(f"Auth Required {url}", 'WARNING', "Not protected")
                    phase_results['auth_required'].append({'url': url, 'protected': False})
                    
            except Exception as e:
                self.log_test(f"Auth Check {url}", 'FAIL', str(e))
        
        self.results['phase_results']['phase6'] = phase_results
    
    def generate_report(self):
        """Generate comprehensive QA report"""
        print("\n" + "="*60)
        print("QA REPORT SUMMARY")
        print("="*60)
        
        print(f"\n📊 Test Results:")
        print(f"  ✅ Passed: {self.results['success_count']}")
        print(f"  ❌ Failed: {self.results['failure_count']}")
        print(f"  ⚠️  Warnings: {len(self.results['warnings'])}")
        print(f"  🚨 Critical Issues: {len(self.results['critical_issues'])}")
        
        if self.results['critical_issues']:
            print(f"\n🚨 Critical Issues Found:")
            for issue in self.results['critical_issues']:
                print(f"  - {issue['test']}: {issue['details']}")
        
        if self.results['warnings']:
            print(f"\n⚠️  Warnings:")
            for warning in self.results['warnings'][:5]:  # Show first 5
                print(f"  - {warning['test']}: {warning['details']}")
        
        # Save detailed report
        report_path = Path('qa_report_automated.json')
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Generate recommendations
        print("\n📋 Recommendations:")
        
        if self.results['failure_count'] == 0:
            print("  ✅ All tests passed! System is functioning correctly.")
        else:
            print("  1. Review and fix critical issues immediately")
            print("  2. Address warnings to prevent future problems")
            print("  3. Re-run tests after fixes")
        
        if 'phase5' in self.results['phase_results']:
            perf_data = self.results['phase_results']['phase5']
            if 'query_counts' in perf_data:
                for op, count in perf_data['query_counts'].items():
                    if count > 10:
                        print(f"  - Optimize queries for {op} (currently {count} queries)")
        
        return self.results
    
    def run_all_phases(self):
        """Execute all QA phases"""
        print("\n" + "="*60)
        print("PRIMEPATH COMPREHENSIVE QA PROCESS")
        print(f"Started: {datetime.now()}")
        print("="*60)
        
        try:
            self.phase1_database_analysis()
            self.phase2_recent_fixes_validation()
            self.phase3_url_endpoint_validation()
            self.phase4_feature_functionality()
            self.phase5_performance_validation()
            self.phase6_security_validation()
            
        except Exception as e:
            print(f"\n❌ Fatal error during QA: {e}")
            traceback.print_exc()
            self.results['critical_issues'].append({
                'test': 'QA Process',
                'details': f'Fatal error: {str(e)}'
            })
        
        return self.generate_report()


if __name__ == "__main__":
    print("🚀 Starting Comprehensive QA Process...")
    
    validator = ComprehensiveQAValidator()
    results = validator.run_all_phases()
    
    # Exit code based on results
    if results['failure_count'] > 0 or results['critical_issues']:
        sys.exit(1)
    else:
        sys.exit(0)