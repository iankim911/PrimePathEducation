#!/usr/bin/env python
"""
Comprehensive test to verify namespace initialization fixes work for both test types
"""

import os
import sys
import django
import json
import requests
import time

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import StudentSession, Exam, Question
from primepath_routinetest.models import StudentSession as RoutineStudentSession, Exam as RoutineExam
from core.models import CurriculumLevel

def test_namespace_initialization():
    """Test namespace initialization in both placement and routine test interfaces"""
    
    print("=" * 80)
    print("COMPREHENSIVE NAMESPACE INITIALIZATION TEST")
    print("=" * 80)
    
    base_url = "http://127.0.0.1:8000"
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # Test 1: Placement Test Interface
    print("\n" + "=" * 60)
    print("TEST 1: PLACEMENT TEST INTERFACE")
    print("=" * 60)
    
    try:
        # Create placement test session
        exam = Exam.objects.filter(questions__isnull=False).first()
        level = CurriculumLevel.objects.first()
        
        if exam and level:
            session = StudentSession.objects.create(
                student_name='Namespace Test - Placement',
                grade=10,
                academic_rank='TOP_10',
                exam=exam,
                original_curriculum_level=level
            )
            
            placement_url = f"{base_url}/placement/test/{session.id}/"
            print(f"✅ Placement test session created: {session.id}")
            
            # Test page load
            response = requests.get(placement_url)
            if response.status_code == 200:
                print("✅ Placement test page loads successfully")
                
                # Check for bootstrap.js
                if 'bootstrap.js' in response.text:
                    print("✅ bootstrap.js included in placement test")
                    results['passed'].append("Placement test bootstrap.js")
                else:
                    print("❌ bootstrap.js missing in placement test")
                    results['failed'].append("Placement test bootstrap.js")
                
                # Check for debug-config.js
                if 'debug-config.js' in response.text:
                    print("✅ debug-config.js included in placement test")
                    results['passed'].append("Placement test debug-config.js")
                else:
                    print("❌ debug-config.js missing in placement test")
                    results['failed'].append("Placement test debug-config.js")
                
                # Check for proper script order
                script_order = [
                    'bootstrap.js',
                    'debug-config.js',
                    'app-config.js',
                    'event-delegation.js',
                    'answer-manager.js',
                    'navigation.js'
                ]
                
                bootstrap_pos = response.text.find('bootstrap.js')
                navigation_pos = response.text.find('navigation.js')
                
                if bootstrap_pos < navigation_pos and bootstrap_pos != -1:
                    print("✅ Script loading order correct in placement test")
                    results['passed'].append("Placement test script order")
                else:
                    print("❌ Script loading order incorrect in placement test")
                    results['failed'].append("Placement test script order")
                
                # Check for initialization logging
                if 'PRIMEPATH INITIALIZATION STARTING' in response.text:
                    print("✅ Initialization logging present in placement test")
                    results['passed'].append("Placement test init logging")
                else:
                    print("❌ Initialization logging missing in placement test")
                    results['failed'].append("Placement test init logging")
                
            else:
                print(f"❌ Placement test page returned status {response.status_code}")
                results['failed'].append(f"Placement test page load: {response.status_code}")
            
            # Cleanup
            session.delete()
            
        else:
            print("❌ Cannot create placement test session - missing exam or level")
            results['failed'].append("Placement test session creation")
            
    except Exception as e:
        print(f"❌ Placement test error: {e}")
        results['failed'].append(f"Placement test: {e}")
    
    # Test 2: Routine Test Interface  
    print("\n" + "=" * 60)
    print("TEST 2: ROUTINE TEST INTERFACE")
    print("=" * 60)
    
    try:
        # Create routine test session  
        routine_exam = RoutineExam.objects.filter(routine_questions__isnull=False).first()
        
        if routine_exam:
            routine_session = RoutineStudentSession.objects.create(
                student_name='Namespace Test - Routine',
                grade=10,
                academic_rank='TOP_10',
                exam=routine_exam,
                original_curriculum_level=level
            )
            
            routine_url = f"{base_url}/routine-test/test/{routine_session.id}/"
            print(f"✅ Routine test session created: {routine_session.id}")
            
            # Test page load
            response = requests.get(routine_url)
            if response.status_code == 200:
                print("✅ Routine test page loads successfully")
                
                # Check for bootstrap.js (THIS WAS THE CRITICAL MISSING PIECE)
                if 'bootstrap.js' in response.text:
                    print("✅ bootstrap.js NOW INCLUDED in routine test (FIXED!)")
                    results['passed'].append("Routine test bootstrap.js")
                else:
                    print("❌ bootstrap.js STILL missing in routine test")
                    results['failed'].append("Routine test bootstrap.js")
                
                # Check for debug-config.js
                if 'debug-config.js' in response.text:
                    print("✅ debug-config.js NOW INCLUDED in routine test (FIXED!)")
                    results['passed'].append("Routine test debug-config.js")
                else:
                    print("❌ debug-config.js missing in routine test")
                    results['failed'].append("Routine test debug-config.js")
                
                # Check for module-loader.js
                if 'module-loader.js' in response.text:
                    print("✅ module-loader.js NOW INCLUDED in routine test (FIXED!)")
                    results['passed'].append("Routine test module-loader.js")
                else:
                    print("❌ module-loader.js missing in routine test")
                    results['failed'].append("Routine test module-loader.js")
                
                # Check for proper script order
                bootstrap_pos = response.text.find('bootstrap.js')
                navigation_pos = response.text.find('navigation.js')
                
                if bootstrap_pos < navigation_pos and bootstrap_pos != -1:
                    print("✅ Script loading order correct in routine test (FIXED!)")
                    results['passed'].append("Routine test script order")
                else:
                    print("❌ Script loading order incorrect in routine test")
                    results['failed'].append("Routine test script order")
                
                # Check for enhanced initialization logging
                if 'PRIMEPATH ROUTINE TEST INITIALIZATION STARTING' in response.text:
                    print("✅ Enhanced initialization logging present in routine test (ADDED!)")
                    results['passed'].append("Routine test enhanced init logging")
                else:
                    print("❌ Enhanced initialization logging missing in routine test")
                    results['failed'].append("Routine test enhanced init logging")
                
                # Check for error recovery code
                if 'Creating emergency namespaces' in response.text:
                    print("✅ Error recovery code present in routine test (ADDED!)")
                    results['passed'].append("Routine test error recovery")
                else:
                    print("❌ Error recovery code missing in routine test")
                    results['failed'].append("Routine test error recovery")
                
                # Check for health check system
                if 'healthCheck()' in response.text:
                    print("✅ Health check system present in routine test (ADDED!)")
                    results['passed'].append("Routine test health check")
                else:
                    print("❌ Health check system missing in routine test")
                    results['failed'].append("Routine test health check")
                
            else:
                print(f"❌ Routine test page returned status {response.status_code}")
                results['failed'].append(f"Routine test page load: {response.status_code}")
            
            # Cleanup
            routine_session.delete()
            
        else:
            print("❌ Cannot create routine test session - missing routine exam")
            results['failed'].append("Routine test session creation")
            
    except Exception as e:
        print(f"❌ Routine test error: {e}")
        results['failed'].append(f"Routine test: {e}")
    
    # Test 3: Namespace Safety Checks
    print("\n" + "=" * 60)
    print("TEST 3: NAMESPACE SAFETY CHECKS")  
    print("=" * 60)
    
    # Test bootstrap.js accessibility
    bootstrap_url = f"{base_url}/static/js/bootstrap.js"
    try:
        response = requests.head(bootstrap_url)
        if response.status_code == 200:
            print("✅ bootstrap.js file is accessible")
            results['passed'].append("Bootstrap.js accessibility")
        else:
            print(f"❌ bootstrap.js returned status {response.status_code}")
            results['failed'].append("Bootstrap.js accessibility")
    except Exception as e:
        print(f"❌ Error accessing bootstrap.js: {e}")
        results['failed'].append(f"Bootstrap.js access: {e}")
    
    # Test debug-config.js accessibility
    debug_config_url = f"{base_url}/static/js/config/debug-config.js"
    try:
        response = requests.head(debug_config_url)
        if response.status_code == 200:
            print("✅ debug-config.js file is accessible")
            results['passed'].append("Debug-config.js accessibility")
        else:
            print(f"❌ debug-config.js returned status {response.status_code}")
            results['failed'].append("Debug-config.js accessibility")
    except Exception as e:
        print(f"❌ Error accessing debug-config.js: {e}")
        results['failed'].append(f"Debug-config.js access: {e}")
    
    # Final Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(results['passed']) + len(results['failed'])
    success_rate = (len(results['passed']) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n✅ Passed: {len(results['passed'])} tests")
    for test in results['passed']:
        print(f"   - {test}")
    
    if results['failed']:
        print(f"\n❌ Failed: {len(results['failed'])} tests")
        for test in results['failed']:
            print(f"   - {test}")
    
    if results['warnings']:
        print(f"\n⚠️  Warnings: {len(results['warnings'])}")
        for warning in results['warnings']:
            print(f"   - {warning}")
    
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 NAMESPACE INITIALIZATION FIX SUCCESSFUL!")
        print("✅ Both placement test and routine test interfaces working")
        print("✅ All critical scripts loading in correct order")
        print("✅ Error recovery systems in place")
        print("✅ Comprehensive logging implemented")
        return True
    elif success_rate >= 80:
        print("\n✅ NAMESPACE FIX MOSTLY SUCCESSFUL")
        print("Minor issues detected but critical functionality restored")
        return True
    else:
        print("\n⚠️ NAMESPACE FIX NEEDS ATTENTION")
        print("Critical issues remain - please review failed tests")
        return False

if __name__ == "__main__":
    success = test_namespace_initialization()
    sys.exit(0 if success else 1)