# Upload Exam - Quick Reference Card
**Working Version: V1 - August 6, 2025**

## 🚨 EMERGENCY RECOVERY

If Upload Exam breaks, use ONE of these:

### Option 1: Full Revert (Safest)
```bash
git checkout upload-exam-working-v1-2025-08-06
```

### Option 2: Get Specific Files
```bash
# Get the working exam service
git checkout upload-exam-working-v1-2025-08-06 -- placement_test/services/exam_service.py

# Get the working view
git checkout upload-exam-working-v1-2025-08-06 -- placement_test/views.py

# Get the working template
git checkout upload-exam-working-v1-2025-08-06 -- templates/placement_test/create_exam.html
```

### Option 3: See What Changed
```bash
# Compare current with working version
git diff upload-exam-working-v1-2025-08-06 -- placement_test/services/exam_service.py
```

---

## ✅ WORKING STATE CHECKLIST

The Upload Exam feature is WORKING when:

1. **No 500 Error** on form submission
2. **PDF Preview** appears after file selection
3. **Success Message** shows after upload
4. **Form Validates** missing fields properly
5. **Exam Appears** in the exam list

---

## 🔧 CRITICAL CODE SECTIONS

### 1. exam_service.py (Line 39-49)
```python
# MUST NOT have skip_first_left_half field!
exam = Exam.objects.create(
    name=exam_data['name'],
    # ... other fields ...
    is_active=exam_data.get('is_active', True)
    # NO skip_first_left_half here!
)
```

### 2. views.py (Lines 243-268)
```python
# MUST have validation
if not exam_name:
    raise ValidationException("Exam name is required", code="MISSING_NAME")
if not total_questions:
    raise ValidationException("Total number of questions is required", code="MISSING_QUESTIONS")
if not pdf_file:
    raise ValidationException("PDF file is required", code="MISSING_PDF")
```

### 3. create_exam.html (Lines 1051-1053)
```javascript
// MUST set default name immediately
const baseName = selectedOption.getAttribute('data-level-name');
finalExamName = `[PlacementTest] ${baseName}_v_a`; // Default FIRST
// Then fetch actual version...
```

---

## 📁 KEY FILES

| File | Purpose | Critical Lines |
|------|---------|---------------|
| `placement_test/services/exam_service.py` | Creates exam in DB | 39-49 |
| `placement_test/views.py` | Handles POST request | 240-286 |
| `templates/placement_test/create_exam.html` | Frontend form | 1048-1110 |
| `placement_test/models.py` | Exam model definition | 7-23 |

---

## 🧪 QUICK TEST

```bash
# 1. Start server
cd primepath_project
../venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite

# 2. Test page loads
curl -I http://127.0.0.1:8000/api/placement/exams/create/

# 3. Run automated test
../venv/Scripts/python.exe test_exam_creation.py
```

---

## 📋 WHAT WAS FIXED

1. **Removed `skip_first_left_half`** - Field no longer exists in DB
2. **Added form validation** - Prevents 500 errors
3. **Fixed race condition** - Name sets immediately
4. **Added error handling** - User-friendly messages

---

## 🔍 DEBUGGING TIPS

If you see **500 Error**:
- Check if `skip_first_left_half` crept back into code
- Check if validation was removed from views.py
- Check if name field is missing from POST data

If you see **"Exam name is required"**:
- Check JavaScript generateVersionedName() function
- Check if finalExamName is being set
- Check form submission handler

---

## 📞 FULL DOCUMENTATION

See: `UPLOAD_EXAM_WORKING_STATE_V1_2025_08_06.md`

---

**Remember**: This is V1 - the FIRST working version after all fixes applied on August 6, 2025