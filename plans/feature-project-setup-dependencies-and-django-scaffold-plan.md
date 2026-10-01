# Project setup: dependencies and Django scaffold: TDD plan

## Context

Creates the Django project `learning_companion` with the decided stack wired up, a
placeholder home page, settings read from the environment, and a Makefile for every task.
Refinement: [feature-project-setup-dependencies-and-django-scaffold-refinement.md](feature-project-setup-dependencies-and-django-scaffold-refinement.md).
Source: #1. Branch: none yet. Create one off `main` before building (for example
`feature/1-project-setup`), since the build stops on the default branch.

In scope: project and app skeleton, requirements files, pyproject config, Makefile,
settings via django-environ, base template with Tailwind and HTMX, home page, CLAUDE.md
Commands section. Not in scope: auth, models, Dockerfile, PostgreSQL, any use of HTMX or
OpenAI beyond loading the script and reading the key.

## Progress

Plan written on 2026-10-01.
Reviewed on 2026-10-01, round 2: no rework. Manual checks pending: AC1, AC2, AC7, AC12. The user created `.env.example` and `.env` on 2026-10-01 (step 5, check 1). AC7 waits for their confirmation of the contents, since Claude can't read `.env*`. Round 1's rework steps 6 and 7 are built, and 11 tests pass.
Deviations: `tailwind` was added to INSTALLED_APPS before `tailwind init` (it needs it). D19 covers ruff's wider defaults. Step 2 loads `django_htmx` on the existing `{% load %}` line. Step 3's helper passes `check=False` to `subprocess.run` (ruff PLW1510). Step 4 also corrected the `make install` and `make dev` descriptions in CLAUDE.md's Commands table to match the Makefile. Without a `.env`, `make migrate` stops on the missing `SECRET_KEY` (D8). It runs once the user's `.env` exists (step 5, check 1).

## Decisions

D1. (Q1) Python version: 3.12, recorded as `requires-python = ">=3.12"` in `pyproject.toml`. `make install` creates the venv with `python3.12`. Source: user, 2026-10-01.
D2. (Q2) Pinning: exact `==` pins for every direct dependency except Django, which is `Django~=5.2.0`. Versions checked on 2026-10-01: Django 5.2.17, django-environ 0.14.0, django-htmx 1.29.0, django-tailwind 4.5.0, pytest 9.1.1, pytest-django 4.14.0, ruff 0.16.9, honcho 2.0.0. Transitive dependencies are not pinned. Source: user, 2026-10-01.
D3. (Q3) `make install` does both: it pip-installs both requirements files, then runs `manage.py tailwind install` (npm install plus a first CSS build). Node and npm are needed on every dev machine. Source: user, 2026-10-01.
D4. (Q4) `make dev` runs `manage.py tailwind dev`, which uses honcho and `Procfile.tailwind` to start runserver and the Tailwind watcher together. Source: user, 2026-10-01.
D5. (Q5) The built CSS (`theme/static/css/dist/`) is not committed and goes in `.gitignore`. `theme/static_src/package-lock.json` is committed, in the spirit of D2. Source: user, 2026-10-01 (lock file: follows from D2).
D6. (Q6) "Styled by Tailwind" is tested as follows: the page links `/static/css/dist/styles.css` and its markup carries Tailwind classes. Seeing the styling in a browser through `make dev` is a manual check. Tests don't need the built CSS file: `{% tailwind_css %}` only emits a `{% static %}` link. Source: user, 2026-10-01; django-tailwind `templatetags`, read 2026-10-01.
D7. (Q7) HTMX comes from django-htmx's bundled copy, loaded with `{% load django_htmx %}{% htmx_script %}`. The tag's default is htmx 2, served as `django_htmx/htmx-2.min.js`. `django_htmx.middleware.HtmxMiddleware` is added in step 0. Source: user, 2026-10-01; django-htmx 1.29.0 source.
D8. (Q8) Defaults are dev-friendly. A missing `DATABASE_URL` falls back to `sqlite:///<BASE_DIR>/db.sqlite3`. `DEBUG` defaults to `False` (replaced by D20: `True`). A missing `SECRET_KEY` raises `ImproperlyConfigured`. `OPENAI_API_KEY` defaults to `""`. CLAUDE.md gets a note that these defaults may need to change after development. Source: user, 2026-10-01.
D9. (Q9) Tests run with `learning_companion/settings_test.py`, which sets test values with `os.environ.setdefault` (`SECRET_KEY=test-only-not-secret`, `ENV_FILE=os.devnull`) and then imports everything from `settings.py`. `pyproject.toml` points pytest-django at it. The suite therefore ignores any local `.env`. Security note: the test key only ever loads under pytest, never serves a request, and needs no change for production. Source: user ("do what's best"), 2026-10-01.
D10. (Q9b) The `deny` rules on `.env.*` stay. Claude cannot write `.env.example`, so the build lists its exact contents and the user creates it, plus their own `.env` from it. AC7 becomes a manual check. Source: user, 2026-10-01.
D11. (Q10) Apps: `core` (home view and its template) and `theme` (django-tailwind's default; holds `base.html` and the Tailwind sources). Source: user ("common practice"), 2026-10-01.
D12. (Q11) Config lives in one `pyproject.toml`: `[project]` (name, version, `requires-python`), `[tool.pytest.ini_options]` and `[tool.ruff]` with ruff's default rules. Tests live in a top-level `tests/` directory. Source: user, 2026-10-01 (tests directory: plan).
D13. (Q12) `make install` creates `.venv/` if it's missing. Every target calls `.venv/bin/...` directly, so no activation is needed. The Makefile also exports `PATH` with `.venv/bin` first, so honcho and the bare `python` in `Procfile.tailwind` resolve to the venv. Source: user, 2026-10-01; django-tailwind `tailwind dev` source.
D14. (Q13) The theme app is generated from Tailwind v4 Full (Node): `manage.py tailwind init --app-name theme --tailwind-version 4 --no-input`, without DaisyUI. Source: user, 2026-10-01.
D15. (Q14) honcho is pinned in `requirements-dev.txt`, so `tailwind dev` doesn't pip-install it on its own. cookiecutter is installed into the venv once in step 0 for `tailwind init`, then uninstalled, and stays out of both requirements files. A fresh clone never needs it: `tailwind install` only runs npm. Source: user, 2026-10-01; django-tailwind source.
D16. `settings.py` reads the env file from `env("ENV_FILE", default=BASE_DIR / ".env")`. This lets the settings tests point at a temporary `.env` or at none, regardless of the developer's own `.env`. Source: plan, needed to test AC5 and AC14.
D17. `tailwind install` loads Django settings, and a fresh clone has no `.env`, so `make install` runs it with `SECRET_KEY=$${SECRET_KEY:-install-only-not-secret}`. That key loads settings for the npm step only and never serves a request. Without it, AC1 fails under D8. Source: plan, follows from D3 and D8.
D18. `Procfile.tailwind` is created in step 0 with django-tailwind's default content and committed, so the first `make dev` doesn't leave an untracked file (AC13). Source: django-tailwind source.
D19. (Q15) ruff 0.16.9's default rule set is wider than the E/F the plan assumed. Keep the current defaults and ignore only `EXE002` in `[tool.ruff.lint]` (the NTFS mount marks every file executable). Remove the unused imports from the `startapp` files, delete `core/tests.py` (tests live in `tests/`, D12), and drop the `noqa` in `settings_test.py`. Source: user, 2026-10-01, during build.
D20. (Q16) `make dev` needs `DEBUG=True` in `.env` because `DEBUG` defaults to `False` (D8, R1). Should the default change? Answer: default `DEBUG` to `True`. This replaces D8's `DEBUG` part and AC15's "`DEBUG` is `False`". Source: user, 2026-10-01, during review.

## Acceptance criteria

- [ ] AC1. `make install` on a fresh clone installs `requirements.txt` and `requirements-dev.txt` into a venv without errors → step 0 (in the working tree), step 5 (fresh clone, manual)
- [ ] AC2. `make dev` starts the server, and `/` returns 200 with a placeholder page styled by Tailwind → step 1 (automated part), step 5 (browser, manual)
- [x] AC3. The base template loads the HTMX script → step 2
- [x] AC4. `make migrate` applies Django's built-in migrations to SQLite → step 0
- [x] AC5. Settings read `SECRET_KEY`, `DEBUG`, `DATABASE_URL` and `OPENAI_API_KEY` from the environment or `.env` via django-environ, and nothing secret is hard-coded → step 3, step 7
- [x] AC6. `DATABASE_URL` set to a SQLite URL is enough to run the app, so there's no database code in settings → step 3
- [ ] AC7. `.env.example` lists the four variables with placeholder values → step 5 (manual, D10)
- [x] AC8. `make test` runs pytest and passes with at least one test → step 0
- [x] AC9. `make test ARGS="-k <name>"` runs only the matching tests → step 0
- [x] AC10. `make lint` (`ruff check .`) and `make format` (`ruff format`) run clean on the generated code → step 0
- [x] AC11. CLAUDE.md's Commands section matches the real Makefile, and the "added by the scaffold ticket" note is removed → step 4, step 6
- [ ] AC12. `make test` passes on a fresh clone that has no `.env` file → step 0 (working tree), step 5 (fresh clone, manual; R2)
- [x] AC13. `git status` after `make install`, `make migrate`, `make test` and a Tailwind build shows no generated files (venv, `db.sqlite3`, caches, `node_modules/`) as untracked → step 0
- [x] AC14. With `SECRET_KEY` unset, loading settings fails with an error naming `SECRET_KEY` (from D8) → step 3
- [x] AC15. With `DATABASE_URL`, `DEBUG` and `OPENAI_API_KEY` unset, settings use SQLite at `BASE_DIR/db.sqlite3`, `DEBUG` is `True` and `OPENAI_API_KEY` is `""` (from D8, D20) → step 3, step 7

## Step 0: project setup

**Setup.**

1. Write `requirements.txt` with `Django~=5.2.0`, `django-environ==0.14.0`,
   `django-htmx==1.29.0` and `django-tailwind==4.5.0`. Write `requirements-dev.txt` with
   `pytest==9.1.1`, `pytest-django==4.14.0`, `ruff==0.16.9` and `honcho==2.0.0` (D2, D15).
2. Write `Makefile` (D13, D17):
   - `VENV := .venv`, `PY := $(VENV)/bin/python`, `export PATH := $(CURDIR)/$(VENV)/bin:$(PATH)`.
   - `install`: run `python3.12 -m venv .venv` if `.venv/` is missing, then
     `$(PY) -m pip install -r requirements.txt -r requirements-dev.txt`, then
     `SECRET_KEY=$${SECRET_KEY:-install-only-not-secret} $(PY) manage.py tailwind install`.
   - `test`: `$(PY) -m pytest $(ARGS)`.
   - `lint`: `$(VENV)/bin/ruff check .`.
   - `format`: `$(VENV)/bin/ruff format`.
   - `dev`: `$(PY) manage.py tailwind dev`.
   - `migrate`: `$(PY) manage.py migrate`.
   - All six are `.PHONY`.
3. Create the venv and install both requirements files (the first two lines of
   `make install`). The Tailwind step can't run until the theme app exists.
4. `.venv/bin/django-admin startproject learning_companion .`, giving `manage.py` and the
   `learning_companion/` package.
5. `.venv/bin/python manage.py startapp core`.
6. `.venv/bin/pip install cookiecutter`, then
   `.venv/bin/python manage.py tailwind init --app-name theme --tailwind-version 4 --no-input`,
   then `.venv/bin/pip uninstall -y cookiecutter` and its dependencies that nothing else
   needs (D15). This generates `theme/` with `templates/base.html` and `static_src/`.
7. Edit `learning_companion/settings.py`, keeping the startproject values otherwise: add
   `tailwind`, `theme`, `django_htmx` and `core` to `INSTALLED_APPS`, set
   `TAILWIND_APP_NAME = "theme"`, and add `django_htmx.middleware.HtmxMiddleware` to
   `MIDDLEWARE`. The environment handling comes in step 3.
8. Run `make install` in full. It now runs `tailwind install`, which creates
   `theme/static_src/package-lock.json`, `node_modules/` and `theme/static/css/dist/styles.css`.
9. Write `learning_companion/settings_test.py` (D9): `os.environ.setdefault` for
   `SECRET_KEY` (`test-only-not-secret`) and `ENV_FILE` (`os.devnull`), then
   `from .settings import *  # noqa: F403`.
10. Write `pyproject.toml` (D1, D12): `[project]` with `name = "learning-companion"`,
    `version = "0.1.0"` and `requires-python = ">=3.12"`; `[tool.pytest.ini_options]` with
    `DJANGO_SETTINGS_MODULE = "learning_companion.settings_test"` and `testpaths = ["tests"]`;
    and `[tool.ruff]` with no rule selection, so the defaults apply.
11. Add `theme/static/css/dist/` to `.gitignore` (D5).
12. Write `Procfile.tailwind` with django-tailwind's default content (D18):
    `django: python manage.py runserver` and `tailwind: python manage.py tailwind start`.
13. Run `make format` once so the generated code is in ruff's format.

**First test.** `tests/test_setup.py::test_ac8_suite_runs_against_project` asserts
`settings.ROOT_URLCONF == "learning_companion.urls"` and `"core" in settings.INSTALLED_APPS`.
It passes on its first run; there is no red run.

**Check.**

- `make test`: one test collected, passing (AC8). No `.env` exists yet (AC12).
- `make test ARGS="-k test_ac8"`: the one test runs; `make test ARGS="-k nomatch"`: no
  tests run, 1 deselected (AC9).
- `make lint` reports no errors, and `make format` reports every file unchanged (AC10).
- `make migrate` applies the `admin`, `auth`, `contenttypes` and `sessions` migrations to
  `db.sqlite3` (AC4).
- `make install` exits 0 in the working tree (AC1, first half; the fresh clone is in step 5).
- `git status --porcelain` lists only source files: none of `.venv/`, `db.sqlite3`,
  `.pytest_cache/`, `.ruff_cache/`, `node_modules/` or `theme/static/css/dist/` (AC13).

## Step 1: AC2, home page with Tailwind

**Test.** `tests/test_home.py::test_ac2_home_page_is_styled_by_tailwind`, using
pytest-django's `client` fixture. It runs `client.get("/")` and asserts: status 200;
`core/home.html` and `base.html` are among the templates used
(`[t.name for t in response.templates]`); the content contains
`href="/static/css/dist/styles.css`; and the content contains the placeholder heading
`Learning Companion` inside an element with a `class="` attribute.

**Red.** It fails on the status assertion: `/` returns 404, because
`learning_companion/urls.py` has only the admin route.

**Green.** Add `core/views.py::home`, which renders `core/home.html`. Add
`core/templates/core/home.html`, which extends `base.html` and fills `{% block content %}`
with `<h1 class="text-3xl font-bold">Learning Companion</h1>` and a one-line placeholder.
In `theme/templates/base.html`, replace the generated "Django + Tailwind" section with
`{% block content %}{% endblock %}` and set the `<title>` to `Learning Companion`. Add
`path("", views.home, name="home")` to `learning_companion/urls.py`.

**Refactor.** None.

## Step 2: AC3, HTMX in the base template

**Test.** `tests/test_home.py::test_ac3_base_template_loads_htmx` runs `client.get("/")`
and asserts that the content contains `src="/static/django_htmx/htmx-2.min.js"`.

**Red.** It fails on the assertion: `base.html` has no script tag yet.

**Green.** In `theme/templates/base.html`, add `{% load django_htmx %}` and put
`{% htmx_script %}` in `<head>` (D7).

**Refactor.** None.

## Step 3: AC5, AC6, AC14, AC15, settings from the environment

**Test.** `tests/test_settings.py`. A helper `load_settings(tmp_path, **env)` runs
`[sys.executable, "-c", SCRIPT]` with `cwd` at the repo root and an environment built
only from `PATH`, `DJANGO_SETTINGS_MODULE=learning_companion.settings`,
`ENV_FILE=<tmp_path>/.env` and `env`. `SCRIPT` prints JSON with `SECRET_KEY`, `DEBUG`,
`DATABASES["default"]["ENGINE"]`, `str(DATABASES["default"]["NAME"])` and
`getattr(settings, "OPENAI_API_KEY", None)`. The helper returns the completed process, and
the parsed JSON when the exit code is 0.

- `test_ac5_reads_settings`, parametrized over `source` in `["environment", "env_file"]`.
  For `environment`, the four values are passed in `env`: `SECRET_KEY=from-test`,
  `DEBUG=True`, `DATABASE_URL=sqlite:///<tmp_path>/a.sqlite3`, `OPENAI_API_KEY=sk-test`.
  For `env_file`, the same four lines are written to `<tmp_path>/.env` and `env` is
  empty. Both cases assert that the JSON shows those values (`DEBUG` is `True`).
- `test_ac5_settings_hard_code_no_secret`: the text of `learning_companion/settings.py`
  does not contain `django-insecure`.
- `test_ac6_sqlite_url_configures_database`: with `SECRET_KEY` and
  `DATABASE_URL=sqlite:///<tmp_path>/b.sqlite3`, `ENGINE` is
  `django.db.backends.sqlite3` and `NAME` is `<tmp_path>/b.sqlite3`. The text of
  `settings.py` does not contain `"ENGINE"`.
- `test_ac14_missing_secret_key_fails`: with no variables, the exit code is non-zero and
  stderr contains `SECRET_KEY`.
- `test_ac15_defaults`: with only `SECRET_KEY=x`, `NAME` is
  `str(<repo root>/"db.sqlite3")`, `DEBUG` is `False` and `OPENAI_API_KEY` is `""`.

**Red.** Every test fails on an assertion against the startproject `settings.py`. The
values ignore the environment: `SECRET_KEY` is the hard-coded `django-insecure-...`,
`DEBUG` is `True` and `OPENAI_API_KEY` is `None`. The settings file contains
`django-insecure` and `"ENGINE"`. The missing-key run exits 0.
`test_ac15_defaults` fails on `DEBUG` and `OPENAI_API_KEY`, not on `NAME`.

**Green.** In `learning_companion/settings.py`: `env = environ.Env()`,
`environ.Env.read_env(env("ENV_FILE", default=str(BASE_DIR / ".env")))`,
`SECRET_KEY = env("SECRET_KEY")`, `DEBUG = env.bool("DEBUG", default=False)`,
`DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}`
and `OPENAI_API_KEY = env("OPENAI_API_KEY", default="")`. Remove the hard-coded key and
the literal `DATABASES` block.

**Refactor.** None.

## Step 4: AC11, CLAUDE.md matches the Makefile

**Test.** `tests/test_docs.py::test_ac11_claude_md_commands_match_makefile` collects the
target names from the `Makefile` with the regex `^([a-z][a-z-]*):` (multiline), excluding
`.PHONY`. It asserts that each target appears in `CLAUDE.md` as `` `make <target>` ``,
that every `` `make <name>` `` in CLAUDE.md's Commands table is a real target, and that
`CLAUDE.md` does not contain `Added by the scaffold ticket`.

**Red.** It fails on the last assertion: CLAUDE.md still says "Added by the scaffold
ticket; none of these exist yet." The table already matches the six targets.

**Green.** Edit `CLAUDE.md`. Remove that sentence from the Commands section. Add a short
note under Stack (D8): settings default to dev-friendly values (`DATABASE_URL` falls back
to SQLite, `DEBUG` to `False`, `OPENAI_API_KEY` to empty), and these may need to change
before production.

**Refactor.** None.

## Step 5: AC1, AC2, AC7, manual checks

The build lists these for the user and doesn't tick them itself.

1. **AC7.** Create `.env.example` with exactly these lines:
   ```
   SECRET_KEY=change-me
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   OPENAI_API_KEY=sk-your-key-here
   ```
   Then `cp .env.example .env` and, in `.env` only, replace `SECRET_KEY` with the output
   of `.venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`.
   Expected: `git status` shows `.env.example` as new, and `.env` doesn't appear.
2. **AC2.** Run `make dev`. Expected: honcho starts `django` and `tailwind` processes, and
   the output shows `http://127.0.0.1:8000/`. Open it: the heading "Learning Companion"
   is large and bold (Tailwind applied), and the browser dev tools show
   `styles.css` and `htmx-2.min.js` loading with status 200.
3. **AC1.** After `/ship` commits the branch:
   `git clone <repo path> /tmp/lc-clone && cd /tmp/lc-clone && make install`.
   Expected: exits 0 without a `.env`, and `make test` passes there too (AC12).

## Step 6: rework R3, AC11, CLAUDE.md test reads only the Commands table

**Test.** In `tests/test_docs.py`, add `test_ac11_target_counts_only_in_commands_table`.
It calls a helper `undocumented_targets(makefile_text, claude_md_text)`, extracted from
`test_ac11_claude_md_commands_match_makefile`, with a Makefile text of `dev:\n\techo` and
a CLAUDE.md text where `` `make dev-server` `` appears in the Commands table and
`` `make dev` `` appears only under another heading (`## Other`). It asserts the result
is `{"dev"}`.

**Red.** It fails on the assertion. The current check searches the whole file for
`` `make dev`` without the closing backtick, so `` `make dev-server` `` and the mention
under `## Other` both count, and the result is the empty set.

**Green.** In `tests/test_docs.py`, move the target and Commands-section parsing into
`undocumented_targets`, which returns `targets - documented`. Make
`test_ac11_claude_md_commands_match_makefile` assert that this is empty, in place of the
whole-file search at line 15.

**Refactor.** None.

## Step 7: rework R1, AC5, AC15, `DEBUG` defaults to `True`

**Test.** In `tests/test_settings.py`, change two earlier tests, as this rework allows:
- `test_ac15_defaults`: assert `values["DEBUG"] is True` in place of `is False` (D20).
- `test_ac5_reads_settings`: pass `"DEBUG": "False"` and assert `values["DEBUG"] is False`.
  With a `True` default, the current `DEBUG=True` row would pass even if settings ignored
  the environment, so it has to use the non-default value.

**Red.** `test_ac15_defaults` fails on `assert False is True`: `settings.py:31` has
`env.bool("DEBUG", default=False)`. The changed `test_ac5_reads_settings` rows already
pass against the current code (it reads `DEBUG=False` from the environment and the
`.env` file). They are there to keep AC5 meaningful once the default flips.

**Green.** In `learning_companion/settings.py`, change the line to
`DEBUG = env.bool("DEBUG", default=True)`. In `CLAUDE.md`'s Stack line for
django-environ, change "`DEBUG` to `False`" to "`DEBUG` to `True`", and say that
production must set `DEBUG=False`.

**Refactor.** None.

## Review

### Round 1, 2026-10-01

- R1. should-fix, `learning_companion/settings.py:31`: with only `SECRET_KEY` set, `make dev` fails (`DEBUG` defaults to `False` and `ALLOWED_HOSTS = []`), and CLAUDE.md:16 says only `SECRET_KEY` is required. Q16 answered: default `DEBUG` to `True` (D20). → plan updated 2026-10-01, fixed in step 7
- R2. nit, plan AC12: ticked, but its fresh-clone check is pending in step 5. → accepted, AC12 unticked and pending manual (step 5 item 3)
- R3. nit, `tests/test_docs.py:15`: the documented-target check searches the whole file without the closing backtick, so `` `make dev-server` `` counts as `make dev`. → fixed in step 6

### Round 2, 2026-10-01

- No findings.

## Files

New:
- `requirements.txt`, `requirements-dev.txt`: pinned dependencies (D2).
- `Makefile`: the six commands (D13, D17).
- `pyproject.toml`: Python version, pytest and ruff config (D1, D12).
- `manage.py`, `learning_companion/__init__.py`, `settings.py`, `urls.py`, `asgi.py`, `wsgi.py`: from `startproject`.
- `learning_companion/settings_test.py`: test settings (D9).
- `core/` (from `startapp`), `core/views.py`, `core/templates/core/home.html`: home page.
- `theme/` (from `tailwind init`): `apps.py`, `templates/base.html`, `static_src/package.json`, `postcss.config.js`, `src/styles.css`, `package-lock.json`.
- `Procfile.tailwind`: processes for `make dev` (D18).
- `tests/test_setup.py`, `tests/test_home.py`, `tests/test_settings.py`, `tests/test_docs.py`.
- `.env.example`: written by the user (D10).

Changed:
- `.gitignore`: add `theme/static/css/dist/` (D5).
- `CLAUDE.md`: Commands note removed, defaults note added (AC11, D8).

## Verification

- After each new test: `make test ARGS="-k <test name>"` fails for the reason in the step's Red.
- After each Green: `make test` passes in full.
- At the end: `make test` (all tests passing), `make lint` (no errors), `make format`
  (no files changed), `make migrate` (no pending migrations), and `git status --porcelain`
  shows no generated files (AC13).
- The project has no type-check or separate build step. `make install` covers the CSS build.
