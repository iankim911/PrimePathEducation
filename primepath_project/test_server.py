import sys
import os

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("\nChecking Django installation...")

try:
    import django
    print(f"Django version: {django.get_version()}")
    print("Django is installed correctly!")
except ImportError as e:
    print("ERROR: Django is not installed!")
    print(f"Error details: {e}")
    print("\nPlease install Django by running:")
    print("pip install Django==5.0.1")
    sys.exit(1)

print("\nChecking if manage.py exists...")
if os.path.exists('manage.py'):
    print("manage.py found!")
else:
    print("ERROR: manage.py not found in current directory!")
    print("Make sure you're in the primepath_project directory")
    sys.exit(1)

print("\nTrying to import Django settings...")
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings')
    django.setup()
    print("Django settings loaded successfully!")
except Exception as e:
    print(f"ERROR loading Django settings: {e}")
    sys.exit(1)

print("\nEverything looks good! Now try running:")
print("python manage.py runserver")