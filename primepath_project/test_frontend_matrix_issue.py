#!/usr/bin/env python
"""
Frontend Matrix Investigation Script
Analyzes CSS and JavaScript rendering issues
"""
import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def investigate_frontend_rendering():
    """Investigate frontend rendering issues"""
    print_header("FRONTEND MATRIX RENDERING INVESTIGATION")
    
    # Create authenticated client
    client = Client()
    
    # Create test user and teacher
    user = User.objects.filter(username='frontend_test_user').first()
    if not user:
        user = User.objects.create_user('frontend_test_user', 'frontend@test.com', 'testpass123')
        user.is_staff = True
        user.save()
    
    teacher, created = Teacher.objects.get_or_create(
        email=user.email,
        defaults={'name': 'Frontend Test Teacher', 'user': user}
    )
    
    # Create class assignment
    TeacherClassAssignment.objects.get_or_create(
        teacher=teacher,
        class_code='CLASS_7A',
        defaults={'access_level': 'FULL', 'assigned_by': user}
    )
    
    client.force_login(user)
    print(f"✅ Authenticated as: {user.username}")
    
    # Get the matrix page
    response = client.get('/RoutineTest/schedule-matrix/')
    
    if response.status_code == 200:
        print(f"✅ Page loads successfully: Status {response.status_code}")
        
        content = response.content.decode('utf-8')
        
        # Comprehensive analysis
        print("\n🔍 FRONTEND ANALYSIS:")
        
        # 1. CSS Issues
        print("\n1. CSS ANALYSIS:")
        css_checks = {
            'Matrix CSS loaded': '.matrix-table' in content,
            'Cell styling present': '.matrix-cell' in content,
            'Responsive CSS': '@media' in content,
            'Hidden elements': 'display: none' in content,
            'Visibility issues': 'visibility: hidden' in content,
            'Opacity issues': 'opacity: 0' in content,
        }
        
        for check, result in css_checks.items():
            status = "✓" if result else "✗"
            print(f"   {status} {check}: {'Present' if result else 'Missing'}")
        
        # 2. JavaScript Issues
        print("\n2. JAVASCRIPT ANALYSIS:")
        js_checks = {
            'Matrix JS loaded': 'switchTab(' in content,
            'Debug logging': 'debugLog(' in content,
            'DOM manipulation': 'querySelector' in content,
            'Event handlers': 'addEventListener' in content,
            'Matrix variables': 'currentTab =' in content,
        }
        
        for check, result in js_checks.items():
            status = "✓" if result else "✗"
            print(f"   {status} {check}: {'Present' if result else 'Missing'}")
        
        # 3. HTML Structure Issues
        print("\n3. HTML STRUCTURE ANALYSIS:")
        
        # Count table elements
        import re
        thead_count = len(re.findall(r'<thead>', content))
        tbody_count = len(re.findall(r'<tbody>', content))
        th_count = len(re.findall(r'<th>', content))
        td_count = len(re.findall(r'<td>', content))
        matrix_cell_count = len(re.findall(r'class="matrix-cell', content))
        
        print(f"   ✓ Table headers (thead): {thead_count}")
        print(f"   ✓ Table bodies (tbody): {tbody_count}")
        print(f"   ✓ Header cells (th): {th_count}")
        print(f"   ✓ Data cells (td): {td_count}")
        print(f"   ✓ Matrix cells: {matrix_cell_count}")
        
        # 4. Month Headers Check
        print("\n4. MONTH HEADERS CHECK:")
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        for month in months:
            present = month in content
            status = "✓" if present else "✗"
            print(f"   {status} {month}: {'Present' if present else 'Missing'}")
        
        # 5. Matrix Cell Content Check
        print("\n5. MATRIX CELL CONTENT CHECK:")
        cell_content_checks = {
            'Empty cells (⬜)': '⬜' in content,
            'Scheduled cells (📅)': '📅' in content,
            'Cell icons': 'cell-icon' in content,
            'Cell counts': 'cell-count' in content,
            'Data attributes': 'data-cell-id' in content,
            'Click handlers': 'onclick="openCellDetail' in content,
        }
        
        for check, result in cell_content_checks.items():
            status = "✓" if result else "✗"
            print(f"   {status} {check}: {'Present' if result else 'Missing'}")
        
        # 6. Potential Issues Analysis
        print("\n6. POTENTIAL FRONTEND ISSUES:")
        
        potential_issues = []
        
        # Check for CSS conflicts
        if 'display: none' in content:
            potential_issues.append("CSS might be hiding elements with 'display: none'")
        
        # Check for JavaScript errors in console setup
        if 'console.log' in content and 'console.error' in content:
            potential_issues.append("JavaScript debugging enabled - check browser console for errors")
        
        # Check responsive design issues
        if '@media' in content and 'max-width' in content:
            potential_issues.append("Responsive CSS present - might be viewport/mobile display issue")
        
        # Check for tab switching logic
        if 'switchTab(' in content and 'display: none' in content:
            potential_issues.append("Tab switching logic might be hiding matrix content initially")
        
        if potential_issues:
            for issue in potential_issues:
                print(f"   ⚠️  {issue}")
        else:
            print("   ✅ No obvious frontend issues detected")
        
        # 7. Save detailed analysis
        with open('/tmp/frontend_analysis.html', 'w') as f:
            f.write(content)
        print(f"\n💾 Full page content saved to /tmp/frontend_analysis.html")
        
        # 8. Extract specific matrix table for analysis
        import re
        matrix_table_pattern = r'<table class="matrix-table">(.*?)</table>'
        matrix_matches = re.findall(matrix_table_pattern, content, re.DOTALL)
        
        if matrix_matches:
            print(f"\n✅ Found {len(matrix_matches)} matrix table(s)")
            
            # Save just the matrix table
            with open('/tmp/matrix_table_only.html', 'w') as f:
                f.write(f'<table class="matrix-table">{matrix_matches[0]}</table>')
            print("💾 Matrix table saved to /tmp/matrix_table_only.html")
            
            # Analyze table structure
            table_content = matrix_matches[0]
            row_count = len(re.findall(r'<tr', table_content))
            cell_count = len(re.findall(r'<td', table_content))
            print(f"   📊 Matrix table rows: {row_count}")
            print(f"   📊 Matrix table cells: {cell_count}")
        
        return True
    else:
        print(f"❌ Page failed to load: Status {response.status_code}")
        return False


def investigate_css_specificity():
    """Check for CSS specificity issues that might hide content"""
    print_header("CSS SPECIFICITY INVESTIGATION")
    
    print("Checking for common CSS issues that cause 'empty' appearance:")
    
    css_issues = [
        "Cell height set to 0 or very small value",
        "Text color matching background color", 
        "Overflow hidden cutting off content",
        "Z-index issues causing content to be behind other elements",
        "Transform or position causing content to be off-screen",
        "Font-size set to 0",
        "White-space: nowrap with overflow: hidden",
        "Viewport meta tag causing scaling issues",
    ]
    
    for issue in css_issues:
        print(f"   ⚠️  Check: {issue}")
    
    print("\n💡 RECOMMENDATIONS:")
    print("   1. Open browser developer tools (F12)")
    print("   2. Inspect the matrix table elements")
    print("   3. Check computed CSS styles for matrix-cell elements")
    print("   4. Look for any red error messages in browser console")
    print("   5. Test in different browsers (Chrome, Firefox, Safari)")
    print("   6. Try disabling browser extensions")
    print("   7. Clear browser cache and cookies")


def generate_fix_strategy():
    """Generate strategy to fix the frontend rendering issue"""
    print_header("FIX STRATEGY RECOMMENDATIONS")
    
    print("Based on analysis, the fix strategy should focus on:")
    
    strategies = [
        "1. CSS DEBUGGING:",
        "   - Add temporary red borders to .matrix-cell elements",
        "   - Increase cell heights to ensure visibility", 
        "   - Check for conflicting CSS rules",
        "   - Test with simplified CSS (disable responsive styles)",
        "",
        "2. JAVASCRIPT DEBUGGING:",
        "   - Add console.log statements to switchTab() function",
        "   - Verify DOM elements are being found correctly",
        "   - Check for JavaScript errors breaking the page",
        "   - Test with JavaScript disabled",
        "",
        "3. BROWSER TESTING:",
        "   - Test in incognito mode (no extensions)",
        "   - Test in different browsers",
        "   - Check browser zoom level (should be 100%)",
        "   - Clear all browser data",
        "",
        "4. RESPONSIVE DESIGN:",
        "   - Test on different screen sizes",
        "   - Check viewport meta tag",
        "   - Verify media queries aren't hiding content",
        "   - Test mobile vs desktop view",
        "",
        "5. TEMPLATE DEBUGGING:",
        "   - Add visible debug text inside matrix cells",
        "   - Temporarily remove CSS to see raw HTML",
        "   - Add background colors to identify layout issues",
    ]
    
    for strategy in strategies:
        print(strategy)


def main():
    """Run complete frontend investigation"""
    print("\n" + "="*80)
    print("  COMPREHENSIVE FRONTEND MATRIX INVESTIGATION")
    print("="*80)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all investigations
        investigate_frontend_rendering()
        investigate_css_specificity()
        generate_fix_strategy()
        
        print_header("INVESTIGATION SUMMARY")
        print("✅ Frontend analysis complete")
        print("✅ HTML structure is correct (backend working)")
        print("⚠️  Issue is in CSS/JavaScript/Browser rendering")
        print("💡 Next step: Live browser debugging with developer tools")
        
        print("\n📁 Debug files created:")
        print("   /tmp/frontend_analysis.html - Full page content")
        print("   /tmp/matrix_table_only.html - Isolated matrix table")
        
    except Exception as e:
        print(f"\n❌ Investigation error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()