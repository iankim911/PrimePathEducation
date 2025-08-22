#!/usr/bin/env python
"""
Test script to verify the Copy Modal Curriculum dropdown fix
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_copy_modal_curriculum():
    print("=" * 80)
    print("TESTING COPY MODAL CURRICULUM DROPDOWN FIX")
    print("=" * 80)
    
    client = Client()
    
    # Login as admin
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No admin user found")
        return False
    
    client.force_login(admin)
    print(f"✅ Logged in as: {admin.username}")
    
    # Load the exam list page
    response = client.get('/RoutineTest/exams/')
    if response.status_code != 200:
        print(f"❌ Failed to load exam list page: {response.status_code}")
        return False
    
    print("✅ Exam list page loaded successfully")
    
    # Check if curriculum data is in the response
    content = response.content.decode()
    
    # Check for curriculum data initialization
    if 'window.CopyCurriculumData = {}' in content:
        print("✅ CopyCurriculumData initialization found in HTML")
    else:
        print("❌ CopyCurriculumData initialization NOT found")
        return False
    
    # Check for the populate function
    if 'function populateCopyProgramDropdown()' in content:
        print("✅ populateCopyProgramDropdown function found")
    else:
        print("❌ populateCopyProgramDropdown function NOT found")
        return False
    
    # Check for the fix - the call to populate in openCopyModalInternal
    if 'populateCopyProgramDropdown()' in content and 'openCopyModalInternal' in content:
        # Check if the call is in the right place
        modal_internal_start = content.find('window.openCopyModalInternal')
        if modal_internal_start > -1:
            modal_internal_section = content[modal_internal_start:modal_internal_start + 3000]
            if 'populateCopyProgramDropdown()' in modal_internal_section:
                print("✅ FIX APPLIED: populateCopyProgramDropdown() is called in openCopyModalInternal")
            else:
                print("❌ FIX NOT APPLIED: populateCopyProgramDropdown() not called in openCopyModalInternal")
                return False
    
    # Check for curriculum data for each program
    programs = ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']
    programs_found = []
    
    for program in programs:
        # Look for program data in the JavaScript
        if f"'{program}'" in content or f'"{program}"' in content:
            # More specific check - look for the program in curriculum data structure
            if f"window.CopyCurriculumData['{program}']" in content:
                programs_found.append(program)
                print(f"✅ {program} curriculum data found")
            else:
                print(f"⚠️  {program} mentioned but not in curriculum data structure")
    
    if len(programs_found) == 4:
        print(f"✅ All 4 programs found in curriculum data")
    else:
        print(f"⚠️  Only {len(programs_found)}/4 programs found: {programs_found}")
    
    # Check for the modal HTML structure
    if 'id="copyExamModal"' in content:
        print("✅ Copy exam modal HTML found")
    else:
        print("❌ Copy exam modal HTML NOT found")
        return False
    
    if 'id="copyProgramSelect"' in content:
        print("✅ Program select dropdown HTML found")
    else:
        print("❌ Program select dropdown HTML NOT found")
        return False
    
    # Check for the copy buttons
    copy_button_count = content.count('openCopyModal(')
    if copy_button_count > 0:
        print(f"✅ Found {copy_button_count} copy exam buttons")
    else:
        print("❌ No copy exam buttons found")
    
    print("\n" + "=" * 80)
    print("TEST RESULTS:")
    print("=" * 80)
    
    # Final verification
    critical_checks = [
        'window.CopyCurriculumData = {}' in content,
        'function populateCopyProgramDropdown()' in content,
        'populateCopyProgramDropdown()' in content[content.find('openCopyModalInternal'):content.find('openCopyModalInternal')+3000] if 'openCopyModalInternal' in content else False,
        'id="copyProgramSelect"' in content,
        len(programs_found) >= 3  # At least 3 programs should be found
    ]
    
    if all(critical_checks):
        print("✅✅✅ ALL CRITICAL CHECKS PASSED - FIX IS WORKING!")
        print("\nThe copy modal should now show program names when opened.")
        return True
    else:
        print("❌ Some critical checks failed")
        print(f"Critical checks status: {critical_checks}")
        return False

if __name__ == "__main__":
    success = test_copy_modal_curriculum()
    sys.exit(0 if success else 1)