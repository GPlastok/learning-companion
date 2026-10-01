# Authentication and profile management: TDD plan

## Context

This ticket adds a custom User model with sign-up, login, logout and account deletion. People log in with their username or their email.

Each user gets a Profile with an admin-maintained cohort and a list of focus-area tags. Only the owner and staff can see a profile.

Refinement: [feature-authentication-and-profile-management-refinement.md](feature-authentication-and-profile-management-refinement.md). Source: #3.

Branch: none yet. Create one off `main` before building, for example `feature/3-authentication-and-profile-management`. The build stops on the default branch.

**In scope:**

- a new `accounts` app with User, Profile and Cohort;
- a `Tag` model in `core`, with seed data;
- sign-up, login, logout and account deletion;
- the profile page and its edit form;
- the nav bar and a login page with a punchline;
- admin registration.

**Not in scope:**

- password reset, password change and email verification (D10);
- activity tracking beyond `last_login` (D4);
- a landing page and a logo image;
- HTMX (D27);
- the `learning` app, which ticket #4 creates (D1).

## Progress

Plan written on 2026-10-01. Updated the same day for Q1c (the `accounts` app).

Step 0 done: 11 tests pass, as before the build. Lint failed on the generated migration until D29.

Step 1 done: 15 tests pass, 11 before the build plus 4 new. Deviations: the user fixtures take `db` and `tests/test_signup.py` has a module `django_db` mark (`django_user_model` gives no database access, unlike D26 says). The sign-up page's link to login waits for step 3, where the `login` route appears.

Step 2 done: 20 tests pass.

Step 3 done: 24 tests pass. The sign-up page's login link went in here (see step 1).

Step 4 done: 28 tests pass. The nav's Profile link points at `#` until step 7.

Step 5 done: 31 tests pass. The backend also treats two accounts sharing an email (possible only through the admin) as no match, and hashes the password when no user is found, as `ModelBackend` does.

Step 6 done: 34 tests pass. Migrations: `core/0001_initial`, `core/0002_seed_tags`, `accounts/0002_cohort_profile`, `accounts/0003_seed_cohorts` (seeds split per D1). `Meta.ordering` uses tuples so RUF012 stays quiet outside migrations. Profile is ordered by username.

Step 7 done: 43 tests pass. Deviations: the `owner` and `staff` rows of `test_ac16_profile_access` passed against the stub at red (it returns 200), which the plan didn't list; they guard against the 403 check blocking owner or staff. The delete link on the profile waits for step 9, where its route appears.

Step 8 done: 47 tests pass.

Step 9 done: 50 tests pass. The profile page's delete link went in here (see step 7).

Step 10 done: 55 tests pass, 11 before the build plus 44 new.

Verification: `make lint` first failed on RUF012 for `ProfileForm.Meta.widgets`; `focus_areas` became a declared `ModelMultipleChoiceField` with the same widget. Then all checks passed.

Built on 2026-10-01. Manual check offered to the user (D20).

Review round 1 on 2026-10-01: 5 rework steps added (11 to 15). R7 → plan (D26 wording).

Plan updated for R7 on 2026-10-01.

Step 11 done (rework R2): 55 tests pass.

Step 12 done (rework R1): 56 tests pass.

Step 13 done (rework R4): 57 tests pass.

Step 14 done (rework R5): 57 tests pass. Step 15 done (rework R6): 58 tests pass (the email row is new).

Verification after rework: make test 58 passed, make lint clean, make format no changes, no missing migrations.

Built on 2026-10-01, rework steps 11 to 15 included.

Review round 2 on 2026-10-01: 2 rework steps added (16, 17). R10 → plan (D32 changes AC21).

Plan updated for R10 on 2026-10-01: D33, AC21 reworded, AC24 added, steps 18 and 19.

Step 16 done (rework R8): 59 tests pass.

Step 17 done (rework R9): 60 tests pass.

Step 18 done (rework R10): 60 tests pass (one test replaced).

Step 19 done (rework R10): 61 tests pass.

Verification after round 2 rework: make test 61 passed, make lint clean, make format no changes, no missing migrations.

Built on 2026-10-01, rework steps 16 to 19 included. Two review rounds used.

Review round 3 on 2026-10-01 (asked for by the user): 2 rework steps added (20, 21).

Step 20 done (rework R11): 61 tests pass.

Step 21 done (rework R12): 64 tests pass.

Verification after round 3 rework: make test 64 passed, make lint clean, make format no changes, no missing migrations.

Built on 2026-10-01, rework steps 20 and 21 included. Three review rounds used.

Reviewed on 2026-10-01, round 4: no rework.

## Decisions

### Apps and models

D1. (Q1, Q1c) Where the code lives:

- **`accounts`** (new, from `startapp`): User, Profile, Cohort, and the sign-up, login, profile and delete views, forms, backend and signal.
- **`core`**: the home page and `Tag`, because goals and resources will reuse tags later.
- **`learning`**: goals, sessions and resources. Ticket #4 creates it; this ticket doesn't.

The User goes in `accounts` now because moving it between apps later means rewriting migrations. Source: user, 2026-10-01.

D2. (Q2) `accounts.User(AbstractUser)` has no extra fields. `AbstractUser` already has `id`, `username`, `first_name`, `last_name`, `email`, `password`, `date_joined` and `last_login`.

User and Profile stay separate. User holds identity and login. Profile holds the bootcamp data. Source: user, 2026-10-01.

D3. (Q2a) Primary keys are integers (`BigAutoField`, the project default). Source: user, 2026-10-01.

D4. (Q2b) Last activity is `last_login` for now. Tracking every request waits for a later ticket. Source: user, 2026-10-01.

D9. (Q7, Q7a, Q8) Cohorts and tags:

- `accounts.Cohort`: `name` (unique) and `is_active` (default `True`).
- `core.Tag`: `name` (unique).
- `Profile.cohort`: nullable `ForeignKey(Cohort, on_delete=PROTECT)`.
- `Profile.focus_areas`: `ManyToManyField("core.Tag", blank=True)`.

Admins maintain both lists, and users can't create tags. The cohort is required. The user picks it once, from active cohorts only, when completing the profile. After that the field is gone from their form, and only an admin can change it.

Data migrations create the starting data. `accounts` creates Cohort 1, Cohort 2 and Cohort 3, all active. `core` creates the tags:

Python, JavaScript, TypeScript, HTML & CSS, React, Django, Node.js, SQL & Databases, Git, Testing, APIs, Docker & DevOps, Cloud, AI & Machine Learning, Data Analysis, UX Research, UI Design, Figma, Accessibility, Product Management, Agile & Scrum.

Tag names are stored as written, with no case folding. Only admins add tags. Source: user, 2026-10-01 (case folding: plan).

D19. (Q17) The local `db.sqlite3` has only Django's built-in tables: 0 users, 0 sessions, 0 admin log entries (read on 2026-10-01). Once the custom User migration exists, the build deletes it and runs `make migrate`. Tests are unaffected. Source: user, 2026-10-01.

### Sign-up and login

D5. (Q3) People log in with their username or their email.

`accounts.backends.UsernameOrEmailBackend` subclasses `ModelBackend`. It looks the user up by exact `username` first, then by `email__iexact`. `AUTHENTICATION_BACKENDS` lists only this backend.

Sign-up requires an email, and no two users may share one, compared case-insensitively. Nothing verifies it (D10). Source: user, 2026-10-01.

D6. (Q4, Q20) The sign-up form asks for username, email, first name, last name, password and password confirmation, all of them required. The user fills in cohort and focus areas later. Source: user, 2026-10-01.

D8. (Q6) The name is `first_name` and `last_name` on User. Source: user, 2026-10-01.

D10. (Q15) No password reset, password change or email verification, and no email backend.

`django.contrib.auth.urls` is not included, since it would add the reset routes. Source: user, 2026-10-01.

D15. (Q12) Where each action leads:

- Sign-up logs the new user in and goes to home.
- Login goes to home.
- Logout goes to the login page.

Settings: `LOGIN_URL = "login"`, `LOGIN_REDIRECT_URL = "home"`, `LOGOUT_REDIRECT_URL = "login"`. Source: user, 2026-10-01.

D17. (Q14) Logout is a POST form in the nav, with `{% csrf_token %}`. Django's `LogoutView` handles it. Source: user, 2026-10-01.

D21. (Q19) `settings_test.py` sets `PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]` to keep auth tests fast. Test-only, no new dependency. Source: user, 2026-10-01.

### Profile

D7. (Q5) Every new user gets an empty Profile, with no cohort and no focus areas.

A `post_save` receiver on User in `accounts/signals.py` creates it, connected in `AccountsConfig.ready()`. That also covers users made with `createsuperuser` or in the admin.

While the profile has no cohort, home shows "Complete your profile" with a link to the edit form. Source: user, 2026-10-01 (signal: plan).

D11. (Q9) Users can edit their first name, last name and focus areas. They can't edit cohort (D9), username or email in this ticket. Source: user ("focus areas tags etc."), 2026-10-01; reading confirmed in chat.

D12. (Q9) Deleting an account takes two steps:

- `GET /accounts/delete/` shows "Are you sure? Deleting profiles is permanent" and a POST button.
- The POST deletes the user (the profile goes with it), logs out and goes to the login page.

A GET never deletes. Source: user, 2026-10-01 (page and redirect: plan, agreed in chat).

D13. (Q10) Who sees which profile:

- `/profile/` redirects to `/profile/<pk>/` for the logged-in user.
- `/profile/<pk>/` returns 200 to its owner and to any `is_staff` user.
- Any other logged-in user gets 403.
- A missing pk returns 404.

Staff only view profiles in the app. They edit them in `/admin/`. Source: user, 2026-10-01.

D31 replaces the 404 rule for users who aren't staff.

D18. (Q16) The admin registers every model. `accounts/admin.py` registers User (with Django's `UserAdmin`), Profile and Cohort. `core/admin.py` registers Tag. Source: user, 2026-10-01.

### Pages

D14. (Q11) Every page except login and sign-up requires login. An anonymous visitor goes to `LOGIN_URL` with `?next=`. Source: user, 2026-10-01.

D16. (Q13) There's no landing page. Home requires login (D14).

The login page shows a punchline next to the form. Placeholder text: "Set goals. Log sessions. See how far you've come."

Logged-in pages have a nav bar:

- on the left, the text logo "Learning Companion", linking to home;
- on the right, a "Profile" link and the logout button.

Anonymous visitors see no nav. Source: user, 2026-10-01 (punchline text and Profile link: plan).

D27. HTMX isn't used in this ticket. CLAUDE.md names the goals ticket as its first user. Every form is a plain POST. Source: CLAUDE.md.

### Code layout

D22. Routes live in a new `accounts/urls.py`. The root `learning_companion/urls.py` includes it at `""` with `include("accounts.urls")`.

There's no `app_name`, so the names stay plain and `LOGIN_URL = "login"` works:

| Path | Name |
|---|---|
| `accounts/signup/` | `signup` |
| `accounts/login/` | `login` (`LoginView`) |
| `accounts/logout/` | `logout` (`LogoutView`) |
| `accounts/delete/` | `account_delete` |
| `profile/` | `profile` |
| `profile/<int:pk>/` | `profile_detail` |
| `profile/edit/` | `profile_edit` |

Source: plan.

D23. Views are function-based, like `core/views.py:4-5`. Login and logout use Django's `LoginView` and `LogoutView`.

Templates:

- `accounts/templates/registration/login.html` (`LoginView`'s default name, found through `APP_DIRS`);
- the rest in `accounts/templates/accounts/`.

Source: plan, refinement Patterns.

D24. Forms live in `accounts/forms.py`:

- `SignUpForm(UserCreationForm)` has the D6 fields and the case-insensitive email check.
- `ProfileForm` edits `first_name`, `last_name` and `focus_areas` (`CheckboxSelectMultiple`). While `profile.cohort` is unset, it adds a required `cohort` field that offers only active cohorts.

Source: plan.

D25. Once home requires login, ticket 1's `test_ac2_home_page_is_styled_by_tailwind` and `test_ac3_base_template_loads_htmx` in `tests/test_home.py` would fail, because they request `/` anonymously. Step 4 switches both to `logged_in_client` and keeps their assertions. Source: code.

D26. A new `tests/conftest.py` holds the shared fixtures:

- `password`: `"Sup3r-secret-pw"`;
- `user`: `ada`, `ada@example.com`, Ada Lovelace;
- `other_user`: `grace`, `grace@example.com`, Grace Hopper;
- `staff_user`: `staff`, `is_staff=True`;
- `logged_in_client`: `client.force_login(user)`;
- `signup_data(**overrides)`: a plain function returning valid sign-up POST data for `linus`, `linus@example.com`, Linus Torvalds.

The user fixtures create users with `django_user_model.objects.create_user` and take the `db` fixture for database access. Test modules that use the database without these fixtures carry `pytestmark = pytest.mark.django_db`. Source: plan; corrected for R7, 2026-10-01.

D28. `startapp accounts` creates files with unused imports and an `accounts/tests.py`. As in ticket 1 (D19 there), the build removes the unused imports and deletes `accounts/tests.py`. Tests live in `tests/`. Source: ticket-1 plan.

### Testing

D30. (Q22, R1) A username that looks like an email would hijack email login for the real owner of that address (D5). Answer: sign-up rejects usernames that contain `@`. Admins can still create one in `/admin/`. Source: user, 2026-10-01, during review.

D31. (Q23, R4) A 404 for missing pks and a 403 for existing ones tells a visitor which user ids exist. Answer: `profile_detail` checks permission before the lookup. A user who isn't the owner or staff gets 403 for any pk, existing or not. Staff still get 404 for a missing pk. This replaces D13's "A missing pk returns 404" for everyone but staff. Source: user, 2026-10-01, during review.

D32. (Q24, R10) Logged-in users who open `/accounts/login/` saw the nav with a logout button above the login form. Answer: every page shows the nav with the "Learning Companion" logo on the left. The Profile link and the logout button appear only for logged-in users. This replaces D16's "Anonymous visitors see no nav". Source: user, 2026-10-01, during review.

D33. (Q25, R10) With the nav from D32, a logged-in user on the login page saw a login form they don't need. Answer: `LoginView` gets `redirect_authenticated_user=True`, so a logged-in user who opens `/accounts/login/` goes to home. Source: user, 2026-10-01, during review.

D34. (Q26, R12) A user can end up without a profile: a `loaddata` fixture without profiles (D7's receiver skips raw saves since step 17), or a profile deleted in the admin. `home` and `profile_edit` then crash. Does recreating it contradict the deletion? No: D7 says every user has a profile, and account deletion (D12) is the way to remove someone's data. Answer: a missing profile is recreated empty on the user's next visit, which acts as a profile reset. `accounts.models.profile_for(user)` does `Profile.objects.get_or_create(user=user)`. Source: user, 2026-10-01, during review.

D29. (Q21) Ruff's `RUF012` flags the list class attributes Django generates in every migration. `pyproject.toml` ignores only that rule for `*/migrations/*`; migrations are still linted otherwise, and `make format` formats them. Source: user, 2026-10-01, during build.

D20. (Q18) Automated tests cover every criterion. When the build is done, it asks the user whether they also want to check by hand. Source: user, 2026-10-01.

## Acceptance criteria

- [x] AC1. Confirm you can sign up, log out, and log back in, and that the profile page only shows your own data. → step 14
- [x] AC2. Signing up with invalid data (a username already taken, passwords that don't match, a password the validators reject) shows the errors on the form and creates no user → step 16
- [x] AC3. Logging in with a wrong password shows an error and leaves the visitor logged out → step 3
- [x] AC4. A visitor who is not logged in sees no profile data when they open the profile page → step 7
- [x] AC5. After logging out, the profile page no longer shows the previous user's data → step 7
- [x] AC6. A logged-in user stays logged in after reloading a page → step 3
- [x] AC7. A user whose profile has no focus areas sees the profile page without errors → step 7
- [x] AC8. A user can log in with their email address, in any letter case, as well as with their username (from D5) → step 5
- [x] AC9. Signing up with an email that another user already has, in any letter case, shows an error and creates no user (from D5) → step 2
- [x] AC10. Sign-up requires first name and last name and stores them with the email on the new user (from D6) → step 15
- [x] AC11. A new user is logged in straight away and lands on home (from D15) → step 1
- [x] AC12. Login leads to home and logout leads to the login page (from D15) → step 3
- [x] AC13. Every new user has a profile, and home shows "Complete your profile" until the profile has a cohort (from D7) → step 17
- [x] AC14. After migrating, Cohort 1, 2 and 3 and the starting focus-area tags exist (from D9) → step 6
- [x] AC15. `/profile/` opens the logged-in user's own profile (from D13) → step 7
- [x] AC16. A user who opens another user's profile gets 403, whether that profile exists or not, and a staff user can open any profile (from D13, D31) → step 13
- [x] AC17. The profile form offers only active cohorts and requires one while the cohort is unset. Once it's set, the user can't change it (from D9) → step 8
- [x] AC18. A user can change their first name, last name and focus areas (from D11) → step 8
- [x] AC19. Deleting the account asks "Are you sure? Deleting profiles is permanent" first. Confirming deletes the user and the profile, logs out and leads to the login page (from D12) → step 11
- [x] AC20. Home requires login, and the login page shows the punchline next to the form (from D14, D16) → step 4
- [x] AC21. Every page shows a nav with the "Learning Companion" logo on the left. Logged-in pages also show a Profile link and a logout button on the right. The login page shows only the logo (from D16, D17, D32) → step 20
- [x] AC22. User, Profile, Cohort and Tag are in the admin, and a staff user can list all profiles there (from D18) → step 10
- [x] AC23. Signing up with a username that contains `@` shows an error and creates no user (from D30) → step 12
- [x] AC24. A logged-in user who opens the login page goes to home (from D33) → step 19
- [x] AC25. A user whose profile is missing gets a new empty one the next time they open home, their profile or the profile form (from D34) → step 21

## Step 0: groundwork

No tests of its own. The existing suite has to stay green.

**The app.** Run `manage.py startapp accounts` and tidy it per D28. Add `"accounts"` to `INSTALLED_APPS` in `learning_companion/settings.py`, after `"core"`.

**The User.** In `accounts/models.py`, add `class User(AbstractUser): pass` with a docstring that points to D2. Set `AUTH_USER_MODEL = "accounts.User"` in settings. Run `manage.py makemigrations accounts`, which creates `accounts/migrations/0001_initial.py`.

**Test settings.** Add `PASSWORD_HASHERS` from D21 to `learning_companion/settings_test.py`, after `from .settings import *`.

**Fixtures.** Create `tests/conftest.py` with the D26 fixtures.

**The local database.** Delete `db.sqlite3` and run `make migrate` (D19). `make migrate` needs the user's `.env` for `SECRET_KEY`. If it stops, ask the user to run it.

**Check.**

- `make test` passes the 11 existing tests.
- `make lint` is clean.
- `.venv/bin/python manage.py makemigrations --check --dry-run` reports no changes.

## Step 1: AC10, AC11, sign-up creates a user and logs them in

**Test.** Write these in `tests/test_signup.py`, using `signup_data()` from `tests/conftest.py`.

- `test_ac10_signup_stores_names_and_email(client, django_user_model)`: GET `reverse("signup")` first and assert 200 with `accounts/signup.html`. Then POST `signup_data()`. Assert a user `linus` exists with the form's email, first name and last name.
- `test_ac10_signup_requires_names(client, django_user_model)`, parametrized over `"first_name"` and `"last_name"`: POST with that field blank. Assert 200, an error on that field, and no user.
- `test_ac11_signup_logs_in_and_redirects_home(client)`: POST `signup_data()` with `follow=True`. Assert the chain ends at `reverse("home")` and `response.wsgi_request.user.is_authenticated`.

**Red.** At first `reverse("signup")` raises `NoReverseMatch`. That's an error, not an assertion. So start by adding the route in `accounts/urls.py` (and its `include` in the root `urls.py`), pointing at a `signup` stub that returns `HttpResponse("")`.

Then the tests fail on their assertions: no user is created, and nothing redirects.

**Green.**

- `accounts/forms.py`: `SignUpForm(UserCreationForm)` with `Meta.model = User` and `fields = ("username", "email", "first_name", "last_name")`. `email`, `first_name` and `last_name` get `required=True`.
- `accounts/views.py`: `signup(request)` saves the form, calls `login(request, user)` and redirects to `home`. On GET or invalid data it renders `accounts/signup.html`.
- `accounts/templates/accounts/signup.html`: extends `base.html`, with the form, `{% csrf_token %}` and a link to login.
- Settings: `LOGIN_URL`, `LOGIN_REDIRECT_URL` and `LOGOUT_REDIRECT_URL` (D15).

**Refactor.** None.

## Step 2: AC2, AC9, sign-up rejects invalid data

**Test.** In `tests/test_signup.py`:

`test_ac2_signup_rejects_invalid_data(client, user, django_user_model)` is parametrized with ids:

- `taken_username`: `username="ada"`, error on `username`;
- `password_mismatch`: `password2="Different-pw-99"`, error on `password2`;
- `weak_password`: both passwords `"12345678"`, error on `password2`.

Each row POSTs `signup_data(**row)`. It asserts 200, an error on the named field, and that `ada` is still the only user.

`test_ac9_signup_rejects_taken_email(client, user, django_user_model)` is parametrized over `"ada@example.com"` and `"ADA@Example.com"`. It asserts 200, an error on `email`, and a user count of 1.

**Red.** The three AC2 rows pass already, because `UserCreationForm` makes those checks. That's expected.

The AC9 rows fail on the assertion. The form accepts the duplicate email and creates a second user.

**Green.** `SignUpForm.clean_email()` raises `ValidationError` when `User.objects.filter(email__iexact=email).exists()`.

**Refactor.** None.

## Step 3: AC3, AC6, AC12, login and logout

**Test.** In `tests/test_login.py`:

- `test_ac12_login_redirects_home(client, user, password)`: POST `username="ada"` and the password to `reverse("login")`, with `follow=True`. Assert the chain ends at `reverse("home")` and the user is logged in.
- `test_ac12_logout_redirects_to_login(logged_in_client)`: POST to `reverse("logout")` with `follow=True`. Assert the chain ends at `reverse("login")` and the user is anonymous.
- `test_ac3_wrong_password_shows_error(client, user)`: POST `password="wrong-pw"`. Assert 200, a non-empty `response.context["form"].non_field_errors()`, and no `"_auth_user_id"` in `client.session`.
- `test_ac6_session_survives_reload(client, user, password)`: log in with a POST, then GET `reverse("home")` twice. Assert the second response's `wsgi_request.user == user`.

**Red.** All four fail with `NoReverseMatch`, because the `login` and `logout` routes don't exist.

That's the only red this step can show. Django's `LoginView` and `LogoutView` do the whole job once the routes and a template exist. The build records the `NoReverseMatch` run in the build log. Step 4 tests the template's content (AC20).

**Green.**

- `accounts/urls.py`: `accounts/login/` to `auth_views.LoginView.as_view()`, and `accounts/logout/` to `auth_views.LogoutView.as_view()`.
- `accounts/templates/registration/login.html`: extends `base.html`. It renders `form` with `{% csrf_token %}`, shows `form.non_field_errors`, and links to sign-up.

**Refactor.** None.

## Step 4: AC20, AC21, home requires login, login page, nav bar

**Test.**

First, switch ticket 1's two tests in `tests/test_home.py` to `logged_in_client` (D25), keeping their assertions.

Then add:

- `tests/test_home.py`, `test_ac20_home_requires_login(client)`: GET `/`. Assert a 302 to `f"{reverse('login')}?next=/"`.
- `tests/test_login.py`, `test_ac20_login_page_shows_punchline(client)`: GET `reverse("login")`. Assert 200, the punchline text, and a `<form` with `name="username"`.
- `tests/test_home.py`, `test_ac21_nav_has_logo_and_logout(logged_in_client)`: GET `/`. Assert a `<nav`, a link to `reverse("home")` reading "Learning Companion", and a form with `action="{reverse('logout')}"` and `method="post"`.
- `tests/test_login.py`, `test_ac21_login_page_has_no_nav(client)`: GET `reverse("login")`. Assert no `<nav` in the content.

**Red.**

- The home test fails: status 200 instead of 302.
- The punchline test fails: the text is missing.
- The nav test fails: there's no `<nav`.

The no-nav test passes already, since no page has a nav yet. That's expected, because it guards the `{% if user.is_authenticated %}` that Green adds. The two switched ticket-1 tests stay green.

**Green.**

- `core/views.py`: `@login_required` on `home`.
- `registration/login.html`: two columns, punchline beside the form.
- `theme/templates/base.html`: inside `{% if user.is_authenticated %}`, a `<nav>`. The logo link sits on the left. On the right are a "Profile" link (its target comes in step 7) and the logout form with `{% csrf_token %}`.

**Refactor.** None.

## Step 5: AC8, log in with email

**Test.** `tests/test_login.py`, `test_ac8_login_accepts_username_or_email(client, user, password)`, parametrized over `"ada"`, `"ada@example.com"` and `"ADA@example.com"`.

Each row POSTs the value as `username`, with the password. It asserts a redirect to `home` and a logged-in user.

**Red.** The `"ada"` row passes already, through Django's default backend.

The two email rows fail on the assertion: 200 with a form error. `ModelBackend` only matches usernames.

**Green.** `accounts/backends.py`: `UsernameOrEmailBackend(ModelBackend)` overrides `authenticate(self, request, username=None, password=None, **kwargs)`.

It tries `User.objects.get(username=username)`, then `User.objects.get(email__iexact=username)`. It checks the password and `user_can_authenticate`, and returns `None` when neither lookup finds anyone.

Settings: `AUTHENTICATION_BACKENDS = ["accounts.backends.UsernameOrEmailBackend"]`.

**Refactor.** None.

## Step 6: AC13, AC14, profile models, seed data and the auto-created profile

**Test.** In `tests/test_profile.py`:

- `test_ac13_every_new_user_has_a_profile(django_user_model)`: create a user with `create_user`. Assert `user.profile.cohort is None` and `user.profile.focus_areas.count() == 0`.
- `test_ac13_home_prompts_until_cohort_set(logged_in_client, user)`: GET `/`. Assert "Complete your profile" and a link to `reverse("profile_edit")`. Set the profile's cohort to `Cohort.objects.get(name="Cohort 1")`, save and GET again. Assert the text is gone.
- `test_ac14_seed_cohorts_and_tags_exist(db)`: assert the active cohort names are `["Cohort 1", "Cohort 2", "Cohort 3"]` and the tag names match the D9 list, as a set.

**Red.** At first the imports fail: `Cohort` and `Tag` don't exist. To get an assertion failure, step 6 starts with Green parts 1 and 2 (models and schema migrations), without the signal or the seeds.

`reverse("profile_edit")` needs a route, so add a `profile_edit` stub returning `HttpResponse("")`. Step 8 builds it.

Then the tests fail on their assertions. `user.profile` raises `RelatedObjectDoesNotExist`, the cohort and tag sets are empty, and home has no prompt.

**Green.**

1. Models. `core/models.py` gets `Tag`. `accounts/models.py` gets `Cohort` and `Profile`, where `user` is `OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="profile")`, and `cohort` and `focus_areas` follow D9. Each has `__str__` (the name, or the username) and `Meta.ordering` by name.
2. Schema migrations: `manage.py makemigrations core accounts`.
3. Seed migrations: `makemigrations core --empty --name seed_tags` and `makemigrations accounts --empty --name seed_cohorts`. Each has a `RunPython` that creates the D9 data and a reverse function that deletes it.
4. The signal. `accounts/signals.py` has a `post_save` receiver on `User` that creates a `Profile` when `created`. `AccountsConfig.ready()` in `accounts/apps.py` imports it.
5. Home. `core/views.py` `home` passes `profile=request.user.profile`. `core/home.html` shows the prompt while `profile.cohort` is `None`.

**Refactor.** None.

## Step 7: AC1, AC4, AC5, AC7, AC15, AC16, the profile page

**Test.** In `tests/test_profile.py`:

- `test_ac15_profile_redirects_to_own(logged_in_client, user)`: GET `reverse("profile")`. Assert a redirect to `reverse("profile_detail", args=[user.pk])`.
- `test_ac16_profile_access(client, user, request, viewer, status)`, parametrized with ids `owner` (200), `other_user` (403) and `staff` (200): force-login the viewer fixture with `request.getfixturevalue`, GET `user`'s profile, and assert the status.
- `test_ac16_missing_profile_is_404(logged_in_client)`: GET pk `999999`. Assert 404.
- `test_ac4_anonymous_sees_no_profile_data(client, user)`: GET `user`'s profile. Assert a 302 to login with `?next=`, and no `"ada@example.com"` in the content.
- `test_ac7_profile_without_focus_areas(logged_in_client, user)`: GET own profile. Assert 200, "Ada Lovelace" and "No focus areas yet".
- `test_ac5_logout_hides_profile(logged_in_client, user)`: GET own profile (200), POST logout, then GET it again. Assert a 302 to login and no `"ada@example.com"`.

`test_ac1_signup_logout_login_shows_own_profile(client, other_user)` walks the supplied criterion end to end:

1. sign up as `linus` with `signup_data()`;
2. POST logout;
3. POST login as `linus`;
4. GET `reverse("profile")` with `follow=True`.

It asserts 200, that "Linus Torvalds" and "linus@example.com" are present, and that "grace" and "grace@example.com" are not.

**Red.** `reverse("profile")` raises `NoReverseMatch`. Add both routes, pointing at stubs that return `HttpResponse("")`.

Then the tests fail on their assertions: an empty 200 instead of the redirect, the 403, the 404 or the profile data. AC4 and AC5 fail on the missing 302, since the stubs don't require login.

**Green.** In `accounts/views.py`:

- `profile(request)`: `@login_required`, redirects to `profile_detail` with `request.user.pk`.
- `profile_detail(request, pk)`: `@login_required`, `get_object_or_404(Profile, user__pk=pk)`. Raises `PermissionDenied` unless the viewer is the owner or `is_staff`. Renders `accounts/profile_detail.html`.

The page shows full name, username, email, the cohort (or "Not set"), and the focus areas (or "No focus areas yet"). The owner also sees links to edit and delete.

In `base.html`, point the nav's "Profile" link at `reverse("profile")`.

**Refactor.** None.

## Step 8: AC17, AC18, the profile edit form

**Test.** In `tests/test_profile.py`:

- `test_ac17_cohort_choices_are_active_only(logged_in_client)`: set Cohort 3 inactive, then GET `reverse("profile_edit")`. Assert the `cohort` field's choices are Cohort 1 and Cohort 2.
- `test_ac17_cohort_required_while_unset(logged_in_client, user)`: POST names but no cohort. Assert 200, an error on `cohort`, and the cohort still `None`.
- `test_ac17_cohort_locked_once_set(logged_in_client, user)`: set Cohort 1. GET the form and assert `"cohort"` isn't among its fields. Then POST `cohort=<Cohort 2 pk>` with valid names. Assert the cohort is still Cohort 1.
- `test_ac18_user_edits_names_and_focus_areas(logged_in_client, user)`: POST `first_name="Augusta"`, `last_name="King"`, Cohort 1, and the tags "Python" and "Testing". Assert a redirect to `reverse("profile")`, the new names, and exactly those two focus areas.

**Red.** All four fail on their assertions. The step-6 stub returns an empty 200 with no `form` in its context, and the POST changes nothing.

**Green.** `accounts/forms.py`, `ProfileForm` (D24):

- It takes `instance=profile` and edits `first_name` and `last_name` on `profile.user`.
- In `__init__`, if `instance.cohort` is `None`, it adds `cohort` as `ModelChoiceField(queryset=Cohort.objects.filter(is_active=True), required=True)`.
- `save()` saves the names, the cohort (when the field exists) and `focus_areas`.

`accounts/views.py`, `profile_edit(request)`: `@login_required`. GET renders `accounts/profile_form.html`. A valid POST saves and redirects to `profile`.

**Refactor.** None.

## Step 9: AC19, account deletion

**Test.** In `tests/test_account_delete.py`:

- `test_ac19_delete_asks_first(logged_in_client, user, django_user_model)`: GET `reverse("account_delete")`. Assert 200, "Are you sure? Deleting profiles is permanent", a `method="post"` form, and that the user still exists.
- `test_ac19_delete_removes_user_and_profile(logged_in_client, user, django_user_model)`: POST with `follow=True`. Assert the chain ends at `reverse("login")`, the user is anonymous, and no `User` or `Profile` with that pk remains.
- `test_ac19_delete_requires_login(client)`: GET. Assert a 302 to login.

**Red.** `reverse("account_delete")` raises `NoReverseMatch`. Add the route to a stub returning `HttpResponse("")`. Then all three fail on their assertions: no text, no deletion, no redirect.

**Green.** `accounts/views.py`, `account_delete(request)`: `@login_required`.

- GET renders `accounts/account_confirm_delete.html`.
- POST runs `user = request.user`, `logout(request)`, `user.delete()`, then redirects to `login`.

**Refactor.** None.

## Step 10: AC22, admin registration

**Test.** In `tests/test_admin.py`:

- `test_ac22_models_registered_in_admin()`, parametrized over `User`, `Profile`, `Cohort` and `Tag`: assert `admin.site.is_registered(model)`.
- `test_ac22_staff_lists_profiles(admin_client, user, other_user)`: GET `reverse("admin:accounts_profile_changelist")`. Assert 200 and that "ada" and "grace" appear.

**Red.** The registration rows fail on the assertion: `is_registered` returns `False`. The changelist test fails with `NoReverseMatch`, because the admin URL only exists after registration. The build log records that as its red.

**Green.**

- `accounts/admin.py`: `admin.site.register(User, UserAdmin)`. `@admin.register` for `Profile` (`list_display = ("user", "cohort")`) and `Cohort` (`list_display = ("name", "is_active")`).
- `core/admin.py`: `@admin.register(Tag)`.

**Refactor.** None.

## Step 11: rework R2, AC19, the confirmation test checks the delete form

**Test.** In `tests/test_account_delete.py`, change `test_ac19_delete_asks_first`.

Replace `assert 'method="post"' in content` with a regex for a `<form method="post"` whose content holds the "Delete my account" button. The nav's logout form has `action="/accounts/logout/"` and no such button, so it no longer satisfies the check.

**Red.** None: test-only change. The page already has the delete form, so the suite stays green.

**Green.** None.

**Refactor.** None.

## Step 12: rework R1, AC23, usernames can't contain `@`

**Test.** In `tests/test_signup.py`, add `test_ac23_signup_rejects_at_in_username(client, django_user_model)`.

It POSTs `signup_data(username="ada@example.com")`. It asserts 200, an error on `username`, and no user.

**Red.** Fails on the assertion: the form accepts the username, and the response is a 302.

**Green.** `SignUpForm.clean_username()` in `accounts/forms.py` raises `ValidationError` when the username contains `@`.

**Refactor.** None.

## Step 13: rework R4, AC16, permission before the lookup

**Test.** In `tests/test_profile.py`:

- Change `test_ac16_missing_profile_is_404(client, staff_user)`: force-login `staff_user`, GET pk `999999`, assert 404.
- Add `test_ac16_non_owner_gets_403_for_missing_profile(logged_in_client)`: GET pk `999999` as `ada`, assert 403.

**Red.** The new test fails on the assertion: `get_object_or_404` runs first and returns 404. The changed 404 test passes already for staff.

**Green.** In `accounts/views.py`, `profile_detail` raises `PermissionDenied` before calling `get_object_or_404` when the viewer is neither the owner nor staff.

**Refactor.** None.

## Step 14: rework R5, AC1, the walk-through checks the logout

**Test.** In `tests/test_profile.py`, `test_ac1_signup_logout_login_shows_own_profile`: after the logout POST, assert `"_auth_user_id" not in client.session`.

**Red.** None: test-only change. Logout works, so the suite stays green.

**Green.** None.

**Refactor.** None.

## Step 15: rework R6, AC10, email is required at sign-up

**Test.** In `tests/test_signup.py`, rename `test_ac10_signup_requires_names` to `test_ac10_signup_requires_names_and_email` and add `"email"` to its parametrize list.

**Red.** None: test-only change. `SignUpForm` already makes email required, so the suite stays green.

**Green.** None.

**Refactor.** None.

## Step 16: rework R8, AC2, case-insensitive taken usernames

**Test.** In `tests/test_signup.py`, add a row to `test_ac2_signup_rejects_invalid_data`: `{"username": "ADA"}`, error on `username`, id `taken_username_other_case`.

**Red.** The new row fails on `assert 302 == 200`. `SignUpForm.clean_username` replaces Django's check for usernames that differ only in case, so `ADA` is accepted.

**Green.** In `accounts/forms.py`, `SignUpForm.clean_username` starts with `username = super().clean_username()` and checks for `@` only when `username` is set (the parent returns `None` once it has recorded the error).

**Refactor.** None.

## Step 17: rework R9, AC13, no extra profile on `loaddata`

**Test.** In `tests/test_profile.py`, add `test_ac13_raw_save_creates_no_profile(django_user_model)`.

It builds `User(username="loaded")`, saves it with `save_base(raw=True)` as `loaddata` does, and asserts `Profile.objects.filter(user__username="loaded").exists()` is `False`.

**Red.** Fails on the assertion: the receiver creates a profile on every `created` save, raw or not.

**Green.** In `accounts/signals.py`, the receiver checks `if created and not kwargs.get("raw"):`.

**Refactor.** None.

## Step 18: rework R10, AC21, the nav on every page

**Test.** In `tests/test_login.py`, replace `test_ac21_login_page_has_no_nav` with `test_ac21_login_page_nav_has_logo_only(client)`.

It GETs `reverse("login")` as an anonymous visitor. It asserts a `<nav`, a link to `reverse("home")` reading "Learning Companion", no form with `action="{reverse('logout')}"`, and no link to `reverse("profile")`.

`test_ac21_nav_has_logo_and_logout` in `tests/test_home.py` stays as it is.

**Red.** Fails on the assertion: `<nav` is missing, because `base.html` wraps the whole nav in `{% if user.is_authenticated %}`.

**Green.** In `theme/templates/base.html`, the `<nav>` and the logo are always rendered. `{% if user.is_authenticated %}` wraps only the right side: the Profile link and the logout form.

**Refactor.** None.

## Step 19: rework R10, AC24, logged-in users skip the login page

**Test.** In `tests/test_login.py`, add `test_ac24_logged_in_user_skips_login(logged_in_client)`. It GETs `reverse("login")` and asserts a 302 to `reverse("home")`.

**Red.** Fails on the assertion: status 200, since `LoginView` shows the form to anyone.

**Green.** In `accounts/urls.py`, `auth_views.LoginView.as_view(redirect_authenticated_user=True)`.

**Refactor.** None.

## Step 20: rework R11, AC21, the nav test checks the Profile link

**Test.** In `tests/test_home.py`, `test_ac21_nav_has_logo_and_logout`: add `assert f'href="{reverse("profile")}"' in content`.

**Red.** None: test-only change. The nav already has the link, so the suite stays green.

**Green.** None.

**Refactor.** None.

## Step 21: rework R12, AC25, a missing profile is recreated

**Test.** In `tests/test_profile.py`, add `test_ac25_missing_profile_is_recreated(logged_in_client, user, url)`, parametrized over `reverse("home")`, `reverse("profile_edit")` and `reverse("profile_detail", args=[user.pk])` (built inside the test from a name and a flag for the pk).

Each row deletes `user.profile`, GETs the page, and asserts 200 and a `Profile` for `user` with `cohort` `None`.

**Red.** The `home` and `profile_edit` rows fail with `RelatedObjectDoesNotExist`, the crash R12 describes. The `profile_detail` row fails on `assert 404 == 200`.

**Green.** `accounts/models.py`: `profile_for(user)` returns `Profile.objects.get_or_create(user=user)[0]`. `core/views.py` `home` and `accounts/views.py` `profile_edit` use it in place of `request.user.profile`. `profile_detail` uses it when the viewer opens their own profile, and keeps `get_object_or_404` for staff viewing others.

**Refactor.** None.

## Review

### Round 1, 2026-10-01

- R1. should-fix, `accounts/backends.py`: a username like `ada@example.com` takes over Ada's email login, because the username match wins. → Q22, D30 → fixed in step 12
- R2. should-fix, `tests/test_account_delete.py:15`: `method="post"` also matches the nav's logout form. → fixed in step 11 (auto)
- R3. nit, `accounts/forms.py`: only sign-up enforces unique email; the admin and `createsuperuser` can make duplicates, and there's no database constraint. → follow-up
- R4. nit, `accounts/views.py`: 404 versus 403 tells non-owners which user ids exist. → Q23, D31 → fixed in step 13
- R5. nit, `tests/test_profile.py`: the AC1 walk-through never checks that the logout worked. → fixed in step 14
- R6. nit, `tests/test_signup.py`: no test checks that email is required at sign-up. → fixed in step 15
- R7. nit: D26 says `django_user_model` gives database access; the fixtures take `db` (Progress, step 1). → plan updated 2026-10-01

### Round 2, 2026-10-01

- R8. should-fix, `accounts/forms.py:18`: `clean_username` skips Django's check, so `Ada` signs up next to `ada`. → fixed in step 16
- R9. nit, `accounts/signals.py:10`: `loaddata` triggers the receiver and creates duplicate profiles. → fixed in step 17
- R10. nit, `accounts/urls.py:8`: a logged-in user on the login page sees the nav and a logout button. → Q24, D32, Q25, D33 → plan updated 2026-10-01 → fixed in steps 18, 19

### Round 3, 2026-10-01

- R11. should-fix, `tests/test_home.py:31`: no test checks the nav's Profile link for logged-in users. → fixed in step 20
- R12. nit, `core/views.py:7`: a user without a profile (fixture load, admin delete) crashes `home` and `profile_edit`. → Q26, D34 → fixed in step 21

### Round 4, 2026-10-01

No findings (scope: steps 20 and 21, asked for by the user).

## Files

**New, `accounts` app:**

- `accounts/__init__.py`, `apps.py`, `migrations/__init__.py`: from `startapp` (D28).
- `accounts/models.py`: User, Cohort, Profile.
- `accounts/migrations/0001_initial.py`: User (step 0).
- `accounts/migrations/0002_*.py`: Cohort and Profile (step 6, named by `makemigrations`).
- `accounts/migrations/0003_seed_cohorts.py`: Cohort 1 to 3 (step 6).
- `accounts/backends.py`: `UsernameOrEmailBackend` (D5).
- `accounts/forms.py`: `SignUpForm`, `ProfileForm` (D24).
- `accounts/signals.py`: the auto-created profile (D7).
- `accounts/views.py`: `signup`, `profile`, `profile_detail`, `profile_edit`, `account_delete`.
- `accounts/urls.py`: the D22 routes.
- `accounts/admin.py`: User, Profile, Cohort (D18).
- `accounts/templates/registration/login.html`: login with the punchline (D16).
- `accounts/templates/accounts/signup.html`, `profile_detail.html`, `profile_form.html`, `account_confirm_delete.html`.

**New, `core`:**

- `core/migrations/0001_initial.py`: Tag (step 6).
- `core/migrations/0002_seed_tags.py`: the starting tags (step 6).

**New, tests:**

- `tests/conftest.py`: shared fixtures and `signup_data` (D26).
- `tests/test_signup.py`, `test_login.py`, `test_profile.py`, `test_account_delete.py`, `test_admin.py`.

**Changed:**

- `pyproject.toml`: per-file ignore of `RUF012` for migrations (D29).
- `core/models.py`: `Tag`.
- `core/admin.py`: Tag (D18).
- `core/views.py`: `@login_required` on `home`, and the profile prompt (via `profile_for`, D34).
- `core/templates/core/home.html`: the "Complete your profile" prompt.
- `theme/templates/base.html`: the nav bar (D16, D17).
- `learning_companion/urls.py`: `include("accounts.urls")`.
- `learning_companion/settings.py`: `"accounts"` in `INSTALLED_APPS`, `AUTH_USER_MODEL`, `AUTHENTICATION_BACKENDS`, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`.
- `learning_companion/settings_test.py`: `PASSWORD_HASHERS` (D21).
- `tests/test_home.py`: ticket 1's two tests use `logged_in_client` (D25).

**Local only, not tracked:** `db.sqlite3`, deleted and re-migrated (D19).

## Verification

After each new test, `make test ARGS="-k <test name>"` fails for the reason in the step's Red.

After each Green, `make test` passes in full.

At the end:

- `make test`: all tests pass.
- `make lint`: no errors.
- `make format`: no files changed.
- `.venv/bin/python manage.py makemigrations --check --dry-run`: no missing migrations.

The project has no type check or separate build step.

When done, ask the user whether they want to check the flow by hand (D20). If they do:

1. `make dev`;
2. sign up and complete the profile;
3. log out, then log in with the email;
4. open another user's `/profile/<pk>/` and see 403;
5. delete the account.
