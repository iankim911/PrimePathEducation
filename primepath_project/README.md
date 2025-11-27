# PrimePath Backend Setup Instructions

## Prerequisites
- Python 3.8+
- PostgreSQL
- pip

## Installation Steps

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure PostgreSQL:
- Create database: `primepath_db`
- Create user: `primepath_user`
- Grant privileges

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Load initial curriculum data:
```bash
python manage.py loaddata curriculum_data.json
python manage.py populate_curriculum
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## Project Structure

- `core/` - Core models and curriculum management
- `placement_test/` - Placement test functionality
- `media/` - Uploaded PDFs and audio files
- `static/` - Static assets
- `templates/` - HTML templates

## Key Features

- Curriculum mapping (48 levels across 4 programs)
- PDF exam upload with file size validation
- Audio file support for listening sections
- Auto-grading for MCQ and checkbox questions
- Difficulty adjustment during tests
- Placement rule configuration
- Session tracking and analytics

## API Endpoints

### Placement Test
- `/api/placement/start/` - Start new test
- `/api/placement/session/<id>/` - Take test
- `/api/placement/session/<id>/submit/` - Submit answer
- `/api/placement/session/<id>/adjust-difficulty/` - Adjust difficulty
- `/api/placement/session/<id>/complete/` - Complete test
- `/api/placement/session/<id>/result/` - View results

### Teacher Dashboard
- `/teacher/dashboard/` - Main dashboard
- `/curriculum/levels/` - View curriculum structure
- `/placement-rules/` - Manage placement rules
- `/api/placement/exams/` - Manage exams

## Notes
- CORS is enabled for all origins (adjust for production)
- File upload limit: 10MB for PDFs, 50MB for audio
- No authentication required (as requested)