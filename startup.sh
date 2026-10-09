#!/bin/bash
# Azure App Service startup script for Python Django application
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=120 config.wsgi:application
