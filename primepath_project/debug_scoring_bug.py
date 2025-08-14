#!/usr/bin/env python3
"""
Debug script to analyze the scoring calculation bug.
Traces through the exact calculation that led to the 50% display issue.
"""

import os
import sys
import django
import json

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import StudentSession, StudentAnswer, Question
from placement_test.services.grading_service import GradingService

def analyze_scoring_bug():
    """Analyze the scoring calculation bug in detail"""
    print("🔍 SCORING BUG ANALYSIS")
    print("=" * 60)
    
    # Find sessions with percentage_score that might be wrong
    sessions = StudentSession.objects.filter(
        completed_at__isnull=False,
        score__isnull=False,
        percentage_score__isnull=False
    ).order_by('-completed_at')[:10]
    
    print(f"Analyzing {len(sessions)} recent completed sessions...")
    
    for session in sessions:
        print(f"\n📊 SESSION: {session.student_name} - {session.exam.name}")
        print(f"   Session ID: {session.id}")
        print(f"   Stored Score: {session.score}")
        print(f"   Stored Percentage: {session.percentage_score}%")
        
        # Get all answers for this session
        answers = session.answers.select_related('question').all()
        
        # Calculate manually using the CURRENT grading logic
        total_score_manual = 0
        total_possible_manual = 0
        long_questions_score = 0
        long_questions_possible = 0
        
        print(f"\n   DETAILED BREAKDOWN:")
        for answer in answers:
            question = answer.question
            print(f"   Q{question.question_number} ({question.question_type}): "
                  f"{answer.points_earned}/{question.points} points")
            
            # Current grading logic (the BUG)
            if question.question_type not in ['LONG']:
                total_possible_manual += question.points
                total_score_manual += answer.points_earned
            else:
                long_questions_score += answer.points_earned
                long_questions_possible += question.points
                # BUG: LONG points are added to total_score but not total_possible
                total_score_manual += answer.points_earned  
        
        print(f"\n   CURRENT LOGIC (BUGGY):")
        print(f"   - Non-LONG score: {total_score_manual - long_questions_score}")
        print(f"   - Non-LONG possible: {total_possible_manual}")
        print(f"   - LONG score: {long_questions_score} (added to total_score)")
        print(f"   - LONG possible: {long_questions_possible} (NOT added to total_possible)")
        print(f"   - Total score used: {total_score_manual}")
        print(f"   - Total possible used: {total_possible_manual}")
        
        if total_possible_manual > 0:
            calculated_percentage = (total_score_manual / total_possible_manual) * 100
            print(f"   - Calculated percentage: {calculated_percentage:.2f}%")
            print(f"   - Stored percentage: {session.percentage_score}%")
            
            if abs(float(session.percentage_score) - calculated_percentage) > 0.01:
                print(f"   ⚠️ PERCENTAGE MISMATCH!")
        
        # Calculate CORRECT logic
        correct_total_score = sum(answer.points_earned for answer in answers)
        correct_total_possible = sum(answer.question.points for answer in answers)
        
        print(f"\n   CORRECT LOGIC (FIXED):")
        print(f"   - Total score: {correct_total_score}")
        print(f"   - Total possible: {correct_total_possible}")
        
        if correct_total_possible > 0:
            correct_percentage = (correct_total_score / correct_total_possible) * 100
            print(f"   - Correct percentage: {correct_percentage:.2f}%")
            
            if abs(float(session.percentage_score) - correct_percentage) > 0.01:
                print(f"   🔴 BUG DETECTED: Stored {session.percentage_score}% vs Correct {correct_percentage:.2f}%")
                
                # Check for the 50% vs 200% inversion pattern
                if abs(float(session.percentage_score) - (correct_total_possible / correct_total_score * 100)) < 0.01:
                    print(f"   🎯 FOUND INVERSION PATTERN: Formula is inverted!")
                    print(f"      Should be: {correct_total_score}/{correct_total_possible} = {correct_percentage:.2f}%")
                    print(f"      Actually:  {correct_total_possible}/{correct_total_score} = {session.percentage_score}%")
        
        print("-" * 60)

def test_grading_service_directly():
    """Test the grading service with a known session"""
    print("\n🧪 TESTING GRADING SERVICE DIRECTLY")
    print("=" * 60)
    
    # Find a recent session to test
    session = StudentSession.objects.filter(
        completed_at__isnull=False,
        answers__isnull=False
    ).first()
    
    if not session:
        print("No completed sessions found for testing")
        return
    
    print(f"Testing session: {session.id}")
    print(f"Current stored values:")
    print(f"  Score: {session.score}")
    print(f"  Percentage: {session.percentage_score}%")
    
    # Backup original values
    original_score = session.score
    original_percentage = session.percentage_score
    
    # Re-run grading service
    print(f"\nRe-running GradingService.grade_session()...")
    results = GradingService.grade_session(session)
    
    print(f"GradingService results:")
    print(f"  total_score: {results['total_score']}")
    print(f"  total_possible: {results['total_possible']}")
    print(f"  percentage_score: {results['percentage_score']:.2f}%")
    
    # Check if values changed
    session.refresh_from_db()
    print(f"\nAfter re-grading:")
    print(f"  Score: {session.score}")
    print(f"  Percentage: {session.percentage_score}%")
    
    if session.score != original_score or session.percentage_score != original_percentage:
        print("🔴 VALUES CHANGED! This confirms inconsistent calculation.")
    else:
        print("✅ Values remained the same.")

def examine_template_data():
    """Check what data is actually passed to the template"""
    print("\n📄 EXAMINING TEMPLATE DATA")
    print("=" * 60)
    
    # Find a session with the issue
    session = StudentSession.objects.filter(
        completed_at__isnull=False,
        percentage_score__isnull=False
    ).first()
    
    if not session:
        print("No sessions found")
        return
    
    print(f"Session: {session.id}")
    print(f"Template will receive:")
    print(f"  session.score: {session.score}")
    print(f"  session.percentage_score: {session.percentage_score}")
    
    # Check if total_possible_score exists
    if hasattr(session, 'total_possible_score'):
        print(f"  session.total_possible_score: {session.total_possible_score}")
    else:
        print(f"  session.total_possible_score: DOES NOT EXIST")
    
    # Check detailed results
    try:
        results = GradingService.get_detailed_results(str(session.id))
        print(f"\nDetailed results:")
        for key, value in results.items():
            if key != 'type_performance':  # Skip complex nested data
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error getting detailed results: {e}")

def main():
    """Run all analysis"""
    try:
        analyze_scoring_bug()
        test_grading_service_directly()
        examine_template_data()
        
        print("\n🎯 SUMMARY")
        print("=" * 60)
        print("The bug analysis reveals the core issue in GradingService.grade_session():")
        print("1. LONG questions are excluded from total_possible calculation")
        print("2. BUT LONG question points are still added to total_score")
        print("3. This creates an inflated numerator with deflated denominator")
        print("4. May also have inversion where formula is (possible/earned) instead of (earned/possible)")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()