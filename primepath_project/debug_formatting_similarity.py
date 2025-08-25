#!/usr/bin/env python
"""
Debug the formatting similarity issue
"""

def debug_similarity_check():
    """Debug why 'Hight1_SaiSun_3-5' vs 'Hight SaiSun 3-5' isn't matching"""
    
    test_cases = [
        ('Hight1_SaiSun_3-5', 'Hight SaiSun 3-5'),
        ('HightTV2_SaiSun_11-1', 'HightTV2 SaiSun 11-1'),  # This should work
    ]
    
    for code, curriculum in test_cases:
        print(f"\n🔍 DEBUGGING: '{code}' vs '{curriculum}'")
        
        # Test current logic
        print(f"   Code normalized: '{code.replace('_', ' ').replace('-', '')}'")
        print(f"   Curriculum normalized: '{curriculum.replace('-', '')}'")
        
        cond1 = code.replace('_', ' ').replace('-', '') in curriculum.replace('-', '')
        cond2 = curriculum.replace(' ', '').replace('-', '') in code.replace('_', '').replace('-', '')
        
        print(f"   Condition 1 (code in curriculum): {cond1}")
        print(f"   Condition 2 (curriculum in code): {cond2}")
        print(f"   Both conditions: {cond1 and cond2}")
        
        # Let's try a different approach - character-based similarity
        code_chars = set(code.replace('_', '').replace('-', '').replace(' ', '').lower())
        curriculum_chars = set(curriculum.replace('_', '').replace('-', '').replace(' ', '').lower())
        
        intersection = code_chars & curriculum_chars
        union = code_chars | curriculum_chars
        similarity = len(intersection) / len(union) if union else 0
        
        print(f"   Character similarity: {similarity:.2f}")
        print(f"   Code chars: {sorted(code_chars)}")
        print(f"   Curriculum chars: {sorted(curriculum_chars)}")
        
        # Test length-based approach
        code_clean = code.replace('_', '').replace('-', '').replace(' ', '').lower()
        curriculum_clean = curriculum.replace('_', '').replace('-', '').replace(' ', '').lower()
        
        print(f"   Code clean: '{code_clean}'")
        print(f"   Curriculum clean: '{curriculum_clean}'")
        print(f"   Length diff: {abs(len(code_clean) - len(curriculum_clean))}")
        
        # Test if they're essentially the same with minor differences
        if similarity > 0.8 and abs(len(code_clean) - len(curriculum_clean)) <= 2:
            print(f"   ✅ WOULD BE CAUGHT by improved similarity check")
        else:
            print(f"   ❌ Would not be caught")

if __name__ == "__main__":
    debug_similarity_check()