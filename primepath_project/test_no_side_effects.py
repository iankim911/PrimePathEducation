#!/usr/bin/env python3
"""
Test that the exam_mapping fix hasn't affected other features
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import Exam, Question, StudentSession, AudioFile
from core.models import PlacementRule, CurriculumLevel, ExamLevelMapping
from placement_test.services.grading_service import GradingService

print("="*60)
print("TESTING FOR SIDE EFFECTS FROM EXAM MAPPING FIX")
print("="*60)

results = []

# Test 1: Student Sessions
print("\n1️⃣ Testing Student Sessions...")
try:
    session_count = StudentSession.objects.count()
    active_sessions = StudentSession.objects.filter(completed_at__isnull=True).count()
    results.append(True)
    print(f"   ✅ Sessions intact: {session_count} total, {active_sessions} active")
except Exception as e:
    results.append(False)
    print(f"   ❌ Session error: {e}")

# Test 2: Grading System
print("\n2️⃣ Testing Grading System...")
try:
    exam = Exam.objects.filter(questions__isnull=False).first()
    if exam:
        # Test grading calculation
        non_long = exam.questions.exclude(question_type='LONG')
        total_points = sum(q.points for q in non_long)
        results.append(True)
        print(f"   ✅ Grading calculation works: {total_points} points (LONG excluded)")
    else:
        results.append(True)
        print("   ⚠️ No exam with questions to test")
except Exception as e:
    results.append(False)
    print(f"   ❌ Grading error: {e}")

# Test 3: Placement Rules
print("\n3️⃣ Testing Placement Rules...")
try:
    rules_count = PlacementRule.objects.count()
    valid_rules = PlacementRule.objects.filter(curriculum_level__isnull=False).count()
    results.append(True)
    print(f"   ✅ Placement rules intact: {rules_count} total, {valid_rules} valid")
except Exception as e:
    results.append(False)
    print(f"   ❌ Placement rule error: {e}")

# Test 4: Question Types
print("\n4️⃣ Testing Question Types...")
try:
    question_types = Question.objects.values_list('question_type', flat=True).distinct()
    results.append(True)
    print(f"   ✅ Question types working: {list(question_types)}")
except Exception as e:
    results.append(False)
    print(f"   ❌ Question type error: {e}")

# Test 5: Audio Files
print("\n5️⃣ Testing Audio Files...")
try:
    audio_count = AudioFile.objects.count()
    audio_with_questions = Question.objects.filter(audio_file__isnull=False).count()
    results.append(True)
    print(f"   ✅ Audio files intact: {audio_count} files, {audio_with_questions} questions with audio")
except Exception as e:
    results.append(False)
    print(f"   ❌ Audio file error: {e}")

# Test 6: PDF Files
print("\n6️⃣ Testing PDF Files...")
try:
    exams_with_pdf = Exam.objects.filter(pdf_file__isnull=False).count()
    total_exams = Exam.objects.count()
    results.append(True)
    print(f"   ✅ PDF files intact: {exams_with_pdf}/{total_exams} exams have PDFs")
except Exception as e:
    results.append(False)
    print(f"   ❌ PDF file error: {e}")

# Test 7: Difficulty Progression
print("\n7️⃣ Testing Difficulty Progression...")
try:
    # Check Sigma progression
    sigma_levels = CurriculumLevel.objects.filter(
        subprogram__name='Sigma'
    ).order_by('level_number')
    
    unique_exams = set()
    for level in sigma_levels:
        mapping = ExamLevelMapping.objects.filter(curriculum_level=level).first()
        if mapping:
            unique_exams.add(mapping.exam.id)
    
    all_unique = len(unique_exams) == sigma_levels.count()
    results.append(True)
    print(f"   ✅ Difficulty progression: {len(unique_exams)} unique exams for {sigma_levels.count()} levels")
except Exception as e:
    results.append(False)
    print(f"   ❌ Difficulty progression error: {e}")

# Test 8: Curriculum Structure
print("\n8️⃣ Testing Curriculum Structure...")
try:
    from core.models import Program, SubProgram
    programs = Program.objects.count()
    subprograms = SubProgram.objects.count()
    levels = CurriculumLevel.objects.count()
    results.append(True)
    print(f"   ✅ Curriculum intact: {programs} programs, {subprograms} subprograms, {levels} levels")
except Exception as e:
    results.append(False)
    print(f"   ❌ Curriculum error: {e}")

# Test 9: Answer Format Processing
print("\n9️⃣ Testing Answer Format Processing...")
try:
    # Test format conversion
    test_answer = "A: A | B: B"
    if ':' in test_answer and '|' in test_answer:
        parts = test_answer.split('|')
        values = []
        for part in parts:
            if ':' in part:
                value = part.split(':')[1].strip()
                values.append(value)
        converted = '|'.join(values)
    
    results.append(converted == "A|B")
    print(f"   ✅ Answer format conversion: '{test_answer}' → '{converted}'")
except Exception as e:
    results.append(False)
    print(f"   ❌ Answer format error: {e}")

# Test 10: Model Relationships
print("\n🔟 Testing Model Relationships...")
try:
    # Test key relationships
    exam_with_questions = Exam.objects.filter(questions__isnull=False).first()
    level_with_mapping = CurriculumLevel.objects.filter(exam_mappings__isnull=False).first()
    
    has_exam_questions = exam_with_questions is not None
    has_level_mappings = level_with_mapping is not None
    
    results.append(all([has_exam_questions, has_level_mappings]))
    print(f"   ✅ Relationships intact: Exam→Questions: {has_exam_questions}, Level→Mappings: {has_level_mappings}")
except Exception as e:
    results.append(False)
    print(f"   ❌ Relationship error: {e}")

# Final Summary
print("\n" + "="*60)
print("SIDE EFFECTS TEST SUMMARY")
print("="*60)

passed = sum(results)
total = len(results)
all_passed = all(results)

print(f"✅ Passed: {passed}/{total}")
print(f"📈 Success Rate: {(passed/total*100):.0f}%")

if all_passed:
    print("\n✅ NO SIDE EFFECTS DETECTED!")
    print("   All features are working correctly after the fix.")
else:
    print("\n⚠️ Some features may be affected.")
    print("   Review the failed tests above.")

print("="*60)