#!/usr/bin/env python3
"""
Verification script for phantom class cleanup
Confirms all phantom classes have been removed from database
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models import Class
from primepath_routinetest.models.class_access import TeacherClassAssignment

def main():
    print("🔍 PHANTOM CLASS CLEANUP VERIFICATION")
    print("=" * 50)
    
    # Your actual class list
    actual_classes = [
        'PS1', 'P1', 'P2', 'A2', 'B2', 'B3', 'B4', 'B5', 'S2', 'H1', 'H2', 
        'C2', 'C3', 'C4', 'C5', 'H4', 'Young-cho2', 'Chung-choM', 'Chung-cho1', 
        'SejongM', 'MAS', 'TaejoC', 'TaejoD', 'TaejoE', 'TaejoG', 'SungjongM', 
        'Sungjong2', 'Sungjong3', 'Sungjong4', 'Young-choM', 'D2', 'D3', 'D4', 
        'High1 SaiSun 3-5', 'High1 SaiSun 5-7', 'High1V2 SaiSun 11-1', 'High1V2 SaiSun 1-3'
    ]
    
    # Check Class model
    all_classes = Class.objects.all()
    current_classes = list(Class.objects.values_list('section', flat=True))
    
    print(f"📊 Database Status:")
    print(f"   Expected classes: {len(actual_classes)}")
    print(f"   Current classes:  {len(current_classes)}")
    
    # Check for phantom classes
    phantom_classes = [cls for cls in current_classes if cls not in actual_classes and cls]
    missing_classes = [cls for cls in actual_classes if cls not in current_classes]
    
    print(f"\n🚨 Phantom Classes Found: {len(phantom_classes)}")
    if phantom_classes:
        for phantom in phantom_classes:
            print(f"   PHANTOM: {phantom}")
    else:
        print("   ✅ No phantom classes!")
    
    print(f"\n❌ Missing Valid Classes: {len(missing_classes)}")
    if missing_classes:
        for missing in missing_classes:
            print(f"   MISSING: {missing}")
    else:
        print("   ✅ All valid classes present!")
    
    # Check TeacherClassAssignment model
    all_assignments = TeacherClassAssignment.objects.all()
    current_assignments = list(TeacherClassAssignment.objects.values_list('class_code', flat=True))
    phantom_assignments = [code for code in current_assignments if code not in actual_classes and code]
    
    print(f"\n🎯 TeacherClassAssignment Status:")
    print(f"   Current assignments: {len(current_assignments)}")
    print(f"   Phantom assignments: {len(phantom_assignments)}")
    
    if phantom_assignments:
        for phantom in phantom_assignments:
            print(f"   PHANTOM ASSIGNMENT: {phantom}")
    else:
        print("   ✅ No phantom assignments!")
    
    # Check specifically for PINNACLE phantoms
    pinnacle_phantoms = [cls for cls in current_classes if 'PINNACLE_' in cls]
    print(f"\n🏔️  PINNACLE Phantom Check: {len(pinnacle_phantoms)}")
    if pinnacle_phantoms:
        for phantom in pinnacle_phantoms:
            print(f"   PINNACLE PHANTOM: {phantom}")
    else:
        print("   ✅ No PINNACLE phantoms!")
    
    # Overall status
    print(f"\n{'='*50}")
    if len(phantom_classes) == 0 and len(missing_classes) == 0 and len(phantom_assignments) == 0:
        print("🎉 SUCCESS: All phantom classes removed!")
        print("   Database is clean and contains only valid classes")
        print(f"   Ready for production use with {len(actual_classes)} classes")
    else:
        print("❌ ISSUES DETECTED:")
        print(f"   Phantom classes: {len(phantom_classes)}")
        print(f"   Missing classes: {len(missing_classes)}")
        print(f"   Phantom assignments: {len(phantom_assignments)}")

if __name__ == "__main__":
    main()