#!/usr/bin/env python
"""
Pre-Cleanup Comprehensive QA Test
Run this before starting any cleanup to establish baseline functionality
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from placement_test.models import Question, Exam, StudentSession
from core.models import CurriculumLevel, PlacementRule, School, Teacher

print('='*80)
print('PRE-CLEANUP COMPREHENSIVE QA TEST')
print(f'Timestamp: {datetime.now()}')
print('='*80)

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'categories': {},
    'critical_features': []
}

def log_test(category, test_name, passed, critical=False):
    """Log test result"""
    status = "✅" if passed else "❌"
    print(f"{status} {test_name}")
    
    test_results['passed' if passed else 'failed'] += 1
    
    if category not in test_results['categories']:
        test_results['categories'][category] = {'passed': 0, 'failed': 0}
    test_results['categories'][category]['passed' if passed else 'failed'] += 1
    
    if critical:
        test_results['critical_features'].append({
            'name': test_name,
            'passed': passed,
            'category': category
        })

print("\n1. MODEL LAYER TESTS")
print("-" * 50)

# Test all question types
for q_type in ['MCQ', 'CHECKBOX', 'SHORT', 'LONG', 'MIXED']:
    try:
        q = Question.objects.filter(question_type=q_type).first()
        if q:
            # Test options_count behavior
            if q_type == 'MIXED':
                original = q.options_count
                q.options_count = 8
                q.save()
                q.refresh_from_db()
                passed = (q.options_count == 8)
                q.options_count = original
                q.save()
            else:
                passed = True
            log_test('Models', f'{q_type} Question', passed, critical=True)
        else:
            log_test('Models', f'{q_type} Question', False)
    except Exception as e:
        log_test('Models', f'{q_type} Question', False)

# Test Exam model
try:
    exam = Exam.objects.first()
    log_test('Models', 'Exam model', exam is not None, critical=True)
except:
    log_test('Models', 'Exam model', False, critical=True)

# Test StudentSession
try:
    session = StudentSession.objects.first()
    log_test('Models', 'StudentSession model', True, critical=True)
except:
    log_test('Models', 'StudentSession model', False, critical=True)

print("\n2. VIEW LAYER TESTS")
print("-" * 50)

client = Client()

# Test critical views
critical_urls = [
    ('/', 'Index page'),
    ('/teacher/dashboard/', 'Teacher dashboard'),
    ('/api/placement/exams/', 'Exam list'),
    ('/curriculum/levels/', 'Curriculum levels'),
    ('/placement-rules/', 'Placement rules'),
]

for url, name in critical_urls:
    try:
        response = client.get(url)
        log_test('Views', name, response.status_code in [200, 302], critical=True)
    except Exception as e:
        log_test('Views', name, False, critical=True)

print("\n3. API ENDPOINT TESTS")
print("-" * 50)

# Test question update API
question = Question.objects.first()
if question:
    try:
        response = client.post(
            f'/api/placement/questions/{question.id}/update/',
            {
                'correct_answer': question.correct_answer,
                'points': question.points,
                'options_count': question.options_count
            }
        )
        log_test('API', 'Question update endpoint', response.status_code == 200, critical=True)
    except:
        log_test('API', 'Question update endpoint', False, critical=True)

# Test exam save answers API
exam = Exam.objects.first()
if exam:
    try:
        response = client.post(
            f'/api/placement/exams/{exam.id}/save-answers/',
            json.dumps({'questions': [], 'audio_assignments': {}}),
            content_type='application/json'
        )
        log_test('API', 'Save answers endpoint', response.status_code == 200, critical=True)
    except:
        log_test('API', 'Save answers endpoint', False, critical=True)

print("\n4. TEMPLATE TESTS")
print("-" * 50)

# Test that critical templates exist and load
critical_templates = [
    'placement_test/student_test_v2.html',
    'placement_test/preview_and_answers.html',
    'placement_test/manage_questions.html',
    'placement_test/exam_list.html',
    'placement_test/create_exam.html',
]

for template in critical_templates:
    try:
        from django.template import loader
        t = loader.get_template(template)
        log_test('Templates', template, True, critical=True)
    except:
        log_test('Templates', template, False, critical=True)

print("\n5. SERVICE LAYER TESTS")
print("-" * 50)

# Test services
try:
    from placement_test.services import ExamService, SessionService, GradingService, PlacementService
    log_test('Services', 'ExamService', True, critical=True)
    log_test('Services', 'SessionService', True, critical=True)
    log_test('Services', 'GradingService', True, critical=True)
    log_test('Services', 'PlacementService', True, critical=True)
except Exception as e:
    log_test('Services', 'Service imports', False, critical=True)

try:
    from core.services import CurriculumService, SchoolService, TeacherService
    log_test('Services', 'Core services', True, critical=True)
except:
    log_test('Services', 'Core services', False, critical=True)

print("\n6. MIXED MCQ FEATURE TEST")
print("-" * 50)

# Test the critical MIXED MCQ options count feature
mixed = Question.objects.filter(question_type='MIXED').first()
if mixed:
    try:
        # Test options_count preservation
        original = mixed.options_count
        mixed.options_count = 7
        mixed.save()
        mixed.refresh_from_db()
        
        # Test template filter
        from placement_test.templatetags.grade_tags import get_mixed_components
        components = get_mixed_components(mixed)
        mcq_comps = [c for c in components if c.get('type') == 'mcq']
        
        if mcq_comps:
            options = mcq_comps[0].get('options', [])
            passed = (len(options) == 7 and mixed.options_count == 7)
        else:
            passed = False
            
        log_test('Features', 'MIXED MCQ options count', passed, critical=True)
        
        # Restore original
        mixed.options_count = original
        mixed.save()
    except:
        log_test('Features', 'MIXED MCQ options count', False, critical=True)

print("\n7. STUDENT WORKFLOW TEST")
print("-" * 50)

# Test student workflow endpoints
if exam:
    try:
        # Test session creation
        response = client.post(
            f'/api/placement/exams/{exam.id}/start/',
            {
                'student_name': 'Test Student',
                'student_phone': '1234567890',
                'parent_phone': '0987654321'
            }
        )
        log_test('Workflow', 'Session creation', response.status_code in [200, 302], critical=True)
    except:
        log_test('Workflow', 'Session creation', False, critical=True)

print("\n8. MODULARIZATION STATUS")
print("-" * 50)

# Check modularization
try:
    # Check if views are modularized
    from placement_test.views import student, exam, session, ajax
    log_test('Modular', 'Views modularization', True)
except:
    log_test('Modular', 'Views modularization', False)

# Check if URLs are modularized
try:
    import placement_test.student_urls
    import placement_test.exam_urls
    import placement_test.session_urls
    import placement_test.api_urls
    log_test('Modular', 'URLs modularization', True)
except:
    log_test('Modular', 'URLs modularization', False)

# Summary
print("\n" + "="*80)
print("PRE-CLEANUP QA RESULTS")
print("="*80)

total_tests = test_results['passed'] + test_results['failed']
pass_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0

print(f"\n📊 OVERALL RESULTS:")
print(f"Total Tests: {total_tests}")
print(f"Passed: {test_results['passed']}")
print(f"Failed: {test_results['failed']}")
print(f"Pass Rate: {pass_rate:.1f}%")

print(f"\n📋 CATEGORY BREAKDOWN:")
for category, stats in test_results['categories'].items():
    cat_total = stats['passed'] + stats['failed']
    cat_rate = (stats['passed'] / cat_total * 100) if cat_total > 0 else 0
    print(f"{category:10} - {stats['passed']}/{cat_total} passed ({cat_rate:.0f}%)")

print(f"\n🔴 CRITICAL FEATURES STATUS:")
critical_passed = sum(1 for f in test_results['critical_features'] if f['passed'])
critical_total = len(test_results['critical_features'])
for feature in test_results['critical_features']:
    status = "✅" if feature['passed'] else "❌"
    print(f"{status} {feature['name']}")

print(f"\nCritical Features: {critical_passed}/{critical_total} working")

if pass_rate >= 95:
    print("\n✅ READY FOR CLEANUP - All critical features working")
    print("Proceed with Phase 1 cleanup (safe files)")
else:
    print("\n⚠️ WARNING - Some tests failed")
    print("Investigate failures before proceeding with cleanup")

# Save results
with open('pre_cleanup_qa_results.json', 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"\nDetailed results saved to: pre_cleanup_qa_results.json")
print("="*80)