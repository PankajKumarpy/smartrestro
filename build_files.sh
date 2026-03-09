#!/bin/bash
# Build script for Vercel deployment
# This runs during the Vercel build phase to collect all static files
# (including Django admin CSS/JS) into the staticfiles/ directory
# so Whitenoise can serve them.

set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Build complete."
