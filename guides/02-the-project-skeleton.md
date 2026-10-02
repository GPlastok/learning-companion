# 2. The project skeleton

Ticket #1 set up the empty Django project. This chapter explains its parts, because every later feature plugs into them.

## Project versus app

Django splits code into two levels.

The **project** is the whole website. Ours is `learning_companion/`. It holds the settings, the root URL list and the entry points a web server uses (`wsgi.py`, `asgi.py`). There is exactly one.

An **app** is one area of the site: its models, views, templates and admin. You can have many. Ours so far:

| App | Holds | Created by |
|---|---|---|
| `core` | the home page and `Tag` | ticket #1 (`manage.py startapp core`) |
| `theme` | `base.html` and the Tailwind CSS sources | ticket #1 (`manage.py tailwind init`) |
| `accounts` | users, profiles, cohorts, login and sign-up | ticket #3 (`manage.py startapp accounts`) |

A `learning` app for goals, sessions and resources comes with ticket #4 (decision D1).

An app only exists for Django once it's listed in `INSTALLED_APPS`:

```python
# learning_companion/settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tailwind",
    "theme",
    "django_htmx",
    "core",
    "accounts",
]
```

The `django.contrib.*` entries are apps too. They ship with Django. `auth` gives you users, passwords and login. `admin` gives you the back office (chapter 9). `sessions` remembers who's logged in between requests.

## `manage.py`

`manage.py` is Django's command line. You'll use these the most:

| Command | Does |
|---|---|
| `manage.py runserver` | start the development server (`make dev` does this, plus Tailwind) |
| `manage.py startapp <name>` | create a new app folder |
| `manage.py makemigrations` | write migration files from model changes (chapter 3) |
| `manage.py migrate` | apply migrations to the database (`make migrate`) |
| `manage.py createsuperuser` | create an admin account |
| `manage.py shell` | a Python prompt with Django loaded |

## Settings from the environment

Secrets don't belong in code. The settings read them from environment variables, or from a `.env` file, using **django-environ**:

```python
env = environ.Env()
environ.Env.read_env(env("ENV_FILE", default=str(BASE_DIR / ".env")))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=True)
```

`SECRET_KEY` has no default. If it's missing, Django refuses to start, which is what you want. `DEBUG` defaults to `True` to keep development easy. Production must set `DEBUG=False`.

The database works the same way:

```python
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}
```

`env.db` turns a URL like `sqlite:///db.sqlite3` or `postgres://user:pw@host/db` into the dictionary Django expects. Switching to PostgreSQL later means changing one variable, not the code.

## Test settings

Tests use their own settings file, `learning_companion/settings_test.py`:

```python
os.environ.setdefault("SECRET_KEY", "test-only-not-secret")
os.environ.setdefault("ENV_FILE", os.devnull)

from .settings import *

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
```

It sets a throwaway key, points `ENV_FILE` at nothing so your real `.env` is ignored, and then loads the normal settings.

The last line was added in ticket #3. Real password hashing is deliberately slow, so that attackers can't guess quickly. In tests that slowness only costs time, so tests use the fast (and insecure) MD5 hasher. That's decision D21.

`pyproject.toml` tells pytest to use this file:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "learning_companion.settings_test"
testpaths = ["tests"]
```

## The Makefile

The Makefile is the menu of commands, so nobody has to remember the long versions:

```make
test:
	$(PY) -m pytest $(ARGS)

lint:
	$(VENV)/bin/ruff check .

migrate:
	$(PY) manage.py migrate
```

`$(PY)` is `.venv/bin/python`, so you never need to activate the virtual environment. `ARGS` passes extra options to pytest: `make test ARGS="-k test_ac8"` runs only the matching tests.

## Tailwind and HTMX

**Tailwind** is a CSS framework: you style elements with small utility classes like `text-3xl font-bold` right in the HTML. django-tailwind builds the CSS file. `make dev` runs the builder next to the server, so changes appear when you save.

**HTMX** lets a page update part of itself from the server without a JavaScript framework. `base.html` loads it on every page, but nothing uses it yet. The goals ticket (#4) is the first that will (decision D27).

Both are loaded in `theme/templates/base.html`:

```html
{% load static tailwind_tags django_htmx %}
...
    {% tailwind_css %}
    {% htmx_script %}
```

## Try it yourself

1. Run `make test`. Count the tests in the output (64 when this was written).
2. Run `make test ARGS="-k test_ac8 -v"`. Only the email-login tests run, with their names listed.
3. Open `.venv/bin/python manage.py shell` and type:

   ```python
   from django.conf import settings
   settings.INSTALLED_APPS
   settings.DATABASES["default"]["ENGINE"]
   ```

   You see the app list and `django.db.backends.sqlite3`.
