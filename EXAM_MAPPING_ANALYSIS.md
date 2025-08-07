# Exam-to-Level Mapping Issue Analysis

## Date: August 8, 2025

## Problem Description
The Exam-to-Level Mapping page shows "0 of 0 levels have exams mapped" and the Curriculum Level and Mapped Exams sections are completely empty.

## Root Cause Analysis

### 1. Missing PRIME CORE Program
**CRITICAL ISSUE FOUND**: The PRIME CORE program is missing from the database!

#### Current Database State:
```
Programs: 3 (Should be 4)
- ASCENT (Grades 5-6) ✅
- EDGE (Grades 7-9) ✅  
- PINNACLE (Grades 10-12) ✅
- CORE (Grades 1-4) ❌ MISSING
```

#### Expected Programs (from PRD):
1. **PRIME CORE** (Grades 1-4) - MISSING
2. PRIME ASCENT (Grades 5-6) - Exists
3. PRIME EDGE (Grades 7-9) - Exists
4. PRIME PINNACLE (Grades 10-12) - Exists

### 2. Incomplete SubPrograms
Only 11 SubPrograms exist, but should have more based on PRD structure:

#### Missing CORE SubPrograms:
- CORE PHONICS
- CORE SIGMA
- CORE ELITE
- CORE PRO

### 3. Missing CurriculumLevels
Since CORE program is missing, all its curriculum levels (12 levels total) are also missing.

## Data Flow Analysis

### How the Page Works:
1. **View** (`core/views.py:exam_mapping`):
   - Fetches all Programs with related SubPrograms and Levels
   - Separates levels by program name (CORE, ASCENT, EDGE, PINNACLE)
   - Passes `core_levels`, `ascent_levels`, etc. to template

2. **Template** (`exam_mapping.html`):
   - Iterates through each program's levels
   - Shows "No curriculum levels found" if list is empty
   - The CORE section shows empty because `core_levels` list is empty

3. **Why CORE is Empty**:
   - The view correctly checks `if program.name == 'CORE'`
   - But no Program with name='CORE' exists in database
   - Therefore, `core_levels` remains empty list

## Setup Requirements

### From PRD (Section 4):
```
PRIME CORE (Grades 1–4):
- CORE PHONICS (3 levels)
- CORE SIGMA (3 levels)
- CORE ELITE (3 levels)
- CORE PRO (3 levels)
Total: 12 levels
```

### From README.md:
Setup instructions mention:
```bash
python manage.py loaddata curriculum_data.json
python manage.py populate_curriculum
```

### Fixture File Analysis:
The `curriculum_data.json` fixture file EXISTS and contains:
- Program with pk=1, name="CORE" (Lines 3-10)
- SubPrograms for CORE (Lines 42-77):
  - CORE PHONICS (pk=1)
  - CORE SIGMA (pk=2)
  - CORE ELITE (pk=3)
  - CORE PRO (pk=4)

## Why Data is Missing

### Hypothesis 1: Fixture Not Loaded
The `curriculum_data.json` fixture was never loaded into the database.

### Hypothesis 2: Data Was Deleted
The CORE program might have been deleted accidentally during development.

### Hypothesis 3: Migration Issue
A migration might have dropped or modified the CORE program data.

## Solution Steps

### Step 1: Load the Fixture Data
```bash
cd primepath_project
../venv/Scripts/python.exe manage.py loaddata core/fixtures/curriculum_data.json
```

### Step 2: Run populate_curriculum Command
```bash
../venv/Scripts/python.exe manage.py populate_curriculum
```

This will:
1. Create the CORE Program with its 4 SubPrograms
2. Generate 3 levels for each SubProgram (12 total for CORE)
3. Also ensure other programs have their levels

### Step 3: Verify Data
After loading, verify:
- 4 Programs should exist (CORE, ASCENT, EDGE, PINNACLE)
- Each program should have its SubPrograms
- Each SubProgram should have 3 CurriculumLevels

## Expected Result After Fix

The Exam-to-Level Mapping page should show:
- **PRIME CORE**: 12 levels (4 subprograms × 3 levels)
- **PRIME ASCENT**: 9 levels (3 subprograms × 3 levels)
- **PRIME EDGE**: 12 levels (4 subprograms × 3 levels)
- **PRIME PINNACLE**: 12 levels (4 subprograms × 3 levels)

Total: 45 curriculum levels across all programs

## Additional Notes

### Why This Happened:
1. The fixture file exists but wasn't loaded
2. The database only has partial data (3 of 4 programs)
3. This is a data initialization issue, not a code bug

### Prevention:
1. Add a check in views to show warning if programs are missing
2. Create a management command to verify curriculum data integrity
3. Add this to deployment checklist

## Conclusion

The Exam-to-Level Mapping page is functioning correctly from a code perspective. The issue is **missing data** in the database, specifically the entire PRIME CORE program and its associated subprograms and levels. Loading the existing fixture file should resolve this issue completely.