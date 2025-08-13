#!/usr/bin/env python
"""
Test critical features after cleanup to ensure nothing broke
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from placement_test.models import Exam, StudentSession
from core.models import Program, SubProgram, CurriculumLevel, ExamLevelMapping
import json

print("=" * 100)
print("CRITICAL FEATURES TEST AFTER CLEANUP")
print(f"Timestamp: {datetime.now()}")
print("=" * 100)

# Create test client
client = Client()
user = User.objects.filter(is_superuser=True).first()
if user:
    client.force_login(user)

test_results = {
    'passed': [],
    'failed': []
}

# Test 1: Dashboard Access
print("\n1. TESTING DASHBOARD ACCESS")
print("-" * 50)
try:
    response = client.get('/dashboard/')
    if response.status_code == 200:
        print("✅ Dashboard loads successfully")
        test_results['passed'].append("Dashboard access")
    else:
        print(f"❌ Dashboard failed: Status {response.status_code}")
        test_results['failed'].append(f"Dashboard: Status {response.status_code}")
except Exception as e:
    print(f"❌ Dashboard error: {e}")
    test_results['failed'].append(f"Dashboard: {e}")

# Test 2: Upload Exam Page
print("\n2. TESTING UPLOAD EXAM PAGE")
print("-" * 50)
try:
    response = client.get('/upload-exam/')
    if response.status_code == 200:
        print("✅ Upload Exam page loads")
        test_results['passed'].append("Upload Exam page")
    else:
        print(f"❌ Upload Exam failed: Status {response.status_code}")
        test_results['failed'].append(f"Upload Exam: Status {response.status_code}")
except Exception as e:
    print(f"❌ Upload Exam error: {e}")
    test_results['failed'].append(f"Upload Exam: {e}")

# Test 3: Manage Exams Page
print("\n3. TESTING MANAGE EXAMS PAGE")
print("-" * 50)
try:
    response = client.get('/manage-exams/')
    if response.status_code == 200:
        print("✅ Manage Exams page loads")
        test_results['passed'].append("Manage Exams page")
    else:
        print(f"❌ Manage Exams failed: Status {response.status_code}")
        test_results['failed'].append(f"Manage Exams: Status {response.status_code}")
except Exception as e:
    print(f"❌ Manage Exams error: {e}")
    test_results['failed'].append(f"Manage Exams: {e}")

# Test 4: Exam-to-Level Mapping (CRITICAL - recently modified)
print("\n4. TESTING EXAM-TO-LEVEL MAPPING")
print("-" * 50)
try:
    response = client.get('/exam-mapping/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check no debug box
        if 'DEBUG: Server-side Data Count' not in content:
            print("✅ Debug box removed")
            test_results['passed'].append("Debug box removal")
        else:
            print("❌ Debug box still present")
            test_results['failed'].append("Debug box still present")
        
        # Check no INACTIVE subprograms
        if '[INACTIVE]' not in content:
            print("✅ No INACTIVE subprograms in HTML")
            test_results['passed'].append("INACTIVE filtering")
        else:
            print("❌ INACTIVE subprograms found in HTML")
            test_results['failed'].append("INACTIVE subprograms in HTML")
        
        # Check no debug console logs
        if 'EXAM_MAPPING_DEBUG' not in content:
            print("✅ Debug console logs removed")
            test_results['passed'].append("Debug logs removal")
        else:
            print("❌ Debug console logs still present")
            test_results['failed'].append("Debug logs still present")
            
        print("✅ Exam-to-Level Mapping loads")
        test_results['passed'].append("Exam-to-Level Mapping page")
    else:
        print(f"❌ Exam Mapping failed: Status {response.status_code}")
        test_results['failed'].append(f"Exam Mapping: Status {response.status_code}")
except Exception as e:
    print(f"❌ Exam Mapping error: {e}")
    test_results['failed'].append(f"Exam Mapping: {e}")

# Test 5: Placement Rules Page
print("\n5. TESTING PLACEMENT RULES PAGE")
print("-" * 50)
try:
    response = client.get('/placement-rules/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check no test subprograms
        if '[INACTIVE]' not in content:
            print("✅ No INACTIVE subprograms in Placement Rules")
            test_results['passed'].append("Placement Rules filtering")
        else:
            print("❌ INACTIVE subprograms in Placement Rules")
            test_results['failed'].append("INACTIVE in Placement Rules")
            
        print("✅ Placement Rules page loads")
        test_results['passed'].append("Placement Rules page")
    else:
        print(f"❌ Placement Rules failed: Status {response.status_code}")
        test_results['failed'].append(f"Placement Rules: Status {response.status_code}")
except Exception as e:
    print(f"❌ Placement Rules error: {e}")
    test_results['failed'].append(f"Placement Rules: {e}")

# Test 6: Student Sessions Page
print("\n6. TESTING STUDENT SESSIONS PAGE")
print("-" * 50)
try:
    response = client.get('/student-sessions/')
    if response.status_code == 200:
        print("✅ Student Sessions page loads")
        test_results['passed'].append("Student Sessions page")
    else:
        print(f"❌ Student Sessions failed: Status {response.status_code}")
        test_results['failed'].append(f"Student Sessions: Status {response.status_code}")
except Exception as e:
    print(f"❌ Student Sessions error: {e}")
    test_results['failed'].append(f"Student Sessions: {e}")

# Test 7: API Endpoints
print("\n7. TESTING API ENDPOINTS")
print("-" * 50)
try:
    # Test save exam mappings endpoint
    test_data = {
        'mappings': []
    }
    response = client.post('/api/save-exam-mappings/',
                           data=json.dumps(test_data),
                           content_type='application/json')
    if response.status_code == 200:
        print("✅ Save exam mappings API works")
        test_results['passed'].append("Save exam mappings API")
    else:
        print(f"❌ Save exam mappings API: Status {response.status_code}")
        test_results['failed'].append(f"Save mappings API: {response.status_code}")
except Exception as e:
    print(f"❌ API error: {e}")
    test_results['failed'].append(f"API: {e}")

# Test 8: Check View Filtering Logic
print("\n8. TESTING VIEW FILTERING LOGIC")
print("-" * 50)
from core.curriculum_constants import is_test_subprogram, is_valid_subprogram

# Test the filtering functions
test_subprograms = [
    '[INACTIVE] Test SubProgram',
    'CORE PHONICS',
    'Test SubProgram',
    'ASCENT NOVA'
]

all_correct = True
for name in test_subprograms:
    is_test = is_test_subprogram(name)
    expected = 'INACTIVE' in name or 'Test' in name
    if is_test == expected:
        print(f"✅ Correctly identified: {name} -> {'TEST' if is_test else 'VALID'}")
    else:
        print(f"❌ Incorrectly identified: {name}")
        all_correct = False

if all_correct:
    test_results['passed'].append("Filtering logic")
else:
    test_results['failed'].append("Filtering logic")

# Test 9: Database State
print("\n9. TESTING DATABASE STATE")
print("-" * 50)
inactive_count = SubProgram.objects.filter(name__startswith='[INACTIVE]').count()
print(f"INACTIVE subprograms in database: {inactive_count}")
if inactive_count == 7:  # Expected 7 test subprograms
    print("✅ Database state correct")
    test_results['passed'].append("Database state")
else:
    print(f"⚠️ Expected 7 INACTIVE, found {inactive_count}")
    test_results['failed'].append(f"Database: {inactive_count} INACTIVE")

# Test 10: Check for Redundancies
print("\n10. CHECKING FOR REDUNDANCIES")
print("-" * 50)

# Check if multiple continue statements exist (sign of redundant fixes)
from core import views
import inspect
source = inspect.getsource(views.exam_mapping)
continue_count = source.count('continue')
print(f"Continue statements in exam_mapping view: {continue_count}")
if continue_count <= 6:  # Reasonable number
    print("✅ No excessive redundancy detected")
    test_results['passed'].append("No redundancy")
else:
    print(f"⚠️ Possible redundancy: {continue_count} continue statements")
    test_results['failed'].append(f"Redundancy: {continue_count} continues")

print("\n" + "=" * 100)
print("TEST SUMMARY")
print("=" * 100)
print(f"✅ PASSED: {len(test_results['passed'])} tests")
for test in test_results['passed']:
    print(f"   - {test}")

if test_results['failed']:
    print(f"\n❌ FAILED: {len(test_results['failed'])} tests")
    for test in test_results['failed']:
        print(f"   - {test}")
else:
    print("\n🎉 ALL TESTS PASSED!")

print("\n" + "=" * 100)
print("MODULARITY CHECK")
print("=" * 100)

# Check if service layer is intact
try:
    from core.services import CurriculumService
    print("✅ Service layer intact")
except ImportError:
    print("❌ Service layer broken")

# Check if mixins are intact
try:
    from common.mixins import AjaxResponseMixin
    print("✅ Mixins intact")
except ImportError:
    print("❌ Mixins broken")

# Check if base views are intact
try:
    from common.views.base import BaseAPIView
    print("✅ Base views intact")
except ImportError:
    print("❌ Base views broken")

print("=" * 100)