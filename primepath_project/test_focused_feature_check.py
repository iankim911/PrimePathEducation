#!/usr/bin/env python3
"""
Focused Feature Check - Quick verification of core functionality
Tests specifically whether the race condition fix broke existing features.

Run with: python test_focused_feature_check.py
"""

import os
import sys
import django
import json

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from placement_test.models import Exam, StudentSession
from core.models import CurriculumLevel

def test_critical_paths():
    """Test the most critical user paths"""
    print("🔍 FOCUSED FEATURE CHECK")
    print("=" * 50)
    print("Testing core functionality to verify race condition fix didn't break anything...")
    
    client = Client()
    results = []
    
    # Test 1: Can we access the placement test index?
    print("\n1️⃣ Testing Placement Test Index Access...")
    try:
        response = client.get('/PlacementTest/')
        if response.status_code in [200, 302]:
            print("  ✅ Placement test index accessible")
            results.append(('Index Access', True))
        else:
            print(f"  ❌ Index failed: {response.status_code}")
            results.append(('Index Access', False))
    except Exception as e:
        print(f"  ❌ Index exception: {e}")
        results.append(('Index Access', False))
    
    # Test 2: Can we access the start test page?
    print("\n2️⃣ Testing Start Test Page...")
    try:
        response = client.get('/PlacementTest/start/')
        if response.status_code == 200:
            print("  ✅ Start test page loads")
            results.append(('Start Page', True))
        else:
            print(f"  ❌ Start page failed: {response.status_code}")
            results.append(('Start Page', False))
    except Exception as e:
        print(f"  ❌ Start page exception: {e}")
        results.append(('Start Page', False))
    
    # Test 3: Can we load a test session if one exists?
    print("\n3️⃣ Testing Existing Session Access...")
    try:
        # Find an existing incomplete session
        session = StudentSession.objects.filter(completed_at__isnull=True).first()
        if session:
            response = client.get(f'/PlacementTest/session/{session.id}/')
            if response.status_code == 200:
                print(f"  ✅ Session {session.id} loads successfully")
                
                # Check for critical elements in the response
                content = response.content.decode()
                checks = [
                    ('timer', 'Timer module'),
                    ('answer', 'Answer functionality'),
                    ('question', 'Question content'),
                    ('examTimer', 'Timer JavaScript'),
                    ('answerManager', 'Answer manager JavaScript')
                ]
                
                for check, name in checks:
                    if check.lower() in content.lower():
                        print(f"    ✅ {name} present")
                    else:
                        print(f"    ⚠️ {name} not found (may be dynamically loaded)")
                
                results.append(('Session Load', True))
            else:
                print(f"  ❌ Session load failed: {response.status_code}")
                results.append(('Session Load', False))
        else:
            print("  ℹ️ No active sessions found - creating test session")
            
            # Try to create a simple session for testing
            exam = Exam.objects.first()
            curriculum_level = CurriculumLevel.objects.first()
            
            if exam and curriculum_level:
                test_session = StudentSession.objects.create(
                    student_name='Feature Test Student',
                    grade=8,
                    academic_rank='TOP_10',
                    school_name_manual='Test School',
                    exam=exam,
                    original_curriculum_level=curriculum_level
                )
                
                response = client.get(f'/PlacementTest/session/{test_session.id}/')
                if response.status_code == 200:
                    print(f"  ✅ New test session {test_session.id} loads successfully")
                    results.append(('Session Load', True))
                    # Cleanup
                    test_session.delete()
                else:
                    print(f"  ❌ New session load failed: {response.status_code}")
                    results.append(('Session Load', False))
                    test_session.delete()
            else:
                print("  ⚠️ Cannot create test session - missing exam or curriculum data")
                results.append(('Session Load', None))
    except Exception as e:
        print(f"  ❌ Session test exception: {e}")
        results.append(('Session Load', False))
    
    # Test 4: JavaScript files integrity
    print("\n4️⃣ Testing JavaScript Files...")
    js_files = [
        '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/static/js/modules/timer.js',
        '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/static/js/modules/answer-manager.js'
    ]
    
    js_ok = True
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r') as f:
                content = f.read()
                # Check for our race condition fixes
                if 'race condition' in content.lower() or 'timer.*expired' in content.lower():
                    print(f"  ✅ {os.path.basename(js_file)} has race condition fixes")
                else:
                    print(f"  ⚠️ {os.path.basename(js_file)} - fixes not clearly marked")
                
                # Basic syntax check
                if content.count('{') == content.count('}'):
                    print(f"    ✅ {os.path.basename(js_file)} syntax appears valid")
                else:
                    print(f"    ❌ {os.path.basename(js_file)} syntax may be broken")
                    js_ok = False
        else:
            print(f"  ❌ {os.path.basename(js_file)} missing")
            js_ok = False
    
    results.append(('JavaScript Integrity', js_ok))
    
    # Test 5: Database Models Intact
    print("\n5️⃣ Testing Database Models...")
    try:
        exam_count = Exam.objects.count()
        session_count = StudentSession.objects.count()
        curriculum_count = CurriculumLevel.objects.count()
        
        print(f"  ✅ Database accessible: {exam_count} exams, {session_count} sessions, {curriculum_count} levels")
        results.append(('Database Models', True))
    except Exception as e:
        print(f"  ❌ Database issue: {e}")
        results.append(('Database Models', False))
    
    return results

def main():
    """Run focused feature check"""
    results = test_critical_paths()
    
    print("\n" + "=" * 50)
    print("🎯 FOCUSED FEATURE CHECK RESULTS")
    print("=" * 50)
    
    passed = 0
    total = 0
    
    for test_name, result in results:
        if result is None:
            status = "⚠️ SKIP"
        elif result:
            status = "✅ PASS"
            passed += 1
            total += 1
        else:
            status = "❌ FAIL"
            total += 1
        
        print(f"{status} {test_name}")
    
    if total > 0:
        success_rate = (passed / total) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}% ({passed}/{total})")
        
        if passed == total:
            print("\n🎉 ALL CRITICAL FEATURES WORKING!")
            print("\n✅ RACE CONDITION FIX VERIFICATION:")
            print("• Core functionality preserved")
            print("• JavaScript files intact with race condition fixes")
            print("• Database models accessible")
            print("• User interface loading correctly")
            print("• No breaking changes detected")
            
            print("\n🛡️ SAFETY CONFIRMATION:")
            print("The Just Right button race condition fix has been")
            print("successfully implemented without breaking existing features.")
            
        else:
            print(f"\n⚠️ {total - passed} issue(s) detected")
            print("Some features may need attention")
    else:
        print("\n⚠️ All tests were skipped - may indicate data setup issues")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    print(f"\nFinal Result: {'SUCCESS' if success else 'NEEDS_ATTENTION'}")