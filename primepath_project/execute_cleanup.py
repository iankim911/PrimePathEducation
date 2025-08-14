#!/usr/bin/env python
"""
Execute Cleanup - Safe removal of identified files
This script removes files in phases with testing after each phase
"""

import os
import shutil
import json
from datetime import datetime

print('='*80)
print('CODEBASE CLEANUP EXECUTION')
print(f'Timestamp: {datetime.now()}')
print('='*80)

# Track cleanup progress
cleanup_log = {
    'timestamp': str(datetime.now()),
    'phases': [],
    'total_removed': 0,
    'errors': []
}

def remove_file(filepath, dry_run=False):
    """Safely remove a file"""
    try:
        if os.path.exists(filepath):
            if not dry_run:
                os.remove(filepath)
                print(f"  ✅ Removed: {filepath}")
                return True
            else:
                print(f"  [DRY RUN] Would remove: {filepath}")
                return True
        else:
            print(f"  ⚠️ Not found: {filepath}")
            return False
    except Exception as e:
        print(f"  ❌ Error removing {filepath}: {e}")
        cleanup_log['errors'].append(f"{filepath}: {str(e)}")
        return False

def execute_phase_1(dry_run=False):
    """Phase 1: Remove obviously temporary test files"""
    print("\n" + "="*60)
    print("PHASE 1: REMOVING TEMPORARY TEST FILES")
    print("="*60)
    
    removed_count = 0
    
    # Test files in root directory
    test_files = [
        'test_mixed_mcq_fix.py', 'test_mixed_mcq_v2_fix.py',
        'test_comprehensive_qa_final.py', 'test_comprehensive_qa_options.py',
        'test_comprehensive_qa_long_answer.py', 'test_comprehensive_qa.py',
        'test_final_qa_comprehensive.py', 'test_final_qa_all_features.py',
        'test_existing_features_comprehensive.py', 'test_existing_features_impact.py',
        'test_existing_features_logic.py', 'test_mixed_fix.py',
        'test_mixed_fix_simple.py', 'test_mixed_comprehensive.py',
        'test_mixed_long_answer_fix.py', 'test_mixed_mcq_options.py',
        'test_mixed_questions_fix.py', 'test_mixed_preview_fix.py',
        'test_multiple_short_fix.py', 'test_options_count_feature.py',
        'test_question_types_detailed.py', 'test_submit_fix_comprehensive.py',
        'test_all_question_types_comprehensive.py', 'test_all_features_after_mixed_fix.py',
        'test_all_question_combinations.py', 'test_all_combinations.py',
        'test_actual_rendering.py', 'test_filter_fix.py',
        'test_data_integrity_final.py', 'test_all_existing_features_final.py',
        'verify_existing_features.py', 'verify_fix_complete.py',
        'verify_long_fix_complete.py', 'double_check_existing_features.py',
        'final_existing_features_check.py', 'focused_feature_check.py',
        'comprehensive_qa_test.py', 'comprehensive_qa_final.py',
        'final_comprehensive_test.py', 'demo_options_count_feature.py',
        'create_test_session_and_debug.py', 'find_problematic_questions.py',
        'investigate_3_to_2_issue.py', 'investigate_long_questions.py',
        'fix_long_options_count.py', 'fix_options_count_now.py',
        'qa_test_final.py', 'qa_test_long_fix.py',
        'test_ui_fixes.py', 'test_fix_validation.py',
        'simple_fix_test.py', 'test_phone_field_fix.py',
        'test_student_interface_fix.py', 'quick_test_student_fix.py',
        'test_exam_mapping.py',  # Duplicate of tests/test_exam_mapping.py
    ]
    
    print(f"\nRemoving {len(test_files)} test files...")
    for file in test_files:
        if remove_file(file, dry_run):
            removed_count += 1
    
    # JSON result files
    json_files = [
        'qa_seamless_ui_results.json', 'qa_test_results.json',
        'comprehensive_qa_results.json', 'final_qa_results.json',
        'test_submit_fix_results.json', 'test_mixed_preview_results.json',
        'test_all_existing_features_results.json', 'qa_final_results.json',
        'qa_long_fix_results.json', 'test_existing_features_results.json',
        'test_final_qa_results.json', 'codebase_audit_report.json',
        'pre_cleanup_qa_results.json',
    ]
    
    print(f"\nRemoving {len(json_files)} JSON result files...")
    for file in json_files:
        if remove_file(file, dry_run):
            removed_count += 1
    
    # Log files
    log_files = [
        'server.log', 'server_new.log', 'server_audio_fix.log',
        'server_audio_fixed.log', 'server_secure.log',
    ]
    
    print(f"\nRemoving {len(log_files)} log files...")
    for file in log_files:
        if remove_file(file, dry_run):
            removed_count += 1
    
    # HTML test output
    html_files = [
        'fix_test_result.html', 'test_navigation_fix.html',
        'test_page_output.html', 'test_upload.html',
    ]
    
    print(f"\nRemoving {len(html_files)} HTML test files...")
    for file in html_files:
        if remove_file(file, dry_run):
            removed_count += 1
    
    # Analysis and cleanup scripts
    analysis_files = [
        'cleanup_analysis.py', 'cleanup_execute.py',
        'post_cleanup_qa.py', 'final_cleanup_verification.py',
        'audit_technical_debt.py', 'technical_debt_analysis.py',
        'debug_service_issues.py', 'check_mappings.py',
    ]
    
    print(f"\nRemoving {len(analysis_files)} analysis/cleanup scripts...")
    for file in analysis_files:
        if remove_file(file, dry_run):
            removed_count += 1
    
    # Backup lists
    backup_files = [
        'cleanup_backup_list_20250808_170946.txt',
        'cleanup_backup_list_20250808_171001.txt',
    ]
    
    print(f"\nRemoving {len(backup_files)} backup list files...")
    for file in backup_files:
        if remove_file(file, dry_run):
            removed_count += 1
    
    # Misc files
    misc_files = [
        'test_placement.txt',
    ]
    
    print(f"\nRemoving {len(misc_files)} misc files...")
    for file in misc_files:
        if remove_file(file, dry_run):
            removed_count += 1
    
    cleanup_log['phases'].append({
        'phase': 1,
        'description': 'Remove temporary test files',
        'removed': removed_count,
        'timestamp': str(datetime.now())
    })
    
    print(f"\n✅ Phase 1 Complete: Removed {removed_count} files")
    return removed_count

def execute_phase_2(dry_run=False):
    """Phase 2: Remove temporary documentation"""
    print("\n" + "="*60)
    print("PHASE 2: REMOVING TEMPORARY DOCUMENTATION")
    print("="*60)
    
    removed_count = 0
    
    # Temporary documentation files (keep README.md, CLAUDE.md, FILE_STORAGE_EXPLAINED.md)
    doc_files = [
        'GAP_FIX_COMPLETE_DOCUMENTATION.md', 'GAP_FIX_FINAL_REPORT.md',
        'FINAL_FIX_REPORT.md', 'SERVER_CACHE_FIX_REPORT.md',
        'MIXED_MCQ_FIX_COMPLETE.md', 'MIXED_MCQ_PREVIEW_FIX_COMPLETE.md',
        'MIXED_MCQ_V2_FIX_COMPLETE.md', 'MIXED_MCQ_OPTIONS_FIX_FINAL.md',
        'UPLOAD_EXAM_WORKING_STATE_V1_2025_08_06.md',
        'TECHNICAL_DEBT_SUMMARY.md', 'TECHNICAL_DEBT_ASSESSMENT.md',
        'COMPREHENSIVE_FIX_IMPLEMENTATION.md', 'MIXED_QUESTIONS_FIX_COMPLETE.md',
        'MULTIPLE_INPUTS_FIX_COMPREHENSIVE.md', 'MULTIPLE_SHORT_ANSWER_FINAL_FIX.md',
        'EXISTING_FEATURES_VERIFICATION_COMPLETE.md', 'FINAL_FIX_REPORT_MIXED_MCQ_SUBMIT.md',
        'FINAL_VERIFICATION_REPORT.md', 'FIX_LONG_ANSWERS_COMPLETE.md',
        'FIX_MULTIPLE_INPUTS_COMPLETE.md', 'FIX_OPTIONS_COUNT_COMPLETE.md',
        'LAYOUT_IMPROVEMENTS.md', 'MARGIN_ADJUSTMENT_FINAL.md',
        'MARGIN_REDUCTION_COMPLETE.md', 'OUTER_MARGIN_REDUCTION.md',
        'PDF_TROUBLESHOOTING.md', 'SKIP_FIRST_LEFT_HALF_IMPLEMENTATION.md',
        'VERTICAL_SPLIT_FIX.md',
    ]
    
    print(f"\nRemoving {len(doc_files)} temporary documentation files...")
    for file in doc_files:
        if remove_file(file, dry_run):
            removed_count += 1
    
    cleanup_log['phases'].append({
        'phase': 2,
        'description': 'Remove temporary documentation',
        'removed': removed_count,
        'timestamp': str(datetime.now())
    })
    
    print(f"\n✅ Phase 2 Complete: Removed {removed_count} files")
    return removed_count

def execute_phase_3(dry_run=False):
    """Phase 3: Remove unused refactored code"""
    print("\n" + "="*60)
    print("PHASE 3: REMOVING UNUSED REFACTORED CODE")
    print("="*60)
    
    removed_count = 0
    
    # Unused refactored views
    refactored_files = [
        'core/views_refactored.py',
        'placement_test/views_refactored.py',
        'primepath_project/settings_old.py',
    ]
    
    print(f"\nRemoving {len(refactored_files)} unused refactored files...")
    for file in refactored_files:
        if remove_file(file, dry_run):
            removed_count += 1
    
    cleanup_log['phases'].append({
        'phase': 3,
        'description': 'Remove unused refactored code',
        'removed': removed_count,
        'timestamp': str(datetime.now())
    })
    
    print(f"\n✅ Phase 3 Complete: Removed {removed_count} files")
    return removed_count

def execute_phase_4(dry_run=False):
    """Phase 4: Remove old views.py if modular views are working"""
    print("\n" + "="*60)
    print("PHASE 4: CONSOLIDATING MODULAR VIEWS")
    print("="*60)
    
    removed_count = 0
    
    # Check if modular views are working
    if os.path.exists('placement_test/views/__init__.py'):
        # Remove the old single views.py file
        old_views = 'placement_test/views.py'
        if os.path.exists(old_views):
            print(f"\n🔍 Found old views.py alongside modular views/ folder")
            if remove_file(old_views, dry_run):
                removed_count += 1
    
    # Remove old student_test.html template (v2 is being used)
    old_template = 'templates/placement_test/student_test.html'
    if os.path.exists(old_template):
        print(f"\n🔍 Found old student_test.html (v2 is being used)")
        if remove_file(old_template, dry_run):
            removed_count += 1
    
    cleanup_log['phases'].append({
        'phase': 4,
        'description': 'Consolidate modular code',
        'removed': removed_count,
        'timestamp': str(datetime.now())
    })
    
    print(f"\n✅ Phase 4 Complete: Removed {removed_count} files")
    return removed_count

def execute_phase_5(dry_run=False):
    """Phase 5: Remove serena folder if not needed"""
    print("\n" + "="*60)
    print("PHASE 5: REMOVING UNUSED FOLDERS")
    print("="*60)
    
    removed_count = 0
    
    # Remove serena_installation folder
    if os.path.exists('serena_installation'):
        if not dry_run:
            shutil.rmtree('serena_installation')
            print(f"  ✅ Removed folder: serena_installation")
        else:
            print(f"  [DRY RUN] Would remove folder: serena_installation")
        removed_count += 1
    
    cleanup_log['phases'].append({
        'phase': 5,
        'description': 'Remove unused folders',
        'removed': removed_count,
        'timestamp': str(datetime.now())
    })
    
    print(f"\n✅ Phase 5 Complete: Removed {removed_count} folders")
    return removed_count

def run_quick_test():
    """Run a quick test to ensure nothing is broken"""
    print("\n" + "="*60)
    print("RUNNING QUICK TEST")
    print("="*60)
    
    try:
        import django
        django.setup()
        
        from django.test import Client
        client = Client()
        
        # Test critical endpoints
        tests = [
            ('/', 'Index'),
            ('/api/PlacementTest/exams/', 'Exams'),
            ('/placement-rules/', 'Rules'),
        ]
        
        passed = 0
        for url, name in tests:
            try:
                response = client.get(url)
                if response.status_code in [200, 302]:
                    print(f"  ✅ {name}: OK")
                    passed += 1
                else:
                    print(f"  ❌ {name}: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {name}: {e}")
        
        return passed == len(tests)
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

# Main execution
if __name__ == "__main__":
    import sys
    
    dry_run = '--dry-run' in sys.argv
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No files will be deleted")
    else:
        print("\n⚠️ REAL MODE - Files will be permanently deleted!")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Cleanup cancelled")
            sys.exit(0)
    
    total_removed = 0
    
    # Execute phases
    print("\n" + "="*80)
    print("STARTING CLEANUP")
    print("="*80)
    
    # Phase 1: Safe cleanup
    count = execute_phase_1(dry_run)
    total_removed += count
    if not dry_run and not run_quick_test():
        print("\n❌ Quick test failed after Phase 1! Stopping cleanup.")
        sys.exit(1)
    
    # Phase 2: Documentation cleanup
    count = execute_phase_2(dry_run)
    total_removed += count
    if not dry_run and not run_quick_test():
        print("\n❌ Quick test failed after Phase 2! Stopping cleanup.")
        sys.exit(1)
    
    # Phase 3: Unused refactored code
    count = execute_phase_3(dry_run)
    total_removed += count
    if not dry_run and not run_quick_test():
        print("\n❌ Quick test failed after Phase 3! Stopping cleanup.")
        sys.exit(1)
    
    # Phase 4: Consolidate modular code
    count = execute_phase_4(dry_run)
    total_removed += count
    if not dry_run and not run_quick_test():
        print("\n❌ Quick test failed after Phase 4! Stopping cleanup.")
        sys.exit(1)
    
    # Phase 5: Remove unused folders
    count = execute_phase_5(dry_run)
    total_removed += count
    
    cleanup_log['total_removed'] = total_removed
    
    # Summary
    print("\n" + "="*80)
    print("CLEANUP COMPLETE")
    print("="*80)
    print(f"Total files/folders removed: {total_removed}")
    
    if cleanup_log['errors']:
        print(f"\n⚠️ Errors encountered: {len(cleanup_log['errors'])}")
        for error in cleanup_log['errors']:
            print(f"  - {error}")
    
    # Save log
    if not dry_run:
        with open('cleanup_execution_log.json', 'w') as f:
            json.dump(cleanup_log, f, indent=2)
        print(f"\nCleanup log saved to: cleanup_execution_log.json")
    
    print("\n✅ Cleanup execution complete!")
    print("Run comprehensive QA test to verify all features still work")
    print("="*80)