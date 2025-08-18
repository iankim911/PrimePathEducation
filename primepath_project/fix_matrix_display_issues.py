#!/usr/bin/env python
"""
Matrix Display Issues Fix
Addresses CSS/JavaScript rendering problems identified in frontend investigation
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def fix_template_css_issues():
    """Fix CSS issues that might hide matrix content"""
    print_header("FIXING TEMPLATE CSS ISSUES")
    
    template_path = "templates/primepath_routinetest/schedule_matrix.html"
    
    # Read current template
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Backup the original
    with open(f"{template_path}.backup", 'w') as f:
        f.write(content)
    print("✅ Created backup of original template")
    
    # CSS fixes to ensure visibility
    css_fixes = """
/* MATRIX DISPLAY FIXES - Ensure visibility */
.matrix-container {
    background: white !important;
    border-radius: 8px;
    padding: 20px !important;
    margin-bottom: 30px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

.matrix-content {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    min-height: 400px !important;
}

/* Ensure monthly matrix is visible by default */
#monthly-matrix {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Matrix Table Visibility */
.matrix-table {
    width: 100% !important;
    border-collapse: separate;
    border-spacing: 0;
    margin-top: 20px;
    display: table !important;
    visibility: visible !important;
    opacity: 1 !important;
    table-layout: fixed !important;
}

.matrix-table thead {
    background: #2E7D32 !important;
    color: white !important;
    display: table-header-group !important;
    visibility: visible !important;
}

.matrix-table tbody {
    display: table-row-group !important;
    visibility: visible !important;
    opacity: 1 !important;
}

.matrix-table th {
    padding: 12px 8px !important;
    text-align: center !important;
    font-weight: 600;
    font-size: 14px !important;
    border: 1px solid #1B5E20 !important;
    position: sticky;
    top: 0;
    z-index: 10;
    display: table-cell !important;
    visibility: visible !important;
    background: #2E7D32 !important;
    color: white !important;
}

.matrix-table td {
    border: 1px solid #E0E0E0 !important;
    padding: 4px !important;
    text-align: center !important;
    position: relative;
    display: table-cell !important;
    visibility: visible !important;
    min-width: 80px !important;
    min-height: 60px !important;
}

/* Matrix Cell Critical Fixes */
.matrix-cell {
    min-height: 60px !important;
    max-height: none !important;
    padding: 8px !important;
    cursor: pointer;
    position: relative;
    transition: all 0.3s ease;
    display: flex !important;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    visibility: visible !important;
    opacity: 1 !important;
    background: #FAFAFA !important;
    border-radius: 4px;
    width: 100% !important;
    box-sizing: border-box;
}

.matrix-cell.empty {
    background: #FAFAFA !important;
    border: 1px solid #E0E0E0 !important;
}

.matrix-cell.scheduled {
    background: #E3F2FD !important;
    border: 1px solid #2196F3 !important;
}

.cell-icon {
    font-size: 24px !important;
    margin-bottom: 4px !important;
    display: block !important;
    visibility: visible !important;
    line-height: 1 !important;
}

.cell-count {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #555 !important;
    background: white !important;
    padding: 2px 8px !important;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    display: block !important;
    visibility: visible !important;
}

/* Responsive fixes */
@media (max-width: 1200px) {
    .matrix-table {
        font-size: 14px !important;
        min-width: 100% !important;
    }
    
    .matrix-table th,
    .matrix-table td {
        padding: 6px 4px !important;
        min-width: 60px !important;
    }
    
    .cell-icon {
        font-size: 20px !important;
    }
}

@media (max-width: 768px) {
    .matrix-container {
        padding: 15px !important;
        overflow-x: auto !important;
    }
    
    .matrix-table {
        min-width: 800px !important;
        width: 800px !important;
    }
    
    .matrix-table th,
    .matrix-table td {
        min-width: 50px !important;
        font-size: 12px !important;
    }
}

/* Debug borders (temporary) */
.debug-mode .matrix-table th {
    border: 2px solid red !important;
}

.debug-mode .matrix-table td {
    border: 2px solid blue !important;
}

.debug-mode .matrix-cell {
    border: 2px solid green !important;
    background: yellow !important;
}
"""
    
    # Find the end of existing CSS and insert fixes
    css_end_marker = "{% endblock %}"
    css_insertion_point = content.find(css_end_marker)
    
    if css_insertion_point != -1:
        # Insert before the endblock
        new_content = content[:css_insertion_point] + css_fixes + "\n" + content[css_insertion_point:]
        
        with open(template_path, 'w') as f:
            f.write(new_content)
        print("✅ Added CSS visibility fixes to template")
    else:
        print("❌ Could not find CSS insertion point")
        return False
    
    return True


def fix_javascript_issues():
    """Fix JavaScript issues that might prevent matrix display"""
    print_header("FIXING JAVASCRIPT ISSUES")
    
    template_path = "templates/primepath_routinetest/schedule_matrix.html"
    
    # Read current template
    with open(template_path, 'r') as f:
        content = f.read()
    
    # JavaScript fixes for matrix display
    js_fixes = """
// MATRIX DISPLAY FIXES - Ensure proper initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('[MATRIX FIX] DOM loaded, initializing matrix fixes...');
    
    // Force show monthly matrix on page load
    const monthlyMatrix = document.getElementById('monthly-matrix');
    const quarterlyMatrix = document.getElementById('quarterly-matrix');
    
    if (monthlyMatrix) {
        monthlyMatrix.style.display = 'block';
        monthlyMatrix.style.visibility = 'visible';
        monthlyMatrix.style.opacity = '1';
        console.log('[MATRIX FIX] Monthly matrix forced visible');
    }
    
    if (quarterlyMatrix) {
        quarterlyMatrix.style.display = 'none';
        console.log('[MATRIX FIX] Quarterly matrix hidden initially');
    }
    
    // Ensure all matrix cells are visible
    const matrixCells = document.querySelectorAll('.matrix-cell');
    console.log('[MATRIX FIX] Found', matrixCells.length, 'matrix cells');
    
    matrixCells.forEach((cell, index) => {
        cell.style.display = 'flex';
        cell.style.visibility = 'visible';
        cell.style.opacity = '1';
        cell.style.minHeight = '60px';
        
        // Add debug info for first few cells
        if (index < 5) {
            console.log('[MATRIX FIX] Cell', index, 'data:', {
                id: cell.dataset.cellId,
                class: cell.dataset.class,
                period: cell.dataset.period,
                type: cell.dataset.type
            });
        }
    });
    
    // Ensure table is visible
    const matrixTables = document.querySelectorAll('.matrix-table');
    console.log('[MATRIX FIX] Found', matrixTables.length, 'matrix tables');
    
    matrixTables.forEach(table => {
        table.style.display = 'table';
        table.style.visibility = 'visible';
        table.style.opacity = '1';
        table.style.width = '100%';
    });
    
    // Fix tab switching to ensure proper display
    const tabButtons = document.querySelectorAll('.matrix-tab');
    tabButtons.forEach(tab => {
        tab.addEventListener('click', function() {
            console.log('[MATRIX FIX] Tab clicked:', this.dataset.type);
            
            // Ensure proper display switching
            if (this.dataset.type === 'monthly') {
                if (monthlyMatrix) {
                    monthlyMatrix.style.display = 'block';
                    monthlyMatrix.style.visibility = 'visible';
                    monthlyMatrix.style.opacity = '1';
                }
                if (quarterlyMatrix) {
                    quarterlyMatrix.style.display = 'none';
                }
            } else if (this.dataset.type === 'quarterly') {
                if (monthlyMatrix) {
                    monthlyMatrix.style.display = 'none';
                }
                if (quarterlyMatrix) {
                    quarterlyMatrix.style.display = 'block';
                    quarterlyMatrix.style.visibility = 'visible';
                    quarterlyMatrix.style.opacity = '1';
                }
            }
        });
    });
    
    // Add debug mode toggle (Ctrl+Shift+D)
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.key === 'D') {
            document.body.classList.toggle('debug-mode');
            console.log('[MATRIX FIX] Debug mode toggled');
        }
    });
    
    console.log('[MATRIX FIX] Matrix initialization complete');
});

// Enhanced switchTab function with forced visibility
function switchTab(type) {
    console.log('[MATRIX FIX] Enhanced switchTab called:', type);
    
    // Call original function first
    if (window.originalSwitchTab) {
        window.originalSwitchTab(type);
    }
    
    // Force visibility fixes
    const monthlyMatrix = document.getElementById('monthly-matrix');
    const quarterlyMatrix = document.getElementById('quarterly-matrix');
    
    if (type === 'monthly') {
        if (monthlyMatrix) {
            monthlyMatrix.style.display = 'block';
            monthlyMatrix.style.visibility = 'visible';
            monthlyMatrix.style.opacity = '1';
            console.log('[MATRIX FIX] Monthly matrix made visible');
        }
        if (quarterlyMatrix) {
            quarterlyMatrix.style.display = 'none';
        }
    } else if (type === 'quarterly') {
        if (monthlyMatrix) {
            monthlyMatrix.style.display = 'none';
        }
        if (quarterlyMatrix) {
            quarterlyMatrix.style.display = 'block';
            quarterlyMatrix.style.visibility = 'visible';
            quarterlyMatrix.style.opacity = '1';
            console.log('[MATRIX FIX] Quarterly matrix made visible');
        }
    }
    
    // Update current tab
    currentTab = type;
    
    // Update tab states
    document.querySelectorAll('.matrix-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.dataset.type === type) {
            tab.classList.add('active');
        }
    });
}

// Backup original function if it exists
if (typeof switchTab !== 'undefined') {
    window.originalSwitchTab = switchTab;
}
"""
    
    # Find the end of existing JavaScript and insert fixes
    js_end_marker = "{% endblock %}"
    js_insertion_point = content.rfind(js_end_marker)  # Find last occurrence
    
    if js_insertion_point != -1:
        # Insert before the last endblock
        new_content = content[:js_insertion_point] + js_fixes + "\n</script>\n" + content[js_insertion_point:]
        
        with open(template_path, 'w') as f:
            f.write(new_content)
        print("✅ Added JavaScript visibility fixes to template")
    else:
        print("❌ Could not find JavaScript insertion point")
        return False
    
    return True


def add_debug_mode():
    """Add debug mode to help identify issues"""
    print_header("ADDING DEBUG MODE")
    
    template_path = "templates/primepath_routinetest/schedule_matrix.html"
    
    # Read current template
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Add debug indicator to template
    debug_html = """
<!-- DEBUG MODE INDICATOR -->
<div id="matrix-debug-panel" style="position: fixed; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: #00ff00; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; z-index: 9999; display: none;">
    <div>🐛 Matrix Debug Mode</div>
    <div>Press Ctrl+Shift+D to toggle</div>
    <div id="debug-info"></div>
</div>

<script>
// Show debug panel in debug mode
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        const panel = document.getElementById('matrix-debug-panel');
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        
        if (panel.style.display === 'block') {
            updateDebugInfo();
        }
    }
});

function updateDebugInfo() {
    const debugInfo = document.getElementById('debug-info');
    if (debugInfo) {
        const matrixCells = document.querySelectorAll('.matrix-cell');
        const visibleCells = Array.from(matrixCells).filter(cell => 
            getComputedStyle(cell).display !== 'none' && 
            getComputedStyle(cell).visibility !== 'hidden'
        );
        
        debugInfo.innerHTML = `
            <div>Total cells: ${matrixCells.length}</div>
            <div>Visible cells: ${visibleCells.length}</div>
            <div>Current tab: ${currentTab || 'unknown'}</div>
        `;
    }
}
</script>
"""
    
    # Find a good insertion point (after the matrix container)
    insertion_marker = '<div class="matrix-container">'
    insertion_point = content.find(insertion_marker)
    
    if insertion_point != -1:
        new_content = content[:insertion_point] + debug_html + "\n" + content[insertion_point:]
        
        with open(template_path, 'w') as f:
            f.write(new_content)
        print("✅ Added debug mode to template")
    else:
        print("❌ Could not find HTML insertion point")
        return False
    
    return True


def create_simple_test_template():
    """Create a simplified test template to verify basic functionality"""
    print_header("CREATING SIMPLE TEST TEMPLATE")
    
    simple_template = '''{% extends 'routinetest_base.html' %}
{% load static %}
{% load matrix_filters %}

{% block title %}Matrix Test - RoutineTest{% endblock %}

{% block extra_css %}
<style>
.test-container {
    padding: 20px;
    background: white;
    margin: 20px;
    border-radius: 8px;
}

.test-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}

.test-table th,
.test-table td {
    border: 2px solid #333;
    padding: 10px;
    text-align: center;
}

.test-table th {
    background: #2E7D32;
    color: white;
    font-weight: bold;
}

.test-cell {
    min-height: 60px;
    background: #f0f0f0;
    border: 1px solid #ccc;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 10px;
}

.test-icon {
    font-size: 24px;
    margin-bottom: 5px;
}
</style>
{% endblock %}

{% block content %}
<div class="test-container">
    <h1>🧪 Matrix Rendering Test</h1>
    
    <h2>Basic Table Test</h2>
    <table class="test-table">
        <thead>
            <tr>
                <th>Class</th>
                <th>January</th>
                <th>February</th>
                <th>March</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Class 7A</td>
                <td>
                    <div class="test-cell">
                        <div class="test-icon">📅</div>
                        <div>1 exam</div>
                    </div>
                </td>
                <td>
                    <div class="test-cell">
                        <div class="test-icon">⬜</div>
                    </div>
                </td>
                <td>
                    <div class="test-cell">
                        <div class="test-icon">⬜</div>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
    
    <h2>Matrix Data Test</h2>
    <p>Monthly matrix keys: {{ monthly_matrix.keys|length }}</p>
    <p>Month names: {{ month_names|length }}</p>
    
    {% if monthly_matrix %}
        <h3>Matrix Data Structure:</h3>
        {% for class_code, class_data in monthly_matrix.items %}
            <p><strong>{{ class_code }}</strong>: {{ class_data.display_name }} ({{ class_data.cells.keys|length }} cells)</p>
        {% endfor %}
    {% endif %}
    
    <h2>Template Filter Test</h2>
    {% if monthly_matrix %}
        {% for class_code, class_data in monthly_matrix.items %}
            <p>Testing get_item filter for {{ class_code }}:</p>
            <ul>
            {% for month in months %}
                {% with cell=class_data.cells|get_item:month %}
                <li>{{ month }}: {% if cell %}{{ cell.icon }} ({{ cell.status }}){% else %}No data{% endif %}</li>
                {% endwith %}
            {% endfor %}
            </ul>
        {% endfor %}
    {% endif %}
</div>
{% endblock %}
'''
    
    test_template_path = "templates/primepath_routinetest/matrix_test.html"
    with open(test_template_path, 'w') as f:
        f.write(simple_template)
    
    print(f"✅ Created simple test template: {test_template_path}")
    print("   Access via: /RoutineTest/matrix-test/")
    
    return True


def main():
    """Run all matrix display fixes"""
    print_header("MATRIX DISPLAY ISSUES - COMPREHENSIVE FIX")
    
    fixes_applied = []
    
    try:
        # Apply CSS fixes
        if fix_template_css_issues():
            fixes_applied.append("CSS visibility fixes")
        
        # Apply JavaScript fixes
        if fix_javascript_issues():
            fixes_applied.append("JavaScript display fixes")
        
        # Add debug mode
        if add_debug_mode():
            fixes_applied.append("Debug mode")
        
        # Create test template
        if create_simple_test_template():
            fixes_applied.append("Simple test template")
        
        print_header("FIX SUMMARY")
        
        if fixes_applied:
            print("✅ Successfully applied fixes:")
            for fix in fixes_applied:
                print(f"   ✓ {fix}")
            
            print("\n📋 NEXT STEPS:")
            print("   1. Restart Django server")
            print("   2. Clear browser cache (Ctrl+Shift+R)")
            print("   3. Visit /RoutineTest/schedule-matrix/")
            print("   4. Press Ctrl+Shift+D for debug mode")
            print("   5. Test /RoutineTest/matrix-test/ for simple verification")
            
            print("\n🔧 TESTING:")
            print("   - Check browser console for '[MATRIX FIX]' messages")
            print("   - Verify all month headers are visible")
            print("   - Confirm matrix cells have icons and content")
            print("   - Test tab switching between monthly/quarterly")
            
        else:
            print("❌ No fixes could be applied")
            
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()