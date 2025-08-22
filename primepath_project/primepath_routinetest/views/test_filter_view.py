from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from primepath_routinetest.models import Exam
from primepath_routinetest.services.exam_service import ExamService
import logging

logger = logging.getLogger(__name__)

@login_required
def test_filter(request):
    """Simple test view to verify filter is working"""
    
    # Get filter parameter
    assigned_only_param = request.GET.get('assigned_only', 'false')
    show_assigned_only = assigned_only_param.lower() == 'true'
    
    logger.info(f"[TEST_FILTER] URL: {request.get_full_path()}")
    logger.info(f"[TEST_FILTER] assigned_only param: '{assigned_only_param}'")
    logger.info(f"[TEST_FILTER] show_assigned_only: {show_assigned_only}")
    
    # Get all exams
    exams = Exam.objects.all()
    
    # Apply filter
    hierarchical_exams = ExamService.organize_exams_hierarchically(
        exams, 
        request.user, 
        filter_assigned_only=show_assigned_only
    )
    
    # Count VIEW ONLY exams
    view_only_count = 0
    total_count = 0
    for program in hierarchical_exams.values():
        for exam_list in program.values():
            for exam in exam_list:
                total_count += 1
                if exam.access_badge == 'VIEW ONLY':
                    view_only_count += 1
    
    logger.info(f"[TEST_FILTER] Total exams: {total_count}")
    logger.info(f"[TEST_FILTER] VIEW ONLY exams: {view_only_count}")
    
    if show_assigned_only and view_only_count > 0:
        logger.error(f"[TEST_FILTER] ERROR: Filter is ON but {view_only_count} VIEW ONLY exams are showing!")
    elif show_assigned_only and view_only_count == 0:
        logger.info(f"[TEST_FILTER] SUCCESS: Filter is ON and no VIEW ONLY exams are showing")
    
    context = {
        'request': request,
        'show_assigned_only': show_assigned_only,
        'hierarchical_exams': hierarchical_exams,
        'view_only_count': view_only_count,
        'total_count': total_count,
    }
    
    return render(request, 'primepath_routinetest/test_filter.html', context)