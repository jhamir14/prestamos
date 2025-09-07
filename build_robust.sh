#!/usr/bin/env bash
# Robust build script for Render with Python 3.13
set -e

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing psycopg dependencies..."
pip install psycopg[binary]==3.1.18

echo "Installing other dependencies..."
pip install Django==5.2.5
pip install gunicorn==21.2.0
pip install whitenoise==6.6.0
pip install dj-database-url==2.1.0
pip install djangorestframework==3.16.1

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
