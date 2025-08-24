"""
Management command to process notification queue
Run this periodically (e.g., via cron) to send pending notifications
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from primepath_student.services import NotificationService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process pending notifications in the queue'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of notifications to process in one batch'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without actually sending'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS(f"{'[DRY RUN] ' if dry_run else ''}Processing notification queue..."))
        
        if dry_run:
            from primepath_student.models.notifications import NotificationQueue
            
            pending = NotificationQueue.objects.filter(
                is_processed=False,
                scheduled_time__lte=timezone.now()
            ).count()
            
            self.stdout.write(f"Would process {min(pending, batch_size)} notifications")
            self.stdout.write(f"Total pending: {pending}")
            
            # Show sample of what would be sent
            samples = NotificationQueue.objects.filter(
                is_processed=False,
                scheduled_time__lte=timezone.now()
            ).select_related('notification', 'notification__student')[:5]
            
            for queue_entry in samples:
                notification = queue_entry.notification
                self.stdout.write(
                    f"  - {notification.notification_type} via {notification.channel} "
                    f"to {notification.student.student_id}"
                )
        else:
            # Actually process the queue
            processed, failed = NotificationService.process_queue(batch_size)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Processed {processed} notifications successfully"
                )
            )
            
            if failed > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"{failed} notifications failed"
                    )
                )
            
            # Clean up old processed entries (older than 7 days)
            from primepath_student.models.notifications import NotificationQueue
            from datetime import timedelta
            
            cutoff_date = timezone.now() - timedelta(days=7)
            deleted_count = NotificationQueue.objects.filter(
                is_processed=True,
                processed_at__lt=cutoff_date
            ).delete()[0]
            
            if deleted_count > 0:
                self.stdout.write(
                    f"Cleaned up {deleted_count} old queue entries"
                )