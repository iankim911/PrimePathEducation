"""
Phase 3: Template Compatibility Layer
Date: August 26, 2025
Purpose: Provides backward compatibility during migration from base.html and routinetest_base.html to unified_base.html
"""

import logging
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.http import HttpResponse
from pathlib import Path

logger = logging.getLogger(__name__)

class TemplateCompatibilityMiddleware:
    """
    Middleware to handle template migration compatibility.
    Maps old base templates to new unified_base.html during transition period.
    """
    
    # Templates that have been migrated to use unified_base.html
    MIGRATED_TEMPLATES = set([
        'test_unified_placement.html',
        'test_unified_routine.html',
        
        # Core module (15 templates) - BATCH 1 COMPLETED
        'core/auth/login.html',           # Batch 1 - Migrated Aug 27, 2025
        'core/index.html',                # Batch 1 - Migrated Aug 27, 2025  
        'core/auth/profile.html',         # Batch 1 - Migrated Aug 27, 2025
        'core/auth/logout_confirm.html',  # Batch 1 - Migrated Aug 27, 2025
        'core/base_clean.html',           # Batch 1 - Legacy adapter created Aug 27, 2025
        'core/exam_mapping.html',
        'core/login_with_kakao.html',
        'core/placement_configuration.html',
        'core/placement_rules_matrix.html',
        'core/placement_rules.html',
        'core/teacher_dashboard.html',
        'core/teacher_exams.html',
        'core/teacher_login.html',
        'core/teacher_sessions.html',
        'core/teacher_settings.html',
        
        # Registration (8 templates)
        'registration/choice.html',
        'registration/complete.html',
        'registration/step1_basic.html',
        'registration/step2_personal.html',
        'registration/step3_contact.html',
        'registration/step4_academic.html',
        'registration/step5_parent.html',
        'registration/step6_additional.html',
        
        # PlacementTest (2 templates)
        'placement_test/index.html',
        'placement_test/auth/login.html',
        
        # RoutineTest (37 templates - ALL migrated)
        'primepath_routinetest/admin_classes_teachers.html',
        'primepath_routinetest/admin_pending_requests.html',
        'primepath_routinetest/admin_teacher_management.html',
        'primepath_routinetest/admin/manage_classes.html',
        'primepath_routinetest/analytics/dashboard.html',
        'primepath_routinetest/auth/login.html',
        'primepath_routinetest/class_access_admin.html',
        'primepath_routinetest/class_access.html',
        'primepath_routinetest/class_code_overview.html',
        'primepath_routinetest/class_details.html',
        'primepath_routinetest/classes_exams_unified_backup.html',
        'primepath_routinetest/classes_exams_unified.html',
        'primepath_routinetest/create_exam_fixed.html',
        'primepath_routinetest/create_exam.html',
        'primepath_routinetest/dashboards/admin_dashboard.html',
        'primepath_routinetest/dashboards/student_dashboard.html',
        'primepath_routinetest/dashboards/teacher_dashboard.html',
        'primepath_routinetest/edit_exam.html',
        'primepath_routinetest/error.html',
        'primepath_routinetest/exam_detail.html',
        'primepath_routinetest/exam_list_hierarchical_backup.html',
        'primepath_routinetest/exam_list_hierarchical_fixed.html',
        'primepath_routinetest/exam_list_hierarchical.html',
        'primepath_routinetest/exam_list.html',
        'primepath_routinetest/exam_results.html',
        'primepath_routinetest/grade_session.html',
        'primepath_routinetest/index.html',
        'primepath_routinetest/manage_questions.html',
        'primepath_routinetest/manage_roster.html',
        'primepath_routinetest/preview_and_answers.html',
        'primepath_routinetest/session_detail.html',
        'primepath_routinetest/session_list.html',
        'primepath_routinetest/start_test.html',
        'primepath_routinetest/teacher_assessment.html',
        'primepath_routinetest/test_result.html',
        
        # Student Portal (8 templates - BATCH 2 - August 27, 2025)
        'primepath_student/auth/login.html',
        'primepath_student/auth/register.html',
        'primepath_student/dashboard.html',
        'primepath_student/profile.html',
        'primepath_student/class_detail.html',
        'primepath_student/exam/take_exam.html',
        'primepath_student/exam/exam_result.html',
        'primepath_student/exam/exam_history.html',
        
        # Total: 72 templates migrated to unified_base.html (54.1% complete)
    ])
    
    # Map of old base templates to new unified base
    BASE_TEMPLATE_MAP = {
        'base.html': 'unified_base.html',
        'routinetest_base.html': 'unified_base.html',
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.compatibility_mode = True  # Can be toggled via settings
        
    def __call__(self, request):
        """Process the request and response."""
        
        # Add compatibility flag to request
        request.template_compatibility = {
            'mode': self.compatibility_mode,
            'migrated': self.MIGRATED_TEMPLATES,
            'mapping': self.BASE_TEMPLATE_MAP
        }
        
        # Process the response
        response = self.get_response(request)
        
        # Log template usage for migration tracking
        if hasattr(request, 'template_used'):
            self._log_template_usage(request.template_used)
            
        return response
    
    def _log_template_usage(self, template_name):
        """Log which base template is being used for migration tracking."""
        if template_name in self.MIGRATED_TEMPLATES:
            logger.debug(f"✅ {template_name} using unified_base.html")
        else:
            logger.debug(f"⏳ {template_name} still using old base template")

    @classmethod
    def is_template_migrated(cls, template_name):
        """Check if a template has been migrated to unified base."""
        return template_name in cls.MIGRATED_TEMPLATES
    
    @classmethod
    def mark_template_migrated(cls, template_name):
        """Mark a template as migrated (for use in migration scripts)."""
        cls.MIGRATED_TEMPLATES.add(template_name)
        logger.info(f"Marked {template_name} as migrated to unified_base.html")


class TemplateContextProcessor:
    """
    Context processor to inject compatibility data into template context.
    """
    
    def __init__(self, request):
        self.request = request
        
    def get_context_data(self):
        """Return compatibility context data."""
        context = {
            'using_unified_base': False,
            'template_module': 'core',
            'compatibility_mode': True,
        }
        
        # Check if current template is using unified base
        if hasattr(self.request, 'template_compatibility'):
            template_name = getattr(self.request, 'template_name', None)
            if template_name:
                context['using_unified_base'] = TemplateCompatibilityMiddleware.is_template_migrated(template_name)
                
        # Detect module from URL
        if '/placement/' in self.request.path:
            context['template_module'] = 'placement_test'
        elif '/RoutineTest/' in self.request.path:
            context['template_module'] = 'primepath_routinetest'
            
        return context


def template_compatibility(request):
    """
    Context processor function for template compatibility.
    Add to TEMPLATES['OPTIONS']['context_processors'] in settings.
    """
    processor = TemplateContextProcessor(request)
    return processor.get_context_data()