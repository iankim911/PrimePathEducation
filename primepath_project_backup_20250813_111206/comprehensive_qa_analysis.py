#!/usr/bin/env python
"""
ULTRA-DEEP COMPREHENSIVE QA ANALYSIS
Analyzes entire codebase structure, relationships, and interactions
"""

import os
import sys
import django
import json
from pathlib import Path
from datetime import datetime
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.apps import apps
from django.urls import get_resolver
from django.db import models as django_models

print('='*80)
print('ULTRA-DEEP COMPREHENSIVE QA ANALYSIS')
print(f'Timestamp: {datetime.now()}')
print('='*80)

# Analysis results
analysis = {
    'apps': {},
    'models': {},
    'views': {},
    'urls': {},
    'templates': {},
    'static': {},
    'relationships': {},
    'settings': {},
    'issues': [],
    'warnings': []
}

def analyze_project_structure():
    """Map complete project structure"""
    print("\n1. PROJECT STRUCTURE ANALYSIS")
    print("-" * 50)
    
    base_dir = Path('.')
    
    # Core directories
    dirs = {
        'apps': ['core', 'placement_test', 'api', 'common'],
        'config': ['primepath_project'],
        'templates': ['templates'],
        'static': ['static'],
        'media': ['media']
    }
    
    structure = {}
    for category, paths in dirs.items():
        structure[category] = {}
        for path in paths:
            dir_path = base_dir / path
            if dir_path.exists():
                # Count files by type
                py_files = list(dir_path.rglob('*.py'))
                html_files = list(dir_path.rglob('*.html'))
                css_files = list(dir_path.rglob('*.css'))
                js_files = list(dir_path.rglob('*.js'))
                
                structure[category][path] = {
                    'exists': True,
                    'py_files': len(py_files),
                    'html_files': len(html_files),
                    'css_files': len(css_files),
                    'js_files': len(js_files),
                    'total_files': len(list(dir_path.rglob('*')))
                }
                
                print(f"✅ {path}: {len(py_files)} .py, {len(html_files)} .html, "
                      f"{len(css_files)} .css, {len(js_files)} .js")
            else:
                structure[category][path] = {'exists': False}
                print(f"❌ {path}: NOT FOUND")
    
    return structure

def analyze_django_apps():
    """Analyze all Django apps and their components"""
    print("\n2. DJANGO APPS ANALYSIS")
    print("-" * 50)
    
    app_configs = apps.get_app_configs()
    
    for app_config in app_configs:
        app_name = app_config.name
        
        # Skip Django internal apps
        if app_name.startswith('django.'):
            continue
        
        print(f"\n📦 {app_name}")
        
        # Get models
        models = list(app_config.get_models())
        print(f"  Models: {len(models)}")
        
        # Analyze each model
        model_info = {}
        for model in models:
            model_name = model.__name__
            fields = model._meta.get_fields()
            
            # Categorize fields
            field_types = {
                'regular': [],
                'foreign_keys': [],
                'many_to_many': [],
                'one_to_one': [],
                'reverse_relations': []
            }
            
            for field in fields:
                if field.many_to_many:
                    field_types['many_to_many'].append(field.name)
                elif field.one_to_one:
                    field_types['one_to_one'].append(field.name)
                elif field.many_to_one:
                    field_types['foreign_keys'].append(field.name)
                elif field.one_to_many:
                    field_types['reverse_relations'].append(field.name)
                else:
                    field_types['regular'].append(field.name)
            
            model_info[model_name] = {
                'field_count': len(fields),
                'fields': field_types,
                'db_table': model._meta.db_table
            }
            
            print(f"    - {model_name}: {len(fields)} fields, "
                  f"{len(field_types['foreign_keys'])} FKs")
        
        analysis['apps'][app_name] = {
            'models': model_info,
            'model_count': len(models)
        }
    
    return analysis['apps']

def analyze_url_patterns():
    """Analyze all URL patterns and routing"""
    print("\n3. URL PATTERNS ANALYSIS")
    print("-" * 50)
    
    from django.urls import URLPattern, URLResolver
    
    def extract_patterns(resolver, prefix=''):
        patterns = []
        for pattern in resolver.url_patterns:
            if isinstance(pattern, URLPattern):
                patterns.append({
                    'pattern': prefix + str(pattern.pattern),
                    'name': pattern.name,
                    'callback': pattern.callback.__name__ if hasattr(pattern.callback, '__name__') else str(pattern.callback)
                })
            elif isinstance(pattern, URLResolver):
                # Recursive for included URLs
                sub_prefix = prefix + str(pattern.pattern)
                patterns.extend(extract_patterns(pattern, sub_prefix))
        return patterns
    
    resolver = get_resolver()
    all_patterns = extract_patterns(resolver)
    
    # Group by app
    app_patterns = {}
    for pattern in all_patterns:
        # Try to determine app from callback
        callback_str = pattern['callback']
        if '.' in callback_str:
            app_name = callback_str.split('.')[0]
        else:
            app_name = 'root'
        
        if app_name not in app_patterns:
            app_patterns[app_name] = []
        app_patterns[app_name].append(pattern)
    
    for app, patterns in app_patterns.items():
        print(f"\n  {app}: {len(patterns)} patterns")
        # Show first 3 patterns as examples
        for p in patterns[:3]:
            print(f"    - {p['pattern'][:50]} → {p['callback']}")
    
    analysis['urls'] = app_patterns
    return app_patterns

def analyze_model_relationships():
    """Deep analysis of model relationships"""
    print("\n4. MODEL RELATIONSHIPS ANALYSIS")
    print("-" * 50)
    
    from placement_test.models import Question, Exam, StudentSession, AudioFile, DifficultyAdjustment
    from core.models import CurriculumLevel, Program, SubProgram, PlacementRule
    
    relationships = {}
    
    # Critical relationships to check
    critical_relations = [
        ('Question', 'exam', 'Exam'),
        ('Question', 'audio_file', 'AudioFile'),
        ('StudentSession', 'exam', 'Exam'),
        ('StudentSession', 'original_curriculum_level', 'CurriculumLevel'),
        ('StudentSession', 'final_curriculum_level', 'CurriculumLevel'),
        ('AudioFile', 'exam', 'Exam'),
        ('DifficultyAdjustment', 'session', 'StudentSession'),
        ('DifficultyAdjustment', 'from_level', 'CurriculumLevel'),
        ('DifficultyAdjustment', 'to_level', 'CurriculumLevel'),
        ('CurriculumLevel', 'subprogram', 'SubProgram'),
        ('SubProgram', 'program', 'Program'),
        ('PlacementRule', 'curriculum_level', 'CurriculumLevel'),
    ]
    
    for model_name, field_name, related_model in critical_relations:
        try:
            # Get actual model classes
            model = apps.get_model('placement_test', model_name) if model_name in ['Question', 'Exam', 'StudentSession', 'AudioFile', 'DifficultyAdjustment'] else apps.get_model('core', model_name)
            
            field = model._meta.get_field(field_name)
            
            rel_info = {
                'type': 'ForeignKey' if field.many_to_one else 'OneToOne' if field.one_to_one else 'ManyToMany',
                'null': field.null if hasattr(field, 'null') else False,
                'on_delete': str(field.remote_field.on_delete) if hasattr(field, 'remote_field') else None
            }
            
            key = f"{model_name}.{field_name} → {related_model}"
            relationships[key] = rel_info
            
            print(f"✅ {key}: {rel_info['type']}, null={rel_info['null']}")
            
        except Exception as e:
            print(f"❌ {model_name}.{field_name}: {str(e)}")
            analysis['issues'].append(f"Relationship issue: {model_name}.{field_name}")
    
    analysis['relationships'] = relationships
    return relationships

def analyze_views_and_dependencies():
    """Analyze views and their dependencies"""
    print("\n5. VIEWS AND DEPENDENCIES ANALYSIS")
    print("-" * 50)
    
    # Import view modules
    view_modules = []
    
    try:
        from placement_test import views as pt_views
        view_modules.append(('placement_test', pt_views))
    except:
        print("❌ Could not import placement_test views")
    
    try:
        from core import views as core_views
        view_modules.append(('core', core_views))
    except:
        print("❌ Could not import core views")
    
    for module_name, module in view_modules:
        print(f"\n📄 {module_name} views:")
        
        # Get all functions/classes in module
        items = dir(module)
        views = [item for item in items if not item.startswith('_')]
        
        view_info = {}
        for view_name in views[:10]:  # Analyze first 10
            try:
                view = getattr(module, view_name)
                if callable(view):
                    # Check if it's a view function or class
                    is_class = isinstance(view, type)
                    
                    # Try to get decorators
                    decorators = []
                    if hasattr(view, '__wrapped__'):
                        decorators.append('decorated')
                    
                    view_info[view_name] = {
                        'type': 'class' if is_class else 'function',
                        'decorators': decorators
                    }
                    
                    print(f"    - {view_name}: {'class' if is_class else 'function'}")
            except:
                pass
        
        analysis['views'][module_name] = view_info
    
    return analysis['views']

def analyze_templates():
    """Analyze template structure and inheritance"""
    print("\n6. TEMPLATE ANALYSIS")
    print("-" * 50)
    
    template_dir = Path('templates')
    
    if template_dir.exists():
        # Find all HTML templates
        templates = list(template_dir.rglob('*.html'))
        
        # Group by directory
        template_groups = {}
        for template in templates:
            rel_path = template.relative_to(template_dir)
            group = rel_path.parts[0] if len(rel_path.parts) > 1 else 'root'
            
            if group not in template_groups:
                template_groups[group] = []
            template_groups[group].append(str(rel_path))
        
        for group, files in template_groups.items():
            print(f"\n  {group}: {len(files)} templates")
            for f in files[:3]:  # Show first 3
                print(f"    - {f}")
        
        # Check for template inheritance
        base_templates = []
        for template in templates:
            content = template.read_text()
            if '{% block' in content and not '{% extends' in content:
                base_templates.append(str(template.relative_to(template_dir)))
        
        print(f"\n  Base templates: {len(base_templates)}")
        for base in base_templates:
            print(f"    - {base}")
        
        analysis['templates'] = {
            'total': len(templates),
            'groups': template_groups,
            'base_templates': base_templates
        }
    
    return analysis['templates']

def analyze_static_files():
    """Analyze static files (CSS, JS)"""
    print("\n7. STATIC FILES ANALYSIS")
    print("-" * 50)
    
    static_dir = Path('static')
    
    if static_dir.exists():
        # CSS files
        css_files = list(static_dir.rglob('*.css'))
        print(f"\n  CSS files: {len(css_files)}")
        for css in css_files[:5]:
            size = css.stat().st_size / 1024  # KB
            print(f"    - {css.relative_to(static_dir)}: {size:.1f}KB")
        
        # JS files
        js_files = list(static_dir.rglob('*.js'))
        print(f"\n  JavaScript files: {len(js_files)}")
        for js in js_files[:5]:
            size = js.stat().st_size / 1024
            print(f"    - {js.relative_to(static_dir)}: {size:.1f}KB")
        
        analysis['static'] = {
            'css_count': len(css_files),
            'js_count': len(js_files),
            'css_files': [str(f.relative_to(static_dir)) for f in css_files],
            'js_files': [str(f.relative_to(static_dir)) for f in js_files]
        }
    
    return analysis['static']

def check_critical_features():
    """Check that all critical features are intact"""
    print("\n8. CRITICAL FEATURES CHECK")
    print("-" * 50)
    
    from placement_test.models import Question, Exam
    
    critical_checks = []
    
    # 1. MIXED MCQ options
    mixed = Question.objects.filter(question_type='MIXED').first()
    if mixed:
        if hasattr(mixed, 'options_count'):
            critical_checks.append(('MIXED MCQ options_count field', True))
            print("✅ MIXED MCQ options_count field exists")
        else:
            critical_checks.append(('MIXED MCQ options_count field', False))
            print("❌ MIXED MCQ options_count field missing!")
    
    # 2. Exam default_options_count
    exam = Exam.objects.first()
    if exam:
        if hasattr(exam, 'default_options_count'):
            critical_checks.append(('Exam default_options_count', True))
            print("✅ Exam default_options_count exists")
        else:
            critical_checks.append(('Exam default_options_count', False))
            print("❌ Exam default_options_count missing!")
    
    # 3. DifficultyAdjustment model
    try:
        from placement_test.models import DifficultyAdjustment
        critical_checks.append(('DifficultyAdjustment model', True))
        print("✅ DifficultyAdjustment model exists")
    except:
        critical_checks.append(('DifficultyAdjustment model', False))
        print("❌ DifficultyAdjustment model missing!")
    
    # 4. Audio assignments
    q_with_audio = Question.objects.filter(audio_file__isnull=False).exists()
    critical_checks.append(('Audio file assignments', q_with_audio))
    print(f"{'✅' if q_with_audio else '⚠️'} Audio file assignments: {'working' if q_with_audio else 'no assignments found'}")
    
    # 5. Session tracking
    from placement_test.models import StudentSession
    session = StudentSession.objects.first()
    if session:
        has_tracking = (
            hasattr(session, 'original_curriculum_level') and
            hasattr(session, 'final_curriculum_level') and
            hasattr(session, 'difficulty_adjustments')
        )
        critical_checks.append(('Session difficulty tracking', has_tracking))
        print(f"{'✅' if has_tracking else '❌'} Session difficulty tracking fields")
    
    return critical_checks

def analyze_settings():
    """Analyze Django settings"""
    print("\n9. SETTINGS ANALYSIS")
    print("-" * 50)
    
    from django.conf import settings
    
    critical_settings = {
        'DEBUG': settings.DEBUG,
        'DATABASES': list(settings.DATABASES.keys()),
        'INSTALLED_APPS': [app for app in settings.INSTALLED_APPS if not app.startswith('django.')],
        'MIDDLEWARE': len(settings.MIDDLEWARE),
        'TEMPLATES': len(settings.TEMPLATES),
        'STATIC_URL': settings.STATIC_URL,
        'MEDIA_URL': settings.MEDIA_URL,
        'USE_TZ': settings.USE_TZ,
    }
    
    for key, value in critical_settings.items():
        print(f"  {key}: {value}")
    
    analysis['settings'] = critical_settings
    return critical_settings

def identify_interaction_points():
    """Identify all component interaction points"""
    print("\n10. COMPONENT INTERACTION ANALYSIS")
    print("-" * 50)
    
    interactions = {
        'frontend_backend': [],
        'model_view': [],
        'view_template': [],
        'api_endpoints': []
    }
    
    # Frontend-Backend interactions (AJAX/Forms)
    template_dir = Path('templates')
    if template_dir.exists():
        for template in template_dir.rglob('*.html'):
            content = template.read_text()
            
            # Find AJAX calls
            ajax_patterns = re.findall(r'fetch\([\'"]([^\'"]+)', content)
            for pattern in ajax_patterns:
                interactions['frontend_backend'].append({
                    'template': str(template.relative_to(template_dir)),
                    'endpoint': pattern,
                    'type': 'AJAX'
                })
            
            # Find forms
            form_patterns = re.findall(r'<form[^>]*action=[\'"]([^\'"]+)', content)
            for pattern in form_patterns:
                interactions['frontend_backend'].append({
                    'template': str(template.relative_to(template_dir)),
                    'endpoint': pattern,
                    'type': 'FORM'
                })
    
    print(f"  Frontend-Backend interactions: {len(interactions['frontend_backend'])}")
    for interaction in interactions['frontend_backend'][:5]:
        print(f"    - {interaction['template'][:30]} → {interaction['endpoint'][:30]} ({interaction['type']})")
    
    analysis['interactions'] = interactions
    return interactions

# Run all analyses
print("\n" + "="*80)
print("STARTING COMPREHENSIVE ANALYSIS")
print("="*80)

structure = analyze_project_structure()
apps = analyze_django_apps()
urls = analyze_url_patterns()
relationships = analyze_model_relationships()
views = analyze_views_and_dependencies()
templates = analyze_templates()
static = analyze_static_files()
critical = check_critical_features()
settings = analyze_settings()
interactions = identify_interaction_points()

# Summary
print("\n" + "="*80)
print("ANALYSIS SUMMARY")
print("="*80)

# Count totals
total_models = sum(app_data['model_count'] for app_data in analysis['apps'].values())
total_urls = sum(len(patterns) for patterns in analysis['urls'].values())
total_templates = analysis['templates'].get('total', 0)
total_static = analysis['static'].get('css_count', 0) + analysis['static'].get('js_count', 0)

print(f"\n📊 CODEBASE METRICS:")
print(f"  Django Apps: {len(analysis['apps'])}")
print(f"  Models: {total_models}")
print(f"  URL Patterns: {total_urls}")
print(f"  Templates: {total_templates}")
print(f"  Static Files: {total_static}")
print(f"  Model Relationships: {len(analysis['relationships'])}")

print(f"\n⚠️ ISSUES FOUND: {len(analysis['issues'])}")
if analysis['issues']:
    for issue in analysis['issues']:
        print(f"  - {issue}")

print(f"\n🔍 CRITICAL FEATURES STATUS:")
critical_passed = sum(1 for _, passed in critical if passed)
print(f"  {critical_passed}/{len(critical)} features verified")

# Save detailed analysis
with open('comprehensive_qa_analysis.json', 'w') as f:
    # Convert non-serializable objects
    def clean_for_json(obj):
        if isinstance(obj, Path):
            return str(obj)
        return obj
    
    json.dump(analysis, f, indent=2, default=clean_for_json)

print(f"\n💾 Detailed analysis saved to: comprehensive_qa_analysis.json")
print("="*80)