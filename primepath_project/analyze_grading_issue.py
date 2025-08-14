#!/usr/bin/env python3
"""
Analyze why student is getting 75% despite copying all correct answers
"""

import os
import sys
import django
import json

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import StudentSession, Question, StudentAnswer, Exam
from placement_test.services.grading_service import GradingService

print("="*60)
print("GRADING ISSUE ANALYSIS - 75% DESPITE CORRECT ANSWERS")
print("="*60)

# Get the most recent session
recent_session = StudentSession.objects.filter(
    completed_at__isnull=False,
    percentage_score__gt=0
).order_by('-completed_at').first()

if recent_session:
    print(f"\nAnalyzing Session: {recent_session.id}")
    print(f"Student: {recent_session.student_name}")
    print(f"Exam: {recent_session.exam.name}")
    print(f"Score: {recent_session.percentage_score:.1f}%")
    # Calculate total points
    total_points = sum(q.points for q in recent_session.exam.questions.all())
    print(f"Points: {recent_session.score}/{total_points}")
    
    # Analyze exam questions
    print("\n" + "="*40)
    print("EXAM QUESTION BREAKDOWN")
    print("="*40)
    
    questions = recent_session.exam.questions.all().order_by('question_number')
    question_types = {}
    for q in questions:
        if q.question_type not in question_types:
            question_types[q.question_type] = {'count': 0, 'points': 0}
        question_types[q.question_type]['count'] += 1
        question_types[q.question_type]['points'] += q.points
    
    total_points_excluding_long = 0
    for q_type, data in question_types.items():
        print(f"{q_type}: {data['count']} questions, {data['points']} points", end="")
        if q_type == 'LONG':
            print(" [EXCLUDED FROM SCORING]")
        else:
            total_points_excluding_long += data['points']
            print()
    
    print(f"\nTotal Points (excluding LONG): {total_points_excluding_long}")
    print(f"Total Points (including LONG): {total_points}")
    
    # Analyze student answers
    print("\n" + "="*40)
    print("STUDENT ANSWER ANALYSIS")
    print("="*40)
    
    answers = recent_session.answers.select_related('question').all().order_by('question__question_number')
    
    correct_count = 0
    incorrect_count = 0
    points_earned = 0
    points_missed = 0
    
    print("\nDetailed Question Analysis:")
    print("-" * 40)
    
    for answer in answers:
        q = answer.question
        if q.question_type != 'LONG':
            print(f"\nQ{q.question_number} ({q.question_type}):")
            print(f"  Points: {q.points}")
            print(f"  Student Answer: '{answer.answer[:50]}...' " if answer.answer else "  Student Answer: [None]")
            print(f"  Correct Answer: '{q.correct_answer[:50]}...' " if q.correct_answer else "  Correct Answer: [None]")
            
            # Re-grade to check
            grade_result = GradingService.auto_grade_answer(answer)
            print(f"  Is Correct: {answer.is_correct} (Auto-grade: {grade_result['is_correct']})")
            print(f"  Points Earned: {answer.points_earned}")
            
            if answer.is_correct:
                correct_count += 1
                points_earned += answer.points_earned
            else:
                incorrect_count += 1
                points_missed += q.points
    
    # Calculate what percentage should be
    print("\n" + "="*40)
    print("SCORING CALCULATION")
    print("="*40)
    
    print(f"Questions Correct: {correct_count}")
    print(f"Questions Incorrect: {incorrect_count}")
    print(f"Points Earned: {points_earned}")
    print(f"Points Possible (excluding LONG): {total_points_excluding_long}")
    
    if total_points_excluding_long > 0:
        calculated_percentage = (points_earned / total_points_excluding_long) * 100
        print(f"\nCalculated Percentage: {calculated_percentage:.1f}%")
        print(f"Stored Percentage: {recent_session.percentage_score:.1f}%")
        
        if abs(calculated_percentage - recent_session.percentage_score) > 0.1:
            print("\n⚠️ DISCREPANCY DETECTED!")
    
    # Check for specific issues
    print("\n" + "="*40)
    print("POTENTIAL ISSUES")
    print("="*40)
    
    # Check for answer format issues
    format_issues = []
    for answer in answers:
        if answer.question.question_type != 'LONG':
            # Check for frontend format issues
            if ':' in answer.answer and '|' in answer.answer:
                format_issues.append({
                    'question': answer.question.question_number,
                    'type': answer.question.question_type,
                    'answer': answer.answer
                })
    
    if format_issues:
        print("\n⚠️ Answer Format Issues Found:")
        for issue in format_issues:
            print(f"  Q{issue['question']}: Frontend format detected: {issue['answer'][:50]}...")
    
    # Check if 75% matches 3/4 pattern
    if recent_session.percentage_score == 75.0:
        print("\n🔍 75% Analysis:")
        print("  75% suggests 3 out of 4 scoring units")
        print("  This could mean:")
        print("  - 3 out of 4 questions correct")
        print("  - 3 out of 4 points earned")
        print("  - One question consistently graded wrong")
        
        # Find which question might be wrong
        if incorrect_count == 1:
            wrong_answer = next((a for a in answers if not a.is_correct and a.question.question_type != 'LONG'), None)
            if wrong_answer:
                print(f"\n  ❌ The incorrect question is Q{wrong_answer.question.question_number}")
                print(f"     Type: {wrong_answer.question.question_type}")
                print(f"     Student: '{wrong_answer.answer}'")
                print(f"     Expected: '{wrong_answer.question.correct_answer}'")

else:
    print("No completed sessions found to analyze")

print("\n" + "="*60)