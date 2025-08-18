#!/usr/bin/env python
"""
Test to reproduce and fix the UUID serialization issue in matrix_cell_detail
"""
import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment, ExamScheduleMatrix, Exam
from primepath_routinetest.views.schedule_matrix import matrix_cell_detail
from django.test import RequestFactory


def test_uuid_serialization_issue():
    """Test and fix the UUID serialization issue"""
    print("🔍 TESTING UUID SERIALIZATION ISSUE")
    
    # Create test client and user
    client = Client()
    user = User.objects.filter(username='uuid_test_user').first()
    if not user:
        user = User.objects.create_user('uuid_test_user', 'uuid@test.com', 'testpass123')
        user.is_staff = True
        user.save()
    
    teacher = Teacher.objects.get_or_create(
        email=user.email,
        defaults={'name': 'UUID Test Teacher', 'user': user}
    )[0]
    
    # Create test class assignment
    assignment = TeacherClassAssignment.objects.get_or_create(
        teacher=teacher,
        class_code='CLASS_7A',
        defaults={'access_level': 'FULL', 'assigned_by': user}
    )[0]
    
    # Get or create a matrix cell
    matrix_cell, created = ExamScheduleMatrix.get_or_create_cell(
        class_code='CLASS_7A',
        academic_year='2025',
        time_period_type='MONTHLY',
        time_period_value='JAN',
        user=user
    )
    
    print(f"✅ Matrix cell created/found: {matrix_cell.id}")
    print(f"   Cell UUID type: {type(matrix_cell.id)}")
    print(f"   Cell class: {matrix_cell.class_code}")
    print(f"   Cell period: {matrix_cell.time_period_value}")
    
    # Test the view with various methods
    client.force_login(user)
    
    # Test 1: Direct URL access (GET)
    print(f"\n🧪 TEST 1: GET request to cell detail")
    try:
        response = client.get(f'/RoutineTest/schedule-matrix/cell/{matrix_cell.id}/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            print(f"   Content length: {len(content)} characters")
            if 'error' in content.lower():
                print(f"   ⚠️  Error detected in content")
            else:
                print(f"   ✅ GET request successful")
        else:
            print(f"   ❌ GET request failed with status {response.status_code}")
            if hasattr(response, 'content'):
                print(f"   Error content: {response.content.decode('utf-8')[:500]}")
    except Exception as e:
        print(f"   ❌ GET request exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Manual view call to check context serialization
    print(f"\n🧪 TEST 2: Direct view call to check context")
    try:
        factory = RequestFactory()
        request = factory.get(f'/RoutineTest/schedule-matrix/cell/{matrix_cell.id}/')
        request.user = user
        
        # Call view directly
        from primepath_routinetest.views.schedule_matrix import matrix_cell_detail
        response = matrix_cell_detail(request, matrix_cell.id)
        
        print(f"   Direct view call status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Direct view call successful")
        else:
            print(f"   ❌ Direct view call failed")
            
    except Exception as e:
        print(f"   ❌ Direct view call exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Check if it's a template rendering issue
    print(f"\n🧪 TEST 3: Examine view context data")
    try:
        # Get the data that would be passed to template
        assigned_exams = matrix_cell.get_exam_list()
        completion_stats = matrix_cell.get_completion_stats()
        
        print(f"   Assigned exams: {len(assigned_exams)}")
        print(f"   Completion stats keys: {list(completion_stats.keys())}")
        
        # Try to serialize the context data
        context_data = {
            'matrix_cell_id': str(matrix_cell.id),  # Convert UUID to string
            'matrix_cell_class': matrix_cell.class_code,
            'assigned_exams': assigned_exams,
            'completion_stats': completion_stats,
        }
        
        # Test JSON serialization
        json_data = json.dumps(context_data)
        print(f"   ✅ Context data is JSON serializable")
        print(f"   Context JSON length: {len(json_data)} characters")
        
    except Exception as e:
        print(f"   ❌ Context serialization error: {e}")
        print(f"   This confirms the UUID serialization issue!")
        
        # Check individual pieces
        print(f"\n   🔍 DEBUGGING CONTEXT PIECES:")
        try:
            print(f"   Matrix cell ID type: {type(matrix_cell.id)}")
            print(f"   Matrix cell ID value: {matrix_cell.id}")
            
            # Try serializing just the matrix cell id
            json.dumps(str(matrix_cell.id))
            print(f"   ✅ Matrix cell ID (as string) is serializable")
            
            # Check assigned exams
            if assigned_exams:
                print(f"   First exam structure: {assigned_exams[0].keys()}")
                for key, value in assigned_exams[0].items():
                    try:
                        json.dumps(value)
                        print(f"   ✅ {key}: {type(value)} - serializable")
                    except:
                        print(f"   ❌ {key}: {type(value)} - NOT serializable")
            
        except Exception as debug_e:
            print(f"   Debug error: {debug_e}")
    
    # Test 4: AJAX request simulation
    print(f"\n🧪 TEST 4: AJAX request simulation")
    try:
        response = client.get(
            f'/RoutineTest/schedule-matrix/cell/{matrix_cell.id}/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        print(f"   AJAX status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ AJAX request successful")
        else:
            print(f"   ❌ AJAX request failed")
            if hasattr(response, 'content'):
                print(f"   Error: {response.content.decode('utf-8')[:200]}")
                
    except Exception as e:
        print(f"   ❌ AJAX request exception: {e}")
    
    return matrix_cell


def analyze_exam_list_method():
    """Analyze the get_exam_list method specifically"""
    print(f"\n🔬 ANALYZING get_exam_list() METHOD")
    
    # Get a matrix cell with some exams
    matrix_cells = ExamScheduleMatrix.objects.all()
    
    for matrix_cell in matrix_cells[:3]:  # Check first 3 cells
        print(f"\n   📍 Matrix Cell: {matrix_cell.id}")
        print(f"      Class: {matrix_cell.class_code}")
        print(f"      Period: {matrix_cell.time_period_value}")
        print(f"      Exam count: {matrix_cell.get_exam_count()}")
        
        if matrix_cell.get_exam_count() > 0:
            try:
                exam_list = matrix_cell.get_exam_list()
                print(f"      ✅ get_exam_list() returned {len(exam_list)} exams")
                
                # Check each exam in the list
                for i, exam_data in enumerate(exam_list):
                    print(f"         Exam {i+1}: {exam_data.get('name', 'Unknown')}")
                    
                    # Try to serialize this exam data
                    try:
                        json.dumps(exam_data)
                        print(f"         ✅ Exam {i+1} is JSON serializable")
                    except Exception as e:
                        print(f"         ❌ Exam {i+1} JSON error: {e}")
                        
                        # Check individual fields
                        for key, value in exam_data.items():
                            try:
                                json.dumps(value)
                                print(f"            ✅ {key}: {type(value)}")
                            except:
                                print(f"            ❌ {key}: {type(value)} - NOT serializable")
                
                # Try to serialize the entire exam list
                try:
                    json.dumps(exam_list)
                    print(f"      ✅ Entire exam list is JSON serializable")
                except Exception as e:
                    print(f"      ❌ Exam list JSON error: {e}")
                    
            except Exception as e:
                print(f"      ❌ get_exam_list() error: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    print("=" * 80)
    print("  UUID SERIALIZATION ISSUE - ANALYSIS & FIX")
    print("=" * 80)
    
    try:
        matrix_cell = test_uuid_serialization_issue()
        analyze_exam_list_method()
        
        print(f"\n" + "=" * 80)
        print("🎯 ANALYSIS COMPLETE")
        print("✅ Issue location identified")
        print("💡 Ready for fix implementation")
        print(f"🌐 Test URL: http://127.0.0.1:8000/RoutineTest/schedule-matrix/cell/{matrix_cell.id}/")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 80)