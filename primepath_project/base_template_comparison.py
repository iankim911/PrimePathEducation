#!/usr/bin/env python
"""
Phase 3, Day 1: Base Template Comparison
Detailed analysis of base.html vs routinetest_base.html
"""

import os
import re
from pathlib import Path
from difflib import unified_diff

def analyze_base_templates():
    """Compare base.html and routinetest_base.html in detail."""
    
    base_path = Path("/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/base.html")
    routine_base_path = Path("/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/routinetest_base.html")
    
    print("=" * 80)
    print("BASE TEMPLATE DETAILED COMPARISON")
    print("=" * 80)
    print()
    
    # Read both templates
    with open(base_path, 'r') as f:
        base_content = f.read()
        base_lines = base_content.splitlines()
    
    with open(routine_base_path, 'r') as f:
        routine_content = f.read()
        routine_lines = routine_content.splitlines()
    
    print(f"base.html: {len(base_lines)} lines")
    print(f"routinetest_base.html: {len(routine_lines)} lines")
    print()
    
    # Extract key components
    components = {
        'base.html': extract_components(base_content),
        'routinetest_base.html': extract_components(routine_content)
    }
    
    # Compare components
    print("1. BLOCK DEFINITIONS")
    print("-" * 40)
    base_blocks = set(components['base.html']['blocks'])
    routine_blocks = set(components['routinetest_base.html']['blocks'])
    
    print(f"Common blocks: {base_blocks & routine_blocks}")
    print(f"Unique to base.html: {base_blocks - routine_blocks}")
    print(f"Unique to routinetest_base.html: {routine_blocks - base_blocks}")
    print()
    
    print("2. CSS FILES")
    print("-" * 40)
    print("base.html CSS:")
    for css in components['base.html']['css_files']:
        print(f"  - {css}")
    print()
    print("routinetest_base.html CSS:")
    for css in components['routinetest_base.html']['css_files']:
        print(f"  - {css}")
    print()
    
    print("3. JAVASCRIPT FILES")
    print("-" * 40)
    print("base.html JS:")
    for js in components['base.html']['js_files']:
        print(f"  - {js}")
    print()
    print("routinetest_base.html JS:")
    for js in components['routinetest_base.html']['js_files']:
        print(f"  - {js}")
    print()
    
    print("4. CUSTOM TEMPLATE TAGS")
    print("-" * 40)
    print(f"base.html tags: {components['base.html']['custom_tags']}")
    print(f"routinetest_base.html tags: {components['routinetest_base.html']['custom_tags']}")
    print()
    
    print("5. META TAGS")
    print("-" * 40)
    print("base.html meta tags:", len(components['base.html']['meta_tags']))
    print("routinetest_base.html meta tags:", len(components['routinetest_base.html']['meta_tags']))
    print()
    
    # Design recommendations
    print("6. UNIFICATION STRATEGY")
    print("-" * 40)
    print("✅ Keep from both:")
    print("  - All block definitions (union of both)")
    print("  - Mobile responsive CSS")
    print("  - Favicon links")
    print("  - Meta viewport tags")
    print()
    print("✅ Consolidate:")
    print("  - CSS loading strategy (merge and deduplicate)")
    print("  - JavaScript loading (unified approach)")
    print("  - Custom tags (load all required)")
    print()
    print("⚠️  Resolve conflicts:")
    print("  - Different font sizes (base: default vs routine: 17px)")
    print("  - Different navigation systems")
    print("  - Debug console logging approaches")
    
    return components

def extract_components(content):
    """Extract key components from a template."""
    
    components = {
        'blocks': [],
        'css_files': [],
        'js_files': [],
        'custom_tags': [],
        'meta_tags': [],
        'inline_styles': [],
        'inline_scripts': []
    }
    
    # Extract blocks
    block_pattern = r'{%\s*block\s+(\w+)\s*%}'
    components['blocks'] = re.findall(block_pattern, content)
    
    # Extract CSS files
    css_pattern = r'<link[^>]*href="([^"]*\.css[^"]*)"[^>]*>'
    components['css_files'] = re.findall(css_pattern, content)
    
    # Extract JS files
    js_pattern = r'<script[^>]*src="([^"]*\.js[^"]*)"[^>]*>'
    components['js_files'] = re.findall(js_pattern, content)
    
    # Extract custom tags
    tag_pattern = r'{%\s*load\s+(\w+)\s*%}'
    components['custom_tags'] = re.findall(tag_pattern, content)
    
    # Extract meta tags
    meta_pattern = r'<meta[^>]*>'
    components['meta_tags'] = re.findall(meta_pattern, content)
    
    # Check for inline styles
    if '<style>' in content:
        components['inline_styles'].append('Has inline styles')
    
    # Check for inline scripts
    if '<script>' in content and 'src=' not in content:
        inline_script_blocks = content.count('<script>') + content.count('<script ')
        components['inline_scripts'].append(f'{inline_script_blocks} inline script blocks')
    
    return components

def create_unified_base_design():
    """Create design for unified_base.html."""
    
    print()
    print("=" * 80)
    print("UNIFIED BASE TEMPLATE DESIGN")
    print("=" * 80)
    print()
    
    design = """
# unified_base.html Design Specification

## Structure:
```django
{% load static %}
{% load navigation_tags %}  {# Support for routinetest navigation #}
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Meta Tags (from both templates) -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PrimePath Assessment Platform{% endblock %}</title>
    
    <!-- Favicon (unified) -->
    <link rel="icon" type="image/x-icon" href="{% static 'favicon.ico' %}">
    <link rel="icon" type="image/svg+xml" href="{% static 'favicon.svg' %}">
    
    <!-- Core CSS (consolidated) -->
    <link rel="stylesheet" href="{% static 'css/unified-base.css' %}">
    <link rel="stylesheet" href="{% static 'css/mobile-responsive.css' %}">
    
    <!-- Module-specific CSS -->
    {% block module_css %}
        {# Placement test or routine test specific styles #}
    {% endblock %}
    
    <!-- Extra CSS -->
    {% block extra_css %}{% endblock %}
    
    <!-- JavaScript Configuration -->
    <script>
        window.PRIMEPATH_CONFIG = {
            module: '{% block module_name %}core{% endblock %}',
            debug: {% if debug %}true{% else %}false{% endif %},
            csrfToken: '{{ csrf_token }}'
        };
    </script>
</head>
<body class="{% block body_class %}{% endblock %}">
    <!-- Header (supports both styles) -->
    {% block header_wrapper %}
    <header class="header {% block header_class %}{% endblock %}">
        {% block header %}
            <h1>{% block header_title %}PrimePath{% endblock %}</h1>
        {% endblock %}
    </header>
    {% endblock %}
    
    <!-- Navigation (flexible) -->
    {% block navigation %}
        {# Can be tabs (routinetest) or menu (placement) #}
    {% endblock %}
    
    <!-- Main Content -->
    <main class="main-content">
        {% block content_wrapper %}
            <div class="container">
                {% block content %}{% endblock %}
            </div>
        {% endblock %}
    </main>
    
    <!-- Footer -->
    {% block footer %}{% endblock %}
    
    <!-- Core JavaScript -->
    <script src="{% static 'js/unified-core.js' %}"></script>
    
    <!-- Module-specific JavaScript -->
    {% block module_js %}{% endblock %}
    
    <!-- Extra JavaScript -->
    {% block extra_js %}{% endblock %}
</body>
</html>
```

## Key Features:
1. **Flexible block structure** - Supports both template systems
2. **Unified CSS approach** - Single core CSS file
3. **Module-aware** - Can adapt to placement/routine context
4. **Backward compatible** - All existing blocks preserved
5. **Clean JavaScript** - Centralized configuration
"""
    print(design)
    
    return design

if __name__ == '__main__':
    # Run analysis
    components = analyze_base_templates()
    
    # Create design
    design = create_unified_base_design()
    
    print()
    print("✅ Analysis complete. Ready to create unified_base.html")