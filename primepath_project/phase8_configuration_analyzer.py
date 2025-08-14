#!/usr/bin/env python
"""
Phase 8: Configuration & Settings Deep Analysis
Ultra-comprehensive configuration audit with relationship preservation
"""
import os
import sys
import re
import json
import ast
from pathlib import Path
from datetime import datetime
import hashlib
from collections import defaultdict
import configparser

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
import django
django.setup()

from django.conf import settings
from django.apps import apps

class Phase8ConfigurationAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.results = {
            'settings_files': [],
            'environment_variables': [],
            'hardcoded_secrets': [],
            'database_configs': [],
            'static_configs': [],
            'middleware_analysis': [],
            'installed_apps': [],
            'url_patterns': [],
            'template_configs': [],
            'security_issues': [],
            'redundancies': [],
            'development_configs': [],
            'production_configs': [],
            'relationships': [],
            'console_logs': [],
            'gitignore_issues': [],
            'cors_configs': [],
            'auth_configs': [],
            'cache_configs': [],
            'logging_configs': [],
            'file_upload_configs': [],
            'session_configs': [],
            'csrf_configs': [],
            'allowed_hosts': [],
            'debug_settings': []
        }
        
        self.critical_relationships = {
            'database_models': {},
            'url_view_mappings': {},
            'template_dependencies': {},
            'static_dependencies': {},
            'middleware_dependencies': {},
            'app_dependencies': {}
        }
        
        # Patterns to detect issues
        self.sensitive_patterns = [
            r'SECRET_KEY\s*=\s*["\']([^"\']+)["\']',
            r'PASSWORD\s*=\s*["\']([^"\']+)["\']',
            r'API_KEY\s*=\s*["\']([^"\']+)["\']',
            r'TOKEN\s*=\s*["\']([^"\']+)["\']',
            r'DATABASE_URL\s*=\s*["\']([^"\']+)["\']',
            r'AWS_.*\s*=\s*["\']([^"\']+)["\']',
            r'STRIPE_.*\s*=\s*["\']([^"\']+)["\']'
        ]
        
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
        
        # Also print to console
        prefix = f"[PHASE8_{category.upper()}]"
        if level == 'error':
            print(f"❌ {prefix} {message}")
        elif level == 'warning':
            print(f"⚠️ {prefix} {message}")
        else:
            print(f"✅ {prefix} {message}")
            
    def scan_settings_files(self):
        """Deep scan of all settings files"""
        print("\n" + "="*80)
        print("🔍 SCANNING SETTINGS FILES")
        print("="*80)
        
        self.log_console("SETTINGS", "Starting deep settings scan", "info")
        
        settings_dir = self.base_path / 'primepath_project'
        settings_patterns = ['settings*.py', 'local_settings.py', 'production.py', 'development.py']
        
        for pattern in settings_patterns:
            for settings_file in settings_dir.glob(pattern):
                if settings_file.exists():
                    self.log_console("SETTINGS", f"Found: {settings_file.name}", "info")
                    self.analyze_settings_file(settings_file)
                    
        # Analyze current Django settings
        self.analyze_django_settings()
        
    def analyze_settings_file(self, file_path):
        """Analyze individual settings file"""
        relative_path = file_path.relative_to(self.base_path)
        
        print(f"\n  Analyzing: {relative_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        analysis = {
            'file': str(relative_path),
            'size': len(content),
            'lines': content.count('\n'),
            'issues': [],
            'configs': []
        }
        
        # Check for hardcoded secrets
        for pattern in self.sensitive_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                for match in matches:
                    # Don't expose actual secrets, just indicate they exist
                    if 'SECRET_KEY' in pattern and not match.startswith('os.'):
                        analysis['issues'].append({
                            'type': 'hardcoded_secret',
                            'pattern': pattern.split('\\s')[0],
                            'severity': 'high'
                        })
                        self.results['hardcoded_secrets'].append(str(relative_path))
                        self.log_console("SECURITY", f"Hardcoded secret in {relative_path}", "error")
                        
        # Check for DEBUG settings
        if 'DEBUG = True' in content or 'DEBUG=True' in content:
            analysis['issues'].append({
                'type': 'debug_enabled',
                'severity': 'medium'
            })
            self.results['debug_settings'].append(str(relative_path))
            self.log_console("CONFIG", f"DEBUG=True in {relative_path}", "warning")
            
        # Check for development configs
        dev_patterns = ['localhost', '127.0.0.1', '0.0.0.0', 'test', 'dev', 'staging']
        for pattern in dev_patterns:
            if pattern in content.lower():
                self.results['development_configs'].append({
                    'file': str(relative_path),
                    'pattern': pattern
                })
                
        # Check for database configs
        if 'DATABASES' in content:
            analysis['configs'].append('database')
            self.results['database_configs'].append(str(relative_path))
            
        # Check for static/media configs
        if 'STATIC_' in content or 'MEDIA_' in content:
            analysis['configs'].append('static_media')
            self.results['static_configs'].append(str(relative_path))
            
        # Check for CORS configs
        if 'CORS' in content:
            analysis['configs'].append('cors')
            self.results['cors_configs'].append(str(relative_path))
            
        # Check for authentication configs
        if 'AUTH_' in content or 'AUTHENTICATION_' in content:
            analysis['configs'].append('authentication')
            self.results['auth_configs'].append(str(relative_path))
            
        self.results['settings_files'].append(analysis)
        
    def analyze_django_settings(self):
        """Analyze current Django settings"""
        print("\n" + "="*80)
        print("📊 ANALYZING DJANGO CONFIGURATION")
        print("="*80)
        
        self.log_console("DJANGO", "Analyzing active Django settings", "info")
        
        # Check DEBUG mode
        if hasattr(settings, 'DEBUG'):
            if settings.DEBUG:
                self.log_console("DJANGO", "DEBUG mode is ON", "warning")
                self.results['security_issues'].append("DEBUG mode enabled in production")
            else:
                self.log_console("DJANGO", "DEBUG mode is OFF", "info")
                
        # Check SECRET_KEY
        if hasattr(settings, 'SECRET_KEY'):
            if settings.SECRET_KEY == 'your-secret-key-here' or 'insecure' in settings.SECRET_KEY:
                self.log_console("DJANGO", "Insecure SECRET_KEY detected", "error")
                self.results['security_issues'].append("Insecure SECRET_KEY")
                
        # Check ALLOWED_HOSTS
        if hasattr(settings, 'ALLOWED_HOSTS'):
            self.results['allowed_hosts'] = settings.ALLOWED_HOSTS
            if '*' in settings.ALLOWED_HOSTS:
                self.log_console("DJANGO", "ALLOWED_HOSTS contains wildcard", "warning")
                self.results['security_issues'].append("ALLOWED_HOSTS contains wildcard")
                
        # Analyze INSTALLED_APPS
        if hasattr(settings, 'INSTALLED_APPS'):
            self.results['installed_apps'] = list(settings.INSTALLED_APPS)
            
            # Check for development apps in production
            dev_apps = ['debug_toolbar', 'django_extensions', 'silk']
            for app in settings.INSTALLED_APPS:
                if any(dev_app in app for dev_app in dev_apps):
                    self.log_console("DJANGO", f"Development app in INSTALLED_APPS: {app}", "warning")
                    self.results['development_configs'].append({
                        'type': 'dev_app',
                        'app': app
                    })
                    
        # Analyze MIDDLEWARE
        if hasattr(settings, 'MIDDLEWARE'):
            self.results['middleware_analysis'] = list(settings.MIDDLEWARE)
            
            # Check middleware order and relationships
            self.analyze_middleware_relationships(settings.MIDDLEWARE)
            
        # Check database configuration
        if hasattr(settings, 'DATABASES'):
            for db_name, db_config in settings.DATABASES.items():
                if 'PASSWORD' in db_config and db_config['PASSWORD']:
                    # Don't log actual password
                    self.log_console("DATABASE", f"Database '{db_name}' has password set", "info")
                    
        # Check static and media configuration
        if hasattr(settings, 'STATIC_URL'):
            self.log_console("STATIC", f"STATIC_URL: {settings.STATIC_URL}", "info")
            
        if hasattr(settings, 'MEDIA_URL'):
            self.log_console("MEDIA", f"MEDIA_URL: {settings.MEDIA_URL}", "info")
            
        # Check session configuration
        if hasattr(settings, 'SESSION_COOKIE_SECURE'):
            if not settings.SESSION_COOKIE_SECURE and not settings.DEBUG:
                self.log_console("SESSION", "SESSION_COOKIE_SECURE is False", "warning")
                self.results['security_issues'].append("SESSION_COOKIE_SECURE is False")
                
        # Check CSRF configuration
        if hasattr(settings, 'CSRF_COOKIE_SECURE'):
            if not settings.CSRF_COOKIE_SECURE and not settings.DEBUG:
                self.log_console("CSRF", "CSRF_COOKIE_SECURE is False", "warning")
                self.results['security_issues'].append("CSRF_COOKIE_SECURE is False")
                
    def analyze_middleware_relationships(self, middleware_list):
        """Analyze middleware dependencies and order"""
        print("\n  Analyzing middleware relationships...")
        
        critical_order = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware'
        ]
        
        for i, middleware in enumerate(middleware_list):
            # Check if critical middleware is in correct order
            if middleware in critical_order:
                expected_index = critical_order.index(middleware)
                if i < expected_index:
                    self.log_console("MIDDLEWARE", f"Potential order issue: {middleware}", "warning")
                    
            # Store relationships
            self.critical_relationships['middleware_dependencies'][middleware] = {
                'position': i,
                'depends_on': middleware_list[:i] if i > 0 else []
            }
            
    def scan_environment_files(self):
        """Scan for environment variable files"""
        print("\n" + "="*80)
        print("🌍 SCANNING ENVIRONMENT FILES")
        print("="*80)
        
        self.log_console("ENV", "Scanning for environment files", "info")
        
        env_patterns = ['.env', '.env.*', '*.env', 'env.*']
        
        for pattern in env_patterns:
            for env_file in self.base_path.glob(pattern):
                if env_file.is_file():
                    self.log_console("ENV", f"Found environment file: {env_file.name}", "warning")
                    self.analyze_env_file(env_file)
                    
    def analyze_env_file(self, file_path):
        """Analyze environment file"""
        relative_path = file_path.relative_to(self.base_path)
        
        print(f"  Analyzing: {relative_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        
                        # Check for sensitive keys
                        sensitive_keys = ['SECRET', 'PASSWORD', 'KEY', 'TOKEN', 'API']
                        if any(s in key.upper() for s in sensitive_keys):
                            self.results['environment_variables'].append({
                                'file': str(relative_path),
                                'key': key,
                                'is_sensitive': True
                            })
                            self.log_console("ENV", f"Sensitive variable: {key}", "warning")
                            
        except Exception as e:
            self.log_console("ENV", f"Error reading {relative_path}: {e}", "error")
            
    def check_gitignore(self):
        """Check .gitignore for security issues"""
        print("\n" + "="*80)
        print("📝 CHECKING .GITIGNORE")
        print("="*80)
        
        self.log_console("GIT", "Checking .gitignore configuration", "info")
        
        gitignore_path = self.base_path.parent / '.gitignore'
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
                
            # Critical patterns that should be in .gitignore
            critical_patterns = [
                '*.env',
                '.env',
                'db.sqlite3',
                '*.pyc',
                '__pycache__',
                'media/',
                'staticfiles/',
                '*.log',
                'local_settings.py',
                '*.secret',
                '*.key',
                'node_modules/',
                '.vscode/',
                '.idea/',
                '*.backup',
                '*.phase*_backup'
            ]
            
            missing_patterns = []
            for pattern in critical_patterns:
                if pattern not in gitignore_content:
                    missing_patterns.append(pattern)
                    
            if missing_patterns:
                self.log_console("GIT", f"Missing {len(missing_patterns)} critical patterns", "warning")
                self.results['gitignore_issues'] = missing_patterns
            else:
                self.log_console("GIT", "All critical patterns present", "info")
                
        else:
            self.log_console("GIT", ".gitignore not found!", "error")
            self.results['gitignore_issues'].append("No .gitignore file")
            
    def map_url_view_relationships(self):
        """Map all URL to view relationships"""
        print("\n" + "="*80)
        print("🔗 MAPPING URL-VIEW RELATIONSHIPS")
        print("="*80)
        
        self.log_console("URLS", "Mapping URL patterns to views", "info")
        
        from django.urls import get_resolver
        
        resolver = get_resolver()
        
        def extract_patterns(resolver, prefix=''):
            patterns = []
            
            for pattern in resolver.url_patterns:
                if hasattr(pattern, 'url_patterns'):
                    # Namespace or include
                    namespace = getattr(pattern, 'namespace', '')
                    new_prefix = f"{prefix}{pattern.pattern}/"
                    patterns.extend(extract_patterns(pattern, new_prefix))
                else:
                    # Regular pattern
                    view_name = None
                    if hasattr(pattern.callback, '__name__'):
                        view_name = pattern.callback.__name__
                    elif hasattr(pattern.callback, 'view_class'):
                        view_name = pattern.callback.view_class.__name__
                        
                    patterns.append({
                        'pattern': f"{prefix}{pattern.pattern}",
                        'name': pattern.name,
                        'view': view_name
                    })
                    
            return patterns
            
        url_patterns = extract_patterns(resolver)
        
        # Store relationships
        for pattern in url_patterns:
            if pattern['view']:
                self.critical_relationships['url_view_mappings'][pattern['pattern']] = pattern['view']
                
        self.results['url_patterns'] = url_patterns[:20]  # Store sample
        
        print(f"  ✅ Mapped {len(url_patterns)} URL patterns")
        self.log_console("URLS", f"Found {len(url_patterns)} URL patterns", "info")
        
    def analyze_app_configurations(self):
        """Analyze all app configurations"""
        print("\n" + "="*80)
        print("📱 ANALYZING APP CONFIGURATIONS")
        print("="*80)
        
        self.log_console("APPS", "Analyzing app configurations", "info")
        
        for app_config in apps.get_app_configs():
            app_name = app_config.name
            
            # Check for app-specific settings
            app_path = Path(app_config.path)
            
            # Check for app settings.py
            app_settings = app_path / 'settings.py'
            if app_settings.exists():
                self.log_console("APPS", f"{app_name} has custom settings", "info")
                self.analyze_settings_file(app_settings)
                
            # Check for app config.py
            app_config_file = app_path / 'config.py'
            if app_config_file.exists():
                self.log_console("APPS", f"{app_name} has config file", "info")
                
            # Map app dependencies
            self.map_app_dependencies(app_config)
            
    def map_app_dependencies(self, app_config):
        """Map dependencies for an app"""
        app_name = app_config.name
        dependencies = []
        
        # Check models for foreign key relationships
        for model in app_config.get_models():
            for field in model._meta.fields:
                if hasattr(field, 'related_model') and field.related_model:
                    related_app = field.related_model._meta.app_label
                    if related_app != app_config.label:
                        dependencies.append(related_app)
                        
        self.critical_relationships['app_dependencies'][app_name] = list(set(dependencies))
        
    def check_redundancies(self):
        """Check for configuration redundancies"""
        print("\n" + "="*80)
        print("🔄 CHECKING FOR REDUNDANCIES")
        print("="*80)
        
        self.log_console("REDUNDANCY", "Checking for configuration redundancies", "info")
        
        # Check for duplicate database configs
        if len(self.results['database_configs']) > 1:
            self.log_console("REDUNDANCY", f"Multiple database configs: {len(self.results['database_configs'])}", "warning")
            self.results['redundancies'].append({
                'type': 'database_configs',
                'files': self.results['database_configs']
            })
            
        # Check for duplicate static configs
        if len(self.results['static_configs']) > 1:
            self.log_console("REDUNDANCY", f"Multiple static configs: {len(self.results['static_configs'])}", "warning")
            self.results['redundancies'].append({
                'type': 'static_configs',
                'files': self.results['static_configs']
            })
            
        # Check for conflicting settings files
        settings_files = [f['file'] for f in self.results['settings_files']]
        if 'primepath_project/settings.py' in settings_files and 'primepath_project/settings_sqlite.py' in settings_files:
            self.log_console("REDUNDANCY", "Both settings.py and settings_sqlite.py exist", "warning")
            
    def generate_monitoring_script(self):
        """Generate console monitoring for configuration changes"""
        script_content = f'''
// ===== PHASE 8 CONFIGURATION MONITORING =====
// Generated: {datetime.now().isoformat()}

console.log('%c===== PHASE 8 CONFIGURATION ANALYSIS =====', 'color: purple; font-weight: bold');

// Configuration Analysis Results
const configAnalysis = {{
    settingsFiles: {len(self.results['settings_files'])},
    environmentVariables: {len(self.results['environment_variables'])},
    securityIssues: {len(self.results['security_issues'])},
    redundancies: {len(self.results['redundancies'])},
    developmentConfigs: {len(self.results['development_configs'])},
    urlPatterns: {len(self.critical_relationships['url_view_mappings'])},
    middlewareCount: {len(self.results['middleware_analysis'])},
    installedApps: {len(self.results['installed_apps'])}
}};

console.table(configAnalysis);

// Security Check
console.log('%c===== SECURITY CONFIGURATION CHECK =====', 'color: red; font-weight: bold');

const securityStatus = {{
    debug: {'true' if any('debug_enabled' in str(s) for s in self.results['settings_files']) else 'false'},
    secretKeySecure: {'false' if self.results['hardcoded_secrets'] else 'true'},
    allowedHosts: {self.results['allowed_hosts']},
    securityIssues: {len(self.results['security_issues'])}
}};

console.table(securityStatus);

// Check critical endpoints still work
console.log('%c===== TESTING CRITICAL ENDPOINTS =====', 'color: green; font-weight: bold');

const criticalEndpoints = [
    '/api/PlacementTest/exams/',
    '/api/PlacementTest/sessions/',
    '/PlacementTest/PlacementTest/teacher/dashboard/',
    '/placement-rules/',
    '/exam-mapping/'
];

criticalEndpoints.forEach(endpoint => {{
    fetch(endpoint)
        .then(response => {{
            if (response.ok || response.status === 403) {{
                console.log(`✅ [PHASE8] ${{endpoint}}: Accessible`);
            }} else {{
                console.error(`❌ [PHASE8] ${{endpoint}}: Status ${{response.status}}`);
            }}
        }})
        .catch(error => {{
            console.error(`❌ [PHASE8] ${{endpoint}}: Failed`, error);
        }});
}});

// Monitor for configuration-related errors
window.addEventListener('error', function(e) {{
    if (e.message.includes('settings') || e.message.includes('config')) {{
        console.error('[PHASE8 CONFIG ERROR]', e.message, 'at', e.filename, ':', e.lineno);
    }}
}});

// Check if static files load correctly
const testStaticFile = '/static/js/modules/answer-manager.js';
fetch(testStaticFile)
    .then(response => {{
        if (response.ok) {{
            console.log('✅ [PHASE8] Static files serving correctly');
        }} else {{
            console.error('❌ [PHASE8] Static files issue');
        }}
    }});

console.log('%c===== PHASE 8 MONITORING ACTIVE =====', 'color: purple; font-weight: bold');
'''
        
        # Save monitoring script
        script_path = self.base_path / 'static' / 'js' / 'phase8_config_monitoring.js'
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        print(f"\n  ✅ Created: static/js/phase8_config_monitoring.js")
        
    def generate_report(self):
        """Generate comprehensive configuration report"""
        print("\n" + "="*80)
        print("📊 CONFIGURATION ANALYSIS REPORT")
        print("="*80)
        
        # Summary statistics
        print(f"\n  📋 SUMMARY:")
        print(f"     Settings Files: {len(self.results['settings_files'])}")
        print(f"     Environment Variables: {len(self.results['environment_variables'])}")
        print(f"     Security Issues: {len(self.results['security_issues'])}")
        print(f"     Hardcoded Secrets: {len(self.results['hardcoded_secrets'])}")
        print(f"     Development Configs: {len(self.results['development_configs'])}")
        print(f"     Redundancies: {len(self.results['redundancies'])}")
        print(f"     URL Patterns: {len(self.critical_relationships['url_view_mappings'])}")
        print(f"     Middleware: {len(self.results['middleware_analysis'])}")
        print(f"     Installed Apps: {len(self.results['installed_apps'])}")
        
        # Critical issues
        if self.results['security_issues']:
            print(f"\n  ⚠️ SECURITY ISSUES:")
            for issue in self.results['security_issues'][:5]:
                print(f"     - {issue}")
                
        if self.results['hardcoded_secrets']:
            print(f"\n  🔐 HARDCODED SECRETS FOUND IN:")
            for file in self.results['hardcoded_secrets'][:5]:
                print(f"     - {file}")
                
        # Relationships preserved
        print(f"\n  ✅ RELATIONSHIPS PRESERVED:")
        print(f"     URL→View Mappings: {len(self.critical_relationships['url_view_mappings'])}")
        print(f"     App Dependencies: {len(self.critical_relationships['app_dependencies'])}")
        print(f"     Middleware Order: {len(self.critical_relationships['middleware_dependencies'])}")
        
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'settings_files': len(self.results['settings_files']),
                'environment_variables': len(self.results['environment_variables']),
                'security_issues': len(self.results['security_issues']),
                'hardcoded_secrets': len(self.results['hardcoded_secrets']),
                'redundancies': len(self.results['redundancies']),
                'relationships_preserved': sum(len(v) for v in self.critical_relationships.values())
            },
            'results': self.results,
            'relationships': self.critical_relationships,
            'console_logs': self.console_logs
        }
        
        report_path = self.base_path / 'phase8_config_analysis_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"\n  💾 Detailed report saved to: phase8_config_analysis_report.json")
        
        return report
        
    def run(self):
        """Execute Phase 8 configuration analysis"""
        print("\n" + "="*80)
        print("🚀 PHASE 8: CONFIGURATION & SETTINGS ANALYSIS")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Deep configuration analysis
            self.scan_settings_files()
            self.scan_environment_files()
            self.check_gitignore()
            
            # Map relationships
            self.map_url_view_relationships()
            self.analyze_app_configurations()
            
            # Check for issues
            self.check_redundancies()
            
            # Generate monitoring
            self.generate_monitoring_script()
            
            # Generate report
            report = self.generate_report()
            
            print("\n" + "="*80)
            print("✅ PHASE 8 ANALYSIS COMPLETE")
            print("="*80)
            
            # Provide recommendations
            print("\n📌 KEY RECOMMENDATIONS:")
            
            if self.results['debug_settings']:
                print("  1. Disable DEBUG in production settings")
                
            if self.results['hardcoded_secrets']:
                print("  2. Move secrets to environment variables")
                
            if self.results['security_issues']:
                print("  3. Address security configuration issues")
                
            if self.results['redundancies']:
                print("  4. Consolidate redundant configurations")
                
            if self.results['gitignore_issues']:
                print("  5. Update .gitignore with missing patterns")
                
            return report
            
        except Exception as e:
            print(f"\n❌ ANALYSIS FAILED: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Main execution"""
    analyzer = Phase8ConfigurationAnalyzer()
    report = analyzer.run()
    
    if report:
        # Check critical issues count
        critical_count = (
            len(report['results']['security_issues']) +
            len(report['results']['hardcoded_secrets'])
        )
        
        if critical_count > 0:
            print(f"\n⚠️ Found {critical_count} critical issues that need attention")
            print("Ready to create safe cleanup implementation")
            
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())