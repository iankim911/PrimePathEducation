# PrimePath Assessment Platform

An educational assessment platform for student placement tests with adaptive curriculum mapping.

## Features

- **Student Placement Tests**: Automated placement tests with timer and audio support
- **Curriculum Mapping**: Dynamic mapping of exams to curriculum levels
- **Placement Rules**: Configure student placement based on grade and English class rank
- **Audio Integration**: Support for audio files in exams
- **PDF Preview**: Built-in PDF viewer for exam papers
- **Teacher Dashboard**: Comprehensive management interface

## Tech Stack

- **Backend**: Django 5.0.1
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (development)
- **PDF Handling**: PDF.js
- **Authentication**: Django built-in auth with custom decorators

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd PrimePath_
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Load initial data (if available):
   ```bash
   python manage.py loaddata initial_data.json
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at `http://localhost:8000`

## Project Structure

```
PrimePath_/
├── primepath_project/      # Main project directory
│   ├── core/              # Core app (models, authentication)
│   ├── placement_test/    # Placement test functionality
│   ├── templates/         # HTML templates
│   ├── static/           # Static files (CSS, JS)
│   └── media/            # Uploaded files (PDFs, audio)
├── manage.py
└── requirements.txt
```

## Usage

### For Teachers:
1. Login with admin credentials (ID: admin, Password: admin123)
2. Upload exam PDFs with audio files
3. Configure placement rules and exam mappings
4. Monitor student sessions

### For Students:
1. Enter name, grade, and English class rank
2. Take the placement test
3. View results and curriculum recommendations

## Key Components

- **Exam Management**: Upload and manage placement tests
- **Exam-to-Level Mapping**: Map exams to curriculum levels
- **Placement Rules**: Configure grade/rank to curriculum mapping
- **Student Sessions**: Track and monitor test sessions

## Development

### Running Tests:
```bash
python manage.py test
```

### Making Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

## License

[Your License Here]

## Contact

[Your Contact Information]