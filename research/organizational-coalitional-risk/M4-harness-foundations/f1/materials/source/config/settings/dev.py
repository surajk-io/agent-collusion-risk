"""Local development settings."""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Easier local debugging of API errors.
REST_FRAMEWORK["EXCEPTION_HANDLER"] = (  # noqa: F405
    "rest_framework.views.exception_handler"
)

# Console email backend so invitation emails are printed, not sent.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
