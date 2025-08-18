# Fix for 504 Gateway Timeout Error

## 🔴 Problem
Getting "504 Gateway Time-out" errors when performing multiple tasks quickly in RoutineTest module.

## 🔍 Root Causes

### 1. **Database Query Inefficiency**
The schedule matrix view is creating many database queries in loops:
```python
# Current issue in schedule_matrix.py:
for assignment in assigned_classes:  # Loop 1
    for month in months:  # Loop 2 (12 iterations)
        matrix_cell, created = ExamScheduleMatrix.get_or_create_cell(...)  # DB query

for assignment in assigned_classes:  # Loop 3
    for quarter in quarters:  # Loop 4 (4 iterations)
        matrix_cell, created = ExamScheduleMatrix.get_or_create_cell(...)  # DB query
```

This creates (classes × 16) database queries per page load!

### 2. **Synchronous Blocking Operations**
- Each `get_or_create_cell` is a blocking database operation
- No query optimization or caching
- No connection pooling in SQLite

### 3. **Development Server Limitations**
- Django's development server is single-threaded
- SQLite locks the entire database during writes
- No request queuing or load balancing

## ✅ Immediate Solutions

### Quick Fix 1: Increase Timeout (Temporary)
```nginx
# If using nginx proxy
location / {
    proxy_read_timeout 300;  # Increase from 60 to 300 seconds
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
}
```

### Quick Fix 2: Optimize Database Queries
```python
# Use bulk_create and prefetch_related
from django.db import transaction

@transaction.atomic
def schedule_matrix_view(request):
    # Prefetch all related data
    assigned_classes = TeacherClassAssignment.objects.filter(
        teacher=teacher,
        is_active=True
    ).select_related('teacher').prefetch_related('exams')
    
    # Bulk create matrix cells
    cells_to_create = []
    for assignment in assigned_classes:
        # Collect all cells to create
        # ... 
    ExamScheduleMatrix.objects.bulk_create(cells_to_create, ignore_conflicts=True)
```

### Quick Fix 3: Add Caching
```python
from django.core.cache import cache

def get_class_curriculum_mapping(class_code, academic_year):
    cache_key = f"curriculum_map_{class_code}_{academic_year}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # ... existing logic ...
    cache.set(cache_key, curriculum_info, 300)  # Cache for 5 minutes
    return curriculum_info
```

## 🚀 Proper Solution

### Step 1: Install Database Connection Pooling
```bash
pip install django-db-pool
```

### Step 2: Use PostgreSQL Instead of SQLite (Production)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'primepath',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

### Step 3: Implement Async Views (Django 4.1+)
```python
import asyncio
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
async def schedule_matrix_view(request):
    # Async implementation
    ...
```

## 🔧 Immediate Optimization for Current Code

Create this optimized version: