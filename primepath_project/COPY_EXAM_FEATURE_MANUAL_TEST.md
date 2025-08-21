# Copy Exam Feature - Manual Test Guide

## Feature Summary
The copy exam feature has been successfully implemented with the following enhancements:
- ✅ Year selection dropdown (2024-2027)
- ✅ Custom naming suffix field
- ✅ Automatic naming convention matching Upload Exam feature
- ✅ Real-time name preview
- ✅ Comprehensive error handling and logging

## Testing Steps

### 1. Navigate to Exam Library
- Go to: http://127.0.0.1:8000/RoutineTest/exams/
- Login with teacher credentials if needed

### 2. Find an Exam to Copy
- Look for any exam in the library
- Each exam should have a "Copy" button

### 3. Open Copy Modal
- Click the "Copy" button on any exam
- The copy modal should open with:
  - Source exam name displayed at the top
  - Target Class dropdown
  - Exam Type selector (Review/Quarterly)
  - Time Period selector (updates based on exam type)
  - **NEW: Academic Year dropdown (2024-2027)**
  - **NEW: Custom Name Suffix field**
  - **NEW: Exam Name Preview section**

### 4. Test Name Generation
- Select different options and observe the name preview update:
  - Exam Type: Review → Time Period: February → Year: 2025
  - Expected preview: `[RT] - Feb 2025 - [Curriculum]`
  - Add suffix "test123" 
  - Expected preview: `[RT] - Feb 2025 - [Curriculum]_test123`

### 5. Copy the Exam
- Fill in all required fields
- Add an optional custom suffix
- Click "Copy Exam"
- Should see success message
- Page should reload showing the new exam

## Expected Naming Convention

### Format
`[Type] - [Period] [Year] - [Curriculum]_[suffix]`

### Examples
- `[RT] - Jan 2025 - EDGE Spark Lv1_123`
- `[QTR] - Q1 2026 - CORE Phonics Lv2_version2`
- `[RT] - Mar 2025 - PINNACLE Vision Lv1`

## Console Debugging
Open browser console (F12) to see detailed logging:
- `[COPY_EXAM_REQUEST]` - Initial request details
- `[GENERATE_EXAM_NAME]` - Name generation process
- `[COPY_EXAM_SUCCESS]` - Successful creation
- `[COPY_EXAM_MATRIX_SUCCESS]` - Added to schedule matrix

## Technical Details

### Backend Changes
- Modified `copy_exam` function in `exam_api.py`
- Added `generate_exam_name` helper function
- Created `create_copied_exam` helper function
- Uses RoutineExam model for ExamScheduleMatrix compatibility

### Frontend Changes
- Updated `exam_list_hierarchical.html` with new form fields
- Enhanced `copy-exam-modal.js` with name preview functionality
- Added real-time preview updates

### Known Limitations
- Questions and audio files are not copied (due to model incompatibility)
- Copied exams need questions to be added manually through the exam editor

## Verification
Run the comprehensive test:
```bash
cd /Users/ian/Desktop/VIBECODE/PrimePath/primepath_project
../venv/bin/python test_copy_exam_comprehensive.py
```

Expected output:
- ✅ Name generation tests pass
- ✅ Copy exam API successful
- ✅ Frontend elements verified
- ✅ JavaScript functionality confirmed

---
*Feature implemented: August 21, 2025*
*All requirements met per user specifications*