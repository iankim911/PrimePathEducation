# PrimePath Assessment Platform - Phase 2 PRD (v1.3 - Final)
## Monthly Review Tests & Quarterly Assessment Management for Existing Students

### Version 1.3 | Date: August 2025
*Complete specification with all stakeholder clarifications incorporated*

---

## 1. Executive Summary

Phase 2 extends the PrimePath Assessment Platform to support continuous assessment of **existing students** through monthly review tests and quarterly exams. This phase introduces multi-user authentication with social logins (Google, Kakao), role-based access control, comprehensive class management, and detailed test history tracking. The system is designed for internal use within a single school in Korea, serving approximately 400 students, with the primary goal of capturing academic performance data and running analytics to gain insights into student progress. This phase also establishes the foundation for future AI-driven personalized learning features.

## 2. Project Context & Objectives

### 2.1 Primary Objectives
1. Enable existing students to take monthly review tests and quarterly exams on laptops or tablets in classroom settings
2. Implement secure multi-user authentication with Google and Kakao social logins
3. Create a three-tier access system (Student → Teacher → Admin)
4. Build comprehensive class management capabilities for teachers and admin
5. Track and store complete student assessment history with detailed performance metrics
6. Establish data foundation for future AI-driven analytics and personalized learning

### 2.2 System Parameters
- **User Base:** ~400 students initially
- **Geography:** Single school in Korea (KST timezone)
- **Language:** Bilingual support (Korean/English) with UI toggle
- **Deployment:** Internal use only for academic performance tracking
- **Growth:** Minimal expected over 1-2 years
- **Purpose:** Capture student performance data and generate insights

## 3. User Management & Access Control

### 3.1 Three-Tier Access Structure

#### 3.1.1 Students (Tier 1) - View-Only Access
**Account Creation Process:**
- Self-registration via platform
- Login options: Google OAuth, Kakao Login, or Email/Password
- Username format: `firstname.lastname.numbers` (numbers added if duplicate)
- Minimum age: 7 years (parents can register on behalf)
- After registration, students provide their ID to teachers for class assignment

**Permissions:**
- Take assigned exams (monthly reviews and quarterly tests)
- View personal test history across all classes (including previous quarters)
- Access scores immediately after exam completion
- Submit tests early and modify answers until deadline
- Review own past answers and performance

**Restrictions:**
- View-only access (cannot modify any content)
- Cannot see other students' data
- No export capabilities
- No access to teacher/admin features

#### 3.1.2 Teachers (Tier 2) - Class Management Access
**Account Setup:**
- Created or approved by admin
- Login via Google OAuth, Kakao, or Email/Password
- Can be assigned to multiple classes by admin

**Core Permissions:**
- All student view permissions PLUS:
- Assign students to their classes (using student-provided IDs)
- Schedule and assign exams with specific deadlines
- Differentiate instruction by assigning different exams to specific students
- View all students across assigned classes in unified view
- Bulk assign same exam to entire class
- Export class data in CSV, PDF, or Excel formats
- Access performance reports for their students

**Restrictions:**
- Cannot create classes (admin only)
- Cannot override auto-graded scores
- Cannot assign themselves to classes (admin only)

#### 3.1.3 Admin (Tier 3) - Full System Control
**Account Structure:**
- Single shared account (one ID/password)
- Used by both director and system administrator
- No individual activity logging

**Full Permissions:**
- Complete system control
- Create and manage all classes
- Assign/reassign teachers to any classes
- Assign multiple teachers to same class
- Access all teacher functionalities
- System-wide data export and reporting
- Manage curriculum and exam mappings
- Handle teacher departures and reassignments

### 3.2 Authentication & Security

#### 3.2.1 Login Methods (Priority Order)
1. **Google OAuth 2.0** - Primary method for all users
2. **Kakao Login** - Secondary (popular in Korea)
3. **Email/Password** - Fallback with phone number recovery option

#### 3.2.2 Account Recovery
- Industry standard recovery via:
  - Registered email address
  - Registered phone number
  - Connected social accounts (Google/Kakao)
- Parents assist young students using child's credentials

#### 3.2.3 Session Management
- **Duration:** Persistent until manual logout
- **Concurrent Access:** Same account can login from multiple devices
- **Test Sessions:** Protected and maintained during active exams

#### 3.2.4 Compliance & Consent
- **Minimum Age:** 7 years
- **Consent Process:** Pop-up agreement required upon registration
- **AI Data Usage:** Consent embedded in agreement (not optional)
- **Privacy Compliance:** GDPR/COPPA considerations implemented
- **Parental Involvement:** Parents can register on behalf of children

## 4. Class Management System

### 4.1 Class Structure & Organization

#### 4.1.1 Hierarchy
```
Academic Structure:
└── Classes (Created by Admin)
    ├── Class Name: Free-format (teacher's choice, internal convention)
    ├── Class Size: Maximum 20 students
    ├── Teachers: Multiple allowed (admin-assigned)
    ├── Students: Mixed curriculum levels supported
    ├── Curriculum Levels: Can have multiple from 44 existing levels
    ├── Academic Period: Quarterly-based
    └── Assigned Exams: Review tests and quarterly exams
```

#### 4.1.2 Key Characteristics
- **Flexible Naming:** Teachers choose names (internal convention exists)
- **Mixed-Ability Support:** Single class can contain students at different curriculum levels
- **Quarterly Lifecycle:** Classes end each quarter, requiring manual reassignment
- **Multiple Enrollment:** Students can be in multiple classes for same level
- **Historical Continuity:** Students maintain access to all previous class tests

### 4.2 Operational Workflows

#### 4.2.1 Admin Workflows
- Create new classes at start of each quarter
- Assign one or more teachers to each class
- Handle teacher transitions (reassign classes when teachers leave)
- Manage overall class structure and organization

#### 4.2.2 Teacher Workflows
- Receive student IDs from students who self-registered
- Add students to assigned classes
- Schedule exams with specific completion deadlines
- Assign different exams to different students (differentiation)
- Monitor student progress across all assigned classes
- Export performance data for reporting

#### 4.2.3 Student Journey
1. Self-register on platform (Google/Kakao/Email)
2. Receive unique ID
3. Provide ID to teacher
4. Get assigned to appropriate class(es)
5. Access and complete assigned tests
6. View scores immediately
7. Continue to new classes each quarter

### 4.3 Quarterly Transitions
- **Process:** Manual reassignment required every quarter
- **Class Data:** Classes end but historical data preserved
- **Student Records:** All test history follows student ID
- **Continuity:** Students can access previous quarter's tests and scores

## 5. Exam Management System

### 5.1 Exam Types & Structure

#### 5.1.1 Monthly Review Tests
- **Frequency:** 3-4 per quarter per curriculum level
- **Purpose:** Regular assessment and practice
- **Upload:** Separate upload category from quarterly exams
- **Assignment:** Same mechanism as quarterly exams

#### 5.1.2 Quarterly Exams
- **Frequency:** 1 per quarter per curriculum level
- **Purpose:** Comprehensive assessment
- **Weight:** Major assessment for the quarter
- **Upload:** Distinct category in exam management

#### 5.1.3 Exam Matrix Organization
```
For each of 44 Curriculum Levels:
└── Year (e.g., 2025)
    └── Quarter (Q1, Q2, Q3, Q4)
        ├── Review Test 1 (PDF)
        ├── Review Test 2 (PDF)
        ├── Review Test 3 (PDF)
        ├── Review Test 4 (PDF, if applicable)
        └── Quarterly Exam (PDF)
```

### 5.2 Content Specifications

#### 5.2.1 Question Types (Same as Placement Tests)
- Multiple choice questions
- Short answer questions
- Audio-based questions (listening comprehension)
- Speaking test placeholders (marked for manual grading)

#### 5.2.2 Content Management
- **Storage:** Questions remain in PDF format
- **Answer Keys:** Manually entered through interface
- **Version Control:** Maintained for all uploaded PDFs
- **Audio Files:** Supported for listening sections
- **Future Expansion:** Foundation for question bank (AI features)

### 5.3 Test Assignment & Administration

#### 5.3.1 Assignment Process
1. Teacher selects exam from uploaded content
2. Sets specific deadline (date and time, e.g., "Dec 15, 3:00 PM")
3. Chooses assignment method:
   - Bulk: Assign to entire class
   - Individual: Assign different exams to specific students
4. Students see assigned tests in dashboard

#### 5.3.2 Test-Taking Rules
- **Deadline Type:** Specific datetime with hard cutoff
- **Early Submission:** Allowed, with ability to modify until deadline
- **Late Submission:** Not accepted after deadline (hard cutoff)
- **Multiple Attempts:** System tracks both best score AND average
- **Incomplete Tests:** Unanswered questions scored as zero points

### 5.4 Anti-Cheating Measures

#### 5.4.1 Browser Security (Industry Best Practices)
- **Copy/Paste:** Disabled during tests
- **Tab Switching:** Prevented with warning and auto-submit
- **Right-Click:** Consider disabling
- **Full-Screen Mode:** Consider enforcing
- **Multiple Tabs:** Prevention implemented

#### 5.4.2 Violation Handling
- First violation: Warning displayed
- Continued violations: Flag for teacher review
- Severe violations: Consider auto-submit

### 5.5 Technical Features
- **Auto-Save:** Every minute to local storage
- **Network Interruption:** Local save continues, syncs when reconnected
- **Data Cleanup:** Local data deleted after successful cloud sync
- **Score Display:** Immediate upon test completion
- **Time Tracking:** Per-question timing for future analytics

## 6. Performance Tracking & Scoring

### 6.1 Scoring System
- **Primary Metric:** Percentage of correct answers
- **No Rankings:** Individual scores only, no class rankings
- **Partial Credit:** Not supported (future AI feature)
- **Score Display:** Immediate visibility after submission

### 6.2 Performance Metrics Tracked
- **Score Tracking:** Both best score AND average of all attempts
- **Time Analytics:**
  - Total time spent on exam
  - Time per question (identify rushing vs struggling)
  - Answer change patterns
- **Completion Data:**
  - Questions attempted vs skipped
  - Submission time relative to deadline

### 6.3 Data Retention & Persistence
- **Retention Period:** 10 years
- **Data Persistence:** All data tied to student ID (survives class changes)
- **Historical Access:** Students retain access to all past tests and scores
- **Version Control:** Exam versions tracked for score validity

## 7. Data Management & Export

### 7.1 Export Capabilities by Role

#### 7.1.1 Admin Export Rights
- Full system data export
- All classes and students
- System-wide performance analytics
- Formats: CSV, PDF reports, Excel

#### 7.1.2 Teacher Export Rights
- Limited to their assigned classes
- Individual student reports
- Class performance summaries
- Formats: CSV, PDF reports, Excel

#### 7.1.3 Student Export Rights
- No export capabilities
- View-only access to own data

### 7.2 Current Export Scope
- Individual student performance reports
- Class performance summaries
- Test completion statistics
- Score trends over time

### 7.3 Future Export Scope
- Question-level analysis
- Learning pattern insights
- Weakness identification reports
- AI-generated recommendations

## 8. User Interface Specifications

### 8.1 Language Support
- **Toggle Location:** Button at top of UI
- **Switching:** Real-time language change
- **Scope:** UI elements (buttons, navigation, labels)
- **Default:** Based on user preference

### 8.2 Student Portal Interface
```
Student Dashboard:
├── My Classes
│   ├── Current Quarter Classes
│   └── Previous Quarter Classes (Historical)
├── Assigned Tests
│   ├── Upcoming (with deadline countdown)
│   ├── In Progress (resumable)
│   └── Completed (with scores)
├── Test History
│   ├── All Attempts
│   ├── Best Scores
│   └── Score Averages
└── Quick Actions
    ├── Take New Test
    └── Review Past Tests
```

### 8.3 Teacher Portal Interface
```
Teacher Dashboard:
├── My Classes (All Assigned)
│   ├── Class Rosters
│   └── Quick Student Add
├── Cross-Class Student View
│   └── Performance Across Classes
├── Test Management
│   ├── Assign to Entire Class
│   ├── Assign to Individual Students
│   └── Set/Modify Deadlines
├── Performance Analytics
│   ├── Class Averages
│   └── Individual Progress
└── Data Export
    ├── Generate Reports
    └── Download Data
```

### 8.4 Admin Portal Interface
```
Admin Dashboard:
├── Class Management
│   ├── Create New Classes
│   ├── Assign Teachers to Classes
│   └── Quarterly Reset Tools
├── Teacher Management
│   ├── Add/Remove Teachers
│   └── Reassign Classes
├── System Reports
│   ├── School-wide Analytics
│   └── Curriculum Performance
├── Exam Management (Enhanced)
│   └── Upload Review/Quarterly Tests
└── All Teacher Functions
```

## 9. Technical Architecture Considerations

### 9.1 Authentication Implementation
- OAuth 2.0 with PKCE for social logins
- JWT tokens for session management
- Secure password hashing for email/password
- Multi-device session support

### 9.2 Database Design Principles
- Student-centric data model (ID-based)
- Efficient indexing for 400+ users
- Exam version control system
- Historical data preservation

### 9.3 Frontend Requirements
- Responsive design for tablets and laptops
- Minimum screen size support defined
- Touch-friendly interface for tablets
- Bilingual component architecture

### 9.4 Performance Requirements
- Page load: <3 seconds
- Auto-save latency: <1 second
- Score calculation: Immediate
- Export generation: <5 seconds

## 10. Features Explicitly NOT Included

### 10.1 Not Required in Phase 2
- Offline test-taking capability
- Mobile Device Management (MDM) integration
- Stylus/handwriting support
- Learning Management System (LMS) integration
- External gradebook synchronization
- Calendar integration (Google/Outlook)
- Automated test reminders
- Push notifications
- Separate parent portal/accounts
- In-app help documentation or tutorials
- Chat/email/phone support channels
- District or national benchmark comparisons
- Progress indicators ("on track" vs "needs help")
- Manual score override by teachers
- Individual activity logging for shared admin account
- Accommodation features (extra time, large fonts, read-aloud)

## 11. AI Integration Preparation (Future Phase)

### 11.1 Data Collection Starting Now
To enable future AI features, collect:
- Complete problem-solving data
- All exam questions and student answers
- Detailed timing patterns per question
- Answer change history
- Error patterns and common mistakes

### 11.2 Planned AI Features (Phase 3+)
- GPT API integration for answer analysis
- Automated weakness detection
- Personalized improvement recommendations
- AI-generated custom quizzes based on weaknesses
- Intelligent vocabulary lists from errors
- Automated flashcard generation
- Speaking and writing assessment (with AI evaluation)
- Predictive performance modeling

### 11.3 Long-term Vision
- Printable student dashboards for parent meetings
- Personalized learning paths
- Adaptive testing based on performance
- Real-time intervention recommendations

## 12. Implementation Timeline

### Phase 2A: Authentication & Users (Weeks 1-2)
- Implement Google OAuth and Kakao Login
- Build registration flows with consent
- Create three-tier role system
- Set up password recovery mechanisms

### Phase 2B: Class Management (Weeks 3-4)
- Build admin class creation interface
- Implement teacher assignment system
- Create student enrollment workflows
- Design quarterly transition tools

### Phase 2C: Enhanced Exam Management (Weeks 5-6)
- Separate review test and quarterly exam uploads
- Implement exam-to-class assignment
- Build differentiated assignment capabilities
- Create deadline management system

### Phase 2D: Student Experience (Weeks 7-8)
- Develop student dashboard
- Build test-taking interface with anti-cheating
- Implement auto-save and recovery
- Create score display and history views

### Phase 2E: Teacher Tools & Analytics (Weeks 9-10)
- Build cross-class student views
- Implement export functionality
- Create performance reports
- Test with production data

## 13. Success Metrics

### 13.1 Functional Success Criteria
- ✓ 100% of students can self-register and access tests
- ✓ Teachers efficiently manage classes up to 20 students
- ✓ System handles concurrent test sessions smoothly
- ✓ Both best scores and averages tracked accurately
- ✓ Bilingual toggle works seamlessly
- ✓ Data exports function in all three formats
- ✓ Anti-cheating measures prevent common violations

### 13.2 Technical Performance Metrics
- ✓ Support 400 students without degradation
- ✓ 10-year data retention implemented
- ✓ Immediate score calculation and display
- ✓ Multi-device concurrent login supported
- ✓ Auto-save prevents data loss

### 13.3 User Adoption Goals
- 80% of students complete registration within first week
- 90% of assigned tests completed by deadline
- Average test completion rate >95%
- Zero data loss incidents
- Teacher satisfaction with class management tools

## 14. Risk Mitigation

| Risk | Impact | Mitigation Strategy |
|------|--------|-------------------|
| OAuth provider downtime | High | Email/password fallback available |
| Network interruption during tests | High | Local auto-save every minute |
| Student forgets login | Medium | Multiple recovery options (email/phone) |
| Concurrent test load | Medium | Performance testing with 400+ users |
| Young student confusion | Medium | Teachers assist with registration |
| Tab switching/cheating | Medium | Technical prevention + teacher monitoring |
| Quarterly transition delays | Low | Clear admin procedures and training |

## 15. Appendices

### Appendix A: Curriculum Structure Reference
- 44 total curriculum levels across 4 programs
- PRIME CORE: 12 levels (4 subprograms × 3 levels)
- PRIME ASCENT: 12 levels (4 subprograms × 3 levels)
- PRIME EDGE: 12 levels (4 subprograms × 3 levels)
- PRIME PINNACLE: 8 levels (4 subprograms × 2 levels)

### Appendix B: Exam Naming Convention (Suggested)
```
Examples:
- REVIEW-CORE-Phonics-L1-2025-Q1-01
- REVIEW-CORE-Phonics-L1-2025-Q1-02
- QUARTERLY-CORE-Phonics-L1-2025-Q1-FINAL
- REVIEW-EDGE-Rise-L2-2025-Q3-03
- QUARTERLY-PINNACLE-Vision-L1-2025-Q4-FINAL
```

### Appendix C: Username Examples
```
Standard: john.smith
First duplicate: john.smith.1
Second duplicate: john.smith.2
```

### Appendix D: Test Flow States
```
Test Status Progression:
NOT_STARTED → IN_PROGRESS → COMPLETED
                    ↓
            (Hard deadline = Auto-close)
```

---

**Document Status:** FINAL - Ready for Development  
**Version:** 1.3  
**Approval Required From:** System Admin + Director  
**Last Updated:** August 2025  
**Next Steps:** 
1. Technical architecture detailed design
2. Database schema creation
3. UI/UX mockups
4. Development sprint planning
5. Teacher training material preparation