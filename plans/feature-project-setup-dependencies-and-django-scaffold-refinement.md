# Project setup: dependencies and Django scaffold: refinement

## Context

Turn the repo into a runnable Django project named `learning_companion`, with the stack
from CLAUDE.md wired up (django-tailwind, django-htmx, django-environ, pytest +
pytest-django, ruff) and a Makefile command for each task. It ships no features: no auth,
no models, one placeholder home page. The repo has no project yet, so the survey sections
below record "not found" and take the planned stack and commands from CLAUDE.md. The
plan's step 0 sets the project up. Branch: none yet (on `main`).

Source: #1 (https://github.com/GPlastok/learning-companion/issues/1)

## Progress

Refinement done on 2026-10-01. Nothing planned or built yet. Next: the user answers the
open questions, then a plan is written.
Plan written on 2026-10-01: plans/feature-project-setup-dependencies-and-django-scaffold-plan.md.
Built on 2026-10-01, see plans/feature-project-setup-dependencies-and-django-scaffold-plan.md.
Plan written on 2026-10-01: plans/feature-project-setup-dependencies-and-django-scaffold-plan.md (updated for review R1).

## Acceptance criteria

### Supplied

- [ ] `make install` on a fresh clone installs `requirements.txt` and `requirements-dev.txt` into a venv without errors
- [ ] `make dev` starts the server, and `/` returns 200 with a placeholder page styled by Tailwind
- [ ] The base template loads the HTMX script
- [ ] `make migrate` applies Django's built-in migrations to SQLite
- [ ] Settings read `SECRET_KEY`, `DEBUG`, `DATABASE_URL` and `OPENAI_API_KEY` from the environment or `.env` via django-environ, and nothing secret is hard-coded
- [ ] `DATABASE_URL` set to a SQLite URL is enough to run the app, so there's no database code in settings
- [ ] `.env.example` lists the four variables with placeholder values
- [ ] `make test` runs pytest and passes with at least one test
- [ ] `make test ARGS="-k <name>"` runs only the matching tests
- [ ] `make lint` (`ruff check .`) and `make format` (`ruff format`) run clean on the generated code
- [ ] CLAUDE.md's Commands section matches the real Makefile, and the "added by the scaffold ticket" note is removed

### Added by refinement

- [ ] `make test` passes on a fresh clone that has no `.env` file
- [ ] `git status` after `make install`, `make migrate`, `make test` and a Tailwind build shows no generated files (venv, `db.sqlite3`, caches, `node_modules/`) as untracked

## Files and functions

Not found: the repo has no project yet. Tracked files are `CLAUDE.md`, `.gitignore`,
`.claude/` (settings, hooks, skills) and `.github/ISSUE_TEMPLATE/` (`config.yml`,
`feature.yml`).

Planned in CLAUDE.md, not created yet:

- Django project `learning_companion` from `django-admin startproject` (name from the ticket).
- `requirements.txt` (runtime) and `requirements-dev.txt` (tests, ruff).
- `Makefile` with `install`, `test` (with `ARGS`), `lint`, `format`, `dev`, `migrate`.
- `.env.example` with `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `OPENAI_API_KEY`.
- A base template loading HTMX, and a placeholder home page at `/`.

## Current data shapes

Not found: the repo has no project yet. No models are in scope; only Django's built-in
migrations run (AC4). The database is SQLite now, PostgreSQL later, read from
`DATABASE_URL` (CLAUDE.md, Stack).

## Tests

Not found: the repo has no project yet. Planned in CLAUDE.md:

- Runner: pytest + pytest-django; `make test`, `make test ARGS="-k test_ac3"`.
- Naming: test functions are named after the criterion they cover
  (`test_ac14_prefixes_player_lines`); a table of inputs is one test with
  `@pytest.mark.parametrize`.
- Other checks: `make lint` (`ruff check .`) and `make format` (`ruff format`). `/ship`
  runs `make test` and `make lint`.

Environment on this machine: Python 3.12.3, Node v24.14.1, npm 11.11.0.

## Patterns to follow

No code to copy yet. Constraints from the guidance files:

- Stack is fixed (CLAUDE.md, Stack, decided 2026-10-01). A change is raised as a question,
  not made.
- Node runs only at build time for Tailwind (CLAUDE.md, Stack; a two-stage Dockerfile later).
- HTMX: the scaffold adds the script tag; the goals ticket is the first to use it.
- Tags will be a `Tag` model (M2M) later; not in scope here.
- `.claude/settings.json` allows `make test`, `make test ARGS=*`, `make lint`,
  `make format` without a prompt, and denies reading or editing `.env` and `.env.*`.
  Claude can create and read `.env.example` only if the deny pattern `./.env.*` doesn't
  match it (see question 9).
- `.gitignore` already ignores `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`,
  `.ruff_cache/`, `db.sqlite3`, `staticfiles/`, `media/`, `.env`, `.env.*` (except
  `.env.example`) and `node_modules/`. The venv path it expects is `.venv/`.

## Open questions

1. Which Python version is the target (this machine has 3.12.3), and should it be written
   down (for example `requires-python` or a `.python-version` file)?
2. Are dependencies pinned to exact versions (`==`) in the requirements files, or given as
   ranges?
3. Does `make install` also install Tailwind's Node dependencies (`python manage.py
   tailwind install`), or is that a separate target? AC1 names only the two requirements
   files.
4. Does `make dev` run the Tailwind watcher alongside `runserver` (for example
   `manage.py tailwind dev` or two processes), or only `runserver` against an already
   built CSS file?
5. Is the built Tailwind CSS committed, or built on each machine? This decides whether
   tests can see a CSS file on a fresh clone without Node.
6. What does "styled by Tailwind" mean as a pass or fail in a test: the page links the
   Tailwind stylesheet and uses Tailwind classes, or the built CSS file exists and
   contains the classes used? Is the `make dev` part checked manually?
7. Where does HTMX come from: django-htmx's bundled script (`{% htmx_script %}`), a
   vendored static file, or a CDN?
8. What happens when a variable is missing: does `SECRET_KEY` missing raise an error, does
   `DEBUG` default to `False`, does a missing `DATABASE_URL` fall back to SQLite or fail,
   and is `OPENAI_API_KEY` allowed to be empty?
9. How do tests get `SECRET_KEY` and `DATABASE_URL` on a fresh clone without `.env`
   (pytest settings, env in the test config, or a test settings module)? Related: the
   `deny` rule `Read(./.env.*)` may also block Claude from reading `.env.example`; should
   an allow exception be added, or is `.env.example` written blind?
10. What are the app names: the Django app holding the home page, and the django-tailwind
    theme app (its default is `theme`)?
11. Where do pytest and ruff config live (`pyproject.toml`, `pytest.ini`, `ruff.toml`),
    and which ruff rules are enabled beyond the defaults?
12. Does `make install` create the venv at `.venv/` if it's missing, and do the other
    targets use `.venv/bin/python` directly or expect an activated venv?
