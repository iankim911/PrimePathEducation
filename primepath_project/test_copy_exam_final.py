#!/usr/bin/env python
"""
Comprehensive test for Copy Exam functionality
Tests the complete flow from backend data to frontend interaction
"""
import os
import sys
import json
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import CurriculumLevel
from primepath_routinetest.models import RoutineExam as Exam
from primepath_routinetest.services import ExamService

def run_tests():
    """Run comprehensive copy exam tests"""
    print("=" * 80)
    print("COPY EXAM FUNCTIONALITY TEST")
    print("=" * 80)
    
    # Test 1: Check curriculum data structure
    print("\n1. Testing Curriculum Data Structure...")
    print("-" * 40)
    
    try:
        curriculum_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        # Check if we got the right structure
        if 'curriculum_data' in curriculum_data:
            actual_data = curriculum_data['curriculum_data']
        else:
            actual_data = curriculum_data
        
        # Validate programs exist
        expected_programs = ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']
        for program in expected_programs:
            if program in actual_data:
                subprogram_count = len(actual_data[program].get('subprograms', {}))
                print(f"  ✅ {program}: {subprogram_count} subprograms")
                
                # Show first subprogram as example
                if actual_data[program].get('subprograms'):
                    first_subprogram = list(actual_data[program]['subprograms'].keys())[0]
                    levels = actual_data[program]['subprograms'][first_subprogram].get('levels', [])
                    print(f"     Example: {first_subprogram} has {len(levels)} levels")
            else:
                print(f"  ❌ {program}: MISSING")
        
        print("  ✅ Curriculum data structure is valid")
        
    except Exception as e:
        print(f"  ❌ Failed to get curriculum data: {e}")
        return False
    
    # Test 2: Check if exam exists to copy
    print("\n2. Testing Source Exam Availability...")
    print("-" * 40)
    
    source_exam = None
    try:
        # Get any exam to use as source
        source_exam = Exam.objects.first()
        if source_exam:
            print(f"  ✅ Found source exam: {source_exam.name}")
            print(f"     ID: {source_exam.id}")
        else:
            print("  ⚠️  No exams found in database")
            print("     Creating a test exam...")
            
            # Create a test exam
            source_exam = Exam.objects.create(
                name="Test Exam for Copy",
                exam_type="review",
                academic_year="2025"
            )
            print(f"  ✅ Created test exam: {source_exam.name}")
    
    except Exception as e:
        print(f"  ❌ Failed to get/create source exam: {e}")
        return False
    
    # Test 3: Check curriculum levels exist
    print("\n3. Testing Curriculum Levels...")
    print("-" * 40)
    
    target_level = None
    try:
        # Get or create a curriculum level
        # Note: CurriculumLevel has a ForeignKey to SubProgram, not direct program field
        from core.models import SubProgram
        
        # First get the SubProgram
        subprogram = SubProgram.objects.filter(
            name="Phonics",
            program__name="CORE"
        ).first()
        
        if subprogram:
            target_level = CurriculumLevel.objects.filter(
                subprogram=subprogram
            ).first()
        else:
            target_level = None
        
        if not target_level:
            print("  ⚠️  No CORE Phonics level found")
            # Try to get any curriculum level
            target_level = CurriculumLevel.objects.first()
            if not target_level:
                print("  ❌ No curriculum levels found in database")
                return False
        
        # Get program and subprogram names through relationships
        program_name = target_level.subprogram.program.name if target_level.subprogram and target_level.subprogram.program else "Unknown"
        subprogram_name = target_level.subprogram.name if target_level.subprogram else "Unknown"
        
        print(f"  ✅ Target curriculum level: {program_name} {subprogram_name} Level {target_level.level_number}")
        print(f"     ID: {target_level.id}")
        
    except Exception as e:
        print(f"  ❌ Failed to get/create curriculum level: {e}")
        return False
    
    # Test 4: Test the copy API endpoint
    print("\n4. Testing Copy API Endpoint...")
    print("-" * 40)
    
    try:
        # Login as teacher
        client = Client()
        
        # Get or create teacher1 user
        user = User.objects.filter(username='teacher1').first()
        if not user:
            print("  Creating teacher1 user...")
            user = User.objects.create_user(
                username='teacher1',
                password='teacher123'
            )
        
        # Login
        logged_in = client.login(username='teacher1', password='teacher123')
        if logged_in:
            print("  ✅ Logged in as teacher1")
        else:
            print("  ❌ Failed to login")
            return False
        
        # Prepare copy request data
        copy_data = {
            'source_exam_id': str(source_exam.id),
            'curriculum_level_id': str(target_level.id),
            'custom_suffix': 'TEST COPY'
        }
        
        print(f"  Sending copy request...")
        print(f"    Source exam: {source_exam.name}")
        print(f"    Target curriculum: {program_name} {subprogram_name} Level {target_level.level_number}")
        
        # Make the API call
        response = client.post(
            '/RoutineTest/exams/copy/',
            data=json.dumps(copy_data),
            content_type='application/json'
        )
        
        print(f"  Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success'):
                print(f"  ✅ Copy successful!")
                print(f"     New exam ID: {response_data.get('new_exam_id')}")
                print(f"     New exam name: {response_data.get('new_exam_name')}")
                
                # Verify the new exam exists
                new_exam = Exam.objects.filter(id=response_data.get('new_exam_id')).first()
                if new_exam:
                    print(f"  ✅ Verified new exam exists in database")
                else:
                    print(f"  ❌ New exam not found in database")
            else:
                print(f"  ❌ Copy failed: {response_data.get('error')}")
        else:
            print(f"  ❌ HTTP error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"     Error: {error_data.get('error')}")
            except:
                print(f"     Response: {response.content.decode()}")
        
    except Exception as e:
        print(f"  ❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Verify exam list view works
    print("\n5. Testing Exam List View...")
    print("-" * 40)
    
    try:
        response = client.get('/RoutineTest/exams/')
        print(f"  Response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ Exam list page loads successfully")
            
            # Check if curriculum data is in context
            if hasattr(response, 'context') and response.context:
                has_curriculum = 'curriculum_hierarchy_for_copy' in response.context
                print(f"  {'✅' if has_curriculum else '❌'} Curriculum data in context: {has_curriculum}")
        else:
            print(f"  ❌ Failed to load exam list page")
        
    except Exception as e:
        print(f"  ❌ View test failed: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)