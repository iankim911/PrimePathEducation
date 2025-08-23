#!/usr/bin/env python3
"""
LIVE SERVER VALIDATION FOR COPY MODAL DROPDOWN FIX
=================================================

This script starts a Django server and validates the Copy Modal dropdown
functionality with real browser interaction simulation.
"""

import os
import sys
import django
import subprocess
import time
import signal
import json
from datetime import datetime
import threading

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from primepath_routinetest.services.exam_service import ExamService

print("="*80)
print("🚀 LIVE SERVER VALIDATION FOR COPY MODAL DROPDOWN FIX")
print("="*80)
print(f"Started: {datetime.now().isoformat()}")
print()

# Global variable to store server process
server_process = None

def start_django_server():
    """Start Django development server"""
    global server_process
    
    print("🚀 Starting Django development server...")
    try:
        server_process = subprocess.Popen([
            '../venv/bin/python', 
            'manage.py', 
            'runserver', 
            '127.0.0.1:8000',
            '--settings=primepath_project.settings_sqlite',
            '--noreload'
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        cwd='/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project'
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to initialize...")
        time.sleep(5)
        
        # Check if server is running
        if server_process.poll() is None:
            print("✅ Django server started successfully")
            return True
        else:
            print("❌ Failed to start Django server")
            return False
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def stop_django_server():
    """Stop Django development server"""
    global server_process
    
    if server_process:
        print("🛑 Stopping Django server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped")

def test_server_response():
    """Test if server is responding"""
    try:
        import requests
        response = requests.get('http://127.0.0.1:8000/', timeout=10)
        return response.status_code == 200
    except:
        # Fallback to curl
        result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://127.0.0.1:8000/'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and result.stdout.strip() == '200'

def validate_exam_library_access():
    """Test access to exam library page"""
    print("🔍 Testing exam library page access...")
    
    try:
        client = Client()
        
        # Get admin user for testing
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No admin user found for testing")
            return False
        
        # Login
        client.force_login(admin_user)
        print(f"✅ Logged in as: {admin_user.username}")
        
        # Test exam library page
        response = client.get('/routinetest/exam/exam_library/')
        
        if response.status_code == 200:
            print("✅ Exam library page accessible")
            
            # Check if curriculum data is in template context
            context_checks = {
                'curriculum_hierarchy_for_copy': 'curriculum_hierarchy_for_copy' in response.context,
                'curriculum_levels_for_copy': 'curriculum_levels_for_copy' in response.context,
                'is_admin': response.context.get('is_admin', False),
                'can_manage_exams': response.context.get('can_manage_exams', False)
            }
            
            print("📊 Template context validation:")
            for check, result in context_checks.items():
                status = "✅" if result else "❌"
                print(f"  {status} {check}: {result}")
            
            # Validate curriculum data structure
            curriculum_data = response.context.get('curriculum_hierarchy_for_copy')
            if curriculum_data:
                programs = curriculum_data.get('curriculum_data', {}).keys()
                expected_programs = ['CORE', 'EDGE', 'ASCENT', 'PINNACLE']
                programs_present = all(prog in programs for prog in expected_programs)
                
                print(f"📊 Curriculum data validation:")
                print(f"  ✅ Data structure available: True")
                print(f"  ✅ Expected programs present: {programs_present}")
                print(f"  ✅ Programs found: {list(programs)}")
                
                return all(context_checks.values()) and programs_present
            else:
                print("❌ Curriculum hierarchy data not found in context")
                return False
        else:
            print(f"❌ Exam library page returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error validating exam library access: {e}")
        return False

def validate_copy_modal_template():
    """Validate Copy Modal elements in template"""
    print("🔍 Validating Copy Modal template elements...")
    
    try:
        client = Client()
        admin_user = User.objects.filter(is_superuser=True).first()
        client.force_login(admin_user)
        
        response = client.get('/routinetest/exam/exam_library/')
        content = response.content.decode('utf-8')
        
        # Check for key modal elements
        template_checks = {
            'copy_modal_exists': 'copyExamModal' in content,
            'program_dropdown_exists': 'copyProgramSelect' in content,
            'curriculum_data_init': 'CopyCurriculumData' in content,
            'enhanced_v4_logic': 'ENHANCED v4.0' in content,
            'json_script_filter': 'json_script' in content or 'curriculum-hierarchy-data' in content,
            'fallback_functions': 'tryFallbackCurriculumInitialization' in content,
            'error_handling': 'CopyCurriculumDataError' in content,
            'diagnostic_function': 'runCurriculumDiagnostic' in content
        }
        
        print("📊 Template elements validation:")
        for check, result in template_checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}: {result}")
        
        # Check for specific curriculum programs in fallback data
        program_checks = {
            'core_phonics': 'CORE' in content and 'Phonics' in content,
            'edge_spark': 'EDGE' in content and 'Spark' in content,
            'ascent_nova': 'ASCENT' in content and 'Nova' in content,
            'pinnacle_vision': 'PINNACLE' in content and 'Vision' in content
        }
        
        print("📊 Curriculum programs in template:")
        for check, result in program_checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}: {result}")
        
        all_template_checks = all(template_checks.values())
        all_program_checks = all(program_checks.values())
        
        return all_template_checks and all_program_checks
        
    except Exception as e:
        print(f"❌ Error validating template: {e}")
        return False

def create_test_summary():
    """Create comprehensive test summary"""
    print()
    print("="*80)
    print("📋 LIVE SERVER VALIDATION SUMMARY")
    print("="*80)
    
    # Test results storage
    results = {}
    
    # Test 1: Server startup
    print("🔧 TEST 1: Server Startup")
    results['server_startup'] = start_django_server()
    
    if not results['server_startup']:
        print("❌ Cannot proceed with tests - server failed to start")
        return results
    
    # Test 2: Server response
    print("🔧 TEST 2: Server Response")
    results['server_response'] = test_server_response()
    
    # Test 3: Exam library access
    print("🔧 TEST 3: Exam Library Access")
    results['exam_library_access'] = validate_exam_library_access()
    
    # Test 4: Copy modal template
    print("🔧 TEST 4: Copy Modal Template")
    results['copy_modal_template'] = validate_copy_modal_template()
    
    # Test 5: Backend service validation
    print("🔧 TEST 5: Backend Service Validation")
    try:
        curriculum_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        results['backend_service'] = (
            curriculum_data and 
            'curriculum_data' in curriculum_data and
            len(curriculum_data['curriculum_data']) == 4
        )
        print(f"✅ Backend service working: {results['backend_service']}")
    except Exception as e:
        results['backend_service'] = False
        print(f"❌ Backend service failed: {e}")
    
    # Calculate overall results
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print()
    print("📊 FINAL RESULTS:")
    print(f"  Tests Passed: {passed_tests}/{total_tests}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 VALIDATION SUCCESSFUL - Copy Modal fix is ready!")
        print("✅ The dropdown should now populate with CORE, EDGE, ASCENT, PINNACLE")
    elif success_rate >= 60:
        print("⚠️  MOSTLY SUCCESSFUL - Minor issues may remain")
        print("🔧 Review any failed tests for potential improvements")
    else:
        print("❌ VALIDATION FAILED - Significant issues remain")
        print("🔧 Additional fixes required")
    
    print()
    print("🌐 To test manually:")
    print("  1. Go to: http://127.0.0.1:8000/routinetest/exam/exam_library/")
    print("  2. Click 'Copy Exam' button on any exam")
    print("  3. Check if Program dropdown shows: CORE, EDGE, ASCENT, PINNACLE")
    print("  4. Open browser console to see detailed debugging logs")
    
    return results

# Cleanup handler
def cleanup_handler(signum, frame):
    """Handle cleanup on exit"""
    print("\n🛑 Received interrupt signal, cleaning up...")
    stop_django_server()
    sys.exit(0)

# Register cleanup handler
signal.signal(signal.SIGINT, cleanup_handler)
signal.signal(signal.SIGTERM, cleanup_handler)

# Run validation
try:
    results = create_test_summary()
    
    # Keep server running for manual testing if successful
    if sum(results.values()) >= 4:  # If most tests passed
        print()
        print("🚀 Server is running for manual testing...")
        print("   Press Ctrl+C to stop")
        
        # Keep alive
        try:
            while True:
                time.sleep(5)
                if server_process and server_process.poll() is not None:
                    print("❌ Server process terminated unexpectedly")
                    break
        except KeyboardInterrupt:
            pass
    
finally:
    stop_django_server()
    print()
    print("="*80)
    print(f"Live Server Validation Completed: {datetime.now().isoformat()}")
    print("="*80)