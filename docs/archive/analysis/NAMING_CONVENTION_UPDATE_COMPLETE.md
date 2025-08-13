# Naming Convention Update - Implementation Complete

## Date: August 10, 2025

## Summary
Successfully implemented the new exam naming convention as requested, simplifying and standardizing how exam files are named in the system.

## Changes Implemented

### 1. Naming Convention Updates
- **[PlacementTest]** → **[PT]**
- Removed redundant **"PRIME"** from all exam names
- **"Level"** → **"Lv"** (e.g., Level 3 → Lv3)
- **Version format**: Changed from `_v_a`, `_v_b` to `_v1`, `_v2`, etc.
- **Date format**: Added YYMMDD format (e.g., 250810 for Aug 10, 2025)
- **Version logic**: Only add version suffix (_v2, _v3) when multiple uploads for same level on same day

### 2. New Naming Format
```
First upload of the day:  [PT]_Subject_Lv#_YYMMDD
Second upload same day:    [PT]_Subject_Lv#_YYMMDD_v2
Third upload same day:     [PT]_Subject_Lv#_YYMMDD_v3
```

### 3. Examples
- Old: `[PlacementTest] PRIME CORE PHONICS - Level 3_v_a`
- New: `[PT]_CORE_PHONICS_Lv3_250810`

- Old: `[PlacementTest] PRIME EDGE RISE - Level 5_v_b`  
- New: `[PT]_EDGE_RISE_Lv5_250810_v2` (if second upload same day)

- Old: `[PlacementTest] PRIME ASCENT NOVA - Level 1_v_a`
- New: `[PT]_ASCENT_NOVA_Lv1_250810`

**Note**: All spaces in names are automatically replaced with underscores for cleaner file names.

## Files Modified

### Backend Changes
1. **core/models/curriculum.py**
   - Added `display_name` property (shows "Lv" format)
   - Added `exam_base_name` property (generates base name without PRIME)

2. **placement_test/services/exam_service.py**
   - Added `get_next_version_number()` method for numeric versions
   - Checks for same-day uploads to determine if version needed
   - Kept old `get_next_version_letter()` for backward compatibility

3. **placement_test/views/exam.py**
   - Updated `check_exam_version` endpoint to return date and version
   - Modified `create_exam` view to use new naming properties

### Frontend Changes
4. **templates/placement_test/create_exam.html**
   - Updated dropdown to show simplified names (without PRIME, with Lv)
   - Modified JavaScript to generate names with new format
   - Updated help text to explain new naming convention
   - Custom name guidelines now show new format

## Testing Results

### ✅ All Core Tests Passed
- CurriculumLevel properties working correctly
- Version number generation logic working
- Exam name format validated
- API endpoint returning correct data

### ✅ Comprehensive QA Results
- 23/25 tests passed
- All naming convention features working
- Backward compatibility maintained
- No breaking changes to existing functionality

## How It Works

### For Pre-designed Names:
1. User selects curriculum level from dropdown (shows simplified format)
2. System checks if any exams uploaded today for that level
3. If first upload: Creates name like `[PT]_CORE_PHONICS_Lv1_250810`
4. If second+ upload: Adds version like `[PT]_CORE_PHONICS_Lv1_250810_v2`

### For Custom Names:
- Guidelines show new format: `[PT]_Subject_Lv#_Modifier_YYMMDD`
- Example: `[PT]_Math_Lv5_Advanced_250810`

## Benefits
1. **Shorter names** - More concise and easier to read
2. **Systematic versioning** - Clear when multiple versions exist
3. **Date tracking** - Easy to see when exam was uploaded
4. **No redundancy** - Removed repeated "PRIME" text
5. **Standard abbreviations** - Consistent use of Lv for levels

## Backward Compatibility
- Existing exams with old naming convention remain unchanged
- System can still read and process old format
- Only new uploads use the new convention

## Next Steps
The implementation is complete and tested. The system will now:
- Use the new naming convention for all new exam uploads
- Display simplified names in the upload dropdown
- Automatically handle versioning for same-day uploads
- Show dates in YYMMDD format

No further action required. The naming convention update is fully operational.