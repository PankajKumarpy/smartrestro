#!/usr/bin/env bash
# ---------------------------------------------------------------
# build_files.sh  –  Vercel Build Command
#
# Set this as the Build Command in Vercel project settings:
#   bash build_files.sh
#
# Environment variables required in Vercel dashboard:
#   DJANGO_SETTINGS_MODULE = config.settings.prod
#   SECRET_KEY             = <your-secret-key>
#   DATABASE_URL           = <postgres-connection-string>
#   ALLOWED_HOSTS          = <your-app>.vercel.app
#   CSRF_TRUSTED_ORIGINS   = https://<your-app>.vercel.app
#   DEBUG                  = False
# ---------------------------------------------------------------
set -e

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo "=== Collecting static files (admin CSS/JS + app assets) ==="
python manage.py collectstatic --noinput --clear

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Build complete ==="
