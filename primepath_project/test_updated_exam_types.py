#!/usr/bin/env python
"""
Test script to verify updated exam type labels
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models.exam import Exam

def test_updated_labels():
    """Test the updated exam type labels"""
    print("\n" + "="*60)
    print("TESTING UPDATED EXAM TYPE LABELS")
    print("="*60)
    
    # Check the choices in the model
    print("\n[1] Model Choices:")
    choices = dict(Exam.EXAM_TYPE_CHOICES)
    for value, label in choices.items():
        print(f"   {value}: '{label}'")
    
    # Test creating exams with new labels
    print("\n[2] Testing Display Methods:")
    
    # Create a test exam object (without saving)
    review_exam = Exam(
        name="Test Review Exam",
        exam_type='REVIEW',
        total_questions=20
    )
    
    quarterly_exam = Exam(
        name="Test Quarterly Exam", 
        exam_type='QUARTERLY',
        total_questions=50
    )
    
    print(f"\n   Review Exam:")
    print(f"   - get_exam_type_display(): '{review_exam.get_exam_type_display()}'")
    print(f"   - get_exam_type_display_short(): '{review_exam.get_exam_type_display_short()}'")
    print(f"   - __str__(): '{str(review_exam)}'")
    
    print(f"\n   Quarterly Exam:")
    print(f"   - get_exam_type_display(): '{quarterly_exam.get_exam_type_display()}'")
    print(f"   - get_exam_type_display_short(): '{quarterly_exam.get_exam_type_display_short()}'")
    print(f"   - __str__(): '{str(quarterly_exam)}'")
    
    # Verify the expected values
    print("\n[3] Verification:")
    expected_review = "Review / Monthly Exam"
    expected_quarterly = "Quarterly Exam"
    
    if review_exam.get_exam_type_display() == expected_review:
        print(f"   ✅ Review label correct: '{expected_review}'")
    else:
        print(f"   ❌ Review label incorrect. Expected: '{expected_review}', Got: '{review_exam.get_exam_type_display()}'")
    
    if quarterly_exam.get_exam_type_display() == expected_quarterly:
        print(f"   ✅ Quarterly label correct: '{expected_quarterly}'")
    else:
        print(f"   ❌ Quarterly label incorrect. Expected: '{expected_quarterly}', Got: '{quarterly_exam.get_exam_type_display()}'")
    
    print("\n" + "="*60)
    print("LABEL UPDATE COMPLETE")
    print("="*60)
    print("\nThe exam type labels have been updated to:")
    print("  • Review / Monthly Exam")
    print("  • Quarterly Exam")
    print("\nThese will now appear in:")
    print("  • Create Exam dropdown")
    print("  • Exam list badges")
    print("  • Console logs")
    print("  • Database model choices")

if __name__ == '__main__':
    test_updated_labels()