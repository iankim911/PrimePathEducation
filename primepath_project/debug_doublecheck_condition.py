#!/usr/bin/env python
"""
Debug the double-check filtering condition in the web view
to see why it's not triggering
"""
import os
import sys
import django

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def debug_double_check():
    """Debug the double-check filtering condition"""
    
    print("🔍 DEBUG: DOUBLE-CHECK FILTERING CONDITION")
    print("=" * 50)
    
    # Setup client
    client = Client()
    user = User.objects.get(username='teacher1')
    user.set_password('teacher123')
    user.save()
    client.login(username='teacher1', password='teacher123')
    
    print("🧪 Making web request with debug logging...")
    
    # Temporarily patch the exam view to add debug logging
    from primepath_routinetest.views import exam
    
    # Get original view function
    original_exam_list = exam.exam_list
    
    def debug_exam_list(request):
        """Wrapper with debug logging"""
        print(f"\n🔍 DEBUG_WRAPPER: Starting exam_list view")
        
        # Call original view but add debug info
        # We'll examine the key variables
        ownership_filter = request.GET.get('ownership', 'my')
        assigned_only_param = request.GET.get('assigned_only', 'false')
        legacy_show_assigned_only = assigned_only_param.lower() == 'true'
        
        # Apply ownership logic 
        if ownership_filter == 'my':
            show_assigned_only = True
        elif ownership_filter == 'others':
            show_assigned_only = False  
        else:
            show_assigned_only = legacy_show_assigned_only
            
        is_admin = request.user.is_superuser or request.user.is_staff
        
        print(f"🔍 DEBUG_WRAPPER: ownership_filter = '{ownership_filter}'")
        print(f"🔍 DEBUG_WRAPPER: show_assigned_only = {show_assigned_only}")
        print(f"🔍 DEBUG_WRAPPER: is_admin = {is_admin}")
        print(f"🔍 DEBUG_WRAPPER: not is_admin = {not is_admin}")
        print(f"🔍 DEBUG_WRAPPER: Double-check condition (show_assigned_only and not is_admin) = {show_assigned_only and not is_admin}")
        
        if show_assigned_only and not is_admin:
            print(f"✅ DEBUG_WRAPPER: Double-check condition WILL be met")
        else:
            print(f"❌ DEBUG_WRAPPER: Double-check condition will NOT be met")
        
        # Call original function
        return original_exam_list(request)
    
    # Temporarily replace the view
    exam.exam_list = debug_exam_list
    
    try:
        # Make request
        response = client.get('/RoutineTest/exams/?ownership=my&exam_type=ALL')
        
        print(f"\n📊 Response status: {response.status_code}")
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            view_only_count = content.count('VIEW ONLY')
            print(f"📊 VIEW ONLY badges in response: {view_only_count}")
        
    finally:
        # Restore original view
        exam.exam_list = original_exam_list
    
    print("\n🎯 ANALYSIS:")
    print("If the double-check condition shows as 'WILL be met' but we don't see")
    print("[FILTER_DOUBLE_CHECK] logs in the actual view, there might be")
    print("a different code path or the view logic has changed.")

if __name__ == "__main__":
    debug_double_check()