# PrimePath Educational Assessment Platform - Comprehensive Documentation

## Project Overview

PrimePath is a sophisticated educational assessment platform built with Django that provides placement testing capabilities for English language learning programs. The system automatically matches students to appropriate curriculum levels based on their grade and academic performance, then administers customized placement tests.

**Current Status**: Backend complete, fully functional with comprehensive models, API endpoints, service architecture, and frontend templates.

## Architecture and Technology Stack

### Core Technologies
- **Backend**: Django 5.0.1
- **Database**: PostgreSQL (configurable to SQLite for development)
- **File Storage**: Local filesystem with Django's file handling
- **Frontend**: HTML templates with vanilla JavaScript
- **Dependencies**: Minimal - Pillow for image processing, python-decouple for config

### Project Structure
```
PrimePath_/
├── primepath_project/                 # Main Django project
│   ├── core/                         # Core business logic app
│   │   ├── models.py                 # Curriculum, placement rules
│   │   ├── views.py                  # Dashboard, configuration views
│   │   ├── services/                 # Business logic services
│   │   ├── exceptions.py             # Custom exception classes
│   │   ├── decorators.py             # Error handling decorators
│   │   └── constants.py              # Application constants
│   ├── placement_test/               # Assessment functionality app
│   │   ├── models.py                 # Exam, session, answer models
│   │   ├── views.py                  # Test taking, exam management
│   │   ├── services/                 # Placement, grading, session services
│   │   └── templatetags/             # Custom template tags
│   ├── templates/                    # HTML templates
│   └── media/                        # Uploaded files (PDFs, audio)
```

## Database Models and Relationships

### Core App Models

#### Educational Structure Hierarchy
```python
Program (4 programs)
├── SubProgram (15 total across all programs)
│   └── CurriculumLevel (45 total - 3 levels per subprogram)
```

**Programs Available:**
- PRIME CORE (Grades 1-6)
- PRIME ASCENT (Grades 7-9) 
- PRIME EDGE (Grades 10-12)
- PRIME PINNACLE (Advanced)

**Key Models:**
- `School`: Educational institutions
- `Teacher`: Instructors (with head teacher designation)
- `Program`: Top-level curriculum programs
- `SubProgram`: Specialized tracks within programs
- `CurriculumLevel`: Specific learning levels (45 total)
- `PlacementRule`: Grade + rank → curriculum mapping rules
- `ExamLevelMapping`: Maps exams to curriculum levels with slot positions

### Placement Test App Models

**Assessment Models:**
- `Exam`: Assessment documents with PDF files, timer settings, question counts
- `AudioFile`: Audio components for listening sections
- `Question`: Individual test items with multiple types (MCQ, checkbox, short/long answer)
- `StudentSession`: Complete test-taking sessions with timing and scores
- `StudentAnswer`: Individual question responses with auto-grading
- `DifficultyAdjustment`: Records of mid-test difficulty changes

### Key Relationships
- Each curriculum level can have multiple exams mapped to it (1-to-5 slots)
- Students are placed via: Grade + Academic Rank → Placement Rule → Curriculum Level → Random Exam Selection
- Sessions track complete test-taking experiences with all answers and timing
- Difficulty can be adjusted mid-test, switching to different curriculum levels

## Key Features Implemented

### 1. Student Placement System
- **Two-step process**: Placement Rules → Exam Mapping
- **Placement Rules**: Define grade + academic rank combinations that map to curriculum levels
- **Exam Mapping**: Each curriculum level can have up to 5 different exam versions
- **Random Selection**: System randomly selects from available exams for a level

### 2. Assessment Capabilities
- **Multiple Question Types**: MCQ, checkbox (select all), short answer, long answer
- **PDF Integration**: Full-screen PDF viewer for test materials
- **Audio Support**: MP3, WAV, M4A files with question range assignments
- **Timer System**: Configurable test timing with auto-submission
- **Auto-grading**: Automatic scoring for objective questions

### 3. Test Experience Features
- **Difficulty Adjustment**: Students can request easier/harder tests mid-session
- **Session Persistence**: All answers auto-saved, can resume if interrupted
- **Progress Tracking**: Real-time tracking of answered vs. remaining questions
- **Result Generation**: Immediate scoring and curriculum level recommendations

### 4. Administrative Interface
- **Teacher Dashboard**: Overview of recent sessions, active exams, statistics
- **Exam Management**: Upload PDFs, audio files, configure questions and answers
- **Placement Configuration**: Visual matrix for setting up placement rules
- **Exam-to-Level Mapping**: Interface for mapping exams to curriculum levels
- **Session Monitoring**: View all student sessions with filtering and export

## Recent Fixes and Customizations

### Phone Number Validation (Start Test Form)
- **Korean Phone Format**: Enforces 010-XXXX-XXXX format
- **Real-time Validation**: JavaScript formatting with immediate feedback
- **Server-side Cleanup**: Strips hyphens and spaces before storage
- **User Experience**: Clear error messages and format hints

### Exam Mapping Persistence
- **Individual Level Saving**: Can save mappings for single curriculum levels
- **Bulk Operations**: Save all mappings across programs simultaneously
- **Slot Management**: Add/remove exam slots (up to 5) with proper renumbering
- **Data Integrity**: Prevents duplicate mappings with database constraints

### UI Improvements
- **Navigation Enhancement**: Clean tab-based navigation across all admin functions
- **Responsive Design**: Works on desktop, tablet, and large mobile devices
- **Status Indicators**: Visual feedback for exams with/without PDF files
- **Progress Statistics**: Real-time count of mapped levels per program

### Service Layer Architecture
- **PlacementService**: Handles student-to-exam matching logic
- **SessionService**: Manages test sessions and answer submissions
- **ExamService**: Exam creation, question management, file handling
- **GradingService**: Automatic answer evaluation and scoring

## URL Patterns and API Endpoints

### Student-Facing URLs
```
/api/placement/start/                    # Start placement test form
/api/placement/session/<uuid>/           # Take test interface
/api/placement/session/<uuid>/result/    # View test results
```

### Administrative URLs
```
/                                        # Home page
/teacher/dashboard/                      # Teacher dashboard
/api/placement/exams/                    # Exam list and management
/api/placement/exams/create/             # Upload new exams
/exam-mapping/                           # Curriculum-to-exam mapping
/placement-rules/                        # Grade/rank placement rules
/api/placement/sessions/                 # Student session management
```

### API Endpoints
```
POST /api/placement/session/<uuid>/submit/           # Submit individual answers
POST /api/placement/session/<uuid>/adjust-difficulty/ # Request difficulty change
POST /api/placement/session/<uuid>/complete/         # Complete test session
GET  /api/placement/audio/<id>/                      # Stream audio files
POST /api/exam-mappings/save/                        # Save exam mappings
POST /api/placement-rules/save/                      # Save placement rules
```

## JavaScript Functionality

### Test Taking Interface
- **PDF Viewer Integration**: Left panel displays exam PDF with zoom controls
- **Answer Submission**: Right panel with question navigation and answer inputs
- **Timer Management**: Countdown timer with warnings and auto-submission
- **Auto-save**: Periodic saving of answers without page refresh
- **Difficulty Adjustment**: Modal for requesting level changes

### Administrative Interfaces
- **Exam Mapping**: Dynamic add/remove exam slots with validation
- **Placement Rules**: Interactive grid for setting grade/rank combinations
- **Question Management**: Bulk question type and answer configuration
- **Real-time Statistics**: Live updates of mapping coverage and session counts

## Service Layer Patterns

### Error Handling Strategy
- **Custom Exceptions**: Specific exception types for different error scenarios
- **Decorator Pattern**: `@handle_errors` decorator for consistent error responses
- **Logging Integration**: Comprehensive logging with structured data
- **User-Friendly Messages**: Clean error messages for both UI and API consumers

### Transaction Management
- **Atomic Operations**: Critical operations wrapped in database transactions
- **Rollback Safety**: Automatic rollback on errors during multi-step operations
- **Consistency Guarantees**: Ensures data integrity across related model updates

### Validation Patterns
- **Service-Level Validation**: Business logic validation in service classes
- **Model Validation**: Database-level constraints and custom validators
- **Form Validation**: Client-side validation with server-side backup

## Development Commands and Procedures

### Initial Setup
```bash
# Navigate to project directory
cd C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\primepath_project

# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py makemigrations
python manage.py migrate

# Load curriculum data
python manage.py loaddata core/fixtures/curriculum_data.json
python manage.py populate_curriculum

# Create admin user (optional)
python manage.py createsuperuser
```

### Running the Server
```bash
# Development server
python manage.py runserver

# Or use the provided batch files:
# - RUN_SERVER_NOW.bat (main server starter)
# - RUN_PRIMEPATH.bat (application runner)
```

### Database Operations
```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (if needed)
python manage.py flush
```

### File Management
- **Media Files**: Stored in `media/exams/` with subfolders for PDFs and audio
- **Static Files**: CSS/JS served from `static/` directory
- **Upload Limits**: 10MB for PDFs, 50MB for audio files
- **File Validation**: Extension and size validation on upload

## Important Design Patterns and Conventions

### Service-Oriented Architecture
- **Separation of Concerns**: Views handle HTTP, services handle business logic
- **Testability**: Services are easily unit testable
- **Reusability**: Service methods can be called from multiple views or contexts

### Model Relationships
- **Foreign Keys**: Extensive use of relationships for data integrity
- **Cascading Deletes**: Proper cleanup when parent objects are deleted
- **Unique Constraints**: Prevent duplicate data at database level

### Template Organization
- **Base Template**: Consistent layout and navigation across all pages
- **Template Tags**: Custom tags for grade formatting and calculations
- **Static Files**: Inline CSS and JavaScript for simplicity

## Known Issues and Areas Needing Attention

### Current Limitations
1. **Authentication System**: Currently no authentication required (by design)
2. **File Storage**: Local filesystem storage (not suitable for production scale)
3. **Concurrent Testing**: No session locking for simultaneous attempts
4. **Advanced Analytics**: Limited reporting and analytics capabilities

### Potential Improvements
1. **Caching**: Add Redis/Memcached for better performance
2. **API Documentation**: Swagger/OpenAPI documentation
3. **Mobile Optimization**: Better mobile responsive design
4. **Batch Operations**: Bulk exam upload and management tools
5. **Advanced Reporting**: Detailed analytics and export capabilities

### Security Considerations
1. **File Upload Security**: Validates file types but could add virus scanning
2. **CSRF Protection**: Enabled for all form submissions
3. **SQL Injection**: Protected by Django ORM
4. **XSS Prevention**: Auto-escaping enabled in templates

## Configuration Management

### Environment Variables
```bash
# Required settings (via .env file)
SECRET_KEY=your-secret-key
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=primepath
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Feature Flags
- `ENABLE_DIFFICULTY_ADJUSTMENT`: Allow mid-test difficulty changes
- `ENABLE_AUDIO_SUPPORT`: Enable audio file functionality
- `ENABLE_AUTO_GRADING`: Automatic answer grading

### File Upload Settings
- `FILE_UPLOAD_MAX_MEMORY_SIZE`: 10MB default
- `DATA_UPLOAD_MAX_MEMORY_SIZE`: 10MB default
- PDF files: Max 10MB
- Audio files: Max 50MB

## Testing and Quality Assurance

### Test Coverage Areas
- **Model Validation**: All model constraints and relationships
- **Service Logic**: Business logic in service classes
- **API Endpoints**: All HTTP endpoints with various input scenarios
- **File Handling**: Upload, storage, and retrieval of media files

### Quality Metrics
- **Code Organization**: Clear separation between views, services, and models
- **Error Handling**: Comprehensive exception handling with user-friendly messages
- **Database Integrity**: Foreign key constraints and unique constraints
- **Performance**: Optimized queries with select_related and prefetch_related

This documentation provides a comprehensive overview of the PrimePath platform's current state, architecture, and capabilities. The system is production-ready for the core placement testing functionality with room for enhancement in areas like advanced analytics, mobile optimization, and scalability improvements.