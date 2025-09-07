#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install system dependencies for PostgreSQL
apt-get update
apt-get install -y libpq-dev

# Install Python dependencies
pip install -r requirements.txt

# Apply any outstanding database migrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
"

# Convert static asset files
python manage.py collectstatic --no-input