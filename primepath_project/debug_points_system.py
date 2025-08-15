#!/usr/bin/env python3
"""
POINTS SYSTEM DEBUG AND TROUBLESHOOTING UTILITY

This utility provides comprehensive debugging and troubleshooting capabilities
for the PrimePath points editing system. It can be used in production to
diagnose issues, verify data integrity, and provide detailed system health reports.

Usage:
    python debug_points_system.py [command] [options]

Commands:
    health-check        - Comprehensive system health check
    verify-data         - Verify data integrity across all components  
    trace-question      - Trace a specific question through the system
    trace-session       - Trace a specific student session through grading
    performance-profile - Profile system performance
    repair-data         - Attempt to repair common data issues
    export-diagnostics  - Export comprehensive diagnostic data

Examples:
    python debug_points_system.py health-check
    python debug_points_system.py trace-question --question-id 123
    python debug_points_system.py verify-data --fix-issues
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

from django.db import connection, transaction
from django.db.models import Count, Avg, Sum, Min, Max, Q
from django.core.exceptions import ValidationError

from placement_test.models import Question, Exam, StudentSession, StudentAnswer
from placement_test.services.points_service import PointsService
from placement_test.services.grading_service import GradingService

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'points_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger('PointsDebugger')

class PointsSystemDebugger:
    """
    Comprehensive debugging and troubleshooting utility for the points system.
    """
    
    def __init__(self):
        self.issues_found = []
        self.performance_metrics = {}
        self.diagnostic_data = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'health_checks': {},
            'data_integrity': {},
            'performance': {},
            'recommendations': []
        }
    
    def log_issue(self, severity: str, component: str, message: str, details: Dict = None):
        """Log an issue with comprehensive details."""
        issue = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity,  # INFO, WARNING, ERROR, CRITICAL
            'component': component,
            'message': message,
            'details': details or {}
        }
        self.issues_found.append(issue)
        
        log_func = getattr(logger, severity.lower(), logger.info)
        log_func(f"[{component}] {message}")
        
        if details and logger.level <= logging.DEBUG:
            logger.debug(f"[{component}] Details: {json.dumps(details, indent=2, default=str)}")
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive system health check."""
        logger.info("🏥 Starting comprehensive points system health check...")
        
        health_report = {
            'overall_status': 'HEALTHY',
            'checks': {},
            'summary': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Check 1: Database connectivity and basic counts
        try:
            exam_count = Exam.objects.count()
            question_count = Question.objects.count()
            session_count = StudentSession.objects.count()
            answer_count = StudentAnswer.objects.count()
            
            health_report['checks']['database_connectivity'] = {
                'status': 'PASS',
                'exams': exam_count,
                'questions': question_count,
                'sessions': session_count,
                'answers': answer_count
            }
            
            if exam_count == 0:
                self.log_issue('WARNING', 'Database', 'No exams found in system')
                health_report['overall_status'] = 'WARNING'
            
        except Exception as e:
            self.log_issue('CRITICAL', 'Database', f'Database connectivity failed: {e}')
            health_report['checks']['database_connectivity'] = {'status': 'FAIL', 'error': str(e)}
            health_report['overall_status'] = 'CRITICAL'
        
        # Check 2: Points field integrity
        try:
            # Check for questions with invalid points
            invalid_points = Question.objects.filter(
                Q(points__lt=1) | Q(points__gt=10) | Q(points__isnull=True)
            ).count()
            
            points_stats = Question.objects.aggregate(
                avg_points=Avg('points'),
                min_points=Min('points'),
                max_points=Max('points'),
                total_questions=Count('id')
            )
            
            health_report['checks']['points_integrity'] = {
                'status': 'PASS' if invalid_points == 0 else 'FAIL',
                'invalid_points_count': invalid_points,
                'stats': points_stats
            }
            
            if invalid_points > 0:
                self.log_issue('ERROR', 'Points', f'{invalid_points} questions have invalid points values')
                health_report['overall_status'] = 'ERROR'
                
        except Exception as e:
            self.log_issue('ERROR', 'Points', f'Points integrity check failed: {e}')
            health_report['checks']['points_integrity'] = {'status': 'FAIL', 'error': str(e)}
        
        # Check 3: Grading consistency
        try:
            # Check for answers with mismatched points
            mismatched_points = 0
            sample_answers = StudentAnswer.objects.select_related('question').filter(
                is_correct=True
            )[:100]  # Sample for performance
            
            for answer in sample_answers:
                expected_points = answer.question.points
                if answer.points_earned != expected_points:
                    mismatched_points += 1
            
            health_report['checks']['grading_consistency'] = {
                'status': 'PASS' if mismatched_points == 0 else 'WARNING',
                'mismatched_points': mismatched_points,
                'sample_size': sample_answers.count()
            }
            
            if mismatched_points > 0:
                self.log_issue('WARNING', 'Grading', 
                             f'{mismatched_points} answers have mismatched points_earned vs question.points')
                
        except Exception as e:
            self.log_issue('WARNING', 'Grading', f'Grading consistency check failed: {e}')
        
        # Check 4: PointsService functionality
        try:
            # Test basic validation
            is_valid, _, _ = PointsService.validate_points_value(5)
            if not is_valid:
                raise Exception("Basic validation test failed")
            
            # Test analytics generation
            analytics = PointsService.get_points_analytics()
            if not analytics['success']:
                raise Exception(f"Analytics generation failed: {analytics.get('error')}")
            
            health_report['checks']['points_service'] = {
                'status': 'PASS',
                'validation_working': True,
                'analytics_working': True
            }
            
        except Exception as e:
            self.log_issue('ERROR', 'PointsService', f'PointsService functionality check failed: {e}')
            health_report['checks']['points_service'] = {'status': 'FAIL', 'error': str(e)}
        
        # Check 5: Session scoring accuracy
        try:
            # Sample recent sessions for scoring verification
            recent_sessions = StudentSession.objects.filter(
                completed_at__isnull=False,
                completed_at__gte=datetime.now() - timedelta(days=30)
            ).order_by('-completed_at')[:10]
            
            scoring_issues = 0
            for session in recent_sessions:
                # Recalculate score and compare
                answers = session.answers.select_related('question').all()
                calculated_score = sum(
                    answer.points_earned for answer in answers 
                    if answer.question.question_type != 'LONG'
                )
                
                if abs(calculated_score - (session.score or 0)) > 0.1:
                    scoring_issues += 1
                    self.log_issue('WARNING', 'Scoring', 
                                 f'Session {session.id} score mismatch: {session.score} vs {calculated_score}')
            
            health_report['checks']['session_scoring'] = {
                'status': 'PASS' if scoring_issues == 0 else 'WARNING',
                'sessions_checked': recent_sessions.count(),
                'scoring_issues': scoring_issues
            }
            
        except Exception as e:
            self.log_issue('WARNING', 'Scoring', f'Session scoring check failed: {e}')
        
        # Set overall status based on checks
        if any(check.get('status') == 'FAIL' for check in health_report['checks'].values()):
            health_report['overall_status'] = 'CRITICAL'
        elif any(check.get('status') == 'WARNING' for check in health_report['checks'].values()):
            health_report['overall_status'] = 'WARNING'
        
        # Generate summary
        health_report['summary'] = {
            'total_issues': len(self.issues_found),
            'critical_issues': len([i for i in self.issues_found if i['severity'] == 'CRITICAL']),
            'error_issues': len([i for i in self.issues_found if i['severity'] == 'ERROR']),
            'warning_issues': len([i for i in self.issues_found if i['severity'] == 'WARNING']),
        }
        
        self.diagnostic_data['health_checks'] = health_report
        
        logger.info(f"🏥 Health check completed: {health_report['overall_status']}")
        logger.info(f"📊 Found {len(self.issues_found)} total issues")
        
        return health_report
    
    def trace_question(self, question_id: int) -> Dict[str, Any]:
        """Trace a specific question through the entire system."""
        logger.info(f"🔍 Tracing question {question_id} through the system...")
        
        trace_report = {
            'question_id': question_id,
            'timestamp': datetime.now().isoformat(),
            'question_data': {},
            'related_answers': [],
            'grading_analysis': {},
            'point_history': [],
            'issues': []
        }
        
        try:
            # Get question data
            question = Question.objects.select_related('exam').get(id=question_id)
            trace_report['question_data'] = {
                'id': question.id,
                'exam_id': question.exam.id,
                'exam_name': question.exam.name,
                'question_number': question.question_number,
                'question_type': question.question_type,
                'points': question.points,
                'correct_answer': question.correct_answer[:100] + '...' if len(question.correct_answer) > 100 else question.correct_answer,
                'options_count': question.options_count
            }
            
            # Get related answers
            answers = StudentAnswer.objects.select_related('session', 'question').filter(
                question=question
            ).order_by('-session__created_at')
            
            trace_report['related_answers'] = [{
                'session_id': str(answer.session.id),
                'student_name': answer.session.student_name,
                'answer': answer.answer[:50] + '...' if len(answer.answer) > 50 else answer.answer,
                'is_correct': answer.is_correct,
                'points_earned': answer.points_earned,
                'created_at': answer.session.created_at.isoformat() if answer.session.created_at else None
            } for answer in answers[:10]]  # Limit to 10 most recent
            
            # Analyze grading
            correct_answers = answers.filter(is_correct=True).count()
            incorrect_answers = answers.filter(is_correct=False).count()
            null_grading = answers.filter(is_correct__isnull=True).count()
            
            trace_report['grading_analysis'] = {
                'total_answers': answers.count(),
                'correct_answers': correct_answers,
                'incorrect_answers': incorrect_answers,
                'ungraded_answers': null_grading,
                'accuracy_rate': (correct_answers / answers.count() * 100) if answers.count() > 0 else 0
            }
            
            # Check for issues
            if question.points < 1 or question.points > 10:
                trace_report['issues'].append(f"Invalid points value: {question.points}")
            
            if null_grading > 0:
                trace_report['issues'].append(f"{null_grading} answers are ungraded")
            
            # Test current grading for sample answers
            sample_answers = answers[:5]
            grading_test_results = []
            
            for answer in sample_answers:
                try:
                    grade_result = GradingService.auto_grade_answer(answer)
                    grading_test_results.append({
                        'answer_id': answer.id,
                        'current_is_correct': answer.is_correct,
                        'current_points_earned': answer.points_earned,
                        'recalculated_is_correct': grade_result['is_correct'],
                        'recalculated_points_earned': grade_result['points_earned'],
                        'matches': (
                            answer.is_correct == grade_result['is_correct'] and
                            answer.points_earned == grade_result['points_earned']
                        )
                    })
                except Exception as e:
                    grading_test_results.append({
                        'answer_id': answer.id,
                        'error': str(e)
                    })
            
            trace_report['grading_test_results'] = grading_test_results
            
        except Question.DoesNotExist:
            self.log_issue('ERROR', 'Trace', f'Question {question_id} not found')
            trace_report['error'] = f'Question {question_id} not found'
        except Exception as e:
            self.log_issue('ERROR', 'Trace', f'Error tracing question {question_id}: {e}')
            trace_report['error'] = str(e)
        
        logger.info(f"🔍 Question {question_id} trace completed")
        return trace_report
    
    def verify_data_integrity(self, fix_issues: bool = False) -> Dict[str, Any]:
        """Verify data integrity across all system components."""
        logger.info("🔧 Starting comprehensive data integrity verification...")
        
        integrity_report = {
            'timestamp': datetime.now().isoformat(),
            'checks_performed': [],
            'issues_found': [],
            'fixes_applied': [],
            'summary': {}
        }
        
        # Check 1: Orphaned student answers
        logger.info("Checking for orphaned student answers...")
        orphaned_answers = StudentAnswer.objects.filter(question__isnull=True).count()
        if orphaned_answers > 0:
            integrity_report['issues_found'].append({
                'type': 'orphaned_answers',
                'count': orphaned_answers,
                'severity': 'ERROR',
                'description': 'Student answers with no associated question'
            })
            
            if fix_issues:
                deleted_count = StudentAnswer.objects.filter(question__isnull=True).delete()[0]
                integrity_report['fixes_applied'].append({
                    'type': 'deleted_orphaned_answers',
                    'count': deleted_count
                })
        
        # Check 2: Questions with invalid points
        logger.info("Checking for questions with invalid points...")
        invalid_points = Question.objects.filter(
            Q(points__lt=1) | Q(points__gt=10) | Q(points__isnull=True)
        )
        
        if invalid_points.exists():
            for question in invalid_points:
                integrity_report['issues_found'].append({
                    'type': 'invalid_points',
                    'question_id': question.id,
                    'current_points': question.points,
                    'severity': 'ERROR',
                    'description': f'Question {question.id} has invalid points: {question.points}'
                })
                
                if fix_issues:
                    question.points = max(1, min(10, question.points or 1))
                    question.save()
                    integrity_report['fixes_applied'].append({
                        'type': 'fixed_points',
                        'question_id': question.id,
                        'new_points': question.points
                    })
        
        # Check 3: Mismatched points_earned
        logger.info("Checking for mismatched points_earned values...")
        mismatched_answers = []
        for answer in StudentAnswer.objects.select_related('question').filter(
            is_correct=True, question__isnull=False
        )[:100]:  # Sample for performance
            expected_points = answer.question.points
            if answer.points_earned != expected_points:
                mismatched_answers.append({
                    'answer_id': answer.id,
                    'question_id': answer.question.id,
                    'expected_points': expected_points,
                    'actual_points': answer.points_earned
                })
        
        if mismatched_answers:
            integrity_report['issues_found'].append({
                'type': 'mismatched_points_earned',
                'count': len(mismatched_answers),
                'severity': 'WARNING',
                'examples': mismatched_answers[:5]
            })
            
            if fix_issues:
                fixed_count = 0
                for mismatch in mismatched_answers:
                    try:
                        answer = StudentAnswer.objects.get(id=mismatch['answer_id'])
                        answer.points_earned = mismatch['expected_points']
                        answer.save()
                        fixed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to fix answer {mismatch['answer_id']}: {e}")
                
                integrity_report['fixes_applied'].append({
                    'type': 'fixed_points_earned',
                    'count': fixed_count
                })
        
        # Check 4: Session scoring consistency
        logger.info("Checking session scoring consistency...")
        scoring_issues = []
        recent_sessions = StudentSession.objects.filter(
            completed_at__isnull=False
        ).order_by('-completed_at')[:50]
        
        for session in recent_sessions:
            answers = session.answers.select_related('question').all()
            calculated_score = sum(
                answer.points_earned for answer in answers
                if answer.question.question_type != 'LONG'
            )
            
            if abs(calculated_score - (session.score or 0)) > 0.1:
                scoring_issues.append({
                    'session_id': str(session.id),
                    'stored_score': session.score,
                    'calculated_score': calculated_score,
                    'difference': calculated_score - (session.score or 0)
                })
        
        if scoring_issues:
            integrity_report['issues_found'].append({
                'type': 'session_scoring_mismatch',
                'count': len(scoring_issues),
                'severity': 'WARNING',
                'examples': scoring_issues[:5]
            })
            
            if fix_issues:
                fixed_sessions = 0
                for issue in scoring_issues:
                    try:
                        session = StudentSession.objects.get(id=issue['session_id'])
                        session.score = issue['calculated_score']
                        
                        # Recalculate percentage
                        total_possible = sum(
                            answer.question.points for answer in session.answers.select_related('question').all()
                            if answer.question.question_type != 'LONG'
                        )
                        if total_possible > 0:
                            session.percentage_score = (issue['calculated_score'] / total_possible) * 100
                        
                        session.save()
                        fixed_sessions += 1
                    except Exception as e:
                        logger.error(f"Failed to fix session {issue['session_id']}: {e}")
                
                integrity_report['fixes_applied'].append({
                    'type': 'fixed_session_scores',
                    'count': fixed_sessions
                })
        
        # Generate summary
        integrity_report['summary'] = {
            'total_checks': 4,
            'issues_found': len(integrity_report['issues_found']),
            'fixes_applied': len(integrity_report['fixes_applied']),
            'critical_issues': len([i for i in integrity_report['issues_found'] if i['severity'] == 'ERROR']),
            'warning_issues': len([i for i in integrity_report['issues_found'] if i['severity'] == 'WARNING'])
        }
        
        self.diagnostic_data['data_integrity'] = integrity_report
        
        logger.info(f"🔧 Data integrity verification completed")
        logger.info(f"📊 Found {len(integrity_report['issues_found'])} issues")
        if fix_issues:
            logger.info(f"🔨 Applied {len(integrity_report['fixes_applied'])} fixes")
        
        return integrity_report
    
    def export_diagnostics(self, output_file: str = None) -> str:
        """Export comprehensive diagnostic data."""
        if not output_file:
            output_file = f"points_system_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Add system information
        self.diagnostic_data['system_info'] = {
            'total_exams': Exam.objects.count(),
            'total_questions': Question.objects.count(),
            'total_sessions': StudentSession.objects.count(),
            'total_answers': StudentAnswer.objects.count(),
            'database_queries': len(connection.queries),
            'django_version': django.get_version()
        }
        
        # Add all collected issues
        self.diagnostic_data['issues_summary'] = {
            'total_issues': len(self.issues_found),
            'by_severity': dict(Counter(issue['severity'] for issue in self.issues_found)),
            'by_component': dict(Counter(issue['component'] for issue in self.issues_found)),
            'issues': self.issues_found
        }
        
        # Export to file
        with open(output_file, 'w') as f:
            json.dump(self.diagnostic_data, f, indent=2, default=str)
        
        logger.info(f"💾 Diagnostic data exported to: {output_file}")
        return output_file


def main():
    """Main CLI interface for the points system debugger."""
    parser = argparse.ArgumentParser(
        description="Points System Debug and Troubleshooting Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health check command
    health_parser = subparsers.add_parser('health-check', help='Comprehensive system health check')
    
    # Verify data command
    verify_parser = subparsers.add_parser('verify-data', help='Verify data integrity')
    verify_parser.add_argument('--fix-issues', action='store_true', 
                             help='Attempt to fix issues automatically')
    
    # Trace question command
    trace_parser = subparsers.add_parser('trace-question', help='Trace a specific question')
    trace_parser.add_argument('--question-id', type=int, required=True,
                            help='ID of the question to trace')
    
    # Export diagnostics command
    export_parser = subparsers.add_parser('export-diagnostics', help='Export diagnostic data')
    export_parser.add_argument('--output', type=str, help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    debugger = PointsSystemDebugger()
    
    try:
        if args.command == 'health-check':
            logger.info("🚀 Starting points system health check...")
            report = debugger.health_check()
            
            print("\n" + "="*80)
            print("POINTS SYSTEM HEALTH CHECK RESULTS")
            print("="*80)
            print(f"Overall Status: {report['overall_status']}")
            print(f"Timestamp: {report['timestamp']}")
            print("\nCheck Results:")
            
            for check_name, result in report['checks'].items():
                status_emoji = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️"}.get(result['status'], "❓")
                print(f"  {status_emoji} {check_name.replace('_', ' ').title()}: {result['status']}")
                
                if result.get('error'):
                    print(f"      Error: {result['error']}")
            
            print(f"\nSummary:")
            summary = report['summary']
            print(f"  Total Issues: {summary['total_issues']}")
            print(f"  Critical: {summary['critical_issues']}")
            print(f"  Errors: {summary['error_issues']}")
            print(f"  Warnings: {summary['warning_issues']}")
            
        elif args.command == 'verify-data':
            logger.info("🚀 Starting data integrity verification...")
            report = debugger.verify_data_integrity(fix_issues=args.fix_issues)
            
            print("\n" + "="*80)
            print("DATA INTEGRITY VERIFICATION RESULTS")
            print("="*80)
            print(f"Timestamp: {report['timestamp']}")
            print(f"Issues Found: {len(report['issues_found'])}")
            
            if args.fix_issues:
                print(f"Fixes Applied: {len(report['fixes_applied'])}")
            
            for issue in report['issues_found'][:10]:  # Show first 10 issues
                severity_emoji = {"ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}.get(issue['severity'], "❓")
                print(f"  {severity_emoji} {issue['type']}: {issue['description']}")
            
            if len(report['issues_found']) > 10:
                print(f"  ... and {len(report['issues_found']) - 10} more issues")
            
        elif args.command == 'trace-question':
            logger.info(f"🚀 Tracing question {args.question_id}...")
            report = debugger.trace_question(args.question_id)
            
            print("\n" + "="*80)
            print(f"QUESTION {args.question_id} TRACE RESULTS")
            print("="*80)
            
            if report.get('error'):
                print(f"❌ Error: {report['error']}")
            else:
                q_data = report['question_data']
                print(f"Question: {q_data['question_number']} ({q_data['question_type']})")
                print(f"Exam: {q_data['exam_name']}")
                print(f"Points: {q_data['points']}")
                print(f"Related Answers: {len(report['related_answers'])}")
                
                grading = report['grading_analysis']
                print(f"Grading Analysis:")
                print(f"  Total Answers: {grading['total_answers']}")
                print(f"  Correct: {grading['correct_answers']}")
                print(f"  Incorrect: {grading['incorrect_answers']}")
                print(f"  Accuracy: {grading['accuracy_rate']:.1f}%")
                
                if report['issues']:
                    print(f"Issues Found:")
                    for issue in report['issues']:
                        print(f"  ❌ {issue}")
            
        elif args.command == 'export-diagnostics':
            logger.info("🚀 Exporting diagnostic data...")
            # Run health check and data verification first
            debugger.health_check()
            debugger.verify_data_integrity()
            
            output_file = debugger.export_diagnostics(args.output)
            print(f"\n✅ Diagnostic data exported to: {output_file}")
        
        # Always export diagnostics at the end
        if args.command != 'export-diagnostics':
            output_file = debugger.export_diagnostics()
            print(f"\n💾 Full diagnostic data saved to: {output_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)