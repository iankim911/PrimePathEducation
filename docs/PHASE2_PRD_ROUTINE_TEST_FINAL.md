# Product Requirements Document (PRD) - FINAL
# PrimePath Routine Test System - Phase 2

**Version:** 2.0 FINAL  
**Date:** August 15, 2025  
**Status:** Ready for Implementation

---

## 1. EXECUTIVE SUMMARY

### 1.1 Product Overview
PrimePath Routine Test System is a comprehensive assessment platform for regular student evaluation through Review Tests (monthly) and Quarterly Exams, with progress tracking throughout the academic year.

### 1.2 Core Distinction from Phase 1
- **Phase 1 (Placement Test)**: One-time assessment, no student accounts, single admin
- **Phase 2 (Routine Test)**: Recurring tests, student accounts required, multi-tier access (Admin/Teacher/Student)

### 1.3 Scope Decisions
- **IN SCOPE**: PDF exam uploads, Review Tests, Quarterly Exams, basic analytics
- **OUT OF SCOPE (Phase 3)**: Question bank, pop quizzes, practice tests, parent portal, advanced analytics dashboard

---

## 2. SYSTEM ARCHITECTURE

### 2.1 Module Independence
```
Phase 1 (Placement Test)          Phase 2 (Routine Test)
├── Separate Database             ├── Separate Database
├── Single Admin                  ├── Multi-tier Access
├── No Student Accounts           ├── Student Accounts Required
└── Own Exam Repository           └── Teacher Libraries + School Library
```

### 2.2 User Hierarchy & Permissions

| Role | Capabilities |
|------|-------------|
| **Admin** | • All teacher capabilities<br>• Assign teachers to classes<br>• Override any teacher decision<br>• Access all data system-wide<br>• View/edit all exams |
| **Teacher** | • Upload exams to personal library<br>• View school-wide library<br>• Manage assigned classes only<br>• Transfer students FROM assigned classes<br>• Schedule and control test release |
| **Student** | • Self-register account<br>• Take assigned tests<br>• View results (when released)<br>• Track own progress |

---

## 3. CORE FEATURES - DETAILED SPECIFICATIONS

### 3.1 Upload Exams Module

#### Workflow (Step-by-Step)
1. **Upload Files**
   - PDF exam file (required)
   - Audio files (optional, for listening sections)

2. **Select Test Type**
   - **Review Test** → Select Month (January-December dropdown)
   - **Quarterly Exam** → Select Quarter (Q1-Q4 dropdown)

3. **Select Curriculum Level**
   ```
   Program → SubProgram → Level
   
   CORE     → Phonics/Sigma/Elite/Pro → Level 1-3
   ASCENT   → Nova/Drive/Pro → Level 1-3  
   EDGE     → Spark/Rise/Pursuit/Pro → Level 1-3
   PINNACLE → Vision/Endeavor/Pro → Level 1-2
   ```

4. **Select Target Class**
   - Dropdown shows only teacher's assigned classes
   - Admin sees all classes

5. **Automatic Naming**
   ```
   Format: [TYPE | PERIOD] - PROGRAM SubProgram Level X - ClassCode_CustomDescription
   Example: [REVIEW | March] - CORE Elite Level 2 - CLS101_Midterm
   ```

6. **Add Custom Description**
   - Optional field
   - Appended after underscore in exam name
   - This is the ONLY part teachers can edit later

7. **Configure Exam Settings**
   - Duration (minutes)
   - Number of questions
   - MCQ options (3, 4, or 5 choices)

#### Key Features (Inherited from Phase 1)
- PDF viewer with rotation controls
- Audio file upload and management
- All existing upload functionality from Phase 1

---

### 3.2 Assign Answers Module

#### Interface (Exactly like Phase 1 "Manage Exams")
- Modular card view of all exams
- PDF preview with page navigation
- Audio assignment to specific questions
- Multiple answer formats:
  - Multiple choice (A-E)
  - Short answer text
  - Numeric responses
  - True/False

#### Key Differences from Phase 1
- **Edit Restriction**: Can only edit custom description, not auto-generated name parts
- **Library Views**:
  - "My Exams" tab - Teacher's own uploads
  - "School Library" tab - All teachers' uploads (view-only)
- **Delete**: Requires confirmation, moves to archive

#### Manual Grade Override
- Teachers can override auto-graded answers
- Add comments per exam (not per question)
- Batch score adjustments

---

### 3.3 Class Management Module

#### Main View - Class Cards
Each card shows:
```
┌─────────────────────────┐
│ Class: CLS101           │
│ Students: 25            │
│ Avg Score: 85%          │
│ Pending Tests: 2        │
│ [Enter Class]           │
└─────────────────────────┘
```

#### Inside Class View - Split Layout

**Left Panel (60%) - Student List**
```
Student Cards showing:
- Name & Student ID
- Last test score
- Performance trend (↑/↓/→)
- Status (Active/Inactive)

Actions:
- Add student (by ID)
- Remove student
- Transfer to another class
```

**Right Panel (40%) - Test Management**

Two tabs: **Review Tests** | **Quarterly Exams**

**Review Tests Tab Structure:**
```
January:  [No exam assigned]        [+ Add Exam Pool]
February: [3 exams in pool]         [Start] [Edit Pool]
March:    [Test Active - 20/25 completed] [View Results]
...
December: [No exam assigned]        [+ Add Exam Pool]
```

**Quarterly Exams Tab Structure:**
```
Q1: [2 exams in pool]    [Schedule: Mar 15-20] [Start]
Q2: [No exam assigned]   [+ Add Exam Pool]
Q3: [No exam assigned]   [+ Add Exam Pool]
Q4: [No exam assigned]   [+ Add Exam Pool]
```

#### Test Pool System
- Teacher selects multiple exams for a time period
- System randomly assigns ONE exam to each student from the pool
- Different students get different exams (prevents cheating)
- Teacher can see which student got which exam

#### Test Scheduling
1. **Set Availability Window**
   - Start date/time
   - End date/time
   - Exam appears in student portal only during this window

2. **Exam Duration**
   - Once student starts, timer begins
   - Based on exam's configured duration
   - Cannot pause/resume

3. **Result Release**
   - Teacher-controlled
   - Can release immediately or hold for review

---

### 3.4 Student Interface

#### Student Dashboard
```
Welcome, [Student Name]

Active Tests:
┌──────────────────────────────────┐
│ March Review Test                │
│ Available: Mar 10-15             │
│ Duration: 60 min                 │
│ [Start Test]                     │
└──────────────────────────────────┘

Recent Results (if released):
- February Review: 85/100
- Q1 Exam: 92/100

Progress: [Simple chart showing trend]
```

#### Test Taking Interface
- Identical to Phase 1 placement test interface
- Timer (cannot pause)
- Question navigation
- Audio player for listening sections
- Auto-submit when time expires
- NO save and resume capability

---

## 4. USER WORKFLOWS

### 4.1 Teacher Workflow - Exam Creation & Assignment

```
1. Login
2. Upload Exam → Select Type (Review/Quarterly) → Select Period → Map to Curriculum → Select Class
3. Assign Answers (same as Phase 1)
4. Go to Class Management
5. Select Class
6. Choose Review Tests or Quarterly Exams tab
7. Add exams to pool for specific period
8. Set availability window
9. Activate test
10. Review results & release to students
```

### 4.2 Student Workflow - Registration & Test Taking

```
1. Self-register account
2. Share Student ID with teacher
3. Teacher adds to class
4. Login → See available tests
5. Start test during availability window
6. Complete test (no pause/resume)
7. Auto-submit or manual submit
8. Wait for teacher to release results
9. View results and feedback
```

### 4.3 Admin Workflow

```
Has all teacher capabilities PLUS:
- Manage Teachers → Assign to classes
- Access any class
- Override any setting
- View all data
```

---

## 5. TECHNICAL SPECIFICATIONS

### 5.1 Authentication
- **Students**: Self-registration with email/phone
- **OAuth Integration**: Google, Kakao (future)
- **Simple credentials**: Email + Password

### 5.2 Data Management

#### Exam Library Structure
```
School Database
├── Teacher Libraries (private)
│   ├── Teacher A exams
│   ├── Teacher B exams
│   └── Teacher C exams
└── School Library (shared, read-only)
    └── All teacher uploads visible
```

#### Test Attempts
- **Review Tests**: Single attempt (teacher can grant retry)
- **Quarterly Exams**: Single attempt only
- All attempts logged with timestamps

### 5.3 Key Technical Decisions
- **Database**: Completely separate from Phase 1
- **File Storage**: Separate folder structure
- **Shared Elements**: Only curriculum structure (reference data)
- **No Integration**: Phase 1 and Phase 2 operate independently

---

## 6. WHAT WE'RE NOT BUILDING (Deferred to Phase 3)

### Explicitly Excluded Features
1. **Question Bank** - Only PDF uploads for now
2. **Advanced Analytics Dashboard** - Basic stats only in class view
3. **Parent Portal** - No parent access
4. **Practice Tests/Pop Quizzes** - Only Review & Quarterly
5. **Save & Resume** - Tests must be completed in one session
6. **Performance Categories** - No automatic categorization by skill
7. **Cross-class Analytics** - Teachers see only their classes

---

## 7. IMPLEMENTATION PHASES

### Phase 2.1: Foundation (Week 1-2)
- [x] Copy Phase 1 codebase
- [ ] Rename placement_test → routine_test
- [ ] Add User model with roles (Admin/Teacher/Student)
- [ ] Student self-registration system
- [ ] Teacher-Class assignment structure

### Phase 2.2: Core Features (Week 3-4)
- [ ] Upload Exams with test type selection
- [ ] Exam library (personal + school-wide view)
- [ ] Assign Answers (reuse Phase 1 code)
- [ ] Class Management UI
- [ ] Test pool system

### Phase 2.3: Test Management (Week 5-6)
- [ ] Scheduling system
- [ ] Random exam assignment from pool
- [ ] Student test-taking (reuse Phase 1)
- [ ] Result management
- [ ] Teacher-controlled result release

### Phase 2.4: Polish (Week 7-8)
- [ ] Manual grade override
- [ ] Comments on exams
- [ ] Basic progress tracking
- [ ] Testing and bug fixes

---

## 8. SUCCESS METRICS

### Must Achieve
- System handles 500+ concurrent test takers
- 95% code reuse from Phase 1 upload/test modules
- Zero data leakage between Phase 1 and Phase 2
- Teachers can manage 5+ classes efficiently

### Nice to Have
- 90% student test completion rate
- <2 second page loads
- Positive teacher feedback on ease of use

---

## 9. CRITICAL DECISIONS SUMMARY

| Decision Point | Final Decision |
|----------------|----------------|
| Test Creation | PDF upload only (no question bank) |
| Library Access | Personal library + school-wide view |
| Test Types | Review (monthly) + Quarterly only |
| Student Registration | Self-register, teacher adds by ID |
| Class Transfers | Teachers can transfer OUT only |
| Test Assignment | Pool system with random selection |
| Scheduling | Teacher sets window, strict enforcement |
| Results Release | Teacher-controlled |
| Attempts | Single attempt (teacher can grant retry) |
| Parent Access | Not included |
| Analytics | Basic only in class view |

---

## 10. OPEN QUESTIONS RESOLVED

All clarification questions have been answered and incorporated into this document.

---

## 11. NEXT STEPS

1. **Immediate Actions**
   - Set up PrimePath_RoutineTest folder
   - Copy Phase 1 code
   - Create new Django apps for routine_test

2. **First Sprint Goals**
   - User authentication system
   - Student registration
   - Basic class structure

3. **Validation Needed**
   - Review this PRD for final approval
   - Confirm 8-week timeline is acceptable
   - Approve simplified feature set

---

## APPENDICES

### A. Reusable Components from Phase 1 (95% reuse)
- Entire Upload Exam interface
- Manage Exams → Assign Answers interface  
- PDF viewer with rotation
- Audio player and assignment
- Timer system
- Question display components
- Answer input methods
- Test-taking interface

### B. New Components for Phase 2
- User registration system
- Role-based access control
- Class management interface
- Test pool & random assignment
- Scheduling system
- Result release control
- Basic progress display

### C. File Naming Examples
```
Review Tests:
[REVIEW | January] - CORE Phonics Level 1 - CLS101_Vocabulary
[REVIEW | March] - EDGE Pro Level 3 - ADV202_Grammar

Quarterly Exams:
[QUARTERLY | Q1] - PINNACLE Vision Level 2 - HONORS_Final
[QUARTERLY | Q3] - ASCENT Nova Level 1 - BEG101_Midterm
```

---

**Document History**
- v1.0 - Initial draft (August 13, 2025)
- v2.0 - Final version with all clarifications (August 15, 2025)

**Approval**
This PRD is ready for implementation based on clarifications provided.

---