"""
User-related models: Teacher, School
Part of Phase 9: Model Modularization
"""
from django.db import models


class School(models.Model):
    """School information for student registration"""
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    """Teacher/Staff user model"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_head_teacher = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({'Head' if self.is_head_teacher else 'Teacher'})"