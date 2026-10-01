# CRUD for goals and learning sessions: refinement

## Context

Add the core domain: a Goal (title, description, status planned / in-progress / done,
created_at, updated_at) and a LearningSession linked to a Goal (date, duration, notes,
tags), with migrations, and list, create, edit and delete pages for both. A user only ever
sees their own goals and sessions, and the goals list can be filtered by status.

The project is the ticket-3 codebase: a custom User, sign-up, email login and profiles in
`accounts`, and a global admin-managed `Tag` model in `core`. No goal or session code
exists yet. Branch: currently `feature/3-authentication-and-profile-management`; no branch
for #4 yet.

Source: #4 (https://github.com/GPlastok/learning-companion/issues/4)

## Progress

Refinement done on 2026-10-01. Nothing planned or built yet. Next: the user answers the
open questions, then a plan is written.

## Acceptance criteria

The ticket has no criteria section or checklist, so all of these come from the ticket
text and the existing features.

Goals:

- [ ] A logged-in user can create a goal with a title, a description and a status, and it then appears in their goals list
- [ ] A goal's status can only be planned, in-progress or done; any other value shows a form error and saves nothing
- [ ] Submitting the goal form without a title shows an error on the form and saves nothing
- [ ] A goal stores when it was created and when it was last updated; editing it changes the updated time and leaves the created time as it was
- [ ] A user can edit their goal, and the list shows the new values afterwards
- [ ] A user can delete their goal after a confirmation step, and it no longer appears in the list
- [ ] The goals list shows only the logged-in user's goals, never another user's
- [ ] Opening the edit or delete page of another user's goal neither shows nor changes that goal
- [ ] Filtering the goals list by a status shows only the user's goals with that status
- [ ] The goals list without a filter shows all of the user's goals
- [ ] A user with no goals, or a filter with no matching goals, sees an empty-state message instead of an empty list

Learning sessions:

- [ ] A logged-in user can create a learning session for one of their goals with a date, a duration, notes and tags, and it then appears in their sessions list
- [ ] The session form offers only the user's own goals; submitting another user's goal saves nothing and shows an error
- [ ] Tags on a session are chosen from the existing tags, and the chosen tags are shown with the session
- [ ] A session with no tags saves without errors
- [ ] Submitting the session form without a date, without a duration or with a duration of zero or less shows an error and saves nothing
- [ ] A user can edit their session, and the list shows the new values afterwards
- [ ] A user can delete their session after a confirmation step, and it no longer appears in the list
- [ ] The sessions list shows only the logged-in user's sessions, never another user's
- [ ] Opening the edit or delete page of another user's session neither shows nor changes that session
- [ ] A user with no sessions sees an empty-state message instead of an empty list

Both:

- [ ] A visitor who is not logged in is sent to the login page from every goal and session page
- [ ] Deleting the account also removes the user's goals and sessions
- [ ] The models' migrations are committed, so `makemigrations --check` reports no changes

## Files and functions

Routing:

- `learning_companion/urls.py:24-26`: `path("", views.home, name="home")` (from `core.views`),
  `path("admin/", admin.site.urls)`, `path("", include("accounts.urls"))`. No namespaces.
- `accounts/urls.py:7-17`: `signup`, `login`, `logout`, `account_delete` under
  `accounts/`; `profile`, `profile_detail` (`profile/<int:pk>/`), `profile_edit`
  (`profile/edit/`). No `app_name`.
- `core/urls.py`: not found.

Views (all function-based):

- `core/views.py:7-9`: `home(request)`, `@login_required`, renders `core/home.html` with
  `{"profile": profile_for(request.user)}`.
- `accounts/views.py:10-16`: `signup`, the `Form(request.POST or None)` /
  `if request.method == "POST" and form.is_valid()` / `redirect(...)` / `render(...)` shape.
- `accounts/views.py:24-37`: `profile_detail(request, pk)`. A non-owner who isn't staff
  gets `PermissionDenied` (403) before any lookup, for any pk, existing or not (D31 in the
  ticket-3 plan); staff get 404 for a missing pk.
- `accounts/views.py:40-46`: `profile_edit`, `ProfileForm(request.POST or None,
  instance=profile_for(request.user))`, scoped to the user because the URL has no pk.
- `accounts/views.py:49-56`: `account_delete`. GET renders the confirmation page; POST logs
  out, calls `user.delete()`, redirects to `login`. No `require_http_methods`.
- No view uses `request.htmx`, `django.contrib.messages` or partial templates.

Forms:

- `accounts/forms.py:32-66`: `ProfileForm(forms.ModelForm)`, the only form with a Tag M2M
  (lines 37-41) and a custom `save(commit=True)` that calls `save_m2m()` (56-66).

Templates:

- `theme/templates/base.html`: loads `static tailwind_tags django_htmx` (1),
  `{% tailwind_css %}` (9), `{% htmx_script %}` (10); nav with a `home` brand link, and,
  when logged in, a `profile` link and a logout POST form (15-28); one block `content`
  (31). No goals link, no messages display, no `hx-headers` CSRF, hardcoded `<title>`.
- `accounts/templates/accounts/account_confirm_delete.html:4-12`: h1, warning, POST form
  with `{% csrf_token %}`, red submit, Cancel link.
- `accounts/templates/accounts/profile_form.html:6-10`: `{% csrf_token %}`,
  `{{ form.as_p }}`, black submit button; page wrapper `<section class="py-16 max-w-xl">`.
- `accounts/templates/accounts/profile_detail.html:16-20`: `{% for %}…{% empty %}`;
  22-27: owner-only links behind `{% if is_owner %}`.

Admin:

- `core/admin.py:5`: `admin.site.register(Tag)`.
- `accounts/admin.py:9-16`: `@admin.register(...)` with `list_display`.

## Current data shapes

`core/models.py:4-13`:

```python
class Tag(models.Model):
    """A focus area, maintained by admins; later tickets tag goals and resources too."""

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
```

Tags are global, with no owner. `core/migrations/0002_seed_tags.py:5-27` seeds 21 of them
(`STARTING_TAGS`: Python, JavaScript, … Agile & Scrum) with a `RunPython(create_tags,
delete_tags)` pair.

`accounts/models.py:21-29`, the closest model to copy:

```python
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    # Empty until the user completes the profile; then only an admin changes it (D9).
    cohort = models.ForeignKey(Cohort, on_delete=models.PROTECT, null=True, blank=True)
    focus_areas = models.ManyToManyField("core.Tag", blank=True)
```

`User` is a bare `AbstractUser` (`accounts/models.py:6-7`); a `post_save` signal creates
the Profile (`accounts/signals.py:7-12`).

Settings (`learning_companion/settings.py`): `AUTH_USER_MODEL = "accounts.User"` (54),
`LOGIN_URL = "login"` (58), `LOGIN_REDIRECT_URL = "home"` (59), `DATABASES` from
`DATABASE_URL` with a SQLite default (96-97), `TIME_ZONE = "UTC"` (125), `USE_TZ = True`
(129), `DEFAULT_AUTO_FIELD = BigAutoField` (140). `INSTALLED_APPS` ends with `core`,
`accounts` (38-49).

Not in the codebase yet: `TextChoices`, `auto_now` / `auto_now_add`, `DateField`,
`DurationField`, and a plain `ForeignKey` to the user.

## Tests

- Runner: pytest 9.1.1 + pytest-django 4.14.0; `pyproject.toml:6-8` sets
  `DJANGO_SETTINGS_MODULE = "learning_companion.settings_test"`, `testpaths = ["tests"]`.
  `settings_test.py` adds a test `SECRET_KEY`, `ENV_FILE=os.devnull` and the MD5 hasher.
- Commands: `make test`, `make test ARGS="-k <name>"`, `make lint` (`ruff check .`,
  default rules, `EXE002` ignored, `RUF012` ignored in migrations), `make format`. No type
  checker, no build step, no CI workflow. `/ship` runs `make test` and `make lint`.
- `tests/test_docs.py:20` checks that CLAUDE.md's Commands table matches the Makefile.
- Fixtures in `tests/conftest.py`: `password`, `user` (ada), `other_user` (grace),
  `staff_user`, `logged_in_client`; helper `signup_data(**overrides)`. No factories, no
  goal or session fixtures.
- DB access via a module-level `pytestmark = pytest.mark.django_db`
  (`tests/test_profile.py:8`).
- Typical patterns:
  - owner / other / staff access as one parametrized test (`tests/test_profile.py:79-92`);
  - another user's data absent from content (`tests/test_profile.py:126-142`);
  - invalid form: status 200, field in `response.context["form"].errors`, DB unchanged
    (`tests/test_signup.py:22-27`);
  - M2M post with `[t.pk for t in tags]` and a `values_list` set assertion
    (`tests/test_profile.py:194-214`);
  - delete confirmation then POST (`tests/test_account_delete.py:11-31`);
  - login required: `response.url == f"{reverse('login')}?next={url}"`
    (`tests/test_home.py:24-27`).
- AC numbers restart per ticket, and the same `test_ac<N>` prefix already appears in files
  from different tickets (`test_ac8` in `test_setup.py:4` and `test_login.py:65`), so
  `ARGS="-k test_ac8"` matches both.
- Gaps: no list views, no per-user queryset filtering test, no query-string filter test,
  no HTMX request (`HX-Request` header) anywhere.

## Patterns to follow

- Function-based views with `@login_required` (`accounts/views.py:19`, `core/views.py:7`).
- Form handling: `Form(request.POST or None, instance=...)`, then validate, save and
  `redirect(name)`, else `render` (`accounts/views.py:41-46`).
- Delete: GET shows a confirmation page, POST deletes and redirects
  (`accounts/views.py:49-56`, `account_confirm_delete.html:4-12`).
- URLs: flat names, no namespace, `<int:pk>/` and an `edit/` suffix
  (`accounts/urls.py:15-17`), app included at `""` (`learning_companion/urls.py:26`).
- User link: `settings.AUTH_USER_MODEL`, `on_delete=models.CASCADE`, explicit
  `related_name` (`accounts/models.py:22-24`).
- Tag M2M: `models.ManyToManyField("core.Tag", blank=True)` (`accounts/models.py:27`); in
  the form, `ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False,
  widget=forms.CheckboxSelectMultiple)` (`accounts/forms.py:37-41`).
- Models have `Meta.ordering` as a tuple and a `__str__` (`core/models.py:9-13`).
- Admin: `@admin.register(Model)` with `list_display` (`accounts/admin.py:9-11`).
- Templates at `<app>/templates/<app>/<name>.html`, extend `base.html`, fill
  `{% block content %}`, inline Tailwind classes; empty lists via `{% empty %}`.
- Code comments cite decision IDs (`accounts/models.py:25`).
- Tests: `test_ac<N>_<behaviour>`, one parametrized test per table of inputs, shared
  fixtures in `tests/conftest.py` next to `other_user`.
- Constraints from CLAUDE.md: stack fixed (raise changes as a question); tags are the
  `Tag` M2M model; CLAUDE.md names the goals ticket as the first user of HTMX; nothing is
  installed that the plan doesn't list.

## Open questions

1. When a user opens the edit or delete page of another user's goal or session, should they get 403 (as `profile_detail` does, D31) or 404?
2. What unit and input format does a session's duration use: whole minutes, hours and minutes, or something else? Is there an upper limit?
3. Can a session's date be in the future? Should the date default to today?
4. Are session tags chosen only from the admin-managed tag list, or can users create new tags?
5. Is there one sessions list for all of the user's sessions, or are sessions listed per goal (for example on a goal page)? If one list, can it be filtered by goal?
6. Can a session be moved to a different goal when it is edited?
7. What happens to a goal's sessions when the goal is deleted: are they deleted with it, or is deleting a goal that has sessions blocked? Does the confirmation page say how many sessions will go?
8. How does the status filter work for the user: links, a dropdown, or something else? Should it update the list in place with HTMX, or reload the page? Should the filter show in the URL so a reload or a shared link keeps it?
9. What should an unknown status value in the filter do: show all goals, show none, or show an error?
10. What status does a new goal start with, and is the description required?
11. In what order are goals and sessions listed (for example newest first, or by session date)? What does each list row show?
12. Besides the list, should a goal or session have its own detail page? The ticket names only list, create, edit and delete.
13. Which actions, if any, should use HTMX (for example inline delete or the filter)? CLAUDE.md names this ticket as HTMX's first user, but the ticket text doesn't ask for it.
14. Where do the goals and sessions pages link from: the nav, the home page, or both?
15. Should goals and sessions be registered in the Django admin?
16. Should a confirmation message appear after creating, editing or deleting? The messages framework is installed but nothing displays messages yet.
