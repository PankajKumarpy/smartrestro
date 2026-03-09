from __future__ import annotations

import os

from .base import *  # noqa: F403

DEBUG = env("DEBUG", default=False)  # noqa: F405

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 30)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)  # noqa: F405
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)  # noqa: F405

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"


# ------------------------------------------------------------
# Vercel – automatically trust the deployment URL
# Vercel sets VERCEL_URL to the unique deployment hostname,
# e.g. "smartrestro-abc123.vercel.app". We add it so Django
# doesn't reject requests with a 400 Bad Request.
# ------------------------------------------------------------
_vercel_url = os.environ.get("VERCEL_URL", "")  # e.g. smartrestro-xyz.vercel.app

if _vercel_url:
    ALLOWED_HOSTS = list(ALLOWED_HOSTS) + [_vercel_url]  # noqa: F405
    CSRF_TRUSTED_ORIGINS = list(CSRF_TRUSTED_ORIGINS) + [f"https://{_vercel_url}"]  # noqa: F405

# Always allow .vercel.app wildcard as a safety net
ALLOWED_HOSTS = list(ALLOWED_HOSTS) + [".vercel.app"]  # noqa: F405
