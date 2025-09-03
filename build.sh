#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DJANGO_SETTINGS_MODULE=gestion_prestamos.settings
export DEBUG=False

# Run migrations
cd gestion_prestamos
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

cd ..
