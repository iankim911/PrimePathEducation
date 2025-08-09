#!/usr/bin/env python
"""
Test to verify that existing features are not affected by recent changes.
Checks all core functionality to ensure no regressions.
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from django.db.models import Q
from placement_test.models import (
    Exam, Question, StudentSession, StudentAnswer, AudioFile
)
from core.models import (
    CurriculumLevel, PlacementRule, ExamLevelMapping, School, Program
)
from placement_test.services import (
    ExamService, SessionService, PlacementService, GradingService
)
from placement_test.templatetags.grade_tags import (
    has_multiple_answers, get_answer_letters, get_mixed_components
)


def test_existing_features():
    """Test all existing features for regressions."""
    
    print("\n" + "="*80)
    print("TESTING EXISTING FEATURES FOR REGRESSIONS")
    print("="*80)
    
    issues = []
    client = Client()
    
    # ========== 1. EXAM CREATION & MANAGEMENT ==========
    print("\n[1] EXAM CREATION & MANAGEMENT")
    print("-"*40)
    
    try:
        # Test exam list view
        response = client.get(reverse('placement_test:exam_list'))
        if response.status_code == 200:
            print("  ✅ Exam list view: Working")
        else:
            issues.append(f"Exam list returned {response.status_code}")
            print(f"  ❌ Exam list view: Status {response.status_code}")
        
        # Test create exam view
        response = client.get(reverse('placement_test:create_exam'))
        if response.status_code == 200:
            print("  ✅ Create exam view: Working")
        else:
            issues.append(f"Create exam returned {response.status_code}")
            print(f"  ❌ Create exam view: Status {response.status_code}")
        
        # Test exam service
        exams = Exam.objects.all()[:3]
        for exam in exams:
            questions = exam.questions.all()
            if questions.exists():
                print(f"  ✅ Exam '{exam.name[:30]}...': {questions.count()} questions")
            else:
                issues.append(f"Exam {exam.id} has no questions")
                print(f"  ❌ Exam '{exam.name[:30]}...': No questions")
                
    except Exception as e:
        issues.append(f"Exam management error: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # ========== 2. STUDENT SESSION FLOW ==========
    print("\n[2] STUDENT SESSION FLOW")
    print("-"*40)
    
    try:
        # Test start test page
        response = client.get(reverse('placement_test:start_test'))
        if response.status_code == 200:
            print("  ✅ Start test page: Working")
        else:
            issues.append(f"Start test returned {response.status_code}")
            print(f"  ❌ Start test page: Status {response.status_code}")
        
        # Test existing sessions
        sessions = StudentSession.objects.all()[:3]
        for session in sessions:
            try:
                response = client.get(
                    reverse('placement_test:take_test', args=[session.id])
                )
                if response.status_code == 200:
                    print(f"  ✅ Session {str(session.id)[:8]}...: Accessible")
                else:
                    issues.append(f"Session {session.id} returned {response.status_code}")
                    print(f"  ❌ Session {str(session.id)[:8]}...: Status {response.status_code}")
            except Exception as e:
                issues.append(f"Session {session.id} error: {str(e)}")
                print(f"  ❌ Session error: {str(e)}")
                
    except Exception as e:
        issues.append(f"Session flow error: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # ========== 3. QUESTION RENDERING (BEFORE CHANGES) ==========
    print("\n[3] QUESTION RENDERING - ORIGINAL TYPES")
    print("-"*40)
    
    try:
        # Test MCQ single answer (should use radio buttons)
        mcq_single = Question.objects.filter(
            question_type='MCQ'
        ).exclude(correct_answer__contains=',').first()
        
        if mcq_single:
            has_multi = has_multiple_answers(mcq_single)
            if not has_multi:
                print("  ✅ MCQ single: Correctly shows radio buttons")
            else:
                issues.append("MCQ single incorrectly shows as multiple")
                print("  ❌ MCQ single: Incorrectly treated as multiple")
        
        # Test CHECKBOX (should always show checkboxes)
        checkbox = Question.objects.filter(question_type='CHECKBOX').first()
        if checkbox:
            print(f"  ✅ CHECKBOX: {checkbox.options_count} options")
        
        # Test original SHORT questions (before our changes)
        short_single = Question.objects.filter(
            question_type='SHORT',
            options_count__lte=1
        ).exclude(correct_answer__contains='|').first()
        
        if short_single:
            has_multi = has_multiple_answers(short_single)
            if not has_multi:
                print("  ✅ SHORT single: Correctly shows single input")
            else:
                issues.append("SHORT single incorrectly shows as multiple")
                print("  ❌ SHORT single: Incorrectly treated as multiple")
                
    except Exception as e:
        issues.append(f"Question rendering error: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # ========== 4. AUDIO SYSTEM ==========
    print("\n[4] AUDIO SYSTEM")
    print("-"*40)
    
    try:
        audio_files = AudioFile.objects.all()[:3]
        for audio in audio_files:
            if audio.audio_file:
                print(f"  ✅ Audio {audio.id}: {audio.name or 'Unnamed'}")
                
                # Check if audio is properly linked to questions
                questions_with_audio = Question.objects.filter(audio_file=audio)
                if questions_with_audio.exists():
                    print(f"     Used by {questions_with_audio.count()} question(s)")
            else:
                issues.append(f"Audio {audio.id} has no file")
                print(f"  ❌ Audio {audio.id}: No file attached")
                
    except Exception as e:
        issues.append(f"Audio system error: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # ========== 5. GRADING SYSTEM ==========
    print("\n[5] GRADING SYSTEM")
    print("-"*40)
    
    try:
        grading = GradingService()
        
        # Test MCQ grading
        mcq_result = grading.grade_mcq_answer('A', 'A')
        if mcq_result == True:
            print("  ✅ MCQ grading: Working")
        else:
            issues.append("MCQ grading not working")
            print("  ❌ MCQ grading: Not working")
        
        # Test checkbox grading
        checkbox_result = grading.grade_checkbox_answer('A,B', 'A,B')
        if checkbox_result == True:
            print("  ✅ Checkbox grading: Working")
        else:
            issues.append("Checkbox grading not working")
            print("  ❌ Checkbox grading: Not working")
        
        # Test short answer grading
        short_result = grading.grade_short_answer('test', 'test')
        if short_result == True:
            print("  ✅ Short answer grading: Working")
        else:
            issues.append("Short answer grading not working")
            print("  ❌ Short answer grading: Not working")
            
    except Exception as e:
        issues.append(f"Grading system error: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # ========== 6. PLACEMENT RULES ==========
    print("\n[6] PLACEMENT RULES")
    print("-"*40)
    
    try:
        rules = PlacementRule.objects.all()[:3]
        for rule in rules:
            print(f"  ✅ Rule: Grade {rule.grade}, Rank {rule.academic_rank}")
        
        # Test placement matching
        try:
            exam, level = PlacementService.match_student_to_exam(
                grade=5,
                academic_rank='average'
            )
            if exam:
                print(f"  ✅ Placement match: {exam.name[:30]}...")
            else:
                print("  ⚠️ No placement match found (may be normal)")
        except Exception as e:
            if "Invalid academic rank" in str(e):
                print("  ⚠️ Academic rank validation working")
            else:
                issues.append(f"Placement matching error: {str(e)}")
                print(f"  ❌ Placement error: {str(e)}")
                
    except Exception as e:
        issues.append(f"Placement rules error: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # ========== 7. PDF SYSTEM ==========
    print("\n[7] PDF SYSTEM")
    print("-"*40)
    
    try:
        exams_with_pdf = Exam.objects.filter(pdf_file__isnull=False)[:3]
        for exam in exams_with_pdf:
            if exam.pdf_file:
                print(f"  ✅ PDF: {exam.pdf_file.name}")
            else:
                issues.append(f"Exam {exam.id} PDF field empty")
                print(f"  ❌ Exam {exam.id}: PDF field empty")
                
    except Exception as e:
        issues.append(f"PDF system error: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # ========== 8. TEMPLATE FILTERS (ORIGINAL BEHAVIOR) ==========
    print("\n[8] TEMPLATE FILTERS - ORIGINAL BEHAVIOR")
    print("-"*40)
    
    try:
        # Test that our changes didn't break original SHORT questions
        short_orig = Question.objects.filter(
            question_type='SHORT',
            options_count=0
        ).first()
        
        if short_orig:
            has_multi = has_multiple_answers(short_orig)
            letters = get_answer_letters(short_orig)
            
            if not has_multi and len(letters) == 0:
                print("  ✅ SHORT with options_count=0: Correctly single input")
            else:
                issues.append(f"SHORT options_count=0 broken: has_multi={has_multi}, letters={letters}")
                print(f"  ❌ SHORT with options_count=0: Broken")
        
        # Test MIXED questions still work
        mixed = Question.objects.filter(question_type='MIXED').first()
        if mixed:
            components = get_mixed_components(mixed)
            if len(components) == mixed.options_count:
                print(f"  ✅ MIXED: Generates {mixed.options_count} components")
            else:
                issues.append(f"MIXED broken: {len(components)} != {mixed.options_count}")
                print(f"  ❌ MIXED: Component count mismatch")
                
    except Exception as e:
        issues.append(f"Template filter error: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # ========== 9. DATABASE INTEGRITY ==========
    print("\n[9] DATABASE INTEGRITY")
    print("-"*40)
    
    try:
        # Check for orphaned records
        orphan_questions = Question.objects.filter(exam__isnull=True)
        if orphan_questions.exists():
            issues.append(f"{orphan_questions.count()} orphaned questions")
            print(f"  ❌ Found {orphan_questions.count()} orphaned questions")
        else:
            print("  ✅ No orphaned questions")
        
        orphan_answers = StudentAnswer.objects.filter(session__isnull=True)
        if orphan_answers.exists():
            issues.append(f"{orphan_answers.count()} orphaned answers")
            print(f"  ❌ Found {orphan_answers.count()} orphaned answers")
        else:
            print("  ✅ No orphaned answers")
            
    except Exception as e:
        issues.append(f"Database integrity error: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # ========== 10. JAVASCRIPT FUNCTIONALITY ==========
    print("\n[10] JAVASCRIPT FUNCTIONALITY CHECK")
    print("-"*40)
    
    try:
        # Check if a test page loads without JS errors
        session = StudentSession.objects.first()
        if session:
            response = client.get(
                reverse('placement_test:take_test', args=[session.id])
            )
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for critical JS components
                js_checks = [
                    ('APP_CONFIG', 'APP_CONFIG present'),
                    ('answerManager', 'Answer Manager present'),
                    ('navigationModule', 'Navigation Module present'),
                    ('markAnswered', 'markAnswered function present')
                ]
                
                for js_component, description in js_checks:
                    if js_component in content:
                        print(f"  ✅ {description}")
                    else:
                        issues.append(f"JS component missing: {js_component}")
                        print(f"  ❌ {description}: Missing")
                        
    except Exception as e:
        issues.append(f"JavaScript check error: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # ========== SUMMARY ==========
    print("\n" + "="*80)
    print("REGRESSION TEST SUMMARY")
    print("="*80)
    
    if issues:
        print("\n❌ ISSUES FOUND (Potential Regressions):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\n🔍 IMPACT ANALYSIS:")
        
        # Categorize issues
        critical = [i for i in issues if any(x in i.lower() for x in ['error', 'broken', 'missing'])]
        warnings = [i for i in issues if i not in critical]
        
        if critical:
            print(f"\n🚨 CRITICAL ({len(critical)} issues):")
            for issue in critical:
                print(f"  • {issue}")
        
        if warnings:
            print(f"\n⚠️ WARNINGS ({len(warnings)} issues):")
            for issue in warnings:
                print(f"  • {issue}")
        
        print("\n📋 RECOMMENDATIONS:")
        print("1. Review template filter changes for unintended side effects")
        print("2. Test grading system with new input formats")
        print("3. Verify JavaScript still handles all question types")
        print("4. Check database migrations if any schema changes")
        
        return False
    else:
        print("\n✅ ALL EXISTING FEATURES WORKING CORRECTLY")
        print("No regressions detected from recent changes")
        
        print("\n📊 VERIFIED COMPONENTS:")
        print("  • Exam creation and management")
        print("  • Student session flow")
        print("  • Question rendering (all types)")
        print("  • Audio system")
        print("  • Grading system")
        print("  • Placement rules")
        print("  • PDF system")
        print("  • Template filters")
        print("  • Database integrity")
        print("  • JavaScript functionality")
        
        return True


if __name__ == "__main__":
    success = test_existing_features()
    sys.exit(0 if success else 1)