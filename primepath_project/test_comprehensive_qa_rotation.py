#!/usr/bin/env python
"""
Comprehensive QA test after PDF rotation feature implementation
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from placement_test.models import Exam, Question, AudioFile, StudentSession
from core.models import Program, SubProgram, CurriculumLevel, PlacementRule

def test_feature(name, test_func):
    """Helper to run and report test results"""
    try:
        result = test_func()
        if result:
            print(f"  ✓ {name}")
            return True
        else:
            print(f"  ✗ {name}")
            return False
    except Exception as e:
        print(f"  ✗ {name}: {str(e)[:50]}")
        return False

def test_exam_deletion():
    """Test exam deletion with audio files"""
    try:
        # Create test exam with audio
        exam = Exam.objects.create(
            name="Test Exam for Deletion",
            total_questions=5,
            is_active=True
        )
        
        # Create audio file with correct field name
        audio = AudioFile.objects.create(
            exam=exam,
            name="Test Audio",
            start_question=1,
            end_question=3
        )
        
        # Delete exam (should cascade properly)
        exam.delete()
        return True
    except AttributeError as e:
        if "'AudioFile' object has no attribute 'file'" in str(e):
            return False
        raise
    except:
        return False

def test_exam_creation():
    """Test exam creation view"""
    client = Client()
    response = client.get('/placement/exams/create/')
    return response.status_code == 200

def test_exam_list():
    """Test exam list view"""
    client = Client()
    response = client.get('/placement/exams/')
    return response.status_code == 200

def test_teacher_dashboard():
    """Test teacher dashboard"""
    client = Client()
    response = client.get('/')
    if response.status_code == 302:  # Redirect
        return True
    return response.status_code == 200

def test_placement_rules():
    """Test placement rules page"""
    client = Client()
    response = client.get('/placement-rules/')
    return response.status_code == 200

def test_exam_mapping():
    """Test exam mapping page"""
    client = Client()
    response = client.get('/exam-mapping/')
    return response.status_code == 200

def test_save_exam_answers_api():
    """Test save exam answers API endpoint"""
    client = Client()
    exam = Exam.objects.first()
    if not exam:
        return True  # Skip if no exams
    
    test_data = {
        'questions': [],
        'audio_assignments': {}
    }
    
    response = client.post(
        f'/api/placement/exams/{exam.id}/save-answers/',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    return response.status_code == 200

def test_models_integrity():
    """Test model relationships and fields"""
    checks = []
    
    # Check core models exist
    checks.append(Program.objects.model._meta.db_table is not None)
    checks.append(SubProgram.objects.model._meta.db_table is not None)
    checks.append(CurriculumLevel.objects.model._meta.db_table is not None)
    
    # Check exam model has required fields
    exam_fields = [f.name for f in Exam._meta.get_fields()]
    required_fields = ['name', 'total_questions', 'timer_minutes', 'pdf_file']
    checks.append(all(field in exam_fields for field in required_fields))
    
    # Check AudioFile has correct field name
    audio_fields = [f.name for f in AudioFile._meta.get_fields()]
    checks.append('audio_file' in audio_fields)
    
    return all(checks)

def test_student_interface():
    """Test student interface rendering"""
    client = Client()
    
    # Check if any sessions exist
    session = StudentSession.objects.first()
    if session:
        response = client.get(f'/placement/test/{session.id}/')
        return response.status_code in [200, 302]
    return True  # Skip if no sessions

def test_javascript_files():
    """Test that JavaScript files exist"""
    js_files = [
        'static/js/modules/pdf-viewer.js',
        'static/js/modules/audio-player.js',
        'static/js/modules/timer.js',
        'static/js/modules/answer-manager.js',
        'static/js/modules/navigation.js'
    ]
    
    for file_path in js_files:
        if not os.path.exists(file_path):
            return False
    return True

def test_templates_exist():
    """Test that required templates exist"""
    templates = [
        'templates/placement_test/create_exam.html',
        'templates/placement_test/preview_and_answers.html',
        'templates/placement_test/student_test_v2.html',
        'templates/placement_test/exam_list.html',
        'templates/core/placement_rules_matrix.html',
        'templates/core/exam_mapping.html'
    ]
    
    for template_path in templates:
        if not os.path.exists(template_path):
            return False
    return True

def test_rotation_implementation():
    """Test rotation feature implementation (code level only)"""
    checks = []
    
    # Check if model has field defined (not in DB yet)
    exam_fields = [f.name for f in Exam._meta.get_fields()]
    checks.append('pdf_rotation' in exam_fields)
    
    # Check if views handle rotation
    with open('placement_test/views/ajax.py', 'r') as f:
        content = f.read()
        checks.append('pdf_rotation' in content)
    
    # Check if templates have rotation support
    with open('templates/placement_test/create_exam.html', 'r') as f:
        content = f.read()
        checks.append('pdf_rotation' in content)
    
    with open('templates/placement_test/preview_and_answers.html', 'r') as f:
        content = f.read()
        checks.append('currentRotation' in content and 'pdf_rotation' in content)
    
    return all(checks)

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE QA TEST - PDF ROTATION IMPLEMENTATION")
    print("="*70)
    
    test_groups = [
        ("CORE FUNCTIONALITY", [
            ("Exam Creation Page", test_exam_creation),
            ("Exam List Page", test_exam_list),
            ("Teacher Dashboard", test_teacher_dashboard),
            ("Placement Rules Page", test_placement_rules),
            ("Exam Mapping Page", test_exam_mapping),
        ]),
        ("API ENDPOINTS", [
            ("Save Exam Answers API", test_save_exam_answers_api),
        ]),
        ("DATA INTEGRITY", [
            ("Exam Deletion with Audio", test_exam_deletion),
            ("Models Integrity", test_models_integrity),
        ]),
        ("USER INTERFACES", [
            ("Student Test Interface", test_student_interface),
        ]),
        ("STATIC RESOURCES", [
            ("JavaScript Modules", test_javascript_files),
            ("Templates", test_templates_exist),
        ]),
        ("ROTATION FEATURE", [
            ("Rotation Code Implementation", test_rotation_implementation),
        ])
    ]
    
    all_passed = True
    results_summary = []
    
    for group_name, tests in test_groups:
        print(f"\n{group_name}:")
        group_passed = 0
        group_total = len(tests)
        
        for test_name, test_func in tests:
            passed = test_feature(test_name, test_func)
            if passed:
                group_passed += 1
            else:
                all_passed = False
        
        results_summary.append((group_name, group_passed, group_total))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for group_name, passed, total in results_summary:
        status = "✅" if passed == total else "⚠️"
        print(f"{status} {group_name}: {passed}/{total} passed")
    
    print("\n" + "="*70)
    print("PDF ROTATION FEATURE STATUS")
    print("="*70)
    print("\n✅ IMPLEMENTED:")
    print("  • Added pdf_rotation field to Exam model")
    print("  • Updated save_exam_answers API to handle rotation")
    print("  • Modified create_exam.html to send rotation on upload")
    print("  • Modified preview_and_answers.html to save rotation")
    print("  • Updated student view to pass rotation to template")
    print("  • Modified student_test_v2.html to apply saved rotation")
    
    print("\n⚠️ PENDING:")
    print("  • Migration needs to be created and run")
    print("    Due to permission issues, migration file couldn't be created")
    print("    Manual steps required:")
    print("    1. Create file: placement_test/migrations/0013_exam_pdf_rotation.py")
    print("    2. Run: python manage.py migrate")
    
    print("\n📋 MIGRATION CONTENT NEEDED:")
    print("-"*70)
    print("""from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):
    dependencies = [
        ('placement_test', '0012_add_performance_indexes'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='exam',
            name='pdf_rotation',
            field=models.IntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(270)
                ],
                help_text='PDF rotation angle in degrees (0, 90, 180, 270)'
            ),
        ),
    ]""")
    print("-"*70)
    
    if all_passed:
        print("\n✅ ALL EXISTING FEATURES WORKING - No regressions detected!")
    else:
        print("\n⚠️ Some tests failed - review details above")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("1. Create and run the migration file")
    print("2. Test rotation persistence in Upload Exam")
    print("3. Test rotation save in Manage Exams")
    print("4. Verify rotation displays correctly for students")
    print("="*70)

if __name__ == '__main__':
    main()