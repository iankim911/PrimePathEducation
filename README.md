# PrimePath Assessment Platform

[![Django](https://img.shields.io/badge/Django-5.0.1-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Phase](https://img.shields.io/badge/Phase-9-purple.svg)](PHASE9_COMPLETION_REPORT.md)

A comprehensive educational assessment platform for student placement tests with adaptive curriculum mapping, audio support, and real-time monitoring.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Recent Updates](#recent-updates)
- [License](#license)

## ✨ Features

### Core Features
- **📝 Student Placement Tests**: Automated placement tests with timer and audio support
- **🎯 Adaptive Curriculum Mapping**: Dynamic mapping of exams to curriculum levels
- **📊 Placement Rules Engine**: Configure student placement based on grade and English class rank
- **🎵 Audio Integration**: Full audio support for listening comprehension questions
- **📄 PDF Viewer**: Built-in PDF.js viewer with rotation and zoom controls
- **👩‍🏫 Teacher Dashboard**: Comprehensive management interface with real-time monitoring
- **📱 Mobile Responsive**: Fully responsive design for all devices
- **🔒 Secure Authentication**: Django-based authentication with role-based access

### Recent Enhancements (Phase 7-9)
- **🧹 Code Quality**: Cleaned 95 code issues, optimized performance
- **🔐 Enhanced Security**: Environment-based configuration, secure defaults
- **📊 Console Monitoring**: Real-time debugging and performance tracking
- **📚 Comprehensive Documentation**: Full API, deployment, and developer guides
- **🔄 Relationship Preservation**: All 257 component relationships maintained

## 🛠 Tech Stack

### Backend
- **Framework**: Django 5.0.1
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **API**: Django REST Framework 3.14.0
- **Authentication**: Django built-in with custom decorators
- **Task Queue**: Celery 5.3.4 (optional)

### Frontend
- **Core**: HTML5, CSS3, ES6+ JavaScript
- **PDF Handling**: PDF.js 2.x
- **Audio**: HTML5 Audio API
- **Styling**: Custom CSS with responsive design
- **Monitoring**: Phase 7-9 console monitoring system

### Infrastructure
- **Cache**: Redis (optional)
- **File Storage**: Local filesystem / AWS S3 (prod)
- **Monitoring**: Custom console logging system

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/PrimePath.git
cd PrimePath

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
cd primepath_project
python manage.py migrate --settings=primepath_project.settings_sqlite

# Create superuser
python manage.py createsuperuser --settings=primepath_project.settings_sqlite

# Start development server
python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite

# Access at http://127.0.0.1:8000
```

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip and virtualenv
- Git
- SQLite (development) or PostgreSQL (production)
- Redis (optional, for caching and Celery)

### Detailed Installation

1. **Clone and Navigate**:
   ```bash
   git clone https://github.com/yourusername/PrimePath.git
   cd PrimePath
   ```

2. **Virtual Environment Setup**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**:
   ```bash
   cd primepath_project
   python manage.py migrate --settings=primepath_project.settings_sqlite
   python manage.py createsuperuser --settings=primepath_project.settings_sqlite
   ```

6. **Load Initial Data** (optional):
   ```bash
   python manage.py loaddata initial_data.json --settings=primepath_project.settings_sqlite
   ```

7. **Collect Static Files**:
   ```bash
   python manage.py collectstatic --noinput --settings=primepath_project.settings_sqlite
   ```

8. **Run Development Server**:
   ```bash
   python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite
   ```

## ⚙️ Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DATABASE_URL=postgres://user:pass@localhost/dbname  # For production

# Security (Production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Feature Flags
ENABLE_API_V2=True
ENABLE_ADVANCED_MONITORING=True
PHASE8_MONITORING_ENABLED=True

# File Upload Limits
MAX_UPLOAD_SIZE=52428800  # 50MB
```

### Settings Files

- `settings_sqlite.py`: Development settings with SQLite
- `settings_production.py`: Production settings (create from template)
- `.env`: Environment-specific configuration

## 📁 Project Structure

```
PrimePath/
├── primepath_project/           # Main Django project
│   ├── primepath_project/      # Project settings
│   │   ├── settings_sqlite.py  # Development settings
│   │   └── urls.py             # Root URL configuration
│   ├── core/                   # Core application
│   │   ├── models.py           # Core models (Teacher, School, Curriculum)
│   │   ├── views/              # Modular views
│   │   ├── services/           # Business logic services
│   │   └── templates/          # Core templates
│   ├── placement_test/         # Placement test app
│   │   ├── models.py           # Test models (Exam, Question, Session)
│   │   ├── views/              # Test views
│   │   └── templates/          # Test templates
│   ├── api/                    # API application
│   │   ├── views.py            # API endpoints
│   │   └── serializers.py      # DRF serializers
│   ├── common/                 # Shared utilities
│   │   ├── mixins.py           # Reusable mixins
│   │   └── views/              # Base view classes
│   ├── static/                 # Static files
│   │   ├── js/                 # JavaScript modules
│   │   │   ├── modules/        # Modular JS components
│   │   │   └── phase*/         # Phase monitoring scripts
│   │   ├── css/                # Stylesheets
│   │   └── docs/               # Documentation
│   ├── media/                  # User uploads
│   │   ├── exams/pdfs/         # Exam PDFs
│   │   └── exams/audio/        # Audio files
│   └── templates/              # HTML templates
│       ├── base.html           # Base template
│       └── components/         # Reusable components
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 📖 Usage

### For Teachers/Administrators

1. **Login**: Access `/teacher/login/` with credentials
2. **Dashboard**: View overview at `/teacher/dashboard/`
3. **Create Exam**:
   - Navigate to "Upload Exam"
   - Select curriculum level
   - Upload PDF and audio files
   - Configure questions and answers
4. **Manage Placement Rules**:
   - Go to "Student Levels"
   - Configure grade/rank mappings
5. **Monitor Sessions**:
   - View active test sessions
   - Track student progress

### For Students

1. **Start Test**:
   - Enter name, grade, and English class rank
   - Phone number (optional)
2. **Take Test**:
   - Answer multiple choice questions
   - Use audio player for listening sections
   - Navigate with question buttons
3. **Submit**:
   - Review answers before submission
   - View results and recommendations

### Key URLs

- `/` - Home page
- `/teacher/dashboard/` - Teacher dashboard
- `/api/placement/exams/create/` - Create exam
- `/api/placement/start/` - Start test
- `/placement-rules/` - Placement rules configuration
- `/exam-mapping/` - Exam to level mapping

## 🔌 API Documentation

### Authentication
All API endpoints require authentication except public test endpoints.

### Main Endpoints

#### Exams
- `GET /api/placement/exams/` - List all exams
- `POST /api/placement/exams/create/` - Create new exam
- `GET /api/placement/exams/{id}/` - Get exam details
- `PUT /api/placement/exams/{id}/` - Update exam
- `DELETE /api/placement/exams/{id}/` - Delete exam

#### Sessions
- `GET /api/placement/sessions/` - List test sessions
- `POST /api/placement/start/` - Start new test session
- `GET /api/placement/sessions/{id}/` - Get session details
- `POST /api/placement/sessions/{id}/submit-answer/` - Submit answer

#### Placement Rules
- `GET /api/core/placement-rules/` - Get placement rules
- `POST /api/core/placement-rules/` - Create rule
- `PUT /api/core/placement-rules/{id}/` - Update rule

For complete API documentation, see [API.md](API.md).

## 💻 Development

### Setting Up Development Environment

1. **Install Development Dependencies**:
   ```bash
   pip install -r requirements-dev.txt  # If available
   ```

2. **Enable Debug Mode**:
   ```bash
   # In .env
   DEBUG=True
   ```

3. **Run with Auto-reload**:
   ```bash
   python manage.py runserver --settings=primepath_project.settings_sqlite
   ```

### Code Style

- Python: PEP 8
- JavaScript: ES6+ standards
- CSS: BEM methodology
- HTML: Semantic HTML5

### Phase Monitoring

The codebase includes Phase 7-9 monitoring for:
- Code quality tracking
- Configuration validation
- Documentation coverage
- Performance monitoring

Access monitoring at browser console:
```javascript
// View Phase 8 configuration status
window.PHASE8_CONFIG

// View Phase 9 API documentation
window.PHASE9_API_DOCS.showEndpoints()
```

## 🧪 Testing

### Run All Tests
```bash
python manage.py test --settings=primepath_project.settings_sqlite
```

### Run Specific App Tests
```bash
python manage.py test placement_test --settings=primepath_project.settings_sqlite
python manage.py test core --settings=primepath_project.settings_sqlite
```

### Feature Verification
```bash
python verify_all_features.py
```

### Coverage Report
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Production Setup

1. **Set Environment Variables**:
   ```bash
   export DEBUG=False
   export SECRET_KEY=your-production-secret-key
   export ALLOWED_HOSTS=yourdomain.com
   ```

2. **Use Production Settings**:
   ```bash
   python manage.py migrate --settings=primepath_project.settings_production
   python manage.py collectstatic --settings=primepath_project.settings_production
   ```

3. **Run with Gunicorn**:
   ```bash
   gunicorn primepath_project.wsgi:application --bind 0.0.0.0:8000
   ```

## 🔧 Troubleshooting

### Common Issues

1. **"Connection Refused" in Browser**:
   - Check if server is running: `curl -I http://127.0.0.1:8000/`
   - Clear browser cache
   - Try incognito mode

2. **"Command timed out"**:
   - Normal if after "Watching for file changes"
   - Server is running, ignore timeout

3. **Template Changes Not Showing**:
   - Restart server without `--noreload`
   - Clear browser cache

4. **Database Errors**:
   ```bash
   python manage.py migrate --run-syncdb
   ```

5. **Static Files Not Loading**:
   ```bash
   python manage.py collectstatic --clear --noinput
   ```

For more issues, check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 Recent Updates

### Phase 9 (August 13, 2025)
- Comprehensive documentation update
- API documentation generation
- Deployment guide creation
- 257 relationships documented

### Phase 8 (August 13, 2025)
- Configuration security improvements
- Environment-based settings
- Enhanced .gitignore
- Production-ready configuration

### Phase 7 (August 13, 2025)
- Code quality cleanup
- Removed 95 code issues
- Optimized JavaScript
- Console monitoring added

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- PrimePath Development Team

## 🙏 Acknowledgments

- Django Software Foundation
- PDF.js Contributors
- Open Source Community

---

**Version**: 1.0.0 | **Last Updated**: August 13, 2025 | **Phase**: 9 Complete

For technical support, please create an issue on GitHub.