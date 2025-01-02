#!/bin/bash

# Create staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start the application (this will be overridden by Procfile)
exec gunicorn backend.wsgi:application --forwarded-allow-ips "*"
