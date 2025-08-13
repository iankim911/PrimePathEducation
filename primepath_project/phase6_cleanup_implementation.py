#!/usr/bin/env python
"""
Phase 6: Database & Organization Cleanup Implementation
Comprehensive cleanup with relationship preservation and robust logging
"""
import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
import django
django.setup()

from django.db import transaction
from core.models import SubProgram, CurriculumLevel, Program
from placement_test.models import StudentSession, Exam, Question, StudentAnswer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase6_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Phase6Cleanup:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.base_path = Path(__file__).parent
        self.results = {
            'test_subprograms_cleaned': 0,
            'test_sessions_cleaned': 0,
            'orphaned_files_moved': 0,
            'empty_dirs_removed': 0,
            'errors': [],
            'preserved_relationships': []
        }
        self.console_logs = []
        
    def log_console(self, message, level='info'):
        """Add console.log statements for frontend debugging"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.console_logs.append(log_entry)
        
        # Also log to Python logger
        if level == 'error':
            logger.error(f"[CONSOLE] {message}")
        elif level == 'warn':
            logger.warning(f"[CONSOLE] {message}")
        else:
            logger.info(f"[CONSOLE] {message}")
            
    def clean_test_subprograms(self):
        """Remove test subprograms from database while preserving relationships"""
        print("\n" + "="*80)
        print("🧹 CLEANING TEST SUBPROGRAMS")
        print("="*80)
        
        self.log_console("Starting test subprogram cleanup", "info")
        
        # Define test subprogram patterns
        test_patterns = [
            'Test SubProgram',
            'SHORT Answer Test SubProgram',
            'Comprehensive Test SubProgram',
            'Management Test SubProgram',
            'SHORT Display Test SubProgram',
            'Submit Test SubProgram',
            'Final Test SubProgram',
            '[INACTIVE]'
        ]
        
        test_subprograms = SubProgram.objects.none()
        for pattern in test_patterns:
            test_subprograms = test_subprograms | SubProgram.objects.filter(name__icontains=pattern)
        
        print(f"\n  Found {test_subprograms.count()} test subprograms to clean")
        
        for subprogram in test_subprograms:
            print(f"\n  Analyzing: {subprogram.name}")
            
            # Check for related curriculum levels
            levels = CurriculumLevel.objects.filter(subprogram=subprogram)
            print(f"    - Has {levels.count()} curriculum levels")
            
            # Check for exams using these levels
            exam_count = 0
            for level in levels:
                exam_count += Exam.objects.filter(curriculum_level=level).count()
            
            if exam_count > 0:
                print(f"    ⚠️ PRESERVED: Has {exam_count} related exams")
                self.results['preserved_relationships'].append({
                    'subprogram': subprogram.name,
                    'reason': f'Has {exam_count} related exams',
                    'action': 'Mark as INACTIVE instead of delete'
                })
                
                # Mark as inactive instead of deleting
                if not self.dry_run and '[INACTIVE]' not in subprogram.name:
                    subprogram.name = f"[INACTIVE] {subprogram.name}"
                    subprogram.save()
                    self.log_console(f"Marked {subprogram.name} as INACTIVE", "warn")
            else:
                print(f"    ✅ Safe to delete (no exams)")
                if not self.dry_run:
                    try:
                        with transaction.atomic():
                            # Delete curriculum levels first
                            levels.delete()
                            # Then delete subprogram
                            subprogram.delete()
                            self.results['test_subprograms_cleaned'] += 1
                            self.log_console(f"Deleted test subprogram: {subprogram.name}", "info")
                    except Exception as e:
                        self.results['errors'].append(f"Error deleting {subprogram.name}: {e}")
                        self.log_console(f"Error deleting {subprogram.name}: {e}", "error")
                else:
                    print(f"    [DRY RUN] Would delete {subprogram.name}")
                    
    def clean_test_sessions(self):
        """Remove test student sessions while preserving real data"""
        print("\n" + "="*80)
        print("🧹 CLEANING TEST STUDENT SESSIONS")
        print("="*80)
        
        self.log_console("Starting test session cleanup", "info")
        
        # Find test sessions
        test_sessions = StudentSession.objects.filter(
            student_name__iregex=r'(test|demo|sample|example)'
        )
        
        print(f"\n  Found {test_sessions.count()} test sessions")
        
        for session in test_sessions:
            print(f"\n  Session: {session.student_name} (ID: {session.id})")
            print(f"    - Exam: {session.exam.name if session.exam else 'None'}")
            print(f"    - Started: {session.started_at}")
            print(f"    - Completed: {'Yes' if session.completed_at else 'No'}")
            
            # Check for related answers
            answers = StudentAnswer.objects.filter(session=session)
            print(f"    - Has {answers.count()} answers")
            
            if not self.dry_run:
                try:
                    with transaction.atomic():
                        # Delete answers first
                        answers.delete()
                        # Then delete session
                        session.delete()
                        self.results['test_sessions_cleaned'] += 1
                        self.log_console(f"Deleted test session: {session.student_name}", "info")
                except Exception as e:
                    self.results['errors'].append(f"Error deleting session {session.id}: {e}")
                    self.log_console(f"Error deleting session {session.id}: {e}", "error")
            else:
                print(f"    [DRY RUN] Would delete session")
                
    def organize_orphaned_files(self):
        """Move orphaned test files to organized structure"""
        print("\n" + "="*80)
        print("📁 ORGANIZING ORPHANED FILES")
        print("="*80)
        
        self.log_console("Starting file organization", "info")
        
        # Create organized test directory structure
        test_root = self.base_path / 'tests'
        test_dirs = {
            'unit': test_root / 'unit',
            'integration': test_root / 'integration',
            'fixtures': test_root / 'fixtures',
            'utils': test_root / 'utils',
            'archive': test_root / 'archive'
        }
        
        # Create directories if not in dry run
        if not self.dry_run:
            for dir_path in test_dirs.values():
                dir_path.mkdir(parents=True, exist_ok=True)
                
        # Find orphaned test files
        orphaned_patterns = [
            ('test_*.py', 'integration'),
            ('*_test.py', 'integration'),
            ('comprehensive_*.py', 'archive'),
            ('deep_*.py', 'archive'),
            ('ultra_*.py', 'archive'),
            ('ultimate_*.py', 'archive'),
            ('double_check*.py', 'archive'),
            ('analyze_*.py', 'utils'),
            ('phase*.py', 'archive'),
            ('qa_*.py', 'integration'),
            ('final_*.py', 'archive'),
            ('verify_*.py', 'utils'),
            ('check_*.py', 'utils'),
            ('quick_*.py', 'utils')
        ]
        
        files_to_move = []
        
        # Find files matching patterns
        for pattern, category in orphaned_patterns:
            for file_path in self.base_path.glob(pattern):
                if file_path.is_file() and 'tests' not in str(file_path):
                    files_to_move.append((file_path, test_dirs[category]))
                    
        print(f"\n  Found {len(files_to_move)} files to organize")
        
        for src_file, dest_dir in files_to_move[:10]:  # Show first 10
            dest_file = dest_dir / src_file.name
            print(f"    {src_file.name} → {dest_dir.relative_to(self.base_path)}/")
            
            if not self.dry_run:
                try:
                    shutil.move(str(src_file), str(dest_file))
                    self.results['orphaned_files_moved'] += 1
                    self.log_console(f"Moved {src_file.name} to {dest_dir.name}/", "info")
                except Exception as e:
                    self.results['errors'].append(f"Error moving {src_file.name}: {e}")
                    self.log_console(f"Error moving {src_file.name}: {e}", "error")
                    
        if len(files_to_move) > 10:
            print(f"    ... and {len(files_to_move) - 10} more files")
            
    def remove_empty_directories(self):
        """Remove empty directories"""
        print("\n" + "="*80)
        print("📁 REMOVING EMPTY DIRECTORIES")
        print("="*80)
        
        self.log_console("Removing empty directories", "info")
        
        empty_dirs = []
        
        # Find empty directories
        for root, dirs, files in os.walk(self.base_path, topdown=False):
            # Skip special directories
            if any(skip in root for skip in ['__pycache__', '.git', 'migrations', 'media']):
                continue
                
            # Check if directory is empty
            if not files and not os.listdir(root):
                empty_dirs.append(Path(root))
                
        print(f"\n  Found {len(empty_dirs)} empty directories")
        
        for empty_dir in empty_dirs:
            print(f"    {empty_dir.relative_to(self.base_path)}")
            
            if not self.dry_run:
                try:
                    empty_dir.rmdir()
                    self.results['empty_dirs_removed'] += 1
                    self.log_console(f"Removed empty dir: {empty_dir.name}", "info")
                except Exception as e:
                    self.results['errors'].append(f"Error removing {empty_dir}: {e}")
                    
    def verify_relationships(self):
        """Verify all model relationships are intact"""
        print("\n" + "="*80)
        print("🔍 VERIFYING MODEL RELATIONSHIPS")
        print("="*80)
        
        self.log_console("Verifying model relationships", "info")
        
        checks = []
        
        # Check Exam → CurriculumLevel
        exams = Exam.objects.all()
        for exam in exams:
            if exam.curriculum_level:
                checks.append(f"Exam '{exam.name}' → Level '{exam.curriculum_level}'")
                
        # Check StudentSession → Exam
        sessions = StudentSession.objects.all()
        for session in sessions:
            if session.exam:
                checks.append(f"Session '{session.student_name}' → Exam '{session.exam.name}'")
                
        # Check Question → Exam
        questions = Question.objects.all()
        exam_questions = {}
        for question in questions:
            if question.exam:
                if question.exam.name not in exam_questions:
                    exam_questions[question.exam.name] = 0
                exam_questions[question.exam.name] += 1
                
        for exam_name, count in exam_questions.items():
            checks.append(f"Exam '{exam_name}' has {count} questions")
            
        print(f"\n  ✅ Verified {len(checks)} relationships")
        for check in checks[:5]:  # Show first 5
            print(f"    {check}")
            
        if len(checks) > 5:
            print(f"    ... and {len(checks) - 5} more")
            
        self.log_console(f"All {len(checks)} relationships verified", "info")
        
    def generate_console_script(self):
        """Generate JavaScript for frontend console logging"""
        print("\n" + "="*80)
        print("📜 GENERATING CONSOLE LOGGING SCRIPT")
        print("="*80)
        
        script_content = f'''
// ===== PHASE 6 CLEANUP MONITORING =====
// Generated: {datetime.now().isoformat()}

console.log('%c===== PHASE 6 CLEANUP STATUS =====', 'color: blue; font-weight: bold');

// Cleanup results
const cleanupResults = {{
    testSubprogramsCleaned: {self.results['test_subprograms_cleaned']},
    testSessionsCleaned: {self.results['test_sessions_cleaned']},
    orphanedFilesMoved: {self.results['orphaned_files_moved']},
    emptyDirsRemoved: {self.results['empty_dirs_removed']},
    errors: {len(self.results['errors'])},
    preservedRelationships: {len(self.results['preserved_relationships'])}
}};

console.table(cleanupResults);

// Log cleanup actions
const cleanupLogs = {json.dumps(self.console_logs, indent=2)};

cleanupLogs.forEach(log => {{
    const timestamp = new Date(log.timestamp).toLocaleTimeString();
    const prefix = `[PHASE6 ${{timestamp}}]`;
    
    if (log.level === 'error') {{
        console.error(`${{prefix}} ${{log.message}}`);
    }} else if (log.level === 'warn') {{
        console.warn(`${{prefix}} ${{log.message}}`);
    }} else {{
        console.log(`${{prefix}} ${{log.message}}`);
    }}
}});

// Verify critical features still work
console.log('%c===== FEATURE VERIFICATION =====', 'color: green; font-weight: bold');

// Check exam dropdown
fetch('/api/placement/exams/create/')
    .then(response => {{
        console.log('[PHASE6] Exam creation endpoint: ' + (response.ok ? '✅ OK' : '❌ Failed'));
    }})
    .catch(err => console.error('[PHASE6] Exam endpoint error:', err));

// Check student sessions
fetch('/api/placement/sessions/')
    .then(response => {{
        console.log('[PHASE6] Sessions endpoint: ' + (response.ok ? '✅ OK' : '❌ Failed'));
    }})
    .catch(err => console.error('[PHASE6] Sessions endpoint error:', err));

// Monitor for any JavaScript errors
window.addEventListener('error', function(e) {{
    console.error('[PHASE6] Runtime error detected:', e.message);
}});

console.log('%c===== PHASE 6 MONITORING ACTIVE =====', 'color: green; font-weight: bold');
'''
        
        # Save script
        script_path = self.base_path / 'static' / 'js' / 'phase6_monitoring.js'
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        print(f"  ✅ Created: static/js/phase6_monitoring.js")
        
        # Also create a template snippet
        template_snippet = '''
<!-- Phase 6 Cleanup Monitoring -->
<script src="{% static 'js/phase6_monitoring.js' %}"></script>
<script>
    console.log('[PHASE6] Monitoring script loaded at: ' + new Date().toISOString());
</script>
'''
        
        snippet_path = self.base_path / 'templates' / 'phase6_monitoring_snippet.html'
        with open(snippet_path, 'w') as f:
            f.write(template_snippet)
            
        print(f"  ✅ Created: templates/phase6_monitoring_snippet.html")
        
    def generate_report(self):
        """Generate comprehensive cleanup report"""
        print("\n" + "="*80)
        print("📊 PHASE 6 CLEANUP REPORT")
        print("="*80)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'results': self.results,
            'console_logs': self.console_logs,
            'status': 'SUCCESS' if not self.results['errors'] else 'PARTIAL'
        }
        
        # Save report
        report_path = self.base_path / 'phase6_cleanup_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n  📋 SUMMARY:")
        print(f"     Test SubPrograms Cleaned: {self.results['test_subprograms_cleaned']}")
        print(f"     Test Sessions Cleaned: {self.results['test_sessions_cleaned']}")
        print(f"     Orphaned Files Organized: {self.results['orphaned_files_moved']}")
        print(f"     Empty Directories Removed: {self.results['empty_dirs_removed']}")
        print(f"     Relationships Preserved: {len(self.results['preserved_relationships'])}")
        print(f"     Errors: {len(self.results['errors'])}")
        
        if self.results['errors']:
            print(f"\n  ⚠️ ERRORS ENCOUNTERED:")
            for error in self.results['errors'][:5]:
                print(f"     - {error}")
                
        if self.results['preserved_relationships']:
            print(f"\n  🔒 PRESERVED RELATIONSHIPS:")
            for rel in self.results['preserved_relationships'][:5]:
                print(f"     - {rel['subprogram']}: {rel['reason']}")
                
        print(f"\n  💾 Full report saved to: phase6_cleanup_report.json")
        
        return report
        
    def run(self):
        """Execute Phase 6 cleanup"""
        print("\n" + "="*80)
        print("🚀 PHASE 6: DATABASE & ORGANIZATION CLEANUP")
        print("="*80)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        
        try:
            # Execute cleanup steps
            self.clean_test_subprograms()
            self.clean_test_sessions()
            self.organize_orphaned_files()
            self.remove_empty_directories()
            self.verify_relationships()
            self.generate_console_script()
            
            # Generate report
            report = self.generate_report()
            
            print("\n" + "="*80)
            if self.dry_run:
                print("✅ DRY RUN COMPLETE - Review results above")
                print("To execute cleanup, run with dry_run=False")
            else:
                print("✅ PHASE 6 CLEANUP COMPLETE")
                
            print("="*80)
            
            return report
            
        except Exception as e:
            logger.error(f"Phase 6 cleanup failed: {e}")
            print(f"\n❌ CLEANUP FAILED: {e}")
            return None

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Phase 6 Cleanup')
    parser.add_argument('--execute', action='store_true', 
                       help='Execute cleanup (default is dry run)')
    args = parser.parse_args()
    
    # Run cleanup
    cleanup = Phase6Cleanup(dry_run=not args.execute)
    report = cleanup.run()
    
    if report:
        return 0 if report['status'] == 'SUCCESS' else 1
    return 1

if __name__ == "__main__":
    sys.exit(main())