#!/usr/bin/env python
"""
Comprehensive URL Update Script
Updates all JavaScript and template files to use new URL structure
/PlacementTest/ and /RoutineTest/
"""
import os
import re
import json
from pathlib import Path

# Console logging colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_update(file_path, pattern, replacement, context=""):
    """Log each update with context"""
    print(f"{Colors.GREEN}[UPDATE]{Colors.ENDC} {file_path}")
    print(f"  {Colors.YELLOW}Pattern:{Colors.ENDC} {pattern[:50]}...")
    print(f"  {Colors.BLUE}Replace:{Colors.ENDC} {replacement[:50]}...")
    if context:
        print(f"  {Colors.HEADER}Context:{Colors.ENDC} {context}")

def update_file(filepath, updates_made):
    """Update URLs in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Define comprehensive replacement patterns
        replacements = [
            # API endpoints - Placement Test
            (r'/api/PlacementTest/', '/api/PlacementTest/', 'API endpoint'),
            (r'/api/v2/PlacementTest/', '/api/v2/PlacementTest/', 'API v2 endpoint'),
            (r"'api/PlacementTest/", "'api/PlacementTest/", 'API string literal'),
            (r'"api/PlacementTest/', '"api/PlacementTest/', 'API string literal'),
            
            # API endpoints - Routine Test
            (r'/api/RoutineTest/', '/api/RoutineTest/', 'API endpoint'),
            (r"'api/RoutineTest/", "'api/RoutineTest/", 'API string literal'),
            (r'"api/RoutineTest/', '"api/RoutineTest/', 'API string literal'),
            
            # URL paths - Placement Test
            (r'/PlacementTest/', '/PlacementTest/', 'URL path'),
            (r"'PlacementTest/", "'PlacementTest/", 'URL string literal'),
            (r'"PlacementTest/', '"PlacementTest/', 'URL string literal'),
            
            # URL paths - Routine Test
            (r'/RoutineTest/', '/RoutineTest/', 'URL path'),
            (r"'RoutineTest/", "'RoutineTest/", 'URL string literal'),
            (r'"RoutineTest/', '"RoutineTest/', 'URL string literal'),
            
            # Teacher dashboard
            (r'/PlacementTest/PlacementTest/teacher/dashboard/', '/PlacementTest/PlacementTest/PlacementTest/teacher/dashboard/', 'Teacher dashboard'),
            (r'/PlacementTest/teacher/', '/PlacementTest/PlacementTest/teacher/', 'Teacher URLs'),
            
            # Template includes and namespaces (for HTML files)
            (r"'PlacementTest:", "'PlacementTest:", 'Django namespace'),
            (r'"PlacementTest:', '"PlacementTest:', 'Django namespace'),
            (r"'RoutineTest:", "'RoutineTest:", 'Django namespace'),
            (r'"RoutineTest:', '"RoutineTest:', 'Django namespace'),
            
            # JavaScript specific patterns
            (r'fetch\([\'"`]/api/PlacementTest/', 'fetch(\'/api/PlacementTest/', 'Fetch API call'),
            (r'fetch\([\'"`]/api/RoutineTest/', 'fetch(\'/api/RoutineTest/', 'Fetch API call'),
            
            # URL construction in JavaScript
            (r'\$\{.*?\}/api/PlacementTest/', '${...}/api/PlacementTest/', 'Template literal'),
            (r'\$\{.*?\}/api/RoutineTest/', '${...}/api/RoutineTest/', 'Template literal'),
        ]
        
        # Apply replacements and log each change
        for pattern, replacement, context in replacements:
            if re.search(pattern, content):
                log_update(filepath, pattern, replacement, context)
                content = re.sub(pattern, replacement, content)
                updates_made['patterns'].add(pattern)
                updates_made['files'].add(str(filepath))
        
        # Special handling for specific files
        if 'answer-manager.js' in str(filepath):
            # Update default endpoints
            content = re.sub(
                r"this\.saveEndpoint = options\.saveEndpoint \|\| '/api/PlacementTest/save-answer/'",
                "this.saveEndpoint = options.saveEndpoint || '/api/PlacementTest/save-answer/'",
                content
            )
            # Add console logging
            if 'console.log("[URL_UPDATE]' not in content:
                content = content.replace(
                    'class AnswerManager extends BaseModule {',
                    '''class AnswerManager extends BaseModule {
        constructor(options = {}) {
            console.log("[URL_UPDATE] AnswerManager using new URL structure");
            console.log("[URL_UPDATE] PlacementTest API: /api/PlacementTest/");
            super(options);'''
                )
        
        # Write back if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.ENDC} processing {filepath}: {e}")
        return False

def main():
    """Main update function"""
    print(f"""
{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║          COMPREHENSIVE URL UPDATE SCRIPT                    ║
║   Updating to /PlacementTest/ and /RoutineTest/            ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
    """)
    
    project_dir = Path("/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project")
    
    updates_made = {
        'files': set(),
        'patterns': set(),
        'js_files': 0,
        'html_files': 0,
        'py_files': 0
    }
    
    # Update JavaScript files
    print(f"\n{Colors.HEADER}[PHASE 1] Updating JavaScript files...{Colors.ENDC}")
    for filepath in project_dir.rglob("*.js"):
        if 'node_modules' not in str(filepath) and 'backup' not in str(filepath):
            if update_file(filepath, updates_made):
                updates_made['js_files'] += 1
    
    # Update HTML templates
    print(f"\n{Colors.HEADER}[PHASE 2] Updating HTML templates...{Colors.ENDC}")
    for filepath in project_dir.rglob("*.html"):
        if 'backup' not in str(filepath):
            if update_file(filepath, updates_made):
                updates_made['html_files'] += 1
    
    # Update Python files (views, tests)
    print(f"\n{Colors.HEADER}[PHASE 3] Updating Python files...{Colors.ENDC}")
    for filepath in project_dir.rglob("*.py"):
        if 'migrations' not in str(filepath) and 'backup' not in str(filepath):
            if update_file(filepath, updates_made):
                updates_made['py_files'] += 1
    
    # Print summary
    print(f"""
{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║                    UPDATE SUMMARY                           ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
    
{Colors.GREEN}✅ Updates Completed:{Colors.ENDC}
  • JavaScript files: {updates_made['js_files']}
  • HTML templates: {updates_made['html_files']}
  • Python files: {updates_made['py_files']}
  • Total files updated: {len(updates_made['files'])}
  • Unique patterns replaced: {len(updates_made['patterns'])}
    
{Colors.BLUE}📝 URL Structure:{Colors.ENDC}
  • /PlacementTest/ → /PlacementTest/
  • /RoutineTest/ → /RoutineTest/
  • /PlacementTest/teacher/ → /PlacementTest/PlacementTest/teacher/
  • /api/PlacementTest/ → /api/PlacementTest/
  • /api/RoutineTest/ → /api/RoutineTest/
    
{Colors.YELLOW}⚠️  Next Steps:{Colors.ENDC}
  1. Restart Django server
  2. Clear browser cache
  3. Test all functionality
  4. Check console logs for debugging info
    """)
    
    # Write detailed log file
    log_file = project_dir / 'url_update_log.json'
    with open(log_file, 'w') as f:
        json.dump({
            'files_updated': list(updates_made['files']),
            'patterns_replaced': list(updates_made['patterns']),
            'js_files': updates_made['js_files'],
            'html_files': updates_made['html_files'],
            'py_files': updates_made['py_files']
        }, f, indent=2)
    
    print(f"{Colors.GREEN}Log saved to: {log_file}{Colors.ENDC}")

if __name__ == "__main__":
    main()