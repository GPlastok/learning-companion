# Authentication and profile management: refinement

## Context

Wire up Django's built-in auth with a custom User model, so people can sign up, log in
and log out, and add a Profile linked to the user with a name, a cohort and a list of
focus-area tags. The profile page shows only the logged-in user's own data. The project is
the ticket-1 scaffold: one `core` app with a placeholder home page, no models, no
migrations and no auth routes yet. Branch: none yet (on `main`).

Source: #3 (https://github.com/GPlastok/learning-companion/issues/3)

## Progress

Refinement done on 2026-10-01. Nothing planned or built yet. Next: the user answers the
open questions, then a plan is written.
Plan written on 2026-10-01: plans/feature-authentication-and-profile-management-plan.md.
Built on 2026-10-01, see plans/feature-authentication-and-profile-management-plan.md.
Plan written on 2026-10-01: plans/feature-authentication-and-profile-management-plan.md (updated for review R7).
Plan written on 2026-10-01: plans/feature-authentication-and-profile-management-plan.md (updated for review R10).

## Acceptance criteria

### Supplied

- [ ] Confirm you can sign up, log out, and log back in, and that the profile page only shows your own data.

### Added by refinement

- [ ] Signing up with invalid data (a username already taken, passwords that don't match, a password the validators reject) shows the errors on the form and creates no user
- [ ] Logging in with a wrong password shows an error and leaves the visitor logged out
- [ ] A visitor who is not logged in sees no profile data when they open the profile page
- [ ] After logging out, the profile page no longer shows the previous user's data
- [ ] A logged-in user stays logged in after reloading a page
- [ ] A user whose profile has no focus areas sees the profile page without errors

## Files and functions

Routing and views:

- `learning_companion/urls.py:19-26`: imports only `path` (no `include`); two routes,
  `path("", views.home, name="home")` and `path("admin/", admin.site.urls)`. No auth URLs,
  no app-level `urls.py`, no namespaces.
- `core/views.py:4-5`: `home(request)` renders `core/home.html`. Function-based, no
  decorators, no context. The only view; no forms module.

Templates:

- `theme/templates/base.html`: loads `static tailwind_tags django_htmx` (line 1), a fixed
  `<title>Learning Companion</title>` (line 5), `{% tailwind_css %}` (line 9),
  `{% htmx_script %}` (line 10), one block `content` inside `<div class="container
  mx-auto">` (lines 15-17). No nav, no auth links, no messages display, no `csrf_token`,
  no `hx-headers`.
- `core/templates/core/home.html`: extends `base.html`, a section with an h1 and "Nothing
  here yet.".
- No `registration/` template directory anywhere.

Settings (`learning_companion/settings.py`):

- `INSTALLED_APPS` (38-49): Django's admin, auth, contenttypes, sessions, messages,
  staticfiles, then `tailwind`, `theme`, `django_htmx`, `core`.
- `MIDDLEWARE` (53-62): Session, Csrf, Authentication, Message, and `HtmxMiddleware` last.
- `TEMPLATES` (66-79): `DIRS: []`, `APP_DIRS: True`, context processors request, auth,
  messages.
- `AUTH_PASSWORD_VALIDATORS` (95-108): Django's four defaults.
- `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"` (131).
- Not set: `AUTH_USER_MODEL`, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`.

App:

- `core/models.py:1`, `core/admin.py:1`: stub comments only.
- `core/apps.py:4-6`: `CoreConfig`, `default_auto_field = BigAutoField`, `name = "core"`.
- `core/migrations/`: only `__init__.py`. No `0001` migration.

## Current data shapes

No models exist. No `Tag`, `Profile` or `User` class, no `AbstractUser`, no M2M, no
signals anywhere in the project.

Database, `settings.py:87-89`:

```python
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}
```

A local `db.sqlite3` (131072 bytes, 2026-10-01 14:17) exists and is gitignored
(`.gitignore:9`). It wasn't opened; its size fits Django's built-in migrations having been
applied with the default `auth.User`. Django documents that switching `AUTH_USER_MODEL`
after those migrations have run needs a fresh database. The test database is unaffected:
pytest-django builds its own each run.

Planned in CLAUDE.md (Stack): tags as a `Tag` model with an M2M relation, not
`ArrayField`, so per-tag queries and counts work on SQLite and PostgreSQL.

`.env.example`: `SECRET_KEY`, `DEBUG=True`, `DATABASE_URL=sqlite:///db.sqlite3`,
`OPENAI_API_KEY`. No auth-related variables.

## Tests

- Runner: pytest 9.1.1 + pytest-django 4.14.0. `pyproject.toml:6-8` sets
  `DJANGO_SETTINGS_MODULE = "learning_companion.settings_test"` and `testpaths =
  ["tests"]`; no `addopts`, markers or `--reuse-db`.
- Commands: `make test` (`.venv/bin/python -m pytest $(ARGS)`), `make test ARGS="-k
  test_ac3"`.
- `learning_companion/settings_test.py:1-8`: sets `SECRET_KEY` and `ENV_FILE=os.devnull`,
  then `from .settings import *`. No test password hasher.
- Files: `tests/test_docs.py` (AC11 of ticket 1), `tests/test_home.py` (AC2, AC3 via the
  `client` fixture), `tests/test_settings.py` (settings loaded in a subprocess via
  `load_settings(tmp_path, **env)`, parametrized AC5), `tests/test_setup.py` (AC8). No
  `tests/__init__.py`, no `conftest.py`, no factories.
- Typical test, `tests/test_home.py:4-13`:

  ```python
  def test_ac2_home_page_is_styled_by_tailwind(client):
      response = client.get("/")

      assert response.status_code == 200
      template_names = [t.name for t in response.templates]
      assert "core/home.html" in template_names
      ...
  ```

- Gaps: no test touches the database (no `django_db` mark, no `db` fixture), no user
  fixtures, no auth or profile tests. `django_user_model`, `client.force_login` and
  `admin_client` are available from pytest-django but unused.
- Test-only dependencies: no factory_boy, model_bakery or coverage.
- Other checks: `make lint` (`ruff check .`, default rules, `EXE002` ignored) and
  `make format`. No type checker, no build target, no CI workflow. `/ship` runs
  `make test` and `make lint`.

## Patterns to follow

- Views are function-based and call `render(request, "<app>/<name>.html")`
  (`core/views.py:4-5`).
- Routes are registered in the root `urls.py` with a short `name=` and no namespace
  (`learning_companion/urls.py:24`).
- App templates live at `<app>/templates/<app>/<name>.html`, extend `base.html` and fill
  `{% block content %}` (`core/templates/core/home.html:1,3`), styled with inline Tailwind
  utility classes.
- Tests are named `test_ac<N>_<behaviour>`, one `@pytest.mark.parametrize` test per table
  of inputs (CLAUDE.md, Tests; `tests/test_settings.py:46`), use built-in fixtures and plain
  asserts on `status_code`, `response.templates` and decoded content
  (`tests/test_home.py:4-13`).
- Tests live in top-level `tests/`, not in the app (`pyproject.toml:8`).
- Constraints: stack fixed in CLAUDE.md (raise changes as a question); tags as a `Tag` M2M
  model; HTMX is wired but CLAUDE.md names the goals ticket as its first user; nothing is
  installed that the plan doesn't list; Claude can't read or write `.env` or `.env.*`.

## Open questions

1. Where do the custom User, Profile and Tag models live: in the existing `core` app or in
   a new app (for example `accounts`)?
2. Does the custom User add anything beyond Django's `AbstractUser`, or is it a plain
   subclass kept for later changes?
3. Do people log in with a username or with an email address?
4. Which fields does the sign-up form ask for: only username and password, or also the
   profile fields (name, cohort, focus areas)?
5. Is a Profile created automatically for every new user, or only when the user fills it
   in? What does the profile page show before it's filled in?
6. Is the profile's "name" its own field, or Django's `first_name`/`last_name` on the User?
   Which profile fields are required?
7. What is a cohort: free text, a fixed list of choices, or its own model?
8. Focus-area tags: can a user type new tags freely, or pick from a set? Is the `Tag` model
   shared across users, and is it the same model later tickets will use for goals and
   resources? Are tag names case-insensitive and unique?
9. Does "profile management" include editing the profile in this ticket, or only viewing
   it?
10. What is the profile page's URL: one page for "my profile" (`/profile/`), or a page per
    user (`/profile/<id>/`)? If per user, what does someone get when they open another
    user's profile: 404, 403 or a redirect?
11. What does a visitor who is not logged in get on the profile page: a redirect to the
    login page, or something else?
12. After sign-up, is the new user logged in straight away? Where do sign-up, login and
    logout each send the user (home, profile, login page)?
13. Should `base.html` get a nav with sign-up, login, logout and profile links, and should
    the home page change for a logged-in user?
14. Django 5's `LogoutView` only accepts POST. Is logout a form button in the nav, or
    something else?
15. Are password reset, password change and email verification in scope, or later tickets?
16. Should User, Profile and Tag be registered in the admin?
17. The local `db.sqlite3` already holds the built-in migrations. Is it fine to delete and
    recreate it, or is there data in it to keep?
18. The supplied criterion says "Confirm you can ...", which reads as a manual check. Should
    it be covered by automated tests, a manual check, or both?
