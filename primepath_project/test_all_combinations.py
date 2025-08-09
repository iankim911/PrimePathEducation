#!/usr/bin/env python
"""
Comprehensive test of ALL question type combinations and permutations.
Tests every possible configuration to identify any issues.
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from placement_test.models import Question, Exam, StudentSession
from placement_test.templatetags.grade_tags import (
    has_multiple_answers, get_answer_letters, get_mixed_components, is_mixed_question
)


def test_all_combinations():
    """Test ALL question type combinations systematically."""
    
    issues_found = []
    test_results = []
    
    print("\n" + "="*80)
    print("COMPREHENSIVE TESTING OF ALL QUESTION TYPE COMBINATIONS")
    print("="*80)
    
    # ========== MCQ VARIATIONS ==========
    print("\n" + "="*40)
    print("MCQ VARIATIONS")
    print("="*40)
    
    # Test 1.1: Single MCQ
    print("\n[1.1] Single MCQ (Radio buttons)")
    single_mcq = Question.objects.filter(
        question_type='MCQ'
    ).exclude(correct_answer__contains=',').first()
    
    if single_mcq:
        result = analyze_question(single_mcq)
        print(result)
        if result.get('issue'):
            issues_found.append(('Single MCQ', result['issue']))
        test_results.append(('Single MCQ', not result.get('issue')))
    
    # Test 1.2: Multiple MCQ
    print("\n[1.2] Multiple MCQ (Checkboxes)")
    multi_mcq = Question.objects.filter(
        question_type='MCQ',
        correct_answer__contains=','
    ).first()
    
    if multi_mcq:
        result = analyze_question(multi_mcq)
        print(result)
        test_results.append(('Multiple MCQ', not result.get('issue')))
    else:
        print("  No multiple MCQ found in database")
        test_results.append(('Multiple MCQ', None))
    
    # ========== SHORT VARIATIONS ==========
    print("\n" + "="*40)
    print("SHORT ANSWER VARIATIONS")
    print("="*40)
    
    # Test 2.1: Single SHORT
    print("\n[2.1] Single SHORT answer")
    single_short = Question.objects.filter(
        question_type='SHORT',
        options_count__lte=1
    ).first()
    
    if single_short:
        result = analyze_question(single_short)
        print(result)
        test_results.append(('Single SHORT', not result.get('issue')))
    
    # Test 2.2: Multiple SHORT with comma
    print("\n[2.2] Multiple SHORT (comma separator)")
    comma_short = Question.objects.filter(
        question_type='SHORT',
        correct_answer__contains=',',
        options_count__gt=1
    ).first()
    
    if comma_short:
        result = analyze_question(comma_short)
        print(result)
        letters = get_answer_letters(comma_short)
        if comma_short.options_count != len(letters):
            issue = f"Mismatch: options_count={comma_short.options_count} but generates {len(letters)} inputs"
            issues_found.append(('Multiple SHORT comma', issue))
            print(f"  ⚠️ ISSUE: {issue}")
        test_results.append(('Multiple SHORT comma', comma_short.options_count == len(letters)))
    
    # Test 2.3: Multiple SHORT with pipe
    print("\n[2.3] Multiple SHORT (pipe separator)")
    pipe_short = Question.objects.filter(
        question_type='SHORT',
        correct_answer__contains='|',
        options_count__gt=1
    ).first()
    
    if pipe_short:
        result = analyze_question(pipe_short)
        print(result)
        letters = get_answer_letters(pipe_short)
        if pipe_short.options_count != len(letters):
            issue = f"Mismatch: options_count={pipe_short.options_count} but generates {len(letters)} inputs"
            issues_found.append(('Multiple SHORT pipe', issue))
            print(f"  ⚠️ ISSUE: {issue}")
        test_results.append(('Multiple SHORT pipe', pipe_short.options_count == len(letters)))
    
    # Test 2.4: SHORT with alternatives (single input, multiple acceptable)
    print("\n[2.4] SHORT with alternatives")
    alt_short = Question.objects.filter(
        question_type='SHORT',
        correct_answer__contains='|',
        options_count__lte=1
    ).first()
    
    if alt_short:
        result = analyze_question(alt_short)
        print(result)
        if has_multiple_answers(alt_short):
            issue = "Single SHORT with alternatives incorrectly treated as multiple"
            issues_found.append(('SHORT alternatives', issue))
            print(f"  ⚠️ ISSUE: {issue}")
        test_results.append(('SHORT alternatives', not has_multiple_answers(alt_short)))
    
    # ========== LONG VARIATIONS ==========
    print("\n" + "="*40)
    print("LONG ANSWER VARIATIONS")
    print("="*40)
    
    # Test 3.1: Single LONG
    print("\n[3.1] Single LONG answer")
    single_long = Question.objects.filter(
        question_type='LONG',
        options_count__lte=1
    ).first()
    
    if single_long:
        result = analyze_question(single_long)
        print(result)
        test_results.append(('Single LONG', not result.get('issue')))
    
    # Test 3.2: Multiple LONG
    print("\n[3.2] Multiple LONG answers")
    multi_long = Question.objects.filter(
        question_type='LONG',
        options_count__gt=1
    ).first()
    
    if multi_long:
        result = analyze_question(multi_long)
        print(result)
        # Check if multiple textareas would be generated
        if has_multiple_answers(multi_long):
            print("  ✓ Would show multiple textareas")
        else:
            issue = "Multiple LONG not showing multiple textareas"
            issues_found.append(('Multiple LONG', issue))
            print(f"  ⚠️ ISSUE: {issue}")
        test_results.append(('Multiple LONG', has_multiple_answers(multi_long)))
    
    # ========== CHECKBOX VARIATIONS ==========
    print("\n" + "="*40)
    print("CHECKBOX VARIATIONS")
    print("="*40)
    
    # Test 4.1: Standard CHECKBOX
    print("\n[4.1] Standard CHECKBOX")
    checkbox = Question.objects.filter(question_type='CHECKBOX').first()
    
    if checkbox:
        result = analyze_question(checkbox)
        print(result)
        test_results.append(('CHECKBOX', not result.get('issue')))
    
    # ========== MIXED VARIATIONS ==========
    print("\n" + "="*40)
    print("MIXED TYPE VARIATIONS")
    print("="*40)
    
    # Test 5.1: All MIXED questions
    print("\n[5.1] MIXED questions analysis")
    mixed_questions = Question.objects.filter(question_type='MIXED')
    
    for i, mixed_q in enumerate(mixed_questions[:5], 1):
        print(f"\n  Mixed Question {i}:")
        result = analyze_question(mixed_q)
        print(f"    {result}")
        
        components = get_mixed_components(mixed_q)
        print(f"    Components: {len(components)}")
        
        # Check if components match options_count
        if len(components) != mixed_q.options_count:
            issue = f"MIXED Q{mixed_q.id}: components={len(components)} != options_count={mixed_q.options_count}"
            issues_found.append((f'MIXED {i}', issue))
            print(f"    ⚠️ ISSUE: {issue}")
        
        # Check if all components are inputs (as per our fix)
        non_input = [c for c in components if c['type'] != 'input']
        if non_input:
            issue = f"MIXED Q{mixed_q.id}: Non-input components found: {non_input}"
            issues_found.append((f'MIXED {i} types', issue))
            print(f"    ⚠️ ISSUE: {issue}")
        
        test_results.append((f'MIXED {i}', len(components) == mixed_q.options_count and not non_input))
    
    # ========== EDGE CASES ==========
    print("\n" + "="*40)
    print("EDGE CASES & SPECIAL SCENARIOS")
    print("="*40)
    
    # Test 6.1: Empty correct_answer with options_count > 1
    print("\n[6.1] Empty correct_answer with options_count > 1")
    empty_multi = Question.objects.filter(
        correct_answer='',
        options_count__gt=1
    ).first()
    
    if empty_multi:
        result = analyze_question(empty_multi)
        print(result)
        letters = get_answer_letters(empty_multi)
        if len(letters) == empty_multi.options_count:
            print(f"  ✓ Correctly generates {empty_multi.options_count} letters")
        else:
            issue = f"Empty answer: Expected {empty_multi.options_count} letters, got {len(letters)}"
            issues_found.append(('Empty multi', issue))
            print(f"  ⚠️ ISSUE: {issue}")
        test_results.append(('Empty multi', len(letters) == empty_multi.options_count))
    
    # Test 6.2: Special characters in answers
    print("\n[6.2] Special characters in answers")
    special_chars = Question.objects.filter(
        correct_answer__regex=r'[,|;:]'
    ).exclude(question_type='MIXED')[:3]
    
    for q in special_chars:
        print(f"  Q{q.id} ({q.question_type}): \"{q.correct_answer[:50]}...\"")
        if ',' in q.correct_answer and '|' in q.correct_answer:
            print("    Contains both comma and pipe - potential parsing issue")
            issues_found.append(('Special chars', f'Q{q.id} has both comma and pipe'))
    
    # Test 6.3: Very high options_count
    print("\n[6.3] Very high options_count")
    high_options = Question.objects.filter(options_count__gte=5).first()
    
    if high_options:
        result = analyze_question(high_options)
        print(result)
        if high_options.options_count > 10:
            print(f"  ⚠️ WARNING: options_count={high_options.options_count} exceeds available letters (A-J)")
            issues_found.append(('High options', f'Q{high_options.id} has {high_options.options_count} options'))
    
    # ========== TEMPLATE RENDERING TEST ==========
    print("\n" + "="*40)
    print("TEMPLATE RENDERING VERIFICATION")
    print("="*40)
    
    client = Client()
    
    # Test actual rendering for problematic questions
    if issues_found:
        print("\n[7.1] Testing template rendering for questions with issues")
        
        # Get a session for testing
        session = StudentSession.objects.first()
        if session:
            response = client.get(reverse('placement_test:take_test', args=[session.id]))
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                print("  Template rendered successfully")
                
                # Check for specific issue patterns
                for issue_type, issue_desc in issues_found[:3]:  # Test first 3 issues
                    print(f"  Checking: {issue_type}")
                    # Basic check for input fields
                    input_count = content.count('type="text"')
                    checkbox_count = content.count('type="checkbox"')
                    radio_count = content.count('type="radio"')
                    textarea_count = content.count('<textarea')
                    
                    print(f"    Inputs: {input_count}, Checkboxes: {checkbox_count}, Radios: {radio_count}, Textareas: {textarea_count}")
    
    # ========== SUMMARY ==========
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if issues_found:
        print("\n⚠️ ISSUES FOUND:")
        for issue_type, issue_desc in issues_found:
            print(f"  • {issue_type}: {issue_desc}")
    else:
        print("\n✅ NO ISSUES FOUND")
    
    print("\n📊 Test Results:")
    passed = sum(1 for _, result in test_results if result is True)
    failed = sum(1 for _, result in test_results if result is False)
    skipped = sum(1 for _, result in test_results if result is None)
    
    for test_name, result in test_results:
        if result is True:
            print(f"  ✅ {test_name}")
        elif result is False:
            print(f"  ❌ {test_name}")
        else:
            print(f"  ⏭️ {test_name} (skipped/not found)")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    return issues_found


def analyze_question(question):
    """Analyze a single question for potential issues."""
    result = {
        'id': question.id,
        'type': question.question_type,
        'options_count': question.options_count,
        'correct_answer': str(question.correct_answer)[:50] + ('...' if len(str(question.correct_answer)) > 50 else ''),
        'has_multiple': has_multiple_answers(question),
    }
    
    # Check for common issues
    if question.question_type in ['SHORT', 'MIXED']:
        letters = get_answer_letters(question)
        result['letters'] = letters
        
        if question.options_count > 1 and len(letters) != question.options_count:
            result['issue'] = f"Letter count mismatch: {len(letters)} != {question.options_count}"
    
    if question.question_type == 'MIXED':
        components = get_mixed_components(question)
        result['components'] = len(components)
        
        if len(components) != question.options_count:
            result['issue'] = f"Component count mismatch: {len(components)} != {question.options_count}"
    
    return result


if __name__ == "__main__":
    issues = test_all_combinations()
    
    if issues:
        print("\n" + "="*80)
        print("ANALYSIS & RECOMMENDATIONS")
        print("="*80)
        
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        print("1. MIXED questions: All converted to text inputs regardless of JSON structure")
        print("2. SHORT questions: Prioritizing options_count over correct_answer format")
        print("3. LONG questions: Not checking for multiple textareas support")
        print("4. Special characters: May cause parsing conflicts (comma vs pipe)")
        
        print("\n🎯 AFFECTED AREAS:")
        print("• Template filters (grade_tags.py)")
        print("• Student test template (student_test.html)")
        print("• Grading service (may expect different formats)")
        print("• Control panel save logic")
        
        print("\n📋 FIX PLAN:")
        print("1. Review LONG question multiple textarea support")
        print("2. Add special character escaping")
        print("3. Ensure grading compatibility with all formats")
        print("4. Add validation for options_count > 10")
        
        sys.exit(1)
    else:
        print("\n🎉 All combinations working correctly!")
        sys.exit(0)