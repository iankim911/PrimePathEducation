"""
Notification Service for Student Portal
Handles sending notifications via email, SMS, and in-app channels
"""
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.db import transaction
import logging
import requests
from datetime import timedelta
from typing import List, Dict, Optional

from primepath_student.models import StudentProfile, StudentExamSession
from primepath_student.models.notifications import (
    Notification, NotificationPreference, NotificationTemplate,
    NotificationQueue, NotificationLog
)
from primepath_routinetest.models import ExamLaunchSession, RoutineExam

logger = logging.getLogger(__name__)


class NotificationService:
    """Main notification service class"""
    
    @classmethod
    def notify_exam_launch(cls, launch_session: ExamLaunchSession, student_ids: List[str] = None):
        """
        Notify students when an exam is launched
        
        Args:
            launch_session: The ExamLaunchSession instance
            student_ids: Optional list of specific student IDs to notify
        """
        logger.info(f"[NOTIFICATION] Preparing exam launch notifications for {launch_session.exam.name}")
        
        # Get students to notify
        students = cls._get_students_for_class(launch_session.class_code, student_ids)
        
        # Get or create template
        template = cls._get_template('exam_launch')
        
        notifications_created = []
        
        for student in students:
            # Check preferences
            prefs = cls._get_or_create_preferences(student)
            if not prefs.exam_launch:
                continue
            
            # Prepare context for template
            context = {
                'student_name': student.user.first_name or student.student_id,
                'exam_name': launch_session.exam.name,
                'class_code': launch_session.class_code,
                'duration': launch_session.duration_minutes,
                'expires_at': launch_session.expires_at.strftime('%B %d, %Y at %I:%M %p'),
                'exam_url': f"{settings.SITE_URL}/student/exam/start/{launch_session.id}/"
            }
            
            # Create notifications for enabled channels
            for channel in ['email', 'sms', 'in_app']:
                if prefs.should_send_notification('exam_launch', channel):
                    notification = cls._create_notification(
                        student=student,
                        template=template,
                        context=context,
                        channel=channel,
                        notification_type='exam_launch',
                        related_exam_id=launch_session.exam.id,
                        related_class_code=launch_session.class_code
                    )
                    notifications_created.append(notification)
        
        # Queue notifications for sending
        cls._queue_notifications(notifications_created)
        
        logger.info(f"[NOTIFICATION] Created {len(notifications_created)} notifications for exam launch")
        return notifications_created
    
    @classmethod
    def schedule_exam_reminders(cls, launch_session: ExamLaunchSession):
        """
        Schedule reminder notifications for an exam
        
        Args:
            launch_session: The ExamLaunchSession to create reminders for
        """
        students = cls._get_students_for_class(launch_session.class_code)
        
        for student in students:
            prefs = cls._get_or_create_preferences(student)
            if not prefs.exam_reminder:
                continue
            
            # Schedule reminder based on preference
            reminder_time = launch_session.expires_at - timedelta(hours=prefs.reminder_hours_before)
            
            if reminder_time > timezone.now():
                context = {
                    'student_name': student.user.first_name or student.student_id,
                    'exam_name': launch_session.exam.name,
                    'time_remaining': prefs.reminder_hours_before,
                    'exam_url': f"{settings.SITE_URL}/student/exam/start/{launch_session.id}/"
                }
                
                template = cls._get_template('exam_reminder_2h')
                
                for channel in ['email', 'sms', 'in_app']:
                    if prefs.should_send_notification('exam_reminder', channel):
                        notification = cls._create_notification(
                            student=student,
                            template=template,
                            context=context,
                            channel=channel,
                            notification_type='exam_reminder',
                            related_exam_id=launch_session.exam.id,
                            scheduled_for=reminder_time
                        )
                        cls._queue_notifications([notification], scheduled_time=reminder_time)
    
    @classmethod
    def notify_exam_results(cls, exam_session: StudentExamSession):
        """
        Notify student when exam results are available
        
        Args:
            exam_session: The completed StudentExamSession
        """
        student = exam_session.student
        prefs = cls._get_or_create_preferences(student)
        
        if not prefs.exam_results:
            return
        
        template = cls._get_template('exam_results')
        context = {
            'student_name': student.user.first_name or student.student_id,
            'exam_name': exam_session.exam.name,
            'score': exam_session.score,
            'correct_answers': exam_session.correct_answers,
            'total_questions': exam_session.total_questions,
            'results_url': f"{settings.SITE_URL}/student/exam/{exam_session.id}/result/"
        }
        
        notifications = []
        for channel in ['email', 'in_app']:  # Skip SMS for results
            if prefs.should_send_notification('exam_results', channel):
                notification = cls._create_notification(
                    student=student,
                    template=template,
                    context=context,
                    channel=channel,
                    notification_type='exam_results',
                    related_exam_id=exam_session.exam.id
                )
                notifications.append(notification)
        
        cls._queue_notifications(notifications)
        return notifications
    
    @classmethod
    def send_notification(cls, notification: Notification):
        """
        Send a single notification
        
        Args:
            notification: The Notification to send
        """
        try:
            if notification.channel == 'email':
                success = cls._send_email(notification)
            elif notification.channel == 'sms':
                success = cls._send_sms(notification)
            elif notification.channel == 'in_app':
                success = cls._send_in_app(notification)
            else:
                raise ValueError(f"Unknown channel: {notification.channel}")
            
            if success:
                notification.mark_as_sent()
                cls._log_notification(notification, 'sent', success=True)
            else:
                notification.mark_as_failed()
                cls._log_notification(notification, 'failed', success=False)
            
            return success
            
        except Exception as e:
            logger.error(f"[NOTIFICATION] Error sending notification {notification.id}: {e}")
            notification.mark_as_failed(error=str(e))
            cls._log_notification(notification, 'error', success=False, error=str(e))
            return False
    
    @classmethod
    def process_queue(cls, batch_size: int = 50):
        """
        Process pending notifications in the queue
        
        Args:
            batch_size: Number of notifications to process in one batch
        """
        pending_notifications = NotificationQueue.objects.filter(
            is_processed=False,
            scheduled_time__lte=timezone.now()
        ).select_related('notification').order_by('priority', 'scheduled_time')[:batch_size]
        
        processed = 0
        failed = 0
        
        for queue_entry in pending_notifications:
            notification = queue_entry.notification
            
            # Mark as processing
            queue_entry.processing_started_at = timezone.now()
            queue_entry.save()
            
            # Send notification
            success = cls.send_notification(notification)
            
            if success:
                queue_entry.is_processed = True
                queue_entry.processed_at = timezone.now()
                queue_entry.save()
                processed += 1
            else:
                if queue_entry.can_retry():
                    queue_entry.increment_retry()
                else:
                    queue_entry.is_processed = True
                    queue_entry.processed_at = timezone.now()
                    queue_entry.save()
                failed += 1
        
        logger.info(f"[NOTIFICATION] Processed {processed} notifications, {failed} failed")
        return processed, failed
    
    # Private helper methods
    
    @classmethod
    def _get_students_for_class(cls, class_code: str, student_ids: List[str] = None):
        """Get students for a specific class"""
        from primepath_student.models import StudentClassAssignment
        
        query = StudentClassAssignment.objects.filter(
            class_code=class_code,
            is_active=True
        ).select_related('student', 'student__user')
        
        if student_ids:
            query = query.filter(student__student_id__in=student_ids)
        
        return [assignment.student for assignment in query]
    
    @classmethod
    def _get_or_create_preferences(cls, student: StudentProfile):
        """Get or create notification preferences for a student"""
        prefs, created = NotificationPreference.objects.get_or_create(
            student=student,
            defaults={
                'preferred_email': student.user.email,
                'preferred_phone': student.phone_number
            }
        )
        return prefs
    
    @classmethod
    def _get_template(cls, template_type: str):
        """Get notification template by type"""
        try:
            return NotificationTemplate.objects.get(
                template_type=template_type,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            # Create default template if not exists
            return cls._create_default_template(template_type)
    
    @classmethod
    def _create_default_template(cls, template_type: str):
        """Create default notification template"""
        templates = {
            'exam_launch': {
                'name': 'Exam Launch Notification',
                'email_subject': 'New Exam Available: {exam_name}',
                'email_body': 'Hi {student_name},\n\nA new exam "{exam_name}" is now available for your class {class_code}.\n\nDuration: {duration} minutes\nExpires: {expires_at}\n\nStart exam: {exam_url}\n\nBest regards,\nPrimePath Team',
                'sms_message': 'New exam "{exam_name}" available for {class_code}. Expires {expires_at}. Start: {exam_url}',
                'in_app_title': 'New Exam Available',
                'in_app_message': '"{exam_name}" is now available for {class_code}. Duration: {duration} minutes.'
            },
            'exam_reminder_2h': {
                'name': '2 Hour Exam Reminder',
                'email_subject': 'Reminder: {exam_name} expires in {time_remaining} hours',
                'email_body': 'Hi {student_name},\n\nThis is a reminder that the exam "{exam_name}" will expire in {time_remaining} hours.\n\nDon\'t forget to complete it before the deadline!\n\nStart exam: {exam_url}\n\nBest regards,\nPrimePath Team',
                'sms_message': 'Reminder: "{exam_name}" expires in {time_remaining} hours. Start: {exam_url}',
                'in_app_title': 'Exam Expiring Soon',
                'in_app_message': '"{exam_name}" expires in {time_remaining} hours. Complete it now!'
            },
            'exam_results': {
                'name': 'Exam Results Available',
                'email_subject': 'Your results for {exam_name} are ready',
                'email_body': 'Hi {student_name},\n\nYour results for "{exam_name}" are now available.\n\nScore: {score}%\nCorrect Answers: {correct_answers}/{total_questions}\n\nView detailed results: {results_url}\n\nBest regards,\nPrimePath Team',
                'sms_message': 'Results ready for "{exam_name}". Score: {score}%. View: {results_url}',
                'in_app_title': 'Results Available',
                'in_app_message': 'Your score for "{exam_name}": {score}% ({correct_answers}/{total_questions} correct)'
            }
        }
        
        if template_type in templates:
            template_data = templates[template_type]
            return NotificationTemplate.objects.create(
                template_type=template_type,
                **template_data
            )
        
        raise ValueError(f"Unknown template type: {template_type}")
    
    @classmethod
    def _create_notification(cls, student, template, context, channel, 
                           notification_type, related_exam_id=None, 
                           related_class_code=None, scheduled_for=None):
        """Create a notification instance"""
        if channel == 'email':
            subject, body, html_body = template.render_email(context)
            message = body
        elif channel == 'sms':
            subject = template.in_app_title.format(**context)
            message = template.render_sms(context)
            html_body = None
        else:  # in_app
            subject, message = template.render_in_app(context)
            html_body = None
        
        notification = Notification.objects.create(
            student=student,
            notification_type=notification_type,
            channel=channel,
            subject=subject,
            message=message,
            html_message=html_body,
            metadata=context,
            related_exam_id=related_exam_id,
            related_class_code=related_class_code,
            scheduled_for=scheduled_for
        )
        
        return notification
    
    @classmethod
    def _queue_notifications(cls, notifications: List[Notification], 
                           scheduled_time=None, priority='normal'):
        """Add notifications to the queue"""
        queue_entries = []
        for notification in notifications:
            queue_entry = NotificationQueue(
                notification=notification,
                priority=priority,
                scheduled_time=scheduled_time or timezone.now()
            )
            queue_entries.append(queue_entry)
        
        NotificationQueue.objects.bulk_create(queue_entries)
    
    @classmethod
    def _send_email(cls, notification: Notification):
        """Send email notification"""
        try:
            student = notification.student
            prefs = cls._get_or_create_preferences(student)
            
            to_email = prefs.preferred_email or student.user.email
            
            if not to_email:
                logger.warning(f"[EMAIL] No email address for student {student.student_id}")
                return False
            
            send_mail(
                subject=notification.subject,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=notification.html_message,
                fail_silently=False
            )
            
            logger.info(f"[EMAIL] Sent to {to_email}: {notification.subject}")
            return True
            
        except Exception as e:
            logger.error(f"[EMAIL] Failed to send to {to_email}: {e}")
            return False
    
    @classmethod
    def _send_sms(cls, notification: Notification):
        """Send SMS notification"""
        # This is a placeholder - integrate with actual SMS service
        # Examples: Twilio, AWS SNS, MessageBird, etc.
        try:
            student = notification.student
            prefs = cls._get_or_create_preferences(student)
            
            phone = prefs.preferred_phone or student.phone_number
            
            if not phone:
                logger.warning(f"[SMS] No phone number for student {student.student_id}")
                return False
            
            # Placeholder for SMS service integration
            # Example with Twilio:
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=notification.message,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=phone
            # )
            
            logger.info(f"[SMS] Would send to {phone}: {notification.message[:50]}...")
            return True  # Return True for testing
            
        except Exception as e:
            logger.error(f"[SMS] Failed to send: {e}")
            return False
    
    @classmethod
    def _send_in_app(cls, notification: Notification):
        """Mark in-app notification as ready to display"""
        # In-app notifications are simply marked as sent
        # The frontend will fetch and display them
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.save()
        
        logger.info(f"[IN_APP] Created for {notification.student.student_id}: {notification.subject}")
        return True
    
    @classmethod
    def _log_notification(cls, notification, action, success=True, error=None):
        """Log notification activity"""
        NotificationLog.objects.create(
            notification=notification,
            action=action,
            success=success,
            error_message=error,
            details={
                'channel': notification.channel,
                'type': notification.notification_type,
                'student': notification.student.student_id
            }
        )