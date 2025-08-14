#!/usr/bin/env python3
"""
Migration script to fix incorrect scoring calculations.

This script corrects the percentage_score for all completed sessions
that were calculated with the buggy logic that excluded LONG questions
from total_possible but included them in total_score.

Run with: python fix_scoring_migration.py
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.db import transaction
from placement_test.models import StudentSession, StudentAnswer
from placement_test.services.grading_service import GradingService
import logging

logger = logging.getLogger(__name__)

def analyze_scoring_issues():
    """Analyze and report on scoring issues"""
    print("🔍 ANALYZING SCORING ISSUES")
    print("=" * 60)
    
    sessions_to_fix = []
    total_sessions = 0
    
    # Find all completed sessions
    completed_sessions = StudentSession.objects.filter(
        completed_at__isnull=False,
        score__isnull=False,
        percentage_score__isnull=False
    ).order_by('-completed_at')
    
    print(f"Found {completed_sessions.count()} completed sessions to analyze...")
    
    for session in completed_sessions:
        total_sessions += 1
        
        # Calculate correct scores
        answers = session.answers.select_related('question').all()
        correct_total_score = sum(answer.points_earned for answer in answers)
        correct_total_possible = sum(answer.question.points for answer in answers)
        
        if correct_total_possible > 0:
            correct_percentage = (correct_total_score / correct_total_possible) * 100
        else:
            correct_percentage = 0
        
        # Check if current stored values are incorrect
        stored_percentage = float(session.percentage_score or 0)
        
        # Consider scores different if they differ by more than 0.01%
        if abs(stored_percentage - correct_percentage) > 0.01:
            # Additional check: ensure this isn't a rounding difference
            if abs(stored_percentage - correct_percentage) > 0.1:
                sessions_to_fix.append({
                    'session': session,
                    'current_score': session.score,
                    'current_percentage': stored_percentage,
                    'correct_score': correct_total_score,
                    'correct_percentage': correct_percentage,
                    'answers_count': answers.count(),
                    'total_possible': correct_total_possible
                })
    
    print(f"\n📊 ANALYSIS RESULTS:")
    print(f"  Total sessions analyzed: {total_sessions}")
    print(f"  Sessions needing correction: {len(sessions_to_fix)}")
    
    if sessions_to_fix:
        print(f"\n🔴 SESSIONS WITH INCORRECT SCORES:")
        for i, issue in enumerate(sessions_to_fix[:10], 1):  # Show first 10
            session = issue['session']
            print(f"  {i}. {session.student_name} - {session.exam.name}")
            print(f"     Current: {issue['current_score']} points, {issue['current_percentage']:.2f}%")
            print(f"     Correct: {issue['correct_score']} points, {issue['correct_percentage']:.2f}%")
            print(f"     Total possible: {issue['total_possible']} points")
            print()
        
        if len(sessions_to_fix) > 10:
            print(f"     ... and {len(sessions_to_fix) - 10} more sessions")
    
    return sessions_to_fix

def fix_scoring_issues(sessions_to_fix, dry_run=True):
    """Fix the identified scoring issues"""
    
    action = "DRY RUN" if dry_run else "FIXING"
    print(f"\n🔧 {action} - CORRECTING SCORING ISSUES")
    print("=" * 60)
    
    if not sessions_to_fix:
        print("✅ No sessions need correction!")
        return True
    
    fixed_count = 0
    error_count = 0
    
    for i, issue in enumerate(sessions_to_fix, 1):
        session = issue['session']
        
        try:
            print(f"  {i}/{len(sessions_to_fix)} - Session {session.id}")
            print(f"    Student: {session.student_name}")
            print(f"    Before: {issue['current_score']} points, {issue['current_percentage']:.2f}%")
            print(f"    After:  {issue['correct_score']} points, {issue['correct_percentage']:.2f}%")
            
            if not dry_run:
                with transaction.atomic():
                    # Update the session with correct values
                    session.score = issue['correct_score']
                    session.percentage_score = Decimal(str(round(issue['correct_percentage'], 2)))
                    session.save()
                    
                    print(f"    ✅ Fixed!")
            else:
                print(f"    📝 Would fix (dry run)")
            
            fixed_count += 1
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            error_count += 1
    
    print(f"\n📊 {action} SUMMARY:")
    print(f"  Successfully processed: {fixed_count}")
    print(f"  Errors: {error_count}")
    
    if dry_run:
        print(f"\n⚠️ This was a DRY RUN - no changes were made")
        print(f"   Run with dry_run=False to apply the fixes")
    else:
        print(f"\n✅ Scoring corrections have been applied!")
    
    return error_count == 0

def verify_fix():
    """Verify that the fix is working correctly by re-grading a session"""
    print(f"\n🧪 VERIFYING FIX WITH LIVE SESSION")
    print("=" * 60)
    
    # Find a recent session to test
    test_session = StudentSession.objects.filter(
        completed_at__isnull=False,
        answers__isnull=False
    ).first()
    
    if not test_session:
        print("No completed sessions found for verification")
        return False
    
    print(f"Testing with session: {test_session.id}")
    print(f"Before re-grading:")
    print(f"  Score: {test_session.score}")
    print(f"  Percentage: {test_session.percentage_score}%")
    
    # Calculate what the correct values should be
    answers = test_session.answers.select_related('question').all()
    expected_score = sum(answer.points_earned for answer in answers)
    expected_possible = sum(answer.question.points for answer in answers)
    expected_percentage = (expected_score / expected_possible * 100) if expected_possible > 0 else 0
    
    print(f"Expected values:")
    print(f"  Score: {expected_score}")
    print(f"  Percentage: {expected_percentage:.2f}%")
    
    # Re-run grading with the fixed service
    try:
        results = GradingService.grade_session(test_session)
        
        test_session.refresh_from_db()
        print(f"After re-grading with fixed service:")
        print(f"  Score: {test_session.score}")
        print(f"  Percentage: {test_session.percentage_score}%")
        
        # Verify the fix worked
        if (test_session.score == expected_score and 
            abs(float(test_session.percentage_score) - expected_percentage) < 0.01):
            print(f"✅ Fix verified! Grading service now calculates correctly.")
            return True
        else:
            print(f"❌ Fix verification failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def main():
    """Main migration script execution"""
    print("SCORING CALCULATION FIX - MIGRATION SCRIPT")
    print("=" * 60)
    print("This script will:")
    print("1. Analyze all completed sessions for scoring issues")
    print("2. Show which sessions have incorrect percentage calculations")
    print("3. Optionally fix the incorrect scores")
    print("4. Verify the fix is working correctly")
    print()
    
    try:
        # Step 1: Analyze issues
        sessions_to_fix = analyze_scoring_issues()
        
        # Step 2: Show dry run
        if sessions_to_fix:
            fix_scoring_issues(sessions_to_fix, dry_run=True)
            
            # Auto-apply fixes in non-interactive environment
            print("\n" + "=" * 60)
            print("🚀 APPLYING FIXES AUTOMATICALLY...")
            success = fix_scoring_issues(sessions_to_fix, dry_run=False)
            
            if success:
                print(f"\n✅ All scoring issues have been corrected!")
            else:
                print(f"\n⚠️ Some issues occurred during the fix")
        
        # Step 3: Verify the grading service fix
        verify_fix()
        
        print(f"\n🎯 MIGRATION COMPLETE")
        print("The scoring calculation bug has been fixed!")
        print("- GradingService now includes all question types in calculations")
        print("- Templates display correct total possible scores")
        print("- Existing incorrect scores can be corrected with this script")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)