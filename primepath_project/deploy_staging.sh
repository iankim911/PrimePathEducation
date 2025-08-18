#!/bin/bash
# Staging Deployment Script for RoutineTest

echo "================================================"
echo "ROUTINETEST STAGING DEPLOYMENT SCRIPT"
echo "================================================"

# Configuration
PROJECT_DIR="/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project"
VENV_DIR="/Users/ian/Desktop/VIBECODE/PrimePath/venv"
STAGING_BRANCH="staging"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Create staging branch if it doesn't exist
echo -e "\n1. Preparing Git Repository..."
cd $PROJECT_DIR
if git show-ref --verify --quiet refs/heads/$STAGING_BRANCH; then
    print_warning "Staging branch exists, switching to it"
    git checkout $STAGING_BRANCH
else
    print_status "Creating staging branch"
    git checkout -b $STAGING_BRANCH
fi

# 2. Create staging settings
echo -e "\n2. Creating Staging Settings..."
cat > primepath_project/settings_staging.py << 'EOF'
"""
Staging Settings for RoutineTest
"""
from .settings_sqlite import *
import os

# Override settings for staging
DEBUG = True  # Keep True for staging, False for production
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'staging.primepath.edu']

# Database (can use PostgreSQL for staging)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_staging.sqlite3',
    }
}

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media_staging'

# Security (less strict for staging)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email (use console backend for staging)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'staging.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

print("🔧 Using STAGING settings")
EOF
print_status "Staging settings created"

# 3. Create requirements file
echo -e "\n3. Creating Requirements File..."
cat > requirements_staging.txt << 'EOF'
Django==5.0.1
Pillow==10.1.0
gunicorn==21.2.0
whitenoise==6.6.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
django-cors-headers==4.3.1
djangorestframework==3.14.0
EOF
print_status "Requirements file created"

# 4. Create .env file for staging
echo -e "\n4. Creating Environment Variables..."
cat > .env.staging << 'EOF'
# Staging Environment Variables
SECRET_KEY='your-secret-key-here-change-in-production'
DEBUG=True
DATABASE_URL=sqlite:///./db_staging.sqlite3
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1,staging.primepath.edu
EOF
print_status "Environment variables created"

# 5. Create Docker configuration
echo -e "\n5. Creating Docker Configuration..."
cat > Dockerfile.staging << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements_staging.txt .
RUN pip install --no-cache-dir -r requirements_staging.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=primepath_project.settings_staging

# Run migrations
RUN python manage.py migrate --settings=primepath_project.settings_staging

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "primepath_project.wsgi:application"]
EOF

cat > docker-compose.staging.yml << 'EOF'
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.staging
    ports:
      - "8000:8000"
    volumes:
      - ./media_staging:/app/media_staging
      - ./db_staging.sqlite3:/app/db_staging.sqlite3
    environment:
      - DJANGO_SETTINGS_MODULE=primepath_project.settings_staging
    command: >
      sh -c "python manage.py migrate --settings=primepath_project.settings_staging &&
             python manage.py runserver 0.0.0.0:8000 --settings=primepath_project.settings_staging"
EOF
print_status "Docker configuration created"

# 6. Create deployment script
echo -e "\n6. Creating Deployment Script..."
cat > run_staging.sh << 'EOF'
#!/bin/bash
# Run staging server

echo "Starting RoutineTest Staging Server..."

# Option 1: Using Django development server
python manage.py migrate --settings=primepath_project.settings_staging
python manage.py collectstatic --noinput --settings=primepath_project.settings_staging
python manage.py runserver 0.0.0.0:8000 --settings=primepath_project.settings_staging

# Option 2: Using Gunicorn (production-like)
# gunicorn --bind 0.0.0.0:8000 --workers 3 primepath_project.wsgi:application

# Option 3: Using Docker
# docker-compose -f docker-compose.staging.yml up
EOF
chmod +x run_staging.sh
print_status "Deployment script created"

# 7. Create nginx configuration
echo -e "\n7. Creating Nginx Configuration..."
cat > nginx_staging.conf << 'EOF'
server {
    listen 80;
    server_name staging.primepath.edu;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/primepath/;
    }
    
    location /media/ {
        root /var/www/primepath/;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8000;
    }
}
EOF
print_status "Nginx configuration created"

# 8. Run initial setup
echo -e "\n8. Running Initial Setup..."
source $VENV_DIR/bin/activate

# Run migrations for staging
python manage.py migrate --settings=primepath_project.settings_staging
print_status "Migrations complete"

# Collect static files
python manage.py collectstatic --noinput --settings=primepath_project.settings_staging
print_status "Static files collected"

# Create superuser for staging
echo -e "\n9. Creating Staging Superuser..."
python manage.py shell --settings=primepath_project.settings_staging << 'PYTHON'
from django.contrib.auth.models import User
if not User.objects.filter(username='staging_admin').exists():
    User.objects.create_superuser('staging_admin', 'admin@staging.primepath.edu', 'Staging123!')
    print("✅ Staging admin created: username='staging_admin', password='Staging123!'")
else:
    print("⚠️ Staging admin already exists")
PYTHON

# Summary
echo -e "\n================================================"
echo -e "${GREEN}STAGING DEPLOYMENT READY!${NC}"
echo "================================================"
echo ""
echo "📁 Files Created:"
echo "   - settings_staging.py"
echo "   - requirements_staging.txt"
echo "   - .env.staging"
echo "   - Dockerfile.staging"
echo "   - docker-compose.staging.yml"
echo "   - run_staging.sh"
echo "   - nginx_staging.conf"
echo ""
echo "🚀 To Start Staging Server:"
echo "   ./run_staging.sh"
echo ""
echo "🐳 To Use Docker:"
echo "   docker-compose -f docker-compose.staging.yml up"
echo ""
echo "🔐 Staging Admin:"
echo "   Username: staging_admin"
echo "   Password: Staging123!"
echo ""
echo "🌐 Access staging at:"
echo "   http://localhost:8000 (local)"
echo "   http://staging.primepath.edu (configured domain)"
echo ""
print_status "Deployment script complete!"