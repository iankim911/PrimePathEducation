#!/usr/bin/env python
"""
ULTRA-DEEP QA: Complete Codebase Analysis
Checks every component, relationship, and interaction
"""

import os
import sys
import django
import json
import importlib
from pathlib import Path
from datetime import datetime
import ast
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.apps import apps
from django.db import connection
from django.test import Client

print('='*80)
print('ULTRA-DEEP QA: COMPLETE CODEBASE ANALYSIS')
print(f'Timestamp: {datetime.now()}')
print('='*80)

# Comprehensive results tracking
qa_results = {
    'models': {'total': 0, 'issues': []},
    'views': {'total': 0, 'issues': []},
    'urls': {'total': 0, 'issues': []},
    'templates': {'total': 0, 'issues': []},
    'static': {'total': 0, 'issues': []},
    'relationships': {'total': 0, 'broken': []},
    'interactions': {'total': 0, 'broken': []},
    'critical_features': {},
    'test_results': {'passed': 0, 'failed': 0}
}

def section_header(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

# ============================================================================
# 1. DATABASE & MODEL ANALYSIS
# ============================================================================

def analyze_database_models():
    """Deep analysis of all models and their database structure"""
    section_header("1. DATABASE & MODEL ANALYSIS")
    
    print("\n📊 Model Structure:")
    
    # Get all models
    all_models = []
    for app_config in apps.get_app_configs():
        if not app_config.name.startswith('django.'):
            for model in app_config.get_models():
                all_models.append({
                    'app': app_config.label,
                    'name': model.__name__,
                    'model': model,
                    'db_table': model._meta.db_table
                })
    
    qa_results['models']['total'] = len(all_models)
    
    # Check each model
    for model_info in all_models:
        model = model_info['model']
        print(f"\n  {model_info['app']}.{model_info['name']}:")
        print(f"    Table: {model_info['db_table']}")
        
        # Check fields
        fields = model._meta.get_fields()
        field_types = {
            'regular': 0,
            'foreign_keys': 0,
            'many_to_many': 0,
            'reverse': 0
        }
        
        for field in fields:
            if field.many_to_many:
                field_types['many_to_many'] += 1
            elif field.many_to_one:
                field_types['foreign_keys'] += 1
            elif field.one_to_many or field.one_to_one:
                field_types['reverse'] += 1
            else:
                field_types['regular'] += 1
        
        print(f"    Fields: {len(fields)} total ({field_types['regular']} regular, "
              f"{field_types['foreign_keys']} FK, {field_types['many_to_many']} M2M)")
        
        # Check if table exists in database
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=%s",
                [model_info['db_table']])
            if not cursor.fetchone():
                print(f"    ⚠️ WARNING: Table {model_info['db_table']} not in database!")
                qa_results['models']['issues'].append(f"Missing table: {model_info['db_table']}")
    
    # Check critical models
    print("\n✅ Critical Model Checks:")
    
    critical_models = [
        ('placement_test', 'Question'),
        ('placement_test', 'Exam'),
        ('placement_test', 'StudentSession'),
        ('placement_test', 'DifficultyAdjustment'),
        ('core', 'CurriculumLevel'),
        ('core', 'PlacementRule')
    ]
    
    for app_label, model_name in critical_models:
        try:
            model = apps.get_model(app_label, model_name)
            count = model.objects.count()
            print(f"  ✅ {app_label}.{model_name}: {count} records")
        except Exception as e:
            print(f"  ❌ {app_label}.{model_name}: {str(e)}")
            qa_results['models']['issues'].append(f"Model error: {app_label}.{model_name}")

# ============================================================================
# 2. MODEL RELATIONSHIPS ANALYSIS
# ============================================================================

def analyze_model_relationships():
    """Analyze all foreign key relationships"""
    section_header("2. MODEL RELATIONSHIPS")
    
    from placement_test.models import Question, Exam, StudentSession, AudioFile, DifficultyAdjustment
    from core.models import CurriculumLevel, SubProgram, Program, PlacementRule, ExamLevelMapping
    
    relationships = []
    
    # Define all relationships to check
    relationship_checks = [
        (Question, 'exam', Exam, 'CASCADE'),
        (Question, 'audio_file', AudioFile, 'SET_NULL'),
        (StudentSession, 'exam', Exam, 'CASCADE'),
        (StudentSession, 'original_curriculum_level', CurriculumLevel, 'SET_NULL'),
        (StudentSession, 'final_curriculum_level', CurriculumLevel, 'SET_NULL'),
        (AudioFile, 'exam', Exam, 'CASCADE'),
        (DifficultyAdjustment, 'session', StudentSession, 'CASCADE'),
        (DifficultyAdjustment, 'from_level', CurriculumLevel, 'CASCADE'),
        (DifficultyAdjustment, 'to_level', CurriculumLevel, 'CASCADE'),
        (CurriculumLevel, 'subprogram', SubProgram, 'CASCADE'),
        (SubProgram, 'program', Program, 'CASCADE'),
        (PlacementRule, 'curriculum_level', CurriculumLevel, 'CASCADE'),
        (ExamLevelMapping, 'exam', Exam, 'CASCADE'),
        (ExamLevelMapping, 'curriculum_level', CurriculumLevel, 'CASCADE'),
    ]
    
    print("\n📊 Foreign Key Relationships:")
    
    for source_model, field_name, target_model, expected_on_delete in relationship_checks:
        try:
            field = source_model._meta.get_field(field_name)
            
            # Check properties
            actual_on_delete = str(field.remote_field.on_delete).split('.')[-1]
            is_nullable = field.null
            
            status = "✅" if actual_on_delete == expected_on_delete else "⚠️"
            
            print(f"\n  {status} {source_model.__name__}.{field_name} → {target_model.__name__}")
            print(f"     on_delete: {actual_on_delete} (expected: {expected_on_delete})")
            print(f"     nullable: {is_nullable}")
            
            relationships.append({
                'source': source_model.__name__,
                'field': field_name,
                'target': target_model.__name__,
                'on_delete': actual_on_delete,
                'nullable': is_nullable,
                'valid': actual_on_delete == expected_on_delete
            })
            
            if not actual_on_delete == expected_on_delete:
                qa_results['relationships']['broken'].append(
                    f"{source_model.__name__}.{field_name} has {actual_on_delete}, expected {expected_on_delete}"
                )
            
        except Exception as e:
            print(f"\n  ❌ {source_model.__name__}.{field_name}: {str(e)}")
            qa_results['relationships']['broken'].append(f"{source_model.__name__}.{field_name}: {str(e)}")
    
    qa_results['relationships']['total'] = len(relationships)

# ============================================================================
# 3. URL ROUTING ANALYSIS
# ============================================================================

def analyze_url_routing():
    """Analyze all URL patterns and their views"""
    section_header("3. URL ROUTING ANALYSIS")
    
    from django.urls import get_resolver
    
    resolver = get_resolver()
    
    def extract_urls(url_patterns, prefix=''):
        """Recursively extract all URL patterns"""
        patterns = []
        for pattern in url_patterns:
            if hasattr(pattern, 'url_patterns'):
                # This is an included URLconf
                patterns.extend(extract_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
            else:
                # This is a single pattern
                patterns.append({
                    'pattern': prefix + str(pattern.pattern),
                    'name': pattern.name,
                    'callback': pattern.callback if hasattr(pattern, 'callback') else None
                })
        return patterns
    
    all_patterns = extract_urls(resolver.url_patterns)
    qa_results['urls']['total'] = len(all_patterns)
    
    print(f"\n📊 Total URL patterns: {len(all_patterns)}")
    
    # Group by app
    app_urls = {}
    for pattern in all_patterns:
        if pattern['callback']:
            module = pattern['callback'].__module__ if hasattr(pattern['callback'], '__module__') else 'unknown'
            app = module.split('.')[0] if '.' in module else module
            
            if app not in app_urls:
                app_urls[app] = []
            app_urls[app].append(pattern)
    
    for app, patterns in app_urls.items():
        if app not in ['django', 'admin']:
            print(f"\n  {app}: {len(patterns)} patterns")
            # Show sample patterns
            for p in patterns[:3]:
                print(f"    - {str(p['pattern'])[:40]}")
    
    # Check critical URLs
    print("\n✅ Critical URL Checks:")
    critical_urls = [
        '/api/placement/exams/',
        '/api/placement/session/',
        '/teacher/dashboard/',
        '/placement-rules/',
        '/exam-mapping/',
    ]
    
    client = Client()
    for url in critical_urls:
        try:
            response = client.get(url)
            status = response.status_code
            print(f"  {'✅' if status in [200, 302] else '❌'} {url}: {status}")
            
            if status not in [200, 302]:
                qa_results['urls']['issues'].append(f"{url} returned {status}")
        except Exception as e:
            print(f"  ❌ {url}: {str(e)}")
            qa_results['urls']['issues'].append(f"{url}: {str(e)}")

# ============================================================================
# 4. VIEW LAYER ANALYSIS
# ============================================================================

def analyze_views():
    """Analyze all view functions and classes"""
    section_header("4. VIEW LAYER ANALYSIS")
    
    view_files = [
        'placement_test/views/__init__.py',
        'placement_test/views/student.py',
        'placement_test/views/teacher.py',
        'placement_test/views/api.py',
        'core/views.py',
    ]
    
    print("\n📊 View Files Analysis:")
    
    for view_file in view_files:
        file_path = Path(view_file)
        if file_path.exists():
            print(f"\n  {view_file}:")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
                
                functions = []
                classes = []
                decorators = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
                        # Check for decorators
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Name):
                                decorators.append(decorator.id)
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                
                print(f"    Functions: {len(functions)}")
                print(f"    Classes: {len(classes)}")
                print(f"    Common decorators: {set(decorators) if decorators else 'none'}")
                
                # Show sample functions
                for func in functions[:5]:
                    print(f"      - {func}()")
                    
            except SyntaxError as e:
                print(f"    ❌ Syntax error: {e}")
                qa_results['views']['issues'].append(f"Syntax error in {view_file}")
        else:
            print(f"  ❌ {view_file}: NOT FOUND")
            qa_results['views']['issues'].append(f"Missing view file: {view_file}")
    
    qa_results['views']['total'] = len(view_files)

# ============================================================================
# 5. TEMPLATE ANALYSIS
# ============================================================================

def analyze_templates():
    """Analyze all templates and their inheritance"""
    section_header("5. TEMPLATE ANALYSIS")
    
    template_dir = Path('templates')
    
    if not template_dir.exists():
        print("❌ Template directory not found!")
        return
    
    templates = list(template_dir.rglob('*.html'))
    qa_results['templates']['total'] = len(templates)
    
    print(f"\n📊 Total templates: {len(templates)}")
    
    # Analyze template structure
    template_info = {
        'base_templates': [],
        'extends': {},
        'includes': {},
        'ajax_calls': [],
        'forms': []
    }
    
    for template in templates:
        rel_path = str(template.relative_to(template_dir))
        content = template.read_text()
        
        # Check for extends
        extends_match = re.search(r'{%\s*extends\s+["\']([^"\']+)', content)
        if extends_match:
            template_info['extends'][rel_path] = extends_match.group(1)
        else:
            # No extends = base template
            if '{% block' in content:
                template_info['base_templates'].append(rel_path)
        
        # Check for includes
        includes = re.findall(r'{%\s*include\s+["\']([^"\']+)', content)
        if includes:
            template_info['includes'][rel_path] = includes
        
        # Check for AJAX calls
        ajax_calls = re.findall(r'fetch\([\'"]([^\'"]+)', content)
        if ajax_calls:
            template_info['ajax_calls'].extend([(rel_path, call) for call in ajax_calls])
        
        # Check for forms
        forms = re.findall(r'<form[^>]*action=[\'"]([^\'"]+)', content)
        if forms:
            template_info['forms'].extend([(rel_path, form) for form in forms])
    
    print(f"\n  Base templates: {len(template_info['base_templates'])}")
    for base in template_info['base_templates']:
        print(f"    - {base}")
    
    print(f"\n  Templates with AJAX: {len(set(t[0] for t in template_info['ajax_calls']))}")
    for template, endpoint in template_info['ajax_calls'][:5]:
        print(f"    - {template}: {endpoint}")
    
    print(f"\n  Templates with forms: {len(set(t[0] for t in template_info['forms']))}")
    for template, action in template_info['forms'][:5]:
        print(f"    - {template}: {action}")

# ============================================================================
# 6. STATIC FILES ANALYSIS
# ============================================================================

def analyze_static_files():
    """Analyze CSS and JavaScript files"""
    section_header("6. STATIC FILES ANALYSIS")
    
    static_dir = Path('static')
    
    if not static_dir.exists():
        print("❌ Static directory not found!")
        return
    
    css_files = list(static_dir.rglob('*.css'))
    js_files = list(static_dir.rglob('*.js'))
    
    qa_results['static']['total'] = len(css_files) + len(js_files)
    
    print(f"\n📊 Static files:")
    print(f"  CSS files: {len(css_files)}")
    print(f"  JavaScript files: {len(js_files)}")
    
    # Analyze JavaScript modules
    print("\n  JavaScript Modules:")
    js_modules = {}
    
    for js_file in js_files:
        rel_path = str(js_file.relative_to(static_dir))
        content = js_file.read_text()
        
        # Check for module pattern
        if 'PrimePath' in content:
            module_type = 'PrimePath module'
        elif 'class' in content:
            module_type = 'ES6 class'
        elif 'function' in content:
            module_type = 'Function-based'
        else:
            module_type = 'Script'
        
        js_modules[rel_path] = module_type
        
        if 'modules/' in rel_path:
            print(f"    - {rel_path}: {module_type}")
    
    # Check for critical JS files
    print("\n  Critical JS files:")
    critical_js = [
        'js/modules/answer-manager.js',
        'js/modules/navigation.js',
        'js/modules/timer.js',
        'js/modules/pdf-viewer.js',
        'js/modules/audio-player.js'
    ]
    
    for js in critical_js:
        full_path = static_dir / js
        if full_path.exists():
            size = full_path.stat().st_size / 1024
            print(f"    ✅ {js}: {size:.1f}KB")
        else:
            print(f"    ❌ {js}: NOT FOUND")
            qa_results['static']['issues'].append(f"Missing: {js}")

# ============================================================================
# 7. CRITICAL FEATURES CHECK
# ============================================================================

def check_critical_features():
    """Check all critical features are working"""
    section_header("7. CRITICAL FEATURES CHECK")
    
    from placement_test.models import Question, Exam, StudentSession
    
    print("\n🔍 Feature Verification:")
    
    features = {}
    
    # 1. MIXED MCQ
    print("\n  MIXED MCQ Options:")
    mixed = Question.objects.filter(question_type='MIXED').first()
    if mixed and hasattr(mixed, 'options_count'):
        # Test modification
        original = mixed.options_count
        mixed.options_count = 7
        mixed.save()
        mixed.refresh_from_db()
        success = mixed.options_count == 7
        mixed.options_count = original
        mixed.save()
        
        features['MIXED_MCQ'] = success
        print(f"    {'✅' if success else '❌'} Options count field working")
    else:
        features['MIXED_MCQ'] = False
        print("    ❌ MIXED questions not found or missing options_count")
    
    # 2. Difficulty Adjustment
    print("\n  Difficulty Adjustment:")
    try:
        from placement_test.models import DifficultyAdjustment
        features['DIFFICULTY_ADJUSTMENT'] = True
        count = DifficultyAdjustment.objects.count()
        print(f"    ✅ Model exists ({count} adjustments recorded)")
    except:
        features['DIFFICULTY_ADJUSTMENT'] = False
        print("    ❌ DifficultyAdjustment model not found")
    
    # 3. Audio Assignments
    print("\n  Audio Assignments:")
    audio_questions = Question.objects.filter(audio_file__isnull=False).count()
    features['AUDIO'] = audio_questions > 0
    print(f"    {'✅' if audio_questions else '⚠️'} {audio_questions} questions with audio")
    
    # 4. Session Tracking
    print("\n  Session Tracking:")
    session = StudentSession.objects.first()
    if session:
        has_fields = all([
            hasattr(session, 'original_curriculum_level'),
            hasattr(session, 'final_curriculum_level'),
            hasattr(session, 'difficulty_adjustments')
        ])
        features['SESSION_TRACKING'] = has_fields
        print(f"    {'✅' if has_fields else '❌'} All tracking fields present")
    else:
        features['SESSION_TRACKING'] = False
        print("    ⚠️ No sessions to check")
    
    # 5. All Question Types
    print("\n  Question Types:")
    types = ['MCQ', 'CHECKBOX', 'SHORT', 'LONG', 'MIXED']
    all_exist = True
    for q_type in types:
        exists = Question.objects.filter(question_type=q_type).exists()
        if not exists:
            all_exist = False
        print(f"    {'✅' if exists else '❌'} {q_type}")
    features['QUESTION_TYPES'] = all_exist
    
    qa_results['critical_features'] = features

# ============================================================================
# 8. INTEGRATION TESTS
# ============================================================================

def run_integration_tests():
    """Run actual integration tests"""
    section_header("8. INTEGRATION TESTS")
    
    client = Client()
    tests_passed = 0
    tests_failed = 0
    
    print("\n🧪 Running Integration Tests:")
    
    # Test 1: Complete student workflow
    print("\n  Test 1: Student Workflow")
    try:
        from placement_test.models import Exam, StudentSession
        
        exam = Exam.objects.filter(is_active=True).first()
        if exam:
            # Create session
            session = StudentSession.objects.create(
                student_name="Integration Test",
                grade=5,
                academic_rank="TOP_20",
                exam=exam,
                original_curriculum_level=exam.curriculum_level
            )
            
            # Submit answer
            from placement_test.models import StudentAnswer
            question = exam.questions.first()
            if question:
                answer = StudentAnswer.objects.create(
                    session=session,
                    question=question,
                    answer="Test"
                )
                
                # Complete session
                from django.utils import timezone
                session.completed_at = timezone.now()
                session.save()
                
                print("    ✅ Complete workflow successful")
                tests_passed += 1
                
                # Clean up
                session.delete()
            else:
                print("    ❌ No questions in exam")
                tests_failed += 1
        else:
            print("    ❌ No active exam found")
            tests_failed += 1
    except Exception as e:
        print(f"    ❌ Workflow failed: {str(e)}")
        tests_failed += 1
    
    # Test 2: API endpoints
    print("\n  Test 2: API Endpoints")
    endpoints = [
        ('/api/placement/exams/', 'Exam list'),
        ('/teacher/dashboard/', 'Dashboard'),
        ('/placement-rules/', 'Placement rules'),
    ]
    
    for url, name in endpoints:
        try:
            response = client.get(url)
            if response.status_code in [200, 302]:
                print(f"    ✅ {name}")
                tests_passed += 1
            else:
                print(f"    ❌ {name}: {response.status_code}")
                tests_failed += 1
        except Exception as e:
            print(f"    ❌ {name}: {str(e)}")
            tests_failed += 1
    
    qa_results['test_results']['passed'] = tests_passed
    qa_results['test_results']['failed'] = tests_failed

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all analyses"""
    
    # Run all analysis functions
    analyze_database_models()
    analyze_model_relationships()
    analyze_url_routing()
    analyze_views()
    analyze_templates()
    analyze_static_files()
    check_critical_features()
    run_integration_tests()
    
    # Final Summary
    section_header("FINAL QA SUMMARY")
    
    print("\n📊 OVERALL METRICS:")
    print(f"  Models: {qa_results['models']['total']}")
    print(f"  URLs: {qa_results['urls']['total']}")
    print(f"  Views: {qa_results['views']['total']}")
    print(f"  Templates: {qa_results['templates']['total']}")
    print(f"  Static Files: {qa_results['static']['total']}")
    
    print("\n⚠️ ISSUES FOUND:")
    total_issues = (
        len(qa_results['models']['issues']) +
        len(qa_results['relationships']['broken']) +
        len(qa_results['urls']['issues']) +
        len(qa_results['views']['issues']) +
        len(qa_results['static']['issues'])
    )
    
    if total_issues == 0:
        print("  ✅ No issues found!")
    else:
        print(f"  Total issues: {total_issues}")
        
        if qa_results['models']['issues']:
            print(f"\n  Model issues ({len(qa_results['models']['issues'])}):")
            for issue in qa_results['models']['issues'][:3]:
                print(f"    - {issue}")
        
        if qa_results['relationships']['broken']:
            print(f"\n  Relationship issues ({len(qa_results['relationships']['broken'])}):")
            for issue in qa_results['relationships']['broken'][:3]:
                print(f"    - {issue}")
    
    print("\n🔍 CRITICAL FEATURES:")
    all_features_ok = True
    for feature, status in qa_results['critical_features'].items():
        print(f"  {'✅' if status else '❌'} {feature}")
        if not status:
            all_features_ok = False
    
    print("\n🧪 TEST RESULTS:")
    print(f"  Passed: {qa_results['test_results']['passed']}")
    print(f"  Failed: {qa_results['test_results']['failed']}")
    
    # Final verdict
    print("\n" + "="*60)
    if all_features_ok and total_issues == 0:
        print("✅ SYSTEM FULLY OPERATIONAL - NO ISSUES DETECTED")
    elif all_features_ok:
        print("⚠️ SYSTEM OPERATIONAL - MINOR ISSUES DETECTED")
    else:
        print("❌ CRITICAL ISSUES DETECTED - REVIEW NEEDED")
    print("="*60)
    
    # Save results
    with open('ultra_deep_qa_results.json', 'w') as f:
        json.dump(qa_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: ultra_deep_qa_results.json")

if __name__ == '__main__':
    main()