#!/usr/bin/env python
"""
Test what's actually being output in the template
"""
import os
import sys
import django

# Setup Django
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.template import Template, Context
from primepath_routinetest.services.exam_service import ExamService

print("🔍 TESTING TEMPLATE CURRICULUM DATA OUTPUT")
print("=" * 60)

try:
    # Get curriculum data like the view does
    curriculum_hierarchy_for_copy = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
    curriculum_levels_for_copy = ExamService.get_routinetest_curriculum_levels()
    
    print(f"✅ Backend data generated successfully:")
    print(f"   - curriculum_hierarchy_for_copy: {type(curriculum_hierarchy_for_copy)}")
    print(f"   - Has curriculum_data: {'curriculum_data' in curriculum_hierarchy_for_copy}")
    if 'curriculum_data' in curriculum_hierarchy_for_copy:
        programs = list(curriculum_hierarchy_for_copy['curriculum_data'].keys())
        print(f"   - Programs: {programs}")
    
    # Create minimal template to test the curriculum data rendering
    test_template = """
<script>
console.group('%c🔍 COPY MODAL CURRICULUM DEBUG - TEMPLATE ANALYSIS', 'color: #ff6b35; font-size: 16px; font-weight: bold;');
console.log('%c[TEMPLATE_DEBUG] Template rendering started at:', 'color: #0066cc;', new Date().toISOString());
console.log('%c[TEMPLATE_DEBUG] Django template context evaluation:', 'color: #0066cc;');
console.log('  - curriculum_hierarchy_for_copy available: {{ curriculum_hierarchy_for_copy|yesno:"YES,NO" }}');
console.log('  - curriculum_levels_for_copy available: {{ curriculum_levels_for_copy|yesno:"YES,NO" }}');

{% if curriculum_hierarchy_for_copy %}
// Use ENHANCED structured hierarchy data from Django backend
console.log('%c[COPY_CURRICULUM_FIX] ✅ curriculum_hierarchy_for_copy IS AVAILABLE from Django backend', 'color: #00aa00; font-weight: bold;');
{{ curriculum_hierarchy_for_copy|json_script:"copy-curriculum-hierarchy-data" }}
const curriculumScriptElement = document.getElementById('copy-curriculum-hierarchy-data');
if (curriculumScriptElement) {
    console.log('[CURRICULUM] JSON script element found');
    const enhancedData = JSON.parse(curriculumScriptElement.textContent);
    console.log('[CURRICULUM] Enhanced data loaded:', !!enhancedData);
    if (enhancedData.curriculum_data) {
        console.log('[CURRICULUM] Programs in curriculum_data:', Object.keys(enhancedData.curriculum_data));
        window.CopyCurriculumData = enhancedData.curriculum_data;
        window.CopyCurriculumDataReady = true;
    }
}
{% elif curriculum_levels_for_copy %}
console.log('%c[TEMPLATE_DEBUG] ⚠️ Using FALLBACK curriculum_levels_for_copy', 'color: #ff9900; font-weight: bold;');
{% else %}
console.error('%c[TEMPLATE_DEBUG] ❌❌❌ NO CURRICULUM DATA AVAILABLE FROM DJANGO CONTEXT!', 'color: #ff0000; font-size: 18px; font-weight: bold;');
{% endif %}

console.log('[TEMPLATE_DEBUG] Final state check...');
console.log('  - window.CopyCurriculumData available:', !!window.CopyCurriculumData);
if (window.CopyCurriculumData) {
    console.log('  - Programs loaded:', Object.keys(window.CopyCurriculumData));
}
console.groupEnd();
</script>
"""
    
    # Render template with context
    context = Context({
        'curriculum_hierarchy_for_copy': curriculum_hierarchy_for_copy,
        'curriculum_levels_for_copy': curriculum_levels_for_copy
    })
    
    template = Template(test_template)
    rendered_output = template.render(context)
    
    print("\n📋 RENDERED TEMPLATE OUTPUT:")
    print("-" * 40)
    print(rendered_output)
    
    # Check if key indicators are present
    if 'curriculum_hierarchy_for_copy IS AVAILABLE' in rendered_output:
        print("\n✅ Template shows curriculum_hierarchy_for_copy is available")
    elif 'Using FALLBACK curriculum_levels_for_copy' in rendered_output:
        print("\n⚠️ Template is using fallback curriculum_levels_for_copy")
    elif 'NO CURRICULUM DATA AVAILABLE' in rendered_output:
        print("\n❌ Template shows NO curriculum data available")
    else:
        print("\n❓ Unclear which template path was taken")
        
    # Check for JSON script element
    if 'copy-curriculum-hierarchy-data' in rendered_output:
        print("✅ JSON script element is created in template")
    else:
        print("❌ JSON script element is NOT created")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()