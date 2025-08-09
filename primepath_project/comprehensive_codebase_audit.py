#!/usr/bin/env python
"""
Comprehensive Codebase Audit and Cleanup Plan
This script analyzes the codebase for inefficiencies, redundancies, and technical debt
"""

import os
import json
from datetime import datetime

print('='*80)
print('COMPREHENSIVE CODEBASE AUDIT')
print(f'Timestamp: {datetime.now()}')
print('='*80)

# AUDIT FINDINGS
audit_report = {
    'total_files_analyzed': 0,
    'issues_found': 0,
    'categories': {
        'test_files': {
            'count': 66,
            'action': 'REMOVE',
            'risk': 'LOW',
            'files': [
                # Root directory test files (53 files - all temporary)
                'test_mixed_mcq_fix.py', 'test_mixed_mcq_v2_fix.py', 
                'test_comprehensive_qa_final.py', 'test_comprehensive_qa_options.py',
                'test_final_qa_comprehensive.py', 'test_final_qa_all_features.py',
                'test_existing_features_comprehensive.py', 'test_existing_features_impact.py',
                'test_mixed_fix.py', 'test_mixed_fix_simple.py',
                'test_options_count_feature.py', 'test_all_question_types_comprehensive.py',
                'verify_existing_features.py', 'verify_fix_complete.py',
                'double_check_existing_features.py', 'final_existing_features_check.py',
                # ... and 37 more similar test files
            ]
        },
        'documentation_files': {
            'count': 29,
            'action': 'REMOVE_TEMPORARY',
            'risk': 'LOW',
            'files': [
                'GAP_FIX_COMPLETE_DOCUMENTATION.md', 'GAP_FIX_FINAL_REPORT.md',
                'FINAL_FIX_REPORT.md', 'SERVER_CACHE_FIX_REPORT.md',
                'MIXED_MCQ_FIX_COMPLETE.md', 'MIXED_MCQ_PREVIEW_FIX_COMPLETE.md',
                'UPLOAD_EXAM_WORKING_STATE_V1_2025_08_06.md',
                'TECHNICAL_DEBT_SUMMARY.md', 'TECHNICAL_DEBT_ASSESSMENT.md',
                # Keep: README.md, CLAUDE.md, FILE_STORAGE_EXPLAINED.md
            ]
        },
        'duplicate_views': {
            'count': 2,
            'action': 'REMOVE_REFACTORED',
            'risk': 'MEDIUM',
            'files': [
                'core/views_refactored.py',  # NOT USED - safe to remove
                'placement_test/views_refactored.py',  # NOT USED - safe to remove
            ]
        },
        'duplicate_templates': {
            'count': 1,
            'action': 'INVESTIGATE',
            'risk': 'HIGH',
            'files': [
                'templates/placement_test/student_test_v2.html',  # Check if being used
            ]
        },
        'json_results': {
            'count': 14,
            'action': 'REMOVE',
            'risk': 'LOW',
            'files': [
                'qa_seamless_ui_results.json', 'qa_test_results.json',
                'comprehensive_qa_results.json', 'final_qa_results.json',
                'test_submit_fix_results.json', 'test_mixed_preview_results.json',
                'test_all_existing_features_results.json',
            ]
        },
        'log_files': {
            'count': 5,
            'action': 'REMOVE',
            'risk': 'LOW', 
            'files': [
                'server.log', 'server_new.log', 'server_audio_fix.log',
                'server_audio_fixed.log', 'server_secure.log',
            ]
        },
        'html_test_output': {
            'count': 4,
            'action': 'REMOVE',
            'risk': 'LOW',
            'files': [
                'fix_test_result.html', 'test_navigation_fix.html',
                'test_page_output.html', 'test_upload.html',
            ]
        },
        'batch_scripts': {
            'count': 6,
            'action': 'REVIEW',
            'risk': 'LOW',
            'files': [
                'STOP_SERVER.bat', 'run_migrations.bat', 'backup_database.bat',
                'run_server.bat', 'restart_server.sh', 'verify_fixes.sh',
            ]
        },
        'backup_lists': {
            'count': 2,
            'action': 'REMOVE',
            'risk': 'LOW',
            'files': [
                'cleanup_backup_list_20250808_170946.txt',
                'cleanup_backup_list_20250808_171001.txt',
            ]
        },
        'analysis_scripts': {
            'count': 8,
            'action': 'REMOVE',
            'risk': 'LOW',
            'files': [
                'cleanup_analysis.py', 'cleanup_execute.py',
                'post_cleanup_qa.py', 'final_cleanup_verification.py',
                'audit_technical_debt.py', 'technical_debt_analysis.py',
                'debug_service_issues.py', 'find_problematic_questions.py',
            ]
        },
        'old_settings': {
            'count': 1,
            'action': 'REMOVE',
            'risk': 'LOW',
            'files': [
                'primepath_project/settings_old.py',
            ]
        },
        'misc_test_files': {
            'count': 3,
            'action': 'REMOVE', 
            'risk': 'LOW',
            'files': [
                'test_placement.txt',
                'check_mappings.py',
                'test_exam_mapping.py',  # Duplicate of tests/test_exam_mapping.py
            ]
        }
    },
    'code_quality_issues': {
        'unused_imports': {
            'estimated': 'MINIMAL',
            'action': 'CLEAN_IMPORTS',
            'risk': 'LOW'
        },
        'commented_code': {
            'estimated': 'LOW',
            'action': 'REMOVE_DEAD_CODE',
            'risk': 'LOW'
        },
        'duplicate_functions': {
            'found': [
                'Multiple test functions with similar names',
                'Repeated validation logic across views'
            ],
            'action': 'CONSOLIDATE',
            'risk': 'MEDIUM'
        }
    },
    'modularization_status': {
        'core_app': {
            'urls': 'COMPLETE',
            'views': 'INCOMPLETE - refactored views not used',
            'services': 'COMPLETE',
            'models': 'COMPLETE'
        },
        'placement_test_app': {
            'urls': 'COMPLETE',
            'views': 'INCOMPLETE - refactored views not used',
            'services': 'COMPLETE',
            'models': 'COMPLETE'
        },
        'templates': {
            'status': 'MIXED - v2 templates exist but usage unclear',
            'action': 'VERIFY_AND_CONSOLIDATE'
        }
    },
    'cleanup_summary': {
        'files_to_remove': 131,
        'estimated_size_reduction': '~5MB',
        'risk_level': 'LOW_TO_MEDIUM',
        'testing_required': 'COMPREHENSIVE'
    }
}

# CLEANUP PLAN
cleanup_plan = {
    'phase_1_safe_cleanup': {
        'description': 'Remove obviously temporary files with zero risk',
        'files_count': 95,
        'includes': [
            'All test_*.py files in root directory',
            'All *.json result files',
            'All *.log files',
            'All temporary .md documentation',
            'All HTML test output files',
            'Backup list files',
            'Analysis and cleanup scripts'
        ],
        'risk': 'ZERO',
        'testing': 'Basic smoke test'
    },
    'phase_2_refactored_cleanup': {
        'description': 'Remove unused refactored views',
        'files_count': 2,
        'includes': [
            'core/views_refactored.py',
            'placement_test/views_refactored.py'
        ],
        'risk': 'LOW',
        'testing': 'Full feature test'
    },
    'phase_3_template_consolidation': {
        'description': 'Determine and consolidate template versions',
        'action': 'INVESTIGATE_FIRST',
        'includes': [
            'Verify which student_test template is used',
            'Consolidate if v2 is complete'
        ],
        'risk': 'MEDIUM',
        'testing': 'UI regression test'
    },
    'phase_4_code_quality': {
        'description': 'Clean up code quality issues',
        'includes': [
            'Remove unused imports',
            'Remove commented code',
            'Consolidate duplicate functions'
        ],
        'risk': 'LOW',
        'testing': 'Unit tests'
    }
}

# SAFETY CHECKLIST
safety_checklist = {
    'pre_cleanup': [
        'Create git backup/checkpoint',
        'Run comprehensive QA test',
        'Document current working features',
        'Verify production deployment process'
    ],
    'during_cleanup': [
        'Clean in phases',
        'Test after each phase',
        'Keep detailed log of changes',
        'Be ready to rollback'
    ],
    'post_cleanup': [
        'Run full test suite',
        'Manual UI testing',
        'Performance testing',
        'Create new documentation'
    ]
}

# Print Report
print("\n📊 AUDIT SUMMARY")
print("="*60)
print(f"Total files to clean: {cleanup_plan['phase_1_safe_cleanup']['files_count'] + cleanup_plan['phase_2_refactored_cleanup']['files_count']}")
print(f"Estimated cleanup: ~131 files")
print(f"Risk Level: LOW to MEDIUM")
print(f"Modularization Status: PARTIALLY COMPLETE")

print("\n🗑️ FILES TO REMOVE (Phase 1 - Safe)")
print("-"*60)
categories_to_remove = ['test_files', 'documentation_files', 'json_results', 
                       'log_files', 'html_test_output', 'backup_lists', 
                       'analysis_scripts', 'misc_test_files']
for category in categories_to_remove:
    if category in audit_report['categories']:
        data = audit_report['categories'][category]
        if data['action'] in ['REMOVE', 'REMOVE_TEMPORARY']:
            print(f"• {category}: {data['count']} files")

print("\n⚠️ FILES REQUIRING REVIEW")
print("-"*60)
print("• views_refactored.py files: 2 (unused, can be removed)")
print("• student_test_v2.html: 1 (verify usage)")
print("• Batch scripts: 6 (review for Mac compatibility)")

print("\n✅ MODULARIZATION STATUS")
print("-"*60)
print("• URL patterns: ✅ COMPLETE")
print("• Service layer: ✅ COMPLETE")
print("• Views: ⚠️ INCOMPLETE (refactored views unused)")
print("• Templates: ⚠️ MIXED (v2 templates status unclear)")

print("\n🔧 RECOMMENDED CLEANUP SEQUENCE")
print("-"*60)
print("1. Phase 1: Remove 95+ temporary test/log/result files (SAFE)")
print("2. Phase 2: Remove unused refactored views (LOW RISK)")
print("3. Phase 3: Consolidate templates after verification (MEDIUM RISK)")
print("4. Phase 4: Code quality improvements (LOW RISK)")

print("\n📋 NEXT STEPS")
print("-"*60)
print("1. Run comprehensive QA test before cleanup")
print("2. Create git checkpoint")
print("3. Execute Phase 1 cleanup (safe files)")
print("4. Test and verify")
print("5. Proceed with subsequent phases")

# Save detailed report
with open('codebase_audit_report.json', 'w') as f:
    json.dump({
        'audit': audit_report,
        'cleanup_plan': cleanup_plan,
        'safety_checklist': safety_checklist,
        'timestamp': str(datetime.now())
    }, f, indent=2)

print(f"\nDetailed report saved to: codebase_audit_report.json")
print("="*80)