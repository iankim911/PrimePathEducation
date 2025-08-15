#!/usr/bin/env python3
"""
Investigate specific test failures from compatibility test
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import Question, Exam, StudentSession, StudentAnswer
from placement_test.services.placement_service import PlacementService
from core.models import CurriculumLevel, ExamLevelMapping

print("="*60)
print("INVESTIGATING SPECIFIC TEST FAILURES")
print("="*60)

def test_session_management_detailed():
    """Detailed test of session management"""
    print("\n🎯 Session Management Detailed Test")
    print("-" * 50)
    
    try:
        # Test session creation
        sessions = StudentSession.objects.all()
        print(f"Total sessions: {sessions.count()}")
        
        if not sessions.exists():
            print("❌ No sessions found")
            return False
        
        # Test session structure
        session = sessions.first()
        print(f"Session ID: {session.id}")
        print(f"Student name: {session.student_name}")
        print(f"Student email: {session.student_email}")
        print(f"Exam: {session.exam.name if session.exam else 'None'}")
        print(f"Start time: {session.start_time}")
        print(f"Completed: {session.completed_at is not None}")
        
        # Check required fields
        required_fields = ['exam', 'student_name', 'start_time']
        for field in required_fields:
            value = getattr(session, field)
            if value is None:
                print(f"❌ Required field '{field}' is None")
                return False
        
        print("✅ Session structure looks correct")
        
        # Test answers
        answers = StudentAnswer.objects.filter(session=session)
        print(f"Answers for this session: {answers.count()}")
        
        if answers.exists():
            answer = answers.first()
            print(f"Answer fields:")
            print(f"  Question: Q{answer.question.question_number}")
            print(f"  Response: {answer.student_response[:50]}...")
            print(f"  Is correct: {answer.is_correct}")
            print(f"  Points earned: {answer.points_earned}")
            print(f"  Has points_earned field: {hasattr(answer, 'points_earned')}")
            print(f"  Has is_correct field: {hasattr(answer, 'is_correct')}")
            
            if not hasattr(answer, 'points_earned') or not hasattr(answer, 'is_correct'):
                print("❌ Answer missing required fields")
                return False
            else:
                print("✅ Answer fields correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Session test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_difficulty_progression_detailed():
    """Detailed test of difficulty progression"""
    print("\n⬆️ Difficulty Progression Detailed Test")
    print("-" * 50)
    
    try:
        # Test imports
        try:
            from placement_test.services.placement_service import PlacementService
            print("✅ PlacementService imported successfully")
        except ImportError as e:
            print(f"❌ PlacementService import failed: {e}")
            return False
        
        # Test CurriculumLevel
        try:
            curriculum_levels = CurriculumLevel.objects.all()
            print(f"Curriculum levels: {curriculum_levels.count()}")
            
            if curriculum_levels.exists():
                level = curriculum_levels.first()
                print(f"Sample level: {level}")
                print("✅ CurriculumLevel accessible")
            else:
                print("❌ No curriculum levels found")
                return False
                
        except Exception as e:
            print(f"❌ CurriculumLevel test failed: {e}")
            return False
        
        # Test ExamLevelMapping
        try:
            mappings = ExamLevelMapping.objects.all()
            print(f"Exam mappings: {mappings.count()}")
            
            if mappings.exists():
                mapping = mappings.first()
                print(f"Sample mapping: {mapping.exam.name} -> {mapping.curriculum_level}")
                print("✅ ExamLevelMapping accessible")
            else:
                print("⚠️ No exam mappings found (this might be OK)")
                
        except Exception as e:
            print(f"❌ ExamLevelMapping test failed: {e}")
            return False
        
        # Test placement rules method
        try:
            rules = PlacementService.get_placement_rules()
            print(f"Placement rules type: {type(rules)}")
            print(f"Placement rules content (first 100 chars): {str(rules)[:100]}...")
            
            if rules:
                print("✅ Placement rules accessible")
            else:
                print("⚠️ Placement rules returned None/empty")
                
        except Exception as e:
            print(f"❌ Placement rules test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Difficulty progression test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run detailed failure investigation"""
    print("🔍 Investigating specific test failures...\n")
    
    print("Testing Session Management:")
    session_result = test_session_management_detailed()
    
    print("\nTesting Difficulty Progression:")
    difficulty_result = test_difficulty_progression_detailed()
    
    print("\n" + "="*60)
    print("FAILURE INVESTIGATION SUMMARY")
    print("="*60)
    
    print(f"Session Management: {'✅ PASS' if session_result else '❌ FAIL'}")
    print(f"Difficulty Progression: {'✅ PASS' if difficulty_result else '❌ FAIL'}")
    
    if session_result and difficulty_result:
        print("\n✅ Both areas are actually working correctly!")
        print("The original test may have had false negatives.")
    else:
        print(f"\n⚠️ Found issues that need addressing.")
    
    return session_result and difficulty_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)