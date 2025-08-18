# Deployment Checklist - RoutineTest

## Pre-Deployment Requirements

### 1. Environment Configuration
- [ ] Set production SECRET_KEY
- [ ] Set DEBUG=False in production settings
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up environment variables
- [ ] Configure ALLOWED_HOSTS

### 2. Database Setup
```bash
# Run migrations on production database
python manage.py migrate --settings=primepath_project.settings_production

# Create superuser for production
python manage.py createsuperuser --settings=primepath_project.settings_production

# Load initial data if needed
python manage.py loaddata initial_data.json --settings=primepath_project.settings_production
```

### 3. Static Files & Media
```bash
# Collect static files
python manage.py collectstatic --noinput --settings=primepath_project.settings_production

# Ensure media directory exists and has proper permissions
mkdir -p media/routine_exams
chmod 755 media/routine_exams
```

### 4. Security Hardening
- [ ] Enable HTTPS/SSL certificate
- [ ] Configure CSRF settings
- [ ] Set secure cookie settings
- [ ] Enable security middleware
- [ ] Configure CORS if needed

### 5. Performance Optimization
- [ ] Enable database connection pooling
- [ ] Configure caching (Redis/Memcached)
- [ ] Set up CDN for static files
- [ ] Enable gzip compression
- [ ] Configure database indexes

### 6. Monitoring & Logging
- [ ] Set up error tracking (Sentry/Rollbar)
- [ ] Configure application logs
- [ ] Set up uptime monitoring
- [ ] Configure backup strategy

## Deployment Steps

### Option 1: Traditional Server (Apache/Nginx + Gunicorn)
```bash
# Install dependencies
pip install gunicorn psycopg2-binary redis

# Test with Gunicorn
gunicorn primepath_project.wsgi:application --bind 0.0.0.0:8000

# Configure Nginx
sudo nano /etc/nginx/sites-available/primepath

# Enable site
sudo ln -s /etc/nginx/sites-available/primepath /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

# Set up systemd service
sudo nano /etc/systemd/system/gunicorn.service
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### Option 2: Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "primepath_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```bash
# Build and run
docker build -t routinetest .
docker run -d -p 8000:8000 --env-file .env routinetest
```

### Option 3: Platform-as-a-Service (Heroku/Railway)
```bash
# Heroku deployment
heroku create primepath-routinetest
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

## Post-Deployment Verification

### 1. Smoke Tests
- [ ] Admin can login
- [ ] Teacher can login
- [ ] Student can login
- [ ] Create a test class
- [ ] Upload a test exam
- [ ] Assign exam to class
- [ ] Student can take exam
- [ ] Results calculate correctly
- [ ] Export works

### 2. Load Testing
```bash
# Using locust
pip install locust
locust -f loadtest.py --host=https://your-domain.com
```

### 3. Security Scan
```bash
# Check for vulnerabilities
pip install safety
safety check

# Django security check
python manage.py check --deploy
```

## User Training & Documentation

### 1. Create User Guides
- [ ] Admin guide (PDF)
- [ ] Teacher guide (PDF)
- [ ] Student guide (PDF)
- [ ] Video tutorials

### 2. Initial Data Setup
- [ ] Create academic year
- [ ] Set up quarters (Q1-Q4)
- [ ] Load curriculum levels (44 levels)
- [ ] Create initial admin account
- [ ] Set up first classes

### 3. Support Structure
- [ ] Help desk email
- [ ] FAQ page
- [ ] Known issues list
- [ ] Update notification system

## Rollback Plan

### If Issues Occur:
1. **Database Backup**
   ```bash
   pg_dump primepath_prod > backup_$(date +%Y%m%d).sql
   ```

2. **Quick Rollback**
   ```bash
   git checkout v1.0-stable
   python manage.py migrate
   sudo systemctl restart gunicorn
   ```

3. **Emergency Contacts**
   - DevOps Lead: [Contact]
   - Database Admin: [Contact]
   - Security Team: [Contact]

## Go-Live Schedule

### Week 1: Staging Deployment
- Monday: Deploy to staging
- Tuesday-Wednesday: Internal testing
- Thursday: Fix identified issues
- Friday: User acceptance testing

### Week 2: Production Deployment
- Monday: Final backup and prep
- Tuesday: Deploy to production (off-peak hours)
- Wednesday: Monitor and support
- Thursday: Performance tuning
- Friday: Sign-off and handover

## Success Metrics

### Day 1 Metrics
- [ ] < 3 second page load
- [ ] Zero critical errors
- [ ] All users can login
- [ ] Core features working

### Week 1 Metrics
- [ ] 95% uptime
- [ ] < 5% error rate
- [ ] Positive user feedback
- [ ] No data loss

### Month 1 Metrics
- [ ] 400+ students onboarded
- [ ] 30+ teachers active
- [ ] 1000+ exams taken
- [ ] < 1% support tickets

---
**Status**: READY FOR DEPLOYMENT
**Last Updated**: August 18, 2025