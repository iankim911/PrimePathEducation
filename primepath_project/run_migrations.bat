@echo off
echo Running Django migrations...
echo.

:: Check for pending migrations
echo Checking for model changes...
python manage.py makemigrations
echo.

:: Apply migrations
echo Applying migrations...
python manage.py migrate
echo.

echo Migrations complete!
pause