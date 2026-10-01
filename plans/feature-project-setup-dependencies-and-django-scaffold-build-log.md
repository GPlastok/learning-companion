Build log for plans/feature-project-setup-dependencies-and-django-scaffold-plan.md

## 2026-10-01

- Branch: feature/1-project-setup (created by the user). No suite yet, baseline after step 0.
- Step 0 setup: wrote requirements.txt, requirements-dev.txt, Makefile; `python3.12 -m venv .venv` and pip install of both files: Django 5.2.17, django-environ 0.14.0, django-htmx 1.29.0, django-tailwind 4.5.0, pytest 9.1.1, pytest-django 4.14.0, ruff 0.16.9, honcho 2.0.0.
- Step 0 setup: `startproject learning_companion .` and `startapp core` OK.
- Step 0 setup: `tailwind init` failed with "Unknown command: 'tailwind'" until `tailwind` was in INSTALLED_APPS. Added `tailwind` (setup item 7) before item 6; init then created theme/. cookiecutter and its 19 dependencies uninstalled; `pip freeze` matches the pre-cookiecutter state, `pip check` clean.
- Step 0 setup: rest of item 7 (theme, django_htmx, core, TAILWIND_APP_NAME, HtmxMiddleware). `make install` OK: npm install, 0 vulnerabilities, CSS build to theme/static/css/dist/styles.css.
- Step 0 setup: settings_test.py, pyproject.toml, .gitignore entry, Procfile.tailwind, tests/test_setup.py.
- Step 0 check: `make format`: 7 files reformatted, 27 unchanged.
- Step 0 check: `make test`: 1 passed.
- Step 0 check: `make lint`: 21 errors. 17× EXE002 (every file is executable on the NTFS/fuseblk mount; git core.fileMode=false), 4× F401 in startapp boilerplate (core/admin.py, models.py, tests.py, views.py), 1× RUF100 (noqa in settings_test.py). ruff 0.16.9's default rule set is wider than the E/F the plan assumed.
- Stop: plan/tool mismatch on ruff defaults; asked the user.
- User answer Q15: A (keep ruff defaults, ignore EXE002, clean boilerplate). Recorded as D19.
- Step 0: added [tool.ruff.lint] extend-ignore EXE002; removed core/tests.py; `ruff check --fix --select F401 core/`; dropped the noqa in settings_test.py.
- Step 0 check: `make lint`: All checks passed. `make format`: 3 reformatted, then a second run: 34 files left unchanged (AC10).
- Step 0 check: `make test`: 1 passed (AC8); no .env present (AC12).
- Step 0 check: `make test ARGS="-k test_ac8"`: 1 passed; `make test ARGS="-k nomatch"`: 1 deselected, pytest exit 5 (no tests collected) (AC9).
- Step 0 check: `make migrate`: applied admin, auth, contenttypes, sessions migrations to db.sqlite3 (AC4).
- Step 0 check: `make install`: exit 0 in the working tree (AC1, first half).
- Step 0 check: `git status --porcelain --untracked-files=all`: no .venv, db.sqlite3, caches, node_modules or css/dist (AC13).
- Baseline after step 0: 1 test passes.
- Step 1 red: `make test ARGS="-k test_ac2"`: 1 failed, assert 404 == 200 (planned).
- Step 1 green: core/views.py home, core/templates/core/home.html, base.html block + title, URL. `make test`: 2 passed. `make lint`: clean.
- Step 2 red: `make test ARGS="-k test_ac3"`: 1 failed, htmx-2.min.js not in content (planned).
- Step 2 green: `django_htmx` added to base.html's load line, `{% htmx_script %}` in head. `make test`: 3 passed.
- Step 3 red: `make test ARGS="tests/test_settings.py"`: 6 failed, all on assertions (hard-coded key, DEBUG True, startproject DB name, missing-key exit 0, settings text). test_ac15 failed on DEBUG, NAME matched (planned).
- Step 3 green: settings.py reads env via django-environ (D8, D16). `make test`: 9 passed. `make lint`: PLW1510 on subprocess.run in the test helper; added check=False. `make lint`: clean.
- Step 4 red: `make test ARGS="-k test_ac11"`: 1 failed on "Added by the scaffold ticket" (planned).
- Step 4 green: CLAUDE.md note removed, defaults note added (D8), install/dev descriptions corrected. `make test`: 10 passed. `make lint`: clean.
- Verification: `make test` 10 passed; `make lint` all checks passed; `make format` 37 files unchanged; `make migrate` without .env: error on missing SECRET_KEY (D8, expected); `SECRET_KEY=verify-only make migrate`: no migrations to apply; git status: no generated files.
- Manual checks pending: AC1, AC2, AC7.

## 2026-10-01, review round 1 rework

- Review round 1: R1 → plan (D20), R2 accepted (AC12 unticked), R3 → step 6. Plan updated with step 7 for R1.
- Baseline: `make test`: 10 passed.
- Step 6 red (first try): `make test ARGS="-k test_ac11_target"`: NameError, undocumented_targets not defined (wrong reason). Moved the current whole-file check into undocumented_targets unchanged; suite stays green.
- Step 6 red: `make test ARGS="-k test_ac11_target"`: 1 failed, assert set() == {'dev'} (planned).
- Step 6 green: parse only the Commands section (makefile_targets, documented_targets, undocumented_targets). `make test`: 11 passed. `make lint`: clean.
- Step 7 red: `make test ARGS="-k 'test_ac15 or test_ac5_reads'"`: test_ac15_defaults failed, assert False is True; both test_ac5_reads_settings rows passed (planned).
- Step 7 green: DEBUG default=True; CLAUDE.md wording. `make test`: 11 passed. `make lint`: clean. `make format`: 37 unchanged.
- Verification: `SECRET_KEY=verify-only make migrate`: no migrations to apply; git status: no generated files.
- Step 5 check 1 (AC7): the user created .env.example and .env (not read by Claude, deny rule). Awaiting the user's confirmation.
