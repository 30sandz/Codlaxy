#!/bin/bash
set -e  # Exit on error

echo "Checking critical environment variables..."
if [ -z "$PORT" ]; then
    echo "ERROR: PORT environment variable is not set"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set"
    exit 1
fi

echo "Environment Information:"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "PORT: $PORT"
echo "Database URL exists: $(if [ ! -z "$DATABASE_URL" ]; then echo "Yes"; else echo "No"; fi)"
echo "Debug mode: $DEBUG"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Setting up site framework..."
python manage.py setup_site

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Checking Django configuration..."
python manage.py check --deploy

echo "Starting Gunicorn on port $PORT..."
exec gunicorn codlaxy.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance 