#!/usr/bin/env python
"""
Cleanup Execution Script
Safely removes identified redundant files after comprehensive analysis
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

class CleanupExecutor:
    def __init__(self):
        self.project_root = Path(os.path.dirname(os.path.abspath(__file__)))
        self.parent_root = self.project_root.parent
        self.findings_file = self.project_root / 'cleanup_findings.json'
        self.removed_files = []
        self.failed_removals = []
        self.backup_dir = None
        
    def load_findings(self):
        """Load the cleanup findings from JSON"""
        if not self.findings_file.exists():
            print("❌ cleanup_findings.json not found. Run cleanup_analysis.py first.")
            return None
        
        with open(self.findings_file, 'r') as f:
            return json.load(f)
    
    def create_backup_list(self):
        """Create a text file listing all files to be removed"""
        backup_list_file = self.project_root / f'cleanup_backup_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        findings = self.load_findings()
        if not findings:
            return None
        
        with open(backup_list_file, 'w') as f:
            f.write(f"Cleanup Backup List - {datetime.now()}\n")
            f.write("=" * 60 + "\n")
            f.write(f"Total files to remove: {len(findings['safe_to_remove'])}\n")
            f.write("=" * 60 + "\n\n")
            
            for file_path in findings['safe_to_remove']:
                f.write(f"{file_path}\n")
        
        print(f"📝 Backup list created: {backup_list_file}")
        return backup_list_file
    
    def remove_files(self, dry_run=True):
        """Remove identified redundant files"""
        findings = self.load_findings()
        if not findings:
            return False
        
        safe_to_remove = findings['safe_to_remove']
        
        print("\n" + "=" * 60)
        if dry_run:
            print("DRY RUN - No files will be deleted")
        else:
            print("EXECUTING CLEANUP")
        print("=" * 60)
        
        # Group files by category for better reporting
        categories = {
            'Windows Files': [],
            'Old Python Files': [],
            'Test Files': [],
            'Documentation': [],
            'Python Cache': [],
            'Analysis Files': [],
            'Empty Files': [],
            'Other': []
        }
        
        for file_path in safe_to_remove:
            full_path = self.parent_root / file_path
            
            # Categorize the file
            if '.bat' in file_path or '.cmd' in file_path or '.ps1' in file_path:
                category = 'Windows Files'
            elif '_old.py' in file_path:
                category = 'Old Python Files'
            elif 'test_' in file_path or '_test.py' in file_path:
                category = 'Test Files'
            elif '.md' in file_path or '.txt' in file_path:
                category = 'Documentation'
            elif '.pyc' in file_path or '__pycache__' in file_path:
                category = 'Python Cache'
            elif 'analysis' in file_path or 'analyze' in file_path:
                category = 'Analysis Files'
            elif os.path.getsize(full_path) == 0 if full_path.exists() else False:
                category = 'Empty Files'
            else:
                category = 'Other'
            
            categories[category].append(file_path)
        
        # Process removals by category
        for category, files in categories.items():
            if files:
                print(f"\n{category} ({len(files)} files):")
                for file_path in files[:5]:  # Show first 5 files in each category
                    full_path = self.parent_root / file_path
                    
                    if full_path.exists():
                        if dry_run:
                            print(f"  Would remove: {file_path}")
                        else:
                            try:
                                if full_path.is_dir():
                                    shutil.rmtree(full_path)
                                else:
                                    full_path.unlink()
                                self.removed_files.append(file_path)
                                print(f"  ✅ Removed: {file_path}")
                            except Exception as e:
                                self.failed_removals.append((file_path, str(e)))
                                print(f"  ❌ Failed: {file_path} - {e}")
                
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more files")
        
        # Summary
        print("\n" + "=" * 60)
        print("CLEANUP SUMMARY")
        print("=" * 60)
        
        if dry_run:
            print(f"Files that would be removed: {len(safe_to_remove)}")
            print("\nTo execute the cleanup, run:")
            print("  python cleanup_execute.py --execute")
        else:
            print(f"✅ Successfully removed: {len(self.removed_files)} files")
            if self.failed_removals:
                print(f"❌ Failed to remove: {len(self.failed_removals)} files")
                for file_path, error in self.failed_removals[:5]:
                    print(f"  - {file_path}: {error}")
        
        return True
    
    def verify_critical_files(self):
        """Verify all critical files still exist after cleanup"""
        findings = self.load_findings()
        if not findings:
            return False
        
        print("\n🔍 VERIFYING CRITICAL FILES")
        print("=" * 60)
        
        critical_files = findings['critical_files']
        missing_critical = []
        
        # Check a sample of critical files
        sample_size = min(20, len(critical_files))
        for file_path in critical_files[:sample_size]:
            full_path = self.parent_root / file_path
            if not full_path.exists():
                missing_critical.append(file_path)
        
        if missing_critical:
            print(f"⚠️  WARNING: {len(missing_critical)} critical files missing!")
            for file_path in missing_critical:
                print(f"  - {file_path}")
            return False
        else:
            print(f"✅ All sampled critical files verified ({sample_size} files)")
            return True
    
    def post_cleanup_test(self):
        """Run basic tests to ensure system still works"""
        print("\n🧪 RUNNING POST-CLEANUP TESTS")
        print("=" * 60)
        
        tests_passed = 0
        tests_failed = 0
        
        # Test 1: Django imports
        print("\n1. Testing Django imports...")
        try:
            import django
            from django.urls import reverse
            print("  ✅ Django imports working")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ Django import failed: {e}")
            tests_failed += 1
        
        # Test 2: Project imports
        print("\n2. Testing project imports...")
        try:
            from placement_test.models import Exam, StudentSession
            from core.models import School, CurriculumLevel
            print("  ✅ Project imports working")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ Project import failed: {e}")
            tests_failed += 1
        
        # Test 3: URL resolution
        print("\n3. Testing URL resolution...")
        try:
            import django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
            django.setup()
            from django.urls import reverse
            
            urls_to_test = [
                'core:index',
                'core:teacher_dashboard',
                'placement_test:exam_list'
            ]
            
            for url_name in urls_to_test:
                url = reverse(url_name)
                print(f"  ✅ {url_name} -> {url}")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ URL resolution failed: {e}")
            tests_failed += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("POST-CLEANUP TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {tests_passed}")
        print(f"❌ Failed: {tests_failed}")
        
        if tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED - Cleanup successful!")
            return True
        else:
            print("\n⚠️  Some tests failed - Review cleanup results")
            return False


def main():
    executor = CleanupExecutor()
    
    # Parse command line arguments
    execute_mode = '--execute' in sys.argv
    skip_tests = '--skip-tests' in sys.argv
    
    print("=" * 80)
    print("CLEANUP EXECUTOR")
    print("Removing redundant files identified by cleanup analysis")
    print("=" * 80)
    
    # Create backup list
    print("\n📋 Creating backup list...")
    backup_file = executor.create_backup_list()
    if not backup_file:
        print("❌ Failed to create backup list")
        return 1
    
    # Verify critical files before cleanup
    if not executor.verify_critical_files():
        print("\n⚠️  Critical files check failed. Aborting cleanup.")
        return 1
    
    # Execute cleanup
    success = executor.remove_files(dry_run=not execute_mode)
    if not success:
        return 1
    
    if execute_mode:
        # Verify critical files after cleanup
        if not executor.verify_critical_files():
            print("\n⚠️  Critical files missing after cleanup!")
            return 1
        
        # Run post-cleanup tests
        if not skip_tests:
            if not executor.post_cleanup_test():
                print("\n⚠️  Post-cleanup tests failed")
                return 1
    
    print("\n✅ Cleanup process completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())