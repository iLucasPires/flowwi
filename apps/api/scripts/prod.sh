#!/bin/sh

echo "Applying migrations..."
python manage.py migrate

echo "Creating superuser..."
python manage.py createsuperuser --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec daphne -b 0.0.0.0 -p 8000 server.asgi:application
