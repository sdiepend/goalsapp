#!/bin/bash

# Create staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser (Set the DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD environment variables)
python manage.py createsuperuser --noinput

# Start the application (this will be overridden by Procfile)
exec gunicorn backend.wsgi:application --forwarded-allow-ips "*"
