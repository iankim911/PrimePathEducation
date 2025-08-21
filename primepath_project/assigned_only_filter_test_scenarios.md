# "Show Assigned Classes Only" Filter - Test Scenarios

## Bug Fix Summary
**Problem**: When "Show Assigned Classes Only" toggle is checked, exams with "VIEW ONLY" badges still appear, but they shouldn't according to the semantic meaning.

**Root Cause**: The filter only included exams from classes where teacher has `FULL` or `CO_TEACHER` access, excluding `VIEW` access.

**Fix**: Changed the condition from `assignments[cls] in ['FULL', 'CO_TEACHER']` to just `cls in assignments` (any assignment level).

## Test Scenarios

### Scenario 1: Teacher with Mixed Access Levels
**Setup:**
- Teacher has assignments:
  - Class A: FULL access
  - Class B: CO_TEACHER access  
  - Class C: VIEW access
- Exams exist in all three classes

**Expected Behavior:**
- **"Show All Exams" (toggle OFF)**: Shows exams from all classes with appropriate badges
- **"Show Assigned Classes Only" (toggle ON)**: Shows exams from Classes A, B, and C (all assigned)

**Test Results Expected:**
- Class A exams: `FULL ACCESS` or `EDIT` badges
- Class B exams: `EDIT` badges
- Class C exams: `VIEW ONLY` badges ✅ (This is the fix - these should now appear)

### Scenario 2: Teacher with No Assignments
**Setup:**
- Teacher has no class assignments
- Teacher owns some exams (created by them)

**Expected Behavior:**
- **"Show All Exams"**: Shows all exams with appropriate badges
- **"Show Assigned Classes Only"**: Shows only exams they own (if any)

### Scenario 3: Admin User
**Setup:**
- Admin user (is_superuser=True)

**Expected Behavior:**
- **Both modes**: Shows all exams (admins bypass filtering)
- All exams show `ADMIN` badges

### Scenario 4: Teacher with Only VIEW Access
**Setup:**
- Teacher has only VIEW access to all their assigned classes
- Multiple exams in these classes

**Expected Behavior:**
- **"Show All Exams"**: Shows all exams
- **"Show Assigned Classes Only"**: Shows exams from assigned classes with `VIEW ONLY` badges ✅ (Bug fix)

**Before Fix**: No exams would show (bug)
**After Fix**: Exams show with `VIEW ONLY` badges

### Scenario 5: Mixed Ownership and Assignments
**Setup:**
- Teacher owns Exam X in Class A
- Teacher has VIEW access to Class B with Exam Y
- Teacher has FULL access to Class C with Exam Z

**Expected Behavior:**
- **"Show Assigned Classes Only"**: 
  - Exam X: `OWNER` badge (owned)
  - Exam Y: `VIEW ONLY` badge (VIEW access) ✅ (Bug fix)
  - Exam Z: `FULL ACCESS` badge (FULL access)

## Validation Checklist

### ✅ Frontend Behavior
- [ ] Toggle state persists across page reloads
- [ ] URL parameters update correctly (`assigned_only=true/false`)
- [ ] Tab navigation preserves filter state

### ✅ Backend Logic
- [ ] Filtering logic includes VIEW access levels
- [ ] Owner exams always appear regardless of filter
- [ ] Admin users bypass all filtering
- [ ] Permission badges are correctly assigned

### ✅ Edge Cases
- [ ] Empty class assignments (teacher has no classes)
- [ ] Program-level exams without specific class assignments
- [ ] Exams with no class codes assigned

### ✅ No Regressions
- [ ] "Show All Exams" mode unchanged
- [ ] Permission system unchanged (can_edit, can_delete, can_copy)
- [ ] Badge display unchanged
- [ ] Button functionality unchanged

## Expected Impact

### Positive Changes
1. **Semantic Correctness**: "Show Assigned Classes Only" now matches its meaning
2. **User Experience**: Teachers see all exams from their assigned classes, not just editable ones
3. **Information Access**: Teachers can view answer keys for classes they monitor (VIEW access)

### No Negative Impact
1. **Security**: No permission escalation (VIEW remains VIEW)
2. **Performance**: Same filtering logic, just broader criteria
3. **UI**: No interface changes required
4. **Data**: No database changes required

## Test Commands

```bash
# Test the fix with different user types
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from primepath_routinetest.services.exam_service import ExamService
>>> User = get_user_model()

# Test with teacher having VIEW access
>>> teacher = User.objects.get(username='teacher_with_view_access')
>>> assignments = ExamService.get_teacher_assignments(teacher)
>>> print("Teacher assignments:", assignments)

# Test filtering
>>> from primepath_routinetest.models import Exam
>>> exams = Exam.objects.all()[:5]
>>> result = ExamService.organize_exams_hierarchically(exams, teacher, filter_assigned_only=True)
>>> print("Filtered exams:", len([e for classes in result.values() for class_exams in classes.values() for e in class_exams]))
```

## Success Criteria

The fix is successful when:
1. ✅ "Show Assigned Classes Only" includes exams from ALL assigned classes (FULL, CO_TEACHER, VIEW)
2. ✅ VIEW ONLY badge exams appear in "Assigned Only" mode 
3. ✅ No regression in existing functionality
4. ✅ Permission system remains intact
5. ✅ Performance is not degraded