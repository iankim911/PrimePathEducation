import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings')
django.setup()

from django.db import connection

# Check if ExamLevelMapping table exists and has data
with connection.cursor() as cursor:
    # Check table existence
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='core_examlevelmapping';
    """)
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("ExamLevelMapping table exists!")
        
        # Count rows
        cursor.execute("SELECT COUNT(*) FROM core_examlevelmapping;")
        count = cursor.fetchone()[0]
        print(f"Total exam mappings: {count}")
        
        # Show first 5 mappings
        cursor.execute("""
            SELECT elm.id, elm.curriculum_level_id, elm.exam_id, elm.slot,
                   cl.id as level_id, sp.name as subprogram_name, cl.level_number
            FROM core_examlevelmapping elm
            JOIN core_curriculumlevel cl ON elm.curriculum_level_id = cl.id
            JOIN core_subprogram sp ON cl.subprogram_id = sp.id
            LIMIT 5;
        """)
        mappings = cursor.fetchall()
        
        print("\nFirst 5 mappings:")
        for mapping in mappings:
            print(f"  ID: {mapping[0]}, Level: {mapping[5]} Level {mapping[6]}, Exam ID: {mapping[2]}, Slot: {mapping[3]}")
    else:
        print("ExamLevelMapping table does not exist!")
        
# Check placement rules
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM core_placementrule;")
    rule_count = cursor.fetchone()[0]
    print(f"\nTotal placement rules: {rule_count}")
    
    # Show rules for grade 1
    cursor.execute("""
        SELECT pr.*, cl.id, sp.name, cl.level_number
        FROM core_placementrule pr
        JOIN core_curriculumlevel cl ON pr.curriculum_level_id = cl.id
        JOIN core_subprogram sp ON cl.subprogram_id = sp.id
        WHERE pr.grade = 1;
    """)
    rules = cursor.fetchall()
    
    print("\nPlacement rules for grade 1:")
    for rule in rules:
        print(f"  Grade {rule[1]}, Rank {rule[2]}-{rule[3]}% -> {rule[8]} Level {rule[9]}")