#!/usr/bin/env python
"""
Comprehensive Cleanup Analysis
Ultra-deep analysis to identify redundant, outdated, and unnecessary files
"""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict
import hashlib
import json

class ComprehensiveCleanupAnalysis:
    def __init__(self):
        self.project_root = Path(os.path.dirname(os.path.abspath(__file__)))
        self.parent_root = self.project_root.parent
        self.findings = {
            'windows_files': [],
            'backup_files': [],
            'old_files': [],
            'test_files': [],
            'duplicate_tests': [],
            'documentation': [],
            'temporary_files': [],
            'migration_files': [],
            'analysis_files': [],
            'empty_files': [],
            'duplicate_content': defaultdict(list),
            'unused_imports': [],
            'safe_to_remove': [],
            'keep_files': [],
            'critical_files': []
        }
        
    def calculate_file_hash(self, filepath):
        """Calculate MD5 hash of file content"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def analyze_windows_specific_files(self):
        """Identify Windows-specific files"""
        print("\n🪟 ANALYZING WINDOWS-SPECIFIC FILES")
        print("=" * 60)
        
        windows_patterns = [
            '*.bat',
            '*.cmd',
            '*.ps1',
            '*windows*',
            '*win32*',
            '*win64*'
        ]
        
        for pattern in windows_patterns:
            for file in self.parent_root.rglob(pattern):
                if file.is_file():
                    rel_path = file.relative_to(self.parent_root)
                    self.findings['windows_files'].append(str(rel_path))
                    print(f"  📁 {rel_path}")
        
        print(f"\nFound {len(self.findings['windows_files'])} Windows-specific files")
    
    def analyze_backup_and_old_files(self):
        """Identify backup and old files"""
        print("\n📦 ANALYZING BACKUP AND OLD FILES")
        print("=" * 60)
        
        patterns = [
            '*_old.py',
            '*_backup.py',
            '*.bak',
            '*~',
            '*.orig',
            '*.old',
            '*_copy.py'
        ]
        
        for pattern in patterns:
            for file in self.parent_root.rglob(pattern):
                if file.is_file():
                    rel_path = file.relative_to(self.parent_root)
                    if '_old.py' in str(file):
                        self.findings['old_files'].append(str(rel_path))
                    else:
                        self.findings['backup_files'].append(str(rel_path))
                    print(f"  📄 {rel_path}")
        
        print(f"\nFound {len(self.findings['old_files'])} _old.py files")
        print(f"Found {len(self.findings['backup_files'])} other backup files")
    
    def analyze_test_files(self):
        """Analyze test files for duplicates and outdated tests"""
        print("\n🧪 ANALYZING TEST FILES")
        print("=" * 60)
        
        test_patterns = [
            'test_*.py',
            '*_test.py',
            'qa_*.py',
            '*_qa.py',
            'check_*.py',
            'verify_*.py',
            'debug_*.py',
            'final_*.py',
            'simple_*.py',
            'quick_*.py',
            'comprehensive_*.py',
            'double_check_*.py',
            'ultimate_*.py'
        ]
        
        test_file_hashes = {}
        
        for pattern in test_patterns:
            for file in self.project_root.glob(pattern):
                if file.is_file():
                    rel_path = file.relative_to(self.parent_root)
                    self.findings['test_files'].append(str(rel_path))
                    
                    # Check for duplicate content
                    file_hash = self.calculate_file_hash(file)
                    if file_hash:
                        if file_hash in test_file_hashes:
                            self.findings['duplicate_tests'].append({
                                'file1': str(test_file_hashes[file_hash]),
                                'file2': str(rel_path),
                                'hash': file_hash
                            })
                        else:
                            test_file_hashes[file_hash] = rel_path
        
        print(f"\nFound {len(self.findings['test_files'])} test files")
        print(f"Found {len(self.findings['duplicate_tests'])} duplicate test files")
        
        # Group test files by category
        test_categories = defaultdict(list)
        for test_file in self.findings['test_files']:
            if 'phase' in test_file.lower():
                test_categories['phase_tests'].append(test_file)
            elif 'feature' in test_file.lower():
                test_categories['feature_tests'].append(test_file)
            elif 'final' in test_file.lower():
                test_categories['final_tests'].append(test_file)
            elif 'qa' in test_file.lower():
                test_categories['qa_tests'].append(test_file)
            else:
                test_categories['misc_tests'].append(test_file)
        
        for category, files in test_categories.items():
            print(f"  {category}: {len(files)} files")
    
    def analyze_documentation(self):
        """Analyze documentation files"""
        print("\n📚 ANALYZING DOCUMENTATION FILES")
        print("=" * 60)
        
        doc_patterns = ['*.md', '*.txt', '*.rst', '*.doc', '*.docx']
        
        for pattern in doc_patterns:
            for file in self.parent_root.rglob(pattern):
                if file.is_file():
                    rel_path = file.relative_to(self.parent_root)
                    self.findings['documentation'].append(str(rel_path))
        
        print(f"\nFound {len(self.findings['documentation'])} documentation files")
        
        # Categorize documentation
        doc_categories = defaultdict(list)
        for doc in self.findings['documentation']:
            doc_lower = doc.lower()
            if 'phase' in doc_lower:
                doc_categories['phase_docs'].append(doc)
            elif 'complete' in doc_lower or 'success' in doc_lower:
                doc_categories['completion_docs'].append(doc)
            elif 'fix' in doc_lower or 'report' in doc_lower:
                doc_categories['fix_reports'].append(doc)
            elif 'analysis' in doc_lower or 'verification' in doc_lower:
                doc_categories['analysis_docs'].append(doc)
            elif 'windows' in doc_lower or 'mac' in doc_lower or 'migration' in doc_lower:
                doc_categories['migration_docs'].append(doc)
            else:
                doc_categories['other_docs'].append(doc)
        
        for category, files in doc_categories.items():
            print(f"  {category}: {len(files)} files")
    
    def analyze_temporary_files(self):
        """Identify temporary and cache files"""
        print("\n🗑️ ANALYZING TEMPORARY FILES")
        print("=" * 60)
        
        temp_patterns = [
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.DS_Store',
            'Thumbs.db',
            '*.log',
            '*.tmp',
            '*.temp',
            '*.cache',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
            '*.swp',
            '*.swo',
            '*~'
        ]
        
        for pattern in temp_patterns:
            for file in self.parent_root.rglob(pattern):
                rel_path = file.relative_to(self.parent_root)
                self.findings['temporary_files'].append(str(rel_path))
        
        print(f"\nFound {len(self.findings['temporary_files'])} temporary files/directories")
    
    def analyze_migration_and_analysis_files(self):
        """Identify migration and analysis files"""
        print("\n🔄 ANALYZING MIGRATION AND ANALYSIS FILES")
        print("=" * 60)
        
        # Migration files
        migration_patterns = [
            '*migration*.py',
            '*migrate*.py',
            'prepare_*.py',
        ]
        
        for pattern in migration_patterns:
            for file in self.parent_root.rglob(pattern):
                if file.is_file() and 'migrations' not in str(file):
                    rel_path = file.relative_to(self.parent_root)
                    self.findings['migration_files'].append(str(rel_path))
                    print(f"  📋 Migration: {rel_path}")
        
        # Analysis files
        analysis_patterns = [
            '*analysis*.py',
            '*analyze*.py',
            'comprehensive_*.py',
        ]
        
        for pattern in analysis_patterns:
            for file in self.parent_root.rglob(pattern):
                if file.is_file() and str(file) not in self.findings['test_files']:
                    rel_path = file.relative_to(self.parent_root)
                    self.findings['analysis_files'].append(str(rel_path))
                    print(f"  📊 Analysis: {rel_path}")
        
        print(f"\nFound {len(self.findings['migration_files'])} migration files")
        print(f"Found {len(self.findings['analysis_files'])} analysis files")
    
    def analyze_empty_files(self):
        """Identify empty or near-empty files"""
        print("\n📭 ANALYZING EMPTY FILES")
        print("=" * 60)
        
        for file in self.parent_root.rglob('*'):
            if file.is_file():
                try:
                    size = file.stat().st_size
                    if size == 0:
                        rel_path = file.relative_to(self.parent_root)
                        if '__init__.py' not in str(file):  # Keep __init__.py files
                            self.findings['empty_files'].append(str(rel_path))
                            print(f"  🔲 {rel_path}")
                except:
                    pass
        
        print(f"\nFound {len(self.findings['empty_files'])} empty files")
    
    def identify_critical_files(self):
        """Identify files that must NOT be deleted"""
        print("\n⚠️ IDENTIFYING CRITICAL FILES")
        print("=" * 60)
        
        critical_patterns = [
            'manage.py',
            'settings*.py',
            'wsgi.py',
            'asgi.py',
            '__init__.py',
            'requirements*.txt',
            'pyproject.toml',
            'db.sqlite3',
            'models.py',
            'views.py',
            'urls.py',
            'admin.py',
            'apps.py',
            'forms.py',
            'serializers.py',
            '*.html',
            '*.css',
            '*.js',
            'CLAUDE.md',  # Important project instructions
        ]
        
        # Also keep all files in these directories
        critical_dirs = [
            'migrations',
            'templates',
            'static',
            'media',
            'fixtures',
            'models',
            'views',
            'services',
            'management/commands',
        ]
        
        for pattern in critical_patterns:
            for file in self.parent_root.rglob(pattern):
                if file.is_file():
                    rel_path = str(file.relative_to(self.parent_root))
                    self.findings['critical_files'].append(rel_path)
        
        for dir_pattern in critical_dirs:
            for file in self.parent_root.rglob(f'*{dir_pattern}/*'):
                if file.is_file():
                    rel_path = str(file.relative_to(self.parent_root))
                    if rel_path not in self.findings['critical_files']:
                        self.findings['critical_files'].append(rel_path)
        
        print(f"Identified {len(self.findings['critical_files'])} critical files")
    
    def determine_safe_to_remove(self):
        """Determine which files are safe to remove"""
        print("\n✅ DETERMINING SAFE-TO-REMOVE FILES")
        print("=" * 60)
        
        # Files that are definitely safe to remove
        safe_patterns = {
            'windows_files': self.findings['windows_files'],
            'old_files': self.findings['old_files'],
            'backup_files': self.findings['backup_files'],
            'temporary_files': self.findings['temporary_files'],
            'empty_files': self.findings['empty_files'],
        }
        
        # Add outdated test files
        outdated_test_patterns = [
            'test_phase[1-9]_*.py',  # Old phase tests
            'final_*.py',  # Final test iterations
            'double_check*.py',  # Double check iterations
            'quick_test*.py',  # Quick test iterations
            'simple_*.py',  # Simple test iterations
        ]
        
        for pattern in outdated_test_patterns:
            for file in self.project_root.glob(pattern):
                rel_path = str(file.relative_to(self.parent_root))
                if rel_path not in self.findings['critical_files']:
                    self.findings['safe_to_remove'].append(rel_path)
        
        # Add files from safe categories
        for category, files in safe_patterns.items():
            for file in files:
                if file not in self.findings['critical_files']:
                    if file not in self.findings['safe_to_remove']:
                        self.findings['safe_to_remove'].append(file)
        
        # Add duplicate test files (keep one, remove others)
        for dup in self.findings['duplicate_tests']:
            if dup['file2'] not in self.findings['critical_files']:
                if dup['file2'] not in self.findings['safe_to_remove']:
                    self.findings['safe_to_remove'].append(dup['file2'])
        
        # Remove Django migration files from safe_to_remove
        self.findings['safe_to_remove'] = [
            f for f in self.findings['safe_to_remove'] 
            if 'migrations/0' not in f
        ]
        
        print(f"\nIdentified {len(self.findings['safe_to_remove'])} files safe to remove")
        
        # Show breakdown
        categories_count = defaultdict(int)
        for file in self.findings['safe_to_remove']:
            if '.bat' in file or '.cmd' in file:
                categories_count['Windows files'] += 1
            elif '_old.py' in file:
                categories_count['Old Python files'] += 1
            elif 'test_' in file or '_test.py' in file:
                categories_count['Test files'] += 1
            elif '.pyc' in file or '__pycache__' in file:
                categories_count['Python cache'] += 1
            elif '.md' in file:
                categories_count['Documentation'] += 1
            else:
                categories_count['Other'] += 1
        
        for category, count in categories_count.items():
            print(f"  {category}: {count}")
    
    def run_comprehensive_analysis(self):
        """Run all analysis steps"""
        print("=" * 80)
        print("COMPREHENSIVE CLEANUP ANALYSIS")
        print("Ultra-deep analysis of project structure")
        print("=" * 80)
        
        # Run all analyses
        self.analyze_windows_specific_files()
        self.analyze_backup_and_old_files()
        self.analyze_test_files()
        self.analyze_documentation()
        self.analyze_temporary_files()
        self.analyze_migration_and_analysis_files()
        self.analyze_empty_files()
        self.identify_critical_files()
        self.determine_safe_to_remove()
        
        # Save findings to JSON
        findings_file = self.project_root / 'cleanup_findings.json'
        with open(findings_file, 'w') as f:
            # Convert all Path objects to strings for JSON serialization
            json_findings = {}
            for key, value in self.findings.items():
                if isinstance(value, list):
                    json_findings[key] = [str(v) if not isinstance(v, dict) else v for v in value]
                else:
                    json_findings[key] = value
            json.dump(json_findings, f, indent=2)
        
        print(f"\n💾 Findings saved to: {findings_file}")
        
        # Summary
        print("\n" + "=" * 80)
        print("CLEANUP ANALYSIS SUMMARY")
        print("=" * 80)
        
        total_files_analyzed = sum(len(v) if isinstance(v, list) else 0 for v in self.findings.values())
        print(f"\n📊 Total files analyzed: {total_files_analyzed}")
        print(f"✅ Files safe to remove: {len(self.findings['safe_to_remove'])}")
        print(f"⚠️  Critical files to keep: {len(self.findings['critical_files'])}")
        
        # Calculate potential space savings
        total_size = 0
        for file_path in self.findings['safe_to_remove']:
            try:
                full_path = self.parent_root / file_path
                if full_path.exists():
                    total_size += full_path.stat().st_size
            except:
                pass
        
        size_mb = total_size / (1024 * 1024)
        print(f"\n💾 Potential space savings: {size_mb:.2f} MB")
        
        print("\n🎯 RECOMMENDATION:")
        print("1. Review cleanup_findings.json")
        print("2. Create a backup before cleanup")
        print("3. Run cleanup_execute.py to remove files")
        print("4. Test all features after cleanup")
        
        return self.findings


if __name__ == "__main__":
    analyzer = ComprehensiveCleanupAnalysis()
    findings = analyzer.run_comprehensive_analysis()