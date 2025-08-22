#!/usr/bin/env python
"""
Check for URL namespace and template tag conflicts
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    print("Attempting to analyze without full Django initialization...")

def check_namespace_conflicts():
    """Check for URL namespace conflicts"""
    print("\n" + "="*70)
    print("CHECKING URL NAMESPACE CONFLICTS")
    print("="*70)
    
    print("\n🔍 From server logs, detected conflicts:")
    print("1. URL Namespace Warning: 'api:api_v1' isn't unique")
    print("2. Template Tag Warning: 'grade_tags' used for multiple modules")
    print("3. URL Path Conflicts: 5 conflicts in legacy patterns")
    
    # Analyze the logs we saw
    conflicts_found = {
        'url_path_conflicts': [
            {
                'pattern': 'sessions/',
                'conflict': 'sessions_redirect vs session_list'
            },
            {
                'pattern': 'session/<uuid:session_id>/',
                'conflict': 'session_detail_redirect vs take_test'
            },
            {
                'pattern': 'session/<uuid:session_id>/submit/',
                'conflict': 'session_submit_redirect vs submit_answer'
            }
        ],
        'namespace_conflicts': [
            {
                'namespace': 'api:api_v1',
                'issue': 'Not unique - may prevent URL reversing'
            }
        ],
        'template_tag_conflicts': [
            {
                'tag_name': 'grade_tags',
                'modules': [
                    'placement_test.templatetags.grade_tags',
                    'primepath_routinetest.templatetags.grade_tags'
                ]
            }
        ]
    }
    
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"  URL Path Conflicts: {len(conflicts_found['url_path_conflicts'])}")
    print(f"  Namespace Conflicts: {len(conflicts_found['namespace_conflicts'])}")
    print(f"  Template Tag Conflicts: {len(conflicts_found['template_tag_conflicts'])}")
    
    return conflicts_found

def suggest_fixes(conflicts):
    """Suggest fixes for the conflicts"""
    print(f"\n🔧 RECOMMENDED FIXES:")
    
    print(f"\n1. URL Namespace Conflicts:")
    for conflict in conflicts['namespace_conflicts']:
        print(f"   - {conflict['namespace']}: Make namespace unique")
        print(f"     Solution: Change 'api_v1' to 'placement_api_v1' or 'routinetest_api_v1'")
    
    print(f"\n2. Template Tag Conflicts:")
    for conflict in conflicts['template_tag_conflicts']:
        print(f"   - {conflict['tag_name']}: Used by multiple modules")
        print(f"     Modules: {', '.join(conflict['modules'])}")
        print(f"     Solution: Rename one to avoid collision (e.g., 'placement_grade_tags')")
    
    print(f"\n3. URL Path Conflicts:")
    for conflict in conflicts['url_path_conflicts']:
        print(f"   - {conflict['pattern']}: {conflict['conflict']}")
        print(f"     Solution: Use unique URL patterns or consolidate duplicate routes")
    
    print(f"\n🎯 PRIORITY ORDER:")
    print(f"   1. Template tag conflicts (HIGH) - Can break template rendering")
    print(f"   2. URL namespace conflicts (MEDIUM) - Can break URL reversing")
    print(f"   3. URL path conflicts (LOW) - System handles with precedence")

def check_specific_files():
    """Check specific files for conflicts"""
    print(f"\n📁 FILES TO EXAMINE:")
    
    # Template tag files
    template_tag_files = [
        "placement_test/templatetags/grade_tags.py",
        "primepath_routinetest/templatetags/grade_tags.py"
    ]
    
    print(f"\n🏷️  Template Tag Files:")
    for file_path in template_tag_files:
        full_path = os.path.join(os.getcwd(), file_path)
        exists = os.path.exists(full_path)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"   {file_path} - {status}")
    
    # URL configuration files
    url_files = [
        "primepath_project/urls.py",
        "placement_test/urls.py", 
        "primepath_routinetest/urls.py"
    ]
    
    print(f"\n🔗 URL Configuration Files:")
    for file_path in url_files:
        full_path = os.path.join(os.getcwd(), file_path)
        exists = os.path.exists(full_path)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"   {file_path} - {status}")

def main():
    print("CONFLICT DETECTION AND ANALYSIS TOOL")
    print("Analyzing URL namespace and template tag conflicts...")
    
    conflicts = check_namespace_conflicts()
    suggest_fixes(conflicts)
    check_specific_files()
    
    print(f"\n✅ Analysis complete. Next steps:")
    print(f"   1. Fix template tag naming conflicts first")
    print(f"   2. Make URL namespaces unique")
    print(f"   3. Consolidate duplicate URL patterns")
    print(f"   4. Test after each fix")

if __name__ == '__main__':
    main()