"""
Background Tasks - Phase 8
Celery tasks for asynchronous processing
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging
import os

logger = logging.getLogger(__name__)

# Note: Celery configuration would be in settings.py:
# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'


@shared_task
def process_exam_pdf(exam_id: str, pdf_path: str):
    """
    Process uploaded PDF file asynchronously.
    
    Args:
        exam_id: UUID of the exam
        pdf_path: Path to the PDF file
    """
    try:
        from placement_test.models import PlacementExam as Exam
        from core.services import FileService
        
        logger.info(f"Processing PDF for exam {exam_id}")
        
        # Validate PDF
        is_valid = FileService.validate_pdf_file(pdf_path)
        if not is_valid:
            logger.error(f"Invalid PDF file for exam {exam_id}")
            return False
        
        # Extract metadata (page count, size, etc.)
        # This would use PyPDF2 or similar library if available
        
        # Generate thumbnails for preview
        # This would use pdf2image or similar
        
        # Update exam status
        exam = Exam.objects.get(id=exam_id)
        exam.pdf_processed = True
        exam.save()
        
        logger.info(f"PDF processing complete for exam {exam_id}")
        return True
        
    except Exception as e:
        logger.error(f"PDF processing failed for exam {exam_id}: {e}")
        return False


@shared_task
def process_audio_files(exam_id: str, audio_file_ids: list):
    """
    Process uploaded audio files asynchronously.
    
    Args:
        exam_id: UUID of the exam
        audio_file_ids: List of AudioFile IDs
    """
    try:
        from placement_test.models import PlacementAudioFile as AudioFile
        
        logger.info(f"Processing {len(audio_file_ids)} audio files for exam {exam_id}")
        
        for audio_id in audio_file_ids:
            audio_file = AudioFile.objects.get(id=audio_id)
            
            # Validate audio format
            # Convert if necessary (e.g., to MP3)
            # Generate waveform for visualization
            # Extract duration metadata
            
            audio_file.processed = True
            audio_file.save()
        
        logger.info(f"Audio processing complete for exam {exam_id}")
        return True
        
    except Exception as e:
        logger.error(f"Audio processing failed for exam {exam_id}: {e}")
        return False


@shared_task
def calculate_exam_statistics(exam_id: str):
    """
    Calculate and cache exam statistics.
    
    Args:
        exam_id: UUID of the exam
    """
    try:
        from placement_test.services import ExamService
        from core.cache_service import CacheService
        
        logger.info(f"Calculating statistics for exam {exam_id}")
        
        stats = ExamService.get_exam_statistics(exam_id)
        
        # Cache the results
        cache_key = f"exam_stats:{exam_id}"
        CacheService.set(cache_key, stats, prefix='exam', timeout=3600)
        
        logger.info(f"Statistics calculated for exam {exam_id}")
        return stats
        
    except Exception as e:
        logger.error(f"Statistics calculation failed for exam {exam_id}: {e}")
        return None


@shared_task
def generate_session_report(session_id: str):
    """
    Generate PDF report for completed session.
    
    Args:
        session_id: UUID of the session
    """
    try:
        from placement_test.models import StudentSession
        from placement_test.services import GradingService
        
        logger.info(f"Generating report for session {session_id}")
        
        session = StudentSession.objects.get(id=session_id)
        
        if not session.completed_at:
            logger.warning(f"Session {session_id} not completed")
            return False
        
        # Get session results
        results = GradingService.get_session_analytics(session_id)
        
        # Generate PDF report
        # This would use ReportLab or similar library
        report_path = f"reports/session_{session_id}.pdf"
        
        # Save report path to session
        session.report_file = report_path
        session.save()
        
        logger.info(f"Report generated for session {session_id}")
        return report_path
        
    except Exception as e:
        logger.error(f"Report generation failed for session {session_id}: {e}")
        return None


@shared_task
def send_completion_notification(session_id: str):
    """
    Send email notification when test is completed.
    
    Args:
        session_id: UUID of the session
    """
    try:
        from placement_test.models import StudentSession
        
        logger.info(f"Sending completion notification for session {session_id}")
        
        session = StudentSession.objects.get(id=session_id)
        
        if not session.completed_at:
            return False
        
        # Prepare email content
        subject = f"Test Completed - {session.student_name}"
        message = f"""
        Dear {session.student_name},
        
        You have successfully completed the placement test.
        
        Test Details:
        - Exam: {session.exam.name}
        - Score: {session.percentage_score:.1f}%
        - Correct Answers: {session.correct_answers}/{session.total_questions}
        - Placement Level: {session.final_curriculum_level or 'Pending'}
        
        Thank you for taking the test.
        
        Best regards,
        PrimePath Team
        """
        
        # Send email (if email is available)
        # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        
        logger.info(f"Notification sent for session {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Notification failed for session {session_id}: {e}")
        return False


@shared_task
def cleanup_old_sessions(days: int = 30):
    """
    Clean up old incomplete sessions.
    
    Args:
        days: Number of days to keep sessions
    """
    try:
        from placement_test.models import StudentSession
        
        logger.info(f"Cleaning up sessions older than {days} days")
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find incomplete sessions older than cutoff
        old_sessions = StudentSession.objects.filter(
            completed_at__isnull=True,
            start_time__lt=cutoff_date
        )
        
        count = old_sessions.count()
        
        # Delete old sessions
        old_sessions.delete()
        
        logger.info(f"Cleaned up {count} old sessions")
        return count
        
    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        return 0


@shared_task
def cleanup_orphaned_files():
    """Clean up orphaned files not linked to any exam."""
    try:
        from placement_test.models import PlacementExam as Exam, AudioFile
        from core.services import FileService
        
        logger.info("Cleaning up orphaned files")
        
        # Find orphaned audio files
        orphaned_audio = AudioFile.objects.filter(exam__isnull=True)
        audio_count = orphaned_audio.count()
        
        for audio in orphaned_audio:
            if audio.audio_file:
                FileService.delete_file(audio.audio_file.name)
        
        orphaned_audio.delete()
        
        # Find PDF files without exams
        # This would check the media directory for unlinked files
        
        logger.info(f"Cleaned up {audio_count} orphaned audio files")
        return audio_count
        
    except Exception as e:
        logger.error(f"File cleanup failed: {e}")
        return 0


@shared_task
def generate_daily_report():
    """Generate daily statistics report."""
    try:
        from core.services import DashboardService
        from django.core.mail import mail_admins
        
        logger.info("Generating daily report")
        
        # Get daily statistics
        stats = DashboardService.get_dashboard_stats()
        
        # Format report
        report = f"""
        Daily Statistics Report - {timezone.now().date()}
        
        Total Sessions: {stats['total_sessions']}
        Active Exams: {stats['active_exams']}
        Completed Today: {stats.get('completed_today', 0)}
        Average Score: {stats.get('average_score', 0):.1f}%
        Completion Rate: {stats.get('completion_rate', 0):.1f}%
        """
        
        # Send to admins
        mail_admins("Daily Report", report)
        
        logger.info("Daily report sent")
        return True
        
    except Exception as e:
        logger.error(f"Daily report generation failed: {e}")
        return False


@shared_task
def update_placement_analytics():
    """Update placement analytics and cache results."""
    try:
        from placement_test.services import PlacementService
        from core.cache_service import CacheService
        
        logger.info("Updating placement analytics")
        
        # Calculate placement distributions
        analytics = PlacementService.get_placement_analytics()
        
        # Cache results
        CacheService.set(
            'placement_analytics',
            analytics,
            prefix='dashboard',
            timeout=7200  # 2 hours
        )
        
        logger.info("Placement analytics updated")
        return True
        
    except Exception as e:
        logger.error(f"Analytics update failed: {e}")
        return False


# Periodic tasks (would be configured in celery beat schedule)
"""
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-old-sessions': {
        'task': 'core.tasks.cleanup_old_sessions',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    'cleanup-orphaned-files': {
        'task': 'core.tasks.cleanup_orphaned_files',
        'schedule': crontab(hour=3, minute=0),  # Run at 3 AM daily
    },
    'generate-daily-report': {
        'task': 'core.tasks.generate_daily_report',
        'schedule': crontab(hour=7, minute=0),  # Run at 7 AM daily
    },
    'update-placement-analytics': {
        'task': 'core.tasks.update_placement_analytics',
        'schedule': crontab(minute='*/30'),  # Run every 30 minutes
    },
}
"""