from .base import *  # noqa: F403

# Development-friendly defaults (override via .env)
DEBUG = env("DEBUG", default=True)  # noqa: F405

ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])  # noqa: F405

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

