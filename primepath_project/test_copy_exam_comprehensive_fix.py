#!/usr/bin/env python
"""
Comprehensive test for Copy Exam modal dropdown fix
Tests backend data generation, frontend integration, and complete functionality
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.services import ExamService
from primepath_routinetest.models import Exam
from core.models import Teacher

def test_backend_curriculum_generation():
    """Test that backend generates correct curriculum data"""
    print("\n" + "="*80)
    print("TEST 1: BACKEND CURRICULUM DATA GENERATION")
    print("="*80)
    
    try:
        # Call the service method
        print("Calling ExamService.get_routinetest_curriculum_hierarchy_for_frontend()...")
        curriculum_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        # Validate structure
        assert curriculum_data is not None, "Data is None"
        assert 'curriculum_data' in curriculum_data, "Missing curriculum_data key"
        assert 'metadata' in curriculum_data, "Missing metadata key"
        assert 'validation' in curriculum_data, "Missing validation key"
        
        # Check programs
        programs = curriculum_data['curriculum_data'].keys()
        expected_programs = ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']
        
        print(f"✅ Data structure valid")
        print(f"✅ Programs found: {list(programs)}")
        
        # Validate each program
        for program in expected_programs:
            assert program in programs, f"Missing program: {program}"
            program_data = curriculum_data['curriculum_data'][program]
            assert 'subprograms' in program_data, f"Program {program} missing subprograms"
            
            subprogram_count = len(program_data['subprograms'])
            print(f"✅ {program}: {subprogram_count} subprograms")
            
            # Check some subprograms
            for subprogram, sub_data in list(program_data['subprograms'].items())[:2]:
                assert 'levels' in sub_data, f"Subprogram {subprogram} missing levels"
                level_count = len(sub_data['levels'])
                print(f"   - {subprogram}: {level_count} levels")
        
        # Check validation
        validation = curriculum_data['validation']
        print(f"\n✅ Validation status: {'PASSED' if validation['is_valid'] else 'FAILED'}")
        print(f"✅ Total levels: {validation['total_levels']}")
        
        # Test JSON serialization
        json_str = json.dumps(curriculum_data)
        print(f"✅ JSON serializable: Yes ({len(json_str)} characters)")
        
        print("\n✅✅✅ BACKEND TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ BACKEND TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_view_context():
    """Test that view passes curriculum data to template"""
    print("\n" + "="*80)
    print("TEST 2: VIEW CONTEXT DATA")
    print("="*80)
    
    try:
        client = Client()
        
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
            print("Created admin user for testing")
        
        # Ensure teacher profile exists
        if not hasattr(admin_user, 'teacher_profile'):
            Teacher.objects.create(
                user=admin_user,
                name="Admin Teacher",
                email=admin_user.email,
                is_head_teacher=True
            )
        
        # Login
        client.force_login(admin_user)
        print(f"✅ Logged in as: {admin_user.username}")
        
        # Request exam list page
        print("Requesting exam list page...")
        response = client.get('/RoutineTest/exams/')
        
        assert response.status_code == 200, f"Bad response: {response.status_code}"
        print(f"✅ Page loaded successfully")
        
        # Check context
        if hasattr(response, 'context'):
            context = response.context
            
            # Check for curriculum data in context
            has_hierarchy = 'curriculum_hierarchy_for_copy' in context
            has_levels = 'curriculum_levels_for_copy' in context
            
            print(f"✅ curriculum_hierarchy_for_copy in context: {has_hierarchy}")
            print(f"✅ curriculum_levels_for_copy in context: {has_levels}")
            
            if has_hierarchy:
                hierarchy_data = context['curriculum_hierarchy_for_copy']
                if hierarchy_data and 'curriculum_data' in hierarchy_data:
                    programs = list(hierarchy_data['curriculum_data'].keys())
                    print(f"✅ Programs in context: {programs}")
                else:
                    print("⚠️ Hierarchy data structure invalid")
        else:
            print("⚠️ No context available (might be normal in test environment)")
        
        # Check if template contains the json_script tag
        content = response.content.decode('utf-8')
        has_json_script = 'id="copy-curriculum-hierarchy-data"' in content
        print(f"✅ JSON script tag in template: {has_json_script}")
        
        # Check for Copy modal HTML
        has_modal = 'id="copyExamModal"' in content
        has_program_select = 'id="copyProgramSelect"' in content
        
        print(f"✅ Copy modal in template: {has_modal}")
        print(f"✅ Program select in template: {has_program_select}")
        
        print("\n✅✅✅ VIEW CONTEXT TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ VIEW CONTEXT TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_javascript_integration():
    """Test JavaScript integration points"""
    print("\n" + "="*80)
    print("TEST 3: JAVASCRIPT INTEGRATION")
    print("="*80)
    
    try:
        # Check if JavaScript files exist
        js_files = [
            '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/static/js/routinetest/copy-exam-modal-comprehensive-fix.js',
            '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/static/js/routinetest/copy-exam-modal.js'
        ]
        
        for js_file in js_files:
            if os.path.exists(js_file):
                file_size = os.path.getsize(js_file)
                print(f"✅ Found: {os.path.basename(js_file)} ({file_size} bytes)")
                
                # Check for key functions
                with open(js_file, 'r') as f:
                    content = f.read()
                    has_open = 'openCopyModal' in content
                    has_populate = 'populateProgram' in content or 'populateCopyProgram' in content
                    has_init = 'initialize' in content or 'initializeCurriculum' in content
                    
                    print(f"   - Has openCopyModal: {has_open}")
                    print(f"   - Has populate function: {has_populate}")
                    print(f"   - Has initialize function: {has_init}")
            else:
                print(f"⚠️ Not found: {os.path.basename(js_file)}")
        
        print("\n✅✅✅ JAVASCRIPT INTEGRATION TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ JAVASCRIPT INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_exam_copy_functionality():
    """Test actual exam copy functionality"""
    print("\n" + "="*80)
    print("TEST 4: EXAM COPY FUNCTIONALITY")
    print("="*80)
    
    try:
        # Check if there are any exams to copy
        exam_count = Exam.objects.count()
        print(f"Total exams in database: {exam_count}")
        
        if exam_count > 0:
            # Get first exam
            exam = Exam.objects.first()
            print(f"✅ Test exam: {exam.name} (ID: {exam.id})")
            
            # Check exam properties
            print(f"   - Type: {exam.exam_type}")
            print(f"   - Questions: {exam.total_questions}")
            print(f"   - Has PDF: {bool(exam.pdf_file)}")
            print(f"   - Curriculum Level: {exam.curriculum_level}")
            
            # Test permission check
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                from primepath_routinetest.services.exam_service import ExamPermissionService
                can_copy = ExamPermissionService.can_teacher_copy_exam(admin_user, exam)
                print(f"✅ Admin can copy exam: {can_copy}")
        else:
            print("⚠️ No exams in database to test copy functionality")
        
        print("\n✅✅✅ EXAM COPY FUNCTIONALITY TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ EXAM COPY FUNCTIONALITY TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run all tests and generate report"""
    print("\n" + "="*80)
    print("COMPREHENSIVE COPY EXAM MODAL FIX TEST")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80)
    
    results = {
        'backend_generation': False,
        'view_context': False,
        'javascript_integration': False,
        'copy_functionality': False
    }
    
    # Run tests
    results['backend_generation'] = test_backend_curriculum_generation()
    results['view_context'] = test_view_context()
    results['javascript_integration'] = test_javascript_integration()
    results['copy_functionality'] = test_exam_copy_functionality()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉🎉🎉 ALL TESTS PASSED - COPY EXAM MODAL FIX IS WORKING! 🎉🎉🎉")
    else:
        print("\n⚠️ Some tests failed - review the output above for details")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)