#!/usr/bin/env python
"""
Detailed analysis to find the specific exams that are bypassing the filter
"""
import os
import sys
import django

# Add the project path to sys.path
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.services.exam_service import ExamService, ExamPermissionService
from primepath_routinetest.models import Exam
import re
import logging

def detailed_filter_analysis():
    """Compare direct service call vs HTTP response to find discrepancy"""
    
    print("="*80)
    print("DETAILED FILTER ANALYSIS - FINDING THE LEAK")
    print("="*80)
    
    # Get teacher1 user
    user = User.objects.get(username='teacher1')
    print(f"✅ Analyzing user: {user.username}")
    print()
    
    # Direct service call test
    print("📊 DIRECT SERVICE CALL (Known Working)")
    print("-" * 50)
    
    base_query = Exam.objects.select_related(
        'curriculum_level__subprogram__program'
    ).prefetch_related('routine_questions', 'routine_audio_files')
    all_exams = base_query.all()
    
    # Filter OFF
    hierarchical_all = ExamService.organize_exams_hierarchically(
        all_exams, user, filter_assigned_only=False
    )
    
    # Filter ON  
    hierarchical_filtered = ExamService.organize_exams_hierarchically(
        all_exams, user, filter_assigned_only=True
    )
    
    # Collect exams from both results
    def extract_exams_from_hierarchical(hierarchical_data):
        exams = []
        for program, program_data in hierarchical_data.items():
            for class_code, class_exams in program_data.items():
                for exam in class_exams:
                    exams.append({
                        'id': str(exam.id),
                        'name': exam.name,
                        'badge': getattr(exam, 'access_badge', 'UNKNOWN'),
                        'class_codes': getattr(exam, 'class_codes', []),
                        'program': program,
                        'class_code': class_code
                    })
        return exams
    
    all_service_exams = extract_exams_from_hierarchical(hierarchical_all)
    filtered_service_exams = extract_exams_from_hierarchical(hierarchical_filtered)
    
    view_only_all_service = [e for e in all_service_exams if e['badge'] == 'VIEW ONLY']
    view_only_filtered_service = [e for e in filtered_service_exams if e['badge'] == 'VIEW ONLY']
    
    print(f"Service Call - Filter OFF: {len(all_service_exams)} exams ({len(view_only_all_service)} VIEW ONLY)")
    print(f"Service Call - Filter ON: {len(filtered_service_exams)} exams ({len(view_only_filtered_service)} VIEW ONLY)")
    print()
    
    if view_only_filtered_service:
        print("❌ VIEW ONLY exams that leaked through service call:")
        for exam in view_only_filtered_service:
            print(f"   - {exam['name']} (ID: {exam['id'][:8]}...)")
            print(f"     Classes: {exam['class_codes']}")
    else:
        print("✅ Service call correctly filtered all VIEW ONLY exams")
    print()
    
    # HTTP request test
    print("🌐 HTTP REQUEST TEST (Problematic)")
    print("-" * 50)
    
    client = Client()
    client.force_login(user)
    
    # Filter OFF
    response_all = client.get('/RoutineTest/exams/', follow=True)
    html_all = response_all.content.decode('utf-8')
    
    # Filter ON
    response_filtered = client.get('/RoutineTest/exams/?assigned_only=true', follow=True)
    html_filtered = response_filtered.content.decode('utf-8')
    
    # Extract exam info from HTML
    def extract_exams_from_html(html):
        # Pattern to match exam cards with their badges
        pattern = r'<div class="exam-card".*?<span class="exam-title"[^>]*>([^<]+)</span>.*?<span class="access-badge[^"]*"[^>]*>([^<]+)</span>'
        matches = re.findall(pattern, html, re.DOTALL)
        return [(name.strip(), badge.strip()) for name, badge in matches]
    
    all_http_exams = extract_exams_from_html(html_all)
    filtered_http_exams = extract_exams_from_html(html_filtered)
    
    view_only_all_http = [e for e in all_http_exams if e[1] == 'VIEW ONLY']
    view_only_filtered_http = [e for e in filtered_http_exams if e[1] == 'VIEW ONLY']
    
    print(f"HTTP Request - Filter OFF: {len(all_http_exams)} exams ({len(view_only_all_http)} VIEW ONLY)")
    print(f"HTTP Request - Filter ON: {len(filtered_http_exams)} exams ({len(view_only_filtered_http)} VIEW ONLY)")
    print()
    
    if view_only_filtered_http:
        print("❌ VIEW ONLY exams that leaked through HTTP request:")
        for name, badge in view_only_filtered_http:
            print(f"   - {name} ({badge})")
    else:
        print("✅ HTTP request correctly filtered all VIEW ONLY exams")
    print()
    
    # Compare the two approaches
    print("="*80)
    print("COMPARISON ANALYSIS")
    print("="*80)
    
    print(f"Service Call Results:")
    print(f"  - Filter OFF: {len(all_service_exams)} exams")
    print(f"  - Filter ON: {len(filtered_service_exams)} exams")
    print(f"  - VIEW ONLY when filtered: {len(view_only_filtered_service)}")
    print()
    
    print(f"HTTP Request Results:")
    print(f"  - Filter OFF: {len(all_http_exams)} exams")
    print(f"  - Filter ON: {len(filtered_http_exams)} exams")
    print(f"  - VIEW ONLY when filtered: {len(view_only_filtered_http)}")
    print()
    
    if len(view_only_filtered_service) != len(view_only_filtered_http):
        print("❌ DISCREPANCY DETECTED!")
        print(f"   Service call properly filters to {len(view_only_filtered_service)} VIEW ONLY")
        print(f"   HTTP request has {len(view_only_filtered_http)} VIEW ONLY")
        print()
        print("   This indicates the issue is NOT in ExamService.organize_exams_hierarchically()")
        print("   but rather in how the HTTP request processes the filter parameter.")
        print()
        
        # Check what assignments the teacher has
        assignments = ExamPermissionService.get_teacher_assignments(user)
        view_classes = [cls for cls, access in assignments.items() if access == 'VIEW']
        print(f"   Teacher has VIEW ONLY access to: {view_classes}")
        print()
        
        print("   Root cause likely one of:")
        print("   1. URL parameter processing in exam.py view")
        print("   2. Template context variable issues")
        print("   3. Multiple calls to organize_exams_hierarchically with different params")
        print("   4. Caching issues within the request")
        
    else:
        print("✅ Both approaches return same result")
        if len(view_only_filtered_http) > 0:
            print("   The problem is in the core filtering logic itself")
            print("   Need to debug ExamService.organize_exams_hierarchically()")
        else:
            print("   Both correctly filter - browser issue confirmed")
    
    # Check specific problematic exams
    if view_only_filtered_http:
        print()
        print("PROBLEMATIC EXAMS ANALYSIS:")
        print("-" * 40)
        
        for name, badge in view_only_filtered_http:
            print(f"\n🔍 Analyzing: {name}")
            
            # Find the exam in database
            try:
                exam = Exam.objects.filter(name=name).first()
                if exam:
                    print(f"   ID: {exam.id}")
                    print(f"   Class codes: {getattr(exam, 'class_codes', [])}")
                    print(f"   Created by: {exam.created_by.name if exam.created_by else 'Unknown'}")
                    
                    # Check teacher's access to this exam's classes
                    exam_classes = getattr(exam, 'class_codes', [])
                    if exam_classes:
                        for cls in exam_classes:
                            access = assignments.get(cls, 'NO ACCESS')
                            print(f"   Teacher access to {cls}: {access}")
                            if access == 'VIEW':
                                print(f"     ❌ This is VIEW ONLY - should be filtered out!")
                    else:
                        print(f"   ⚠️ Exam has no class codes")
                else:
                    print(f"   ❌ Could not find exam in database")
            except Exception as e:
                print(f"   ❌ Error analyzing exam: {e}")

if __name__ == '__main__':
    # Suppress some logging for cleaner output
    logging.getLogger('primepath_routinetest.services.exam_service').setLevel(logging.WARNING)
    detailed_filter_analysis()