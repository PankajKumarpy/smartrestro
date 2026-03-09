from __future__ import annotations

import os

from .base import *  # noqa: F403

DEBUG = env("DEBUG", default=False)  # noqa: F405

# ----------------------------------------------------------------
# Security – Vercel terminates SSL at the edge and forwards
# requests over HTTP internally, so SECURE_SSL_REDIRECT must be
# OFF or it creates an infinite redirect loop.
# ----------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False   # Vercel handles HTTPS at the edge

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 30)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)  # noqa: F405
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)  # noqa: F405

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

# ----------------------------------------------------------------
# Vercel – auto-trust the deployment domain
# VERCEL_URL is injected automatically by Vercel at build/runtime
# as the unique deployment hostname without the https:// prefix.
# ----------------------------------------------------------------
_vercel_url = os.environ.get("VERCEL_URL", "")  # e.g. smartrestro-abc.vercel.app

ALLOWED_HOSTS = list(ALLOWED_HOSTS) + [".vercel.app", "localhost", "127.0.0.1"]  # noqa: F405

if _vercel_url:
    ALLOWED_HOSTS.append(_vercel_url)
    CSRF_TRUSTED_ORIGINS = list(CSRF_TRUSTED_ORIGINS) + [f"https://{_vercel_url}"]  # noqa: F405

# Also trust any custom domain passed via env
_custom_domain = os.environ.get("CUSTOM_DOMAIN", "")
if _custom_domain:
    ALLOWED_HOSTS.append(_custom_domain)
    CSRF_TRUSTED_ORIGINS = list(CSRF_TRUSTED_ORIGINS) + [f"https://{_custom_domain}"]  # noqa: F405
