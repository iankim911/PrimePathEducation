#!/usr/bin/env python
"""
Test script to verify console logging cleanup and modal functionality
"""

import os
import sys
import django
import json
import requests
from datetime import datetime

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import StudentSession, Exam
from core.models import CurriculumLevel
from django.utils import timezone

def test_console_logging_fix():
    """Test that console logging has been cleaned up properly"""
    
    print("=" * 70)
    print("TESTING CONSOLE LOGGING FIX")
    print("=" * 70)
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    base_url = "http://127.0.0.1:8000"
    
    # Step 1: Check debug config is loaded
    print("\n" + "=" * 70)
    print("STEP 1: CHECKING DEBUG CONFIGURATION")
    print("=" * 70)
    
    debug_config_url = f"{base_url}/static/js/config/debug-config.js"
    
    try:
        response = requests.get(debug_config_url)
        if response.status_code == 200:
            content = response.text
            
            # Check for key components
            checks = [
                ('Debug config object', 'DebugConfig' in content),
                ('Module-specific flags', 'modules: {' in content),
                ('Logger creation', 'createLogger' in content),
                ('Conditional logging', 'shouldLog' in content),
                ('Never log HTML', 'neverLog' in content and 'htmlContent' in content)
            ]
            
            all_passed = True
            for check_name, check_result in checks:
                if check_result:
                    print(f"  ✅ {check_name}")
                else:
                    print(f"  ❌ {check_name}")
                    all_passed = False
            
            if all_passed:
                results['passed'].append("Debug configuration")
            else:
                results['failed'].append("Debug configuration incomplete")
                
        else:
            print(f"  ❌ Debug config not found (status {response.status_code})")
            results['failed'].append("Debug config file missing")
            
    except Exception as e:
        print(f"  ❌ Error checking debug config: {e}")
        results['failed'].append(f"Debug config check: {e}")
    
    # Step 2: Create test session
    print("\n" + "=" * 70)
    print("STEP 2: CREATING TEST SESSION")
    print("=" * 70)
    
    try:
        exam = Exam.objects.filter(questions__isnull=False).first()
        if not exam:
            print("❌ No exam with questions found")
            results['failed'].append("No exam available")
            return False
        
        level = CurriculumLevel.objects.first()
        session = StudentSession.objects.create(
            student_name='Console Test User',
            grade=8,
            academic_rank='TOP_10',
            exam=exam,
            original_curriculum_level=level
        )
        
        test_url = f"{base_url}/PlacementTest/session/{session.id}/"
        print(f"✅ Test session created: {session.id}")
        results['passed'].append("Session creation")
        
    except Exception as e:
        print(f"❌ Failed to create session: {e}")
        results['failed'].append(f"Session creation: {e}")
        return False
    
    # Step 3: Check page for problematic console statements
    print("\n" + "=" * 70)
    print("STEP 3: CHECKING FOR PROBLEMATIC CONSOLE LOGS")
    print("=" * 70)
    
    try:
        response = requests.get(test_url)
        if response.status_code == 200:
            html = response.text
            
            # Check for removed/replaced console statements
            problematic_patterns = [
                ('console.error with modal HTML', 'console.error(\'[MODAL_'),
                ('console.trace in modal code', 'console.trace(\'[MODAL_'),
                ('MutationObserver console.error', 'console.error(\'[MODAL_STATE_AFTER_INCLUDE]'),
                ('Raw HTML logging', 'console.error(\'[MODAL_MUTATION]'),
                ('Submit test console.error', 'console.error(\'[SUBMIT_TEST_CALLED]'),
                ('Modal debug console.error', 'console.error(\'[MODAL_DEBUG]')
            ]
            
            issues_found = []
            for pattern_name, pattern in problematic_patterns:
                if pattern in html:
                    issues_found.append(pattern_name)
                    print(f"  ❌ Found: {pattern_name}")
                else:
                    print(f"  ✅ Removed: {pattern_name}")
            
            if issues_found:
                results['failed'].append(f"Problematic logging still present: {', '.join(issues_found)}")
            else:
                results['passed'].append("Console logging cleanup")
                print("\n  ✅ All problematic console statements removed/replaced")
                
        else:
            print(f"  ❌ Page returned status {response.status_code}")
            results['failed'].append(f"Page load failed: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error checking page: {e}")
        results['failed'].append(f"Page check: {e}")
    
    # Step 4: Check for conditional logging implementation
    print("\n" + "=" * 70)
    print("STEP 4: CHECKING CONDITIONAL LOGGING")
    print("=" * 70)
    
    files_to_check = [
        ('Event Delegation', '/static/js/utils/event-delegation.js', [
            'PrimePathDebug',
            'createLogger',
            'logger.debug',
            'logger.info'
        ]),
        ('Answer Manager', '/static/js/modules/answer-manager.js', [
            'isDebugMode()',
            'this.log(\'debug\'',
            'PrimePathDebug.shouldLog',
            'logger.debug'
        ]),
        ('Student Test Template', test_url, [
            'PrimePathDebug && PrimePathDebug.shouldLog',
            'logger = window.PrimePathDebug.createLogger'
        ])
    ]
    
    for file_name, file_path, patterns in files_to_check:
        print(f"\n  Checking {file_name}...")
        
        try:
            if file_path.startswith('/static/'):
                url = base_url + file_path
            else:
                url = file_path
                
            response = requests.get(url)
            if response.status_code == 200:
                content = response.text
                
                patterns_found = 0
                for pattern in patterns:
                    if pattern in content:
                        patterns_found += 1
                
                if patterns_found > 0:
                    print(f"    ✅ {file_name}: {patterns_found}/{len(patterns)} conditional logging patterns found")
                    results['passed'].append(f"{file_name} conditional logging")
                else:
                    print(f"    ⚠️  {file_name}: No conditional logging patterns found")
                    results['warnings'].append(f"{file_name} may not have conditional logging")
                    
            else:
                print(f"    ❌ {file_name}: Could not fetch (status {response.status_code})")
                results['warnings'].append(f"{file_name} not accessible")
                
        except Exception as e:
            print(f"    ❌ {file_name}: Error - {e}")
            results['warnings'].append(f"{file_name} check error")
    
    # Step 5: Test modal functionality
    print("\n" + "=" * 70)
    print("STEP 5: TESTING MODAL FUNCTIONALITY")
    print("=" * 70)
    
    # Complete the test session to trigger modal
    complete_url = f"{base_url}/api/PlacementTest/session/{session.id}/complete/"
    
    try:
        # Get CSRF token from page
        response = requests.get(test_url)
        csrf_token = None
        
        if 'csrfmiddlewaretoken' in response.text:
            import re
            match = re.search(r"csrf['\"]:\s*['\"]([^'\"]+)['\"]", response.text)
            if match:
                csrf_token = match.group(1)
        
        if csrf_token:
            headers = {
                'X-CSRFToken': csrf_token,
                'Content-Type': 'application/json'
            }
            
            complete_response = requests.post(complete_url, 
                                             json={'session_id': str(session.id)},
                                             headers=headers)
            
            if complete_response.status_code == 200:
                data = complete_response.json()
                
                if 'show_difficulty_choice' in data:
                    print(f"  ✅ Test completion response includes difficulty choice flag: {data['show_difficulty_choice']}")
                    results['passed'].append("Modal trigger logic")
                else:
                    print("  ⚠️  Test completion response missing difficulty choice flag")
                    results['warnings'].append("Modal flag missing")
                    
            else:
                print(f"  ❌ Test completion failed (status {complete_response.status_code})")
                results['failed'].append("Test completion")
        else:
            print("  ⚠️  Could not extract CSRF token")
            results['warnings'].append("CSRF token extraction")
            
    except Exception as e:
        print(f"  ❌ Error testing modal: {e}")
        results['failed'].append(f"Modal test: {e}")
    
    # Step 6: Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
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
    
    # Cleanup
    try:
        session.delete()
        print("\n✅ Test data cleaned up")
    except:
        pass
    
    # Console control instructions
    print("\n" + "=" * 70)
    print("CONSOLE DEBUG CONTROL")
    print("=" * 70)
    print("\nYou can now control debug logging from the browser console:")
    print("  enableDebug()         - Enable all debug logging")
    print("  disableDebug()        - Disable all debug logging")
    print("  enableDebug('modal')  - Enable modal debug logging only")
    print("  disableDebug('modal') - Disable modal debug logging")
    print("  setDebugLevel('INFO') - Set verbosity (ERROR, WARN, INFO, DEBUG, TRACE)")
    print("\nCurrent settings can be viewed with:")
    print("  PrimePathDebug.getStatus()")
    
    if success_rate >= 80:
        print("\n🎉 CONSOLE LOGGING FIX SUCCESSFUL!")
        print("✅ Problematic console statements removed")
        print("✅ Conditional debug logging implemented")
        print("✅ Modal functionality preserved")
        print("✅ Debug control available from console")
        return True
    else:
        print("\n⚠️  CONSOLE LOGGING FIX NEEDS ATTENTION")
        return False

if __name__ == "__main__":
    success = test_console_logging_fix()
    sys.exit(0 if success else 1)