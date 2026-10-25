"""Test settings: fast, isolated, in-memory."""

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["*", "testserver"]

# In-memory sqlite — no file I/O, fresh per test session.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Fast, deterministic password hashing for tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Plain static storage in tests (no manifest/compression, no missing-dir warning).
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# WhiteNoise scans STATIC_ROOT at startup; it's irrelevant to tests, so drop it.
MIDDLEWARE = [m for m in MIDDLEWARE if "whitenoise" not in m.lower()]  # noqa: F405

# Drop the browsable API renderer in tests for clean JSON-only responses.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
)
