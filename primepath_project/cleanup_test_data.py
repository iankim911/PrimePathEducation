#!/usr/bin/env python3
"""
Clean up test data - remove test exams and PDFs
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models import Exam
from placement_test.models import Exam as PlacementExam

def cleanup_test_data():
    """Remove test exams and PDFs created during testing"""
    
    # Test patterns to look for
    test_patterns = [
        'PDF Persistence Test',
        'fixed_test',
        'Test',
        'test_',
        'QA Test',
        'DEBUG',
        'debug',
        'TEMPORARY'
    ]
    
    print("🧹 Starting test data cleanup...")
    
    # Clean up RoutineTest exams
    routinetest_deleted = 0
    for pattern in test_patterns:
        exams = Exam.objects.filter(name__icontains=pattern)
        count = exams.count()
        if count > 0:
            print(f"   Deleting {count} RoutineTest exams matching '{pattern}'...")
            for exam in exams:
                print(f"     - {exam.name}")
                # Delete associated PDF files
                if hasattr(exam, 'pdf_file') and exam.pdf_file:
                    try:
                        if os.path.exists(exam.pdf_file.path):
                            os.remove(exam.pdf_file.path)
                            print(f"       Deleted PDF: {exam.pdf_file.path}")
                    except Exception as e:
                        print(f"       Warning: Could not delete PDF {exam.pdf_file}: {e}")
            exams.delete()
            routinetest_deleted += count
    
    # Clean up PlacementTest exams  
    placement_deleted = 0
    for pattern in test_patterns:
        exams = PlacementExam.objects.filter(name__icontains=pattern)
        count = exams.count()
        if count > 0:
            print(f"   Deleting {count} PlacementTest exams matching '{pattern}'...")
            for exam in exams:
                print(f"     - {exam.name}")
                # Delete associated PDF files
                if hasattr(exam, 'pdf_file') and exam.pdf_file:
                    try:
                        if os.path.exists(exam.pdf_file.path):
                            os.remove(exam.pdf_file.path)
                            print(f"       Deleted PDF: {exam.pdf_file.path}")
                    except Exception as e:
                        print(f"       Warning: Could not delete PDF {exam.pdf_file}: {e}")
            exams.delete()
            placement_deleted += count
    
    # Clean up test PDF files in media directory
    media_root = project_root / 'media'
    pdf_dirs = [
        media_root / 'exams' / 'pdfs',
        media_root / 'routine_exams',
        media_root / 'routinetest' / 'exams'
    ]
    
    files_deleted = 0
    for pdf_dir in pdf_dirs:
        if pdf_dir.exists():
            for pdf_file in pdf_dir.glob('*.pdf'):
                file_name = pdf_file.name.lower()
                if any(pattern.lower() in file_name for pattern in test_patterns):
                    print(f"   Deleting test PDF: {pdf_file}")
                    try:
                        pdf_file.unlink()
                        files_deleted += 1
                    except Exception as e:
                        print(f"     Warning: Could not delete {pdf_file}: {e}")
    
    print(f"\n✅ Cleanup complete!")
    print(f"   RoutineTest exams deleted: {routinetest_deleted}")
    print(f"   PlacementTest exams deleted: {placement_deleted}")
    print(f"   PDF files deleted: {files_deleted}")
    
    return routinetest_deleted + placement_deleted + files_deleted

if __name__ == '__main__':
    total_deleted = cleanup_test_data()
    print(f"\n🎯 Total items cleaned: {total_deleted}")