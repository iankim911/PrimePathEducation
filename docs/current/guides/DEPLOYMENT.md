# PrimePath Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Production Server Setup](#production-server-setup)
3. [Database Configuration](#database-configuration)
4. [Application Deployment](#application-deployment)
5. [Web Server Configuration](#web-server-configuration)
6. [SSL/HTTPS Setup](#sslhttps-setup)
7. [Environment Variables](#environment-variables)
8. [Static Files & Media](#static-files--media)
9. [Process Management](#process-management)
10. [Monitoring & Logging](#monitoring--logging)
11. [Backup & Recovery](#backup--recovery)
12. [Troubleshooting](#troubleshooting)
13. [Security Checklist](#security-checklist)

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04/22.04 LTS (recommended) or similar Linux distribution
- **Python**: 3.9 or higher
- **RAM**: Minimum 2GB, recommended 4GB+
- **Storage**: Minimum 20GB for application and data
- **CPU**: 2+ cores recommended

### Required Software

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.9 python3.9-venv python3.9-dev python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis (for caching and Celery)
sudo apt install redis-server -y

# Install Nginx
sudo apt install nginx -y

# Install Git
sudo apt install git -y

# Install supervisor (for process management)
sudo apt install supervisor -y

# Install certbot (for SSL)
sudo apt install certbot python3-certbot-nginx -y
```

## Production Server Setup

### 1. Create Application User

```bash
# Create a dedicated user for the application
sudo adduser primepath
sudo usermod -aG sudo primepath

# Switch to the application user
sudo su - primepath
```

### 2. Clone Repository

```bash
cd /home/primepath
git clone https://github.com/yourusername/PrimePath.git
cd PrimePath
```

### 3. Setup Virtual Environment

```bash
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

## Database Configuration

### PostgreSQL Setup

```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE primepath_db;
CREATE USER primepath_user WITH PASSWORD 'strong_password_here';
ALTER ROLE primepath_user SET client_encoding TO 'utf8';
ALTER ROLE primepath_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE primepath_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE primepath_db TO primepath_user;
\q
```

### Configure Database Connection

Update your `.env` file:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=primepath_db
DB_USER=primepath_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=5432
```

## Application Deployment

### 1. Environment Configuration

```bash
cd /home/primepath/PrimePath
cp .env.example .env

# Edit .env with production values
nano .env
```

Essential production settings:
```bash
# Django Settings
SECRET_KEY=your-production-secret-key  # Generate new one!
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (as configured above)
DATABASE_URL=postgres://primepath_user:password@localhost/primepath_db

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Static/Media
STATIC_ROOT=/home/primepath/PrimePath/staticfiles
MEDIA_ROOT=/home/primepath/PrimePath/media
```

### 2. Generate Secret Key

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 3. Run Migrations

```bash
cd primepath_project
python manage.py migrate --settings=primepath_project.settings_production
python manage.py createsuperuser --settings=primepath_project.settings_production
python manage.py collectstatic --noinput --settings=primepath_project.settings_production
```

### 4. Create Production Settings

Create `primepath_project/settings_production.py`:
```python
from .settings_sqlite import *
import os

DEBUG = False

# Security
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL')
    )
}

# Static files
STATIC_ROOT = '/home/primepath/PrimePath/staticfiles'
MEDIA_ROOT = '/home/primepath/PrimePath/media'

# Security headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

## Web Server Configuration

### Gunicorn Setup

Create `/home/primepath/PrimePath/gunicorn_config.py`:
```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 2
preload_app = True
accesslog = "/home/primepath/PrimePath/logs/gunicorn_access.log"
errorlog = "/home/primepath/PrimePath/logs/gunicorn_error.log"
loglevel = "info"
```

### Nginx Configuration

Create `/etc/nginx/sites-available/primepath`:
```nginx
upstream primepath_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (will be added by certbot)
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    client_max_body_size 50M;

    # Static files
    location /static/ {
        alias /home/primepath/PrimePath/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/primepath/PrimePath/media/;
        expires 7d;
    }

    # Application
    location / {
        proxy_pass http://primepath_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/primepath /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/HTTPS Setup

### Using Let's Encrypt

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run

# Add to crontab for auto-renewal
sudo crontab -e
# Add: 0 0,12 * * * certbot renew --quiet
```

## Process Management

### Supervisor Configuration

Create `/etc/supervisor/conf.d/primepath.conf`:
```ini
[program:primepath]
command=/home/primepath/PrimePath/venv/bin/gunicorn 
    --config /home/primepath/PrimePath/gunicorn_config.py
    primepath_project.wsgi:application
directory=/home/primepath/PrimePath/primepath_project
user=primepath
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/primepath/PrimePath/logs/supervisor.log
environment=PATH="/home/primepath/PrimePath/venv/bin",
    DJANGO_SETTINGS_MODULE="primepath_project.settings_production"

[program:primepath-celery]
command=/home/primepath/PrimePath/venv/bin/celery 
    -A primepath_project worker -l info
directory=/home/primepath/PrimePath/primepath_project
user=primepath
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/primepath/PrimePath/logs/celery.log

[program:primepath-celery-beat]
command=/home/primepath/PrimePath/venv/bin/celery 
    -A primepath_project beat -l info
directory=/home/primepath/PrimePath/primepath_project
user=primepath
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/primepath/PrimePath/logs/celery-beat.log
```

Start services:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start primepath:*
```

## Monitoring & Logging

### Setup Log Directory

```bash
mkdir -p /home/primepath/PrimePath/logs
touch /home/primepath/PrimePath/logs/{django.log,gunicorn_access.log,gunicorn_error.log,supervisor.log,celery.log}
```

### Log Rotation

Create `/etc/logrotate.d/primepath`:
```
/home/primepath/PrimePath/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 640 primepath primepath
    sharedscripts
    postrotate
        supervisorctl restart primepath:*
    endscript
}
```

### Health Monitoring

Create a health check script `/home/primepath/PrimePath/health_check.sh`:
```bash
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health/)
if [ $response -eq 200 ]; then
    echo "Application is healthy"
else
    echo "Application is down! Response code: $response"
    # Send alert (email, Slack, etc.)
fi
```

Add to crontab:
```bash
*/5 * * * * /home/primepath/PrimePath/health_check.sh
```

## Backup & Recovery

### Database Backup

Create `/home/primepath/backup_db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/home/primepath/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="primepath_db"

mkdir -p $BACKUP_DIR
pg_dump -U primepath_user -h localhost $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /home/primepath/backup_db.sh
```

### Media Files Backup

```bash
#!/bin/bash
BACKUP_DIR="/home/primepath/backups"
DATE=$(date +%Y%m%d)

tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /home/primepath/PrimePath/media/

# Keep only last 7 days
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +7 -delete
```

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   ```bash
   # Check if Gunicorn is running
   sudo supervisorctl status
   
   # Check logs
   tail -f /home/primepath/PrimePath/logs/gunicorn_error.log
   ```

2. **Static files not loading**
   ```bash
   python manage.py collectstatic --noinput --settings=primepath_project.settings_production
   sudo systemctl reload nginx
   ```

3. **Database connection errors**
   ```bash
   # Test database connection
   python manage.py dbshell --settings=primepath_project.settings_production
   ```

4. **Permission errors**
   ```bash
   # Fix ownership
   sudo chown -R primepath:primepath /home/primepath/PrimePath/
   
   # Fix permissions
   chmod 755 /home/primepath/PrimePath
   chmod -R 755 /home/primepath/PrimePath/staticfiles
   chmod -R 755 /home/primepath/PrimePath/media
   ```

## Security Checklist

### Pre-Deployment

- [ ] Generate new SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Remove default passwords
- [ ] Update all dependencies

### Post-Deployment

- [ ] Test SSL configuration
- [ ] Verify security headers
- [ ] Check file permissions
- [ ] Enable firewall (ufw)
- [ ] Setup fail2ban
- [ ] Configure backups
- [ ] Setup monitoring
- [ ] Document admin credentials
- [ ] Test disaster recovery

### Firewall Configuration

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## Maintenance

### Update Application

```bash
cd /home/primepath/PrimePath
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd primepath_project
python manage.py migrate --settings=primepath_project.settings_production
python manage.py collectstatic --noinput --settings=primepath_project.settings_production
sudo supervisorctl restart primepath:*
```

### Monitor Resources

```bash
# Check disk space
df -h

# Check memory
free -h

# Check processes
htop

# Check logs
tail -f /home/primepath/PrimePath/logs/*.log
```

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_session_student ON placement_test_studentsession(student_name);
CREATE INDEX idx_exam_active ON placement_test_exam(is_active);

-- Analyze tables
ANALYZE;
```

### Caching with Redis

Configure in settings:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### CDN for Static Files (Optional)

Consider using CloudFlare or AWS CloudFront for static file delivery.

## Support

For deployment support:
1. Check logs in `/home/primepath/PrimePath/logs/`
2. Review this deployment guide
3. Contact technical support
4. Submit issues on GitHub

---

**Deployment Guide Version**: 1.0.0 | **Last Updated**: August 13, 2025