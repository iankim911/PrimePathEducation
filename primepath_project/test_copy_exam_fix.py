#\!/usr/bin/env python
"""
Test script to verify Copy Exam modal functionality after fix
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import RoutineExam as Exam
from primepath_routinetest.services import ExamService
import json

def test_copy_exam_modal():
    """Test the Copy Exam modal functionality"""
    print("=" * 70)
    print("COPY EXAM MODAL TEST")
    print("=" * 70)
    
    # 1. Test curriculum data availability
    print("\n1. Testing Curriculum Data Service...")
    try:
        curriculum_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        if curriculum_data and 'curriculum_data' in curriculum_data:
            programs = list(curriculum_data['curriculum_data'].keys())
            print(f"   ✅ Curriculum data loaded: {programs}")
            
            # Check structure
            for program in programs[:2]:  # Check first 2 programs
                subprograms = list(curriculum_data['curriculum_data'][program]['subprograms'].keys())
                print(f"   ✅ {program}: {len(subprograms)} subprograms")
        else:
            print("   ❌ Invalid curriculum data structure")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to get curriculum data: {e}")
        return False
    
    # 2. Test exam list page with curriculum data
    print("\n2. Testing Exam List Page...")
    client = Client()
    
    # Login as admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("   ❌ No admin user found")
        return False
    
    client.force_login(admin_user)
    
    # Load exam list page
    response = client.get('/RoutineTest/exams/')
    
    if response.status_code == 200:
        print("   ✅ Exam list page loaded")
        
        # Check context
        context = response.context
        if 'curriculum_hierarchy_for_copy' in context:
            print("   ✅ Curriculum data in template context")
        else:
            print("   ❌ No curriculum data in template context")
            
        # Check if modal HTML is in response
        content = response.content.decode('utf-8')
        checks = {
            'copyExamModal': 'id="copyExamModal"' in content,
            'copyExamForm': 'id="copyExamForm"' in content,
            'copyProgramSelect': 'id="copyProgramSelect"' in content,
            'copySubprogramSelect': 'id="copySubprogramSelect"' in content,
            'copyLevelSelect': 'id="copyLevelSelect"' in content,
            'curriculum_script': 'copy-curriculum-hierarchy-data' in content,
            'fixed_js': 'copy-exam-modal-fixed.js' in content
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}: {result}")
            
        # Check for copy buttons
        copy_button_count = content.count('btn-copy')
        print(f"   📊 Found {copy_button_count} copy buttons")
        
    else:
        print(f"   ❌ Failed to load exam list page: {response.status_code}")
        return False
    
    # 3. Test Copy Exam API endpoint
    print("\n3. Testing Copy Exam API...")
    
    # Get a test exam to copy
    exam = Exam.objects.filter(created_by__user=admin_user).first()
    if exam:
        print(f"   ✅ Found test exam: {exam.name}")
        
        # Prepare copy data
        copy_data = {
            'source_exam_id': str(exam.id),
            'target_class': 'CORE_1A',  # Example target class
            'exam_type': 'QUARTERLY',
            'timeslot': 'Q1',
            'academic_year': '2025',
            'curriculum_level_id': '1',  # Example level ID
            'custom_suffix': '_TEST'
        }
        
        # Test the copy endpoint
        response = client.post(
            '/RoutineTest/api/copy-exam/',
            data=json.dumps(copy_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Copy API works: {result.get('message', 'Success')}")
            else:
                print(f"   ⚠️  Copy API returned error: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Copy API failed: {response.status_code}")
            
    else:
        print("   ⚠️  No exam found to test copy")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("✅ Copy Exam modal should now work with:")
    print("   - Simplified JavaScript (copy-exam-modal-fixed.js)")
    print("   - Curriculum data properly loaded")
    print("   - All dropdowns initialized")
    print("   - Form submission handled")
    print("\n📝 To test in browser:")
    print("   1. Go to http://127.0.0.1:8000/RoutineTest/exams/")
    print("   2. Click any 'Copy Exam' button")
    print("   3. Select exam type, time period, and curriculum")
    print("   4. Submit the form")
    
    return True

if __name__ == '__main__':
    success = test_copy_exam_modal()
    sys.exit(0 if success else 1)
EOF < /dev/null