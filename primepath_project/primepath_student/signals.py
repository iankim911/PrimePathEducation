"""
Signal handlers for StudentProfile model.
Ensures synchronization between StudentProfile and legacy Student model.
"""

import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db import transaction
from primepath_student.models import StudentProfile
from core.models import Student

logger = logging.getLogger(__name__)


@receiver(post_save, sender=StudentProfile)
def sync_profile_to_legacy_student(sender, instance, created, **kwargs):
    """
    Automatically sync StudentProfile to legacy Student model when created or updated.
    This ensures students registered through the new system appear in class management.
    """
    try:
        with transaction.atomic():
            profile = instance
            
            # Log the sync operation
            logger.info(f"[SIGNAL_SYNC] Processing StudentProfile {profile.student_id}")
            print(f"[STUDENT_SYNC] Syncing profile {profile.student_id} to legacy Student model")
            
            # Check if legacy Student exists for this user
            legacy_student = None
            if profile.user:
                legacy_student = Student.objects.filter(user=profile.user).first()
            
            if not legacy_student and profile.get_full_name():
                # Try to find by name as fallback
                legacy_student = Student.objects.filter(name=profile.get_full_name()).first()
            
            if legacy_student:
                # Update existing Student
                logger.info(f"[SIGNAL_SYNC] Updating existing Student {legacy_student.id}")
                
                legacy_student.name = profile.get_full_name() or profile.student_id
                legacy_student.user = profile.user
                legacy_student.current_grade_level = profile.get_grade_display() if profile.grade else 'Unknown'
                legacy_student.parent_phone = profile.phone_number or ''
                legacy_student.parent_email = profile.user.email or ''
                legacy_student.date_of_birth = profile.date_of_birth
                legacy_student.is_active = True
                legacy_student.save()
                
                print(f"[STUDENT_SYNC] Updated legacy Student ID: {legacy_student.id}")
                
            else:
                # Create new Student
                logger.info(f"[SIGNAL_SYNC] Creating new Student for profile {profile.student_id}")
                
                legacy_student = Student.objects.create(
                    user=profile.user,
                    name=profile.get_full_name() or profile.student_id,
                    current_grade_level=profile.get_grade_display() if profile.grade else 'Unknown',
                    parent_phone=profile.phone_number or '',
                    parent_email=profile.user.email or '',
                    date_of_birth=profile.date_of_birth,
                    is_active=True
                )
                
                logger.info(f"[SIGNAL_SYNC] Created Student {legacy_student.id}")
                print(f"[STUDENT_SYNC] Created legacy Student ID: {legacy_student.id}")
            
            # Store the legacy student ID in the profile for reference (if we add this field later)
            # profile.legacy_student_id = str(legacy_student.id)
            # profile.save(update_fields=['legacy_student_id'])
            
    except Exception as e:
        logger.error(f"[SIGNAL_SYNC] Error syncing StudentProfile {instance.student_id}: {e}")
        print(f"[STUDENT_SYNC] ERROR: Failed to sync profile {instance.student_id}: {e}")
        # Don't raise the exception to avoid breaking the save operation


@receiver(pre_delete, sender=StudentProfile)
def deactivate_legacy_student(sender, instance, **kwargs):
    """
    When a StudentProfile is deleted, deactivate the corresponding legacy Student.
    We don't delete it to preserve historical data.
    """
    try:
        profile = instance
        
        # Find the legacy Student
        if profile.user:
            legacy_student = Student.objects.filter(user=profile.user).first()
            if legacy_student:
                logger.info(f"[SIGNAL_SYNC] Deactivating Student {legacy_student.id} for deleted profile {profile.student_id}")
                legacy_student.is_active = False
                legacy_student.save()
                print(f"[STUDENT_SYNC] Deactivated legacy Student ID: {legacy_student.id}")
                
    except Exception as e:
        logger.error(f"[SIGNAL_SYNC] Error deactivating Student for profile {instance.student_id}: {e}")
        print(f"[STUDENT_SYNC] ERROR: Failed to deactivate legacy student: {e}")