#!/usr/bin/env bash
# Final build script for Render with correct psycopg version
set -e

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing psycopg3 (latest version)..."
pip install psycopg[binary]==3.2.9

echo "Installing Django and other dependencies..."
pip install Django==5.2.5
pip install gunicorn==21.2.0
pip install whitenoise==6.6.0
pip install dj-database-url==2.1.0
pip install djangorestframework==3.16.1
pip install reportlab==4.0.8
pip install Pillow==10.4.0

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: admin / admin123')
else:
    print('ℹ️ Superuser already exists')
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
