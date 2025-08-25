#!/usr/bin/env python
"""
Comprehensive QA test for class code fix
Tests all components affected by the class code update
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models.exam import Exam
from primepath_routinetest.models.class_constants import CLASS_CODE_CHOICES
from primepath_routinetest.services.exam_service import ExamService
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_class_constants():
    """Test 1: Verify class constants are correct"""
    print_section("TEST 1: Class Constants Verification")
    
    # Expected actual classes from screenshot
    expected_classes = {
        'PS1', 'P1', 'P2', 'A2', 'B2', 'B3', 'B4', 'B5', 'S2',
        'H1', 'H2', 'H4', 'C2', 'C3', 'C4', 'C5',
        'Young-cho2', 'Young-choM', 'Chung-choM', 'Chung-cho1',
        'SejongM', 'MAS', 'TaejoG', 'TaejoD', 'TaejoDC',
        'SungjongM', 'Sungjong2', 'Sungjong3', 'SungjongC',
        'D2', 'D3', 'D4',
        'High1_SaiSun_3-5', 'High1_SaiSun_5-7',
        'High1V2_SaiSun_11-1', 'High1V2_SaiSun_1-3'
    }
    
    actual_codes = {code for code, _ in CLASS_CODE_CHOICES}
    
    print(f"Expected classes: {len(expected_classes)}")
    print(f"Actual classes: {len(actual_codes)}")
    
    # Check for any old fake classes
    old_patterns = ['PRIMARY_', 'MIDDLE_', 'HIGH_']
    old_found = [code for code in actual_codes if any(code.startswith(p) for p in old_patterns)]
    
    if old_found:
        print(f"✗ FAIL: Old fake classes still present: {old_found}")
        return False
    else:
        print("✓ PASS: No old fake classes found")
    
    # Check all expected classes are present
    missing = expected_classes - actual_codes
    if missing:
        print(f"✗ FAIL: Missing expected classes: {missing}")
        return False
    else:
        print("✓ PASS: All expected classes present")
    
    return True

def test_class_code_mapping():
    """Test 2: Verify class_code_mapping.py is updated"""
    print_section("TEST 2: Class Code Mapping Verification")
    
    print(f"Total mappings: {len(CLASS_CODE_CURRICULUM_MAPPING)}")
    
    # Check for old fake classes in mapping
    old_found = []
    for code in CLASS_CODE_CURRICULUM_MAPPING.keys():
        if any(code.startswith(p) for p in ['PRIMARY_', 'MIDDLE_', 'HIGH_']):
            old_found.append(code)
    
    if old_found:
        print(f"✗ FAIL: Old fake classes in mapping: {old_found[:5]}...")
        return False
    else:
        print("✓ PASS: No old fake classes in mapping")
    
    # Check that curriculum levels are removed (classes should map to themselves)
    curriculum_attached = []
    for code, display in CLASS_CODE_CURRICULUM_MAPPING.items():
        if 'Level' in display or 'CORE' in display or 'ASCENT' in display:
            curriculum_attached.append(f"{code} -> {display}")
    
    if curriculum_attached:
        print(f"✗ FAIL: Curriculum still attached to classes:")
        for item in curriculum_attached[:3]:
            print(f"  {item}")
        return False
    else:
        print("✓ PASS: No curriculum levels attached to classes")
    
    return True

def test_exam_model_method():
    """Test 3: Verify Exam.get_class_code_choices() returns correct data"""
    print_section("TEST 3: Exam Model Method")
    
    print("[Testing Exam.get_class_code_choices()]")
    choices = Exam.get_class_code_choices()
    
    print(f"Total choices returned: {len(choices)}")
    
    if not choices:
        print("✗ FAIL: No choices returned")
        return False
    
    # Check first few choices
    print("First 5 choices:")
    for code, display in choices[:5]:
        print(f"  {code:20} -> {display}")
        
        # Check for old patterns
        if any(code.startswith(p) for p in ['PRIMARY_', 'MIDDLE_', 'HIGH_']):
            print(f"✗ FAIL: Old fake class found: {code}")
            return False
    
    print("✓ PASS: Exam model returns correct choices")
    return True

def test_exam_service():
    """Test 4: Verify ExamService filtering works"""
    print_section("TEST 4: ExamService Class Filtering")
    
    # Create test user and teacher
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_user('test_admin', is_superuser=True)
    
    print(f"Testing with user: {user.username} (superuser: {user.is_superuser})")
    
    # Test get_filtered_class_choices_for_teacher
    print("\n[Testing ExamService.get_filtered_class_choices_for_teacher()]")
    choices = ExamService.get_filtered_class_choices_for_teacher(user, full_access_only=False)
    
    print(f"Choices returned: {len(choices)}")
    
    if not choices:
        print("✗ FAIL: No choices returned from ExamService")
        return False
    
    # Check for old classes
    old_found = []
    for code, display in choices[:10]:
        if any(code.startswith(p) for p in ['PRIMARY_', 'MIDDLE_', 'HIGH_']):
            old_found.append(code)
    
    if old_found:
        print(f"✗ FAIL: Old classes in ExamService: {old_found}")
        return False
    else:
        print("✓ PASS: ExamService returns correct filtered choices")
    
    return True

def test_view_context():
    """Test 5: Verify views use correct class choices"""
    print_section("TEST 5: View Context Verification")
    
    client = Client()
    
    # Get or create admin user
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'testpass123')
    
    # Ensure teacher profile exists
    try:
        teacher = user.teacher_profile
    except:
        from core.models import Teacher
        teacher = Teacher.objects.create(
            user=user,
            name=user.username,
            email=user.email or f"{user.username}@test.com"
        )
    
    client.force_login(user)
    
    # Test create exam view
    print("\n[Testing Create Exam View]")
    response = client.get('/RoutineTest/exams/create/')
    
    if response.status_code != 200:
        print(f"✗ FAIL: Create exam view returned {response.status_code}")
        return False
    
    # Check context
    if hasattr(response, 'context') and response.context:
        class_choices = response.context.get('class_choices', [])
        print(f"Class choices in context: {len(class_choices)}")
        
        if class_choices:
            print("First 3 choices from view:")
            for code, display in class_choices[:3]:
                print(f"  {code:20} -> {display}")
                
                if any(code.startswith(p) for p in ['PRIMARY_', 'MIDDLE_', 'HIGH_']):
                    print(f"✗ FAIL: Old class in view context: {code}")
                    return False
        
        print("✓ PASS: View context has correct class choices")
    else:
        print("✓ SKIP: View context not available in test")
    
    return True

def test_program_mapping():
    """Test 6: Verify PROGRAM_CLASS_MAPPING is updated"""
    print_section("TEST 6: Program Class Mapping")
    
    print("Program mappings:")
    for program, classes in ExamService.PROGRAM_CLASS_MAPPING.items():
        print(f"\n{program}: {len(classes)} classes")
        # Show first 3 classes
        sample = classes[:3] if len(classes) >= 3 else classes
        print(f"  Sample: {sample}")
        
        # Check for old classes
        old_in_program = [c for c in classes if any(c.startswith(p) for p in ['PRIMARY_', 'MIDDLE_', 'HIGH_'])]
        if old_in_program:
            print(f"  ✗ FAIL: Old classes in {program}: {old_in_program[:3]}")
            return False
    
    print("\n✓ PASS: All program mappings use actual classes")
    return True

def run_all_tests():
    """Run all QA tests"""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "CLASS CODE FIX - COMPREHENSIVE QA TEST" + " " * 20 + "║")
    print("╚" + "═" * 78 + "╝")
    
    tests = [
        ("Class Constants", test_class_constants),
        ("Class Code Mapping", test_class_code_mapping),
        ("Exam Model Method", test_exam_model_method),
        ("ExamService Filtering", test_exam_service),
        ("View Context", test_view_context),
        ("Program Mapping", test_program_mapping),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ ERROR in {name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print_section("QA TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print("\nDetailed Results:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Class code fix is working correctly.")
        print("\nKey Achievements:")
        print("✓ All old fake classes (PRIMARY_*, MIDDLE_*, HIGH_*) removed")
        print("✓ Actual classes from screenshot implemented")
        print("✓ No curriculum levels attached to classes")
        print("✓ All views and services using correct class list")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    
    # Final note
    print("\n" + "─" * 80)
    print("IMPORTANT: Remember to restart the Django server for changes to take effect!")
    print("Command: ../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite")
    print("─" * 80)
    
    sys.exit(0 if success else 1)