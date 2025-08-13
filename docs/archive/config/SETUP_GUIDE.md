# PrimePath Setup Guide for Beginners

## 📋 Prerequisites Checklist

✅ Python 3.13.5 (Confirmed installed!)
❌ PostgreSQL (Need to install)
❌ pip (Python package manager)

## 🚀 Step-by-Step Setup Instructions

### Step 1: Install pip (if not already installed)
Open Command Prompt and run:
```bash
py -m ensurepip --upgrade
```

### Step 2: Navigate to Project Directory
```bash
cd "C:\Users\ianki\OneDrive\2. Projects\ClaudeCode_New\PrimePath_\primepath_project"
```

### Step 3: Install Django and Dependencies
```bash
py -m pip install -r ..\requirements.txt
```

### Step 4: Install PostgreSQL
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer
3. Remember your password for the 'postgres' user!
4. Default port is 5432

### Step 5: Create Database
After PostgreSQL is installed, open Command Prompt and run:
```bash
psql -U postgres
```
Enter your password, then run these SQL commands:
```sql
CREATE DATABASE primepath_db;
CREATE USER primepath_user WITH PASSWORD 'primepath_password';
GRANT ALL PRIVILEGES ON DATABASE primepath_db TO primepath_user;
\q
```

### Step 6: Run Django Migrations
```bash
py manage.py makemigrations
py manage.py migrate
```

### Step 7: Load Initial Data
```bash
py manage.py loaddata core/fixtures/curriculum_data.json
py manage.py populate_curriculum
```

### Step 8: Create Admin Account
```bash
py manage.py createsuperuser
```
Choose:
- Username: admin (or your choice)
- Email: your-email@example.com
- Password: (choose a strong password)

### Step 9: Start the Server
```bash
py manage.py runserver
```

### Step 10: Test It!
1. Open your browser
2. Go to: http://localhost:8000
3. You should see the PrimePath homepage
4. Go to: http://localhost:8000/admin
5. Log in with your superuser credentials

## 🎯 What to Test First

1. **Admin Panel** (http://localhost:8000/admin)
   - Can you log in?
   - Can you see all the models?

2. **Check Curriculum Levels**
   - In admin, go to "Curriculum levels"
   - You should see 45 levels (3 for each subprogram)

3. **Create a Test Teacher**
   - In admin, click "Teachers" → "Add Teacher"
   - Fill in the form and save

4. **Create a Placement Rule**
   - In admin, click "Placement rules" → "Add Placement rule"
   - Example: Grade 5, Top 20% → ASCENT NOVA Level 1

## 🚨 Common Issues & Solutions

### "psql not recognized"
- PostgreSQL isn't in your PATH
- Use the full path: `"C:\Program Files\PostgreSQL\16\bin\psql" -U postgres`

### "pip not found"
- Use `py -m pip` instead of just `pip`

### "Port 5432 already in use"
- PostgreSQL might already be running
- That's okay! Continue with the setup

### "Access denied for user primepath_user"
- Make sure you created the user in PostgreSQL
- Check the password matches in settings.py

## 📝 Notes for Beginners

- **migrations** = Instructions for creating database tables
- **fixtures** = Pre-made data to load into the database
- **superuser** = Admin account that can access everything
- **localhost:8000** = Your computer running the website locally

Ready? Start with Step 1!