#!/usr/bin/env python3
"""
Test script to verify curriculum data is available in template context
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.template import Context, Template
from primepath_routinetest.services.exam_service import ExamService

def test_curriculum_data_in_template():
    """Test that curriculum data works in template context"""
    print("=== TESTING CURRICULUM DATA IN TEMPLATE CONTEXT ===")
    print()
    
    # Get curriculum data like the view does
    curriculum_data_for_copy_modal = ExamService.get_routinetest_curriculum_levels()
    
    print(f"✅ Loaded {len(curriculum_data_for_copy_modal)} curriculum levels")
    print(f"   Sample: {curriculum_data_for_copy_modal[0]['program_name']} {curriculum_data_for_copy_modal[0]['subprogram_name']} Level {curriculum_data_for_copy_modal[0]['level_number']}")
    
    # Create a mini template to test the Django template syntax
    template_content = """
// Initialize curriculum data from Django context
{% if curriculum_levels_for_copy %}
window.CopyCurriculumData = {};
{% for level_data in curriculum_levels_for_copy %}
    {% with program=level_data.program_name subprogram=level_data.subprogram_name level=level_data.level_number %}
        if (!window.CopyCurriculumData['{{ program }}']) {
            window.CopyCurriculumData['{{ program }}'] = { subprograms: {} };
        }
        if (!window.CopyCurriculumData['{{ program }}']['subprograms']['{{ subprogram }}']) {
            window.CopyCurriculumData['{{ program }}']['subprograms']['{{ subprogram }}'] = { levels: [] };
        }
        window.CopyCurriculumData['{{ program }}']['subprograms']['{{ subprogram }}']['levels'].push({
            id: {{ level_data.curriculum_level.id }},
            number: {{ level }}
        });
    {% endwith %}
{% endfor %}
console.log('[COPY_CURRICULUM] Loaded curriculum data:', Object.keys(window.CopyCurriculumData));
{% else %}
console.error('[COPY_CURRICULUM] No curriculum data available');
{% endif %}
"""

    template = Template(template_content)
    context = Context({
        'curriculum_levels_for_copy': curriculum_data_for_copy_modal
    })
    
    rendered = template.render(context)
    print()
    print("✅ Template rendered successfully!")
    
    # Check the rendered JavaScript
    if 'window.CopyCurriculumData = {};' in rendered:
        print("✅ CopyCurriculumData object initialized")
    else:
        print("❌ CopyCurriculumData object NOT initialized")
        
    # Count program initializations
    core_count = rendered.count("'CORE'")
    ascent_count = rendered.count("'ASCENT'") 
    edge_count = rendered.count("'EDGE'")
    pinnacle_count = rendered.count("'PINNACLE'")
    
    print(f"✅ CORE program references: {core_count}")
    print(f"✅ ASCENT program references: {ascent_count}")
    print(f"✅ EDGE program references: {edge_count}")
    print(f"✅ PINNACLE program references: {pinnacle_count}")
    
    # Show a snippet of the rendered output
    print()
    print("📋 Sample of rendered JavaScript:")
    lines = rendered.strip().split('\n')
    for i, line in enumerate(lines[:10]):  # Show first 10 lines
        if line.strip():
            print(f"   {i+1}. {line.strip()}")
    
    print()
    print("=== FINAL VERDICT ===")
    if core_count > 0 and ascent_count > 0 and edge_count > 0 and pinnacle_count > 0:
        print("✅ ALL PROGRAMS DETECTED - Fix is working correctly!")
        print("✅ The Program dropdown should now load with all curriculum options")
        return True
    else:
        print("❌ SOME PROGRAMS MISSING - Fix needs debugging")
        return False

if __name__ == '__main__':
    success = test_curriculum_data_in_template()
    sys.exit(0 if success else 1)