"""Settings for the test suite: fixed test values, no local .env."""

import os

os.environ.setdefault("SECRET_KEY", "test-only-not-secret")
os.environ.setdefault("ENV_FILE", os.devnull)

from .settings import *

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
