#!/usr/bin/env python
"""
Clean invalid Unicode characters from database
"""

import os
import sys
import django
import json
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import PlacementExam as Exam, Question, AudioFile
from primepath_routinetest.models import RoutineExam as Exam as RoutineExam, Question as RoutineQuestion
from core.models import Program, SubProgram

def clean_unicode(text):
    """Remove invalid Unicode characters from text"""
    if not text:
        return text
    
    # Remove invalid Unicode surrogates
    try:
        # Try to encode/decode to clean
        text = text.encode('utf-8', 'surrogatepass').decode('utf-8', 'ignore')
    except:
        pass
    
    # Remove zero-width characters and other problematic Unicode
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Remove invalid surrogates
    text = re.sub(r'[\ud800-\udfff]', '', text)
    
    return text

def test_json_serializable(obj, field_name, value):
    """Test if a value can be JSON serialized"""
    try:
        json.dumps({field_name: value})
        return True, None
    except Exception as e:
        return False, str(e)

def clean_model_fields(model_class, fields_to_clean):
    """Clean text fields in a model"""
    print(f"\nCleaning {model_class.__name__}...")
    
    cleaned_count = 0
    error_count = 0
    
    for obj in model_class.objects.all():
        needs_save = False
        
        for field in fields_to_clean:
            if hasattr(obj, field):
                original_value = getattr(obj, field)
                
                # Skip None values
                if original_value is None:
                    continue
                
                # Test if current value is problematic
                is_valid, error = test_json_serializable(obj, field, original_value)
                
                if not is_valid:
                    print(f"  ❌ {obj.id}: Field '{field}' has invalid Unicode: {error[:50]}")
                    
                    # Clean the value
                    cleaned_value = clean_unicode(str(original_value))
                    
                    # Test if cleaned value is now valid
                    is_valid_after, _ = test_json_serializable(obj, field, cleaned_value)
                    
                    if is_valid_after:
                        setattr(obj, field, cleaned_value)
                        needs_save = True
                        print(f"    ✅ Cleaned successfully")
                    else:
                        print(f"    ⚠️ Still invalid after cleaning, setting to empty string")
                        setattr(obj, field, "")
                        needs_save = True
                        error_count += 1
        
        if needs_save:
            try:
                obj.save()
                cleaned_count += 1
            except Exception as e:
                print(f"    ❌ Failed to save: {e}")
                error_count += 1
    
    print(f"  Cleaned {cleaned_count} records, {error_count} errors")
    return cleaned_count, error_count

def main():
    print("="*80)
    print("CLEANING INVALID UNICODE FROM DATABASE")
    print("="*80)
    
    total_cleaned = 0
    total_errors = 0
    
    # Clean Placement Test models
    cleaned, errors = clean_model_fields(
        Exam, 
        ['name', 'description', 'instructions']
    )
    total_cleaned += cleaned
    total_errors += errors
    
    cleaned, errors = clean_model_fields(
        Question,
        ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
    )
    total_cleaned += cleaned
    total_errors += errors
    
    cleaned, errors = clean_model_fields(
        AudioFile,
        ['name', 'transcript']
    )
    total_cleaned += cleaned
    total_errors += errors
    
    # Clean Routine Test models
    cleaned, errors = clean_model_fields(
        RoutineExam,
        ['name', 'exam_type', 'instructions']
    )
    total_cleaned += cleaned
    total_errors += errors
    
    cleaned, errors = clean_model_fields(
        RoutineQuestion,
        ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
    )
    total_cleaned += cleaned
    total_errors += errors
    
    # Clean Core models
    cleaned, errors = clean_model_fields(
        Program,
        ['name', 'description']
    )
    total_cleaned += cleaned
    total_errors += errors
    
    cleaned, errors = clean_model_fields(
        SubProgram,
        ['name', 'description']
    )
    total_cleaned += cleaned
    total_errors += errors
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total records cleaned: {total_cleaned}")
    print(f"Total errors: {total_errors}")
    
    if total_errors == 0:
        print("\n✅ All invalid Unicode has been cleaned!")
    else:
        print("\n⚠️ Some records could not be fully cleaned. Check the output above.")
    
    # Test if API calls work now
    print("\n" + "="*80)
    print("TESTING API AFTER CLEANUP")
    print("="*80)
    
    from django.test import Client
    client = Client()
    
    test_endpoints = [
        '/api/programs/',
        '/PlacementTest/exams/',
        '/RoutineTest/exams/'
    ]
    
    all_pass = True
    for endpoint in test_endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code < 500:
                print(f"✅ {endpoint}: Status {response.status_code}")
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
                all_pass = False
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
            all_pass = False
    
    if all_pass:
        print("\n✅ All API endpoints working after cleanup!")
    else:
        print("\n❌ Some API endpoints still have issues")
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())