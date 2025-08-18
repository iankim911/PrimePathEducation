"""
Management command to clean up expired sessions
Fixes issue: Too many sessions accumulating (258+)
"""
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Clean up expired sessions and optionally old sessions'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Delete sessions older than N days (default: 7)'
        )
        parser.add_argument(
            '--keep-active',
            action='store_true',
            help='Keep sessions that were active in the last 24 hours'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        keep_active = options['keep_active']
        
        # Delete expired sessions
        expired_count = Session.objects.filter(
            expire_date__lt=timezone.now()
        ).delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {expired_count} expired sessions')
        )
        
        # Optionally delete old sessions
        if not keep_active:
            cutoff_date = timezone.now() - timedelta(days=days)
            old_count = Session.objects.filter(
                expire_date__lt=cutoff_date
            ).delete()[0]
            
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {old_count} sessions older than {days} days')
            )
        
        # Report remaining sessions
        remaining = Session.objects.count()
        self.stdout.write(
            self.style.WARNING(f'Remaining sessions: {remaining}')
        )
        
        # Recommend if still too many
        if remaining > 100:
            self.stdout.write(
                self.style.WARNING(
                    'Still many sessions remaining. Consider running with --days=1 to be more aggressive'
                )
            )