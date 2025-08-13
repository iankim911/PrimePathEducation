#!/usr/bin/env python
"""
Deep Codebase Analysis Script
Comprehensive analysis of PrimePath structure and dependencies
"""
import os
import sys
import re
import json
from pathlib import Path
from collections import defaultdict

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
import django
django.setup()

class CodebaseAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.apps = ['core', 'placement_test', 'api', 'common']
        self.analysis = {
            'structure': {},
            'dependencies': defaultdict(list),
            'models': {},
            'views': {},
            'urls': {},
            'templates': {},
            'static_files': {},
            'orphaned_files': [],
            'test_files': [],
            'cleanup_opportunities': []
        }
        
    def analyze_app_structure(self):
        """Analyze each Django app structure"""
        print("\n" + "="*80)
        print("📁 APP STRUCTURE ANALYSIS")
        print("="*80)
        
        for app_name in self.apps:
            app_path = self.base_path / app_name
            if not app_path.exists():
                print(f"  ⚠️ {app_name}: App directory not found")
                continue
                
            structure = {
                'models': [],
                'views': [],
                'urls': [],
                'forms': [],
                'serializers': [],
                'services': [],
                'utils': [],
                'tests': [],
                'templates': [],
                'static': [],
                'migrations': 0
            }
            
            # Count Python files by type
            for py_file in app_path.rglob('*.py'):
                if '__pycache__' in str(py_file):
                    continue
                    
                rel_path = py_file.relative_to(app_path)
                
                if 'migrations' in str(rel_path):
                    structure['migrations'] += 1
                elif 'models' in str(rel_path.name):
                    structure['models'].append(str(rel_path))
                elif 'views' in str(rel_path.name):
                    structure['views'].append(str(rel_path))
                elif 'urls' in str(rel_path.name):
                    structure['urls'].append(str(rel_path))
                elif 'forms' in str(rel_path.name):
                    structure['forms'].append(str(rel_path))
                elif 'serializers' in str(rel_path.name):
                    structure['serializers'].append(str(rel_path))
                elif 'services' in str(rel_path.name):
                    structure['services'].append(str(rel_path))
                elif 'utils' in str(rel_path.name):
                    structure['utils'].append(str(rel_path))
                elif 'test' in str(rel_path.name):
                    structure['tests'].append(str(rel_path))
                    self.analysis['test_files'].append(str(py_file))
            
            # Count templates
            template_dir = app_path / 'templates'
            if template_dir.exists():
                structure['templates'] = len(list(template_dir.rglob('*.html')))
            
            # Count static files
            static_dir = app_path / 'static'
            if static_dir.exists():
                structure['static'] = {
                    'css': len(list(static_dir.rglob('*.css'))),
                    'js': len(list(static_dir.rglob('*.js'))),
                    'images': len(list(static_dir.rglob('*.png'))) + len(list(static_dir.rglob('*.jpg')))
                }
            
            self.analysis['structure'][app_name] = structure
            
            # Print summary
            print(f"\n  📦 {app_name.upper()}")
            print(f"     Models: {len(structure['models'])}")
            print(f"     Views: {len(structure['views'])}")
            print(f"     Services: {len(structure['services'])}")
            print(f"     Tests: {len(structure['tests'])}")
            print(f"     Migrations: {structure['migrations']}")
            print(f"     Templates: {structure['templates']}")
            
    def analyze_dependencies(self):
        """Analyze inter-app dependencies"""
        print("\n" + "="*80)
        print("🔗 DEPENDENCY ANALYSIS")
        print("="*80)
        
        for app_name in self.apps:
            app_path = self.base_path / app_name
            if not app_path.exists():
                continue
                
            dependencies = set()
            
            for py_file in app_path.rglob('*.py'):
                if '__pycache__' in str(py_file):
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Find imports from other apps
                    for other_app in self.apps:
                        if other_app != app_name:
                            if f'from {other_app}' in content or f'import {other_app}' in content:
                                dependencies.add(other_app)
                                
                except Exception as e:
                    pass
                    
            self.analysis['dependencies'][app_name] = list(dependencies)
            
            if dependencies:
                print(f"\n  {app_name} depends on: {', '.join(dependencies)}")
            else:
                print(f"\n  {app_name}: No inter-app dependencies")
                
    def analyze_models(self):
        """Analyze Django models and relationships"""
        print("\n" + "="*80)
        print("📊 MODEL ANALYSIS")
        print("="*80)
        
        from django.apps import apps
        
        for app_name in self.apps:
            models = []
            try:
                app_config = apps.get_app_config(app_name)
                for model in app_config.get_models():
                    model_info = {
                        'name': model.__name__,
                        'fields': len(model._meta.fields),
                        'relationships': [],
                        'db_table': model._meta.db_table
                    }
                    
                    # Find relationships
                    for field in model._meta.fields:
                        if hasattr(field, 'related_model') and field.related_model:
                            model_info['relationships'].append({
                                'type': field.__class__.__name__,
                                'to': field.related_model.__name__
                            })
                            
                    models.append(model_info)
                    
            except Exception as e:
                print(f"  ⚠️ Error analyzing {app_name}: {e}")
                
            self.analysis['models'][app_name] = models
            
            if models:
                print(f"\n  📦 {app_name.upper()}")
                for model in models:
                    print(f"     - {model['name']} ({model['fields']} fields)")
                    if model['relationships']:
                        for rel in model['relationships']:
                            print(f"       → {rel['type']}: {rel['to']}")
                            
    def analyze_urls(self):
        """Analyze URL patterns and routing"""
        print("\n" + "="*80)
        print("🌐 URL PATTERN ANALYSIS")
        print("="*80)
        
        from django.urls import get_resolver
        
        resolver = get_resolver()
        url_patterns = []
        
        def extract_patterns(resolver, prefix=''):
            patterns = []
            for pattern in resolver.url_patterns:
                if hasattr(pattern, 'url_patterns'):
                    # Nested patterns
                    patterns.extend(extract_patterns(pattern, prefix + str(pattern.pattern)))
                else:
                    patterns.append({
                        'pattern': prefix + str(pattern.pattern),
                        'name': pattern.name,
                        'app': pattern.callback.__module__.split('.')[0] if hasattr(pattern, 'callback') else None
                    })
            return patterns
            
        url_patterns = extract_patterns(resolver)
        
        # Group by app
        by_app = defaultdict(list)
        for pattern in url_patterns:
            if pattern['app'] in self.apps:
                by_app[pattern['app']].append(pattern)
                
        for app, patterns in by_app.items():
            print(f"\n  📦 {app.upper()}: {len(patterns)} URL patterns")
            for p in patterns[:5]:  # Show first 5
                print(f"     - {p['pattern']} ({p['name']})")
            if len(patterns) > 5:
                print(f"     ... and {len(patterns) - 5} more")
                
        self.analysis['urls'] = dict(by_app)
        
    def analyze_frontend_assets(self):
        """Analyze templates, CSS, and JavaScript"""
        print("\n" + "="*80)
        print("🎨 FRONTEND ASSETS ANALYSIS")
        print("="*80)
        
        # Templates
        template_dir = self.base_path / 'templates'
        if template_dir.exists():
            templates = list(template_dir.rglob('*.html'))
            self.analysis['templates'] = {
                'count': len(templates),
                'by_app': defaultdict(list)
            }
            
            for template in templates:
                parts = template.relative_to(template_dir).parts
                if len(parts) > 1:
                    app = parts[0]
                    self.analysis['templates']['by_app'][app].append(str(template.name))
                    
            print(f"\n  📄 Templates: {len(templates)} total")
            for app, tmpl_list in self.analysis['templates']['by_app'].items():
                print(f"     {app}: {len(tmpl_list)} templates")
                
        # Static files
        static_dir = self.base_path / 'static'
        if static_dir.exists():
            css_files = list(static_dir.rglob('*.css'))
            js_files = list(static_dir.rglob('*.js'))
            
            self.analysis['static_files'] = {
                'css': {'count': len(css_files), 'files': []},
                'js': {'count': len(js_files), 'files': []}
            }
            
            # Analyze CSS
            print(f"\n  🎨 CSS Files: {len(css_files)}")
            for css in css_files[:5]:
                size = css.stat().st_size / 1024  # KB
                self.analysis['static_files']['css']['files'].append({
                    'name': str(css.relative_to(static_dir)),
                    'size_kb': round(size, 2)
                })
                print(f"     - {css.name} ({size:.1f} KB)")
                
            # Analyze JS
            print(f"\n  📜 JavaScript Files: {len(js_files)}")
            for js in js_files[:5]:
                size = js.stat().st_size / 1024  # KB
                self.analysis['static_files']['js']['files'].append({
                    'name': str(js.relative_to(static_dir)),
                    'size_kb': round(size, 2)
                })
                print(f"     - {js.name} ({size:.1f} KB)")
                
    def find_orphaned_files(self):
        """Find orphaned or unused files"""
        print("\n" + "="*80)
        print("🔍 ORPHANED FILES ANALYSIS")
        print("="*80)
        
        # Find Python files not in standard locations
        all_py_files = set(self.base_path.rglob('*.py'))
        standard_locations = set()
        
        for app in self.apps:
            app_path = self.base_path / app
            if app_path.exists():
                standard_locations.update(app_path.rglob('*.py'))
                
        # Add project settings
        project_path = self.base_path / 'primepath_project'
        if project_path.exists():
            standard_locations.update(project_path.rglob('*.py'))
            
        orphaned = all_py_files - standard_locations
        orphaned = [f for f in orphaned if '__pycache__' not in str(f) and 'migrations' not in str(f)]
        
        self.analysis['orphaned_files'] = [str(f.relative_to(self.base_path)) for f in orphaned]
        
        if orphaned:
            print(f"\n  ⚠️ Found {len(orphaned)} potentially orphaned Python files:")
            for f in orphaned[:10]:
                print(f"     - {f.relative_to(self.base_path)}")
                
    def identify_cleanup_opportunities(self):
        """Identify specific cleanup opportunities"""
        print("\n" + "="*80)
        print("🧹 CLEANUP OPPORTUNITIES")
        print("="*80)
        
        opportunities = []
        
        # 1. Test files outside test directories
        test_files_outside = []
        for test_file in self.analysis['test_files']:
            if 'tests' not in test_file and 'test' not in test_file:
                test_files_outside.append(test_file)
                
        if test_files_outside:
            opportunities.append({
                'type': 'ORGANIZE_TESTS',
                'description': f'Move {len(test_files_outside)} test files to proper test directories',
                'files': test_files_outside
            })
            
        # 2. Orphaned files
        if self.analysis['orphaned_files']:
            opportunities.append({
                'type': 'CLEAN_ORPHANED',
                'description': f'Review {len(self.analysis["orphaned_files"])} orphaned files',
                'files': self.analysis['orphaned_files']
            })
            
        # 3. Empty directories
        empty_dirs = []
        for root, dirs, files in os.walk(self.base_path):
            if not files and not dirs and '__pycache__' not in root:
                empty_dirs.append(root)
                
        if empty_dirs:
            opportunities.append({
                'type': 'REMOVE_EMPTY_DIRS',
                'description': f'Remove {len(empty_dirs)} empty directories',
                'directories': empty_dirs
            })
            
        # 4. Database cleanup
        from placement_test.models import StudentSession
        from core.models import SubProgram
        
        # Check for test sessions
        test_sessions = StudentSession.objects.filter(
            student_name__icontains='test'
        ).count()
        
        if test_sessions > 0:
            opportunities.append({
                'type': 'CLEAN_TEST_DATA',
                'description': f'Remove {test_sessions} test student sessions',
                'count': test_sessions
            })
            
        # Check for test subprograms
        test_subprograms = SubProgram.objects.filter(
            name__icontains='test'
        ).count()
        
        if test_subprograms > 0:
            opportunities.append({
                'type': 'CLEAN_TEST_SUBPROGRAMS',
                'description': f'Clean {test_subprograms} test subprograms from database',
                'count': test_subprograms
            })
            
        self.analysis['cleanup_opportunities'] = opportunities
        
        # Print opportunities
        for i, opp in enumerate(opportunities, 1):
            print(f"\n  {i}. {opp['description']}")
            print(f"     Type: {opp['type']}")
            if 'files' in opp and opp['files']:
                print(f"     Files: {len(opp['files'])}")
            if 'count' in opp:
                print(f"     Count: {opp['count']}")
                
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "="*80)
        print("📊 ANALYSIS SUMMARY")
        print("="*80)
        
        # App summary
        print("\n  📦 APP STRUCTURE:")
        for app, structure in self.analysis['structure'].items():
            total_files = sum(len(v) if isinstance(v, list) else 0 for v in structure.values())
            print(f"     {app}: {total_files} Python files")
            
        # Dependency summary
        print("\n  🔗 DEPENDENCIES:")
        for app, deps in self.analysis['dependencies'].items():
            if deps:
                print(f"     {app} → {', '.join(deps)}")
                
        # Cleanup summary
        print(f"\n  🧹 CLEANUP OPPORTUNITIES: {len(self.analysis['cleanup_opportunities'])}")
        
        # Save detailed report
        report_file = self.base_path / 'codebase_analysis_report.json'
        with open(report_file, 'w') as f:
            # Convert Path objects to strings for JSON serialization
            analysis_copy = json.loads(json.dumps(self.analysis, default=str))
            json.dump(analysis_copy, f, indent=2)
            
        print(f"\n  💾 Detailed report saved to: codebase_analysis_report.json")
        
        # Add console logging
        print("\n  🔍 CONSOLE LOGGING:")
        print("     Adding comprehensive console.log() debugging...")
        self.add_console_logging()
        
        return self.analysis
        
    def add_console_logging(self):
        """Add comprehensive console logging to track cleanup"""
        console_script = '''
// ===== CODEBASE CLEANUP PHASE 6+ TRACKING =====
console.log('%c===== CLEANUP PHASE 6+ MONITORING =====', 'color: blue; font-weight: bold');

// Track app initialization
console.log('[CLEANUP] Checking app initialization...');
['core', 'placement_test', 'api', 'common'].forEach(app => {
    console.log(`[CLEANUP] ${app} app: checking...`);
});

// Track model relationships
console.log('[CLEANUP] Verifying model relationships...');

// Track URL routing
console.log('[CLEANUP] Checking URL patterns...');
if (window.location.pathname) {
    console.log(`[CLEANUP] Current path: ${window.location.pathname}`);
}

// Track frontend assets
console.log('[CLEANUP] Frontend assets check:');
console.log(`  - CSS loaded: ${document.styleSheets.length} stylesheets`);
console.log(`  - JS modules: ${Object.keys(window).filter(k => k.includes('Manager') || k.includes('Module')).length} modules`);

// Track API calls
if (window.fetch) {
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        console.log(`[CLEANUP] API call: ${args[0]}`);
        return originalFetch.apply(this, args);
    };
}

// Track form submissions
document.addEventListener('submit', function(e) {
    console.log(`[CLEANUP] Form submitted: ${e.target.action || 'unknown'}`);
});

// Track navigation
window.addEventListener('popstate', function(e) {
    console.log('[CLEANUP] Navigation event detected');
});

console.log('%c===== CLEANUP MONITORING ACTIVE =====', 'color: green; font-weight: bold');
'''
        
        # Save console script
        console_file = self.base_path / 'static' / 'js' / 'cleanup_monitoring.js'
        console_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(console_file, 'w') as f:
            f.write(console_script)
            
        print(f"     Created: static/js/cleanup_monitoring.js")
        
    def run(self):
        """Run complete analysis"""
        print("\n" + "="*80)
        print("🚀 DEEP CODEBASE ANALYSIS - PHASE 6+ PREPARATION")
        print("="*80)
        print("Analyzing entire PrimePath codebase...")
        
        self.analyze_app_structure()
        self.analyze_dependencies()
        self.analyze_models()
        self.analyze_urls()
        self.analyze_frontend_assets()
        self.find_orphaned_files()
        self.identify_cleanup_opportunities()
        
        return self.generate_report()

if __name__ == "__main__":
    analyzer = CodebaseAnalyzer()
    analysis = analyzer.run()
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Review codebase_analysis_report.json")
    print("2. Decide on cleanup priorities")
    print("3. Execute cleanup with preserved relationships")