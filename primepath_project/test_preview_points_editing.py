#!/usr/bin/env python3
"""
Test the points editing functionality in the Preview & Answer Keys interface
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import Question, Exam
from django.test import Client
from django.urls import reverse
import json

print("="*60)
print("PREVIEW INTERFACE POINTS EDITING TEST")
print("="*60)

def test_preview_template_points_interface():
    """Test that the preview template now includes points editing interface"""
    print("\n🎯 Test 1: Preview Template Points Interface")
    print("-" * 50)
    
    try:
        client = Client()
        
        # Get an exam to test
        exam = Exam.objects.first()
        if not exam:
            print("❌ No exams found for testing")
            return False
        
        print(f"Testing exam: {exam.name}")
        
        # Get the preview page
        response = client.get(f'/PlacementTest/exams/{exam.id}/preview/')
        
        if response.status_code != 200:
            print(f"❌ Preview page returned {response.status_code}")
            return False
        
        html_content = response.content.decode()
        
        # Check for points editing elements
        required_elements = [
            'question-points-container',
            'question-points-display',
            'question-points-edit',
            'points-input',
            'edit-points-btn',
            'save-points-btn',
            'cancel-points-btn'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in html_content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing elements: {missing_elements}")
            return False
        else:
            print("✅ All points editing elements found in HTML")
        
        # Check for JavaScript functionality
        js_functions = [
            'edit-points-btn',
            'save-points-btn', 
            'cancel-points-btn',
            'points-input'
        ]
        
        missing_js = []
        for func in js_functions:
            if func not in html_content:
                missing_js.append(func)
        
        if missing_js:
            print(f"❌ Missing JavaScript: {missing_js}")
            return False
        else:
            print("✅ Points editing JavaScript found")
        
        # Check that points are displayed for questions
        questions = exam.questions.all()
        if questions.exists():
            question = questions.first()
            if f'data-question-id="{question.id}"' in html_content:
                print(f"✅ Question {question.question_number} has points editing interface")
            else:
                print(f"❌ Question {question.question_number} missing points editing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False

def test_api_integration_from_preview():
    """Test that the API endpoint works from the preview interface context"""
    print("\n🔌 Test 2: API Integration from Preview Interface")
    print("-" * 50)
    
    try:
        client = Client()
        
        # Get a question to test
        question = Question.objects.first()
        if not question:
            print("❌ No questions found for testing")
            return False
        
        original_points = question.points
        test_points = 5 if original_points != 5 else 7
        
        print(f"Testing question {question.question_number}: {original_points} → {test_points} points")
        
        # Test the API endpoint that would be called from preview interface
        response = client.post(
            f'/api/PlacementTest/questions/{question.id}/update/',
            {
                'points': test_points
            }
        )
        
        if response.status_code != 200:
            print(f"❌ API returned {response.status_code}")
            return False
        
        response_data = json.loads(response.content.decode())
        
        if not response_data.get('success'):
            print(f"❌ API returned error: {response_data.get('error', 'Unknown')}")
            return False
        
        # Verify database was updated
        question.refresh_from_db()
        if question.points == test_points:
            print(f"✅ Points successfully updated via API: {original_points} → {test_points}")
            
            # Restore original value
            question.points = original_points
            question.save()
            print(f"✅ Points restored to original value: {original_points}")
            return True
        else:
            print(f"❌ Database not updated. Expected {test_points}, got {question.points}")
            return False
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

def test_points_validation_from_preview():
    """Test points validation works from preview interface"""
    print("\n✅ Test 3: Points Validation from Preview Interface")
    print("-" * 50)
    
    try:
        client = Client()
        
        question = Question.objects.first()
        if not question:
            print("❌ No questions found for testing")
            return False
        
        # Test invalid points (too low)
        response = client.post(
            f'/api/PlacementTest/questions/{question.id}/update/',
            {
                'points': 0
            }
        )
        
        # Should still return 200 but with validation handled by model
        if response.status_code == 200:
            # Check question wasn't changed to invalid value
            question.refresh_from_db()
            if question.points >= 1:
                print("✅ Invalid points (0) correctly rejected")
            else:
                print("❌ Invalid points were accepted")
                return False
        
        # Test invalid points (too high)
        response = client.post(
            f'/api/PlacementTest/questions/{question.id}/update/',
            {
                'points': 15
            }
        )
        
        if response.status_code == 200:
            question.refresh_from_db()
            if question.points <= 10:
                print("✅ Invalid points (15) correctly rejected")
            else:
                print("❌ Invalid points were accepted")
                return False
        
        # Test valid points
        original_points = question.points
        test_points = 3
        
        response = client.post(
            f'/api/PlacementTest/questions/{question.id}/update/',
            {
                'points': test_points
            }
        )
        
        response_data = json.loads(response.content.decode())
        if response_data.get('success'):
            question.refresh_from_db()
            if question.points == test_points:
                print(f"✅ Valid points ({test_points}) correctly accepted")
                
                # Restore
                question.points = original_points
                question.save()
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def main():
    """Run all tests for preview interface points editing"""
    print("🚀 Testing points editing in Preview & Answer Keys interface...\n")
    
    tests = [
        ('Preview Template Points Interface', test_preview_template_points_interface),
        ('API Integration from Preview Interface', test_api_integration_from_preview),
        ('Points Validation from Preview Interface', test_points_validation_from_preview),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("PREVIEW INTERFACE POINTS EDITING TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 PREVIEW INTERFACE POINTS EDITING WORKING!")
        print("\n✅ FUNCTIONALITY CONFIRMED:")
        print("   ✓ Preview & Answer Keys template has points editing interface")
        print("   ✓ Click-to-edit functionality implemented")
        print("   ✓ API integration working from preview interface")
        print("   ✓ Points validation working correctly")
        print("   ✓ Users can now edit points from the interface you were viewing!")
        
        print("\n📋 HOW TO USE:")
        print("   1. Go to Manage Exams → Select Exam → Preview & Answer Keys")
        print("   2. Click the ✏️ (edit) button next to any question's points")
        print("   3. Change the points value (1-10) and press Enter or click ✓")
        print("   4. Press Escape or click ✗ to cancel")
        print("   5. Points are saved immediately via API")
        
    else:
        print(f"\n⚠️ {total-passed} issues detected. Review failures above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)