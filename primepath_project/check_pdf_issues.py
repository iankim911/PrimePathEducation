#!/usr/bin/env python
"""
PDF Rotation Persistence Diagnostic
Quick check for PDF upload issues
"""

import sqlite3
import os

def main():
    print("=== PDF ROTATION PERSISTENCE DIAGNOSTIC ===")
    
    # Check database for problematic records
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # RoutineTest exams with rotation but no PDF
    cursor.execute("""
        SELECT 
            hex(id) as id,
            name,
            pdf_file,
            pdf_rotation,
            created_at
        FROM primepath_routinetest_exam 
        WHERE pdf_rotation > 0 AND (pdf_file IS NULL OR pdf_file = '')
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    rt_problems = cursor.fetchall()
    
    # PlacementTest exams with rotation but no PDF
    cursor.execute("""
        SELECT 
            hex(id) as id,
            name,
            pdf_file,
            pdf_rotation,
            created_at
        FROM placement_test_exam 
        WHERE pdf_rotation > 0 AND (pdf_file IS NULL OR pdf_file = '')
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    pt_problems = cursor.fetchall()
    conn.close()
    
    print(f"\n📊 PROBLEMATIC EXAMS FOUND:")
    print(f"   RoutineTest: {len(rt_problems)} exams")
    print(f"   PlacementTest: {len(pt_problems)} exams")
    
    if rt_problems:
        print("\n🔍 RoutineTest Problems:")
        for exam in rt_problems[:5]:
            print(f"   • {exam[1]} (Rotation: {exam[3]}°) - Created: {exam[4]}")
    
    if pt_problems:
        print("\n🔍 PlacementTest Problems:")
        for exam in pt_problems[:5]:
            print(f"   • {exam[1]} (Rotation: {exam[3]}°) - Created: {exam[4]}")
    
    # Check media directories
    print("\n📁 MEDIA DIRECTORIES:")
    media_dirs = [
        'media/routinetest/exams/pdfs',
        'media/exams/pdfs'
    ]
    
    for dir_path in media_dirs:
        if os.path.exists(dir_path):
            files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]
            print(f"   • {dir_path}: {len(files)} PDF files")
        else:
            print(f"   • {dir_path}: Directory missing")
    
    if not rt_problems and not pt_problems:
        print("\n✅ No PDF rotation persistence issues found!")
    else:
        print("\n❌ PDF rotation persistence issues detected.")
        print("   Check server logs during next upload attempt.")

if __name__ == "__main__":
    main()
