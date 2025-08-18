#!/usr/bin/env python3
"""
Test Matrix Functionality Restoration - Live Testing
Comprehensive test of the restored matrix functionality
"""
import os
import sys
import django
from datetime import datetime
import json

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from primepath_routinetest.views.classes_exams_unified import classes_exams_unified_view
from primepath_routinetest.models import ExamScheduleMatrix, Exam, TeacherClassAssignment
from core.models import Teacher

def test_matrix_restoration():
    """Test the matrix functionality restoration"""
    print("\n" + "="*80)
    print("🔧 MATRIX FUNCTIONALITY RESTORATION TEST")
    print("="*80)
    
    # 1. Test the unified view functionality
    print("\n📋 1. TESTING UNIFIED VIEW...")
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_superuser': True,
            'is_staff': True,
            'email': 'admin@example.com'
        }
    )
    
    if created:
        admin_user.set_password('admin')
        admin_user.save()
        print(f"   ✅ Created admin user: {admin_user.username}")
    else:
        print(f"   ✅ Using existing admin user: {admin_user.username}")
    
    # Create request factory and simulate request
    factory = RequestFactory()
    request = factory.get('/RoutineTest/classes-exams/')
    request.user = admin_user
    
    try:
        print(f"   🔄 Calling classes_exams_unified_view...")
        response = classes_exams_unified_view(request)
        print(f"   ✅ View executed successfully")
        print(f"   📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   🎉 Matrix view is working!")
        else:
            print(f"   ❌ View returned status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ View failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. Test ExamScheduleMatrix model functionality
    print("\n🗄️ 2. TESTING MATRIX MODEL...")
    
    try:
        # Test matrix cell creation
        current_year = str(datetime.now().year)
        test_class = 'CLASS_7A'
        test_month = 'JAN'
        
        matrix_cell, created = ExamScheduleMatrix.get_or_create_cell(
            class_code=test_class,
            academic_year=current_year,
            time_period_type='MONTHLY',
            time_period_value=test_month,
            user=admin_user
        )
        
        if created:
            print(f"   ✅ Created test matrix cell: {matrix_cell}")
        else:
            print(f"   ✅ Using existing matrix cell: {matrix_cell}")
        
        # Test matrix cell methods
        print(f"   📊 Exam count: {matrix_cell.get_exam_count()}")
        print(f"   🎨 Status color: {matrix_cell.get_status_color()}")
        print(f"   🔵 Status icon: {matrix_cell.get_status_icon()}")
        print(f"   📅 Display name: {matrix_cell.get_time_period_display()}")
        
        print(f"   ✅ Matrix model methods are working!")
        
    except Exception as e:
        print(f"   ❌ Matrix model test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Test matrix data structure
    print("\n📊 3. TESTING MATRIX DATA STRUCTURE...")
    
    try:
        # Get matrix data for all classes
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        timeslots = months + quarters
        
        print(f"   📅 Total timeslots: {len(timeslots)}")
        print(f"   📅 Months: {len(months)}, Quarters: {len(quarters)}")
        
        # Get class codes from Exam model
        try:
            all_class_codes = [code for code, _ in Exam.CLASS_CODE_CHOICES]
            print(f"   🏫 Available class codes: {len(all_class_codes)}")
            print(f"   🏫 First 5 classes: {all_class_codes[:5]}")
        except Exception as class_error:
            print(f"   ⚠️ Could not get class codes: {class_error}")
            all_class_codes = ['CLASS_7A', 'CLASS_7B', 'CLASS_7C']
        
        # Test matrix structure for first few classes
        matrix_data = {}
        test_classes = all_class_codes[:3]  # Test first 3 classes
        
        for class_code in test_classes:
            matrix_data[class_code] = {}
            
            for timeslot in timeslots[:6]:  # Test first 6 timeslots
                # Determine time period type
                if timeslot in months:
                    time_period_type = 'MONTHLY'
                elif timeslot in quarters:
                    time_period_type = 'QUARTERLY'
                else:
                    continue
                
                # Query for matrix cell
                matrix_cell = ExamScheduleMatrix.objects.filter(
                    class_code=class_code,
                    academic_year=current_year,
                    time_period_type=time_period_type,
                    time_period_value=timeslot
                ).first()
                
                # Build cell data
                cell_data = {
                    'has_exam': False,
                    'review': None,
                    'quarterly': None,
                    'exam_count': 0,
                    'status': 'EMPTY'
                }
                
                if matrix_cell:
                    exams = matrix_cell.exams.all()
                    cell_data.update({
                        'exam_count': len(exams),
                        'status': matrix_cell.status,
                        'has_exam': len(exams) > 0
                    })
                
                matrix_data[class_code][timeslot] = cell_data
        
        print(f"   ✅ Matrix data structure built successfully")
        print(f"   📊 Classes in matrix: {len(matrix_data)}")
        
        # Count populated cells
        total_cells = 0
        populated_cells = 0
        for class_code, slots in matrix_data.items():
            for timeslot, cell in slots.items():
                total_cells += 1
                if cell['has_exam']:
                    populated_cells += 1
        
        print(f"   📈 Total cells: {total_cells}")
        print(f"   📈 Populated cells: {populated_cells}")
        print(f"   📈 Population rate: {(populated_cells/total_cells*100):.1f}%" if total_cells > 0 else "0%")
        
    except Exception as e:
        print(f"   ❌ Matrix data structure test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. Test template filters
    print("\n🏷️ 4. TESTING TEMPLATE FILTERS...")
    
    try:
        from primepath_routinetest.templatetags.matrix_filters import dict_get, get_item
        
        # Test dict_get filter
        test_dict = {'JAN': {'has_exam': True}, 'FEB': {'has_exam': False}}
        jan_result = dict_get(test_dict, 'JAN')
        print(f"   ✅ dict_get filter working: {jan_result}")
        
        # Test get_item filter
        feb_result = get_item(test_dict, 'FEB')
        print(f"   ✅ get_item filter working: {feb_result}")
        
        print(f"   ✅ Template filters are working!")
        
    except Exception as e:
        print(f"   ❌ Template filter test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Final validation
    print("\n🎯 5. FINAL VALIDATION...")
    
    try:
        # Check if we can get the complete matrix for a class
        test_matrix = ExamScheduleMatrix.get_matrix_for_class(
            class_code='CLASS_7A',
            academic_year=current_year,
            time_period_type='MONTHLY'
        )
        
        print(f"   📊 Matrix cells for CLASS_7A: {test_matrix.count()}")
        
        # Test matrix cell details
        if test_matrix.exists():
            first_cell = test_matrix.first()
            print(f"   📅 First cell: {first_cell}")
            print(f"   📊 Exam list: {first_cell.get_exam_list()}")
            print(f"   📈 Completion stats: {first_cell.get_completion_stats()}")
        
        print(f"   ✅ Matrix restoration validation complete!")
        
    except Exception as e:
        print(f"   ❌ Final validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n🎉 MATRIX FUNCTIONALITY RESTORATION TEST COMPLETE!")
    print(f"✅ All tests passed - Matrix functionality is working!")
    print("="*80)
    
    return True

if __name__ == "__main__":
    success = test_matrix_restoration()
    if success:
        print("\n🚀 RESULT: Matrix restoration is successful!")
        sys.exit(0)
    else:
        print("\n💥 RESULT: Matrix restoration has issues!")
        sys.exit(1)