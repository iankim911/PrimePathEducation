# Skip First Left Half Implementation

## Overview
Successfully implemented a feature that allows teachers to configure exams to skip the first left half of page 1. This is useful for exams with cover pages or instructions that don't contain actual questions.

## Changes Made

### 1. **Database Model Update**
Added `skip_first_left_half` field to the Exam model:
```python
skip_first_left_half = models.BooleanField(
    default=False, 
    help_text="Skip the first left half of page 1 in column view"
)
```

### 2. **Upload Exam Interface**
- Added a checkbox in the exam upload form
- Label: "Skip first left half of page 1"
- Help text: "When checked, the exam will start from the right column of page 1 (useful for cover pages)"
- Located in the Exam Information section

### 3. **Preview Updates**
Both admin preview pages now use column view by default:

#### Upload Exam Preview:
- Shows PDF in column view (left/right halves)
- Virtual page numbering (Page 1 = left column, Page 2 = right column)
- When checkbox is checked, preview automatically jumps to page 2
- Page counter shows: "Page X of Y (Left/Right Column)"

#### Manage Exam Preview:
- Same column view implementation
- Shows "Skip First Left Half: Yes/No" in exam info
- Navigation respects the skip setting (can't go to page 1 if skip is enabled)

### 4. **Student Test View**
- Automatically starts from page 2 if skip_first_left_half is enabled
- Previous button disabled on page 2 when skip is enabled
- Students never see the skipped content

## How It Works

### For Teachers:
1. When uploading an exam, check "Skip first left half of page 1"
2. Preview shows the effect immediately
3. Can test navigation to ensure correct behavior

### For Students:
1. If skip is enabled, exam starts from right column of page 1
2. Cannot navigate back to the skipped left column
3. Page numbering remains consistent (starts at page 2)

## Benefits

1. **Cover Pages**: Skip title pages or instructions
2. **Flexible Start**: Begin exam exactly where questions start
3. **Consistent Experience**: Same column view in admin and student interfaces
4. **Visual Feedback**: Clear indication when skip is active

## Migration Required

After pulling these changes, run:
```bash
python manage.py makemigrations
python manage.py migrate
```

This will add the new `skip_first_left_half` field to existing exams (defaulting to False).

## Testing

1. Upload a new exam with the checkbox checked
2. Verify preview starts from page 2 (right column)
3. Test student view to ensure they can't access page 1
4. Verify existing exams still work normally (skip disabled by default)