#!/usr/bin/env python
"""
Phase 3: Test Template Syntax Only
Date: August 26, 2025
Purpose: Validate all migrated templates have correct unified_base.html syntax
"""

import os
import sys
from pathlib import Path

def check_template_syntax(template_path):
    """Check if a template has been properly migrated to unified_base.html"""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'extends_unified': '{% extends "unified_base.html" %}' in content,
        'has_module_block': '{% block module_name %}' in content,
        'has_migration_comment': 'Migrated to unified_base.html' in content,
        'no_old_base': 'extends "base.html"' not in content and 'extends "routinetest_base.html"' not in content,
    }
    
    module = None
    if 'placement_test{% endblock %}' in content:
        module = 'placement_test'
    elif 'primepath_routinetest{% endblock %}' in content:
        module = 'primepath_routinetest'
    elif 'core{% endblock %}' in content:
        module = 'core'
    
    return checks, module

def main():
    """Check all templates for proper migration syntax"""
    template_dir = Path('templates')
    
    # Find all HTML templates
    templates = list(template_dir.glob('**/*.html'))
    
    # Filter to only migrated templates
    migrated = []
    for template in templates:
        rel_path = template.relative_to(template_dir)
        
        # Skip base templates and adapters
        if rel_path.name in ['base.html', 'routinetest_base.html', 'unified_base.html', 
                             'base_adapter.html', 'routinetest_base_adapter.html']:
            continue
            
        # Check if it extends unified_base
        with open(template, 'r', encoding='utf-8') as f:
            if 'extends "unified_base.html"' in f.read():
                migrated.append(template)
    
    print("=" * 80)
    print("TEMPLATE MIGRATION SYNTAX CHECK")
    print("=" * 80)
    print(f"Found {len(migrated)} migrated templates\n")
    
    all_good = True
    modules = {'placement_test': 0, 'primepath_routinetest': 0, 'core': 0, 'other': 0}
    
    for template in sorted(migrated):
        rel_path = template.relative_to(template_dir)
        checks, module = check_template_syntax(template)
        
        if module:
            modules[module] += 1
        else:
            modules['other'] += 1
        
        if all(checks.values()):
            status = "✅"
        else:
            status = "❌"
            all_good = False
            
        issues = []
        if not checks['extends_unified']:
            issues.append("no extends unified_base")
        if not checks['has_module_block']:
            issues.append("no module_name block")
        if not checks['has_migration_comment']:
            issues.append("no migration comment")
        if not checks['no_old_base']:
            issues.append("still has old base reference")
            
        if issues:
            print(f"{status} {rel_path}: {', '.join(issues)}")
        else:
            print(f"{status} {rel_path}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total migrated: {len(migrated)}")
    print(f"Module distribution:")
    for module, count in modules.items():
        if count > 0:
            print(f"  {module}: {count}")
    
    if all_good:
        print("\n🎉 ALL TEMPLATES HAVE CORRECT MIGRATION SYNTAX!")
    else:
        print("\n⚠️  Some templates have syntax issues")
    
    return all_good

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)