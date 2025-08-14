# Duplicate Exam Mapping Fix Documentation
*Date: August 14, 2025*

## Problem Description
The placement test system had a critical issue where the same exam could be mapped to multiple curriculum levels. This prevented proper difficulty adjustment because when students requested harder/easier exams, they would receive the same exam again.

### Specific Issues Found:
1. **[PT]_CORE_SIGMA_Lv3_250812** was mapped to both Sigma Level 1 AND Level 3
2. **[PT]_CORE_SIGMA_Lv2_250812** was mapped to both Sigma Level 1 AND Level 2  
3. **[PT] PHONICS all levels** was mapped to ALL three Phonics levels (1, 2, 3)

This caused the "already at most advanced level" error when students tried to adjust difficulty mid-exam.

## Root Cause Analysis
1. **Missing Database Constraint**: The ExamLevelMapping model had `unique_together` for (curriculum_level, exam) but NOT a constraint preventing the same exam from being mapped to multiple levels
2. **No Frontend Validation**: The admin interface allowed selecting already-mapped exams for different levels
3. **No Backend Validation**: The save operation didn't check if an exam was already mapped elsewhere

## Solution Implemented

### 1. Database Cleanup (COMPLETED)
Created and executed `fix_duplicate_exam_mappings.py` script that:
- Identified all duplicate mappings
- Intelligently kept mappings where exam names matched level numbers (e.g., Lv2 exam stays with Level 2)
- Reassigned alternative exams where available
- Removed mappings where no alternatives existed

**Results:**
- Fixed 3 duplicate exams affecting 7 mappings
- Each exam is now uniquely mapped to only one curriculum level
- Difficulty progression now works correctly

### 2. Backend Prevention (COMPLETED)
Updated `core/models/placement.py`:
```python
class ExamLevelMapping(models.Model):
    # Added validation in clean() method
    def clean(self):
        existing = ExamLevelMapping.objects.filter(exam=self.exam).exclude(pk=self.pk).first()
        if existing:
            raise ValidationError(f'This exam is already mapped to {existing.curriculum_level.full_name}')
    
    # Added database constraint
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['exam'],
                name='unique_exam_per_mapping'
            )
        ]
```

### 3. Frontend Enhancement (COMPLETED)
Updated `templates/core/placement_configuration.html` and `core/views.py`:
- Exam dropdowns now show already-mapped exams as disabled
- Display which level an exam is already mapped to
- Prevent selection of already-mapped exams

### 4. Database Migration (COMPLETED)
Created migration `0006_examlevelmapping_unique_exam_per_mapping.py` to add the unique constraint at the database level.

## Verification Steps

### Check for Duplicates
```bash
python fix_duplicate_exam_mappings.py --report-only
```

### Apply Fix (if duplicates found)
```bash
python fix_duplicate_exam_mappings.py --fix
```

### Apply Migration
```bash
python manage.py migrate core
```

## Testing Confirmation
✅ No duplicate exam mappings remain in database
✅ Each exam is uniquely mapped to one curriculum level
✅ Difficulty adjustment now works correctly (different exams at each level)
✅ Frontend prevents selecting already-mapped exams
✅ Backend validation prevents saving duplicate mappings

## Prevention Measures
1. **Database Constraint**: UniqueConstraint prevents duplicates at DB level
2. **Model Validation**: clean() method validates before save
3. **Frontend Validation**: Disabled options for already-mapped exams
4. **Visual Feedback**: Shows which level an exam is already mapped to

## Impact
- Students can now properly request harder/easier exams
- Each difficulty level has unique exam content
- Curriculum progression works as intended
- No more "already at most advanced level" errors when exams were actually different

## Files Modified
1. `/core/models/placement.py` - Added validation and constraint
2. `/core/views.py` - Enhanced exam data with mapping status
3. `/templates/core/placement_configuration.html` - Updated dropdowns to show mapping status
4. `/fix_duplicate_exam_mappings.py` - Created cleanup utility
5. `/core/migrations/0006_examlevelmapping_unique_exam_per_mapping.py` - Database constraint migration

## Maintenance
Run `fix_duplicate_exam_mappings.py --report-only` periodically to verify no new duplicates have been created.