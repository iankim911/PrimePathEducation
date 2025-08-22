"""
Exam management views
Handles exam creation, editing, preview, and deletion
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
import time
from ..models import Exam, AudioFile, Question
from core.models import CurriculumLevel
from core.exceptions import ValidationException, ExamConfigurationException
from core.decorators import handle_errors
from ..services import ExamService
from ..services.exam_service import ExamPermissionService
import logging
import json

logger = logging.getLogger(__name__)


@login_required
def exam_list(request):
    """List all exams hierarchically by Program and Class Code - Version 6.0 Library View"""
    from collections import defaultdict
    
    # Get filters from request - NEW OWNERSHIP-BASED SYSTEM
    exam_type_filter = request.GET.get('exam_type', 'ALL')
    ownership_filter = request.GET.get('ownership', 'my')  # NEW: 'my' or 'others'
    
    # BACKWARD COMPATIBILITY: Support old assigned_only parameter
    assigned_only_param = request.GET.get('assigned_only', 'false')
    legacy_show_assigned_only = assigned_only_param.lower() == 'true'
    
    # If old parameter is used, convert to new system
    if 'assigned_only' in request.GET and 'ownership' not in request.GET:
        ownership_filter = 'my' if legacy_show_assigned_only else 'others'
    
    # CRITICAL: Apply ownership logic to determine effective filtering
    if ownership_filter == 'my':
        show_assigned_only = True  # My Test Files = filter out VIEW ONLY
    elif ownership_filter == 'others':
        show_assigned_only = False  # Other Teachers' Test Files = show all including VIEW ONLY
    else:
        show_assigned_only = legacy_show_assigned_only  # Fallback to legacy
    
    # DEBUG: Enhanced logging for new system
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[OWNERSHIP_SYSTEM_DEBUG] URL: {request.get_full_path()}")
    logger.info(f"[OWNERSHIP_SYSTEM_DEBUG] ownership parameter: '{ownership_filter}'")
    logger.info(f"[OWNERSHIP_SYSTEM_DEBUG] exam_type parameter: '{exam_type_filter}'")
    logger.info(f"[OWNERSHIP_SYSTEM_DEBUG] Legacy assigned_only: '{assigned_only_param}' -> {show_assigned_only}")
    logger.info(f"[OWNERSHIP_SYSTEM_DEBUG] All GET params: {dict(request.GET)}")
    
    # Validate filters
    valid_exam_types = ['REVIEW', 'QUARTERLY', 'ALL']
    valid_ownership_types = ['my', 'others']
    
    if exam_type_filter not in valid_exam_types:
        exam_type_filter = 'ALL'
        
    if ownership_filter not in valid_ownership_types:
        ownership_filter = 'my'  # Default to "My Test Files"
    
    # Get permission info for current user - UPDATED FOR GLOBAL ACCESS SYSTEM
    is_admin = request.user.is_superuser or request.user.is_staff
    teacher = None
    global_access_level = 'FULL'  # Default for admin
    can_manage_exams = True      # Default for admin
    
    if not is_admin:
        # Get teacher profile and check GLOBAL access level
        try:
            teacher = request.user.teacher_profile
            global_access_level = teacher.global_access_level
            can_manage_exams = teacher.can_manage_exams()
            
            logger.info(f"[GLOBAL_ACCESS_EXAM_LIBRARY] Teacher {teacher.name}: Global access = {global_access_level}, Can manage = {can_manage_exams}")
            print(f"[GLOBAL_ACCESS_EXAM_LIBRARY] {teacher.name} - Global: {global_access_level}, Manage: {can_manage_exams}")
        except:
            # No teacher profile - treat as view only
            global_access_level = 'VIEW_ONLY'
            can_manage_exams = False
            logger.warning(f"[GLOBAL_ACCESS_EXAM_LIBRARY] User {request.user.username} has no teacher profile - defaulting to VIEW_ONLY")
    
    teacher_assignments = ExamPermissionService.get_teacher_assignments(request.user)
    
    # ENHANCED DEBUG LOGGING FOR GLOBAL ACCESS SYSTEM
    debug_info = {
        "user": request.user.username,
        "is_superuser": request.user.is_superuser,
        "is_staff": request.user.is_staff,
        "is_admin": is_admin,
        "has_teacher_profile": hasattr(request.user, 'teacher_profile'),
        "global_access_level": global_access_level,
        "can_manage_exams": can_manage_exams,
        "teacher_assignments_count": len(teacher_assignments),
        "view": "exam_list_global_access",
        "timestamp": timezone.now().isoformat()
    }
    
    logger.info(f"[GLOBAL_ACCESS_DEBUG] {json.dumps(debug_info)}")
    print(f"\n{'='*80}")
    print(f"[GLOBAL_ACCESS_DEBUG] Exam Library Permission Check:")
    print(f"  User: {request.user.username}")
    print(f"  is_superuser: {request.user.is_superuser}")
    print(f"  is_staff: {request.user.is_staff}")
    print(f"  is_admin (calculated): {is_admin}")
    print(f"  has_teacher_profile: {hasattr(request.user, 'teacher_profile')}")
    print(f"  global_access_level: {global_access_level}")
    print(f"  can_manage_exams: {can_manage_exams}")
    print(f"{'='*80}\n")
    
    # Log authentication and permissions
    console_log = {
        "view": "exam_list",
        "version": "6.0-answer-keys-library",
        "user": str(request.user),
        "is_admin": is_admin,
        "teacher_assignments": list(teacher_assignments.keys()),
        "assigned_only_filter": show_assigned_only,
        "exam_type_filter": exam_type_filter,
        "timestamp": timezone.now().isoformat()
    }
    logger.info(f"[EXAM_LIST_V6_LIBRARY] {json.dumps(console_log)}")
    print(f"[EXAM_LIST_V6_LIBRARY] {json.dumps(console_log)}")
    
    # Build base query with related data
    base_query = Exam.objects.select_related(
        'curriculum_level__subprogram__program',
        'created_by'  # CRITICAL: Include created_by for ownership checks
    ).prefetch_related(
        'routine_questions',
        'routine_audio_files'
    )
    
    # Apply exam type filter
    if exam_type_filter == 'REVIEW':
        exams = base_query.filter(exam_type='REVIEW')
        filter_description = "Review/Monthly Exams"
    elif exam_type_filter == 'QUARTERLY':
        exams = base_query.filter(exam_type='QUARTERLY')
        filter_description = "Quarterly Exams"
    else:
        exams = base_query.all()
        filter_description = "All Exams"
    
    # UPDATED: New ownership-based filtering description
    if ownership_filter == 'my':
        filter_description += " (My Test Files)"
    elif ownership_filter == 'others':
        filter_description += " (Other Teachers' Test Files)"
    
    # Backward compatibility support
    if 'assigned_only' in request.GET and ownership_filter == 'my':
        filter_description = filter_description.replace(" (My Test Files)", " (Assigned Classes Only)")
        
    logger.info(f"[OWNERSHIP_SYSTEM_DEBUG] Final filter description: {filter_description}")
    logger.info(f"[OWNERSHIP_SYSTEM_DEBUG] Effective show_assigned_only: {show_assigned_only}")
    
    # Add answer mapping status to each exam
    for exam in exams:
        exam.answer_mapping_status = exam.get_answer_mapping_status()
    
    # UPDATED: Organize exams hierarchically with new ownership-based filtering
    logger.info(f"[OWNERSHIP_SYSTEM_DEBUG] About to call organize_exams_hierarchically")
    logger.info(f"[OWNERSHIP_SYSTEM_DEBUG] Ownership filter: {ownership_filter}")
    logger.info(f"[OWNERSHIP_SYSTEM_DEBUG] Legacy filter_assigned_only: {show_assigned_only}")
    logger.info(f"[OWNERSHIP_SYSTEM_DEBUG] Number of exams before filtering: {exams.count()}")
    
    # NEW: Enhanced service call with ownership parameter
    hierarchical_exams = ExamService.organize_exams_hierarchically(
        exams, 
        request.user, 
        filter_assigned_only=show_assigned_only,  # Backward compatibility 
        ownership_filter=ownership_filter  # NEW: ownership-based filtering
    )
    
    # CRITICAL FIX: Double-check filtering at view level
    # If filter is ON, ensure NO VIEW ONLY exams are in the result
    if show_assigned_only and not is_admin:
        logger.info(f"[FILTER_DOUBLE_CHECK] Filter is ON - removing any VIEW ONLY exams that slipped through")
        filtered_hierarchical = {}
        view_only_removed = 0
        
        for program, program_classes in hierarchical_exams.items():
            filtered_program = {}
            for class_code, class_exams in program_classes.items():
                filtered_exams = []
                for exam in class_exams:
                    # Check if exam has VIEW ONLY badge
                    if hasattr(exam, 'access_badge'):
                        if exam.access_badge == 'VIEW ONLY':
                            logger.warning(f"[FILTER_DOUBLE_CHECK] ❌ REMOVING VIEW ONLY exam: {exam.name} (ID: {exam.id})")
                            view_only_removed += 1
                            continue  # Skip this exam
                        else:
                            logger.info(f"[FILTER_DOUBLE_CHECK] ✅ Keeping exam: {exam.name} with badge: {exam.access_badge}")
                            filtered_exams.append(exam)
                    else:
                        # Exam doesn't have access_badge attribute - keep it
                        filtered_exams.append(exam)
                
                # Only add class if it has exams after filtering
                if filtered_exams:
                    filtered_program[class_code] = filtered_exams
            
            # Only add program if it has classes with exams
            if filtered_program:
                filtered_hierarchical[program] = filtered_program
        
        logger.info(f"[FILTER_DOUBLE_CHECK] Removed {view_only_removed} VIEW ONLY exams from final result")
        hierarchical_exams = filtered_hierarchical
    
    # Count exams after filtering
    total_after = sum(len(exam_list) for program in hierarchical_exams.values() for exam_list in program.values())
    logger.info(f"[FILTER_VIEW_DEBUG] Number of exams after filtering: {total_after}")
    
    # Debug logging
    logger.info(f"[EXAM_LIST_DEBUG] Total exams before hierarchical: {exams.count()}")
    logger.info(f"[EXAM_LIST_DEBUG] hierarchical_exams type: {type(hierarchical_exams)}")
    logger.info(f"[EXAM_LIST_DEBUG] hierarchical_exams keys: {list(hierarchical_exams.keys())}")
    for program, program_data in hierarchical_exams.items():
        if program_data:
            logger.info(f"[EXAM_LIST_DEBUG] {program}: {len(program_data)} classes, type: {type(program_data)}")
            for class_code, class_exams in list(program_data.items())[:2]:  # Log first 2 classes
                logger.info(f"[EXAM_LIST_DEBUG]   {class_code}: {len(class_exams)} exams")
    
    # Calculate summary statistics
    total_exam_count = 0
    complete_count = 0
    partial_count = 0
    not_started_count = 0
    accessible_count = 0
    editable_count = 0
    
    for program_classes in hierarchical_exams.values():
        for class_exams in program_classes.values():
            for exam in class_exams:
                total_exam_count += 1
                
                # Answer mapping status
                if exam.answer_mapping_status['is_complete']:
                    complete_count += 1
                elif exam.answer_mapping_status['status_label'] == 'Partial':
                    partial_count += 1
                elif exam.answer_mapping_status['status_label'] == 'Not Started':
                    not_started_count += 1
                
                # Permission counts
                if exam.is_accessible:
                    accessible_count += 1
                if exam.can_edit:
                    editable_count += 1
    
    # Get counts for each exam type (for tabs)
    review_count = Exam.objects.filter(exam_type='REVIEW').count()
    quarterly_count = Exam.objects.filter(exam_type='QUARTERLY').count()
    total_count = Exam.objects.count()
    
    # Calculate assigned count
    assigned_count = accessible_count
    
    # Log hierarchical organization results
    console_log = {
        "view": "exam_list", 
        "action": "hierarchical_organization_complete",
        "programs_with_exams": {
            program: len(classes) for program, classes in hierarchical_exams.items() if classes
        },
        "total_exams": total_exam_count,
        "accessible_exams": accessible_count,
        "editable_exams": editable_count,
        "assigned_exams": assigned_count,
        "answer_mapping": {
            "complete": complete_count,
            "partial": partial_count,
            "not_started": not_started_count
        }
    }
    logger.info(f"[EXAM_LIST_HIERARCHY_COMPLETE] {json.dumps(console_log)}")
    
    # Get editable classes for the current user
    editable_classes = [
        class_code for class_code, access_level in teacher_assignments.items()
        if access_level in ['FULL', 'CO_TEACHER']
    ]
    
    # Create class display name dictionary
    class_display_names = {}
    for program_classes in ExamService.PROGRAM_CLASS_MAPPING.values():
        for class_code in program_classes:
            class_display_names[class_code] = ExamService.get_class_display_name(class_code)
    
    # Debug: Log what we're passing to template
    logger.info(f"[EXAM_LIST_CONTEXT] Passing is_admin={is_admin} to template")
    
    # Get curriculum data for copy modal - use hierarchy for better frontend integration
    curriculum_data_for_copy_modal = ExamService.get_routinetest_curriculum_levels()
    curriculum_hierarchy_for_copy = ExamService.get_routinetest_curriculum_hierarchy()
    
    # Prepare context for template
    context = {
        'hierarchical_exams': hierarchical_exams,
        'program_order': ExamService.PROGRAM_CLASS_MAPPING.keys(),
        'teacher_assignments': teacher_assignments,
        'editable_classes': editable_classes,
        'is_admin': is_admin,
        
        # NEW: Global access system variables
        'global_access_level': global_access_level,
        'can_manage_exams': can_manage_exams,
        'is_view_only_teacher': global_access_level == 'VIEW_ONLY' and not is_admin,
        'mapping_summary': {
            'total': total_exam_count,
            'complete': complete_count,
            'partial': partial_count,
            'not_started': not_started_count,
            'accessible': accessible_count,
            'editable': editable_count
        },
        
        # Copy modal curriculum data
        'curriculum_levels_for_copy': curriculum_data_for_copy_modal,
        'curriculum_hierarchy_for_copy': curriculum_hierarchy_for_copy,
        'exam_type_filter': exam_type_filter,
        'show_assigned_only': show_assigned_only,  # Keep for backward compatibility
        
        # NEW: Ownership-based system variables
        'ownership_filter': ownership_filter,
        'is_my_files_active': ownership_filter == 'my',
        'is_others_files_active': ownership_filter == 'others',
        
        'exam_type_counts': {
            'review': review_count,
            'quarterly': quarterly_count,
            'all': total_count,
            'assigned': assigned_count
        },
        'filter_description': filter_description,
        'template_version': '6.0-answer-keys-library',
        'cache_bust_id': timezone.now().timestamp(),
        
        # Class display names dictionary
        'get_class_display_name': class_display_names,
        
        # Feature flags
        'features': {
            'copy_exam': True,
            'permission_based_access': True,
            'hierarchical_display': True,
            'assigned_filter': True
        }
    }
    
    response = render(request, 'primepath_routinetest/exam_list_hierarchical.html', context)
    
    # NUCLEAR CACHE PREVENTION - absolutely no caching allowed
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, s-maxage=0, proxy-revalidate, private, no-transform'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response['Last-Modified'] = 'Wed, 22 Aug 2025 00:00:00 GMT'
    response['ETag'] = f'"{hash(str(request.GET) + str(request.user.id) + str(timezone.now().timestamp()))}"'
    response['Vary'] = 'Cookie, User-Agent, Accept-Encoding'
    
    # Additional debugging headers
    response['X-Cache-Control'] = 'no-cache'
    response['X-No-Cache'] = '1'
    response['X-Filter-State'] = 'on' if show_assigned_only else 'off'
    response['X-Response-Time'] = str(time.time())
    response['X-Template-Version'] = '6.0-answer-keys-library'
    response['X-Feature'] = 'ANSWER-KEYS-LIBRARY'
    
    return response


@handle_errors(ajax_only=True)
@login_required
def check_exam_version(request):
    """API endpoint to get the next available version for a curriculum level"""
    from datetime import datetime
    
    curriculum_level_id = request.GET.get('curriculum_level')
    if not curriculum_level_id:
        raise ValidationException(
            "curriculum_level parameter is required",
            code="MISSING_PARAM"
        )
    
    try:
        # Get today's date in YYMMDD format
        date_str = datetime.now().strftime('%y%m%d')
        
        # Get next version number (will be None if no same-day uploads)
        next_version = ExamService.get_next_version_number(int(curriculum_level_id), date_str)
        
        return JsonResponse({
            'next_version': next_version,
            'date_str': date_str
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'next_version': None,
            'date_str': datetime.now().strftime('%y%m%d')
        }, status=400)


@login_required
@handle_errors(template_name='primepath_routinetest/create_exam.html')
def create_exam(request):
    """Create a new exam (requires authentication)"""
    # Get Teacher profile for the authenticated user
    teacher_profile = None
    if request.user.is_authenticated:
        try:
            teacher_profile = request.user.teacher_profile
            console_log = {
                "view": "create_exam",
                "action": "teacher_profile_found",
                "user": str(request.user),
                "teacher_id": teacher_profile.id,
                "teacher_name": teacher_profile.name,
                "is_head_teacher": teacher_profile.is_head_teacher
            }
            logger.info(f"[CREATE_EXAM_TEACHER] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_TEACHER] {json.dumps(console_log)}")
        except AttributeError as e:
            # Handle case where teacher_profile doesn't exist
            # Create a Teacher profile on-the-fly for authenticated users
            from core.models import Teacher
            teacher_profile = Teacher.objects.create(
                user=request.user,
                name=request.user.get_full_name() or request.user.username,
                email=request.user.email or f"{request.user.username}@example.com",
                is_head_teacher=request.user.is_superuser
            )
            console_log = {
                "view": "create_exam",
                "action": "teacher_profile_created",
                "user": str(request.user),
                "teacher_id": teacher_profile.id,
                "teacher_name": teacher_profile.name,
                "reason": "Profile did not exist, created automatically"
            }
            logger.warning(f"[CREATE_EXAM_TEACHER_CREATED] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_TEACHER_CREATED] {json.dumps(console_log)}")
    
    # Log authentication check
    console_log = {
        "view": "create_exam",
        "user": str(request.user),
        "authenticated": request.user.is_authenticated,
        "has_teacher_profile": teacher_profile is not None,
        "teacher_id": teacher_profile.id if teacher_profile else None,
        "method": request.method
    }
    logger.info(f"[CREATE_EXAM] {json.dumps(console_log)}")
    print(f"[CREATE_EXAM_AUTH] {json.dumps(console_log)}")
    
    if request.method == 'POST':
        try:
            # Validate required fields
            exam_name = request.POST.get('name')
            if not exam_name:
                raise ValidationException("Exam name is required", code="MISSING_NAME")
            
            # Get auto-generation components (for logging)
            generated_base_name = request.POST.get('generated_base_name', '')
            user_comment = request.POST.get('user_comment', '')
            
            # Log the auto-generated name components
            console_log = {
                "view": "create_exam",
                "action": "auto_name_received",
                "full_name": exam_name,
                "base_name": generated_base_name,
                "user_comment": user_comment,
                "has_comment": bool(user_comment),
                "timestamp": timezone.now().isoformat()
            }
            logger.info(f"[AUTO_NAME_GEN_BACKEND] {json.dumps(console_log)}")
            print(f"[AUTO_NAME_GEN_BACKEND] {json.dumps(console_log)}")
            
            # EXAM CONFIGURATION FIELDS VALIDATION AND LOGGING
            console_log = {
                "view": "create_exam",
                "action": "exam_config_fields_received",
                "timer_minutes_raw": request.POST.get('timer_minutes'),
                "total_questions_raw": request.POST.get('total_questions'),
                "default_options_count_raw": request.POST.get('default_options_count'),
                "timestamp": timezone.now().isoformat()
            }
            logger.info(f"[EXAM_CONFIG_FIELDS] {json.dumps(console_log)}")
            print(f"[EXAM_CONFIG_FIELDS] {json.dumps(console_log)}")
            
            total_questions = request.POST.get('total_questions')
            if not total_questions:
                raise ValidationException("Total number of questions is required", code="MISSING_QUESTIONS")
            
            # Get exam type from form
            exam_type = request.POST.get('exam_type', 'REVIEW')
            
            # Phase 2: Get time period fields based on exam type
            time_period_month = None
            time_period_quarter = None
            academic_year = request.POST.get('academic_year', '').strip() or None
            
            if exam_type == 'REVIEW':
                time_period_month = request.POST.get('time_period_month', '').strip() or None
            elif exam_type == 'QUARTERLY':
                time_period_quarter = request.POST.get('time_period_quarter', '').strip() or None
            
            
            # Phase 3: Get selected class codes
            class_codes = request.POST.getlist('class_codes[]')  # Get array of selected class codes
            
            # CRITICAL: Validate that teacher can only select their assigned classes
            if not (request.user.is_superuser or request.user.is_staff):
                teacher_assignments = ExamService.get_teacher_assignments(request.user)
                invalid_classes = [code for code in class_codes if code not in teacher_assignments]
                
                if invalid_classes:
                    error_msg = f"You cannot create exams for classes you're not assigned to: {', '.join(invalid_classes)}"
                    logger.warning(f"[CREATE_EXAM_VALIDATION] Teacher {request.user.username} tried to select unauthorized classes: {invalid_classes}")
                    print(f"[CREATE_EXAM_VALIDATION] BLOCKED: Teacher tried to select {invalid_classes}")
                    messages.error(request, error_msg)
                    return redirect('RoutineTest:create_exam')
                
                logger.info(f"[CREATE_EXAM_VALIDATION] Teacher {request.user.username} selected valid classes: {class_codes}")
            
            # Get general instructions (kept at exam level)
            instructions = request.POST.get('instructions', '').strip()
            # Note: Scheduling is now handled per-class via ClassExamSchedule
            
            # Log exam creation attempt with all phases data
            console_log = {
                "view": "create_exam",
                "action": "exam_creation_attempt",
                "exam_name": exam_name,
                "exam_type": exam_type,
                "time_period_month": time_period_month,
                "time_period_quarter": time_period_quarter,
                "academic_year": academic_year,
                "class_codes": class_codes,  # Phase 3: Log selected classes
                "class_codes_count": len(class_codes),
                "has_instructions": bool(instructions),
                "total_questions": total_questions,
                "timer_minutes": request.POST.get('timer_minutes', 60),
                "default_options_count": request.POST.get('default_options_count', 5),
                "created_by_teacher_id": teacher_profile.id if teacher_profile else None,
                "created_by_teacher_name": teacher_profile.name if teacher_profile else None,
                "note": "Class-specific scheduling will be set separately after exam creation"
            }
            logger.info(f"[CREATE_EXAM_ATTEMPT] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_ATTEMPT] {json.dumps(console_log)}")
            
            # Prepare exam data with validation
            exam_data = {
                'name': exam_name,
                'exam_type': exam_type,  # Add exam type to data
                'time_period_month': time_period_month,  # Phase 2: Add month
                'time_period_quarter': time_period_quarter,  # Phase 2: Add quarter
                'academic_year': academic_year,  # Phase 2: Add academic year
                'class_codes': class_codes,  # Phase 3: Add selected class codes
                'instructions': instructions,  # General instructions (kept at exam level)
                'curriculum_level_id': request.POST.get('curriculum_level', '').strip() or None,
                'timer_minutes': int(request.POST.get('timer_minutes', 60)),
                'total_questions': int(total_questions),
                'default_options_count': int(request.POST.get('default_options_count', 5)),
                'passing_score': 0,
                'pdf_rotation': int(request.POST.get('pdf_rotation', 0)),  # Add rotation from form
                'created_by': teacher_profile,  # Use Teacher instance, not User instance
                'is_active': True
            }
            
            # Validate PDF file
            pdf_file = request.FILES.get('pdf_file')
            if not pdf_file:
                raise ValidationException("PDF file is required", code="MISSING_PDF")
            
            # Log the file upload details
            console_log = {
                "view": "create_exam",
                "action": "file_upload_details",
                "pdf_file_name": pdf_file.name if pdf_file else None,
                "pdf_file_size": pdf_file.size if pdf_file else 0,
                "pdf_file_content_type": pdf_file.content_type if pdf_file else None,
                "audio_files_count": len(request.FILES.getlist('audio_files')),
                "audio_names_count": len(request.POST.getlist('audio_names[]'))
            }
            logger.info(f"[CREATE_EXAM_FILES] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_FILES] {json.dumps(console_log)}")
            
            # Use ExamService to create exam with files
            exam = ExamService.create_exam(
                exam_data=exam_data,
                pdf_file=pdf_file,
                audio_files=request.FILES.getlist('audio_files'),
                audio_names=request.POST.getlist('audio_names[]')
            )
            
            # Log successful exam creation
            console_log = {
                "view": "create_exam",
                "action": "exam_created_successfully",
                "exam_id": str(exam.id),
                "exam_name": exam.name,
                "exam_type": exam.exam_type,
                "created_by_teacher_id": exam.created_by.id if exam.created_by else None,
                "created_by_teacher_name": exam.created_by.name if exam.created_by else None,
                "total_questions": exam.total_questions,
                "pdf_file": exam.pdf_file.name if exam.pdf_file else None
            }
            logger.info(f"[CREATE_EXAM_SUCCESS] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_SUCCESS] {json.dumps(console_log)}")
            
            messages.success(request, f'Exam "{exam.name}" uploaded successfully!')
            return redirect('RoutineTest:create_exam')
            
        except ValueError as e:
            console_log = {
                "view": "create_exam",
                "action": "value_error",
                "error": str(e),
                "user": str(request.user)
            }
            logger.error(f"[CREATE_EXAM_ERROR] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_ERROR] {json.dumps(console_log)}")
            messages.error(request, f"Invalid input: {str(e)}")
            # Fall through to render the form again with error message
        except ValidationException as e:
            console_log = {
                "view": "create_exam",
                "action": "validation_error",
                "error_code": e.code if hasattr(e, 'code') else None,
                "error_message": e.message if hasattr(e, 'message') else str(e),
                "user": str(request.user)
            }
            logger.error(f"[CREATE_EXAM_VALIDATION_ERROR] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_VALIDATION_ERROR] {json.dumps(console_log)}")
            messages.error(request, e.message if hasattr(e, 'message') else str(e))
            # Fall through to render the form again with error message
        except Exception as e:
            console_log = {
                "view": "create_exam",
                "action": "unexpected_error",
                "error_type": type(e).__name__,
                "error": str(e),
                "user": str(request.user)
            }
            logger.exception(f"[CREATE_EXAM_UNEXPECTED_ERROR] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_UNEXPECTED_ERROR] {json.dumps(console_log)}")
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            # Fall through to render the form again with error message
    
    # Get RoutineTest curriculum levels using ExamService
    # This uses the ROUTINETEST_CURRICULUM_WHITELIST from constants.py
    from datetime import datetime
    
    # Log curriculum levels retrieval start
    console_log = {
        "view": "create_exam",
        "action": "getting_routinetest_curriculum_levels",
        "message": "Using ExamService to get filtered RoutineTest curriculum levels"
    }
    logger.info(f"[CREATE_EXAM_CURRICULUM] {json.dumps(console_log)}")
    print(f"[CREATE_EXAM_CURRICULUM] {json.dumps(console_log)}")
    
    # Get RoutineTest curriculum levels from ExamService
    curriculum_levels_data = ExamService.get_routinetest_curriculum_levels()
    
    # Get today's date for version checking
    today_str = datetime.now().strftime('%y%m%d')
    
    # Add version info to each level for RoutineTest naming
    levels_with_versions = []
    for level_data in curriculum_levels_data:
        curriculum_level = level_data['curriculum_level']
        
        # Check if there are existing uploads today for this level
        next_version = ExamService.get_next_version_number(curriculum_level.id, today_str)
        
        # Get count of existing exams for this level (for info display)
        existing_count = Exam.objects.filter(curriculum_level=curriculum_level).count()
        
        # Create RoutineTest specific display name using [RT]/[QTR] format
        # Format: "[RT/QTR] - [Time Period] - PROGRAM SUBPROGRAM Level X"
        rt_display_name = level_data['routinetest_display_preview']
        
        # Clean base name for file generation (used in exam name)
        # Format: "PROGRAM_SUBPROGRAM_LvX"
        program_name = level_data['program_name']
        subprogram_name = level_data['subprogram_name']
        level_number = level_data['level_number']
        rt_base_name = f"{program_name}_{subprogram_name}_Lv{level_number}".replace(" ", "_")
        
        levels_with_versions.append({
            'id': curriculum_level.id,
            'display_name': rt_display_name,  # Use RT-specific display name
            'exam_base_name': rt_base_name,  # Use RT-specific base name
            'next_version': next_version,
            'existing_count': existing_count,
            'date_str': today_str,
            'program_name': program_name,
            'subprogram_name': subprogram_name,
            'level_number': level_number
        })
        
        # Log each level being added
        console_log = {
            "view": "create_exam",
            "action": "routinetest_level_added",
            "level_id": curriculum_level.id,
            "rt_display_name": rt_display_name,
            "rt_base_name": rt_base_name,
            "existing_count": existing_count
        }
        logger.debug(f"[CREATE_EXAM_RT_LEVEL] {json.dumps(console_log)}")
        print(f"[CREATE_EXAM_RT_LEVEL] {json.dumps(console_log)}")
    
    # Log final results
    console_log = {
        "view": "create_exam",
        "action": "routinetest_curriculum_levels_loaded",
        "total_levels": len(levels_with_versions),
        "programs": list(set(level['program_name'] for level in levels_with_versions))
    }
    logger.info(f"[CREATE_EXAM_RT_FINAL] {json.dumps(console_log)}")
    print(f"[CREATE_EXAM_RT_FINAL] {json.dumps(console_log)}")
    
    # CRITICAL FIX: Get FILTERED class choices based on teacher's assignments
    # For Upload/Create, teachers should only see classes where they have FULL access
    class_choices = ExamService.get_filtered_class_choices_for_teacher(request.user, full_access_only=True)
    
    # Debug: Log filtered class choices to verify proper filtering
    console_log = {
        "view": "create_exam",
        "action": "filtered_class_choices_loaded",
        "user": request.user.username,
        "is_admin": request.user.is_superuser or request.user.is_staff,
        "class_count": len(class_choices),
        "class_codes": [code for code, _ in class_choices][:5] if class_choices else [],
        "sample_classes": class_choices[:3] if class_choices else [],
        "message": "FILTERED class choices based on teacher assignments"
    }
    logger.info(f"[CREATE_EXAM_FILTERED_CLASSES] {json.dumps(console_log)}")
    print(f"[CREATE_EXAM_FILTERED_CLASSES] User {request.user.username} sees {len(class_choices)} classes (filtered)")
    
    # Create context with comprehensive debugging
    context = {
        'curriculum_levels': levels_with_versions,
        'class_choices': class_choices,
        'class_choices_count': len(class_choices),  # For template debugging
        'class_choices_json': json.dumps(class_choices),  # For JS debugging
        'debug_info': {
            'view_name': 'create_exam',
            'timestamp': timezone.now().isoformat(),
            'user': str(request.user),
            'class_choices_loaded': bool(class_choices),
            'curriculum_levels_loaded': bool(levels_with_versions)
        }
    }
    
    # Final debug log before rendering
    console_log = {
        "view": "create_exam",
        "action": "rendering_template",
        "context_keys": list(context.keys()),
        "class_choices_type": str(type(class_choices)),
        "class_choices_length": len(class_choices),
        "template": "primepath_routinetest/create_exam.html"
    }
    logger.info(f"[CREATE_EXAM_RENDER] {json.dumps(console_log)}")
    print(f"[CREATE_EXAM_RENDER] {json.dumps(console_log)}")
    
    return render(request, 'primepath_routinetest/create_exam.html', context)


@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.routine_questions.all()
    audio_files = exam.routine_audio_files.all()  # Fixed: using correct related_name for RoutineTest
    
    context = {
        'exam': exam,
        'questions': questions,
        'audio_files': audio_files,
    }
    return render(request, 'primepath_routinetest/exam_detail.html', context)


@login_required
def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    return render(request, 'primepath_routinetest/edit_exam.html', {'exam': exam})


@login_required
def preview_exam(request, exam_id):
    """Preview exam with answer key management - WITH PERMISSION CHECK"""
    # Comprehensive debugging
    console_log = {
        "view": "preview_exam",
        "exam_id": str(exam_id),
        "user": str(request.user),
        "method": request.method,
        "timestamp": timezone.now().isoformat()
    }
    logger.info(f"[PREVIEW_EXAM_START] {json.dumps(console_log)}")
    print(f"[PREVIEW_EXAM_START] {json.dumps(console_log)}")
    
    exam = get_object_or_404(Exam, id=exam_id)
    
    # CRITICAL: Check if user can edit this exam
    can_edit = ExamService.can_teacher_edit_exam(request.user, exam)
    is_read_only = not can_edit
    
    # Log permission check result
    permission_log = {
        "exam_id": str(exam_id),
        "exam_name": exam.name,
        "user": request.user.username,
        "can_edit": can_edit,
        "is_read_only": is_read_only,
        "is_admin": request.user.is_superuser or request.user.is_staff,
        "is_owner": exam.created_by and hasattr(request.user, 'teacher_profile') and exam.created_by.id == request.user.teacher_profile.id
    }
    logger.info(f"[PREVIEW_EXAM_PERMISSION] {json.dumps(permission_log)}")
    print(f"[PREVIEW_EXAM_PERMISSION] User {request.user.username} {'CAN EDIT' if can_edit else 'READ-ONLY'} exam {exam.name}")
    
    # Log exam details
    exam_log = {
        "exam_name": exam.name,
        "exam_id": str(exam.id),
        "total_questions": exam.total_questions,
        "has_pdf": bool(exam.pdf_file),
        "is_active": exam.is_active,
        "exam_type": exam.exam_type
    }
    logger.info(f"[PREVIEW_EXAM_LOADED] {json.dumps(exam_log)}")
    print(f"[PREVIEW_EXAM_LOADED] {json.dumps(exam_log)}")
    
    # Get or create questions for the exam with audio files prefetched
    questions = exam.routine_questions.select_related('audio_file').all().order_by('question_number')
    
    # If no questions exist, create them based on total_questions
    if not questions.exists():
        for i in range(1, exam.total_questions + 1):
            Question.objects.create(
                exam=exam,
                question_number=i,
                question_type='MCQ',  # Default to MCQ since PDF contains the questions
                correct_answer='',
                points=1,
                options_count=exam.default_options_count
            )
        questions = exam.routine_questions.all().order_by('question_number')
    
    # Process questions to add response lists for short and long answers
    for question in questions:
        # For SHORT questions, populate response_list with saved values
        if question.question_type == 'SHORT':
            if question.correct_answer:
                # Check which separator is used
                if '|' in question.correct_answer:
                    # Pipe-separated values
                    question.response_list = question.correct_answer.split('|')
                elif ',' in question.correct_answer and question.options_count and question.options_count > 1:
                    # Comma-separated values with multiple fields expected
                    question.response_list = [s.strip() for s in question.correct_answer.split(',')]
                else:
                    # Single value or no special separator
                    question.response_list = [question.correct_answer] if question.correct_answer else []
            else:
                # No saved answer yet
                question.response_list = []
        else:
            question.response_list = []
            
        if question.question_type == 'LONG' and question.correct_answer:
            question.response_list = question.correct_answer.split('|')
        
        # For checkbox questions
        if question.question_type == 'CHECKBOX' and question.correct_answer:
            question.checked_values = question.correct_answer.split(',')
        else:
            question.checked_values = []
    
    # Get audio files
    audio_files = exam.routine_audio_files.all()  # Fixed: using correct related_name for RoutineTest
    
    # Log context being passed to template
    context_log = {
        "questions_count": questions.count(),
        "audio_files_count": audio_files.count(),
        "template": "primepath_routinetest/preview_and_answers.html",
        "exam_id": str(exam.id),
        "exam_name": exam.name
    }
    logger.info(f"[PREVIEW_EXAM_CONTEXT] {json.dumps(context_log)}")
    print(f"[PREVIEW_EXAM_CONTEXT] {json.dumps(context_log)}")
    
    # Build context with permission info
    context = {
        'exam': exam,
        'questions': questions,
        'audio_files': audio_files,
        'can_edit': can_edit,  # CRITICAL: Pass edit permission to template
        'is_read_only': is_read_only,  # For clarity in template
        'permission_message': 'Full Access' if can_edit else 'View Only - Cannot Save Changes'
    }
    
    # Log successful render attempt
    logger.info(f"[PREVIEW_EXAM_RENDER] Rendering template with context for exam: {exam.name}")
    print(f"[PREVIEW_EXAM_RENDER] Rendering template with context for exam: {exam.name}")
    
    return render(request, 'primepath_routinetest/preview_and_answers.html', context)


@login_required
def manage_questions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.routine_questions.all().order_by('question_number')
    
    if request.method == 'POST':
        # Process question updates
        for question in questions:
            question_type = request.POST.get(f'question_type_{question.id}')
            correct_answer = request.POST.get(f'correct_answer_{question.id}', '')
            points = request.POST.get(f'points_{question.id}', 1)
            
            if question_type:
                question.question_type = question_type
            question.correct_answer = correct_answer
            question.points = int(points)
            question.save()
        
        messages.success(request, 'Questions updated successfully!')
        return redirect('RoutineTest:manage_questions', exam_id=exam_id)
    
    return render(request, 'primepath_routinetest/manage_questions.html', {
        'exam': exam,
        'questions': questions,
    })


@require_http_methods(["POST", "DELETE"])
@login_required
def delete_exam(request, exam_id):
    """Delete an exam with comprehensive permission checking and debugging"""
    from django.http import JsonResponse
    from primepath_routinetest.models import TeacherClassAssignment
    from primepath_routinetest.services.exam_service import ExamPermissionService
    import json
    
    # CRITICAL: Log to file for persistence
    import os
    log_file = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/delete_debug.log'
    with open(log_file, 'a') as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"[{timezone.now().isoformat()}] DELETE EXAM VIEW CALLED\n")
        f.write(f"Method: {request.method}\n")
        f.write(f"User: {request.user.username if request.user else 'anonymous'}\n")
        f.write(f"User ID: {request.user.id if request.user else None}\n")
        f.write(f"Is Authenticated: {request.user.is_authenticated}\n")
        f.write(f"Is Staff: {request.user.is_staff}\n")
        f.write(f"Is Superuser: {request.user.is_superuser}\n")
        f.write(f"Exam ID: {exam_id}\n")
        f.write(f"Is AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}\n")
        f.write(f"Headers: {dict(request.headers)}\n")
    
    # IMMEDIATE DEBUG OUTPUT
    print(f"\n{'='*80}")
    print(f"DELETE EXAM CALLED - DEBUGGING")
    print(f"{'='*80}")
    print(f"Request User: {request.user}")
    print(f"User ID: {request.user.id}")
    print(f"Is Authenticated: {request.user.is_authenticated}")
    print(f"Is Staff: {request.user.is_staff}")
    print(f"Is Superuser: {request.user.is_superuser}")
    print(f"Exam ID: {exam_id}")
    print(f"Method: {request.method}")
    print(f"{'='*80}\n")
    
    # COMPREHENSIVE DEBUG LOGGING - REQUEST INFO
    debug_info = {
        "view": "delete_exam",
        "action": "delete_attempt_start",
        "user": request.user.username,
        "user_id": request.user.id,
        "exam_id": str(exam_id),
        "method": request.method,
        "is_ajax": request.headers.get('X-Requested-With') == 'XMLHttpRequest',
        "timestamp": timezone.now().isoformat()
    }
    logger.info(f"[DELETE_EXAM_VIEW] {json.dumps(debug_info)}")
    print(f"[DELETE_EXAM_VIEW] 🚨 DELETE ATTEMPT: {json.dumps(debug_info)}")
    
    exam = get_object_or_404(Exam, id=exam_id)
    exam_name = exam.name
    
    # COMPREHENSIVE DEBUG - EXAM INFO
    debug_info["exam_name"] = exam_name
    debug_info["exam_created_by_id"] = exam.created_by.id if exam.created_by else None
    debug_info["exam_created_by_name"] = exam.created_by.name if exam.created_by else None
    debug_info["exam_classes"] = exam.class_codes if hasattr(exam, 'class_codes') else []
    
    # Check permissions
    is_admin = request.user.is_superuser or request.user.is_staff
    debug_info["is_admin"] = is_admin
    
    if not is_admin:
        # Get teacher profile - try multiple methods
        teacher_profile = None
        
        # Method 1: Direct attribute
        if hasattr(request.user, 'teacher_profile'):
            teacher_profile = request.user.teacher_profile
            debug_info["teacher_profile_method"] = "direct_attribute"
        
        # Method 2: Database query if needed
        if not teacher_profile:
            try:
                from core.models import Teacher
                teacher_profile = Teacher.objects.filter(user=request.user).first()
                if teacher_profile:
                    debug_info["teacher_profile_method"] = "database_query"
            except Exception as e:
                debug_info["teacher_profile_error"] = str(e)
        
        if not teacher_profile:
            error_msg = "You do not have permission to delete this exam. No teacher profile found."
            debug_info["error"] = "No teacher profile"
            logger.error(f"[DELETE_EXAM_VIEW] {json.dumps(debug_info)}")
            print(f"[DELETE_EXAM_VIEW] ❌ NO TEACHER PROFILE: {json.dumps(debug_info)}")
            
            if request.method == 'DELETE' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg}, status=403)
            else:
                messages.error(request, error_msg)
                return redirect('RoutineTest:exam_list')
        
        debug_info["teacher_id"] = teacher_profile.id
        debug_info["teacher_name"] = teacher_profile.name
        
        # CRITICAL OWNERSHIP CHECK
        if exam.created_by:
            is_owner = exam.created_by.id == teacher_profile.id
            debug_info["ownership_check"] = {
                "is_owner": is_owner,
                "exam_created_by_id": exam.created_by.id,
                "teacher_id": teacher_profile.id,
                "match": is_owner
            }
            if is_owner:
                print(f"[DELETE_EXAM_VIEW] 👑 OWNER DETECTED: Teacher {teacher_profile.name} owns exam {exam_name}")
        
        # Check if teacher can delete this exam
        can_delete = ExamPermissionService.can_teacher_delete_exam(request.user, exam)
        debug_info["can_delete"] = can_delete
        
        # LOG TO FILE
        with open(log_file, 'a') as f:
            f.write(f"Permission check result: {can_delete}\n")
            f.write(f"Debug info: {json.dumps(debug_info)}\n")
        
        logger.info(f"[DELETE_EXAM_VIEW] Permission check complete: {json.dumps(debug_info)}")
        
        if not can_delete:
            # Get the exam's classes and teacher's access levels for a detailed message
            exam_classes = exam.class_codes if hasattr(exam, 'class_codes') and exam.class_codes else []
            
            # Get teacher's access levels for these classes
            teacher_assignments = TeacherClassAssignment.objects.filter(
                teacher=teacher_profile,
                is_active=True
            )
            
            access_details = []
            for class_code in exam_classes:
                assignment = teacher_assignments.filter(class_code=class_code).first()
                if assignment:
                    access_details.append(f"{class_code} ({assignment.access_level} access)")
                else:
                    access_details.append(f"{class_code} (no access)")
            
            # Build a clear, single error message
            if access_details:
                error_msg = (
                    f"Access Denied: You cannot delete this exam.\n\n"
                    f"Required: FULL access level or ownership\n"
                    f"Your access: {', '.join(access_details)}\n\n"
                    f"Only exam owners or teachers with FULL access can delete exams."
                )
            else:
                error_msg = (
                    f"Access Denied: You cannot delete this exam.\n\n"
                    f"This exam is assigned to classes: {', '.join(exam_classes) if exam_classes else 'none'}\n"
                    f"You do not have access to these classes."
                )
            
            # Enhanced debug info for permission denial
            debug_info["permission_denied"] = {
                "reason": "Insufficient permissions",
                "is_owner": exam.created_by.id == teacher_profile.id if exam.created_by else False,
                "access_details": access_details,
                "error_message": error_msg
            }
            
            logger.warning(f"[DELETE_EXAM_VIEW] Permission denied: {json.dumps(debug_info)}")
            print(f"[DELETE_EXAM_VIEW] ❌ PERMISSION DENIED: {json.dumps(debug_info)}")
            
            # LOG TO FILE
            with open(log_file, 'a') as f:
                f.write(f"PERMISSION DENIED\n")
                f.write(f"Returning 403 error\n")
            
            if request.method == 'DELETE' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return simple error message that won't be replaced by JavaScript
                simple_error = "You do not have adequate permissions to delete this exam."
                return JsonResponse({'success': False, 'error': simple_error}, status=403)
            else:
                messages.error(request, error_msg)
                return redirect('RoutineTest:exam_list')
    
    # CRITICAL FIX: This code should run for BOTH admins AND non-admins who pass permission check
    # The permission check above already verified if the user can delete
    # If we reach here, the user has permission to delete (either admin or owner/FULL access)
    
    debug_info["proceeding_to_delete"] = True
    logger.info(f"[DELETE_EXAM_VIEW] User has permission, proceeding to delete: {json.dumps(debug_info)}")
    print(f"[DELETE_EXAM_VIEW] ✅ PROCEEDING TO DELETE: User {request.user.username} deleting exam {exam_name}")
    
    # LOG TO FILE
    with open(log_file, 'a') as f:
        f.write(f"PERMISSION GRANTED - Proceeding to delete\n")
        f.write(f"User: {request.user.username}\n")
        f.write(f"Exam: {exam_name}\n")
    
    try:
        # Delete associated files
        if exam.pdf_file:
            exam.pdf_file.delete()
        
        # Delete audio files
        for audio in exam.routine_audio_files.all():  # Fixed: using correct related_name
            if audio.audio_file:
                audio.audio_file.delete()
            audio.delete()
        
        # Delete the exam (questions will cascade)
        exam.delete()
        
        success_message = f'Exam "{exam_name}" deleted successfully!'
        
        # Return JSON for AJAX requests (DELETE method or AJAX header)
        if request.method == 'DELETE' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': success_message})
        else:
            messages.success(request, success_message)
            return redirect('RoutineTest:exam_list')
        
    except Exception as e:
        error_message = f'Error deleting exam: {str(e)}'
        logger.error(error_message)
        
        # Return JSON for AJAX requests (DELETE method or AJAX header)
        if request.method == 'DELETE' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_message}, status=500)
        else:
            messages.error(request, error_message)
            return redirect('RoutineTest:exam_list')


# ========== ANSWER KEYS LIBRARY API ENDPOINTS ==========

@login_required
@require_http_methods(["GET"])
def get_teacher_copyable_classes(request):
    """API endpoint to get classes where teacher can copy exams to"""
    
    try:
        # Get teacher's assigned classes - can copy to ANY assigned class (not just FULL)
        # This aligns with the requirement that teachers can copy to all their assigned classes
        teacher_assignments = ExamService.get_teacher_assignments(request.user)
        copyable_classes = list(teacher_assignments.keys())  # ALL assigned classes are copyable destinations
        is_admin = request.user.is_superuser or request.user.is_staff
        
        # Convert to display format
        class_options = []
        if is_admin:
            # For admins, return all available class codes
            for program, classes in ExamService.PROGRAM_CLASS_MAPPING.items():
                for class_code in sorted(classes):
                    class_options.append({
                        'value': class_code,
                        'label': ExamService.get_class_display_name(class_code),
                        'program': program
                    })
        else:
            # For teachers, return their assigned classes
            for class_code in sorted(copyable_classes):
                # Find which program this class belongs to
                program = 'CORE'  # Default
                for prog, classes in ExamService.PROGRAM_CLASS_MAPPING.items():
                    if class_code in classes:
                        program = prog
                        break
                
                class_options.append({
                    'value': class_code,
                    'label': ExamService.get_class_display_name(class_code),
                    'program': program
                })
        
        return JsonResponse({
            'success': True,
            'classes': class_options,
            'is_admin': is_admin,
            'total_classes': len(class_options)
        })
        
    except Exception as e:
        logger.error(f"[GET_COPYABLE_CLASSES] Error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def copy_exam(request, exam_id):
    """API endpoint to copy an exam to different classes"""
    from ..services import ExamPermissionService
    
    try:
        # Get source exam
        source_exam = get_object_or_404(Exam, id=exam_id)
        
        # Check if user can copy this exam
        if not ExamPermissionService.can_teacher_copy_exam(request.user, source_exam):
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to copy this exam'
            }, status=403)
        
        # Parse request data
        data = json.loads(request.body)
        target_class_codes = data.get('target_class_codes', [])
        exam_type = data.get('exam_type', source_exam.exam_type)
        time_period = data.get('time_period')
        academic_year = data.get('academic_year', source_exam.academic_year)
        
        # Validate target classes
        copyable_classes = ExamPermissionService.get_teacher_copyable_classes(request.user)
        if copyable_classes != 'ALL':
            # Check if all target classes are allowed
            invalid_classes = [code for code in target_class_codes if code not in copyable_classes]
            if invalid_classes:
                return JsonResponse({
                    'success': False,
                    'error': f'You do not have permission to copy to classes: {", ".join(invalid_classes)}'
                }, status=403)
        
        # Validate required fields
        if not target_class_codes:
            return JsonResponse({
                'success': False,
                'error': 'At least one target class must be selected'
            }, status=400)
        
        if not time_period:
            return JsonResponse({
                'success': False,
                'error': 'Time period is required'
            }, status=400)
        
        # Get teacher for copy attribution - CRITICAL: Copier becomes owner with FULL access
        created_by = None
        if hasattr(request.user, 'teacher_profile'):
            created_by = request.user.teacher_profile
            logger.info(f"[EXAM_COPY_OWNERSHIP] Teacher {created_by.name} will OWN the copied exam")
            print(f"[EXAM_COPY_OWNERSHIP] Setting {created_by.name} as OWNER of copied exam")
        else:
            logger.warning(f"[EXAM_COPY_OWNERSHIP] User {request.user.username} has no teacher profile")
        
        # Create the copy with new ownership
        new_exam = Exam.create_copy(
            source_exam=source_exam,
            target_class_codes=target_class_codes,
            exam_type=exam_type,
            time_period=time_period,
            academic_year=academic_year,
            created_by=created_by  # CRITICAL: This makes copier the owner
        )
        
        # Verify ownership was set
        if new_exam.created_by:
            logger.info(f"[EXAM_COPY_OWNERSHIP] SUCCESS: {new_exam.created_by.name} now OWNS exam {new_exam.id}")
            print(f"[EXAM_COPY_OWNERSHIP] ✅ {new_exam.created_by.name} has FULL ACCESS to copied exam")
        
        # Log the copy operation
        console_log = {
            "action": "exam_copied",
            "source_exam_id": str(source_exam.id),
            "source_exam_name": source_exam.name,
            "new_exam_id": str(new_exam.id),
            "new_exam_name": new_exam.name,
            "target_class_codes": target_class_codes,
            "exam_type": exam_type,
            "time_period": time_period,
            "academic_year": academic_year,
            "copied_by": str(request.user),
            "timestamp": timezone.now().isoformat()
        }
        logger.info(f"[EXAM_COPY_SUCCESS] {json.dumps(console_log)}")
        print(f"[EXAM_COPY_SUCCESS] {json.dumps(console_log)}")
        
        return JsonResponse({
            'success': True,
            'new_exam_id': str(new_exam.id),
            'new_exam_name': new_exam.name,
            'message': f'Exam copied successfully to {len(target_class_codes)} class(es)'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"[EXAM_COPY_ERROR] Error copying exam {exam_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)