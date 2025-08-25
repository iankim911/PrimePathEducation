#!/usr/bin/env python
"""
Test the ACTUAL logic from the view file
"""

def test_actual_view_logic():
    """Test using the exact logic from classes_exams_unified.py"""
    
    test_cases = [
        ('PS1', 'PS1'),
        ('Hight1_SaiSun_3-5', 'Hight SaiSun 3-5'),  # Problematic case
        ('HightTV2_SaiSun_11-1', 'HightTV2 SaiSun 11-1'),  # Should work
    ]
    
    debug_codes = ['PS1', 'P1', 'P2', 'High1_SaiSun_3-5', 'High1_SaiSun_5-7', 'High1V2_SaiSun_11-1', 'High1V2_SaiSun_1-3']
    
    print("🧪 TESTING ACTUAL VIEW LOGIC")
    print("="*50)
    
    for code, curriculum in test_cases:
        print(f"\n🔍 Testing: '{code}' vs '{curriculum}'")
        
        class_display_name = None
        
        # EXACT copy of the view logic
        
        # Case 1: Exact match (PS1 -> PS1)
        if curriculum == code:
            class_display_name = code
            dedup_reason = "EXACT_MATCH"
        
        # Case 2: Curriculum is just reformatted version of code
        elif curriculum.replace(' ', '_').replace('-', '_') == code.replace(' ', '_').replace('-', '_'):
            # Show the more readable curriculum version
            class_display_name = curriculum
            dedup_reason = "REFORMATTED"
        
        # Case 3: Advanced formatting similarity check
        elif (code.replace('_', ' ').replace('-', '') in curriculum.replace('-', '') and 
              curriculum.replace(' ', '').replace('-', '') in code.replace('_', '').replace('-', '')):
            class_display_name = curriculum  # Show the more readable version
            dedup_reason = "FORMATTING_SIMILARITY"
        
        # Case 4: Code is substring of curriculum with formatting
        elif code.replace('_', ' ') in curriculum or curriculum.replace(' ', '_') == code:
            class_display_name = curriculum
            dedup_reason = "SUBSTRING_MATCH"
        
        # Case 5: Character-based similarity check for tricky cases
        else:
            # Calculate character-based similarity
            code_chars = set(code.replace('_', '').replace('-', '').replace(' ', '').lower())
            curriculum_chars = set(curriculum.replace('_', '').replace('-', '').replace(' ', '').lower())
            
            if code_chars and curriculum_chars:  # Avoid division by zero
                intersection = code_chars & curriculum_chars
                union = code_chars | curriculum_chars
                similarity = len(intersection) / len(union) if union else 0
                
                # Also check length difference
                code_clean = code.replace('_', '').replace('-', '').replace(' ', '').lower()
                curriculum_clean = curriculum.replace('_', '').replace('-', '').replace(' ', '').lower()
                length_diff = abs(len(code_clean) - len(curriculum_clean))
                
                print(f"   📊 Similarity analysis:")
                print(f"      Code chars: {sorted(code_chars)}")
                print(f"      Curriculum chars: {sorted(curriculum_chars)}")
                print(f"      Similarity: {similarity:.3f}")
                print(f"      Length difference: {length_diff}")
                
                # High similarity + small length difference = probably the same thing formatted differently
                if similarity > 0.85 and length_diff <= 3:
                    class_display_name = curriculum  # Show the more readable version
                    dedup_reason = "HIGH_SIMILARITY"
                    print(f"      ✅ HIGH_SIMILARITY threshold met!")
                else:
                    class_display_name = f"{code} - {curriculum}"
                    dedup_reason = "DIFFERENT_CONTENT"
                    print(f"      ❌ Did not meet HIGH_SIMILARITY threshold")
            else:
                class_display_name = f"{code} - {curriculum}"
                dedup_reason = "DIFFERENT_CONTENT"
        
        print(f"   🎯 Result: '{class_display_name}' ({dedup_reason})")
        
        # Check if this fixed the duplication
        original = f"{code} - {curriculum}"
        if original != class_display_name:
            if ' - ' in class_display_name:
                parts = class_display_name.split(' - ')
                if len(parts) == 2 and parts[0] == parts[1]:
                    print(f"   ❌ Still duplicated!")
                else:
                    print(f"   ✅ Fixed (no longer '{original}')")
            else:
                print(f"   ✅ Fixed (no longer '{original}')")
        else:
            print(f"   ➖ No change from original")
    
    print(f"\n" + "="*50)

if __name__ == "__main__":
    test_actual_view_logic()