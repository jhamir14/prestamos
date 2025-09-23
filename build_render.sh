#!/usr/bin/env bash
# Build script optimized for Render
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='jhamir14').exists():
    User.objects.create_superuser('jhamir14', 'admin@example.com', 'jhamirquispe')
    print('Superuser created: jhamir14')
else:
    print('Superuser already exists')
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
