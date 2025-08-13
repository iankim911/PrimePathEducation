#!/usr/bin/env python
"""
Phase 7: Code Quality & Standards Analysis
Ultra-deep analysis of code quality issues across entire codebase
"""
import os
import sys
import re
import ast
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
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
        logging.FileHandler('phase7_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CodeQualityAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.apps = ['core', 'placement_test', 'api', 'common']
        
        self.analysis = {
            'commented_code': defaultdict(list),
            'unused_imports': defaultdict(list),
            'debug_statements': defaultdict(list),
            'naming_issues': defaultdict(list),
            'duplicate_functions': defaultdict(list),
            'long_functions': defaultdict(list),
            'complex_functions': defaultdict(list),
            'javascript_issues': defaultdict(list),
            'css_issues': defaultdict(list),
            'html_issues': defaultdict(list),
            'relationships': defaultdict(list),
            'dependencies': defaultdict(set),
            'critical_patterns': [],
            'console_logs': []
        }
        
        # Critical patterns to preserve
        self.critical_imports = {
            'models', 'views', 'forms', 'serializers', 'urls', 
            'admin', 'apps', 'signals', 'middleware', 'decorators'
        }
        
        # Standard naming conventions
        self.naming_conventions = {
            'class': re.compile(r'^[A-Z][a-zA-Z0-9]*$'),  # PascalCase
            'function': re.compile(r'^[a-z_][a-z0-9_]*$'),  # snake_case
            'constant': re.compile(r'^[A-Z][A-Z0-9_]*$'),  # UPPER_SNAKE_CASE
            'variable': re.compile(r'^[a-z_][a-z0-9_]*$'),  # snake_case
        }
        
    def analyze_python_file(self, file_path):
        """Comprehensive analysis of a Python file"""
        rel_path = file_path.relative_to(self.base_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Parse AST for detailed analysis
            try:
                tree = ast.parse(content)
                self.analyze_ast(tree, file_path, content)
            except SyntaxError as e:
                logger.warning(f"Syntax error in {rel_path}: {e}")
                
            # Line-by-line analysis
            self.analyze_lines(lines, file_path)
            
            # Pattern analysis
            self.analyze_patterns(content, file_path)
            
            # Relationship analysis
            self.analyze_relationships(content, file_path)
            
        except Exception as e:
            logger.error(f"Error analyzing {rel_path}: {e}")
            
    def analyze_ast(self, tree, file_path, content):
        """Analyze Abstract Syntax Tree for code quality issues"""
        rel_path = file_path.relative_to(self.base_path)
        
        class CodeVisitor(ast.NodeVisitor):
            def __init__(self, analyzer):
                self.analyzer = analyzer
                self.imports = set()
                self.used_names = set()
                self.functions = []
                self.classes = []
                
            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.add(alias.name)
                self.generic_visit(node)
                
            def visit_ImportFrom(self, node):
                if node.module:
                    for alias in node.names:
                        if alias.name != '*':
                            self.imports.add(f"{node.module}.{alias.name}")
                self.generic_visit(node)
                
            def visit_Name(self, node):
                self.used_names.add(node.id)
                self.generic_visit(node)
                
            def visit_FunctionDef(self, node):
                self.functions.append({
                    'name': node.name,
                    'lines': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0,
                    'complexity': self.calculate_complexity(node)
                })
                
                # Check naming convention
                if not self.analyzer.naming_conventions['function'].match(node.name):
                    if not node.name.startswith('test_'):  # Allow test_ prefix
                        self.analyzer.analysis['naming_issues'][str(rel_path)].append({
                            'type': 'function',
                            'name': node.name,
                            'line': node.lineno,
                            'expected': 'snake_case'
                        })
                
                self.generic_visit(node)
                
            def visit_ClassDef(self, node):
                self.classes.append({
                    'name': node.name,
                    'lines': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                })
                
                # Check naming convention
                if not self.analyzer.naming_conventions['class'].match(node.name):
                    self.analyzer.analysis['naming_issues'][str(rel_path)].append({
                        'type': 'class',
                        'name': node.name,
                        'line': node.lineno,
                        'expected': 'PascalCase'
                    })
                
                self.generic_visit(node)
                
            def calculate_complexity(self, node):
                """Calculate cyclomatic complexity"""
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                return complexity
                
        visitor = CodeVisitor(self)
        visitor.visit(tree)
        
        # Check for unused imports
        for imp in visitor.imports:
            imp_name = imp.split('.')[-1]
            if imp_name not in content and imp_name not in str(visitor.used_names):
                # Don't flag critical imports
                if not any(critical in imp.lower() for critical in self.critical_imports):
                    self.analysis['unused_imports'][str(rel_path)].append(imp)
                    
        # Check for long functions
        for func in visitor.functions:
            if func['lines'] > 50:
                self.analysis['long_functions'][str(rel_path)].append({
                    'name': func['name'],
                    'lines': func['lines']
                })
                
            # Check for complex functions
            if func['complexity'] > 10:
                self.analysis['complex_functions'][str(rel_path)].append({
                    'name': func['name'],
                    'complexity': func['complexity']
                })
                
    def analyze_lines(self, lines, file_path):
        """Line-by-line analysis for specific patterns"""
        rel_path = file_path.relative_to(self.base_path)
        
        in_multiline_comment = False
        multiline_comment_start = 0
        consecutive_comments = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for multiline comments
            if '"""' in line or "'''" in line:
                if not in_multiline_comment:
                    in_multiline_comment = True
                    multiline_comment_start = i
                else:
                    in_multiline_comment = False
                    
            # Check for commented code (not docstrings)
            if stripped.startswith('#') and not in_multiline_comment:
                # Heuristic: if it contains Python keywords, likely commented code
                if any(keyword in stripped for keyword in 
                      ['def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ', 
                       'return ', 'print(', '= ', '()', '.']):
                    consecutive_comments.append((i, stripped))
                else:
                    # If we have consecutive comments, check if they're code
                    if len(consecutive_comments) > 2:
                        self.analysis['commented_code'][str(rel_path)].extend(consecutive_comments)
                    consecutive_comments = []
            else:
                if len(consecutive_comments) > 2:
                    self.analysis['commented_code'][str(rel_path)].extend(consecutive_comments)
                consecutive_comments = []
                
            # Check for debug statements
            debug_patterns = [
                r'\bprint\s*\(',
                r'\bconsole\.log\s*\(',
                r'\bdebugger\b',
                r'\bpdb\.set_trace\(',
                r'\bbreakpoint\(',
                r'#\s*TODO(?!:)',  # TODO without colon (likely temporary)
                r'#\s*FIXME',
                r'#\s*HACK',
                r'#\s*XXX',
                r'#\s*DEBUG'
            ]
            
            for pattern in debug_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.analysis['debug_statements'][str(rel_path)].append({
                        'line': i,
                        'content': stripped[:100],
                        'pattern': pattern
                    })
                    
    def analyze_patterns(self, content, file_path):
        """Analyze code patterns and potential duplications"""
        rel_path = file_path.relative_to(self.base_path)
        
        # Find potential duplicate patterns
        function_pattern = re.compile(r'def\s+(\w+)\s*\([^)]*\):')
        functions = function_pattern.findall(content)
        
        # Check for similar function names (potential duplicates)
        for i, func1 in enumerate(functions):
            for func2 in functions[i+1:]:
                if self.similar_names(func1, func2):
                    self.analysis['duplicate_functions'][str(rel_path)].append({
                        'func1': func1,
                        'func2': func2,
                        'similarity': 'high'
                    })
                    
    def analyze_relationships(self, content, file_path):
        """Analyze and preserve critical relationships"""
        rel_path = file_path.relative_to(self.base_path)
        
        # Find model relationships
        if 'models' in str(rel_path):
            foreign_keys = re.findall(r'ForeignKey\([\'"]([^\'")]+)[\'"]', content)
            many_to_many = re.findall(r'ManyToManyField\([\'"]([^\'")]+)[\'"]', content)
            one_to_one = re.findall(r'OneToOneField\([\'"]([^\'")]+)[\'"]', content)
            
            if foreign_keys or many_to_many or one_to_one:
                self.analysis['relationships'][str(rel_path)] = {
                    'foreign_keys': foreign_keys,
                    'many_to_many': many_to_many,
                    'one_to_one': one_to_one
                }
                
        # Find view dependencies
        if 'views' in str(rel_path):
            model_imports = re.findall(r'from\s+[\w.]+models\s+import\s+([^;\n]+)', content)
            form_imports = re.findall(r'from\s+[\w.]+forms\s+import\s+([^;\n]+)', content)
            
            if model_imports or form_imports:
                self.analysis['dependencies'][str(rel_path)].update(model_imports)
                self.analysis['dependencies'][str(rel_path)].update(form_imports)
                
    def analyze_javascript_files(self):
        """Analyze JavaScript files for quality issues"""
        print("\n" + "="*80)
        print("📜 ANALYZING JAVASCRIPT FILES")
        print("="*80)
        
        js_files = list(self.base_path.rglob('*.js'))
        js_files = [f for f in js_files if 'node_modules' not in str(f) and 'vendor' not in str(f)]
        
        for js_file in js_files:
            rel_path = js_file.relative_to(self.base_path)
            
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                issues = []
                
                # Check for console.log statements (except our monitoring)
                for i, line in enumerate(lines, 1):
                    if 'console.log' in line and 'PHASE' not in line and 'CLEANUP' not in line:
                        issues.append({
                            'type': 'console.log',
                            'line': i,
                            'content': line.strip()[:100]
                        })
                        
                    # Check for debugger statements
                    if 'debugger' in line:
                        issues.append({
                            'type': 'debugger',
                            'line': i,
                            'content': line.strip()[:100]
                        })
                        
                    # Check for TODO comments
                    if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                        issues.append({
                            'type': 'todo_comment',
                            'line': i,
                            'content': line.strip()[:100]
                        })
                        
                    # Check for commented code
                    if line.strip().startswith('//') and any(pattern in line for pattern in 
                        ['function', 'var ', 'let ', 'const ', 'if (', 'for (', 'return ']):
                        issues.append({
                            'type': 'commented_code',
                            'line': i,
                            'content': line.strip()[:100]
                        })
                        
                if issues:
                    self.analysis['javascript_issues'][str(rel_path)] = issues
                    
            except Exception as e:
                logger.error(f"Error analyzing JS file {rel_path}: {e}")
                
    def analyze_css_files(self):
        """Analyze CSS files for quality issues"""
        print("\n" + "="*80)
        print("🎨 ANALYZING CSS FILES")
        print("="*80)
        
        css_files = list(self.base_path.rglob('*.css'))
        css_files = [f for f in css_files if 'vendor' not in str(f) and 'admin' not in str(f)]
        
        for css_file in css_files:
            rel_path = css_file.relative_to(self.base_path)
            
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                issues = []
                
                # Check for commented code blocks
                commented_blocks = re.findall(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', content)
                for block in commented_blocks:
                    if any(pattern in block for pattern in ['{', '}', ':', ';']) and len(block) > 50:
                        issues.append({
                            'type': 'commented_css',
                            'content': block[:100] + '...' if len(block) > 100 else block
                        })
                        
                # Check for !important overuse
                important_count = content.count('!important')
                if important_count > 10:
                    issues.append({
                        'type': 'important_overuse',
                        'count': important_count
                    })
                    
                # Check for duplicate selectors
                selectors = re.findall(r'^([^{]+)\s*{', content, re.MULTILINE)
                selector_counts = Counter(selectors)
                duplicates = {k: v for k, v in selector_counts.items() if v > 1}
                
                if duplicates:
                    issues.append({
                        'type': 'duplicate_selectors',
                        'duplicates': duplicates
                    })
                    
                if issues:
                    self.analysis['css_issues'][str(rel_path)] = issues
                    
            except Exception as e:
                logger.error(f"Error analyzing CSS file {rel_path}: {e}")
                
    def analyze_html_templates(self):
        """Analyze HTML templates for quality issues"""
        print("\n" + "="*80)
        print("📄 ANALYZING HTML TEMPLATES")
        print("="*80)
        
        html_files = list(self.base_path.rglob('*.html'))
        
        for html_file in html_files:
            rel_path = html_file.relative_to(self.base_path)
            
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                issues = []
                
                # Check for commented HTML (potential old code)
                html_comments = re.findall(r'<!--[\s\S]*?-->', content)
                for comment in html_comments:
                    # Check if it contains actual HTML tags (not just text comments)
                    if any(tag in comment for tag in ['<div', '<span', '<input', '<button', '<form']):
                        issues.append({
                            'type': 'commented_html',
                            'content': comment[:100] + '...' if len(comment) > 100 else comment
                        })
                        
                # Check for inline styles (should be in CSS)
                inline_styles = re.findall(r'style="[^"]*"', content)
                if len(inline_styles) > 5:  # Allow some inline styles
                    issues.append({
                        'type': 'excessive_inline_styles',
                        'count': len(inline_styles)
                    })
                    
                # Check for inline JavaScript (should be in JS files)
                inline_js = re.findall(r'on\w+="[^"]*"', content)
                if inline_js:
                    issues.append({
                        'type': 'inline_javascript',
                        'count': len(inline_js),
                        'examples': inline_js[:3]
                    })
                    
                if issues:
                    self.analysis['html_issues'][str(rel_path)] = issues
                    
            except Exception as e:
                logger.error(f"Error analyzing HTML file {rel_path}: {e}")
                
    def similar_names(self, name1, name2):
        """Check if two names are similar (potential duplicates)"""
        # Simple similarity check
        if name1 == name2:
            return False  # Exact match handled elsewhere
            
        # Check if one contains the other
        if name1 in name2 or name2 in name1:
            return True
            
        # Check if they differ only by suffix
        common_suffixes = ['_old', '_new', '_temp', '_backup', '2', '_copy']
        for suffix in common_suffixes:
            if name1 + suffix == name2 or name2 + suffix == name1:
                return True
                
        return False
        
    def generate_report(self):
        """Generate comprehensive code quality report"""
        print("\n" + "="*80)
        print("📊 CODE QUALITY ANALYSIS REPORT")
        print("="*80)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'files_analyzed': 0,
                'total_issues': 0,
                'critical_relationships_preserved': len(self.analysis['relationships']),
                'by_category': {}
            },
            'details': {}
        }
        
        # Count issues by category
        categories = [
            'commented_code', 'unused_imports', 'debug_statements', 
            'naming_issues', 'duplicate_functions', 'long_functions',
            'complex_functions', 'javascript_issues', 'css_issues', 'html_issues'
        ]
        
        for category in categories:
            count = sum(len(issues) for issues in self.analysis[category].values())
            report['summary']['by_category'][category] = count
            report['summary']['total_issues'] += count
            
            if count > 0:
                print(f"\n  📌 {category.replace('_', ' ').title()}: {count} issues")
                
                # Show samples
                for file_path, issues in list(self.analysis[category].items())[:3]:
                    if issues:
                        print(f"     - {file_path}: {len(issues)} issues")
                        
        # Add detailed issues to report
        report['details'] = {
            category: dict(self.analysis[category]) 
            for category in categories
        }
        
        # Add relationships to preserve
        report['preserve'] = {
            'relationships': dict(self.analysis['relationships']),
            'dependencies': {k: list(v) for k, v in self.analysis['dependencies'].items()}
        }
        
        # Save report
        report_path = self.base_path / 'phase7_code_quality_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"\n  💾 Detailed report saved to: phase7_code_quality_report.json")
        
        # Generate console monitoring script
        self.generate_console_script(report)
        
        return report
        
    def generate_console_script(self, report):
        """Generate JavaScript console monitoring for Phase 7"""
        print("\n  🔍 Generating console monitoring script...")
        
        script_content = f'''
// ===== PHASE 7 CODE QUALITY MONITORING =====
// Generated: {datetime.now().isoformat()}

console.log('%c===== PHASE 7 CODE QUALITY ANALYSIS =====', 'color: blue; font-weight: bold');

// Analysis Summary
const codeQualityReport = {{
    totalIssues: {report['summary']['total_issues']},
    filesAnalyzed: {report['summary']['files_analyzed']},
    categories: {json.dumps(report['summary']['by_category'])},
    criticalRelationshipsPreserved: {report['summary']['critical_relationships_preserved']}
}};

console.table(codeQualityReport.categories);

// Monitor for runtime errors that might be caused by cleanup
const originalError = window.onerror;
window.onerror = function(msg, url, lineNo, columnNo, error) {{
    console.error('[PHASE7] Runtime error detected:', {{
        message: msg,
        source: url,
        line: lineNo,
        column: columnNo,
        error: error
    }});
    
    // Call original handler if exists
    if (originalError) {{
        return originalError.apply(this, arguments);
    }}
    return false;
}};

// Monitor for unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {{
    console.error('[PHASE7] Unhandled promise rejection:', {{
        reason: event.reason,
        promise: event.promise
    }});
}});

// Check critical functionality
console.log('%c===== VERIFYING CRITICAL FEATURES =====', 'color: green; font-weight: bold');

// Check if key modules are loaded
const criticalModules = [
    'answerManager',
    'pdfViewer', 
    'timer',
    'navigationModule'
];

criticalModules.forEach(module => {{
    if (typeof window[module] !== 'undefined') {{
        console.log(`✅ [PHASE7] ${{module}} loaded successfully`);
    }} else {{
        console.warn(`⚠️ [PHASE7] ${{module}} not found (check if needed on this page)`);
    }}
}});

// Monitor API performance
const originalFetch = window.fetch;
window.fetch = function(...args) {{
    const startTime = performance.now();
    
    return originalFetch.apply(this, args).then(response => {{
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        if (duration > 1000) {{
            console.warn(`[PHASE7] Slow API call detected: ${{args[0]}} took ${{duration.toFixed(2)}}ms`);
        }}
        
        return response;
    }});
}};

// Check for memory leaks
let lastHeapSize = 0;
if (performance.memory) {{
    setInterval(() => {{
        const currentHeapSize = performance.memory.usedJSHeapSize;
        const heapGrowth = currentHeapSize - lastHeapSize;
        
        if (heapGrowth > 10000000) {{ // 10MB growth
            console.warn('[PHASE7] Potential memory leak detected: Heap grew by', 
                        (heapGrowth / 1000000).toFixed(2), 'MB');
        }}
        
        lastHeapSize = currentHeapSize;
    }}, 30000); // Check every 30 seconds
}}

console.log('%c===== PHASE 7 MONITORING ACTIVE =====', 'color: green; font-weight: bold');
'''
        
        # Save monitoring script
        script_path = self.base_path / 'static' / 'js' / 'phase7_monitoring.js'
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        print(f"     ✅ Created: static/js/phase7_monitoring.js")
        
    def run_analysis(self):
        """Run complete code quality analysis"""
        print("\n" + "="*80)
        print("🚀 PHASE 7: CODE QUALITY & STANDARDS ANALYSIS")
        print("="*80)
        print("Performing ultra-deep code quality analysis...")
        
        # Analyze Python files
        print("\n" + "="*80)
        print("🐍 ANALYZING PYTHON FILES")
        print("="*80)
        
        python_files = []
        for app in self.apps:
            app_path = self.base_path / app
            if app_path.exists():
                python_files.extend(app_path.rglob('*.py'))
                
        # Add project settings
        project_path = self.base_path / 'primepath_project'
        if project_path.exists():
            python_files.extend(project_path.rglob('*.py'))
            
        # Filter out migrations and __pycache__
        python_files = [
            f for f in python_files 
            if 'migrations' not in str(f) and '__pycache__' not in str(f)
        ]
        
        print(f"  Found {len(python_files)} Python files to analyze")
        
        for py_file in python_files:
            self.analyze_python_file(py_file)
            
        # Analyze JavaScript files
        self.analyze_javascript_files()
        
        # Analyze CSS files
        self.analyze_css_files()
        
        # Analyze HTML templates
        self.analyze_html_templates()
        
        # Generate report
        report = self.generate_report()
        
        print("\n" + "="*80)
        print("✅ PHASE 7 ANALYSIS COMPLETE")
        print("="*80)
        
        return report

def main():
    """Main execution"""
    analyzer = CodeQualityAnalyzer()
    report = analyzer.run_analysis()
    
    print("\nNext steps:")
    print("1. Review phase7_code_quality_report.json")
    print("2. Run phase7_code_cleanup_implementation.py to fix issues")
    print("3. Verify all functionality remains intact")
    
    return 0 if report else 1

if __name__ == "__main__":
    sys.exit(main())