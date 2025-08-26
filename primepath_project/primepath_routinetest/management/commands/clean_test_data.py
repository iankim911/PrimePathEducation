"""
Management command to clean up test and QA data
Handles test users, students, subprograms, exams, and sessions
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from core.models import Student, SubProgram
from core.curriculum_constants import is_test_subprogram
from primepath_routinetest.models import RoutineExam as Exam, StudentSession
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up test and QA data from the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without making changes'
        )
        parser.add_argument(
            '--category',
            choices=['users', 'students', 'subprograms', 'exams', 'sessions', 'all'],
            default='all',
            help='Which category of test data to clean'
        )
        parser.add_argument(
            '--days-old',
            type=int,
            default=7,
            help='Only delete test data older than this many days (default: 7)'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        category = options['category']
        days_old = options['days_old']
        cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
        
        self.stdout.write(
            self.style.WARNING(f'Cleaning test data from category: {category}')
        )
        self.stdout.write(f'Only cleaning data older than {days_old} days (before {cutoff_date.date()})')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No actual deletions will be made'))
        
        total_deleted = 0
        
        if category in ['users', 'all']:
            total_deleted += self.clean_test_users(dry_run, cutoff_date)
        
        if category in ['students', 'all']:
            total_deleted += self.clean_test_students(dry_run, cutoff_date)
        
        if category in ['subprograms', 'all']:
            total_deleted += self.clean_test_subprograms(dry_run)
        
        if category in ['exams', 'all']:
            total_deleted += self.clean_test_exams(dry_run, cutoff_date)
        
        if category in ['sessions', 'all']:
            total_deleted += self.clean_old_sessions(dry_run, cutoff_date)
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY RUN COMPLETE: Would delete {total_deleted} items total')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'CLEANUP COMPLETE: Deleted {total_deleted} items total')
            )
    
    def clean_test_users(self, dry_run, cutoff_date):
        """Clean up test users"""
        self.stdout.write('\n--- Cleaning Test Users ---')
        
        test_indicators = [
            'test', 'demo', 'sample', 'temp', 'phase', 'nav_test',
            'points_test', 'unified_test', 'tmp_', 'debug_'
        ]
        
        test_users = User.objects.none()
        for indicator in test_indicators:
            test_users = test_users | User.objects.filter(
                username__icontains=indicator,
                date_joined__lt=cutoff_date
            )
        
        # Remove duplicates
        test_users = test_users.distinct()
        
        count = test_users.count()
        self.stdout.write(f'Found {count} test users older than {cutoff_date.date()}')
        
        if count > 0:
            for user in test_users[:10]:  # Show first 10
                self.stdout.write(f'  - {user.username} (created: {user.date_joined.date()})')
            
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
        
        if not dry_run and count > 0:
            with transaction.atomic():
                deleted = test_users.delete()
                logger.info(f'Deleted {count} test users')
        
        return count
    
    def clean_test_students(self, dry_run, cutoff_date):
        """Clean up test students"""
        self.stdout.write('\n--- Cleaning Test Students ---')
        
        # Students linked to test users or with test patterns in name
        # Note: Student model might not have created_at field
        try:
            test_students = Student.objects.filter(
                user__username__icontains='test'
            )
            if hasattr(Student, 'created_at'):
                test_students = test_students.filter(created_at__lt=cutoff_date)
        except Exception:
            test_students = Student.objects.filter(
                name__icontains='test'
            )
        
        count = test_students.count()
        self.stdout.write(f'Found {count} test students older than {cutoff_date.date()}')
        
        if count > 0:
            for student in test_students[:5]:
                username = student.user.username if student.user else "None"
                self.stdout.write(f'  - {student.name} (user: {username})')
        
        if not dry_run and count > 0:
            with transaction.atomic():
                deleted = test_students.delete()
                logger.info(f'Deleted {count} test students')
        
        return count
    
    def clean_test_subprograms(self, dry_run):
        """Clean up test subprograms"""
        self.stdout.write('\n--- Cleaning Test SubPrograms ---')
        
        test_subprograms = []
        all_subprograms = SubProgram.objects.all()
        
        for subprogram in all_subprograms:
            if is_test_subprogram(subprogram.name):
                test_subprograms.append(subprogram)
        
        count = len(test_subprograms)
        self.stdout.write(f'Found {count} test subprograms')
        
        if count > 0:
            for subprogram in test_subprograms:
                self.stdout.write(f'  - ID {subprogram.id}: \"{subprogram.name}\"')
        
        if not dry_run and count > 0:
            with transaction.atomic():
                for subprogram in test_subprograms:
                    subprogram.delete()
                logger.info(f'Deleted {count} test subprograms')
        
        return count
    
    def clean_test_exams(self, dry_run, cutoff_date):
        """Clean up test exams"""
        self.stdout.write('\n--- Cleaning Test Exams ---')
        
        test_exams = Exam.objects.filter(
            name__icontains='test'
        )
        
        # Only clean old test exams if they have a created_at field
        if hasattr(Exam, 'created_at'):
            test_exams = test_exams.filter(created_at__lt=cutoff_date)
        
        count = test_exams.count()
        self.stdout.write(f'Found {count} test exams')
        
        if count > 0:
            for exam in test_exams[:5]:
                created_date = exam.created_at.date() if hasattr(exam, 'created_at') else 'Unknown'
                self.stdout.write(f'  - {exam.name} (created: {created_date})')
        
        if not dry_run and count > 0:
            with transaction.atomic():
                deleted = test_exams.delete()
                logger.info(f'Deleted {count} test exams')
        
        return count
    
    def clean_old_sessions(self, dry_run, cutoff_date):
        """Clean up old test sessions"""
        self.stdout.write('\n--- Cleaning Old Sessions ---')
        
        # Find very old sessions or sessions from test users
        old_sessions = StudentSession.objects.filter(
            started_at__lt=cutoff_date - timezone.timedelta(days=30)  # Extra old
        ) | StudentSession.objects.filter(
            student__user__username__icontains='test'
        )
        
        count = old_sessions.count()
        self.stdout.write(f'Found {count} old/test sessions')
        
        if count > 0:
            # Show some examples
            for session in old_sessions[:3]:
                username = session.student.user.username if session.student and session.student.user else 'No user'
                self.stdout.write(f'  - Session {session.id}: {username} (started: {session.started_at.date()})')
        
        if not dry_run and count > 0:
            with transaction.atomic():
                deleted = old_sessions.delete()
                logger.info(f'Deleted {count} old/test sessions')
        
        return count