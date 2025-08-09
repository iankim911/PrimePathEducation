#!/usr/bin/env python
"""
Comprehensive Technical Debt Analysis
Identifies code smells, anti-patterns, performance issues, and maintenance concerns
"""

import os
import sys
import django
import json
import re
from collections import defaultdict
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection
from django.db.models import Count, Q, F
from placement_test.models import Question, Exam, StudentSession, StudentAnswer
from core.models import PlacementRule, CurriculumLevel


class TechnicalDebtAnalyzer:
    def __init__(self):
        self.debt_items = []
        self.severity_levels = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': []
        }
    
    def add_debt(self, severity, category, description, location=None, recommendation=None):
        """Add a technical debt item."""
        item = {
            'severity': severity,
            'category': category,
            'description': description,
            'location': location,
            'recommendation': recommendation
        }
        self.debt_items.append(item)
        self.severity_levels[severity].append(item)
    
    def analyze_all(self):
        """Run all analysis checks."""
        print("\n" + "="*80)
        print("TECHNICAL DEBT ANALYSIS")
        print("="*80)
        
        # Run all checks
        self.check_database_consistency()
        self.check_code_duplication()
        self.check_performance_issues()
        self.check_error_handling()
        self.check_security_concerns()
        self.check_maintainability()
        self.check_test_coverage()
        self.check_documentation()
        self.check_dependencies()
        self.check_naming_conventions()
        
        # Generate report
        self.generate_report()
    
    def check_database_consistency(self):
        """Check for database inconsistencies and integrity issues."""
        print("\n[1] DATABASE CONSISTENCY CHECK")
        print("-"*40)
        
        # Check for inconsistent data formats
        questions = Question.objects.all()
        
        # 1. Mixed separator formats
        mixed_separators = questions.filter(
            Q(correct_answer__contains=',') & Q(correct_answer__contains='|')
        ).exclude(question_type='MIXED')
        
        if mixed_separators.exists():
            self.add_debt(
                'HIGH',
                'Data Consistency',
                f'{mixed_separators.count()} questions have both comma and pipe separators',
                'Database: Question.correct_answer',
                'Standardize separator format or create migration to clean data'
            )
            print(f"  ⚠️ Found {mixed_separators.count()} questions with mixed separators")
        
        # 2. Options count vs actual answer mismatch
        for q in questions.filter(options_count__gt=0)[:100]:
            if q.correct_answer and q.question_type == 'MCQ':
                # Check if answer letters exceed options
                answers = q.correct_answer.replace(' ', '').split(',') if ',' in q.correct_answer else [q.correct_answer]
                for answer in answers:
                    if answer and answer.isalpha():
                        answer_index = ord(answer.upper()) - ord('A')
                        if answer_index >= q.options_count:
                            self.add_debt(
                                'MEDIUM',
                                'Data Integrity',
                                f'Question {q.id}: answer "{answer}" exceeds options_count={q.options_count}',
                                f'Question ID: {q.id}',
                                'Add validation to prevent invalid answer letters'
                            )
                            print(f"  ⚠️ Q{q.id}: Answer '{answer}' exceeds options_count")
                            break
        
        # 3. MIXED questions with inconsistent JSON
        mixed_questions = Question.objects.filter(question_type='MIXED')
        for mq in mixed_questions:
            if mq.correct_answer:
                try:
                    parsed = json.loads(mq.correct_answer)
                    if not isinstance(parsed, list):
                        self.add_debt(
                            'HIGH',
                            'Data Structure',
                            f'MIXED question {mq.id} has non-list JSON structure',
                            f'Question ID: {mq.id}',
                            'Standardize MIXED question JSON format'
                        )
                except json.JSONDecodeError:
                    self.add_debt(
                        'CRITICAL',
                        'Data Corruption',
                        f'MIXED question {mq.id} has invalid JSON in correct_answer',
                        f'Question ID: {mq.id}',
                        'Fix corrupted JSON data immediately'
                    )
                    print(f"  ❌ Q{mq.id}: Invalid JSON in MIXED question")
        
        # 4. Orphaned records
        orphan_answers = StudentAnswer.objects.filter(
            Q(session__isnull=True) | Q(question__isnull=True)
        )
        if orphan_answers.exists():
            self.add_debt(
                'MEDIUM',
                'Data Integrity',
                f'{orphan_answers.count()} orphaned StudentAnswer records',
                'Database: StudentAnswer',
                'Add cascade delete or periodic cleanup'
            )
        
        print("  ✓ Database consistency check complete")
    
    def check_code_duplication(self):
        """Check for duplicated code patterns."""
        print("\n[2] CODE DUPLICATION CHECK")
        print("-"*40)
        
        # Check template filters
        template_dir = Path('placement_test/templatetags/')
        if template_dir.exists():
            grade_tags = template_dir / 'grade_tags.py'
            if grade_tags.exists():
                content = grade_tags.read_text()
                
                # Check for repeated patterns
                if content.count('options_count') > 20:
                    self.add_debt(
                        'MEDIUM',
                        'Code Duplication',
                        'Excessive repetition of options_count checks in template filters',
                        'grade_tags.py',
                        'Extract common logic into helper functions'
                    )
                    print(f"  ⚠️ Repeated options_count pattern in filters")
                
                # Check for similar filter functions
                if 'has_multiple_answers' in content and 'get_answer_letters' in content:
                    # These functions likely share logic
                    self.add_debt(
                        'LOW',
                        'Code Duplication',
                        'Similar logic in has_multiple_answers and get_answer_letters',
                        'grade_tags.py',
                        'Consider consolidating common logic'
                    )
        
        # Check for duplicated template sections
        student_test = Path('templates/placement_test/student_test.html')
        if student_test.exists():
            content = student_test.read_text()
            
            # Count similar input patterns
            text_input_count = content.count('type="text"')
            checkbox_count = content.count('type="checkbox"')
            
            if text_input_count > 50:  # Arbitrary threshold
                self.add_debt(
                    'LOW',
                    'Template Duplication',
                    'Excessive input element repetition in template',
                    'student_test.html',
                    'Consider using template includes or macros'
                )
        
        print("  ✓ Code duplication check complete")
    
    def check_performance_issues(self):
        """Check for performance problems."""
        print("\n[3] PERFORMANCE CHECK")
        print("-"*40)
        
        # 1. N+1 query problems
        with connection.cursor() as cursor:
            # Check for missing select_related/prefetch_related
            cursor.execute("""
                SELECT COUNT(*) FROM placement_test_question 
                WHERE exam_id IS NOT NULL
            """)
            question_count = cursor.fetchone()[0]
            
            if question_count > 1000:
                self.add_debt(
                    'HIGH',
                    'Performance',
                    f'Large question table ({question_count} rows) needs optimization',
                    'Database queries',
                    'Add select_related() and prefetch_related() to views'
                )
                print(f"  ⚠️ Large dataset: {question_count} questions")
        
        # 2. Missing database indexes
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type = 'index' AND tbl_name = 'placement_test_question'
            """)
            indexes = cursor.fetchall()
            
            # Check for specific needed indexes
            index_names = [idx[0] for idx in indexes]
            needed_indexes = ['question_type', 'options_count', 'exam_id']
            
            for field in needed_indexes:
                if not any(field in idx for idx in index_names):
                    self.add_debt(
                        'MEDIUM',
                        'Performance',
                        f'Missing index on Question.{field}',
                        'Database',
                        f'Add index on {field} field for better query performance'
                    )
                    print(f"  ⚠️ Missing index on {field}")
        
        # 3. Large JSON parsing in templates
        mixed_with_large_json = Question.objects.filter(
            question_type='MIXED'
        ).extra(where=["LENGTH(correct_answer) > 500"])
        
        if mixed_with_large_json.exists():
            self.add_debt(
                'MEDIUM',
                'Performance',
                f'{mixed_with_large_json.count()} MIXED questions with large JSON',
                'Template rendering',
                'Consider caching parsed JSON or preprocessing'
            )
        
        print("  ✓ Performance check complete")
    
    def check_error_handling(self):
        """Check for proper error handling."""
        print("\n[4] ERROR HANDLING CHECK")
        print("-"*40)
        
        # Check Python files for bare exceptions
        py_files = Path('.').rglob('*.py')
        bare_except_count = 0
        
        for py_file in py_files:
            if 'venv' not in str(py_file) and 'migrations' not in str(py_file):
                try:
                    content = py_file.read_text()
                    if 'except:' in content:
                        bare_except_count += content.count('except:')
                        self.add_debt(
                            'MEDIUM',
                            'Error Handling',
                            f'Bare except clause in {py_file.name}',
                            str(py_file),
                            'Use specific exception types'
                        )
                except:
                    pass
        
        if bare_except_count > 0:
            print(f"  ⚠️ Found {bare_except_count} bare except clauses")
        
        # Check for silent failures in template filters
        grade_tags = Path('placement_test/templatetags/grade_tags.py')
        if grade_tags.exists():
            content = grade_tags.read_text()
            if 'except:' in content and 'pass' in content:
                self.add_debt(
                    'HIGH',
                    'Error Handling',
                    'Silent exception handling in template filters',
                    'grade_tags.py',
                    'Log exceptions or return meaningful defaults'
                )
                print("  ⚠️ Silent failures in template filters")
        
        print("  ✓ Error handling check complete")
    
    def check_security_concerns(self):
        """Check for security issues."""
        print("\n[5] SECURITY CHECK")
        print("-"*40)
        
        # 1. Check for SQL injection risks
        py_files = Path('.').rglob('*.py')
        raw_sql_count = 0
        
        for py_file in py_files:
            if 'venv' not in str(py_file) and 'migrations' not in str(py_file):
                try:
                    content = py_file.read_text()
                    if '.raw(' in content or 'cursor.execute' in content:
                        raw_sql_count += 1
                        if '%s' not in content:  # Check for parameterized queries
                            self.add_debt(
                                'CRITICAL',
                                'Security',
                                f'Potential SQL injection in {py_file.name}',
                                str(py_file),
                                'Use parameterized queries or ORM'
                            )
                except:
                    pass
        
        if raw_sql_count > 0:
            print(f"  ⚠️ Found {raw_sql_count} files with raw SQL")
        
        # 2. Check for XSS vulnerabilities
        template_files = Path('templates').rglob('*.html')
        unsafe_output_count = 0
        
        for template in template_files:
            try:
                content = template.read_text()
                if '|safe' in content or 'autoescape off' in content:
                    unsafe_output_count += 1
                    self.add_debt(
                        'HIGH',
                        'Security',
                        f'Unsafe output in {template.name}',
                        str(template),
                        'Validate that |safe is necessary and input is sanitized'
                    )
            except:
                pass
        
        if unsafe_output_count > 0:
            print(f"  ⚠️ Found {unsafe_output_count} templates with unsafe output")
        
        # 3. Check for hardcoded secrets
        settings_file = Path('primepath_project/settings_sqlite.py')
        if settings_file.exists():
            content = settings_file.read_text()
            if 'SECRET_KEY' in content and 'django-insecure' in content:
                self.add_debt(
                    'HIGH',
                    'Security',
                    'Hardcoded SECRET_KEY in settings',
                    'settings_sqlite.py',
                    'Use environment variables for secrets'
                )
                print("  ⚠️ Hardcoded SECRET_KEY found")
        
        print("  ✓ Security check complete")
    
    def check_maintainability(self):
        """Check code maintainability issues."""
        print("\n[6] MAINTAINABILITY CHECK")
        print("-"*40)
        
        # 1. Check for overly complex functions
        grade_tags = Path('placement_test/templatetags/grade_tags.py')
        if grade_tags.exists():
            content = grade_tags.read_text()
            
            # Check get_mixed_components complexity
            if 'get_mixed_components' in content:
                function_start = content.find('def get_mixed_components')
                function_end = content.find('\ndef ', function_start + 1)
                if function_end == -1:
                    function_end = len(content)
                
                function_content = content[function_start:function_end]
                line_count = function_content.count('\n')
                
                if line_count > 50:
                    self.add_debt(
                        'MEDIUM',
                        'Maintainability',
                        f'get_mixed_components function too complex ({line_count} lines)',
                        'grade_tags.py',
                        'Break down into smaller functions'
                    )
                    print(f"  ⚠️ Complex function: get_mixed_components ({line_count} lines)")
        
        # 2. Check for magic numbers/strings
        if grade_tags.exists():
            content = grade_tags.read_text()
            magic_strings = ['ABCDEFGHIJ', 'Short Answer', 'Multiple Choice']
            
            for magic in magic_strings:
                if content.count(magic) > 2:
                    self.add_debt(
                        'LOW',
                        'Maintainability',
                        f'Magic string "{magic}" repeated multiple times',
                        'grade_tags.py',
                        'Define as constants'
                    )
        
        # 3. Check for inconsistent naming
        inconsistent_models = []
        
        # Check if model fields follow conventions
        from django.apps import apps
        for model in apps.get_models():
            for field in model._meta.fields:
                if '_' in field.name and field.name != field.name.lower():
                    inconsistent_models.append(f'{model.__name__}.{field.name}')
        
        if inconsistent_models:
            self.add_debt(
                'LOW',
                'Maintainability',
                f'Inconsistent field naming in {len(inconsistent_models)} models',
                'Models',
                'Follow Python naming conventions (snake_case)'
            )
        
        print("  ✓ Maintainability check complete")
    
    def check_test_coverage(self):
        """Check test coverage and quality."""
        print("\n[7] TEST COVERAGE CHECK")
        print("-"*40)
        
        # Count test files
        test_files = list(Path('.').rglob('test_*.py'))
        test_count = len(test_files)
        
        print(f"  Found {test_count} test files")
        
        # Check for untested critical functions
        critical_functions = [
            'has_multiple_answers',
            'get_answer_letters',
            'get_mixed_components',
            'grade_mcq_answer',
            'grade_short_answer'
        ]
        
        tested_functions = set()
        for test_file in test_files:
            try:
                content = test_file.read_text()
                for func in critical_functions:
                    if func in content:
                        tested_functions.add(func)
            except:
                pass
        
        untested = set(critical_functions) - tested_functions
        if untested:
            self.add_debt(
                'HIGH',
                'Testing',
                f'Critical functions without tests: {", ".join(untested)}',
                'Test coverage',
                'Add unit tests for critical functions'
            )
            print(f"  ⚠️ Untested functions: {untested}")
        
        # Check for test quality
        if test_count < 10:
            self.add_debt(
                'HIGH',
                'Testing',
                f'Insufficient test coverage ({test_count} test files)',
                'Test suite',
                'Add comprehensive unit and integration tests'
            )
        
        print("  ✓ Test coverage check complete")
    
    def check_documentation(self):
        """Check documentation quality."""
        print("\n[8] DOCUMENTATION CHECK")
        print("-"*40)
        
        # Check for missing docstrings
        py_files = list(Path('.').rglob('*.py'))
        files_without_docstrings = 0
        
        for py_file in py_files[:20]:  # Sample check
            if 'venv' not in str(py_file) and 'migrations' not in str(py_file):
                try:
                    content = py_file.read_text()
                    if 'def ' in content and '"""' not in content:
                        files_without_docstrings += 1
                except:
                    pass
        
        if files_without_docstrings > 5:
            self.add_debt(
                'MEDIUM',
                'Documentation',
                f'{files_without_docstrings} Python files lack docstrings',
                'Python files',
                'Add docstrings to all functions and classes'
            )
            print(f"  ⚠️ {files_without_docstrings} files lack docstrings")
        
        # Check for README
        if not Path('README.md').exists():
            self.add_debt(
                'HIGH',
                'Documentation',
                'Missing README.md file',
                'Project root',
                'Add comprehensive README with setup instructions'
            )
            print("  ⚠️ Missing README.md")
        
        print("  ✓ Documentation check complete")
    
    def check_dependencies(self):
        """Check dependency issues."""
        print("\n[9] DEPENDENCY CHECK")
        print("-"*40)
        
        requirements = Path('requirements.txt')
        if requirements.exists():
            content = requirements.read_text()
            lines = content.strip().split('\n')
            
            # Check for version pinning
            unpinned = [line for line in lines if line and '==' not in line and '#' not in line]
            if unpinned:
                self.add_debt(
                    'MEDIUM',
                    'Dependencies',
                    f'{len(unpinned)} unpinned dependencies',
                    'requirements.txt',
                    'Pin all dependency versions for reproducibility'
                )
                print(f"  ⚠️ {len(unpinned)} unpinned dependencies")
            
            # Check for outdated Django
            if 'Django==' in content:
                django_line = [l for l in lines if l.startswith('Django==')][0]
                version = django_line.split('==')[1].split('.')[0]
                if int(version) < 4:
                    self.add_debt(
                        'MEDIUM',
                        'Dependencies',
                        f'Using Django {django_line.split("==")[1]} (outdated)',
                        'requirements.txt',
                        'Consider upgrading to Django 4.x or 5.x'
                    )
        
        print("  ✓ Dependency check complete")
    
    def check_naming_conventions(self):
        """Check naming convention consistency."""
        print("\n[10] NAMING CONVENTIONS CHECK")
        print("-"*40)
        
        issues = []
        
        # Check model naming
        from django.apps import apps
        for model in apps.get_models():
            # Check for inconsistent model names
            if '_' in model.__name__:
                issues.append(f'Model {model.__name__} uses underscores')
                self.add_debt(
                    'LOW',
                    'Naming',
                    f'Model {model.__name__} should use CamelCase',
                    f'{model.__module__}',
                    'Follow Django model naming conventions'
                )
        
        # Check URL patterns
        urls_file = Path('placement_test/urls.py')
        if urls_file.exists():
            content = urls_file.read_text()
            if 'student_test' in content and 'student-test' in content:
                self.add_debt(
                    'LOW',
                    'Naming',
                    'Inconsistent URL naming (underscore vs hyphen)',
                    'urls.py',
                    'Standardize URL naming convention'
                )
                print("  ⚠️ Inconsistent URL naming")
        
        if issues:
            print(f"  ⚠️ Found {len(issues)} naming issues")
        
        print("  ✓ Naming conventions check complete")
    
    def generate_report(self):
        """Generate final technical debt report."""
        print("\n" + "="*80)
        print("TECHNICAL DEBT REPORT")
        print("="*80)
        
        # Summary by severity
        print("\n📊 DEBT SUMMARY BY SEVERITY:")
        print(f"  🔴 CRITICAL: {len(self.severity_levels['CRITICAL'])} issues")
        print(f"  🟠 HIGH: {len(self.severity_levels['HIGH'])} issues")
        print(f"  🟡 MEDIUM: {len(self.severity_levels['MEDIUM'])} issues")
        print(f"  🟢 LOW: {len(self.severity_levels['LOW'])} issues")
        print(f"  📋 TOTAL: {len(self.debt_items)} issues")
        
        # Summary by category
        categories = defaultdict(list)
        for item in self.debt_items:
            categories[item['category']].append(item)
        
        print("\n📂 DEBT BY CATEGORY:")
        for category, items in sorted(categories.items()):
            print(f"  • {category}: {len(items)} issues")
        
        # Critical issues detail
        if self.severity_levels['CRITICAL']:
            print("\n🚨 CRITICAL ISSUES (Immediate Action Required):")
            for item in self.severity_levels['CRITICAL']:
                print(f"\n  Issue: {item['description']}")
                if item['location']:
                    print(f"  Location: {item['location']}")
                if item['recommendation']:
                    print(f"  Fix: {item['recommendation']}")
        
        # High priority issues
        if self.severity_levels['HIGH']:
            print("\n⚠️ HIGH PRIORITY ISSUES:")
            for item in self.severity_levels['HIGH'][:5]:  # Show top 5
                print(f"\n  Issue: {item['description']}")
                if item['recommendation']:
                    print(f"  Fix: {item['recommendation']}")
        
        # Recommendations
        print("\n💡 TOP RECOMMENDATIONS:")
        print("  1. Address all CRITICAL security issues immediately")
        print("  2. Standardize data formats (separators, JSON structure)")
        print("  3. Add comprehensive error handling and logging")
        print("  4. Improve test coverage for critical functions")
        print("  5. Document complex business logic")
        print("  6. Refactor complex functions for better maintainability")
        print("  7. Add performance monitoring and optimization")
        
        # Technical debt score
        score = self.calculate_debt_score()
        print(f"\n📈 TECHNICAL DEBT SCORE: {score}/100")
        
        if score >= 80:
            print("  ✅ Excellent - Minimal technical debt")
        elif score >= 60:
            print("  ⚠️ Good - Some debt but manageable")
        elif score >= 40:
            print("  🟠 Fair - Significant debt requiring attention")
        else:
            print("  🔴 Poor - Critical debt affecting maintainability")
        
        return score
    
    def calculate_debt_score(self):
        """Calculate overall technical debt score (0-100, higher is better)."""
        base_score = 100
        
        # Deduct points based on severity
        deductions = {
            'CRITICAL': 15,
            'HIGH': 8,
            'MEDIUM': 4,
            'LOW': 1
        }
        
        for severity, items in self.severity_levels.items():
            base_score -= len(items) * deductions[severity]
        
        # Ensure score doesn't go below 0
        return max(0, base_score)


if __name__ == "__main__":
    analyzer = TechnicalDebtAnalyzer()
    analyzer.analyze_all()
    
    score = analyzer.calculate_debt_score()
    
    # Exit with appropriate code
    if score < 40:
        sys.exit(1)  # High debt
    else:
        sys.exit(0)  # Acceptable debt