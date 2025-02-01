#!/bin/bash

set -e

# Function to check if postgres is ready
postgres_ready() {
    nc -z $POSTGRES_HOST $POSTGRES_PORT
}

# Wait for PostgreSQL
until postgres_ready; do
  echo >&2 "Postgres is unavailable - sleeping"
  sleep 1
done

echo >&2 "Postgres is up - executing migrations"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start server
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000 