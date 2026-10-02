# Resource library for attaching reference material to goals: refinement

## Context

A user attaches reference material to one of their goals. A resource has a URL, a title and a type (article, video, repo or doc) and belongs to a goal. Resources are added through a form on the goal's detail page, and the detail page lists them grouped or badged by type.

There is no goal detail page yet. Ticket #4 left it to this ticket (#4 D14), so this ticket adds it.

No feature branch yet; the current branch is `docs/10-model-check`.

Source: #5 (https://github.com/GPlastok/learning-companion/issues/5). The ticket has no acceptance criteria of its own, so all criteria below were written by refinement.

## Progress

Refinement done on 2026-10-02. Nothing planned or built yet. Next: the user answers the open questions, then a plan is written.

Plan written on 2026-10-02: plans/feature-resource-library-for-attaching-reference-material-to-goals-plan.md.

Built on 2026-10-02, see plans/feature-resource-library-for-attaching-reference-material-to-goals-plan.md.

## Acceptance criteria

- [ ] A logged-in user can open a detail page for each of their own goals. It shows the goal's title.
- [ ] From the goals list, the user can reach each goal's detail page.
- [ ] Opening the detail page of another user's goal, or of a goal id that doesn't exist, gives 404.
- [ ] A visitor who isn't logged in and opens a goal detail page is sent to the login page, and comes back to the detail page after logging in.
- [ ] The goal detail page has a form for attaching a resource, with fields for URL, title and type.
- [ ] The type offers exactly four choices: article, video, repo and doc.
- [ ] Submitting the form with a valid URL, title and type stores one resource linked to that goal. After the submit, the resource appears on the goal's detail page.
- [ ] Each resource on the detail page shows its title, links to its URL, and shows its type.
- [ ] A URL that isn't a valid web address is rejected with an error on the form, and nothing is stored.
- [ ] A missing URL is rejected with an error on the form, and nothing is stored.
- [ ] A type outside the four choices is rejected with an error on the form, and nothing is stored.
- [ ] A rejected submission keeps the values the user entered.
- [ ] Posting a resource to another user's goal, or to a goal id that doesn't exist, gives 404 and stores nothing.
- [ ] After a successful attach, reloading the page doesn't attach the resource a second time.
- [ ] A confirmation message shows after a resource is attached.
- [ ] A goal's detail page shows only that goal's resources, never another goal's.
- [ ] A goal with no resources shows an empty-state message where the resources would be.
- [ ] Deleting a goal deletes its resources. Deleting an account deletes the resources of its goals and leaves other users' resources alone.
- [ ] Staff can see and manage resources in the admin.
- [ ] The migration for the new model is committed (`makemigrations --check` finds nothing).

## Files and functions

**Routes**

- `learning_companion/urls.py:37-42`: `""` → `core.views.home` (`home`), `admin/`, then `include("accounts.urls")` and `include("learning.urls")` at `""`.
- `learning/urls.py:5-14`: flat names, no `app_name`. `goals/`, `goals/new/`, `goals/<int:pk>/edit/`, `goals/<int:pk>/delete/`, and the same four for `sessions/`. No `goals/<int:pk>/`.

**Views** (`learning/views.py`)

- `_deleted_response(request, list_name)` (13-18): for HTMX, renders `messages.html` with `oob=True`; otherwise redirects to the list.
- `goal_list` (21-51): `@login_required`, `@vary_on_headers("HX-Request")`. Annotates `session_count` and `total_minutes`, applies `?order=` and `?status=`, and returns the partial `_goal_list.html` for an HTMX request that isn't a history restore (D33), otherwise the full page.
- `goal_create` (54-62), `goal_edit` (65-74): `Form(request.POST or None, ...)`, save, `messages.success`, `redirect("goal_list")`, else render `goal_form.html`.
- `goal_delete` (77-84): `@login_required` above `@require_POST`, `get_object_or_404(Goal, pk=pk, user=request.user)`.
- `session_list`, `session_create`, `session_edit`, `session_delete` (87-139): the same shapes, with ownership through `goal__user=request.user`.

**Forms** (`learning/forms.py`)

- `GoalForm` (8-11): `ModelForm`, fields `title`, `description`, `status`.
- `SessionForm` (14-66): takes `user=` as a keyword argument and limits `goal` to that user's goals. Has `clean_date`, `clean`, and a `save` that sets `duration_minutes` and calls `save_m2m()`.

**Templates**

- `theme/templates/base.html`: loads `django_htmx`, `{% htmx_script %}` (line 10), the nav with Goals and Profile for logged-in users (15-29), `{% include "messages.html" %}` (32).
- `theme/templates/messages.html:1-5`: `<div id="messages">`, with `hx-swap-oob="true"` when `oob` is set.
- `learning/templates/learning/goal_list.html`: links to `goal_create` and `session_list`, wraps the partial in `id="goal-list"`.
- `learning/templates/learning/_goal_list.html:20-35`: one `<li id="goal-<pk>">` per goal. The title (line 22) is a plain `<span>` and links nowhere. Then the status badge, session count, total time, updated date, an Edit link and the HTMX Delete form.
- `learning/templates/learning/goal_form.html`: `{{ form.as_p }}` inside a POST form, with a "Back to goals" link.
- `accounts/templates/accounts/profile_detail.html`: the one detail page in the repo. A `<dl>` grid (6-13), a badge list of tags as `<li class="px-2 py-1 border rounded">` with an `{% empty %}` line (15-21), and owner-only links (22-27).

**Other**

- `learning/templatetags/learning_extras.py`: the `duration` filter.
- `learning/admin.py`: `GoalAdmin` and `LearningSessionAdmin` with `list_display`.
- `accounts/views.py:24-37`: `profile_detail`, which gives 403 for someone else's profile (ticket-3 D31). The learning app uses 404 instead (#4 D1).

## Current data shapes

`learning/models.py:5-26`:

```python
class Goal(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in-progress", "In progress"
        DONE = "done", "Done"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
```

`learning/models.py:29-42`:

```python
class LearningSession(models.Model):
    # No user field: the owner is the goal's user (D18).
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="sessions")
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField("core.Tag", blank=True)

    class Meta:
        ordering = ("-date", "-pk")
```

`core/models.py:4-13`: `Tag(name=CharField(max_length=50, unique=True))`, ordered by name. Its docstring says "later tickets tag goals and resources too". 21 tags are seeded in `core/migrations/0002_seed_tags.py`.

Migrations: `learning/migrations/0001_initial.py` only. No `URLField` anywhere in the repo, and no "resource" model, form or template.

Storage: SQLite at `db.sqlite3` by default, PostgreSQL later through `DATABASE_URL` (`learning_companion/settings.py:97-99`). `TIME_ZONE = "Europe/Berlin"`.

## Tests

- Runner: pytest with pytest-django, `DJANGO_SETTINGS_MODULE = "learning_companion.settings_test"`, `testpaths = ["tests"]` (`pyproject.toml:6-8`). The test settings use MD5 hashing and skip `.env`.
- Commands: `make test`, `make test ARGS="-k test_ac3"`, `make lint` (`ruff check .`), `make format`. No type-check or build target. The suite has 145 passing tests.
- Files live flat in `tests/`. The learning ones: `test_goals.py`, `test_sessions.py`, `test_learning_data.py` (cascade, `makemigrations --check`), `test_learning_messages.py`, `test_learning_extras.py`, `test_admin.py`. `test_docs.py` checks that CLAUDE.md's command table matches the Makefile.
- Fixtures in `tests/conftest.py`: `password`, `user` (ada), `other_user` (grace), `goal` ("Learn Django"), `other_goal` ("Learn Rust"), `session`, `other_session`, `staff_user`, `logged_in_client`. Plain helpers return form data: `signup_data`, `goal_data`, `session_data(goal, **overrides)`.
- Typical view test: post with `logged_in_client`, assert 302 and `response.url == reverse(...)`, check the stored row, then GET the page and check `content.decode()`. An invalid post asserts 200, the field name in `response.context["form"].errors`, and an unchanged count (`tests/test_goals.py`, ac1 and ac2).
- Ownership: `test_ac8_other_users_goal_is_404` parametrizes `target` (`other`, `missing`) against `(method, name)` pairs.
- Login: `test_ac22_pages_require_login` (`tests/test_goals.py:317-337`) parametrizes every learning route and asserts the redirect to `login?next=<url>`.
- HTMX: requests send `headers={"HX-Request": "true"}`, and tests check `[t.name for t in response.templates]` and attributes found with `re.search` in the HTML (ac28, ac38).
- Admin: `test_ac41_learning_models_registered_in_admin` parametrizes `[Goal, LearningSession]` (`tests/test_admin.py`).
- Gaps: nothing covers a goal detail page, URL validation or resources.

## Patterns to follow

- Resources belong in the `learning` app: "`learning`: goals, sessions and resources" (ticket-3 D1).
- Ownership comes through the goal, as for sessions: no user field of its own, queries filter on `goal__user` (#4 D18, `learning/models.py:30`).
- Another user's record, or a missing id, is 404 via `get_object_or_404(..., user=request.user)` (#4 D1, `learning/views.py:68`).
- Child records cascade with their goal (#4 D22, `learning/models.py:31`).
- Choice fields use a nested `models.TextChoices` with lowercase values and readable labels (#4 D23, `learning/models.py:6-9`).
- Learning models are registered in the admin with a `list_display` (#4 D16, ticket-3 D18, `learning/admin.py:6-13`).
- Function-based views with `@login_required`; deletes add `@require_POST` below it (#4 D26, `learning/views.py:77-79`).
- Form handling: `Form(request.POST or None, ...)`, validate, save, `messages.success`, `redirect`, else render (`learning/views.py:54-62`).
- Each change is confirmed with a short message such as "Goal created." (#4 D17, `learning/views.py:60`).
- Routes are added to `learning/urls.py` with flat names (#4 D20).
- HTMX responses: partial templates start with `_`, the view returns the partial for `request.htmx` and not a history restore, and uses `@vary_on_headers("HX-Request")` (#4 D10, D33, `learning/views.py:21-51`).
- Deletes ask in the browser's `hx-confirm` popup with no confirmation page (#4 D9, `_goal_list.html:28-34`). Ticket #19 ("Nicer delete confirmation") is open for a styled version.
- Badge styling for a list of labels: `<li class="px-2 py-1 border rounded">` with an `{% empty %}` line (`accounts/templates/accounts/profile_detail.html:15-21`).
- Tags come from the admin-maintained `core.Tag` list; users can't create them (#4 D5, ticket-3 D9).
- Tests: `test_ac<n>_...` names, `@pytest.mark.parametrize` for tables, new fixtures in `tests/conftest.py`, every criterion automated with manual checks offered at the end (#4 D30, D31).

## Open questions

1. What does the goal detail page show besides the resources: the description, status, session count, total time, the goal's sessions, Edit and Delete?
2. How does the goals list lead to the detail page: the title as a link, a separate "View" link, or both? And do the goal form's save and the sessions list's goal title lead there too?
3. What URL does the detail page have: `goals/<int:pk>/`, named `goal_detail`?
4. "Grouped or badged by type": should resources be listed in one list with a type badge each, or in one section per type? If grouped, in what order are the types, and are empty groups hidden?
5. In what order are resources listed: newest first, oldest first, or by title?
6. Is the title required, or optional with the URL shown when it's empty? What is its maximum length?
7. Which URLs are accepted: only `http` and `https`, or anything Django's `URLField` accepts? Is there a maximum length beyond `URLField`'s default of 200?
8. Can the same URL be attached twice to one goal?
9. Does the type have a default in the form, or must the user pick one?
10. Is the attach form part of the detail page itself, or a separate page linked from it? Does submitting it use HTMX to add the resource in place, or a normal post and redirect back to the detail page?
11. Can a user edit or delete a resource after attaching it? The ticket only mentions attaching.
12. Do resources take tags from `core.Tag`? The `Tag` docstring expects it in a later ticket, and the ticket doesn't mention it.
13. Should resource links open in a new tab?
14. What does the confirmation message say ("Resource added."?), and what does the empty state say ("No resources yet."?)?
15. Should the goals list show a resource count per goal, and should the goal delete popup mention resources ("and its 2 sessions and 3 resources?")?
