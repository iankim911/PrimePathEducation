#!/usr/bin/env python
"""
Phase 3: Template Conflict Analysis
Date: August 26, 2025

Comprehensive analysis of template conflicts between placement_test and primepath_routinetest
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_templates():
    """Analyze all templates and identify conflicts."""
    
    project_root = Path("/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project")
    templates_dir = project_root / "templates"
    
    # Initialize tracking structures
    template_map = defaultdict(list)
    extends_map = defaultdict(list)
    include_map = defaultdict(list)
    static_refs = defaultdict(list)
    
    # Scan all templates
    for template_path in templates_dir.rglob("*.html"):
        relative_path = template_path.relative_to(templates_dir)
        template_name = template_path.name
        
        # Track duplicate names
        template_map[template_name].append(str(relative_path))
        
        # Analyze template content
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find extends tags
                extends_matches = re.findall(r'{%\s*extends\s+["\']([^"\']+)["\']', content)
                for base in extends_matches:
                    extends_map[base].append(str(relative_path))
                
                # Find include tags
                include_matches = re.findall(r'{%\s*include\s+["\']([^"\']+)["\']', content)
                for inc in include_matches:
                    include_map[inc].append(str(relative_path))
                
                # Find static references
                static_matches = re.findall(r'{%\s*static\s+["\']([^"\']+)["\']', content)
                for static in static_matches:
                    static_refs[static].append(str(relative_path))
                    
        except Exception as e:
            print(f"Error reading {template_path}: {e}")
    
    return template_map, extends_map, include_map, static_refs

def print_analysis(template_map, extends_map, include_map, static_refs):
    """Print detailed analysis results."""
    
    print("=" * 80)
    print("PHASE 3: TEMPLATE CONFLICT ANALYSIS")
    print("=" * 80)
    print()
    
    # Find conflicts
    conflicts = {name: paths for name, paths in template_map.items() if len(paths) > 1}
    
    print("1. TEMPLATE NAME CONFLICTS")
    print("-" * 40)
    if conflicts:
        for name, paths in sorted(conflicts.items()):
            print(f"\n  ❌ {name} ({len(paths)} instances):")
            for path in paths:
                print(f"     - {path}")
    else:
        print("  ✅ No template name conflicts found")
    
    print("\n2. BASE TEMPLATE USAGE")
    print("-" * 40)
    base_templates = sorted(extends_map.keys())
    for base in base_templates[:10]:  # Show top 10
        count = len(extends_map[base])
        print(f"  {base}: {count} templates")
    
    print("\n3. MOST INCLUDED TEMPLATES")
    print("-" * 40)
    included = sorted(include_map.items(), key=lambda x: len(x[1]), reverse=True)
    for inc, templates in included[:10]:
        print(f"  {inc}: {len(templates)} references")
    
    print("\n4. STATIC ASSET REFERENCES")
    print("-" * 40)
    # Group by type
    css_refs = {k: v for k, v in static_refs.items() if k.endswith('.css')}
    js_refs = {k: v for k, v in static_refs.items() if k.endswith('.js')}
    
    print(f"  CSS files referenced: {len(css_refs)}")
    print(f"  JS files referenced: {len(js_refs)}")
    
    # Find duplicate references
    print("\n5. DUPLICATE STATIC REFERENCES")
    print("-" * 40)
    for static, templates in sorted(static_refs.items()):
        if len(templates) > 5:  # Referenced in many places
            print(f"  {static}: {len(templates)} templates")
    
    print("\n6. STATISTICS SUMMARY")
    print("-" * 40)
    print(f"  Total templates: {len(template_map)}")
    print(f"  Conflicting names: {len(conflicts)}")
    print(f"  Base templates used: {len(extends_map)}")
    print(f"  Included templates: {len(include_map)}")
    print(f"  Static files referenced: {len(static_refs)}")
    
    # Detailed conflict analysis
    print("\n7. CONFLICT SEVERITY ANALYSIS")
    print("-" * 40)
    
    critical_conflicts = []
    medium_conflicts = []
    low_conflicts = []
    
    for name, paths in conflicts.items():
        # Check if they're in different apps
        apps = set()
        for path in paths:
            if 'placement_test' in path:
                apps.add('placement_test')
            elif 'primepath_routinetest' in path:
                apps.add('primepath_routinetest')
            else:
                apps.add('core')
        
        if len(apps) > 1:
            if name in ['index.html', 'exam_list.html', 'edit_exam.html', 'student_test_v2.html']:
                critical_conflicts.append((name, paths))
            else:
                medium_conflicts.append((name, paths))
        else:
            low_conflicts.append((name, paths))
    
    if critical_conflicts:
        print("\n  🔴 CRITICAL CONFLICTS (Different apps, core functionality):")
        for name, paths in critical_conflicts:
            print(f"     {name}: {paths}")
    
    if medium_conflicts:
        print("\n  🟡 MEDIUM CONFLICTS (Different apps, non-critical):")
        for name, paths in medium_conflicts:
            print(f"     {name}: {paths}")
    
    if low_conflicts:
        print("\n  🟢 LOW CONFLICTS (Same app):")
        for name, paths in low_conflicts:
            print(f"     {name}: {paths}")
    
    return conflicts

def analyze_base_templates():
    """Detailed comparison of base.html vs routinetest_base.html"""
    
    print("\n" + "=" * 80)
    print("BASE TEMPLATE ARCHITECTURE ANALYSIS")
    print("=" * 80)
    
    base_path = Path("/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/base.html")
    routine_base_path = Path("/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/routinetest_base.html")
    
    # Compare features
    features = {
        'base.html': {
            'CSS files': [],
            'JS files': [],
            'Custom tags': [],
            'Block definitions': []
        },
        'routinetest_base.html': {
            'CSS files': [],
            'JS files': [],
            'Custom tags': [],
            'Block definitions': []
        }
    }
    
    for name, path in [('base.html', base_path), ('routinetest_base.html', routine_base_path)]:
        if path.exists():
            with open(path, 'r') as f:
                content = f.read()
                
                # Find CSS
                css_matches = re.findall(r'href="[^"]*\.css[^"]*"', content)
                features[name]['CSS files'] = css_matches
                
                # Find JS
                js_matches = re.findall(r'src="[^"]*\.js[^"]*"', content)
                features[name]['JS files'] = js_matches
                
                # Find blocks
                block_matches = re.findall(r'{%\s*block\s+(\w+)', content)
                features[name]['Block definitions'] = block_matches
                
                # Find custom tags
                tag_matches = re.findall(r'{%\s*load\s+(\w+)', content)
                features[name]['Custom tags'] = tag_matches
    
    print("\n1. BASE.HTML FEATURES:")
    print("-" * 40)
    for key, value in features['base.html'].items():
        print(f"  {key}: {len(value)}")
        if value and len(value) <= 5:
            for item in value:
                print(f"    - {item}")
    
    print("\n2. ROUTINETEST_BASE.HTML FEATURES:")
    print("-" * 40)
    for key, value in features['routinetest_base.html'].items():
        print(f"  {key}: {len(value)}")
        if value and len(value) <= 5:
            for item in value:
                print(f"    - {item}")
    
    print("\n3. KEY DIFFERENCES:")
    print("-" * 40)
    
    # CSS differences
    base_css = set(features['base.html']['CSS files'])
    routine_css = set(features['routinetest_base.html']['CSS files'])
    
    print(f"  Unique to base.html CSS: {len(base_css - routine_css)}")
    print(f"  Unique to routinetest_base.html CSS: {len(routine_css - base_css)}")
    
    # Block differences
    base_blocks = set(features['base.html']['Block definitions'])
    routine_blocks = set(features['routinetest_base.html']['Block definitions'])
    
    print(f"  Unique to base.html blocks: {base_blocks - routine_blocks}")
    print(f"  Unique to routinetest_base.html blocks: {routine_blocks - base_blocks}")
    
    return features

if __name__ == '__main__':
    print("Starting Phase 3 Template Analysis...")
    print()
    
    # Run analysis
    template_map, extends_map, include_map, static_refs = analyze_templates()
    conflicts = print_analysis(template_map, extends_map, include_map, static_refs)
    base_features = analyze_base_templates()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\n✅ Found {len(conflicts)} template name conflicts requiring resolution")
    print("✅ Identified base template architecture differences")
    print("✅ Mapped all template dependencies and relationships")
    print("\nReady for Phase 3 detailed planning.")