#!/usr/bin/env python
"""
Ultra-deep analysis of PDF size difference between PlacementTest and RoutineTest.
Compares the implementations to identify why RoutineTest PDF appears too large.
"""
import os
import re
from pathlib import Path

def analyze_css_properties(file_path, module_name):
    """Extract and analyze CSS properties related to PDF sizing."""
    print(f"\n{'='*80}")
    print(f"📊 {module_name} CSS Analysis")
    print("="*80)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Key CSS patterns to find
    patterns = {
        'pdf-section height': r'\.pdf-section\s*{[^}]*height:\s*([^;]+);',
        'pdf-section max-height': r'\.pdf-section\s*{[^}]*max-height:\s*([^;]+);',
        'pdf-viewer height': r'\.pdf-viewer\s*{[^}]*height:\s*([^;]+);',
        'pdf-viewer max-height': r'\.pdf-viewer\s*{[^}]*max-height:\s*([^;]+);',
        'main-content height': r'\.main-content\s*{[^}]*height:\s*([^;]+);',
        'pdf-image-display': r'pdf-image-display[^{]*{[^}]*}',
    }
    
    # Multi-line CSS block extraction
    pdf_section_blocks = re.findall(r'\.pdf-section\s*{([^}]+)}', content, re.MULTILINE | re.DOTALL)
    pdf_viewer_blocks = re.findall(r'\.pdf-viewer\s*{([^}]+)}', content, re.MULTILINE | re.DOTALL)
    main_content_blocks = re.findall(r'\.main-content\s*{([^}]+)}', content, re.MULTILINE | re.DOTALL)
    
    print("\n📐 PDF Section CSS:")
    for block in pdf_section_blocks[:2]:  # Show first 2 matches
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        for line in lines:
            if any(prop in line for prop in ['height', 'max-height', 'min-height', 'flex']):
                print(f"   {line}")
    
    print("\n📐 PDF Viewer CSS:")
    for block in pdf_viewer_blocks[:2]:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        for line in lines:
            if any(prop in line for prop in ['height', 'max-height', 'min-height', 'flex', 'overflow']):
                print(f"   {line}")
    
    print("\n📐 Main Content CSS:")
    for block in main_content_blocks[:2]:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        for line in lines:
            if any(prop in line for prop in ['height', 'max-height', 'display', 'grid']):
                print(f"   {line}")
    
    # Check for media queries
    media_queries = re.findall(r'@media[^{]+{[^}]*\.pdf-section[^}]+}', content, re.MULTILINE | re.DOTALL)
    if media_queries:
        print("\n📱 Media Queries for PDF Section:")
        for query in media_queries[:2]:
            lines = query.split('\n')
            for line in lines:
                if '@media' in line or 'max-height' in line or 'height' in line:
                    print(f"   {line.strip()}")
    
    return content

def analyze_js_scaling(file_path, module_name):
    """Analyze JavaScript PDF scaling parameters."""
    print(f"\n{'='*80}")
    print(f"🔍 {module_name} JavaScript Scaling Analysis")
    print("="*80)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find scale values
    scale_matches = re.findall(r'scale:\s*([0-9.]+)', content)
    viewport_matches = re.findall(r'getViewport\({[^}]*scale:\s*([0-9.]+)', content)
    zoom_init = re.findall(r'currentZoomLevel\s*=\s*([0-9.]+)', content)
    
    print("\n🔢 Scale Values Found:")
    if scale_matches:
        unique_scales = list(set(scale_matches))
        for scale in unique_scales:
            count = scale_matches.count(scale)
            print(f"   scale: {scale} (used {count} times)")
    
    print("\n🔢 Viewport Scale Values:")
    if viewport_matches:
        unique_viewport = list(set(viewport_matches))
        for scale in unique_viewport:
            print(f"   viewport scale: {scale}")
    
    print("\n🔢 Initial Zoom Level:")
    if zoom_init:
        print(f"   currentZoomLevel = {zoom_init[0]}")
    
    # Check for transform scale in applyZoomToImage
    apply_zoom_func = re.search(r'function applyZoomToImage\(\)[^{]*{([^}]+)}', content, re.MULTILINE | re.DOTALL)
    if apply_zoom_func:
        print("\n🔍 applyZoomToImage Function:")
        lines = apply_zoom_func.group(1).split('\n')
        for line in lines:
            if 'transform' in line or 'scale' in line:
                print(f"   {line.strip()}")
    
    # Check renderPageAsImage scale
    render_func = re.search(r'function renderPageAsImage\([^)]*\)[^{]*{[^}]*viewport[^}]+}', content, re.MULTILINE | re.DOTALL)
    if render_func:
        viewport_line = re.search(r'viewport.*getViewport.*scale:\s*([0-9.]+)', render_func.group(0))
        if viewport_line:
            print(f"\n🎨 renderPageAsImage viewport scale: {viewport_line.group(1)}")
    
    return content

def analyze_inline_styles(file_path, module_name):
    """Analyze inline styles on PDF elements."""
    print(f"\n{'='*80}")
    print(f"🎨 {module_name} Inline Styles Analysis")
    print("="*80)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find pdf-image-display div
    image_display = re.search(r'<div id="pdf-image-display"[^>]*style="([^"]+)"', content)
    if image_display:
        print("\n📦 pdf-image-display inline style:")
        styles = image_display.group(1).split(';')
        for style in styles:
            if style.strip():
                print(f"   {style.strip()}")
    
    # Find pdf-page-image img
    page_image = re.search(r'<img id="pdf-page-image"[^>]*style="([^"]+)"', content)
    if page_image:
        print("\n🖼️ pdf-page-image inline style:")
        styles = page_image.group(1).split(';')
        for style in styles:
            if style.strip():
                print(f"   {style.strip()}")
    
    # Find pdf-viewer div
    pdf_viewer = re.search(r'<div[^>]*class="pdf-viewer"[^>]*id="pdf-viewer"[^>]*>', content)
    if pdf_viewer:
        print("\n📋 pdf-viewer element found")
        # Check if it has inline styles
        if 'style=' in pdf_viewer.group(0):
            style_match = re.search(r'style="([^"]+)"', pdf_viewer.group(0))
            if style_match:
                print("   Inline styles:")
                styles = style_match.group(1).split(';')
                for style in styles:
                    if style.strip():
                        print(f"     {style.strip()}")
    
    return content

def compare_implementations():
    """Compare PlacementTest and RoutineTest implementations."""
    base_path = Path("/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates")
    
    placement_file = base_path / "placement_test/preview_and_answers.html"
    routine_file = base_path / "primepath_routinetest/preview_and_answers.html"
    
    print("\n" + "🔬"*40)
    print("🔬 ULTRA-DEEP PDF SIZE ANALYSIS")
    print("🔬"*40)
    
    # Analyze CSS
    placement_css = analyze_css_properties(placement_file, "PlacementTest")
    routine_css = analyze_css_properties(routine_file, "RoutineTest")
    
    # Analyze JavaScript scaling
    placement_js = analyze_js_scaling(placement_file, "PlacementTest")
    routine_js = analyze_js_scaling(routine_file, "RoutineTest")
    
    # Analyze inline styles
    placement_inline = analyze_inline_styles(placement_file, "PlacementTest")
    routine_inline = analyze_inline_styles(routine_file, "RoutineTest")
    
    # Compare key differences
    print("\n" + "="*80)
    print("🔄 KEY DIFFERENCES IDENTIFIED")
    print("="*80)
    
    # Check for differences in max-height values
    placement_max_heights = re.findall(r'\.pdf-section[^}]*max-height:\s*([^;]+);', placement_css)
    routine_max_heights = re.findall(r'\.pdf-section[^}]*max-height:\s*([^;]+);', routine_css)
    
    print("\n📏 PDF Section Max Heights:")
    print(f"   PlacementTest: {set(placement_max_heights) if placement_max_heights else 'None found'}")
    print(f"   RoutineTest: {set(routine_max_heights) if routine_max_heights else 'None found'}")
    
    # Check for scale differences
    placement_scales = re.findall(r'scale:\s*([0-9.]+)', placement_js)
    routine_scales = re.findall(r'scale:\s*([0-9.]+)', routine_js)
    
    print("\n🔍 JavaScript Scale Values:")
    print(f"   PlacementTest unique scales: {set(placement_scales)}")
    print(f"   RoutineTest unique scales: {set(routine_scales)}")
    
    # Check for transform differences in applyZoomToImage
    placement_transform = re.search(r'pageImage\.style\.transform\s*=\s*[^;]+', placement_js)
    routine_transform = re.search(r'pageImage\.style\.transform\s*=\s*[^;]+', routine_js)
    
    print("\n🎯 Transform Application:")
    if placement_transform:
        print(f"   PlacementTest: {placement_transform.group(0)}")
    if routine_transform:
        print(f"   RoutineTest: {routine_transform.group(0)}")
    
    # Check container structure differences
    placement_containers = re.findall(r'<div[^>]*(?:pdf-section|pdf-viewer|main-content)[^>]*>', placement_css)
    routine_containers = re.findall(r'<div[^>]*(?:pdf-section|pdf-viewer|main-content)[^>]*>', routine_css)
    
    print("\n📦 Container Structure:")
    print(f"   PlacementTest containers: {len(placement_containers)}")
    print(f"   RoutineTest containers: {len(routine_containers)}")
    
    # Final recommendation
    print("\n" + "="*80)
    print("💡 RECOMMENDED FIX")
    print("="*80)
    
    print("""
The analysis shows both modules use the same scale (2.5), but the issue is likely:

1. **Container Constraints**: Check if .pdf-section or .pdf-viewer has proper max-height
2. **Image Scaling**: The PDF might be rendered at natural size without container limits
3. **Zoom Level**: Initial zoom might be different or not properly constrained

SOLUTION:
1. Add explicit max-width constraint to the image container
2. Ensure pdf-section has max-height: 85vh (desktop) / 75vh (mobile)
3. Add max-width to pdf-page-image to prevent overflow
4. Consider reducing initial render scale from 2.5 to 1.5 or 2.0
""")

if __name__ == "__main__":
    compare_implementations()