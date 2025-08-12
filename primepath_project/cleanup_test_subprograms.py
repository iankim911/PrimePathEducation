#!/usr/bin/env python
"""
Standalone script to clean up test/QA subprograms from the database
Run with: python cleanup_test_subprograms.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import transaction
from core.models import SubProgram, CurriculumLevel
from core.curriculum_constants import is_test_subprogram
from placement_test.models import Exam, Question, StudentSession
import json
from datetime import datetime


def cleanup_test_subprograms(dry_run=True):
    """Clean up test/QA subprograms from the database"""
    
    print('=' * 80)
    print('TEST SUBPROGRAM CLEANUP')
    print('=' * 80)

    # Find all test subprograms
    all_subprograms = SubProgram.objects.all()
    test_subprograms = []
    
    for sp in all_subprograms:
        if is_test_subprogram(sp.name):
            test_subprograms.append(sp)

    if not test_subprograms:
        print('✅ No test subprograms found in database')
        return

    # Analyze impact
    print(f"\nFound {len(test_subprograms)} test subprograms:")
    total_levels = 0
    total_exams = 0
    total_questions = 0
    total_sessions = 0

    impact_data = []
    
    for sp in test_subprograms:
        levels = sp.levels.all()
        level_count = levels.count()
        
        exam_count = 0
        question_count = 0
        session_count = 0
        
        for level in levels:
            exams = Exam.objects.filter(curriculum_level=level)
            exam_count += exams.count()
            
            for exam in exams:
                questions = exam.questions.count()
                question_count += questions
                sessions = StudentSession.objects.filter(exam=exam).count()
                session_count += sessions
        
        impact_data.append({
            'subprogram': sp,
            'name': sp.name,
            'program': sp.program.name,
            'levels': level_count,
            'exams': exam_count,
            'questions': question_count,
            'sessions': session_count
        })
        
        total_levels += level_count
        total_exams += exam_count
        total_questions += question_count
        total_sessions += session_count
        
        print(f"  - {sp.name} (Program: {sp.program.name})")
        print(f"    Levels: {level_count}, Exams: {exam_count}, Questions: {question_count}, Sessions: {session_count}")

    # Summary
    print('\n' + '=' * 40)
    print('IMPACT SUMMARY')
    print('=' * 40)
    print(f"SubPrograms to delete: {len(test_subprograms)}")
    print(f"CurriculumLevels to delete: {total_levels}")
    print(f"Exams to delete: {total_exams}")
    print(f"Questions to delete: {total_questions}")
    print(f"Student sessions to delete: {total_sessions}")

    if dry_run:
        print('\n✅ DRY RUN - No data was deleted')
        print('Run with --delete flag to actually delete the data')
        print('\nExample: python cleanup_test_subprograms.py --delete')
        return

    # Confirm deletion
    print('\n⚠️  WARNING: This will permanently delete the above data!')
    print('⚠️  This action CANNOT be undone!')
    confirm = input('Type "DELETE" to confirm deletion: ')
    if confirm != 'DELETE':
        print('❌ Deletion cancelled')
        return

    # Perform deletion
    print('\nDeleting test subprograms...')
    
    try:
        with transaction.atomic():
            deleted_count = 0
            
            for data in impact_data:
                sp = data['subprogram']
                print(f"  Deleting {sp.name}...")
                
                # Delete cascade will handle related objects
                sp.delete()
                deleted_count += 1
            
            print(f'\n✅ Successfully deleted {deleted_count} test subprograms')
            
            # Save deletion log
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f'test_subprogram_deletion_log_{timestamp}.json'
            
            log_data = {
                'timestamp': timestamp,
                'deleted_subprograms': [
                    {
                        'name': d['name'],
                        'program': d['program'],
                        'levels': d['levels'],
                        'exams': d['exams'],
                        'questions': d['questions'],
                        'sessions': d['sessions']
                    }
                    for d in impact_data
                ],
                'totals': {
                    'subprograms': len(test_subprograms),
                    'levels': total_levels,
                    'exams': total_exams,
                    'questions': total_questions,
                    'sessions': total_sessions
                }
            }
            
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            print(f'📝 Deletion log saved to: {log_file}')
            
    except Exception as e:
        print(f'❌ Error during deletion: {e}')
        raise

    print('\n' + '=' * 80)
    print('CLEANUP COMPLETE')
    print('=' * 80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up test/QA subprograms from database')
    parser.add_argument('--delete', action='store_true', help='Actually delete the data (default is dry run)')
    
    args = parser.parse_args()
    
    cleanup_test_subprograms(dry_run=not args.delete)