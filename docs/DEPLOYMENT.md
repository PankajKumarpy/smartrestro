## Deployment Guide

This guide provides **local** and **production** setup steps for Smart RMS.

### 1) Local development (SQLite)

- Copy `.env.example` → `.env`
- Run:

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py loaddata fixtures\seed.json
.\.venv\Scripts\python manage.py createsuperuser
.\.venv\Scripts\python manage.py runserver
```

### 2) Local development (PostgreSQL)

Set `.env`:

```env
DEBUG=True
SECRET_KEY=your-dev-secret
DATABASE_URL=postgres://USER:PASSWORD@127.0.0.1:5432/smart_rms
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000
TIME_ZONE=Asia/Kolkata
```

Then:

```powershell
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py loaddata fixtures\seed.json
.\.venv\Scripts\python manage.py createsuperuser
.\.venv\Scripts\python manage.py runserver
```

### 3) Production (Linux recommended)

#### Environment variables

Set:

- `DJANGO_SETTINGS_MODULE=config.settings.prod`
- `DEBUG=False`
- `SECRET_KEY=<strong random value>`
- `ALLOWED_HOSTS=your-domain.com`
- `CSRF_TRUSTED_ORIGINS=https://your-domain.com`
- `DATABASE_URL=postgres://...`

#### Collect static files

```bash
python manage.py collectstatic --noinput
```

#### WSGI server

Run using a WSGI server (example using Gunicorn on Linux):

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Serve behind Nginx/Apache and terminate SSL at the proxy.

#### Notes

- Static files are handled via **WhiteNoise** (works great for small/medium deployments).
- Media uploads (`MEDIA_ROOT`) should be stored on disk or object storage depending on your hosting.
- Ensure database backups for production.

