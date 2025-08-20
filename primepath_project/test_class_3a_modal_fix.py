#!/usr/bin/env python
"""
Test for CLASS_3A Modal Data Inconsistency Fix
Tests the fix for the issue where class cards show "Active Exams: 1" 
but modal shows "No exams assigned".
"""
import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import User

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.views.exam_api import get_class_exams, get_class_overview
from primepath_routinetest.models import ExamScheduleMatrix
from primepath_routinetest.models.exam_management import RoutineExam

def test_class_3a_modal_fix():
    """Test the fix for CLASS_3A modal data inconsistency"""
    print("\n" + "="*80)
    print("TESTING CLASS_3A MODAL DATA CONSISTENCY FIX")
    print("="*80)
    
    # Create test user and request
    factory = RequestFactory()
    user = User.objects.first()
    if not user:
        print("❌ No users found. Please create a user first.")
        return
    
    class_code = "CLASS_3A"
    
    print(f"\n1. Testing CLASS_3A exam data consistency...")
    print(f"   Class Code: {class_code}")
    
    # Test 1: Check what exams exist for CLASS_3A in the matrix
    print(f"\n2. Checking ExamScheduleMatrix for {class_code}...")
    matrix_entries = ExamScheduleMatrix.objects.filter(class_code=class_code)
    print(f"   Found {matrix_entries.count()} matrix entries for {class_code}")
    
    total_exams = 0
    timeslot_assignments = {}
    
    for entry in matrix_entries:
        exam_count = entry.exams.count()
        total_exams += exam_count
        timeslot_assignments[entry.time_period_value] = exam_count
        print(f"   - {entry.time_period_value}: {exam_count} exam(s)")
        
        # Show exam details
        for exam in entry.exams.all():
            print(f"     * {exam.name} (ID: {exam.id})")
    
    print(f"\n   📊 TOTAL EXAMS FOR {class_code}: {total_exams}")
    print(f"   📋 Timeslot Distribution: {timeslot_assignments}")
    
    # Test 2: Test the old behavior (before fix)
    print(f"\n3. Testing API behavior with different timeslot parameters...")
    
    # Test with 'overview' parameter (this was broken before fix)
    request_overview = factory.get(f'/api/class/{class_code}/exams/?timeslot=overview')
    request_overview.user = user
    
    print(f"\n   🔍 Testing with timeslot='overview' (FIXED BEHAVIOR):")
    response_overview = get_class_exams(request_overview, class_code)
    overview_data = response_overview.content.decode('utf-8')
    
    import json
    overview_json = json.loads(overview_data)
    overview_exam_count = len(overview_json.get('exams', []))
    
    print(f"      - Found {overview_exam_count} exams")
    print(f"      - Filter mode: {overview_json.get('filter_mode', 'unknown')}")
    
    # Test with specific timeslot
    if timeslot_assignments:
        specific_timeslot = list(timeslot_assignments.keys())[0]
        request_specific = factory.get(f'/api/class/{class_code}/exams/?timeslot={specific_timeslot}')
        request_specific.user = user
        
        print(f"\n   🔍 Testing with specific timeslot='{specific_timeslot}':")
        response_specific = get_class_exams(request_specific, class_code)
        specific_data = response_specific.content.decode('utf-8')
        specific_json = json.loads(specific_data)
        specific_exam_count = len(specific_json.get('exams', []))
        
        print(f"      - Found {specific_exam_count} exams")
        print(f"      - Filter mode: {specific_json.get('filter_mode', 'unknown')}")
    
    # Test 3: Verify the fix
    print(f"\n4. 🏥 FIX VERIFICATION:")
    print(f"   Expected: overview mode should show ALL {total_exams} exams")
    print(f"   Actual:   overview mode shows {overview_exam_count} exams")
    
    if overview_exam_count == total_exams and total_exams > 0:
        print(f"   ✅ FIX SUCCESS: Modal will now show {overview_exam_count} exam(s) for {class_code}")
        print(f"   ✅ Data consistency RESTORED between class cards and modal!")
    elif total_exams == 0:
        print(f"   ⚠️  NO EXAMS: {class_code} has no exams assigned (this explains the issue)")
        print(f"   💡 SOLUTION: Assign exams to {class_code} to test the fix")
    else:
        print(f"   ❌ FIX FAILED: Expected {total_exams}, got {overview_exam_count}")
        print(f"   🔧 Debug info:")
        print(f"      - Response: {overview_json}")
    
    # Test 4: Test overview API consistency
    print(f"\n5. Testing Overview API consistency...")
    request_overview_api = factory.get(f'/api/class/{class_code}/overview/?timeslot=overview')
    request_overview_api.user = user
    
    try:
        response_overview_api = get_class_overview(request_overview_api, class_code)
        overview_api_data = json.loads(response_overview_api.content.decode('utf-8'))
        overview_api_exam_count = len(overview_api_data.get('exams', []))
        
        print(f"   Overview API found {overview_api_exam_count} exams")
        
        if overview_api_exam_count == overview_exam_count:
            print(f"   ✅ Overview API consistency: PASS")
        else:
            print(f"   ⚠️  Overview API inconsistency: {overview_api_exam_count} vs {overview_exam_count}")
    except Exception as e:
        print(f"   ❌ Overview API error: {e}")
    
    print(f"\n6. 📋 SUMMARY:")
    print(f"   - {class_code} has {total_exams} total exam(s)")
    print(f"   - Overview mode shows {overview_exam_count} exam(s)")
    print(f"   - Fix status: {'✅ SUCCESS' if overview_exam_count == total_exams else '❌ NEEDS WORK'}")
    
    if total_exams > 0:
        print(f"\n7. 🎯 USER EXPERIENCE:")
        print(f"   - Class card shows: 'Active Exams: {total_exams}'")
        print(f"   - Modal will show: '{overview_exam_count} exam(s)' when opened")
        print(f"   - Consistency: {'✅ FIXED' if overview_exam_count == total_exams else '❌ BROKEN'}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_class_3a_modal_fix()