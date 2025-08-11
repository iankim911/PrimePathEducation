"""
User-related models: Teacher, School
Part of Phase 9: Model Modularization
Enhanced with Django User integration for authentication
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
import json

logger = logging.getLogger(__name__)


class School(models.Model):
    """School information for student registration"""
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    """Teacher/Staff user model with Django authentication integration"""
    # Link to Django User for authentication
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='teacher_profile',
        null=True,  # Allow null for existing teachers without users
        blank=True,
        help_text="Django user account for authentication"
    )
    
    # Original Teacher fields
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_head_teacher = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, help_text="Can login and access system")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({'Head' if self.is_head_teacher else 'Teacher'})"
    
    def get_display_name(self):
        """Get display name from User if linked, otherwise use Teacher name"""
        if self.user:
            full_name = f"{self.user.first_name} {self.user.last_name}".strip()
            return full_name if full_name else self.user.username
        return self.name
    
    def sync_with_user(self):
        """Sync Teacher data with linked User"""
        if self.user:
            # Update User fields from Teacher
            if not self.user.email and self.email:
                self.user.email = self.email
            
            # Update name if not set
            if self.name and not (self.user.first_name or self.user.last_name):
                name_parts = self.name.split(' ', 1)
                self.user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    self.user.last_name = name_parts[1]
                self.user.save()
            
            # Log sync
            console_log = {
                "model": "Teacher",
                "action": "sync_with_user",
                "teacher_id": self.id,
                "user_id": self.user.id,
                "teacher_name": self.name,
                "user_username": self.user.username
            }
            logger.info(f"[TEACHER_USER_SYNC] {json.dumps(console_log)}")
            print(f"[TEACHER_USER_SYNC] {json.dumps(console_log)}")


# Signal handlers for User-Teacher synchronization
@receiver(post_save, sender=User)
def create_or_update_teacher_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update Teacher profile when User is saved.
    This ensures every User who should be a teacher has a Teacher profile.
    """
    # Only create Teacher profile for staff users
    if instance.is_staff or instance.is_superuser:
        if created:
            # Check if Teacher with same email exists
            teacher = None
            if instance.email:
                try:
                    teacher = Teacher.objects.get(email=instance.email)
                    teacher.user = instance
                    teacher.save()
                    
                    console_log = {
                        "signal": "create_or_update_teacher_profile",
                        "action": "linked_existing_teacher",
                        "user_id": instance.id,
                        "teacher_id": teacher.id,
                        "email": instance.email
                    }
                    logger.info(f"[USER_TEACHER_SIGNAL] {json.dumps(console_log)}")
                    print(f"[USER_TEACHER_SIGNAL] {json.dumps(console_log)}")
                except Teacher.DoesNotExist:
                    pass
            
            # Create new Teacher if not found
            if not teacher:
                teacher = Teacher.objects.create(
                    user=instance,
                    name=f"{instance.first_name} {instance.last_name}".strip() or instance.username,
                    email=instance.email or f"{instance.username}@example.com",
                    is_head_teacher=instance.is_superuser
                )
                
                console_log = {
                    "signal": "create_or_update_teacher_profile",
                    "action": "created_new_teacher",
                    "user_id": instance.id,
                    "teacher_id": teacher.id,
                    "username": instance.username
                }
                logger.info(f"[USER_TEACHER_SIGNAL] {json.dumps(console_log)}")
                print(f"[USER_TEACHER_SIGNAL] {json.dumps(console_log)}")
        else:
            # Update existing Teacher profile if it exists
            try:
                teacher = instance.teacher_profile
                teacher.sync_with_user()
            except Teacher.DoesNotExist:
                # No teacher profile exists, which is fine for non-staff users
                pass