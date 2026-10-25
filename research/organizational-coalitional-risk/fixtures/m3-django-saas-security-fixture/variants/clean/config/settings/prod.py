"""Production settings.

Expects a real DATABASE_URL (Postgres), a strong SECRET_KEY, and explicit
ALLOWED_HOSTS via the environment.
"""

from .base import *  # noqa: F403

DEBUG = False

# Fail loudly if a real secret was not provided.
SECRET_KEY = env("SECRET_KEY")  # noqa: F405

# Security hardening.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Redis-backed cache when REDIS_URL is configured.
if REDIS_URL:  # noqa: F405
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,  # noqa: F405
        }
    }

EMAIL_BACKEND = env(  # noqa: F405
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
