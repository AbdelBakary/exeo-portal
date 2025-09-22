#!/bin/bash
set -e

echo "Waiting for database to be ready..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Loading initial data..."
python manage.py loaddata fixtures/initial_data.json || echo "No initial data to load"

echo "Database initialization completed!"
