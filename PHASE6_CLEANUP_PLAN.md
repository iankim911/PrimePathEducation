# Phase 6: Database & Organization Cleanup Plan
**Status**: Ready to Execute
**Impact**: High - Removes test data pollution from database and organizes files

---

## 🎯 What Phase 6 Will Do

### 1. Database Cleanup

#### Test SubPrograms (7 items)
Will delete these test subprograms that are polluting the curriculum:
- `[INACTIVE] Test SubProgram`
- `[INACTIVE] SHORT Answer Test SubProgram`
- `[INACTIVE] Comprehensive Test SubProgram`
- `[INACTIVE] Management Test SubProgram`
- `[INACTIVE] SHORT Display Test SubProgram`
- `[INACTIVE] Submit Test SubProgram`
- `[INACTIVE] Final Test SubProgram`

**Impact**: These were causing pollution in the exam dropdown and curriculum structure
**Safety**: All marked as INACTIVE, no related exams

#### Test Student Sessions (3 items)
Will delete these test sessions:
1. **test 1** - [PT] PHONICS all levels (40 answers)
2. **test 1** - [PT]_CORE_SIGMA_Lv2 (10 answers, completed)
3. **Test Student** - [PT]_CORE_ELITE_Lv1 (0 answers)

**Impact**: Removes test data from production database
**Safety**: Only affects sessions with "test" in the name

---

### 2. File Organization (76 files)

Will organize orphaned test files into proper structure:
```
tests/
├── integration/     (test_*.py files)
├── archive/        (comprehensive_*, deep_*, ultra_* files)
├── utils/          (check_*, verify_*, analyze_* files)
└── fixtures/       (data files)
```

**Files to move**: 76 test/utility files currently in root directory

---

### 3. Directory Cleanup (6 empty directories)

Will remove empty directories:
- `static/js/components`
- `placement_test/managementcommands`
- `templates/registration`
- `templates/components/shared`
- `templates/components/common`
- `services/utils`

---

## ✅ Verified Safe

### Model Relationships Preserved
- ✅ 6 Exams remain functional
- ✅ All Exam → CurriculumLevel relationships intact
- ✅ All Question → Exam relationships preserved
- ✅ Valid student sessions untouched

### Inter-App Dependencies
- ✅ core ↔ placement_test bidirectional dependency preserved
- ✅ api → placement_test, core dependencies intact
- ✅ common → core dependency preserved

---

## 🔍 Console Logging Added

Comprehensive JavaScript monitoring will track:
- Database cleanup actions
- File organization operations
- Feature verification after cleanup
- Real-time error detection

---

## 📊 Expected Results

### Before Cleanup
- 7 test subprograms polluting curriculum
- 3 test sessions in database
- 76 orphaned test files in root
- 6 empty directories

### After Cleanup
- ✅ Clean curriculum (only real 44 levels)
- ✅ No test data in production database
- ✅ Organized test file structure
- ✅ Cleaner directory tree

---

## ⚠️ Important Notes

1. **All changes are reversible** via git
2. **Database changes** affect test data only
3. **No production data** will be touched
4. **All features** remain functional

---

## 🚀 Ready to Execute?

To run Phase 6 cleanup:
```bash
# Execute the cleanup (not dry run)
python phase6_cleanup_implementation.py --execute
```

Or continue with dry run to review:
```bash
# Dry run (default)
python phase6_cleanup_implementation.py
```

---

## Next Steps After Phase 6

1. **Phase 7**: Code Quality & Standards
   - Remove commented code
   - Clean unused imports
   - Standardize naming

2. **Phase 8**: Configuration Cleanup
   - Review settings files
   - Consolidate environment variables
   - Update .gitignore

3. **Phase 9**: Documentation Update
   - Update README
   - Document new structure
   - Create developer guide