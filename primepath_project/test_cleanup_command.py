#!/usr/bin/env python
"""
Test the test data cleanup management command
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from io import StringIO
from django.core.management import call_command

def test_cleanup_command():
    """Test the cleanup command with dry run"""
    print("\n" + "="*70)
    print("TESTING TEST DATA CLEANUP COMMAND")
    print("="*70)
    
    # Capture output
    out = StringIO()
    
    try:
        # Test with dry run to see what would be cleaned
        call_command(
            'clean_test_data',
            '--dry-run',
            '--category=users',
            '--days-old=1',  # Very recent to catch more
            stdout=out
        )
        
        output = out.getvalue()
        print("✅ Command executed successfully")
        print("\nOutput:")
        print(output)
        
        return True
        
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False

if __name__ == '__main__':
    success = test_cleanup_command()
    if success:
        print("\n✅ Cleanup command test completed")
    else:
        print("\n❌ Test failed")