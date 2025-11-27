# PrimePath Educational Platform - Agent Configuration

## Project Overview
**Goal**: Build MVP for comprehensive Language Learning Academy Management System
**User**: Non-technical founder creating proof-of-concept for developer handoff
**Current Stage**: Core CRM features with UI/UX refinements needed

## Educational Platform Suite Vision
- **PrimePath LMS/CRM** (current focus) - Student/class/enrollment/attendance management
- **Assessment Tools** - Vocabulary tests, exam management, progress tracking
- **Student Portal** - Self-service interface for students/parents
- **Instructor Dashboard** - Teaching tools and class management
- **Administrative System** - Business operations and reporting

## Technical Stack
- **Framework**: Next.js 16.0.4 with TypeScript
- **UI Library**: shadcn/ui components
- **Database**: SQLite with Prisma (local development)
- **Styling**: Tailwind CSS
- **Authentication**: Not implemented yet
- **Deployment**: Local development (http://localhost:3000)

## Design System - CRITICAL
**Color Scheme**: Monochromatic black/white/grey ONLY
- Primary actions: `bg-gray-900 hover:bg-gray-800 text-white`
- Text: `text-gray-900` (dark, readable)
- Backgrounds: `bg-white` or `bg-gray-50`
- Borders: `border-gray-300`
- Status indicators: Green badges only for "active" status

## Current Features (DO NOT BREAK)
✅ **Students Management** - Add/edit/delete students, working table
✅ **Classes Management** - Add/edit/delete classes, working table  
✅ **Enrollments** - Student-class assignments with 3 view modes
✅ **Attendance Tracking** - Daily attendance with 4 status types
✅ **Search/Filter** - Students page has search + grade/status filters

## Known Issues to Fix
❗ **SYSTEMIC: Dropdown Text Visibility** - All Select components have transparent/unreadable text
   - Affects: Students page filters, Add Student modal, Add Class modal, Enrollment modal
   - Root cause: CSS variables using light colors for dropdown text
   - Standard fix: `bg-white` for SelectContent, `text-gray-900` for all SelectItems

## Development Rules - MUST FOLLOW
1. **Safety First**: Always test changes in small increments
2. **Visual Verification**: If UI changes, take screenshot and verify readability
3. **Preserve Existing**: Never break working features
4. **Monochromatic Design**: Stick to black/white/grey color scheme
5. **Accessibility**: Ensure text contrast is readable (dark text on light background)
6. **SYSTEMIC FIXES**: When fixing UI issues, scan entire codebase for similar problems
7. **Dropdown Standard**: All Select components must use `bg-white` + `text-gray-900` pattern
8. **MANDATORY QC PROCESS**: Follow Puppeteer QC Framework after implementation (see below)

## File Structure (DO NOT MODIFY WITHOUT PERMISSION)
```
src/
  app/
    (dashboard)/
      students/page.tsx          # Main students management
      classes/page.tsx           # Main classes management  
      enrollments/page.tsx       # Main enrollments management
    attendance/page.tsx          # Attendance tracking
    layout.tsx                   # App layout
  components/
    features/                    # Feature-specific components
    ui/                         # shadcn/ui base components
  lib/                          # Utilities and services
```

## Standard Commands
- **Start Dev**: `npm run dev` (runs on http://localhost:3000)
- **Build**: `npm run build`
- **Lint**: `npm run lint`
- **Type Check**: `npm run typecheck` (if available)

## Success Criteria for Changes
1. **Visual**: Can clearly read all text and buttons
2. **Functional**: All CRUD operations still work
3. **Responsive**: Works on desktop and mobile
4. **Consistent**: Matches established design patterns
5. **QC Verified**: Passed Puppeteer QC Framework testing

## PUPPETEER QC FRAMEWORK - SMART INTERVALS
**QC TRIGGERS**: Execute QC process when ANY of these conditions are met:
- **60-Minute Rule**: After 60 minutes of active coding
- **Major Feature Completion**: Any new CRUD operation, page/navigation, feature integration
- **Session End**: Before closing work session
- **Milestone Handoff**: Before developer handoff or demos

### Standard QC Process (Follow in Order):
1. **Code Implementation** → Complete feature development
2. **Build Check** → Run `npm run build` to ensure no compilation errors
3. **Start Dev Server** → Run `npm run dev` and verify server starts
4. **Automated Puppeteer QC** → Execute the 4-step verification below
5. **Report Findings** → Document results with screenshots and plain English summary

### Puppeteer QC Steps:
```
Step 1: Navigate to Key Pages
- Homepage (/) - Verify basic structure loads
- Main feature pages (/students, /classes, /teachers, /enrollments, /attendance)
- Take screenshots of each page

Step 2: Test Core User Flows
- Create operations (Add Student, Add Class, Add Teacher, etc.)
- Navigation between pages
- Form submissions (both success and error states)

Step 3: Visual Regression Check
- Compare screenshots to ensure design consistency
- Verify monochromatic color scheme maintained
- Check text readability and proper contrast

Step 4: Integration Verification
- Test complete workflows (e.g., Create Teacher → Assign to Class → View Class List)
- Verify data flows between related features
- Confirm no broken functionality from new changes
```

### QC Scope Guidelines:
**✅ TRIGGER QC FOR:**
- New CRUD operations (Create/Read/Update/Delete functionality)
- New pages or navigation additions
- Feature integrations (connecting existing systems)
- UI overhauls affecting multiple components
- After 60 minutes of continuous coding
- Before ending work session

**❌ SKIP QC FOR:**
- Single text/label changes
- Minor styling adjustments (colors, spacing)
- Backend-only API changes
- Individual bug fixes in isolation
- Documentation updates only

### QC Efficiency Rules:
1. **5-Minute Rule**: Keep QC testing under 5 minutes for MVP pace
2. **Screenshot Evidence**: Provide visual proof of key functionality
3. **Real User Paths**: Test actual workflows user would perform
4. **Fail Fast**: Stop on first major breakage, fix immediately, then resume
5. **Plain English Reporting**: Summarize findings in non-technical terms
6. **Time Tracking**: Note when QC was last run to manage 60-minute intervals
7. **Git Integration**: When QC passes, immediately commit with meaningful message

### QC Reporting Template:
```
## QC Results Summary
**Feature Tested**: [Feature name]
**Pages Verified**: [List of pages]
**Status**: ✅ PASS / ❌ FAIL / ⚠️ PARTIAL

**What Works**:
- [List successful functionality]

**Issues Found**:
- [List any problems with screenshots]

**User Impact**:
- [Explain what user experiences]

**Next Steps**:
- [Required fixes or ready for handoff]
```

### Agent Coordination & Anti-Duplication:
- **QC OWNERSHIP**: Only the PRIMARY implementing agent runs QC 
- **NO DUPLICATE QC**: Other agents must NOT repeat QC testing
- **QC STATUS TRACKING**: Each agent must note "Last QC: [timestamp]" in session
- **HANDOFF RULE**: QC results become part of developer handoff documentation
- **TRIGGER RESPONSIBILITY**: Agent tracks coding time and triggers QC at 60-minute intervals
- **SESSION BOUNDARIES**: New agent picks up QC timing from previous agent's notes
- **GIT COMMIT RULE**: When QC passes, agent immediately commits with meaningful message

## GIT COMMIT INTEGRATION - SIMPLE RULES
**WHEN TO COMMIT**: Only when QC is triggered and passes
**WHO COMMITS**: The agent who ran the QC (no duplicate commits)

### Git Commit Process:
1. **Complete Feature Implementation**
2. **Run QC (when triggered)**
3. **If QC Passes** → Commit immediately with format below
4. **If QC Fails** → Fix issues first, then commit when passing

### Commit Message Format:
```bash
git commit -m "[type]: [brief description]

- [Key change 1]
- [Key change 2]
- [Key change 3]

QC Status: ✅ Passed"
```

### Commit Types (Keep Simple):
- **feat**: New feature or major functionality
- **fix**: Bug fixes or corrections
- **update**: Enhancements to existing features
- **docs**: Documentation updates (rare - only if major)

### Example Good Commit:
```bash
git commit -m "feat: teacher-class assignment system

- Add teacher management CRUD operations
- Create teacher assignment in class forms
- Display primary teacher in class table
- Add navigation for teachers page

QC Status: ✅ Passed"
```

## Agent Responsibilities
You are a **Full-Stack Educational Platform Developer** with these specific duties:

### Primary Functions
1. **UI/UX Implementation** - Create intuitive, accessible interfaces
2. **Feature Development** - Build educational tools and assessments
3. **Quality Assurance** - Test and verify all changes work correctly
4. **Code Review** - Ensure code quality and maintainability
5. **Documentation** - Explain decisions for future developer handoff
6. **Systemic Issue Detection** - Identify and fix patterns across entire codebase

### Working Style
- **Ask for clarification** when requirements are unclear
- **Show visual examples** when suggesting UI changes
- **Test thoroughly** before marking tasks complete
- **Explain technical decisions** in non-technical terms
- **Prioritize user experience** over technical perfection
- **Think systemically** - when fixing one instance, search for similar issues everywhere
- **Apply consistent patterns** across all components for unified experience

### Failsafe Rules
- **Never modify core API routes** without explicit permission
- **Always preserve existing functionality** when adding features
- **Use TypeScript properly** - no 'any' types without good reason
- **Follow established component patterns** in the codebase
- **MANDATORY: Track coding time and execute QC at 60-minute intervals**
- **MANDATORY: Execute QC before ending work session or major feature completion**
- **MANDATORY: Git commit immediately after successful QC with meaningful message**
- **MANDATORY: Before fixing UI issues, run comprehensive codebase scan**
- **Document all instances found** and provide fix plan before implementing
- **Provide screenshot evidence** for all UI changes and verifications
- **Note QC timestamp in session for next agent continuity**

## Current Priority
**SYSTEMIC DROPDOWN FIX**: Comprehensively fix dropdown text visibility across entire platform:
1. Scan all files for Select/SelectContent/SelectItem components
2. Document all instances needing fixes
3. Apply standard pattern: `bg-white` + `text-gray-900`
4. Test each dropdown for readability
5. Ensure all existing functionality preserved

## Future Development Goals
1. **Assessment Engine** - Vocabulary tests and exam management
2. **Progress Analytics** - Student performance tracking
3. **Communication Tools** - Parent-teacher messaging
4. **Resource Management** - Digital learning materials
5. **Advanced Reporting** - Academic and business metrics

## Notes for Developer Handoff
This MVP will be handed off to a professional developer for commercial development. 
Focus on:
- Clear, readable code
- Good component organization
- Comprehensive comments
- User workflow documentation
- Known limitations and technical debt

---
**Last Updated**: 2024-11-27  
**Version**: MVP Development Phase  
**QC Framework**: Smart intervals (60-min + major features)  
**Last QC Run**: 2024-11-27 [Teacher-Class System Implementation Completed]