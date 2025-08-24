"""
Management command to generate and send analytics reports
Can be scheduled via cron to run daily, weekly, or monthly
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
import logging

from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment
from primepath_routinetest.views.analytics import (
    get_overview_stats,
    get_performance_trends,
    get_exam_analytics,
    get_student_analytics,
    get_class_comparison
)
from primepath_routinetest.models.class_constants import CLASS_CODE_CHOICES

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate and send analytics reports to teachers'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            default='weekly',
            choices=['daily', 'weekly', 'monthly'],
            help='Report period'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Send report to specific email (for testing)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Generate reports without sending emails'
        )
        parser.add_argument(
            '--save-to-file',
            type=str,
            help='Save report to specified file path'
        )
    
    def handle(self, *args, **options):
        period = options['period']
        dry_run = options['dry_run']
        test_email = options.get('email')
        save_path = options.get('save_to_file')
        
        # Calculate date range based on period
        end_date = timezone.now().date()
        if period == 'daily':
            start_date = end_date - timedelta(days=1)
            period_label = 'Daily'
        elif period == 'weekly':
            start_date = end_date - timedelta(days=7)
            period_label = 'Weekly'
        else:  # monthly
            start_date = end_date - timedelta(days=30)
            period_label = 'Monthly'
        
        self.stdout.write(
            self.style.SUCCESS(
                f"{'[DRY RUN] ' if dry_run else ''}Generating {period_label} Analytics Reports"
            )
        )
        self.stdout.write(f"Date Range: {start_date} to {end_date}")
        
        # Get teachers to send reports to
        if test_email:
            # Test mode - generate for all classes but send to test email
            teachers = [{
                'email': test_email,
                'name': 'Test User',
                'classes': [code for code, _ in CLASS_CODE_CHOICES],
                'is_admin': True
            }]
        else:
            # Production mode - get all active teachers with email addresses
            teachers = self._get_teachers_for_reports()
        
        total_reports = 0
        successful = 0
        failed = 0
        
        for teacher_info in teachers:
            try:
                # Generate report for this teacher
                report_file = self._generate_report(
                    teacher_info,
                    start_date,
                    end_date,
                    period_label
                )
                
                if save_path:
                    # Save to file for testing
                    filename = f"{save_path}_{teacher_info['name'].replace(' ', '_')}.xlsx"
                    with open(filename, 'wb') as f:
                        f.write(report_file.getvalue())
                    self.stdout.write(f"Report saved to {filename}")
                
                if not dry_run:
                    # Send email
                    self._send_report_email(
                        teacher_info,
                        report_file,
                        start_date,
                        end_date,
                        period_label
                    )
                    successful += 1
                else:
                    self.stdout.write(
                        f"Would send report to {teacher_info['name']} ({teacher_info['email']})"
                    )
                    successful += 1
                
                total_reports += 1
                
            except Exception as e:
                failed += 1
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to generate report for {teacher_info['name']}: {str(e)}"
                    )
                )
                logger.error(f"Report generation failed: {str(e)}", exc_info=True)
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{period_label} Report Generation Complete:\n"
                f"  Total: {total_reports}\n"
                f"  Successful: {successful}\n"
                f"  Failed: {failed}"
            )
        )
    
    def _get_teachers_for_reports(self):
        """Get list of teachers with their assigned classes"""
        teachers = []
        
        # Get all active teachers with email addresses
        for teacher in Teacher.objects.filter(
            user__is_active=True,
            user__email__isnull=False
        ).exclude(user__email=''):
            
            # Get their assigned classes
            if teacher.is_head_teacher or teacher.user.is_superuser:
                # Head teachers see all classes
                classes = [code for code, _ in CLASS_CODE_CHOICES]
                is_admin = True
            else:
                # Regular teachers see only assigned classes
                classes = list(
                    TeacherClassAssignment.objects.filter(
                        teacher=teacher,
                        is_active=True
                    ).values_list('class_code', flat=True)
                )
                is_admin = False
            
            if classes:  # Only include teachers with assigned classes
                teachers.append({
                    'email': teacher.user.email,
                    'name': teacher.name or teacher.user.get_full_name() or teacher.user.username,
                    'classes': classes,
                    'is_admin': is_admin,
                    'teacher_obj': teacher
                })
        
        return teachers
    
    def _generate_report(self, teacher_info, start_date, end_date, period_label):
        """Generate Excel report for a teacher"""
        classes = teacher_info['classes']
        
        # Get analytics data
        overview = get_overview_stats(classes, start_date, end_date)
        trends = get_performance_trends(classes, start_date, end_date)
        exams = get_exam_analytics(classes, start_date, end_date)
        students = get_student_analytics(classes, start_date, end_date)
        class_comparison = get_class_comparison(classes, start_date, end_date)
        
        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # Report Info Sheet
            info_data = {
                'Report Type': [f'{period_label} Analytics Report'],
                'Generated For': [teacher_info['name']],
                'Date Range': [f'{start_date} to {end_date}'],
                'Generated On': [timezone.now().strftime('%Y-%m-%d %H:%M')],
                'Total Classes': [len(classes)]
            }
            df_info = pd.DataFrame(info_data)
            df_info.to_excel(writer, sheet_name='Report Info', index=False)
            
            # Overview Statistics
            df_overview = pd.DataFrame([overview])
            df_overview.to_excel(writer, sheet_name='Overview', index=False)
            
            # Performance Trends
            if trends.get('dates'):
                df_trends = pd.DataFrame({
                    'Date': trends['dates'],
                    'Exams Completed': trends['exam_counts'],
                    'Average Score': trends['average_scores']
                })
                df_trends.to_excel(writer, sheet_name='Performance Trends', index=False)
            
            # Class Comparison
            if class_comparison:
                df_classes = pd.DataFrame(class_comparison)
                df_classes.to_excel(writer, sheet_name='Class Comparison', index=False)
            
            # Top Students
            if students['top_performers']:
                df_top = pd.DataFrame(students['top_performers'])
                df_top.to_excel(writer, sheet_name='Top Students', index=False)
            
            # Students Needing Support
            if students['struggling_students']:
                df_struggling = pd.DataFrame(students['struggling_students'])
                df_struggling.to_excel(writer, sheet_name='Students Needing Support', index=False)
            
            # Exam Analysis
            if exams:
                exam_data = []
                for exam_stat in exams:
                    exam_data.append({
                        'Exam Name': exam_stat['exam'].name,
                        'Attempts': exam_stat['attempts'],
                        'Average Score': exam_stat['average_score'],
                        'Min Score': exam_stat['min_score'],
                        'Max Score': exam_stat['max_score'],
                        'Pass Rate': round(exam_stat['pass_rate'], 1),
                        'Difficulty': exam_stat['difficulty_level']
                    })
                df_exams = pd.DataFrame(exam_data)
                df_exams.to_excel(writer, sheet_name='Exam Analysis', index=False)
        
        output.seek(0)
        return output
    
    def _send_report_email(self, teacher_info, report_file, start_date, end_date, period_label):
        """Send report via email"""
        subject = f'PrimePath {period_label} Analytics Report - {start_date} to {end_date}'
        
        # Render email body
        html_content = render_to_string('emails/analytics_report.html', {
            'teacher_name': teacher_info['name'],
            'period_label': period_label,
            'start_date': start_date,
            'end_date': end_date,
            'class_count': len(teacher_info['classes']),
            'is_admin': teacher_info['is_admin']
        })
        
        # Create email
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[teacher_info['email']],
        )
        email.content_subtype = 'html'
        
        # Attach Excel report
        filename = f'analytics_report_{period_label.lower()}_{end_date}.xlsx'
        email.attach(filename, report_file.getvalue(), 
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        # Send
        email.send()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Report sent to {teacher_info['name']} ({teacher_info['email']})"
            )
        )