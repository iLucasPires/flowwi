#!/bin/sh

echo "Creating Migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate
