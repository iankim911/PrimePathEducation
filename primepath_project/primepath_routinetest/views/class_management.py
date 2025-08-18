"""
BUILDER: Day 2 - Class Management Views
Admin functions for creating classes and assigning teachers
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from core.models import Teacher
from ..models import Class
import json

def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def manage_classes(request):
    """Admin view for managing classes"""
    classes = Class.objects.filter(is_active=True).prefetch_related('assigned_teachers')
    teachers = Teacher.objects.all().order_by('name')
    
    context = {
        'classes': classes,
        'teachers': teachers,
        'page_title': 'Manage Classes - Admin'
    }
    return render(request, 'primepath_routinetest/admin/manage_classes.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(['POST'])
def create_class(request):
    """Create a new class"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        if not data.get('name') or not data.get('grade_level'):
            return JsonResponse({
                'status': 'error',
                'message': 'Class name and grade level are required'
            }, status=400)
        
        # Check for duplicates
        existing = Class.objects.filter(
            name=data['name'],
            grade_level=data['grade_level'],
            section=data.get('section', ''),
            academic_year=data.get('academic_year', '2024-2025')
        ).first()
        
        if existing:
            return JsonResponse({
                'status': 'error',
                'message': f'A class with this name, grade level, and section already exists for {data.get("academic_year", "2024-2025")}'
            }, status=400)
        
        # Create the class
        new_class = Class.objects.create(
            name=data['name'],
            grade_level=data['grade_level'],
            section=data.get('section', ''),
            academic_year=data.get('academic_year', '2024-2025'),
            created_by=request.user
        )
        
        # Assign teachers if provided
        teacher_ids = data.get('teacher_ids', [])
        if teacher_ids:
            teachers = Teacher.objects.filter(id__in=teacher_ids)
            new_class.assigned_teachers.set(teachers)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Class "{new_class.name}" created successfully!',
            'class_id': str(new_class.id),
            'class_name': str(new_class)
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error creating class: {str(e)}'
        }, status=400)

@login_required
@user_passes_test(is_admin)
@require_http_methods(['POST'])
def assign_teacher(request, class_id):
    """Assign a teacher to a class"""
    try:
        data = json.loads(request.body)
        class_obj = get_object_or_404(Class, id=class_id)
        teacher = get_object_or_404(Teacher, id=data['teacher_id'])
        
        class_obj.assigned_teachers.add(teacher)
        
        return JsonResponse({
            'status': 'success',
            'message': f'{teacher.name} assigned to {class_obj.name}'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error assigning teacher: {str(e)}'
        }, status=400)

@login_required
@user_passes_test(is_admin)
@require_http_methods(['POST'])
def remove_teacher(request, class_id):
    """Remove a teacher from a class"""
    try:
        data = json.loads(request.body)
        class_obj = get_object_or_404(Class, id=class_id)
        teacher = get_object_or_404(Teacher, id=data['teacher_id'])
        
        class_obj.assigned_teachers.remove(teacher)
        
        return JsonResponse({
            'status': 'success',
            'message': f'{teacher.name} removed from {class_obj.name}'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error removing teacher: {str(e)}'
        }, status=400)

@login_required
@user_passes_test(is_admin)
@require_http_methods(['DELETE'])
def delete_class(request, class_id):
    """Soft delete a class"""
    try:
        class_obj = get_object_or_404(Class, id=class_id)
        class_obj.is_active = False
        class_obj.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Class "{class_obj.name}" deleted'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error deleting class: {str(e)}'
        }, status=400)