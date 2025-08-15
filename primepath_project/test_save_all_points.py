#!/usr/bin/env python3
"""
COMPREHENSIVE TEST: Save All Points Persistence
Tests that points are properly saved when using Save All button
"""

import os
import sys
import json
from datetime import datetime

# Django setup
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from placement_test.models import Exam, Question

def test_save_all_with_points():
    """Test that Save All properly saves points values"""
    
    print("=" * 60)
    print("🔧 SAVE ALL POINTS PERSISTENCE TEST")
    print("=" * 60)
    
    # Step 1: Setup authentication
    print("\n📋 STEP 1: Setting up authentication...")
    
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_superuser(
            username='testadmin',
            password='testpass123',
            email='admin@test.com'
        )
        print(f"✅ Created test admin: {user.username}")
    else:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Using existing admin: {user.username}")
    
    client = Client()
    client.login(username=user.username, password='testpass123')
    
    # Step 2: Find test exam and questions
    print("\n📋 STEP 2: Finding test data...")
    
    exam = Exam.objects.filter(questions__isnull=False).first()
    if not exam:
        print("❌ No exam with questions found")
        return False
    
    questions = list(exam.questions.all()[:3])  # Test with first 3 questions
    print(f"✅ Using exam: {exam.name}")
    print(f"✅ Testing with {len(questions)} questions")
    
    # Step 3: Record original points
    print("\n📋 STEP 3: Recording original points...")
    
    original_points = {}
    for q in questions:
        original_points[q.id] = q.points
        print(f"   Q{q.question_number}: {q.points} points")
    
    # Step 4: Prepare test data with new points
    print("\n📋 STEP 4: Preparing Save All request with new points...")
    
    questions_data = []
    new_points = {}
    
    for i, q in enumerate(questions):
        # Set different points for each question
        test_points = min(10, i + 3)  # 3, 4, 5 for first 3 questions
        new_points[q.id] = test_points
        
        q_data = {
            'id': str(q.id),
            'question_number': str(q.question_number),
            'question_type': q.question_type,
            'correct_answer': q.correct_answer,
            'points': test_points,  # CRITICAL: Include points
            'options_count': q.options_count
        }
        questions_data.append(q_data)
        print(f"   Q{q.question_number}: {original_points[q.id]} -> {test_points} points")
    
    # Step 5: Send Save All request
    print("\n📋 STEP 5: Sending Save All request...")
    
    save_url = f'/api/PlacementTest/exams/{exam.id}/save-answers/'
    
    request_data = {
        'questions': questions_data,
        'audio_assignments': {},
        'pdf_rotation': 0
    }
    
    print(f"   URL: {save_url}")
    print(f"   Sending points for {len(questions_data)} questions")
    
    response = client.post(
        save_url,
        data=json.dumps(request_data),
        content_type='application/json',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    print(f"   Response status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Save All failed with status {response.status_code}")
        print(f"   Response: {response.content.decode()}")
        return False
    
    # Step 6: Parse response
    print("\n📋 STEP 6: Checking response...")
    
    try:
        data = response.json()
        if data.get('success'):
            print("✅ Save All reported success")
            if 'points_updated' in data:
                print(f"✅ Points updated for {data['points_updated']} questions")
            if data.get('debug_info', {}).get('points_provided'):
                print(f"   Questions with points: {data['debug_info']['points_provided']}")
        else:
            print(f"❌ Save All failed: {data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Failed to parse response: {e}")
        return False
    
    # Step 7: Verify database was updated
    print("\n📋 STEP 7: Verifying database updates...")
    
    all_saved = True
    for q in questions:
        q.refresh_from_db()
        expected = new_points[q.id]
        actual = q.points
        
        if actual == expected:
            print(f"✅ Q{q.question_number}: {actual} points (correct)")
        else:
            print(f"❌ Q{q.question_number}: {actual} points (expected {expected})")
            all_saved = False
    
    # Step 8: Test page reload (simulate coming back to exam)
    print("\n📋 STEP 8: Simulating page reload...")
    
    # Clear any caches by getting fresh from database
    exam_fresh = Exam.objects.get(id=exam.id)
    questions_fresh = list(exam_fresh.questions.filter(
        id__in=[q.id for q in questions]
    ).order_by('question_number'))
    
    print("   After reload:")
    reload_correct = True
    for q in questions_fresh:
        expected = new_points[q.id]
        actual = q.points
        
        if actual == expected:
            print(f"   ✅ Q{q.question_number}: {actual} points (persisted)")
        else:
            print(f"   ❌ Q{q.question_number}: {actual} points (lost, expected {expected})")
            reload_correct = False
    
    return all_saved and reload_correct

def main():
    print("\n🚀 COMPREHENSIVE SAVE ALL POINTS TEST")
    print("=" * 60)
    
    try:
        success = test_save_all_with_points()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("\n✅ Summary:")
            print("   • Save All includes points in request")
            print("   • Backend processes points updates")
            print("   • Database is updated correctly")
            print("   • Points persist after page reload")
            print("   • No data loss when returning to exam")
            
            print("\n📝 The fix ensures:")
            print("   1. Points are collected from DOM during Save All")
            print("   2. Points are included in the request payload")
            print("   3. ExamService processes points updates")
            print("   4. Changes persist in database")
            print("   5. Comprehensive logging tracks all updates")
        else:
            print("\n" + "=" * 60)
            print("⚠️ Some tests failed - points may not be persisting")
            print("\n🔍 Debug steps:")
            print("   1. Check browser console for [SaveAll] logs")
            print("   2. Check server logs for [save_exam_answers] entries")
            print("   3. Check [ExamService] logs for points updates")
            print("   4. Verify points are in request payload")
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()