#!/bin/bash

# Set default port if PORT is not set
PORT=${PORT:-8000}

# Run migrations
echo "Running Django migrations..."
python manage.py migrate

# Start the Django application
echo "Starting Django application on port $PORT"
exec gunicorn --bind 0.0.0.0:$PORT --workers 3 exeo_portal.wsgi:application
