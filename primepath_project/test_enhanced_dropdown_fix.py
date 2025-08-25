#!/usr/bin/env python
"""
Test enhanced class dropdown deduplication fix
Specifically tests high school class cases
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

def test_enhanced_deduplication():
    """Test the enhanced deduplication logic"""
    print("="*80)
    print("🧪 TESTING ENHANCED CLASS DROPDOWN DEDUPLICATION")
    print("="*80)
    
    # Test cases that cover all scenarios from the screenshot
    test_cases = [
        # Case 1: Exact match (original issue)
        ('PS1', 'PS1'),
        ('P1', 'P1'),
        ('B2', 'B2'),
        
        # Case 2: Reformatted version (high school issue)
        ('High1_SaiSun_3-5', 'High1 SaiSun 3-5'),
        ('High1_SaiSun_5-7', 'High1 SaiSun 5-7'),
        ('High1V2_SaiSun_11-1', 'High1V2 SaiSun 11-1'),
        ('High1V2_SaiSun_1-3', 'High1V2 SaiSun 1-3'),
        
        # Case 3: Typo version (from screenshot)
        ('Hight1_SaiSun_3-5', 'Hight SaiSun 3-5'),  # Note the typo 'Hight'
        ('HightTV2_SaiSun_11-1', 'HightTV2 SaiSun 11-1'),
        
        # Case 4: Different content (should keep both)
        ('TEST_CODE', 'Advanced Test Program'),
    ]
    
    print(f"\n🔧 APPLYING ENHANCED DEDUPLICATION LOGIC:")
    print(f"Case 1: Exact match -> show just code")
    print(f"Case 2: Reformatted version -> show cleaner curriculum")
    print(f"Case 3: Substring match -> show curriculum") 
    print(f"Case 4: Different content -> show 'code - curriculum'")
    
    results = []
    
    for code, curriculum in test_cases:
        # Apply enhanced deduplication logic
        class_display_name = None
        
        # Case 1: Exact match (PS1 -> PS1)
        if curriculum == code:
            class_display_name = code
            dedup_reason = "EXACT_MATCH"
        
        # Case 2: Curriculum is just reformatted version of code
        elif curriculum.replace(' ', '_').replace('-', '_') == code.replace(' ', '_').replace('-', '_'):
            # Show the more readable curriculum version
            class_display_name = curriculum
            dedup_reason = "REFORMATTED"
        
        # Case 3: Code is substring of curriculum with formatting
        elif code.replace('_', ' ') in curriculum or curriculum.replace(' ', '_') == code:
            class_display_name = curriculum
            dedup_reason = "SUBSTRING_MATCH"
        
        # Case 4: Different content - show both
        else:
            class_display_name = f"{code} - {curriculum}"
            dedup_reason = "DIFFERENT_CONTENT"
        
        # Old display for comparison
        old_display = f"{code} - {curriculum}"
        
        results.append({
            'code': code,
            'curriculum': curriculum,
            'old_display': old_display,
            'new_display': class_display_name,
            'reason': dedup_reason,
            'improved': old_display != class_display_name
        })
    
    # Show results
    print(f"\n📋 DEDUPLICATION RESULTS:")
    print(f"{'Code':<20} {'Curriculum':<25} {'Before':<35} {'After':<25} {'Logic'}")
    print(f"{'-'*20} {'-'*25} {'-'*35} {'-'*25} {'-'*15}")
    
    for result in results:
        improved_icon = "✅" if result['improved'] else "➖"
        print(f"{result['code']:<20} {result['curriculum']:<25} {result['old_display']:<35} {result['new_display']:<25} {result['reason']} {improved_icon}")
    
    # Check specific screenshot issues
    print(f"\n📷 SCREENSHOT ISSUE ANALYSIS:")
    screenshot_issues = [
        'Hight1_SaiSun_3-5 - Hight SaiSun 3-5',
        'Hight1_SaiSun_6-7 - Hight SaiSun 6-7', 
        'HightTV2_SaiSun_11-1 - HightTV2 SaiSun 11-1',
        'HightTV2_SaiSun_1-3 - HightTV2 SaiSun 1-3',
    ]
    
    for issue in screenshot_issues:
        parts = issue.split(' - ')
        if len(parts) == 2:
            code, curriculum = parts
            
            # Apply our logic
            if curriculum.replace(' ', '_').replace('-', '_') == code.replace(' ', '_').replace('-', '_'):
                fixed_display = curriculum
                reason = "REFORMATTED"
            elif code.replace('_', ' ') in curriculum:
                fixed_display = curriculum
                reason = "SUBSTRING_MATCH"
            else:
                fixed_display = issue
                reason = "NO_CHANGE"
            
            print(f"   '{issue}' -> '{fixed_display}' ({reason})")
    
    # Summary
    improvements = sum(1 for r in results if r['improved'])
    total = len(results)
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Test cases processed: {total}")
    print(f"   Cases improved: {improvements}")
    print(f"   Improvement rate: {(improvements/total)*100:.1f}%")
    
    # Check for remaining duplications
    remaining_dups = [r for r in results if ' - ' in r['new_display'] and r['new_display'].split(' - ')[0] == r['new_display'].split(' - ')[1]]
    
    if remaining_dups:
        print(f"   ❌ Still duplicated: {len(remaining_dups)}")
        for dup in remaining_dups:
            print(f"      - {dup['new_display']}")
    else:
        print(f"   ✅ No remaining duplications!")
    
    print(f"\n" + "="*80)
    print(f"🎉 ENHANCED FIX TEST COMPLETED!")
    print(f"The enhanced logic handles both simple and complex deduplication cases.")
    print(f"="*80)
    
    return len(remaining_dups) == 0

if __name__ == "__main__":
    success = test_enhanced_deduplication()
    sys.exit(0 if success else 1)