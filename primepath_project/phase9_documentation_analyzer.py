#!/usr/bin/env python
"""
Phase 9: Documentation Deep Analysis & Generation
Ultra-comprehensive documentation audit with relationship preservation
"""
import os
import sys
import re
import json
import ast
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import inspect

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
import django
django.setup()

from django.apps import apps
from django.urls import get_resolver
from django.conf import settings

class Phase9DocumentationAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.project_root = self.base_path.parent
        
        self.documentation = {
            'existing_docs': [],
            'missing_docs': [],
            'api_endpoints': {},
            'models': {},
            'views': {},
            'urls': {},
            'frontend_components': {},
            'relationships': {},
            'environment_vars': {},
            'settings': {},
            'dependencies': {},
            'console_logs': [],
            'test_coverage': {},
            'deployment_info': {}
        }
        
        self.console_logs = []
        
    def log_console(self, category, message, level='info'):
        """Add console logging for debugging"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'message': message,
            'level': level
        }
        self.console_logs.append(log_entry)
        
        prefix = f"[PHASE9_{category.upper()}]"
        if level == 'error':
            print(f"❌ {prefix} {message}")
        elif level == 'warning':
            print(f"⚠️ {prefix} {message}")
        else:
            print(f"✅ {prefix} {message}")
            
    def scan_existing_documentation(self):
        """Scan for existing documentation files"""
        print("\n" + "="*80)
        print("📚 SCANNING EXISTING DOCUMENTATION")
        print("="*80)
        
        self.log_console("DOCS", "Starting documentation scan", "info")
        
        # Common documentation patterns
        doc_patterns = [
            'README*', 'readme*',
            'INSTALL*', 'install*',
            'DEPLOY*', 'deploy*',
            'API*', 'api*',
            'CONTRIBUTING*', 'contributing*',
            'LICENSE*', 'license*',
            'CHANGELOG*', 'changelog*',
            'TODO*', 'todo*',
            '*.md', '*.rst', '*.txt',
            'docs/', 'documentation/'
        ]
        
        found_docs = []
        for pattern in doc_patterns:
            for doc_file in self.project_root.rglob(pattern):
                if doc_file.is_file() and 'venv' not in str(doc_file) and 'node_modules' not in str(doc_file):
                    rel_path = doc_file.relative_to(self.project_root)
                    found_docs.append(str(rel_path))
                    
        self.documentation['existing_docs'] = found_docs
        self.log_console("DOCS", f"Found {len(found_docs)} documentation files", "info")
        
        # Check what's missing
        essential_docs = [
            'README.md',
            'requirements.txt',
            'API.md',
            'DEPLOYMENT.md',
            'CONTRIBUTING.md',
            'LICENSE'
        ]
        
        for doc in essential_docs:
            if not any(doc.lower() in existing.lower() for existing in found_docs):
                self.documentation['missing_docs'].append(doc)
                self.log_console("DOCS", f"Missing essential: {doc}", "warning")
                
    def analyze_api_endpoints(self):
        """Analyze and document all API endpoints"""
        print("\n" + "="*80)
        print("🔌 ANALYZING API ENDPOINTS")
        print("="*80)
        
        self.log_console("API", "Analyzing API endpoints", "info")
        
        from django.urls import get_resolver
        resolver = get_resolver()
        
        def extract_endpoints(resolver, prefix=''):
            endpoints = {}
            
            for pattern in resolver.url_patterns:
                if hasattr(pattern, 'url_patterns'):
                    namespace = getattr(pattern, 'namespace', '')
                    new_prefix = f"{prefix}{pattern.pattern}/"
                    nested = extract_endpoints(pattern, new_prefix)
                    endpoints.update(nested)
                else:
                    view_name = None
                    if hasattr(pattern.callback, '__name__'):
                        view_name = pattern.callback.__name__
                    elif hasattr(pattern.callback, 'view_class'):
                        view_name = pattern.callback.view_class.__name__
                        
                    if 'api' in f"{prefix}{pattern.pattern}".lower():
                        endpoint_info = {
                            'url': f"{prefix}{pattern.pattern}",
                            'name': pattern.name,
                            'view': view_name,
                            'methods': self.get_view_methods(pattern.callback)
                        }
                        endpoints[f"{prefix}{pattern.pattern}"] = endpoint_info
                        
            return endpoints
            
        self.documentation['api_endpoints'] = extract_endpoints(resolver)
        self.log_console("API", f"Documented {len(self.documentation['api_endpoints'])} API endpoints", "info")
        
    def get_view_methods(self, callback):
        """Get HTTP methods supported by a view"""
        methods = []
        if hasattr(callback, 'view_class'):
            view_class = callback.view_class
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if hasattr(view_class, method):
                    methods.append(method.upper())
        else:
            # Function-based view - check decorators
            methods = ['GET', 'POST']  # Default assumption
            
        return methods
        
    def analyze_models(self):
        """Analyze and document all models"""
        print("\n" + "="*80)
        print("📊 ANALYZING MODELS")
        print("="*80)
        
        self.log_console("MODELS", "Analyzing Django models", "info")
        
        for app_config in apps.get_app_configs():
            app_name = app_config.name
            
            if app_name.startswith('django.') or app_name in ['rest_framework', 'corsheaders']:
                continue
                
            models_info = {}
            
            for model in app_config.get_models():
                model_name = model.__name__
                
                # Get fields
                fields = {}
                for field in model._meta.fields:
                    field_info = {
                        'type': field.__class__.__name__,
                        'null': field.null,
                        'blank': field.blank,
                        'default': str(field.default) if field.has_default() else None
                    }
                    
                    # Check relationships
                    if hasattr(field, 'related_model') and field.related_model:
                        field_info['related_to'] = field.related_model.__name__
                        field_info['relationship_type'] = field.__class__.__name__
                        
                    fields[field.name] = field_info
                    
                # Get methods
                methods = [m for m in dir(model) if not m.startswith('_') and callable(getattr(model, m))]
                
                models_info[model_name] = {
                    'app': app_name,
                    'fields': fields,
                    'methods': methods[:10],  # Limit to first 10
                    'db_table': model._meta.db_table,
                    'verbose_name': str(model._meta.verbose_name),
                    'verbose_name_plural': str(model._meta.verbose_name_plural)
                }
                
            if models_info:
                self.documentation['models'][app_name] = models_info
                
        self.log_console("MODELS", f"Documented {sum(len(m) for m in self.documentation['models'].values())} models", "info")
        
    def analyze_frontend_architecture(self):
        """Analyze frontend JavaScript, CSS, and HTML structure"""
        print("\n" + "="*80)
        print("🎨 ANALYZING FRONTEND ARCHITECTURE")
        print("="*80)
        
        self.log_console("FRONTEND", "Analyzing frontend components", "info")
        
        # JavaScript modules
        js_modules = {}
        js_path = self.base_path / 'static' / 'js' / 'modules'
        if js_path.exists():
            for js_file in js_path.glob('*.js'):
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract class/function definitions
                classes = re.findall(r'class\s+(\w+)', content)
                functions = re.findall(r'function\s+(\w+)', content)
                exports = re.findall(r'export\s+(?:default\s+)?(\w+)', content)
                
                js_modules[js_file.name] = {
                    'classes': classes,
                    'functions': functions[:10],  # Limit
                    'exports': exports,
                    'size': len(content),
                    'lines': content.count('\n')
                }
                
        self.documentation['frontend_components']['javascript'] = js_modules
        
        # CSS structure
        css_files = {}
        css_path = self.base_path / 'static' / 'css'
        if css_path.exists():
            for css_file in css_path.rglob('*.css'):
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                css_files[str(css_file.relative_to(css_path))] = {
                    'size': len(content),
                    'lines': content.count('\n'),
                    'selectors': len(re.findall(r'[.#]\w+', content))
                }
                
        self.documentation['frontend_components']['css'] = css_files
        
        # Templates structure
        templates = {}
        template_path = self.base_path / 'templates'
        if template_path.exists():
            for template_file in template_path.rglob('*.html'):
                rel_path = template_file.relative_to(template_path)
                
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract template tags and blocks
                extends = re.findall(r'{%\s*extends\s+["\']([^"\']+)["\']', content)
                blocks = re.findall(r'{%\s*block\s+(\w+)', content)
                includes = re.findall(r'{%\s*include\s+["\']([^"\']+)["\']', content)
                
                templates[str(rel_path)] = {
                    'extends': extends[0] if extends else None,
                    'blocks': blocks,
                    'includes': includes,
                    'has_javascript': '<script' in content,
                    'has_css': '<style' in content or 'css' in content.lower()
                }
                
        self.documentation['frontend_components']['templates'] = templates
        
        self.log_console("FRONTEND", f"Documented {len(js_modules)} JS modules, {len(css_files)} CSS files, {len(templates)} templates", "info")
        
    def map_all_relationships(self):
        """Map all relationships between components"""
        print("\n" + "="*80)
        print("🔗 MAPPING ALL RELATIONSHIPS")
        print("="*80)
        
        self.log_console("RELATIONSHIPS", "Mapping component relationships", "info")
        
        relationships = {
            'model_to_model': {},
            'view_to_model': {},
            'url_to_view': {},
            'template_to_view': {},
            'js_dependencies': {},
            'css_dependencies': {},
            'api_to_model': {}
        }
        
        # Model to Model relationships
        for app_name, models in self.documentation['models'].items():
            for model_name, model_info in models.items():
                related_models = []
                for field_name, field_info in model_info['fields'].items():
                    if 'related_to' in field_info:
                        related_models.append({
                            'field': field_name,
                            'related_model': field_info['related_to'],
                            'type': field_info['relationship_type']
                        })
                        
                if related_models:
                    relationships['model_to_model'][f"{app_name}.{model_name}"] = related_models
                    
        # URL to View relationships
        from django.urls import get_resolver
        resolver = get_resolver()
        
        def extract_url_view_mapping(resolver, prefix=''):
            mappings = {}
            for pattern in resolver.url_patterns:
                if hasattr(pattern, 'url_patterns'):
                    new_prefix = f"{prefix}{pattern.pattern}/"
                    nested = extract_url_view_mapping(pattern, new_prefix)
                    mappings.update(nested)
                else:
                    if pattern.callback:
                        view_name = None
                        if hasattr(pattern.callback, '__name__'):
                            view_name = pattern.callback.__name__
                        elif hasattr(pattern.callback, 'view_class'):
                            view_name = pattern.callback.view_class.__name__
                            
                        if view_name:
                            mappings[f"{prefix}{pattern.pattern}"] = view_name
                            
            return mappings
            
        relationships['url_to_view'] = extract_url_view_mapping(resolver)
        
        self.documentation['relationships'] = relationships
        
        # Count total relationships
        total_relationships = sum([
            len(relationships['model_to_model']),
            len(relationships['url_to_view'])
        ])
        
        self.log_console("RELATIONSHIPS", f"Mapped {total_relationships} total relationships", "info")
        
    def analyze_environment_variables(self):
        """Analyze all environment variables used"""
        print("\n" + "="*80)
        print("🌍 ANALYZING ENVIRONMENT VARIABLES")
        print("="*80)
        
        self.log_console("ENV", "Analyzing environment variables", "info")
        
        env_vars = {}
        
        # Scan settings files for os.environ references
        settings_files = self.base_path.rglob('settings*.py')
        
        for settings_file in settings_files:
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find os.environ references
            env_patterns = re.findall(r'os\.environ\.get\(["\'](\w+)["\']', content)
            env_patterns.extend(re.findall(r'os\.getenv\(["\'](\w+)["\']', content))
            
            for var in env_patterns:
                if var not in env_vars:
                    env_vars[var] = {
                        'files': [str(settings_file.relative_to(self.project_root))],
                        'type': self.infer_env_var_type(var),
                        'required': False  # We'd need more analysis to determine this
                    }
                else:
                    env_vars[var]['files'].append(str(settings_file.relative_to(self.project_root)))
                    
        self.documentation['environment_vars'] = env_vars
        self.log_console("ENV", f"Found {len(env_vars)} environment variables", "info")
        
    def infer_env_var_type(self, var_name):
        """Infer the type of environment variable from its name"""
        var_upper = var_name.upper()
        
        if 'SECRET' in var_upper or 'KEY' in var_upper or 'TOKEN' in var_upper:
            return 'secret'
        elif 'URL' in var_upper or 'HOST' in var_upper:
            return 'url'
        elif 'PORT' in var_upper:
            return 'port'
        elif 'DEBUG' in var_upper or 'ENABLE' in var_upper:
            return 'boolean'
        elif 'PATH' in var_upper or 'DIR' in var_upper:
            return 'path'
        else:
            return 'string'
            
    def analyze_dependencies(self):
        """Analyze project dependencies"""
        print("\n" + "="*80)
        print("📦 ANALYZING DEPENDENCIES")
        print("="*80)
        
        self.log_console("DEPS", "Analyzing project dependencies", "info")
        
        # Python dependencies
        requirements_file = self.project_root / 'requirements.txt'
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                python_deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
            self.documentation['dependencies']['python'] = python_deps
            self.log_console("DEPS", f"Found {len(python_deps)} Python dependencies", "info")
        else:
            self.log_console("DEPS", "No requirements.txt found", "warning")
            
        # Check for package.json (JavaScript dependencies)
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            with open(package_json, 'r') as f:
                package_data = json.load(f)
                
            self.documentation['dependencies']['javascript'] = {
                'dependencies': package_data.get('dependencies', {}),
                'devDependencies': package_data.get('devDependencies', {})
            }
            
    def generate_monitoring_script(self):
        """Generate console monitoring for documentation"""
        script_content = f'''
// ===== PHASE 9 DOCUMENTATION MONITORING =====
// Generated: {datetime.now().isoformat()}

console.log('%c===== PHASE 9 DOCUMENTATION STATUS =====', 'color: indigo; font-weight: bold');

// Documentation Coverage
const documentationCoverage = {{
    existingDocs: {len(self.documentation['existing_docs'])},
    missingDocs: {len(self.documentation['missing_docs'])},
    apiEndpoints: {len(self.documentation['api_endpoints'])},
    models: {sum(len(m) for m in self.documentation['models'].values())},
    frontendComponents: {{
        javascript: {len(self.documentation['frontend_components'].get('javascript', {}))},
        css: {len(self.documentation['frontend_components'].get('css', {}))},
        templates: {len(self.documentation['frontend_components'].get('templates', {}))}
    }},
    relationships: {len(self.documentation['relationships'].get('model_to_model', {})) + len(self.documentation['relationships'].get('url_to_view', {}))},
    environmentVars: {len(self.documentation['environment_vars'])}
}};

console.table(documentationCoverage);

// Check documentation accessibility
console.log('%c===== CHECKING DOCUMENTATION LINKS =====', 'color: indigo; font-weight: bold');

const docLinks = [
    '/static/docs/README.md',
    '/static/docs/API.md',
    '/static/docs/DEPLOYMENT.md'
];

docLinks.forEach(link => {{
    fetch(link)
        .then(response => {{
            if (response.ok) {{
                console.log(`✅ [PHASE9] Documentation found: ${{link}}`);
            }} else {{
                console.log(`ℹ️ [PHASE9] Documentation not yet created: ${{link}}`);
            }}
        }})
        .catch(() => {{
            console.log(`ℹ️ [PHASE9] Documentation path not accessible: ${{link}}`);
        }});
}});

// Monitor for broken documentation links
document.addEventListener('DOMContentLoaded', function() {{
    const docLinks = document.querySelectorAll('a[href*="docs/"], a[href*=".md"]');
    
    docLinks.forEach(link => {{
        link.addEventListener('click', function(e) {{
            console.log(`[PHASE9] Documentation link clicked: ${{link.href}}`);
        }});
    }});
}});

// API Documentation Helper
window.PHASE9_API_DOCS = {{
    endpoints: {json.dumps(list(self.documentation['api_endpoints'].keys())[:10])},
    
    showEndpoints: function() {{
        console.log('%c===== API ENDPOINTS =====', 'color: blue; font-weight: bold');
        this.endpoints.forEach(endpoint => {{
            console.log(`  ${{endpoint}}`);
        }});
    }},
    
    testEndpoint: function(endpoint) {{
        fetch(endpoint)
            .then(response => {{
                console.log(`[PHASE9] ${{endpoint}}: Status ${{response.status}}`);
            }})
            .catch(error => {{
                console.error(`[PHASE9] ${{endpoint}}: Error`, error);
            }});
    }}
}};

console.log('%c===== PHASE 9 DOCUMENTATION READY =====', 'color: indigo; font-weight: bold');
console.log('Use window.PHASE9_API_DOCS.showEndpoints() to see API endpoints');
'''
        
        # Save monitoring script
        script_path = self.base_path / 'static' / 'js' / 'phase9_documentation_monitoring.js'
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        print(f"\n  ✅ Created: static/js/phase9_documentation_monitoring.js")
        
    def generate_report(self):
        """Generate comprehensive documentation analysis report"""
        print("\n" + "="*80)
        print("📊 DOCUMENTATION ANALYSIS REPORT")
        print("="*80)
        
        # Summary statistics
        print(f"\n  📋 SUMMARY:")
        print(f"     Existing Documentation: {len(self.documentation['existing_docs'])}")
        print(f"     Missing Documentation: {len(self.documentation['missing_docs'])}")
        print(f"     API Endpoints: {len(self.documentation['api_endpoints'])}")
        print(f"     Models Documented: {sum(len(m) for m in self.documentation['models'].values())}")
        print(f"     Frontend Components: {len(self.documentation['frontend_components'].get('javascript', {}))}")
        print(f"     Relationships Mapped: {len(self.documentation['relationships'].get('model_to_model', {}))}")
        print(f"     Environment Variables: {len(self.documentation['environment_vars'])}")
        
        if self.documentation['missing_docs']:
            print(f"\n  ⚠️ MISSING DOCUMENTATION:")
            for doc in self.documentation['missing_docs']:
                print(f"     - {doc}")
                
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'existing_docs': len(self.documentation['existing_docs']),
                'missing_docs': len(self.documentation['missing_docs']),
                'api_endpoints': len(self.documentation['api_endpoints']),
                'models': sum(len(m) for m in self.documentation['models'].values()),
                'relationships': len(self.documentation['relationships'].get('model_to_model', {})) + 
                                len(self.documentation['relationships'].get('url_to_view', {})),
                'environment_vars': len(self.documentation['environment_vars'])
            },
            'documentation': self.documentation,
            'console_logs': self.console_logs
        }
        
        report_path = self.base_path / 'phase9_documentation_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"\n  💾 Detailed report saved to: phase9_documentation_report.json")
        
        return report
        
    def run(self):
        """Execute Phase 9 documentation analysis"""
        print("\n" + "="*80)
        print("🚀 PHASE 9: DOCUMENTATION ANALYSIS & GENERATION")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Analyze existing documentation
            self.scan_existing_documentation()
            
            # Analyze codebase
            self.analyze_api_endpoints()
            self.analyze_models()
            self.analyze_frontend_architecture()
            
            # Map relationships
            self.map_all_relationships()
            
            # Analyze configuration
            self.analyze_environment_variables()
            self.analyze_dependencies()
            
            # Generate monitoring
            self.generate_monitoring_script()
            
            # Generate report
            report = self.generate_report()
            
            print("\n" + "="*80)
            print("✅ PHASE 9 ANALYSIS COMPLETE")
            print("="*80)
            
            print("\n📌 READY TO GENERATE DOCUMENTATION:")
            print("  1. README.md - Project overview and setup")
            print("  2. API.md - Complete API documentation")
            print("  3. DEPLOYMENT.md - Deployment guide")
            print("  4. DEVELOPMENT.md - Developer guide")
            print("  5. ARCHITECTURE.md - System architecture")
            
            return report
            
        except Exception as e:
            print(f"\n❌ ANALYSIS FAILED: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Main execution"""
    analyzer = Phase9DocumentationAnalyzer()
    report = analyzer.run()
    
    if report:
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())