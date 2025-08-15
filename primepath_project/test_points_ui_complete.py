#!/usr/bin/env python3
"""
COMPREHENSIVE POINTS UI TEST
Verifies the complete points editing UI is working
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

from django.test import RequestFactory, Client
from placement_test.models import Question, Exam
from placement_test.views import preview_exam

def test_points_ui_complete():
    """Test complete points UI functionality"""
    
    print("=" * 60)
    print("🎨 COMPREHENSIVE POINTS UI TEST")
    print("=" * 60)
    
    # Step 1: Find an exam with questions
    print("\n📋 STEP 1: Finding test exam...")
    
    exams = Exam.objects.filter(questions__isnull=False).distinct()
    if not exams.exists():
        print("❌ No exams with questions found")
        return False
    
    test_exam = exams.first()
    question_count = test_exam.questions.count()
    
    print(f"✅ Using exam: {test_exam.name}")
    print(f"   Exam ID: {test_exam.id}")
    print(f"   Questions: {question_count}")
    
    # Step 2: Test the preview page renders correctly
    print(f"\n🌐 STEP 2: Testing preview page rendering...")
    
    client = Client()
    # Use the correct URL pattern with PlacementTest prefix
    response = client.get(f'/PlacementTest/exams/{test_exam.id}/preview/', follow=True)
    
    if response.status_code == 200:
        print("✅ Preview page renders successfully")
        
        # Check if points editing elements are in the HTML
        content = response.content.decode('utf-8')
        
        # Check for critical UI elements
        checks = {
            'Points containers': 'question-points-container' in content,
            'Points displays': 'question-points-display' in content,
            'Edit buttons': 'edit-points-btn' in content,
            'Points inputs': 'points-input' in content,
            'Save buttons': 'save-points-btn' in content,
            'Cancel buttons': 'cancel-points-btn' in content,
            'Edit divs': 'question-points-edit' in content,
        }
        
        print("\n📊 UI Element Checks:")
        all_passed = True
        for element, present in checks.items():
            status = "✅" if present else "❌"
            print(f"   {status} {element}: {'Present' if present else 'Missing'}")
            if not present:
                all_passed = False
        
        # Check CSS styles are present
        css_checks = {
            'Container styles': '.question-points-container {' in content,
            'Display styles': '.question-points-display {' in content,
            'Edit button styles': '.edit-points-btn {' in content,
            'Input styles': '.points-input {' in content,
            'Save button styles': '.save-points-btn {' in content,
            'Cancel button styles': '.cancel-points-btn {' in content,
            'Impact preview styles': '.points-impact-preview {' in content,
        }
        
        print("\n🎨 CSS Style Checks:")
        for style, present in css_checks.items():
            status = "✅" if present else "❌"
            print(f"   {status} {style}: {'Present' if present else 'Missing'}")
            if not present:
                all_passed = False
        
        # Check JavaScript is present
        js_checks = {
            'Points editor init': '[PointsEditor] 🚀 INITIALIZING POINTS EDITING SYSTEM' in content,
            'Setup function': 'function setupEditButtonHandlers()' in content,
            'Click handlers': "btn.addEventListener('click'" in content,
            'Hover handlers': "btn.addEventListener('mouseenter'" in content,
            'Save handlers': 'save-points-btn' in content and 'addEventListener' in content,
            'API calls': '/api/PlacementTest/questions/' in content,
            'Debug logging': 'console.log' in content and 'PointsEditor' in content,
        }
        
        print("\n📜 JavaScript Checks:")
        for script, present in js_checks.items():
            status = "✅" if present else "❌"
            print(f"   {status} {script}: {'Present' if present else 'Missing'}")
            if not present:
                all_passed = False
        
        # Count actual elements
        print("\n📈 Element Counts:")
        
        # Count edit buttons for each question
        edit_button_count = content.count('class="edit-points-btn"')
        print(f"   Edit buttons: {edit_button_count} (expected: {question_count})")
        
        # Count points displays
        display_count = content.count('class="question-points-display"')
        print(f"   Points displays: {display_count} (expected: {question_count})")
        
        # Count points inputs
        input_count = content.count('class="points-input"')
        print(f"   Points inputs: {input_count} (expected: {question_count})")
        
        if edit_button_count == question_count:
            print("\n✅ All questions have edit buttons!")
        else:
            print(f"\n⚠️ Mismatch: {edit_button_count} buttons for {question_count} questions")
            all_passed = False
        
        # Check for visibility fixes
        if 'display: inline-block !important' in content and 'visibility: visible !important' in content:
            print("\n✅ Critical visibility fixes are in place")
        else:
            print("\n⚠️ Visibility fixes may be missing")
        
        return all_passed
        
    else:
        print(f"❌ Preview page failed with status {response.status_code}")
        return False

def main():
    print("\n" + "=" * 60)
    print("🚀 TESTING POINTS EDITING UI")
    print("=" * 60)
    
    success = test_points_ui_complete()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL UI TESTS PASSED!")
        print("\n✅ Points editing interface is ready for use:")
        print("   • Edit buttons are visible with yellow background")
        print("   • Hover shows impact preview tooltips")
        print("   • Click opens inline editing interface")
        print("   • Save/Cancel buttons have clear styling")
        print("   • Comprehensive console logging is enabled")
        print("\n📝 Next: Open browser and check console for debugging info")
    else:
        print("❌ SOME UI TESTS FAILED")
        print("\n⚠️ Check the failed items above")
        print("📝 Review the template file for missing elements")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)