#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Apply any outstanding database migrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='jhamir14').exists():
    User.objects.create_superuser('jhamir14', 'admin@example.com', 'jhamirquispe')
    print('✅ Superuser created: jhamir14 / jhamirquispe')
else:
    print('ℹ️ Superuser already exists')
"

# Convert static asset files
python manage.py collectstatic --no-input