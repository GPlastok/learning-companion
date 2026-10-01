# Build log: plans/feature-authentication-and-profile-management-plan.md

## 2026-10-01

- Branch: created `feature/3-authentication-and-profile-management` off `main` (user asked).
- Baseline: make test … 11 passed.
- Step 0: startapp accounts, tidied (D28); User model; AUTH_USER_MODEL; PASSWORD_HASHERS; makemigrations accounts … 0001_initial created.
- Step 0: rm db.sqlite3; make migrate … all migrations applied, accounts.0001 included.
- Step 0 check: make test … 11 passed. makemigrations --check --dry-run … No changes detected.
- Step 0 check: make lint … 2 errors, RUF012 (mutable class attribute) on `dependencies` and `operations` in the generated accounts/migrations/0001_initial.py. ruff format --check: that file would be reformatted.
- Stop: plan doesn't say how lint treats generated migrations. Asked the user (Q21).
- Answer Q21: option 1, per-file ignore RUF012 for */migrations/* (D29).
- Step 0 check: ruff format accounts/migrations/0001_initial.py … reformatted. make lint … All checks passed. ruff format --check … 48 already formatted. make test … 11 passed.
- Step 1 red: make test ARGS="tests/test_signup.py" … 4 failed with NoReverseMatch for `signup` (planned first red). Added the route and a stub.
- Step 1 red: same command … 4 failed: no `accounts/signup.html` in templates, no form in context, empty redirect chain (planned).
- Step 1 green: make test … 4 failed: NoReverseMatch for `login` (template link, route comes in step 3) and no database access. Removed the link until step 3; added `db` to the user fixtures and a module `django_db` mark.
- Step 1 green: make test … 15 passed.
- Step 2 red: make test ARGS="tests/test_signup.py -k 'ac2 or ac9'" … 3 AC2 rows passed (planned: UserCreationForm), 2 AC9 rows failed on `assert 302 == 200` (duplicate email accepted).
- Step 2 green: make test … 20 passed.
- Step 3 red: make test ARGS="tests/test_login.py" … 4 failed, NoReverseMatch for `login`/`logout` (planned: the only red this step can show).
- Step 3 green: routes, registration/login.html, sign-up login link restored. make test … 24 passed.
- Step 4 red: make test ARGS="tests/test_home.py tests/test_login.py" … 3 failed as planned (home 200 not 302, no punchline, no <nav>); no-nav test and the two switched ticket-1 tests passed (planned).
- Step 4 green: make test … 28 passed.
- Step 5 red: make test ARGS="tests/test_login.py -k ac8" … "ada" row passed (planned), 2 email rows failed with an empty redirect chain (form error, no login).
- Step 5 green: UsernameOrEmailBackend + AUTHENTICATION_BACKENDS. make test … 31 passed.
- Step 6 red (models, schema migrations and profile_edit stub in place): make test ARGS="tests/test_profile.py" … 3 failed as planned: RelatedObjectDoesNotExist (no profile), no "Complete your profile", empty cohort list.
- Step 6 green: seed migrations, signal, AccountsConfig.ready, home prompt. make test … 34 passed. make migrate … seeds applied to dev db. makemigrations --check … no changes. make lint … passed.
- Step 7 red: make test ARGS="tests/test_profile.py" … 9 failed with NoReverseMatch for `profile`/`profile_detail` (planned first red). Added both routes with stubs.
- Step 7 red: same command … 7 failed on their assertions (planned). The `owner` and `staff` rows of test_ac16_profile_access passed: the stub returns 200, their expected status. Not listed in the plan; logged as a deviation, not a stop.
- Step 7 green: profile, profile_detail, profile_detail.html, nav Profile link. make test … 43 passed.
- Step 8 red: make test ARGS="tests/test_profile.py -k 'ac17 or ac18'" … 4 failed as planned: no form in the stub's context (3), 200 instead of 302 (1).
- Step 8 green: ProfileForm, profile_edit, profile_form.html. make test … 47 passed.
- Step 9 red: make test ARGS="tests/test_account_delete.py" … 3 failed with NoReverseMatch (planned first red); with the stub, 3 failed on their assertions: no text, no redirect, 200 instead of 302.
- Step 9 green: account_delete, account_confirm_delete.html, delete link on the profile. make test … 50 passed.
- Step 10 red: make test ARGS="tests/test_admin.py" … 5 failed as planned: 4 on `is_registered` False, changelist NoReverseMatch.
- Step 10 green: accounts/admin.py, core/admin.py. make test … 55 passed.
- Verification: make test … 55 passed. make lint … 1 error, RUF012 on ProfileForm.Meta.widgets; moved the widget to a declared focus_areas field. make format … 2 files reformatted, then 61 unchanged. make lint … All checks passed. make test … 55 passed. makemigrations --check … No changes detected. manage.py check … no issues.

## 2026-10-01, rework after review round 1

- Baseline: make test … 55 passed.
- Step 11 (R2): red none, test-only (planned). make test … 55 passed.
- Step 12 (R1) red: make test ARGS="-k test_ac23" … 1 failed, `assert 302 == 200` (username with @ accepted), as planned.
- Step 12 green: SignUpForm.clean_username. make test … 56 passed.
- Step 13 (R4) red: make test ARGS="-k test_ac16" … new test failed `assert 404 == 403`; changed staff 404 test passed (planned).
- Step 13 green: permission check before get_object_or_404. make test … 57 passed.
- Step 14 (R5): red none, test-only (planned). Step 15 (R6): red none, test-only (planned); the new email row passed. make test … 58 passed.
- Verification after rework: make lint … passed. make format … 61 unchanged. make test … 58 passed. makemigrations --check … no changes.

## 2026-10-01, rework after review round 2

- Baseline: make test … 58 passed.
- Step 16 (R8) red: make test ARGS="-k test_ac2_" … taken_username_other_case failed `assert 302 == 200`, as planned.
- Step 16 green: clean_username calls super(). make test … 59 passed.
- Step 17 (R9) red: make test ARGS="-k test_ac13_raw" … failed `assert not True` (profile created on raw save), as planned.
- Step 17 green: receiver skips raw saves. make test … 60 passed.
- Step 18 (R10) red: make test ARGS="-k test_ac21_login" … failed `assert '<nav' in ...`, as planned.
- Step 18 green: nav always rendered, right side behind is_authenticated. make test … 60 passed.
- Step 19 (R10) red: make test ARGS="-k test_ac24" … failed `assert 200 == 302`, as planned.
- Step 19 green: redirect_authenticated_user=True. make test … 61 passed.
- Verification after round 2 rework: make lint … passed. make format … 2 files reformatted, then 61 unchanged. make test … 61 passed. makemigrations --check … no changes.

## 2026-10-01, rework after review round 3

- Baseline: make test … 61 passed.
- Step 20 (R11): red none, test-only (planned). make test … 61 passed.
- Step 21 (R12) red: make test ARGS="-k test_ac25" … home and profile_edit rows raised RelatedObjectDoesNotExist, profile_detail row failed `assert 404 == 200`, as planned.
- Step 21 green: profile_for in accounts/models.py, used by home, profile_edit and own profile_detail. make format … unchanged. make test … 64 passed. make lint … passed. makemigrations --check … no changes.
