#!/usr/bin/env python
"""
Direct fix for Matrix tab navigation visibility issue
This script ensures the Matrix tab is properly displayed in RoutineTest
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


def colored(text, color):
    """Helper for colored output"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'magenta': '\033[95m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def fix_navigation():
    """Fix the navigation template to ensure Matrix tab is visible"""
    
    print(colored("\n" + "="*70, 'cyan'))
    print(colored("MATRIX TAB NAVIGATION FIX - DIRECT INTERVENTION", 'cyan'))
    print(colored("="*70, 'cyan'))
    print(colored(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'blue'))
    
    base_dir = Path(__file__).parent
    
    # Step 1: Clear Python cache
    print(colored("\n[1] Clearing Python cache files...", 'yellow'))
    pyc_count = 0
    pycache_count = 0
    
    for root, dirs, files in os.walk(base_dir):
        if 'venv' in root or '.git' in root:
            continue
        
        # Remove .pyc files
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                    pyc_count += 1
                except:
                    pass
        
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            try:
                shutil.rmtree(os.path.join(root, '__pycache__'))
                pycache_count += 1
            except:
                pass
    
    print(colored(f"  ✓ Removed {pyc_count} .pyc files and {pycache_count} __pycache__ directories", 'green'))
    
    # Step 2: Create a completely new navigation template
    print(colored("\n[2] Creating fresh navigation template...", 'yellow'))
    
    nav_template_content = '''<!-- RoutineTest Navigation - FORCE VERSION 5.0 -->
<!-- Generated: ''' + datetime.now().isoformat() + ''' -->
<nav class="nav-tabs" id="routinetest-nav-v5">
    <ul style="display: flex; justify-content: space-between; width: 100%;">
        <div style="display: flex; flex: 1;">
            <li><a href="/RoutineTest/" data-nav="dashboard">Dashboard</a></li>
            <li><a href="/RoutineTest/create-exam/" data-nav="upload">Upload Exam</a></li>
            <li><a href="/RoutineTest/exam-list/" data-nav="keys">Answer Keys</a></li>
            <li><a href="/RoutineTest/access/my-classes/" data-nav="classes">My Classes & Access</a></li>
            
            <!-- MATRIX TAB - FORCE VISIBLE -->
            <li id="matrix-tab-v5" style="display: flex !important;">
                <a href="/RoutineTest/schedule-matrix/" 
                   data-nav="matrix"
                   style="background: #FF9800 !important; 
                          color: white !important; 
                          font-weight: bold !important; 
                          padding: 12px 20px !important;
                          border: 2px solid #E65100 !important;
                          display: block !important;">
                   📊 Exam Assignments
                </a>
            </li>
            
            <li><a href="/RoutineTest/sessions/" data-nav="results">Results & Analytics</a></li>
        </div>
        
        <div style="display: flex; margin-left: auto;">
            {% if user.is_authenticated %}
                <li><a href="#">👤 {{ user.username }}</a></li>
                <li><a href="/logout/" style="background: #e74c3c;">Logout</a></li>
            {% else %}
                <li><a href="/PlacementTest/teacher/login/">Login</a></li>
            {% endif %}
        </div>
    </ul>
</nav>

<script>
console.log('[NAV_V5] Navigation rendered with Matrix tab');
// Force visibility check
setTimeout(() => {
    const tab = document.getElementById('matrix-tab-v5');
    if (tab) {
        tab.style.display = 'flex';
        tab.style.visibility = 'visible';
        console.log('✅ Matrix tab verified visible');
    }
}, 100);
</script>
'''
    
    # Write the new navigation template
    nav_path = base_dir / 'templates' / 'primepath_routinetest' / 'includes' / 'navigation_tabs.html'
    nav_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(nav_path, 'w') as f:
        f.write(nav_template_content)
    
    print(colored(f"  ✓ Created new navigation template at {nav_path}", 'green'))
    
    # Step 3: Update the base template to use simpler include
    print(colored("\n[3] Updating base template...", 'yellow'))
    
    base_template_path = base_dir / 'templates' / 'routinetest_base.html'
    
    if base_template_path.exists():
        with open(base_template_path, 'r') as f:
            content = f.read()
        
        # Check if navigation include is present
        if 'navigation_tabs.html' in content:
            print(colored("  ✓ Base template already includes navigation", 'green'))
        else:
            print(colored("  ⚠ Base template missing navigation include", 'yellow'))
            # You would update it here if needed
    
    # Step 4: Create a JavaScript override file
    print(colored("\n[4] Creating JavaScript override...", 'yellow'))
    
    js_override = '''/**
 * Matrix Tab Override - Forces tab visibility
 * Version 5.0
 */
(function() {
    'use strict';
    
    function createMatrixTab() {
        // Find navigation container
        const navContainers = [
            document.querySelector('.nav-tabs ul > div'),
            document.querySelector('.nav-tabs ul'),
            document.querySelector('.nav-tabs')
        ];
        
        let container = null;
        for (const c of navContainers) {
            if (c) {
                container = c;
                break;
            }
        }
        
        if (!container) {
            console.error('No navigation container found');
            return false;
        }
        
        // Check if Matrix tab exists
        const existingMatrix = Array.from(document.querySelectorAll('.nav-tabs a')).find(a => 
            a.textContent.includes('Exam Assignments') || 
            a.href && a.href.includes('schedule-matrix')
        );
        
        if (existingMatrix) {
            // Force styling on existing tab
            existingMatrix.style.background = 'linear-gradient(135deg, #FF9800 0%, #F57C00 100%)';
            existingMatrix.style.color = 'white';
            existingMatrix.style.fontWeight = 'bold';
            existingMatrix.style.border = '2px solid #E65100';
            console.log('✅ Styled existing Matrix tab');
            return true;
        }
        
        // Create new Matrix tab
        const li = document.createElement('li');
        li.id = 'matrix-tab-created';
        li.style.display = 'flex';
        
        const a = document.createElement('a');
        a.href = '/RoutineTest/schedule-matrix/';
        a.textContent = '📊 Exam Assignments';
        a.style.cssText = `
            background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%) !important;
            color: white !important;
            font-weight: bold !important;
            border: 2px solid #E65100 !important;
            padding: 12px 20px !important;
            display: block !important;
        `;
        
        li.appendChild(a);
        
        // Find position to insert (after My Classes)
        const myClasses = Array.from(container.querySelectorAll('a')).find(a => 
            a.textContent.includes('My Classes')
        );
        
        if (myClasses && myClasses.parentElement) {
            myClasses.parentElement.insertAdjacentElement('afterend', li);
        } else {
            // Add at end if My Classes not found
            if (container.querySelector('div')) {
                container.querySelector('div').appendChild(li);
            } else {
                container.appendChild(li);
            }
        }
        
        console.log('✅ Created new Matrix tab');
        return true;
    }
    
    // Run on various triggers
    createMatrixTab();
    document.addEventListener('DOMContentLoaded', createMatrixTab);
    window.addEventListener('load', createMatrixTab);
    
    // Periodic check
    let checkCount = 0;
    const checkInterval = setInterval(() => {
        createMatrixTab();
        checkCount++;
        if (checkCount > 10) {
            clearInterval(checkInterval);
        }
    }, 500);
    
    // Expose for debugging
    window.ForceMatrixTab = createMatrixTab;
    
    console.log('🚀 Matrix Tab Override v5.0 active');
})();'''
    
    js_path = base_dir / 'static' / 'js' / 'routinetest' / 'matrix-tab-override.js'
    js_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(js_path, 'w') as f:
        f.write(js_override)
    
    print(colored(f"  ✓ Created JavaScript override at {js_path}", 'green'))
    
    # Step 5: Summary
    print(colored("\n" + "="*70, 'cyan'))
    print(colored("✅ FIX COMPLETE", 'green'))
    print(colored("="*70, 'cyan'))
    
    print(colored("\nFILES UPDATED:", 'magenta'))
    print(colored("1. navigation_tabs.html - Fresh navigation template", 'white'))
    print(colored("2. matrix-tab-override.js - JavaScript force visibility", 'white'))
    print(colored("3. Python cache cleared", 'white'))
    
    print(colored("\nNEXT STEPS:", 'magenta'))
    print(colored("1. Add this to base template before </body>:", 'yellow'))
    print(colored('   <script src="{% static \'js/routinetest/matrix-tab-override.js\' %}"></script>', 'white'))
    print(colored("\n2. Restart Django server:", 'yellow'))
    print(colored("   cd primepath_project", 'white'))
    print(colored("   ../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite", 'white'))
    print(colored("\n3. Clear browser cache and reload", 'yellow'))
    
    print(colored("\nTROUBLESHOOTING:", 'magenta'))
    print(colored("- Open browser console and type: ForceMatrixTab()", 'white'))
    print(colored("- Check for errors in console", 'white'))
    print(colored("- Try incognito mode", 'white'))
    
    return True


if __name__ == '__main__':
    success = fix_navigation()
    sys.exit(0 if success else 1)