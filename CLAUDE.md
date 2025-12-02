# PrimePath Educational Platform - Simplified Agent Configuration

## Project Overview
**Goal**: Build MVP for comprehensive Language Learning Academy Management System
**User**: Non-technical founder creating proof-of-concept for developer handoff
**Current Stage**: Core CRM features with UI/UX refinements needed

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
✅ **Teachers Management** - Add/edit/delete teachers, assign to classes
✅ **Enrollments** - Student-class assignments with 3 view modes
✅ **Attendance Tracking** - Daily attendance with 4 status types
✅ **Search/Filter** - Students page has search + grade/status filters
✅ **Curriculum Management** - Hierarchical curriculum structure (1-4 levels deep)

## Upcoming Features - Test Management Module
🚧 **Test Management System** - Comprehensive assessment platform designed for real-time collaborative testing
- **File Upload & Preview**: PDF/image exam papers with rotation, zoom, navigation controls
- **Audio Integration**: MP3/WAV files for listening comprehension sections
- **Real-time Exam Delivery**: Synchronized exam launch to all students simultaneously
- **Multi-format Questions**: Multiple choice, audio-based, short/long answer types
- **Automated Grading**: Instant feedback for objective questions
- **Performance Analytics**: Student and class performance tracking
- **Teacher Dashboard**: Live monitoring during exams, progress tracking
- **Tablet-optimized**: Student interface designed for tablet devices

## Future AI/GPT Integration Considerations
🔮 **Adaptive Learning & Analytics** - System designed with extensibility points for future AI integration
- **OCR Integration**: Hooks for GPT-powered text extraction from uploaded exam papers
- **Performance Analytics**: Data structure designed for AI-powered student performance analysis
- **Adaptive Learning**: Framework prepared for dynamic difficulty adjustment based on student patterns
- **Auto-generated Reports**: Database structure supports AI-generated insights and recommendations
- **Content Analysis**: Exam content structured for GPT analysis of question difficulty and learning objectives
- **Personalized Feedback**: Student answer data formatted for AI-powered personalized feedback generation

### Technical Design Considerations for AI Integration:
- **Structured Data Storage**: All exam content, questions, and student responses stored in AI-friendly formats
- **API Extensibility**: Modular design allows future GPT API integration without system restructuring  
- **Analytics Pipeline**: Performance data aggregated in formats suitable for machine learning analysis
- **Content Metadata**: Rich tagging system for curriculum mapping and learning objective tracking
- **Real-time Processing**: Architecture supports both batch and real-time AI analysis workflows

## SIMPLE QC TESTING
**WHEN TO TEST**: After completing major features (new CRUD, pages, integrations)

### Quick QC Process:
1. **Build Check** → Run `npm run build` to ensure no errors
2. **Start Server** → Run `npm run dev` 
3. **Puppeteer Test** → Navigate and test basic functionality
4. **If it works** → Simple git commit and move on

### Basic Puppeteer Steps:
- Navigate to main pages (verify they load)
- Test new feature functionality (forms, buttons, navigation)  
- Check for obvious breaks or errors
- No screenshots needed - just verify it works

## SIMPLE GIT
```bash
# When feature works after QC:
git add .
git commit -m "feat: [what you built]"
git push origin main

# Example: 
git commit -m "feat: teacher assignment system"
```

## Standard Commands
- **Start Dev**: `npm run dev` (runs on http://localhost:3000)
- **Build**: `npm run build`
- **Lint**: `npm run lint`
- **Check & Restart Server**: `./check-server.sh` (auto-restarts if down)

## Agent Responsibilities
You are a **Single Full-Stack Developer** with these duties:

### Primary Functions
1. **Build features** - Implement requested functionality
2. **Test with Puppeteer** - Quick verification after major features
3. **Simple git commits** - Save working code
4. **Preserve existing** - Don't break what works

### Working Style
- **Build incrementally** - Small working pieces
- **Test when major feature complete** - Use Puppeteer for quick verification
- **Commit when it works** - Simple messages
- **Move fast** - This is MVP, not production

### Key Rules
- **Always preserve existing functionality**
- **Test major features with Puppeteer before moving on**
- **Simple git commits when things work**
- **Follow monochromatic design system**
- **Keep it simple** - This is proof-of-concept

---

## Recent Major Updates - Plain English

### November 27, 2024 - Teachers API Bug Fix
**What was broken:** The Teachers page was showing 500 errors and couldn't load teacher data.

**What was wrong:** The Teachers API was looking for teachers in the wrong academy. It was hardcoded to look for "academy-123" but our database has different academy IDs.

**How we fixed it:** Updated the Teachers API to use the same method as Students and Classes APIs - it now properly finds the correct academy ID from the database.

**What works now:**
- Teachers page loads without errors
- Can view teacher list (currently empty)
- "Add Teacher" button opens modal correctly
- Can add new teachers successfully
- All other features (Students, Classes, Enrollments) still work exactly as before

**Technical details:** Modified `/src/app/api/teachers/route.ts` and `/src/app/api/teachers/[id]/route.ts` to use `getAcademyId()` instead of hardcoded `ACADEMY_ID = 'academy-123'`.

**Testing done:** 
- Build passes ✓
- All pages load correctly ✓  
- Teacher functionality works ✓
- No regressions in existing features ✓

This was a simple database query mismatch - now all API endpoints use the same academy lookup method.

---

## November 27, 2024 - Curriculum System Foundation Improvements

### What was the situation?
The curriculum system was working but had some foundational issues that needed to be addressed before implementing a more sophisticated hierarchical curriculum structure. The system was showing test data mixed with real curriculum information, and we wanted to prepare for a more organized approach to curriculum management.

### What was the vision?
We want each academy to have **one clear curriculum structure** that can be 1, 2, 3, or 4 levels deep. Think of it like building blocks:
- **Level 1**: Main categories (like "General English", "Business English")
- **Level 2**: Programs within each category (like "Elementary", "Intermediate" under General English)
- **Level 3**: Specific class levels (like "Elementary A", "Elementary B" under Elementary)
- **Level 4**: Sub-levels if needed (like "Elementary A1", "Elementary A2" under Elementary A)

The key concept: **whatever is at the deepest level becomes the actual curriculum options for classes**. So if you choose a 3-level structure, Level 3 items are what teachers select when creating classes.

### What we accomplished (Phase 1):
**Foundation work** - We prepared the system for this hierarchical approach without breaking anything that already works.

**What we improved:**
1. **Added smart helper functions** - The system can now easily find "deepest level" curriculum items (the ones that should be used for actual classes) and distinguish them from higher-level categories.

2. **Verified database structure** - Confirmed that our database is already perfectly set up to handle this hierarchical vision with parent-child relationships and level tracking.

3. **Prepared for cleanup** - Identified test data that needs to be removed to make the curriculum structure clean and professional.

4. **Protected existing features** - Made sure that all current functionality (Students, Teachers, Classes, Enrollments, Attendance) continues to work exactly as before.

### What this means for users:
- **No disruption**: All current features continue to work normally
- **Better foundation**: The curriculum system is now prepared for a more organized, hierarchical structure
- **Cleaner data**: Ready to remove test entries and have a professional curriculum setup
- **Future flexibility**: The system can now easily handle 1, 2, 3, or 4-level curriculum structures as needed

### What works exactly the same:
- Adding students, teachers, and classes
- Managing enrollments and attendance
- All existing curriculum functionality
- All navigation and user interfaces

### Next steps planned:
- Clean up test data in the curriculum
- Update the curriculum management interface to show clear hierarchical relationships
- Make it easier to add curriculum items at the right levels
- Ensure only deepest-level curriculum items appear as options when creating classes

This was **preparatory work** - like organizing your workshop before building something complex. Everything you use daily works exactly the same, but the foundation is now stronger for future improvements.

---

## Test Management Module - Comprehensive Product Requirements

### Overview
The Test Management Module is a comprehensive assessment platform that enables real-time, collaborative testing for K-12 English language learning programs. This system integrates seamlessly with the existing LMS infrastructure to provide synchronized exam delivery, automated grading, and performance analytics.

### Core Architecture & Database Extensions

The test management system extends the current database schema with these key tables:

#### Main Tables:
- **exams**: Core exam metadata, file paths, question counts
- **exam_audio_files**: Audio files linked to specific question ranges  
- **exam_questions**: Individual questions with types and correct answers
- **exam_sessions**: Live exam instances with timing and status
- **student_exam_attempts**: Individual student attempts with scores
- **student_answers**: Detailed answer tracking with auto-grading
- **curriculum_exam_mappings**: Links exams to curriculum levels
- **class_exam_types**: Custom exam categories per class

#### Key Design Principles:
1. **Academy Isolation**: All tables include academy_id for multi-tenant security
2. **Audit Trail**: Comprehensive timestamps and soft deletes throughout
3. **Scalability**: Designed for concurrent exam sessions with 500+ students
4. **Extensibility**: Structured for future AI/GPT integration

### Feature Breakdown

#### 1. File Upload & Management System
- **Multi-format Support**: PDF, JPG, PNG for exams; MP3, WAV, M4A for audio
- **Advanced Preview**: Full-screen viewer with rotation, zoom, page navigation
- **Persistent Settings**: Rotation and zoom preferences saved per exam
- **Metadata Tracking**: Uploader identification and timestamp logging
- **Security**: Academy-scoped access with encrypted file transmission

#### 2. Question Configuration Engine
- **Question Types**: Multiple choice, multi-select, short/long answer, audio-based
- **Answer Management**: Correct answer marking, point values, partial credit
- **Audio Integration**: Map audio files to specific question number ranges
- **Bulk Operations**: Efficient question setup for large exams
- **Validation**: Comprehensive checks before exam publishing

#### 3. Real-time Exam Delivery System
- **Synchronous Launch**: Teacher "Launch" button starts exam for all students simultaneously
- **WebSocket Integration**: Real-time communication using Socket.IO
- **Progress Monitoring**: Live dashboard showing student completion status
- **Offline Resilience**: Local storage with automatic sync on reconnection
- **Auto-submission**: Automatic exam completion when time expires

#### 4. Student Tablet Interface
- **Full-screen Experience**: Distraction-free exam environment
- **Touch Optimization**: Large buttons, gesture navigation, accessibility features
- **Auto-save**: Continuous answer storage to prevent data loss
- **Progress Tracking**: Visual indicators for answered/unanswered questions
- **Media Integration**: Built-in audio player for listening comprehension

#### 5. Analytics & Reporting Engine
- **Real-time Metrics**: Live completion rates and progress tracking during exams
- **Individual Analysis**: Per-student performance breakdown by question type
- **Class Analytics**: Aggregate performance, question difficulty analysis
- **Historical Trends**: Performance tracking across multiple exam sessions
- **Export Capabilities**: Data export for external analysis tools

### AI/GPT Integration Framework

The system is architected with specific extensibility points for future AI integration:

#### OCR & Content Analysis
- **Structured Storage**: Exam content stored in JSON format for AI processing
- **Text Extraction Hooks**: API endpoints prepared for GPT-powered OCR
- **Content Tagging**: Metadata structure supports AI-generated learning objective tags
- **Question Classification**: Database fields ready for AI-powered question type analysis

#### Adaptive Learning Pipeline
- **Performance Vectors**: Student answer data structured for ML analysis
- **Difficulty Mapping**: Framework for AI-powered question difficulty scoring
- **Learning Path Analytics**: Data structure supports personalized learning recommendations
- **Real-time Adjustment**: Architecture allows mid-exam difficulty modification based on AI analysis

#### Auto-generated Insights
- **Report Generation**: Template system ready for AI-powered report creation
- **Performance Patterns**: Aggregated data formatted for GPT analysis
- **Personalized Feedback**: Student response data structured for individualized AI feedback
- **Curriculum Mapping**: Learning objective tracking designed for AI-powered curriculum alignment

### Integration with Existing LMS

#### Data Consistency
- **Student Enrollment**: Automatic sync with current class rosters
- **Teacher Permissions**: Inherits existing role-based access controls  
- **Curriculum Alignment**: Deep integration with hierarchical curriculum structure
- **Academy Isolation**: Maintains multi-tenant security model

#### Navigation & UX
- **Dashboard Integration**: Test management accessible from main LMS dashboard
- **Consistent Design**: Follows monochromatic design system (black/white/grey)
- **Mobile Responsive**: Works across desktop, tablet, and mobile devices
- **Search Integration**: Exams included in global academy search functionality

### Implementation Phases

#### Phase 1: Core Infrastructure (4-6 weeks)
- Database schema implementation and migration scripts
- File upload system with preview functionality  
- Basic exam creation interface
- PDF viewer with rotation and zoom controls

#### Phase 2: Assessment Engine (4-6 weeks)
- Question configuration system with multiple types
- Answer key management and validation
- Audio file integration with question mapping
- Student exam interface development

#### Phase 3: Real-time Delivery (6-8 weeks)
- WebSocket implementation for live communication
- Exam session management and teacher dashboard
- Student progress monitoring during exams
- Automated grading and immediate feedback

#### Phase 4: Analytics & AI Preparation (4-6 weeks)
- Performance analytics dashboard
- Report generation system
- AI integration hooks and data formatting
- Comprehensive testing and optimization

### Security & Performance Considerations

#### Academic Integrity
- **Secure Exam Environment**: Full-screen mode prevents tab switching
- **Access Control**: Time-limited exam tokens with session validation
- **Audit Logging**: Comprehensive tracking of all exam-related activities
- **Plagiarism Prevention**: Framework ready for future AI-powered detection

#### Performance Optimization
- **Concurrent Load**: Horizontal scaling support for 500+ simultaneous users
- **File Delivery**: CDN integration for efficient PDF and audio streaming  
- **Database Optimization**: Indexed queries and connection pooling
- **Caching Strategy**: Redis integration for session and file caching

### Success Metrics & KPIs

#### Adoption Metrics
- Teacher utilization rate (target: 80% monthly active teachers)
- Exam creation frequency (target: 10+ new exams per teacher per month)
- Student engagement rate (target: 95% completion rate for assigned exams)

#### Performance Metrics  
- System uptime during exam sessions (target: 99.9%)
- Exam loading time (target: <3 seconds)
- Concurrent user support (target: 500+ simultaneous exam takers)

#### Educational Impact
- Assessment frequency increase (target: 50% more regular assessments)
- Result delivery speed (target: <5 minutes from submission to results)
- Analytics adoption (target: 70% of teachers using performance insights)

---

## Recent Major Updates - Test Management Module Implementation

### November 29, 2024 - Create Exam Page with Advanced Features

**What was implemented:**
The Create Exam page now includes comprehensive test management features requested in the Test Management Module specifications.

**New Features Added:**

#### 1. Curriculum Tagging with Breadcrumbs
- **Multi-Select Support**: Exams can now be tagged to multiple curriculum levels (changed from single dropdown to checkbox-based multi-select)
- **Optional Selection**: Curriculum tagging is now optional - exams can be created without curriculum assignment
- **Breadcrumb Display**: Full hierarchical paths shown (e.g., "Elementary Program > Reading Track > Beginner Level")
- **Tag Interface**: Selected curriculum levels appear as removable tags above the dropdown
- **Smart API**: Uses deepest-level curriculum nodes only, with full path context

#### 2. Audio File Upload System
- **Multiple File Support**: Upload multiple audio files (MP3, WAV, M4A) for listening comprehension
- **File Management**: Visual list of uploaded audio files with remove functionality
- **Validation**: File type and size validation (50MB max per file)
- **Database Integration**: Audio files stored in exam_files table with proper metadata

#### 3. Enhanced PDF Preview
- **Zoom Controls**: Zoom in/out buttons with percentage display (50% - 200% range)
- **Rotation**: 90-degree rotation button for document orientation
- **Reset Function**: Quick reset to default zoom level
- **Professional Toolbar**: Clean interface with intuitive controls
- **Smooth Transitions**: CSS transitions for better user experience

**Technical Implementation:**
- **API Endpoints Created:**
  - `/api/curriculum/deepest` - Returns deepest curriculum nodes with breadcrumb paths
  - `/api/exams/upload-audio` - Handles audio file uploads with validation
  - `/api/exams/curriculum-mapping` - Creates exam-curriculum relationships

- **Database Updates:**
  - Uses existing `curriculum_exam_mappings` table for multiple curriculum assignments
  - Leverages `exam_files` table for audio storage
  - Maintains backward compatibility with single curriculum selection

**Testing & Verification:**
- ✅ Build passes without TypeScript errors
- ✅ All existing features remain functional
- ✅ Server logs confirm successful API calls
- ✅ Multi-select functionality tested with tags and checkboxes

---

## Server Management & Auto-Restart

### Automatic Server Health Check
**Problem**: The development server frequently stops when making code changes or running builds.

**Solution**: Always check server status before operations and auto-restart if needed.

### Quick Server Commands:
```bash
# Check if server is running
curl -I http://localhost:3000

# Start server (if not running)
npm run dev

# Kill and restart server
pkill -f "next dev" && npm run dev

# Start in background with logging
nohup npm run dev > /tmp/nextjs.log 2>&1 &
```

### Agent Behavior:
- **Before any testing**: Check if server responds to requests
- **If server is down**: Automatically restart with `npm run dev`
- **After builds**: Always restart the server
- **Use background mode**: Keep server running during other operations
- **Use health check script**: Run `./check-server.sh` to auto-check and restart
- **Regular checks**: Periodically verify server is still running during long operations

---

## Testing URLs

### Primary Testing Pages:
- **Create Exam** (with all new features): http://localhost:3000/exams/create
- **Main Dashboard**: http://localhost:3000
- **Exams List**: http://localhost:3000/exams
- **Students**: http://localhost:3000/students
- **Classes**: http://localhost:3000/classes
- **Teachers**: http://localhost:3000/teachers

### What to Test on Create Exam Page:
1. **Curriculum Multi-Select**: 
   - Click dropdown to see breadcrumb paths
   - Select multiple levels with checkboxes
   - Remove tags with X button
   - Create exam without curriculum (optional)

2. **Audio Upload**:
   - Click "Upload Audio Files" in Step 3
   - Select multiple audio files
   - View uploaded files list
   - Remove files if needed

3. **PDF Preview**:
   - Upload a PDF file
   - Test zoom in/out controls
   - Test rotation button
   - Use reset zoom function

---
**Last Updated**: 2024-11-29  
**Version**: MVP Development Phase - Test Management Module Partially Implemented