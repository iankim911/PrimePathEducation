# PrimePath LMS – Product Requirements & Development Intent

## 1. Context & Development Philosophy

### 1.1 Who I Am & How I Work
- **Role**: Non-technical Product Manager / Founder running an English academy (hagwon) in Korea
- **Domain Expertise**: 
  - Academy enrollment, class management, testing, parent communication
  - Pain points around placement tests, test management, vocab quizzes, attendance
- **Development Mode**: Black Box Mode
  - AI agent handles all technical implementation
  - No manual debugging or syntax fixes
  - Clean, maintainable architecture

### 1.2 Core Objectives
1. Build a working MVP for immediate use at my academy
2. Gain practical understanding of product, data model, and architecture
3. Create a clean, well-documented codebase ready for professional developers

---

## 2. Product Suite Overview

PrimePath LMS is an operations system for English academies, starting as single-tenant for my academy, evolving to multi-tenant SaaS.

### 2.1 Complete Product Vision

#### Module 1: CRM Lite (Foundation Layer)
- **Students**: Master records (name, grade, school, status, parent info)
- **Classes**: Class entities (name, level, grade, schedule)
- **Enrollments**: Student-class mappings with dates and status
- *This is the base layer - all other modules depend on this*

#### Module 2: Attendance
- Per-class, per-student, per-date records
- Status: present, absent, late, excused
- Unique record per (academy, class, student, date)

#### Module 3: Test Management (Generic Exam Engine)
- Supports all exam types (vocab, placement, unit tests, finals)
- Core entities:
  - Exam definitions
  - Questions
  - Student attempts
  - Answers (per question per attempt)

#### Module 4: Vocabulary Exam Module
- Teacher features:
  - Upload vocab lists (word, meaning, example)
  - Assign to classes/students
- Student features:
  - Take online vocab tests
- System:
  - Store answers, mark correct/incorrect
- *MVP scope: No adaptive learning or AI generation*

#### Module 5: Level Test / Placement Test
- Placement test templates
- Link-based access for prospective students
- Rule-based class recommendations
  - Example: "Grade 5, score > 80 → Class A"

#### Module 6: Reporting & Analytics (Future)
- Attendance summaries
- Test performance trends
- Risk indicators

#### Module 7: Notifications & Integrations (Future)
- KakaoTalk notifications
- Parent/staff reports

#### Module 8: Multi-Tenant SaaS (Future)
- Multiple academies on same platform
- Logical isolation via academy_id
- Central admin controls

---

## 3. MVP Roadmap

### Phase 1: CRM Lite + Basic Attendance ✅ (Current Focus)
**Deliverables:**
- Student CRUD operations
- Class management with schedules
- Student-class enrollments
- Attendance marking (present/absent/late/excused)

**Value:** Complete workflow for daily teacher/admin operations

### Phase 2: Generic Test Management Core
**Deliverables:**
- Core tables: exams, questions, attempts, answers
- Teacher flow: create and assign exams
- Student flow: take exams

### Phase 3: Apply Test Engine to Use Cases
1. Vocabulary Exam implementation
2. Placement Test implementation

### Not in MVP 🚫
- Adaptive learning
- Advanced analytics/dashboards
- AI-based content generation
- Complex onboarding flows
- Full student/parent portals

---

## 4. Technical Architecture

### 4.1 Tech Stack
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Library**: shadcn/ui + Lucide icons
- **Database**: Supabase (PostgreSQL)
- **Development**: AI-assisted with Claude

### 4.2 Database Standards

#### Required Fields (All Business Tables)
```sql
academy_id UUID NOT NULL REFERENCES academies(id),
is_active  BOOLEAN NOT NULL DEFAULT TRUE,
created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
deleted_at TIMESTAMPTZ
```

#### Primary Keys
- Always: `UUID DEFAULT gen_random_uuid()`

#### Schema Location
- Canonical source: `db/schema.sql`

### 4.3 Code Structure

```
db/
  schema.sql

src/
  app/
    (dashboard)/
      layout.tsx
      students/
        page.tsx
      classes/
        page.tsx
      attendance/
        page.tsx
      exams/
        page.tsx
      vocab/
        page.tsx
    api/
      students/
        route.ts
      classes/
        route.ts
      attendance/
        route.ts
      exams/
        route.ts
      vocab/
        route.ts
  lib/
    supabaseClient.ts
    services/
      students.ts
      classes.ts
      enrollments.ts
      attendance.ts
      exams.ts
      vocab.ts
  components/
    layout/
      DashboardShell.tsx
    features/
      students/
        StudentsTable.tsx
      classes/
        ClassesTable.tsx
      attendance/
        AttendanceTable.tsx
      exams/
        ExamForm.tsx

project_rules.md
```

### 4.4 Layer Responsibilities

#### `src/lib/supabaseClient.ts`
- Single source for Supabase client creation
- No direct DB access elsewhere

#### `src/lib/services/*`
- All business/domain logic
- All database operations
- Always receives academyId
- Handles is_active/deleted_at filtering

#### `src/app/api/*/route.ts`
- Thin API controllers
- Parse inputs → call services → return JSON
- Never direct Supabase calls

#### `src/app/(dashboard)/*`
- Teacher/admin pages
- Server components preferred
- Fetch from `/api/*`
- No direct Supabase calls

#### `src/components/layout/*`
- Shared layout components

#### `src/components/features/<feature>/*`
- Feature-specific presentational components
- Props-based, no data fetching
- No business logic

#### `project_rules.md`
- Living document of:
  - Tech stack decisions
  - Data rules
  - Architecture patterns
  - Key conventions

### 4.5 Authentication Strategy
- **Not Priority 1**: Added after CRM Lite + attendance works
- **MVP Approach**: Hard-coded academyId/userId
- **Future**: Full auth with role-based access

---

## 5. Development Intent

### Why Building This Myself
1. **Grounded Understanding**: Know how data flows through student/class/enrollment/attendance/test operations
2. **Avoid Black Box**: Not throwing vague requirements at developers
3. **Clean Reference**: Modern LMS implementation for hagwons that developers can extend

### AI Agent Responsibilities
- Act as autonomous senior engineer
- Keep architecture simple, consistent, extendable
- Follow established patterns strictly
- Refactor when needed for maintainability
- Update project_rules.md with pattern evolution
- Handle all coding/debugging without manual intervention

---

## 6. Success Criteria

### MVP Success
- [ ] Teachers can manage students and classes
- [ ] Daily attendance workflow operational
- [ ] Basic test creation and taking functional
- [ ] Vocab exam workflow complete
- [ ] Placement test with recommendations working

### Architecture Success
- [ ] Clean separation of concerns
- [ ] Consistent patterns across modules
- [ ] Easy to understand for new developers
- [ ] Extensible without major refactoring
- [ ] Well-documented codebase

### Product Success
- [ ] Usable at my academy immediately
- [ ] Reduces operational friction
- [ ] Data model supports future features
- [ ] Ready for multi-tenant evolution

---

## 7. Implementation Guidelines

### When Building Features
1. Start with service layer logic
2. Create API routes as thin controllers
3. Build UI components last
4. Always include academy_id in queries
5. Use soft deletes (is_active/deleted_at)

### When Extending
1. Follow existing patterns exactly
2. Update project_rules.md if introducing new patterns
3. Keep components presentational
4. Services handle all business logic
5. APIs are just translators

### Quality Standards
- TypeScript strict mode
- No any types without justification
- Clear naming conventions
- Comprehensive error handling
- Meaningful commit messages

---

## 8. Current Status & Next Steps

### Completed
- Initial project setup
- Basic structure defined

### In Progress (Phase 1)
- [ ] Students management
- [ ] Classes management
- [ ] Enrollments
- [ ] Attendance marking

### Next Priority (Phase 2)
- [ ] Generic exam engine design
- [ ] Core exam tables
- [ ] Basic exam flows

### Future Phases
- [ ] Vocabulary exam implementation
- [ ] Placement test implementation
- [ ] Authentication system
- [ ] Multi-tenant support

---

*This document is the single source of truth for product requirements and development intent. It should be updated as the product evolves but core principles remain constant.*