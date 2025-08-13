#!/usr/bin/env python3
"""
Phase 11: Final Integration & Modularization Analysis
Ultra-comprehensive analysis of the entire codebase to identify remaining modularization needs
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
import re

class Phase11Analyzer:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'phase': 11,
            'title': 'Final Integration & Testing',
            'areas_to_modularize': [],
            'current_structure': {},
            'recommendations': [],
            'risk_assessment': []
        }
    
    def analyze_all(self):
        """Run complete analysis"""
        print("="*70)
        print("  PHASE 11: FINAL INTEGRATION & MODULARIZATION ANALYSIS")
        print("="*70)
        
        # 1. Analyze current structure
        print("\n1. ANALYZING CURRENT STRUCTURE...")
        self.analyze_current_structure()
        
        # 2. Analyze templates
        print("\n2. ANALYZING TEMPLATE ORGANIZATION...")
        self.analyze_templates()
        
        # 3. Analyze static files
        print("\n3. ANALYZING STATIC FILES...")
        self.analyze_static_files()
        
        # 4. Analyze API structure
        print("\n4. ANALYZING API STRUCTURE...")
        self.analyze_api_structure()
        
        # 5. Analyze test organization
        print("\n5. ANALYZING TEST FRAMEWORK...")
        self.analyze_tests()
        
        # 6. Analyze settings and configuration
        print("\n6. ANALYZING SETTINGS & CONFIG...")
        self.analyze_settings()
        
        # 7. Analyze documentation
        print("\n7. ANALYZING DOCUMENTATION...")
        self.analyze_documentation()
        
        # 8. Check for code duplication
        print("\n8. CHECKING FOR CODE DUPLICATION...")
        self.check_duplication()
        
        # 9. Analyze dependencies
        print("\n9. ANALYZING DEPENDENCIES...")
        self.analyze_dependencies()
        
        # 10. Generate recommendations
        print("\n10. GENERATING RECOMMENDATIONS...")
        self.generate_recommendations()
        
        # Save results
        self.save_results()
    
    def analyze_current_structure(self):
        """Analyze the current project structure"""
        structure = {}
        
        # Apps structure
        apps = ['placement_test', 'core', 'api', 'common']
        for app in apps:
            app_dir = self.base_dir / app
            if app_dir.exists():
                structure[app] = {
                    'models': [],
                    'views': [],
                    'urls': [],
                    'services': [],
                    'templates': [],
                    'static': []
                }
                
                # Check for modular structure
                if (app_dir / 'models').is_dir():
                    structure[app]['models'] = [f.name for f in (app_dir / 'models').glob('*.py') if f.name != '__init__.py']
                elif (app_dir / 'models.py').exists():
                    structure[app]['models'] = ['models.py']
                
                if (app_dir / 'views').is_dir():
                    structure[app]['views'] = [f.name for f in (app_dir / 'views').glob('*.py') if f.name != '__init__.py']
                elif (app_dir / 'views.py').exists():
                    structure[app]['views'] = ['views.py']
                
                if (app_dir / 'services').is_dir():
                    structure[app]['services'] = [f.name for f in (app_dir / 'services').glob('*.py') if f.name != '__init__.py']
                
                print(f"   {app}:")
                print(f"      Models: {len(structure[app]['models'])} files")
                print(f"      Views: {len(structure[app]['views'])} files")
                print(f"      Services: {len(structure[app]['services'])} files")
        
        self.analysis_results['current_structure'] = structure
    
    def analyze_templates(self):
        """Analyze template organization"""
        templates_dir = self.base_dir / 'templates'
        template_analysis = {
            'total_templates': 0,
            'organized_by_app': {},
            'shared_components': [],
            'base_templates': [],
            'needs_reorganization': []
        }
        
        if templates_dir.exists():
            for template_file in templates_dir.rglob('*.html'):
                template_analysis['total_templates'] += 1
                rel_path = template_file.relative_to(templates_dir)
                
                # Check organization
                parts = rel_path.parts
                if len(parts) > 1:
                    app_name = parts[0]
                    if app_name not in template_analysis['organized_by_app']:
                        template_analysis['organized_by_app'][app_name] = []
                    template_analysis['organized_by_app'][app_name].append(str(rel_path))
                    
                    # Check for components
                    if 'components' in str(rel_path):
                        template_analysis['shared_components'].append(str(rel_path))
                else:
                    # Root level template
                    template_analysis['base_templates'].append(str(rel_path))
                
                # Check if needs reorganization (e.g., duplicate functionality)
                content = template_file.read_text()
                if content.count('{% extends') > 1 or 'TODO' in content or 'FIXME' in content:
                    template_analysis['needs_reorganization'].append(str(rel_path))
        
        print(f"   Total templates: {template_analysis['total_templates']}")
        print(f"   Apps with templates: {len(template_analysis['organized_by_app'])}")
        print(f"   Shared components: {len(template_analysis['shared_components'])}")
        print(f"   Base templates: {len(template_analysis['base_templates'])}")
        
        if template_analysis['needs_reorganization']:
            print(f"   ⚠️  Templates needing attention: {len(template_analysis['needs_reorganization'])}")
        
        self.analysis_results['template_analysis'] = template_analysis
    
    def analyze_static_files(self):
        """Analyze static files organization"""
        static_dir = self.base_dir / 'static'
        static_analysis = {
            'css_files': [],
            'js_files': [],
            'img_files': [],
            'organization': {
                'modular_js': [],
                'modular_css': [],
                'legacy_files': []
            }
        }
        
        if static_dir.exists():
            # CSS files
            for css_file in static_dir.rglob('*.css'):
                rel_path = css_file.relative_to(static_dir)
                static_analysis['css_files'].append(str(rel_path))
                
                # Check if modular
                if 'components' in str(rel_path) or 'modules' in str(rel_path):
                    static_analysis['organization']['modular_css'].append(str(rel_path))
                elif 'old' in str(rel_path) or 'legacy' in str(rel_path) or 'backup' in str(rel_path):
                    static_analysis['organization']['legacy_files'].append(str(rel_path))
            
            # JS files
            for js_file in static_dir.rglob('*.js'):
                rel_path = js_file.relative_to(static_dir)
                static_analysis['js_files'].append(str(rel_path))
                
                # Check if modular
                if 'modules' in str(rel_path) or 'components' in str(rel_path):
                    static_analysis['organization']['modular_js'].append(str(rel_path))
                elif 'old' in str(rel_path) or 'legacy' in str(rel_path) or 'backup' in str(rel_path):
                    static_analysis['organization']['legacy_files'].append(str(rel_path))
        
        print(f"   CSS files: {len(static_analysis['css_files'])}")
        print(f"   JS files: {len(static_analysis['js_files'])}")
        print(f"   Modular JS: {len(static_analysis['organization']['modular_js'])}")
        print(f"   Modular CSS: {len(static_analysis['organization']['modular_css'])}")
        
        if static_analysis['organization']['legacy_files']:
            print(f"   ⚠️  Legacy files found: {len(static_analysis['organization']['legacy_files'])}")
        
        self.analysis_results['static_analysis'] = static_analysis
    
    def analyze_api_structure(self):
        """Analyze API structure and versioning"""
        api_analysis = {
            'has_versioning': False,
            'endpoints': [],
            'serializers': [],
            'viewsets': [],
            'needs_improvement': []
        }
        
        api_dir = self.base_dir / 'api'
        if api_dir.exists():
            # Check for versioning
            if (api_dir / 'v1').exists() or (api_dir / 'v2').exists():
                api_analysis['has_versioning'] = True
            
            # Check for serializers
            if (api_dir / 'serializers.py').exists() or (api_dir / 'serializers').is_dir():
                if (api_dir / 'serializers').is_dir():
                    api_analysis['serializers'] = [f.name for f in (api_dir / 'serializers').glob('*.py')]
                else:
                    api_analysis['serializers'] = ['serializers.py']
            
            # Check URLs
            if (api_dir / 'urls.py').exists():
                content = (api_dir / 'urls.py').read_text()
                # Extract URL patterns
                patterns = re.findall(r"path\(['\"]([^'\"]+)", content)
                api_analysis['endpoints'] = patterns[:10]  # First 10 for sample
        
        print(f"   API versioning: {'Yes' if api_analysis['has_versioning'] else 'No'}")
        print(f"   Serializers: {len(api_analysis['serializers'])}")
        print(f"   Sample endpoints: {len(api_analysis['endpoints'])}")
        
        if not api_analysis['has_versioning']:
            api_analysis['needs_improvement'].append('Add API versioning')
            print("   ⚠️  Recommendation: Add API versioning")
        
        self.analysis_results['api_analysis'] = api_analysis
    
    def analyze_tests(self):
        """Analyze test organization"""
        test_analysis = {
            'test_files': [],
            'test_directories': [],
            'coverage': 'unknown',
            'organization': 'mixed'
        }
        
        # Look for test files
        for test_file in self.base_dir.rglob('test*.py'):
            if 'venv' not in str(test_file) and 'migrations' not in str(test_file):
                test_analysis['test_files'].append(str(test_file.relative_to(self.base_dir)))
        
        # Check for tests directories
        for app in ['placement_test', 'core', 'api']:
            test_dir = self.base_dir / app / 'tests'
            if test_dir.exists():
                test_analysis['test_directories'].append(str(test_dir.relative_to(self.base_dir)))
                test_analysis['organization'] = 'modular'
        
        print(f"   Test files found: {len(test_analysis['test_files'])}")
        print(f"   Test directories: {len(test_analysis['test_directories'])}")
        print(f"   Organization: {test_analysis['organization']}")
        
        if test_analysis['organization'] == 'mixed':
            print("   ⚠️  Tests are scattered, consider organizing into test directories")
        
        self.analysis_results['test_analysis'] = test_analysis
    
    def analyze_settings(self):
        """Analyze settings and configuration"""
        settings_analysis = {
            'settings_files': [],
            'environment_specific': False,
            'uses_env_vars': False,
            'has_local_settings': False
        }
        
        settings_dir = self.base_dir / 'primepath_project'
        if settings_dir.exists():
            for settings_file in settings_dir.glob('settings*.py'):
                settings_analysis['settings_files'].append(settings_file.name)
                
                content = settings_file.read_text()
                if 'os.environ' in content or 'env(' in content:
                    settings_analysis['uses_env_vars'] = True
                
                if 'local' in settings_file.name.lower():
                    settings_analysis['has_local_settings'] = True
            
            if len(settings_analysis['settings_files']) > 1:
                settings_analysis['environment_specific'] = True
        
        print(f"   Settings files: {settings_analysis['settings_files']}")
        print(f"   Environment-specific: {settings_analysis['environment_specific']}")
        print(f"   Uses env vars: {settings_analysis['uses_env_vars']}")
        
        self.analysis_results['settings_analysis'] = settings_analysis
    
    def analyze_documentation(self):
        """Analyze documentation structure"""
        doc_analysis = {
            'readme_exists': False,
            'docs_directory': False,
            'markdown_files': [],
            'api_docs': False,
            'code_comments_quality': 'unknown'
        }
        
        # Check for README
        if (self.base_dir / 'README.md').exists() or (self.base_dir / 'readme.md').exists():
            doc_analysis['readme_exists'] = True
        
        # Check for docs directory
        if (self.base_dir / 'docs').exists():
            doc_analysis['docs_directory'] = True
        
        # Find all markdown files
        for md_file in self.base_dir.glob('*.md'):
            doc_analysis['markdown_files'].append(md_file.name)
        
        print(f"   README exists: {doc_analysis['readme_exists']}")
        print(f"   Docs directory: {doc_analysis['docs_directory']}")
        print(f"   Markdown files: {len(doc_analysis['markdown_files'])}")
        
        self.analysis_results['documentation'] = doc_analysis
    
    def check_duplication(self):
        """Check for code duplication"""
        duplication = {
            'similar_functions': [],
            'repeated_patterns': [],
            'duplicate_templates': []
        }
        
        # Simple check for similar view patterns
        view_patterns = {}
        for py_file in self.base_dir.rglob('views*.py'):
            if 'venv' not in str(py_file) and 'migrations' not in str(py_file):
                content = py_file.read_text()
                # Look for common patterns
                if 'def list' in content:
                    view_patterns.setdefault('list_views', []).append(str(py_file.relative_to(self.base_dir)))
                if 'def create' in content:
                    view_patterns.setdefault('create_views', []).append(str(py_file.relative_to(self.base_dir)))
                if 'def update' in content:
                    view_patterns.setdefault('update_views', []).append(str(py_file.relative_to(self.base_dir)))
        
        for pattern, files in view_patterns.items():
            if len(files) > 2:
                duplication['repeated_patterns'].append({
                    'pattern': pattern,
                    'count': len(files),
                    'files': files[:3]  # First 3 examples
                })
        
        print(f"   Repeated patterns found: {len(duplication['repeated_patterns'])}")
        
        self.analysis_results['duplication'] = duplication
    
    def analyze_dependencies(self):
        """Analyze inter-module dependencies"""
        dependencies = {
            'circular_imports': [],
            'tight_coupling': [],
            'loose_modules': []
        }
        
        # Check for potential circular imports
        for py_file in self.base_dir.rglob('*.py'):
            if 'venv' not in str(py_file) and 'migrations' not in str(py_file):
                try:
                    content = py_file.read_text()
                    # Simple check for imports from parent modules
                    if 'from ..' in content and 'import' in content:
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip().startswith('from ..') and 'import' in line:
                                dependencies['tight_coupling'].append({
                                    'file': str(py_file.relative_to(self.base_dir)),
                                    'import': line.strip()[:50]
                                })
                except:
                    pass
        
        print(f"   Tight coupling instances: {len(dependencies['tight_coupling'])}")
        
        self.analysis_results['dependencies'] = dependencies
    
    def generate_recommendations(self):
        """Generate modularization recommendations"""
        recommendations = []
        
        # Based on analysis, generate recommendations
        
        # 1. Template recommendations
        if self.analysis_results.get('template_analysis', {}).get('needs_reorganization'):
            recommendations.append({
                'priority': 'HIGH',
                'area': 'Templates',
                'action': 'Reorganize templates with issues',
                'files': self.analysis_results['template_analysis']['needs_reorganization'][:5]
            })
        
        # 2. Static file recommendations
        if self.analysis_results.get('static_analysis', {}).get('organization', {}).get('legacy_files'):
            recommendations.append({
                'priority': 'MEDIUM',
                'area': 'Static Files',
                'action': 'Clean up legacy/backup files',
                'files': self.analysis_results['static_analysis']['organization']['legacy_files'][:5]
            })
        
        # 3. API recommendations
        if not self.analysis_results.get('api_analysis', {}).get('has_versioning'):
            recommendations.append({
                'priority': 'HIGH',
                'area': 'API',
                'action': 'Implement API versioning (v1, v2)',
                'reason': 'Better backward compatibility and future-proofing'
            })
        
        # 4. Test recommendations
        if self.analysis_results.get('test_analysis', {}).get('organization') == 'mixed':
            recommendations.append({
                'priority': 'MEDIUM',
                'area': 'Tests',
                'action': 'Organize tests into app-specific test directories',
                'benefit': 'Better test organization and easier maintenance'
            })
        
        # 5. Documentation recommendations
        if not self.analysis_results.get('documentation', {}).get('docs_directory'):
            recommendations.append({
                'priority': 'LOW',
                'area': 'Documentation',
                'action': 'Create docs/ directory with structured documentation',
                'benefit': 'Better project documentation and onboarding'
            })
        
        # 6. Code duplication
        if self.analysis_results.get('duplication', {}).get('repeated_patterns'):
            recommendations.append({
                'priority': 'MEDIUM',
                'area': 'Code Quality',
                'action': 'Extract common patterns into base classes or mixins',
                'patterns': [p['pattern'] for p in self.analysis_results['duplication']['repeated_patterns']]
            })
        
        print(f"   Generated {len(recommendations)} recommendations")
        for rec in recommendations:
            print(f"   [{rec['priority']}] {rec['area']}: {rec['action']}")
        
        self.analysis_results['recommendations'] = recommendations
        
        # Risk assessment
        risks = []
        
        # Assess risks
        if len(self.analysis_results.get('dependencies', {}).get('tight_coupling', [])) > 10:
            risks.append({
                'level': 'MEDIUM',
                'area': 'Dependencies',
                'issue': 'High coupling between modules',
                'mitigation': 'Refactor to use dependency injection or service layer'
            })
        
        self.analysis_results['risk_assessment'] = risks
    
    def save_results(self):
        """Save analysis results"""
        output_file = self.base_dir / 'phase11_analysis_results.json'
        with open(output_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        
        print(f"\n📄 Analysis saved to: {output_file}")
        print("="*70)

if __name__ == "__main__":
    analyzer = Phase11Analyzer()
    analyzer.analyze_all()