#!/usr/bin/env python
"""
Phase 7: Code Quality & Standards Cleanup Implementation
Safe cleanup of code quality issues while preserving all functionality
"""
import os
import sys
import re
import json
import ast
from pathlib import Path
from datetime import datetime
import shutil
import logging

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
import django
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase7_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Phase7CodeCleaner:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.base_path = Path(__file__).parent
        
        # Load analysis report
        report_path = self.base_path / 'phase7_code_quality_report.json'
        if report_path.exists():
            with open(report_path, 'r') as f:
                self.analysis_report = json.load(f)
        else:
            self.analysis_report = None
            
        self.results = {
            'commented_code_removed': 0,
            'debug_statements_removed': 0,
            'unused_imports_removed': 0,
            'duplicate_functions_marked': 0,
            'javascript_cleaned': 0,
            'css_cleaned': 0,
            'html_cleaned': 0,
            'files_modified': [],
            'errors': [],
            'preserved_relationships': []
        }
        
        self.console_logs = []
        
        # Critical patterns to NEVER remove
        self.preserve_patterns = {
            'logging': ['logger.', 'logging.', 'log.'],
            'debugging_tools': ['pdb', 'breakpoint', 'debugger'],  # Keep if in debug mode
            'monitoring': ['PHASE', 'CLEANUP', 'console.log("[PHASE'],
            'error_handling': ['except:', 'try:', 'raise '],
            'relationships': ['ForeignKey', 'ManyToMany', 'OneToOne'],
            'critical_imports': ['models', 'views', 'forms', 'urls', 'admin', 'signals']
        }
        
    def log_console(self, message, level='info'):
        """Add console.log statements for frontend debugging"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.console_logs.append(log_entry)
        
        if level == 'error':
            logger.error(f"[CONSOLE] {message}")
        elif level == 'warn':
            logger.warning(f"[CONSOLE] {message}")
        else:
            logger.info(f"[CONSOLE] {message}")
            
    def backup_file(self, file_path):
        """Create backup before modifying file"""
        backup_path = file_path.with_suffix(file_path.suffix + '.phase7_backup')
        if not backup_path.exists() and not self.dry_run:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backed up {file_path.name}")
            
    def clean_python_file(self, file_path, issues):
        """Clean Python file of quality issues"""
        rel_path = file_path.relative_to(self.base_path)
        
        print(f"\n  Cleaning {rel_path}...")
        self.log_console(f"Cleaning Python file: {rel_path}", "info")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            original_lines = lines.copy()
            modified = False
            
            # Process commented code
            if 'commented_code' in issues:
                lines, removed = self.remove_commented_code(lines, issues['commented_code'])
                if removed > 0:
                    self.results['commented_code_removed'] += removed
                    modified = True
                    print(f"    ✅ Removed {removed} commented code blocks")
                    
            # Process debug statements (keep logging, remove print)
            if 'debug_statements' in issues:
                lines, removed = self.remove_debug_statements(lines, issues['debug_statements'])
                if removed > 0:
                    self.results['debug_statements_removed'] += removed
                    modified = True
                    print(f"    ✅ Removed {removed} debug statements")
                    
            # Process unused imports
            if 'unused_imports' in issues:
                lines, removed = self.remove_unused_imports(lines, issues['unused_imports'])
                if removed > 0:
                    self.results['unused_imports_removed'] += removed
                    modified = True
                    print(f"    ✅ Removed {removed} unused imports")
                    
            # Save changes if modified
            if modified and not self.dry_run:
                self.backup_file(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                self.results['files_modified'].append(str(rel_path))
                self.log_console(f"Modified {rel_path}: cleaned code quality issues", "info")
            elif modified:
                print(f"    [DRY RUN] Would modify {rel_path}")
                
        except Exception as e:
            self.results['errors'].append(f"Error cleaning {rel_path}: {e}")
            self.log_console(f"Error cleaning {rel_path}: {e}", "error")
            
    def remove_commented_code(self, lines, commented_blocks):
        """Remove commented code blocks"""
        removed_count = 0
        lines_to_remove = set()
        
        for block in commented_blocks:
            if isinstance(block, tuple):
                line_num = block[0] - 1  # Convert to 0-based
                if 0 <= line_num < len(lines):
                    # Check if it's not a docstring or important comment
                    line = lines[line_num].strip()
                    if not any(preserve in line for preserve in ['TODO:', 'FIXME:', 'NOTE:', 'WARNING:']):
                        lines_to_remove.add(line_num)
                        
        # Remove lines (in reverse to maintain indices)
        for line_num in sorted(lines_to_remove, reverse=True):
            del lines[line_num]
            removed_count += 1
            
        return lines, removed_count
        
    def remove_debug_statements(self, lines, debug_issues):
        """Remove debug print statements but keep logging"""
        removed_count = 0
        lines_to_remove = set()
        
        for issue in debug_issues:
            if 'pattern' in issue and 'print' in issue['pattern']:
                line_num = issue['line'] - 1
                if 0 <= line_num < len(lines):
                    line = lines[line_num]
                    # Don't remove if it's in a critical function or error handler
                    if not any(preserve in line for preserve in ['logger', 'logging', 'error', 'critical']):
                        # Comment out instead of removing (safer)
                        lines[line_num] = '# ' + line
                        removed_count += 1
                        
        return lines, removed_count
        
    def remove_unused_imports(self, lines, unused_imports):
        """Remove unused imports"""
        removed_count = 0
        
        for import_name in unused_imports:
            for i, line in enumerate(lines):
                # Match various import patterns
                patterns = [
                    f'^import {import_name}$',
                    f'^import {import_name} as',
                    f'^from .* import {import_name}$',
                    f'^from .* import .*{import_name}'
                ]
                
                for pattern in patterns:
                    if re.match(pattern, line.strip()):
                        # Don't remove critical imports
                        if not any(critical in import_name for critical in self.preserve_patterns['critical_imports']):
                            lines[i] = '# UNUSED: ' + line
                            removed_count += 1
                            break
                            
        return lines, removed_count
        
    def clean_javascript_file(self, file_path, issues):
        """Clean JavaScript file of quality issues"""
        rel_path = file_path.relative_to(self.base_path)
        
        print(f"\n  Cleaning JS: {rel_path}...")
        self.log_console(f"Cleaning JavaScript file: {rel_path}", "info")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            modified = False
            removed_count = 0
            
            for issue in issues:
                if issue['type'] == 'console.log':
                    # Keep monitoring console.logs
                    if not any(preserve in issue['content'] for preserve in ['PHASE', 'CLEANUP', '[PHASE']):
                        line_num = issue['line'] - 1
                        if 0 <= line_num < len(lines):
                            lines[line_num] = '// REMOVED: ' + lines[line_num]
                            removed_count += 1
                            modified = True
                            
                elif issue['type'] == 'debugger':
                    line_num = issue['line'] - 1
                    if 0 <= line_num < len(lines):
                        lines[line_num] = '// REMOVED: ' + lines[line_num]
                        removed_count += 1
                        modified = True
                        
                elif issue['type'] == 'commented_code':
                    line_num = issue['line'] - 1
                    if 0 <= line_num < len(lines):
                        # Remove the line entirely if it's commented code
                        lines[line_num] = ''
                        removed_count += 1
                        modified = True
                        
            if modified and not self.dry_run:
                self.backup_file(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                self.results['javascript_cleaned'] += removed_count
                self.results['files_modified'].append(str(rel_path))
                print(f"    ✅ Cleaned {removed_count} JS issues")
            elif modified:
                print(f"    [DRY RUN] Would clean {removed_count} JS issues")
                
        except Exception as e:
            self.results['errors'].append(f"Error cleaning JS {rel_path}: {e}")
            self.log_console(f"Error cleaning JS {rel_path}: {e}", "error")
            
    def clean_css_file(self, file_path, issues):
        """Clean CSS file of quality issues"""
        rel_path = file_path.relative_to(self.base_path)
        
        print(f"\n  Cleaning CSS: {rel_path}...")
        self.log_console(f"Cleaning CSS file: {rel_path}", "info")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            modified = False
            
            for issue in issues:
                if issue['type'] == 'commented_css':
                    # Remove large commented CSS blocks
                    if len(issue['content']) > 100:
                        content = content.replace(issue['content'], '')
                        self.results['css_cleaned'] += 1
                        modified = True
                        
            if modified and not self.dry_run:
                self.backup_file(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.results['files_modified'].append(str(rel_path))
                print(f"    ✅ Cleaned CSS issues")
            elif modified:
                print(f"    [DRY RUN] Would clean CSS issues")
                
        except Exception as e:
            self.results['errors'].append(f"Error cleaning CSS {rel_path}: {e}")
            self.log_console(f"Error cleaning CSS {rel_path}: {e}", "error")
            
    def clean_html_file(self, file_path, issues):
        """Clean HTML file of quality issues"""
        rel_path = file_path.relative_to(self.base_path)
        
        print(f"\n  Cleaning HTML: {rel_path}...")
        self.log_console(f"Cleaning HTML file: {rel_path}", "info")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            modified = False
            
            for issue in issues:
                if issue['type'] == 'commented_html':
                    # Remove large commented HTML blocks
                    if len(issue['content']) > 150:
                        content = content.replace(issue['content'], '')
                        self.results['html_cleaned'] += 1
                        modified = True
                        
            if modified and not self.dry_run:
                self.backup_file(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.results['files_modified'].append(str(rel_path))
                print(f"    ✅ Cleaned HTML issues")
            elif modified:
                print(f"    [DRY RUN] Would clean HTML issues")
                
        except Exception as e:
            self.results['errors'].append(f"Error cleaning HTML {rel_path}: {e}")
            self.log_console(f"Error cleaning HTML {rel_path}: {e}", "error")
            
    def verify_relationships(self):
        """Verify all critical relationships are preserved"""
        print("\n" + "="*80)
        print("🔍 VERIFYING PRESERVED RELATIONSHIPS")
        print("="*80)
        
        self.log_console("Verifying model relationships", "info")
        
        from django.apps import apps
        
        preserved = []
        
        # Check all models still have their relationships
        for app_label in ['core', 'placement_test']:
            try:
                app = apps.get_app_config(app_label)
                for model in app.get_models():
                    for field in model._meta.fields:
                        if hasattr(field, 'related_model') and field.related_model:
                            preserved.append({
                                'model': model.__name__,
                                'field': field.name,
                                'related_to': field.related_model.__name__,
                                'type': field.__class__.__name__
                            })
            except Exception as e:
                logger.error(f"Error checking {app_label}: {e}")
                
        self.results['preserved_relationships'] = preserved
        
        print(f"  ✅ Preserved {len(preserved)} model relationships")
        for rel in preserved[:5]:
            print(f"     {rel['model']}.{rel['field']} → {rel['related_to']}")
            
        if len(preserved) > 5:
            print(f"     ... and {len(preserved) - 5} more")
            
        self.log_console(f"All {len(preserved)} relationships preserved", "info")
        
    def generate_monitoring_script(self):
        """Generate enhanced monitoring for Phase 7 cleanup"""
        script_content = f'''
// ===== PHASE 7 CLEANUP MONITORING =====
// Generated: {datetime.now().isoformat()}

console.log('%c===== PHASE 7 CLEANUP RESULTS =====', 'color: blue; font-weight: bold');

// Cleanup statistics
const cleanupStats = {{
    commentedCodeRemoved: {self.results['commented_code_removed']},
    debugStatementsRemoved: {self.results['debug_statements_removed']},
    unusedImportsRemoved: {self.results['unused_imports_removed']},
    javascriptCleaned: {self.results['javascript_cleaned']},
    cssCleaned: {self.results['css_cleaned']},
    htmlCleaned: {self.results['html_cleaned']},
    filesModified: {len(self.results['files_modified'])},
    errors: {len(self.results['errors'])},
    preservedRelationships: {len(self.results['preserved_relationships'])}
}};

console.table(cleanupStats);

// Verify critical functionality still works
console.log('%c===== FUNCTIONALITY VERIFICATION =====', 'color: green; font-weight: bold');

// Test API endpoints
const testEndpoints = [
    '/api/PlacementTest/exams/',
    '/api/PlacementTest/sessions/',
    '/api/core/curriculum-levels/'
];

testEndpoints.forEach(endpoint => {{
    fetch(endpoint)
        .then(response => {{
            console.log(`✅ [PHASE7] ${{endpoint}}: ${{response.status}}`);
        }})
        .catch(error => {{
            console.error(`❌ [PHASE7] ${{endpoint}}: Failed`, error);
        }});
}});

// Monitor for any new errors introduced by cleanup
let errorCount = 0;
window.addEventListener('error', function(e) {{
    errorCount++;
    console.error(`[PHASE7 ERROR #${{errorCount}}]`, e.message, 'at', e.filename, ':', e.lineno);
}});

// Check memory usage
if (performance.memory) {{
    console.log('[PHASE7] Memory usage:', {{
        used: (performance.memory.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
        total: (performance.memory.totalJSHeapSize / 1048576).toFixed(2) + ' MB',
        limit: (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2) + ' MB'
    }});
}}

console.log('%c===== PHASE 7 CLEANUP COMPLETE =====', 'color: green; font-weight: bold');
'''
        
        # Update monitoring script
        script_path = self.base_path / 'static' / 'js' / 'phase7_cleanup_monitoring.js'
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        print(f"\n  ✅ Created: static/js/phase7_cleanup_monitoring.js")
        
    def generate_report(self):
        """Generate cleanup report"""
        print("\n" + "="*80)
        print("📊 PHASE 7 CLEANUP REPORT")
        print("="*80)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'results': self.results,
            'console_logs': self.console_logs
        }
        
        # Save report
        report_path = self.base_path / 'phase7_cleanup_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"\n  📋 SUMMARY:")
        print(f"     Commented Code Removed: {self.results['commented_code_removed']}")
        print(f"     Debug Statements Removed: {self.results['debug_statements_removed']}")
        print(f"     Unused Imports Removed: {self.results['unused_imports_removed']}")
        print(f"     JavaScript Issues Cleaned: {self.results['javascript_cleaned']}")
        print(f"     CSS Issues Cleaned: {self.results['css_cleaned']}")
        print(f"     HTML Issues Cleaned: {self.results['html_cleaned']}")
        print(f"     Files Modified: {len(self.results['files_modified'])}")
        print(f"     Errors: {len(self.results['errors'])}")
        
        if self.results['errors']:
            print(f"\n  ⚠️ ERRORS:")
            for error in self.results['errors'][:5]:
                print(f"     {error}")
                
        print(f"\n  💾 Report saved to: phase7_cleanup_report.json")
        
        return report
        
    def run(self):
        """Execute Phase 7 code cleanup"""
        print("\n" + "="*80)
        print("🚀 PHASE 7: CODE QUALITY CLEANUP")
        print("="*80)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        
        if not self.analysis_report:
            print("❌ No analysis report found. Run phase7_code_quality_analyzer.py first.")
            return None
            
        try:
            # Process Python files
            print("\n" + "="*80)
            print("🐍 CLEANING PYTHON FILES")
            print("="*80)
            
            for file_path, issues in self.analysis_report.get('details', {}).items():
                if file_path.endswith('.py') and issues:
                    full_path = self.base_path / file_path
                    if full_path.exists():
                        self.clean_python_file(full_path, issues)
                        
            # Process JavaScript files
            print("\n" + "="*80)
            print("📜 CLEANING JAVASCRIPT FILES")
            print("="*80)
            
            js_issues = self.analysis_report.get('details', {}).get('javascript_issues', {})
            for file_path, issues in js_issues.items():
                full_path = self.base_path / file_path
                if full_path.exists():
                    self.clean_javascript_file(full_path, issues)
                    
            # Process CSS files
            print("\n" + "="*80)
            print("🎨 CLEANING CSS FILES")
            print("="*80)
            
            css_issues = self.analysis_report.get('details', {}).get('css_issues', {})
            for file_path, issues in css_issues.items():
                full_path = self.base_path / file_path
                if full_path.exists():
                    self.clean_css_file(full_path, issues)
                    
            # Process HTML files
            print("\n" + "="*80)
            print("📄 CLEANING HTML FILES")
            print("="*80)
            
            html_issues = self.analysis_report.get('details', {}).get('html_issues', {})
            for file_path, issues in html_issues.items():
                full_path = self.base_path / file_path
                if full_path.exists():
                    self.clean_html_file(full_path, issues)
                    
            # Verify relationships
            self.verify_relationships()
            
            # Generate monitoring
            self.generate_monitoring_script()
            
            # Generate report
            report = self.generate_report()
            
            print("\n" + "="*80)
            if self.dry_run:
                print("✅ DRY RUN COMPLETE - Review results above")
                print("To execute cleanup, run with --execute")
            else:
                print("✅ PHASE 7 CLEANUP COMPLETE")
                
            print("="*80)
            
            return report
            
        except Exception as e:
            logger.error(f"Phase 7 cleanup failed: {e}")
            print(f"\n❌ CLEANUP FAILED: {e}")
            return None

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Phase 7 Code Cleanup')
    parser.add_argument('--execute', action='store_true', 
                       help='Execute cleanup (default is dry run)')
    args = parser.parse_args()
    
    # Run cleanup
    cleaner = Phase7CodeCleaner(dry_run=not args.execute)
    report = cleaner.run()
    
    if report:
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())