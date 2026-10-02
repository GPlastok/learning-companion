# CRUD for goals and learning sessions: TDD plan

## Context

This ticket adds the core domain in a new `learning` app. A Goal has a title, a description, a status (planned, in progress or done) and timestamps. A LearningSession belongs to a Goal and has a date, a duration, notes and tags.

Each has a list page, a create form, an edit form and a delete button. Users only see their own records. Users can filter the goals list by status and sort it, and filter the sessions list by goal. Both filters swap the list in place with HTMX.

Refinement: [feature-crud-for-goals-and-learning-sessions-refinement.md](feature-crud-for-goals-and-learning-sessions-refinement.md). Source: #4.

Branch: `feature/4-crud-for-goals-and-learning-sessions`.

**In scope:**

- the `learning` app with `Goal` and `LearningSession`, their migration and admin;
- list, create, edit and delete for both;
- the status filter and the order toggle on goals, and the goal filter on sessions;
- messages after each change;
- the Goals nav link and links on home.

**Not in scope:**

- a goal detail page, which #5 adds (D14);
- the dashboard and its totals (#7);
- a styled modal in place of the browser's confirm popup (D9).

## Progress

Plan written on 2026-10-02. Nothing built yet. The suite has 64 passing tests before the build.

Step 0 done: 64 passed, 64 before the build.
Step 1 done: 68 passed, 64 before the build.
Step 2 done: 74 passed, 64 before the build.
Step 3 done: 76 passed, 64 before the build.
Step 4 done: 85 passed, 64 before the build.
Step 5 done: 91 passed, 64 before the build.
Step 6 done: 97 passed, 64 before the build.
Step 7 done: 99 passed, 64 before the build.
Step 8 done: 107 passed, 64 before the build.
Step 9 done: 114 passed, 64 before the build.
Step 10 done: 120 passed, 64 before the build.
Step 11 done: 121 passed, 64 before the build.
Step 12 done: 122 passed, 64 before the build.
Step 13 done: 130 passed, 64 before the build.
Step 14 done: 139 passed, 64 before the build.
Deviations: AC27 and AC30 went red on their assertions or a missing form context, not on NoReverseMatch (see build log). Step 9 sets up its goals in a local `three_goals` fixture. The date widget is set in `SessionForm.__init__`, not `Meta.widgets`, because ruff's RUF012 flags a mutable class attribute. `make format` also wants to reformat code blocks in 6 `guides/*.md` files; that predates this build and was left alone.

Review round 1 on 2026-10-02: 4 rework steps added (15, 16, 17, 18).

Step 15 done: 139 passed, 64 before the build.
Step 16 done: 139 passed, 64 before the build.
Step 17 done: 141 passed, 64 before the build.
Step 18 done: 145 passed, 64 before the build.
Review round 2 on 2026-10-02: 1 rework step added (19). The user chose no third review after it.
Step 19 done: 145 passed, 64 before the build.
Reviewed on 2026-10-02, round 2: rework step 19 built and verified; no third review, by the user's choice.

Manual check on 2026-10-02 found M1 (the order toggle): 1 rework step added (20).
Step 20 done: 145 passed, 64 before the build.
Built on 2026-10-02, M1 fix included. The user found M1 in the manual checks; the other checks passed.

## Decisions

The user first answered the questions on 2026-10-01, in a session that ended before anyone wrote the plan. They were asked again on 2026-10-02. Where the two answers differ, the 2026-10-02 answer wins.

### Access and ownership

D1. (Q1) A user who opens the edit or delete URL of another user's goal or session gets 404, whether the record exists or not.

- The view looks the record up only among the user's own: `get_object_or_404(Goal, pk=pk, user=request.user)`, or `goal__user=request.user` for a session.
- Staff get no special access in the app; they use `/admin/`.
- This differs from `profile_detail`'s 403 (ticket-3 D31), and like D31 it doesn't reveal which ids exist.

Source: user, 2026-10-02 (403 on 2026-10-01, changed after the conflict was shown).

D18. (Q17) A session has no user field of its own. Its owner is its goal's user, and every session query filters on `goal__user`. Source: user, 2026-10-02.

D22. Account deletion removes goals and sessions through `on_delete=CASCADE`: `Goal.user` cascades to goals, and `LearningSession.goal` cascades to sessions. Source: plan, following `Profile.user` (`accounts/models.py:22-24`).

### Fields

D2. (Q2) The form takes the duration as two fields, hours and minutes. The model stores one whole number, `duration_minutes`.

- Hours: 0 or more, no upper limit.
- Minutes: 0 to 59.
- The total must be above zero.

Source: user, 2026-10-01; confirmed 2026-10-02.

D3. (Q3) A session records learning that has already started, not a scheduled one. Its date is today or earlier, and the form starts with today's date (`timezone.localdate()`). Source: user, 2026-10-01 and 2026-10-02.

D4. (Q3) `TIME_ZONE = "Europe/Berlin"` in `learning_companion/settings.py`, so "today" after midnight in Berlin isn't still yesterday in UTC. Source: user, 2026-10-02.

D5. (Q4) Session tags come from the admin-maintained `core.Tag` list; users can't create tags. Source: ticket-3 D9.

D12. (Q10) A new goal starts as planned, and the description is optional. Source: user, 2026-10-01; confirmed 2026-10-02.

D19. (Q18) A goal title is at most 200 characters. Session notes are optional. Source: user, 2026-10-02.

D23. Status values follow the ticket: `planned`, `in-progress`, `done`, shown as "Planned", "In progress" and "Done". They live in `Goal.Status(models.TextChoices)`. Source: plan, ticket text.

### Pages and behaviour

D6. (Q5) There is one sessions list at `sessions/` with every session of the user, filterable by goal.

- The filter is a dropdown ("All goals" and the user's goals) with a "Filter" button, sent as `?goal=<pk>`.
- With HTMX, changing the dropdown swaps only the list and updates the URL.
- The view ignores a `goal` value that isn't one of the user's goals and shows all their sessions (like D11).

Source: user, 2026-10-01 (list and filter); dropdown: user "ok", 2026-10-02; unknown value: plan, following D11.

D7. (Q6) Editing a session can move it to another of the user's goals. Source: user, 2026-10-01 and 2026-10-02.

D8. (Q7) Deleting a goal deletes its sessions too. The delete popup names how many: `Delete “Learn Django” and its 2 sessions?`. Source: user, 2026-10-01 and 2026-10-02.

D9. (Q7, Q13) Deleting asks first in the browser's confirm popup, with no confirmation page.

- The Delete button is a POST form with `hx-post`, `hx-confirm`, `hx-target="closest li"` and `hx-swap="outerHTML"`.
- An HTMX delete returns 200 without the row, so the row disappears in place.
- A delete without HTMX redirects to the list.
- The delete views take POST only (`require_POST`), so a GET deletes nothing.
- Without JavaScript the form posts with no popup. That's accepted.
- After an HTMX delete of the last row, the empty-state message only appears on the next page load. That's accepted.

The popup is the "confirmation step" in AC6 and AC18. Tests check that the button carries `hx-confirm`; the popup itself is a manual check. Source: user, 2026-10-02 ("not a page, a popup or notification"); popup mechanism, no-JS and empty-state limits: plan, accepted by the user ("ok"), 2026-10-02.

D10. (Q8) The status filter is four links: All, Planned, In progress and Done. Each is a normal URL (`?status=planned`) with `hx-get`, `hx-target="#goal-list"` and `hx-push-url="true"`.

- An HTMX request (`request.htmx`, from django-htmx) gets only the partial `learning/_goal_list.html`.
- A normal request gets the full page, which includes the same partial.
- The links are built with Django's `{% querystring %}` tag, so status and order combine.

Source: user, 2026-10-01 (HTMX, URL) and 2026-10-02 (links).

D11. (Q9) The view ignores an unknown status such as `?status=foo` and shows all the user's goals. Source: user, 2026-10-02 (replaces "show none or error" from 2026-10-01).

D13. (Q11) Order and row contents, the 2026-10-01 version:

- Goals are newest first by `created_at`. `?order=oldest` lists oldest first and combines with the status filter. Any other `order` value means newest first.
- A goal row shows the title, the status label, the number of sessions ("2 sessions"), the total time, the last updated date, an Edit link and a Delete button.
- Sessions are newest first by date, then by newest pk.
- A session row shows the date, the goal's title, the duration, the tags, the first line of the notes, an Edit link and a Delete button.

Source: user, 2026-10-02 ("yesterday's version").

D24. Times show as `1 h 30 min`. Whole hours show as `2 h`, under an hour as `45 min`, and zero as `0 min` (a goal with no sessions). A template filter `duration` in `learning/templatetags/learning_extras.py` formats both lists. Source: plan, the format from D13; edge cases accepted by the user ("ok"), 2026-10-02.

D14. (Q12) No detail pages in this ticket. #5 needs a goal detail page and adds it there. Source: user, 2026-10-02 ("the simplest, if it can change later").

D15. (Q14) Links:

- The nav gets a "Goals" link for logged-in users, before "Profile".
- Home replaces "Nothing here yet." with links to the goals list and the sessions list.
- The goals list links to the sessions list. Sessions get no nav link.

Source: user, 2026-10-01.

D16. (Q15) `Goal` and `LearningSession` are registered in the admin. Source: ticket-3 D18.

D17. (Q16) A message confirms each change: "Goal created.", "Goal updated.", "Goal deleted.", "Session created.", "Session updated.", "Session deleted."

- `theme/templates/messages.html` renders `<div id="messages">` with the messages; `base.html` includes it above the content.
- An HTMX delete response renders the same partial with `hx-swap-oob="true"`, so the message appears without a reload.

Source: user, 2026-10-01 and 2026-10-02; mechanism: plan.

D20. (Q19) Routes live in a new `learning/urls.py`, included at `""` in `learning_companion/urls.py`, with flat names and no `app_name`:

| Path | Name |
|---|---|
| `goals/` | `goal_list` |
| `goals/new/` | `goal_create` |
| `goals/<int:pk>/edit/` | `goal_edit` |
| `goals/<int:pk>/delete/` | `goal_delete` |
| `sessions/` | `session_list` |
| `sessions/new/` | `session_create` |
| `sessions/<int:pk>/edit/` | `session_edit` |
| `sessions/<int:pk>/delete/` | `session_delete` |

Source: user, 2026-10-02.

D21. (Q20) A user with no goals who opens the new-session page sees "Create a goal first" with a link to `goal_create`, and no form. Source: user, 2026-10-02.

### Code layout and tests

D25. The `learning` app comes from `manage.py startapp learning`, tidied like ticket-3 D28: unused imports removed, `learning/tests.py` deleted. It goes in `INSTALLED_APPS` after `"accounts"`. Source: ticket-3 D1, D28.

D26. Views are function-based with `@login_required`, like `accounts/views.py`. The delete views put `@login_required` above `@require_POST`, so an anonymous visitor goes to login before the method check. Source: plan, refinement Patterns.

D27. Forms live in `learning/forms.py`:

- `GoalForm(forms.ModelForm)`: `title`, `description`, `status`.
- `SessionForm(forms.ModelForm)`: `goal`, `date`, `notes`, `tags` from the model, plus `hours` and `minutes` as `forms.IntegerField`s. It takes the user as a keyword argument (`SessionForm(data, user=request.user)`) and limits `goal` to that user's goals. `save()` sets `duration_minutes`, then saves and calls `save_m2m()`, like `ProfileForm.save` (`accounts/forms.py:56-66`).

Source: plan.

D28. Tests check HTMX responses without a browser: the request sends `headers={"HX-Request": "true"}`, and the test checks which templates rendered. The popup, the in-place swap and the address bar are manual checks (Verification). Source: plan, refinement Tests ("no HTMX request anywhere").

D29. Timestamps are tested without a new tool. The test moves `created_at` and `updated_at` into the past with `Goal.objects.filter(...).update(...)`, which bypasses `auto_now`, then edits the goal through the view. Source: plan; no freezegun in `requirements-dev.txt`.

D30. Automated tests cover every criterion. When the build is done, it asks the user whether they want to do the manual checks in Verification. Source: ticket-3 D20.

D31. New fixtures go in `tests/conftest.py`, next to `other_user`:

- `goal(user)`: ada's "Learn Django", description "Models and views", planned.
- `other_goal(other_user)`: grace's "Learn Rust", planned.
- `session(goal)`: `date(2026, 9, 30)`, 90 minutes, notes `"Read the ORM docs\nThen tried annotate"`, no tags.
- `other_session(other_goal)`: `date(2026, 9, 29)`, 45 minutes, notes "Borrow checker".
- `goal_data(**overrides)`: a plain function returning `{"title": "Learn Docker", "description": "", "status": "planned"}`.
- `session_data(goal, **overrides)`: a plain function returning `{"goal": goal.pk, "date": "2026-09-30", "hours": 1, "minutes": 30, "notes": "Wrote tests"}`.

Source: plan, following D26 of ticket 3.

### During review

D32. (Q21, R3) D2 had no upper limit on hours, so a huge value overflowed the column and gave a 500. Answer: one session is at most 24 hours. `hours` is 0 to 24, and a total above 1440 minutes is a form error, "A session can't be longer than 24 hours." This replaces D2's "no upper limit". Source: user, 2026-10-02, during review.

D33. (R2) The filters push their URLs into the browser history. A back or forward navigation that misses htmx's history cache sends `HX-Request` together with `HX-History-Restore-Request`, and the list views answered with only the partial. Answer: a history-restore request gets the full page, and both list views send `Vary: HX-Request` so a cached partial never stands in for the page. This adds to D10 and D6. Source: user, 2026-10-02, during review.

## Acceptance criteria

Goals:

- [x] AC1. A logged-in user can create a goal with a title, a description and a status, and it then appears in their goals list → step 2
- [x] AC2. A goal's status can only be planned, in-progress or done; any other value shows a form error and saves nothing → step 2
- [x] AC3. Submitting the goal form without a title shows an error on the form and saves nothing → step 2
- [x] AC4. A goal stores when it was created and when it was last updated; editing it changes the updated time and leaves the created time as it was → step 3
- [x] AC5. A user can edit their goal, and the list shows the new values afterwards → step 3
- [x] AC6. A user can delete their goal after a confirmation step, and it no longer appears in the list → step 4
- [x] AC7. The goals list shows only the logged-in user's goals, never another user's → step 2
- [x] AC8. Opening the edit or delete page of another user's goal neither shows nor changes that goal → step 4
- [x] AC9. Filtering the goals list by a status shows only the user's goals with that status → step 9
- [x] AC10. The goals list without a filter shows all of the user's goals → step 9
- [x] AC11. A user with no goals, or a filter with no matching goals, sees an empty-state message instead of an empty list → step 9

Learning sessions:

- [x] AC12. A logged-in user can create a learning session for one of their goals with a date, a duration, notes and tags, and it then appears in their sessions list → step 5
- [x] AC13. The session form offers only the user's own goals; submitting another user's goal saves nothing and shows an error → step 5
- [x] AC14. Tags on a session are chosen from the existing tags, and the chosen tags are shown with the session → step 5
- [x] AC15. A session with no tags saves without errors → step 5
- [x] AC16. Submitting the session form without a date, without a duration or with a duration of zero or less shows an error and saves nothing → step 6
- [x] AC17. A user can edit their session, and the list shows the new values afterwards → step 7
- [x] AC18. A user can delete their session after a confirmation step, and it no longer appears in the list → step 8
- [x] AC19. The sessions list shows only the logged-in user's sessions, never another user's → step 5
- [x] AC20. Opening the edit or delete page of another user's session neither shows nor changes that session → step 8
- [x] AC21. A user with no sessions sees an empty-state message instead of an empty list → step 10

Both:

- [x] AC22. A visitor who is not logged in is sent to the login page from every goal and session page → step 14
- [x] AC23. Deleting the account also removes the user's goals and sessions → step 1
- [x] AC24. The models' migrations are committed, so `makemigrations --check` reports no changes → step 1

Added by the decisions:

- [x] AC25. A new goal's form starts with the status planned, and a goal saves without a description (from D12) → step 2
- [x] AC26. A goal title longer than 200 characters shows an error and saves nothing (from D19) → step 2
- [x] AC27. Deleting a goal deletes its sessions too, and the delete popup names how many sessions go (from D8) → step 4
- [x] AC28. Deleting a goal through HTMX removes its row in place; without HTMX the delete leads back to the goals list (from D9) → step 19
- [x] AC29. Deleting a session through HTMX removes its row in place; without HTMX the delete leads back to the sessions list (from D9) → step 19
- [x] AC30. The duration is entered as hours and minutes, minutes must be 0 to 59, and 1 h 30 min is stored as 90 minutes (from D2) → step 6
- [x] AC31. A session's date can't be in the future, and the form starts with today's date in Berlin time (from D3, D4) → step 6
- [x] AC32. Editing a session can move it to another of the user's goals (from D7) → step 7
- [x] AC33. The sessions list can be filtered by one of the user's goals, in place with HTMX; a goal value that isn't one of theirs shows all their sessions (from D6) → step 19
- [x] AC34. A user with no goals sees "Create a goal first" with a link to the goal form on the new-session page, and no form (from D21) → step 5
- [x] AC35. The goals list is newest first, `?order=oldest` lists oldest first and combines with the status filter, and each row shows the title, status, number of sessions, total time and last updated date (from D13, D24) → step 20
- [x] AC36. The sessions list is newest first by date, and each row shows the date, the goal's title, the duration as "1 h 30 min", the tags and the first line of the notes (from D13, D24) → step 10
- [x] AC37. An unknown status in the filter shows all of the user's goals (from D11) → step 9
- [x] AC38. The status filter links update the goals list in place: an HTMX request gets only the list, and the links carry the filter in the URL (from D10) → step 9
- [x] AC39. A message confirms each create, edit and delete of a goal or session, also after an HTMX delete (from D17) → step 13
- [x] AC40. Logged-in users see a Goals link in the nav, home links to the goals and sessions lists, and the goals list links to the sessions list (from D15) → step 14
- [x] AC41. Goal and LearningSession are registered in the admin (from D16) → step 1
- [x] AC42. A session longer than 24 hours shows a form error and saves nothing (from D32) → step 18
- [x] AC43. Going back or forward to a filtered goals or sessions list shows the full page: a history-restore request gets the full page, and both lists send `Vary: HX-Request` (from D33) → step 17

## Step 0: groundwork

No tests of its own. The 64 existing tests have to stay green.

**The app.** Run `.venv/bin/python manage.py startapp learning` and tidy it per D25. Add `"learning"` to `INSTALLED_APPS` in `learning_companion/settings.py`, after `"accounts"`.

**The models.** In `learning/models.py`:

- `Goal`: `user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals")`, `title = CharField(max_length=200)`, `description = TextField(blank=True)`, `status = CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)` with the inner `Status(models.TextChoices)` from D23, `created_at = DateTimeField(auto_now_add=True)`, `updated_at = DateTimeField(auto_now=True)`. `Meta.ordering = ("-created_at",)`. `__str__` returns the title.
- `LearningSession`: `goal = ForeignKey(Goal, on_delete=models.CASCADE, related_name="sessions")`, `date = DateField()`, `duration_minutes = PositiveIntegerField()`, `notes = TextField(blank=True)`, `tags = ManyToManyField("core.Tag", blank=True)`. `Meta.ordering = ("-date", "-pk")`. `__str__` returns `f"{self.goal.title} on {self.date}"`.

Comments cite D18 (no user field on the session) and D2 (minutes).

**The migration.** `.venv/bin/python manage.py makemigrations learning` creates `learning/migrations/0001_initial.py`.

**The URLs.** Create `learning/urls.py` with `urlpatterns = []`. Add `path("", include("learning.urls"))` to `learning_companion/urls.py`, after the accounts include. Later steps add the D20 routes.

**The duration filter stub.** Create `learning/templatetags/__init__.py` and `learning/templatetags/learning_extras.py` with `register = template.Library()` and `@register.filter def duration(minutes)` that raises `NotImplementedError`. Step 10 fills it in, and its test then fails on the stub, not on an import.

**Fixtures.** Add the D31 fixtures and helpers to `tests/conftest.py`.

**The local database.** Run `make migrate`. If it stops on a missing `SECRET_KEY`, ask the user to run it.

**Check.**

- `make test` passes the 64 existing tests.
- `make lint` is clean.
- `.venv/bin/python manage.py makemigrations --check --dry-run` reports no changes.

## Step 1: AC23, AC24, AC41, data layer and admin

**Test.** New file `tests/test_learning_data.py`, with `pytestmark = pytest.mark.django_db`:

- `test_ac23_account_delete_removes_goals_and_sessions(logged_in_client, user, goal, session, other_session)`: POST `reverse("account_delete")`. Assert no `Goal` with `user__pk=user.pk` and no `LearningSession` with `goal__user__pk=user.pk` remain, and that `other_session` still exists.
- `test_ac24_migrations_are_committed()`: `call_command("makemigrations", "--check", "--dry-run")` from `django.core.management` returns without raising `SystemExit`.

In `tests/test_admin.py`:

- `test_ac41_learning_models_registered_in_admin(model)`, parametrized over `Goal` and `LearningSession`: assert `admin.site.is_registered(model)`.

**Red.** The AC41 rows fail on the assertion: `is_registered` returns `False`.

The AC23 and AC24 tests pass on their first run, because step 0 created the cascading models and their migration. The build log records them as green from the start. They pin the behaviour against later changes.

**Green.** `learning/admin.py`:

- `@admin.register(Goal)` with `list_display = ("title", "user", "status", "updated_at")`;
- `@admin.register(LearningSession)` with `list_display = ("goal", "date", "duration_minutes")`.

**Refactor.** None.

## Step 2: AC1, AC2, AC3, AC7, AC25, AC26, goal list and create

**Test.** New file `tests/test_goals.py`, with `pytestmark = pytest.mark.django_db`:

- `test_ac1_create_goal_appears_in_list(logged_in_client, user)`: POST `reverse("goal_create")` with `goal_data(title="Learn Docker", description="Images and volumes", status="in-progress")`. Assert a 302 to `reverse("goal_list")` and one `Goal` for `user` with those three values. GET the list and assert "Learn Docker" is in the content, along with a link to `reverse("goal_create")`.
- `test_ac2_invalid_status_is_rejected(logged_in_client)`: POST `goal_data(status="archived")`. Assert 200, `"status"` in `response.context["form"].errors`, and `Goal.objects.count() == 0`.
- `test_ac3_title_is_required(logged_in_client)`: POST `goal_data(title="")`. Assert 200, `"title"` in the form errors, and no goal.
- `test_ac26_title_longer_than_200_is_rejected(logged_in_client)`: POST `goal_data(title="x" * 201)`. Assert 200, `"title"` in the form errors, and no goal.
- `test_ac7_list_shows_only_own_goals(logged_in_client, goal, other_goal)`: GET the list. Assert "Learn Django" is present and "Learn Rust" is not.
- `test_ac25_new_goal_starts_planned_without_description(logged_in_client, user)`: GET `goal_create` and assert `response.context["form"]["status"].value() == "planned"`. POST `goal_data()` (empty description) and assert a goal with `description == ""` exists.

**Red.** `reverse("goal_create")` and `reverse("goal_list")` raise `NoReverseMatch`.

**Green.**

- `learning/forms.py`: `GoalForm` (D27).
- `learning/views.py`:
  - `goal_list(request)`: `@login_required`, renders `learning/goal_list.html` with `goals = Goal.objects.filter(user=request.user)`;
  - `goal_create(request)`: `@login_required`, `GoalForm(request.POST or None)`. On a valid POST it sets `form.instance.user = request.user`, saves and redirects to `goal_list`. Otherwise it renders `learning/goal_form.html`.
- `learning/urls.py`: the two routes from D20.
- Templates in `learning/templates/learning/`:
  - `goal_list.html`: an h1 "Goals", a "New goal" link, and a `<ul>` with one `<li id="goal-{{ goal.pk }}">` per goal showing its title;
  - `goal_form.html`: like `accounts/profile_form.html`, with `{% csrf_token %}`, `{{ form.as_p }}`, a Save button and a "Back to goals" link.

**Refactor.** None.

## Step 3: AC4, AC5, goal edit

**Test.** In `tests/test_goals.py`:

- `test_ac4_edit_changes_updated_but_not_created(logged_in_client, goal)`: set `past = timezone.now() - timedelta(days=3)` and run `Goal.objects.filter(pk=goal.pk).update(created_at=past, updated_at=past)` (D29). POST `reverse("goal_edit", args=[goal.pk])` with `goal_data(title="Learn Django well")`. Refresh the goal. Assert `goal.created_at == past` and `goal.updated_at > past`.
- `test_ac5_edit_goal_shows_new_values(logged_in_client, goal)`: GET the edit page and assert the form's `title` value is "Learn Django". POST `goal_data(title="Master Django", status="done")`. Assert a 302 to `goal_list`, and that the list shows "Master Django" and no longer shows "Learn Django".

**Red.** `reverse("goal_edit", ...)` raises `NoReverseMatch`.

**Green.**

- `learning/views.py`, `goal_edit(request, pk)`: `@login_required`, `goal = get_object_or_404(Goal, pk=pk, user=request.user)` (D1), `GoalForm(request.POST or None, instance=goal)`. A valid POST saves and redirects to `goal_list`; otherwise it renders `learning/goal_form.html`.
- The route `goal_edit`.
- `goal_list.html`: each row gets an "Edit" link to `goal_edit`.

**Refactor.** None.

## Step 4: AC6, AC8, AC27, AC28, goal delete

**Test.** In `tests/test_goals.py`:

- `test_ac6_delete_goal_after_confirmation(logged_in_client, goal)`:
  - GET the list. Assert the row has a form with `hx-post="{reverse('goal_delete', args=[goal.pk])}"` and an `hx-confirm="` attribute.
  - GET `goal_delete`. Assert 405 and that the goal still exists.
  - POST `goal_delete`. Assert a 302 to `goal_list`, no goal with that pk, and "Learn Django" missing from the list.
- `test_ac8_other_users_goal_is_404(logged_in_client, other_goal, method, name, target)`, parametrized:
  - `method`: `get` and `post` for `goal_edit`, `post` for `goal_delete`;
  - `target`: `"other"` (the pk of `other_goal`) and `"missing"` (`999999`).

  Assert 404 each time. Refresh `other_goal` and assert its title is still "Learn Rust" and it still exists. The POST to `goal_edit` sends `goal_data(title="Hijacked")`.
- `test_ac27_delete_goal_deletes_its_sessions(logged_in_client, goal, session)`: add a second session for `goal` (`date(2026, 9, 28)`, 30 minutes). GET the list and assert `hx-confirm="Delete “Learn Django” and its 2 sessions?"` is in the content. POST `goal_delete`. Assert `LearningSession.objects.filter(goal__pk=goal.pk).count() == 0`.
- `test_ac28_htmx_delete_removes_row(logged_in_client, goal)`: POST `goal_delete` with `headers={"HX-Request": "true"}`. Assert 200 (no redirect), `f'id="goal-{goal.pk}"'` not in the content, and the goal gone.

**Red.** `reverse("goal_delete", ...)` raises `NoReverseMatch` in every test except the `goal_edit` rows of AC8. Those pass already, because step 3's lookup only searches the user's goals.

**Green.**

- `learning/views.py`, `goal_delete(request, pk)`: `@login_required` above `@require_POST` (D26), the D1 lookup, `goal.delete()`. If `request.htmx`, return `HttpResponse("")`; otherwise redirect to `goal_list`.
- The route `goal_delete`.
- `goal_list`'s query adds `.annotate(session_count=Count("sessions"))`.
- `goal_list.html`: each row gets a Delete form with `method="post"`, `action` and `hx-post` pointing at `goal_delete`, `{% csrf_token %}`, `hx-confirm="Delete “{{ goal.title }}” and its {{ goal.session_count }} session{{ goal.session_count|pluralize }}?"`, `hx-target="closest li"` and `hx-swap="outerHTML"` (D8, D9).

**Refactor.** None.

## Step 5: AC12, AC13, AC14, AC15, AC19, AC34, session list and create

**Test.** New file `tests/test_sessions.py`, with `pytestmark = pytest.mark.django_db`:

- `test_ac12_create_session_appears_in_list(logged_in_client, goal)`: POST `reverse("session_create")` with `session_data(goal, notes="Wrote model tests")`. Assert a 302 to `reverse("session_list")` and one session on `goal` with `date(2026, 9, 30)`, `duration_minutes == 90` and those notes. GET the list and assert "Wrote model tests" and "Learn Django" are in the content, along with a link to `reverse("session_create")`.
- `test_ac13_form_offers_only_own_goals(logged_in_client, goal, other_goal)`: GET `session_create` and assert the `goal` field's queryset is `[goal]`. POST `session_data(other_goal)`. Assert 200, `"goal"` in the form errors, and no `LearningSession`.
- `test_ac14_tags_are_saved_and_shown(logged_in_client, goal)`: POST `session_data(goal, tags=[t.pk for t in Tag.objects.filter(name__in=["Python", "Testing"])])`. Assert the session's tag names are `{"Python", "Testing"}`. GET the list and assert both names are in the content. Also assert the form's `tags` queryset has `Tag.objects.count()` entries.
- `test_ac15_session_without_tags_saves(logged_in_client, goal)`: POST `session_data(goal)`. Assert a 302 and one session with no tags.
- `test_ac19_list_shows_only_own_sessions(logged_in_client, session, other_session)`: GET the list. Assert "Read the ORM docs" is present and "Borrow checker" is not.
- `test_ac34_no_goals_shows_create_a_goal_first(logged_in_client)`: GET `session_create`. Assert "Create a goal first", `f'href="{reverse("goal_create")}"'`, and no `name="date"` in the content.

**Red.** `reverse("session_create")` and `reverse("session_list")` raise `NoReverseMatch`.

**Green.**

- `learning/forms.py`: `SessionForm` (D27). `hours` and `minutes` are required `forms.IntegerField()`s with no bounds yet (step 6 adds them). `tags` is `ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)`. `date` uses `forms.DateInput(attrs={"type": "date"})`.
- `learning/views.py`:
  - `session_list(request)`: `@login_required`, renders `learning/session_list.html` with `LearningSession.objects.filter(goal__user=request.user).select_related("goal").prefetch_related("tags")` (D18);
  - `session_create(request)`: `@login_required`. If the user has no goals, it renders `learning/session_form.html` with `no_goals=True` and no form (D21). Otherwise it uses `SessionForm(request.POST or None, user=request.user)`; a valid POST saves and redirects to `session_list`.
- The two routes.
- Templates:
  - `session_list.html`: h1 "Sessions", a "New session" link, and a `<ul>` with one `<li id="session-{{ s.pk }}">` per session showing the date, the goal's title, `{{ s.duration_minutes }} min`, the tag names and the notes;
  - `session_form.html`: the form like `goal_form.html`, or, with `no_goals`, "Create a goal first" with a link to `goal_create`.

**Refactor.** None.

## Step 6: AC16, AC30, AC31, session form validation

**Test.** In `tests/test_sessions.py`:

- `test_ac16_invalid_session_is_rejected(logged_in_client, goal, overrides, field)`, parametrized:

  | id | overrides | error on |
  |---|---|---|
  | `no_date` | `date=""` | `date` |
  | `no_duration` | `hours="", minutes=""` | `hours` |
  | `zero` | `hours=0, minutes=0` | `__all__` |
  | `negative` | `hours=-1, minutes=0` | `hours` |

  POST `session_data(goal, **overrides)`. Assert 200, `field` in `response.context["form"].errors`, and no `LearningSession`.
- `test_ac30_duration_hours_and_minutes(logged_in_client, goal)`: POST `session_data(goal, minutes=60)` and assert `"minutes"` in the form errors and no session. POST `session_data(goal, hours=2, minutes=5)` and assert the session's `duration_minutes == 125`.
- `test_ac31_date_today_or_earlier(logged_in_client, goal)`:
  - assert `settings.TIME_ZONE == "Europe/Berlin"`;
  - GET `session_create` and assert the form's `date` initial equals `timezone.localdate()`;
  - POST `session_data(goal, date=(timezone.localdate() + timedelta(days=1)).isoformat())` and assert `"date"` in the errors and no session;
  - POST with `date=timezone.localdate().isoformat()` and assert a 302.

**Red.**

- The `no_date` and `no_duration` rows pass already, because the fields have been required since step 5.
- `zero` and `negative` fail on the assertion: the form accepts them and saves a session.
- AC30 fails: the form accepts 60 minutes.
- AC31 fails on `TIME_ZONE`, which is `"UTC"`.

**Green.**

- `learning_companion/settings.py`: `TIME_ZONE = "Europe/Berlin"` (D4).
- `SessionForm`:
  - `hours = forms.IntegerField(min_value=0)`, `minutes = forms.IntegerField(min_value=0, max_value=59)`;
  - `date` gets `initial=timezone.localdate`;
  - `clean_date()` rejects a date after `timezone.localdate()` with "The date can't be in the future.";
  - `clean()` adds a form error "The duration must be more than zero." when hours and minutes are both present and their total is 0.

**Refactor.** None.

## Step 7: AC17, AC32, session edit

**Test.** In `tests/test_sessions.py`:

- `test_ac17_edit_session_shows_new_values(logged_in_client, goal, session)`: GET `reverse("session_edit", args=[session.pk])`. Assert the form's `hours` value is 1 and `minutes` value is 30. POST `session_data(goal, hours=0, minutes=45, notes="Read about querysets")`. Assert a 302 to `session_list`, `duration_minutes == 45`, and the list shows "Read about querysets" and not "Read the ORM docs".
- `test_ac32_edit_moves_session_to_another_goal(logged_in_client, user, session)`: create a second goal "Learn Docker" for `user`. POST `session_data(that_goal)` to the edit URL. Assert `session.goal` is the new goal after a refresh.

**Red.** `reverse("session_edit", ...)` raises `NoReverseMatch`.

**Green.**

- `SessionForm.__init__`: when `self.instance.pk` is set, the initial values for `hours` and `minutes` come from `divmod(self.instance.duration_minutes, 60)`.
- `learning/views.py`, `session_edit(request, pk)`: `@login_required`, `get_object_or_404(LearningSession, pk=pk, goal__user=request.user)` (D1), `SessionForm(request.POST or None, instance=session, user=request.user)`. A valid POST saves and redirects to `session_list`.
- The route, and an "Edit" link on each session row.

**Refactor.** None.

## Step 8: AC18, AC20, AC29, session delete

**Test.** In `tests/test_sessions.py`:

- `test_ac18_delete_session_after_confirmation(logged_in_client, session)`: the same three parts as AC6. The list row has a form with `hx-post` pointing at `session_delete` and `hx-confirm="Delete this session?"`. A GET returns 405 and keeps the session. A POST redirects to `session_list`, the session is gone, and the list no longer shows "Read the ORM docs".
- `test_ac20_other_users_session_is_404(logged_in_client, other_session, method, name, target)`: parametrized like AC8 over `session_edit` (get, post) and `session_delete` (post), for `"other"` and `"missing"`. Assert 404, and that `other_session` still exists with `duration_minutes == 45`. The POST to `session_edit` sends `session_data(other_session.goal, minutes=1)`.
- `test_ac29_htmx_delete_removes_row(logged_in_client, session)`: POST `session_delete` with `headers={"HX-Request": "true"}`. Assert 200, `f'id="session-{session.pk}"'` not in the content, and the session gone.

**Red.** `reverse("session_delete", ...)` raises `NoReverseMatch` everywhere except the `session_edit` rows of AC20, which pass already through step 7's lookup.

**Green.**

- `learning/views.py`, `session_delete(request, pk)`: like `goal_delete`, with the D1 session lookup and a redirect to `session_list`.
- The route, and the Delete form on each session row with `hx-confirm="Delete this session?"`, `hx-target="closest li"` and `hx-swap="outerHTML"`.

**Refactor.** `goal_delete` and `session_delete` share the HTMX-or-redirect ending. Pull it into a helper `_deleted_response(request, list_name)` in `learning/views.py` only if both read the same afterwards; otherwise none.

## Step 9: AC9, AC10, AC11, AC37, AC38, status filter with HTMX

**Test.** In `tests/test_goals.py`. The setup in each test creates ada's goals "Plan A" (planned), "Doing B" (in-progress) and "Done C" (done) and uses `other_goal` (grace's, planned).

- `test_ac9_filter_by_status(logged_in_client, other_goal, status, shown)`, parametrized: `planned` shows only "Plan A", `in-progress` only "Doing B", `done` only "Done C". GET `reverse("goal_list") + f"?status={status}"`. Assert the expected title is present, the other two are absent, and "Learn Rust" is absent.
- `test_ac10_no_filter_shows_all(logged_in_client, other_goal)`: GET the list. Assert all three titles are present and "Learn Rust" is absent.
- `test_ac11_empty_states(logged_in_client, user)`: with no goals, GET the list and assert "No goals yet." Then create "Plan A" (planned) and GET `?status=done`. Assert "No goals with this status." and no "Plan A".
- `test_ac37_unknown_status_shows_all(logged_in_client)`: GET `?status=foo`. Assert all three titles are present.
- `test_ac38_filter_links_swap_list_in_place(logged_in_client)`:
  - GET the list. Assert links for All, Planned, In progress and Done, where the Planned link has `href="?status=planned"` and carries `hx-get`, `hx-target="#goal-list"` and `hx-push-url="true"`, and the page has `id="goal-list"`.
  - GET `?status=planned` with `headers={"HX-Request": "true"}`. Assert `learning/_goal_list.html` is among the rendered template names, `base.html` is not, and "Plan A" is present without "Doing B".

**Red.**

- AC10 and AC37 pass already: the list ignores `status` and shows all of the user's goals.
- AC9 fails on the assertion: "Doing B" and "Done C" show under `?status=planned`.
- AC11 fails: there's no empty-state text.
- AC38 fails: there are no filter links, and the HTMX request renders `base.html`.

**Green.**

- `goal_list` view: read `status = request.GET.get("status")`. If it's in `Goal.Status.values`, filter on it; otherwise ignore it (D11). Pass `status` (the valid value or `""`) and `status_choices = Goal.Status.choices` to the template. If `request.htmx`, render `learning/_goal_list.html`; otherwise `learning/goal_list.html`.
- New partial `learning/_goal_list.html`: the filter links, then the `<ul>` with `{% for %}…{% empty %}`. The empty text is "No goals with this status." when `status` is set, and "No goals yet." otherwise. Each link uses `href="{% querystring status=value %}"` (`status=None` for All) and the same URL in `hx-get`, with `hx-target="#goal-list"` and `hx-push-url="true"`. The current status link is bold.
- `goal_list.html`: replace the `<ul>` with `<div id="goal-list">{% include "learning/_goal_list.html" %}</div>`.

**Refactor.** None.

## Step 10: AC21, AC36, sessions list rows and the duration format

**Test.** New file `tests/test_learning_extras.py`:

- `test_ac36_duration_format(minutes, text)`, parametrized: `90` → `"1 h 30 min"`, `45` → `"45 min"`, `120` → `"2 h"`, `0` → `"0 min"` (D24). Assert `duration(minutes) == text`, with `duration` imported from `learning.templatetags.learning_extras`.

In `tests/test_sessions.py`:

- `test_ac36_session_rows(logged_in_client, goal, session)`: give `session` the tag "Python". Add a newer session on `goal` (`date(2026, 10, 1)`, 30 minutes, notes "Later one"). GET the list. Assert "Later one" comes before "Read the ORM docs" in the content, and the `session-{session.pk}` row contains "30 Sep 2026", "Learn Django", "1 h 30 min", "Python" and "Read the ORM docs" but not "Then tried annotate".
- `test_ac21_no_sessions_empty_state(logged_in_client, goal)`: GET the list. Assert "No sessions yet."

**Red.**

- The filter test fails with `NotImplementedError` from the step-0 stub.
- The rows test fails on the assertion: the row shows "90 min" and the whole notes.
- The empty-state test fails: there's no text.
- The newest-first order in the rows test already holds through `Meta.ordering` (step 0).

**Green.**

- `learning/templatetags/learning_extras.py`: `duration(minutes)` uses `divmod(minutes, 60)` and returns the D24 formats.
- `session_list.html`: `{% load learning_extras %}`. Each row shows `{{ s.date|date:"j M Y" }}`, the goal's title, `{{ s.duration_minutes|duration }}`, the tag names and `{{ s.notes.splitlines.0 }}`. `{% empty %}` shows "No sessions yet."

To find the row in the test, slice the content from `id="session-{pk}"` to the next `</li>`.

**Refactor.** None.

## Step 11: AC35, goals list rows and order

**Test.** In `tests/test_goals.py`:

- `test_ac35_goal_rows_and_order(logged_in_client, user, goal, session)`:
  - Create "Old goal" (done) for `user` and set its `created_at` to 10 days ago with `update()`. Set `goal.updated_at` to `datetime(2026, 9, 30, 12, tzinfo=UTC)` with `update()`.
  - GET the list. Assert "Learn Django" comes before "Old goal". The `goal-{goal.pk}` row contains "Planned", "1 session", "1 h 30 min" and "30 Sep 2026". The "Old goal" row contains "0 sessions" and "0 min".
  - GET `?order=oldest`. Assert "Old goal" comes before "Learn Django".
  - GET `?order=oldest&status=done`. Assert "Old goal" is present and "Learn Django" is absent.
  - Assert the order toggle link carries `hx-get`, `hx-target="#goal-list"` and `hx-push-url="true"`.

**Red.**

- Newest-first already holds through `Meta.ordering`.
- The assertion fails on the row: there's no status label, count, total or date yet.
- `?order=oldest` still lists newest first.

**Green.**

- `goal_list` view: the query adds `total_minutes=Coalesce(Sum("sessions__duration_minutes"), 0)` next to `session_count`. If `request.GET.get("order") == "oldest"`, order by `created_at`. Pass `order` to the template.
- `_goal_list.html`: `{% load learning_extras %}`. Each row shows `{{ goal.get_status_display }}`, `{{ goal.session_count }} session{{ goal.session_count|pluralize }}`, `{{ goal.total_minutes|duration }}` and `Updated {{ goal.updated_at|date:"j M Y" }}`. Next to the status links, a toggle "Oldest first" / "Newest first" uses `{% querystring order="oldest" %}` or `{% querystring order=None %}`, with the same `hx-*` attributes.

**Refactor.** None.

## Step 12: AC33, sessions goal filter

**Test.** In `tests/test_sessions.py`:

- `test_ac33_filter_by_goal(logged_in_client, user, goal, session, other_session)`: create a second goal "Learn Docker" for `user`, with a session whose notes are "Docker notes".
  - GET `reverse("session_list") + f"?goal={goal.pk}"`. Assert "Read the ORM docs" is present and "Docker notes" is absent.
  - GET `?goal={other_session.goal.pk}`, then `?goal=abc`. Each shows both of ada's sessions and not "Borrow checker".
  - GET the list and assert a `<select name="goal">` whose options are "All goals" and ada's two goals (not "Learn Rust"), inside a form with `hx-get`, `hx-target="#session-list"` and `hx-push-url="true"`.
  - GET `?goal={goal.pk}` with `headers={"HX-Request": "true"}`. Assert `learning/_session_list.html` rendered and `base.html` did not.

**Red.** It fails on the assertion. The view ignores `?goal=`, so "Docker notes" shows, and there's no select.

**Green.**

- `session_list` view: read `goal`. If it's a digit string matching one of the user's goals, filter on it; otherwise ignore it (D6). Pass `goals` (the user's goals) and the chosen `goal_id`. If `request.htmx`, render `learning/_session_list.html`.
- New partial `learning/_session_list.html` with the `<ul>` and its `{% empty %}`.
- `session_list.html`: a `<form method="get" action="{% url 'session_list' %}" hx-get="{% url 'session_list' %}" hx-trigger="change, submit" hx-target="#session-list" hx-push-url="true">` (the Filter button also swaps in place; R5) with the select and a "Filter" button, then `<div id="session-list">{% include "learning/_session_list.html" %}</div>`.

**Refactor.** None.

## Step 13: AC39, messages

**Test.** New file `tests/test_learning_messages.py`, with `pytestmark = pytest.mark.django_db`:

- `test_ac39_message_after_each_change(logged_in_client, goal, session, action, text)`, parametrized with ids:
  - `goal_create`: POST `goal_create` with `goal_data()` → "Goal created.";
  - `goal_edit`: POST `goal_edit` (goal) with `goal_data()` → "Goal updated.";
  - `goal_delete`: POST `goal_delete` (goal) → "Goal deleted.";
  - `session_create`: POST `session_create` with `session_data(goal)` → "Session created.";
  - `session_edit`: POST `session_edit` (session) with `session_data(goal)` → "Session updated.";
  - `session_delete`: POST `session_delete` (session) → "Session deleted.".

  Each posts with `follow=True` and asserts `text` in the content inside `id="messages"`. The test builds the URL from the action name and the matching fixture's pk.
- `test_ac39_htmx_delete_shows_message(logged_in_client, goal, session, name, text)`, parametrized over `goal_delete` / "Goal deleted." and `session_delete` / "Session deleted.": POST with `headers={"HX-Request": "true"}`. Assert the content contains `id="messages"`, `hx-swap-oob="true"` and `text`.

**Red.** It fails on the assertion: no view adds a message and `base.html` shows none.

**Green.**

- New `theme/templates/messages.html`: `<div id="messages"{% if oob %} hx-swap-oob="true"{% endif %}>`, with one `<p>` per message.
- `theme/templates/base.html`: `{% include "messages.html" %}` just inside the content container, above `{% block content %}`.
- `learning/views.py`: `messages.success(request, ...)` with the D17 texts in all six views, before the redirect or the HTMX response. The HTMX branch of both deletes returns `render(request, "messages.html", {"oob": True})` in place of `HttpResponse("")`. That keeps AC28 and AC29 green: the row is still swapped out, now for an empty body plus the out-of-band messages.

**Refactor.** None.

## Step 14: AC22, AC40, links and login

**Test.** In `tests/test_goals.py`:

- `test_ac22_pages_require_login(client, goal, session, name, kind)`, parametrized over all eight routes from D20. `kind` is `None` for list and create pages, `"goal"` or `"session"` for the routes with a pk. GET the URL as an anonymous client. Assert 302 and `response.url == f"{reverse('login')}?next={url}"`.

In `tests/test_home.py`:

- `test_ac40_links_to_goals_and_sessions(logged_in_client)`:
  - GET `/`. Assert the nav has `href="{reverse("goal_list")}"` with the text "Goals". Assert home links to `reverse("goal_list")` and `reverse("session_list")`, and that "Nothing here yet." is gone.
  - GET `reverse("goal_list")`. Assert a link to `reverse("session_list")`.

**Red.**

- AC22 passes on its first run: each view got `@login_required` in the step that created it. The test pins that for all eight routes. The build log records it as green from the start.
- AC40 fails on the assertion: there's no Goals link.

**Green.**

- `theme/templates/base.html`: `<a href="{% url 'goal_list' %}" class="underline">Goals</a>` before the Profile link, inside `{% if user.is_authenticated %}`.
- `core/templates/core/home.html`: replace "Nothing here yet." with a paragraph linking "Your goals" (`goal_list`) and "Your sessions" (`session_list`).
- `goal_list.html`: a "Sessions" link to `session_list` next to "New goal".

**Refactor.** None.

## Step 15: rework R1, AC33, a non-ASCII digit in the goal filter

**Test.** In `tests/test_sessions.py`, `test_ac33_filter_by_goal`: add `"²"` to the loop over ignored values, so it reads `for value in [other_session.goal.pk, "abc", "²"]:`. Nothing else in the test changes.

**Red.** `GET /sessions/?goal=²` raises `ValueError` ("Field 'id' expected a number but got '²'") and the test client re-raises it. `"²".isdigit()` is `True`, so `goals.filter(pk="²")` runs.

**Green.** `learning/views.py`, `session_list`: replace `goal_id.isdigit()` with `goal_id.isdecimal()`.

**Refactor.** None.

## Step 16: rework R4, AC35, the visible session count

**Test.** In `tests/test_goals.py`, `test_ac35_goal_rows_and_order`: take "1 session" out of the `for text in [...]` list and check it as `assert re.search(r"<span>\s*1 session\s*</span>", goal_row)`. Replace `assert "0 sessions" in old_row` with `assert re.search(r"<span>\s*0 sessions\s*</span>", old_row)`. The row slice also holds the Delete form's `hx-confirm` text ("…and its 1 session?"), so the old checks passed without the visible count.

**Red.** None: test-only change. The stronger assertion passes against the current `_goal_list.html`, which has `<span>{{ goal.session_count }} session{{ goal.session_count|pluralize }}</span>`. The build log notes that deleting that span would now fail the test.

**Green.** None beyond the test.

**Refactor.** None.

## Step 17: rework R2, AC43, history restore gets the full page

**Test.**

- In `tests/test_goals.py`, `test_ac43_history_restore_gets_full_page(logged_in_client, goal)`:
  - GET `reverse("goal_list") + "?status=planned"` with `headers={"HX-Request": "true", "HX-History-Restore-Request": "true"}`. Assert `base.html` and `learning/goal_list.html` are among the rendered template names.
  - GET the same URL with only `headers={"HX-Request": "true"}`. Assert `"HX-Request" in response["Vary"]`.
- In `tests/test_sessions.py`, `test_ac43_history_restore_gets_full_page(logged_in_client, goal)`: the same two checks for `reverse("session_list") + f"?goal={goal.pk}"`, with `learning/session_list.html`.

**Red.** Both fail on the template assertion: the views render only the partial (`learning/_goal_list.html`, `learning/_session_list.html`) because `request.htmx` is truthy. The `Vary` check would fail too: the header is only `Cookie`.

**Green.** In `learning/views.py`:

- `goal_list` and `session_list`: change `if request.htmx:` to `if request.htmx and not request.htmx.history_restore_request:`.
- Decorate both with `@vary_on_headers("HX-Request")` from `django.views.decorators.vary`, below `@login_required`.
- A comment cites D33.

**Refactor.** None.

## Step 18: rework R3, AC42, a session is at most 24 hours

**Test.** In `tests/test_sessions.py`, `test_ac42_session_longer_than_24_hours_is_rejected(logged_in_client, goal, overrides, field)`, parametrized:

| id | overrides | error on |
|---|---|---|
| `25_hours` | `hours=25, minutes=0` | `hours` |
| `24_hours_1_min` | `hours=24, minutes=1` | `__all__` |
| `huge` | `hours=10**18, minutes=0` | `hours` |

POST `session_data(goal, **overrides)`. Assert 200, `field` in `response.context["form"].errors`, and no `LearningSession`.

Also `test_ac42_exactly_24_hours_saves(logged_in_client, goal)`: POST `session_data(goal, hours=24, minutes=0)`. Assert a 302 and `duration_minutes == 1440`.

**Red.**

- `25_hours` and `24_hours_1_min` fail on `assert 302 == 200`: the form accepts them and saves.
- `huge` fails with an overflow error from the database instead of a form error.
- `test_ac42_exactly_24_hours_saves` passes already; the build log records it as green from the start.

**Green.** `learning/forms.py`, `SessionForm`:

- `hours = forms.IntegerField(min_value=0, max_value=24)`;
- `clean()` adds the form error "A session can't be longer than 24 hours." when the total is above 1440, next to the zero check.
- A comment cites D32.

**Refactor.** None.

## Step 19: rework R6, R7, AC28, AC29, AC33, the swap attributes are tested

**Test.** Extend three existing tests. Nothing else in them changes.

- `tests/test_goals.py`, `test_ac28_htmx_delete_removes_row`: before the POST, GET `reverse("goal_list")`, find the Delete form with `re.search(rf'<form[^>]+hx-post="{reverse("goal_delete", args=[goal.pk])}"[^>]*>', content)`, and assert it carries `hx-target="closest li"` and `hx-swap="outerHTML"`.
- `tests/test_sessions.py`, `test_ac29_htmx_delete_removes_row`: the same for `reverse("session_list")` and `session_delete`.
- `tests/test_sessions.py`, `test_ac33_filter_by_goal`: next to the `hx-target` check on the filter form, add `assert 'hx-trigger="change, submit"' in form.group(0)`.

**Red.** None: test-only change. The templates already carry the attributes. As in step 16, the build log records a mutation check: remove each attribute in turn from the template, see the test fail, and put it back.

**Green.** None beyond the tests.

**Refactor.** None.

## Step 20: rework M1, AC35, newest first with the annotated query

**Test.** In `tests/test_goals.py`, `test_ac35_goal_rows_and_order`: after creating "Old goal" and moving its `created_at` back, create a third goal, `Goal.objects.create(user=user, title="Newest goal")`. Its pk is the highest, and so is its `created_at`. Then:

- the default GET asserts `content.index("Newest goal") < content.index("Learn Django") < content.index("Old goal")`, in place of the two-goal check;
- the `?order=oldest` GET asserts `content.index("Old goal") < content.index("Learn Django") < content.index("Newest goal")`.

The other checks stay as they are. With only two goals, pk order matched the expected newest-first order by chance, so the test missed the bug.

**Red.** The default GET lists the goals in pk order (Learn Django, Old goal, Newest goal), so `content.index("Newest goal") < content.index("Learn Django")` fails. Django drops `Meta.ordering` once `annotate(Count(...), Sum(...))` adds a GROUP BY.

**Green.** `learning/views.py`, `goal_list`: in the branch for any `order` other than `"oldest"`, add `goals = goals.order_by("-created_at")`, with a comment saying why `Meta.ordering` doesn't apply here.

**Refactor.** None.

## Review

### Round 1, 2026-10-02

- R1. should-fix, `learning/views.py:93`: `isdigit()` accepts `²`, so `?goal=²` gives a 500 instead of being ignored (D6). → fixed in step 15 (auto)
- R2. should-fix, `learning/views.py:44`, `:99`: htmx history-restore requests get only the partial, and the lists send no `Vary: HX-Request`. → D33, fixed in step 17
- R3. should-fix, `learning/forms.py:17`: no cap on hours, so a huge value overflows the column (500). → Q21, D32, fixed in step 18
- R4. should-fix, `tests/test_goals.py:281`: AC35's "1 session" / "0 sessions" checks also match the Delete popup text. → fixed in step 16 (auto)
- R5. nit, `learning/templates/learning/session_list.html:8`: `hx-trigger="change, submit"` and `action` weren't in step 12's text. → plan updated 2026-10-02

### Round 2, 2026-10-02

The round 1 fixes were checked and hold. One code-review finding (no empty state after an HTMX delete of the last row) was dropped: D9 accepts it.

- R6. should-fix, `learning/templates/learning/_goal_list.html:31`, `_session_list.html:14`: no test checks `hx-target="closest li"` / `hx-swap="outerHTML"`, which AC28 and AC29 rely on. → fixed in step 19 (accepted by user, round 2)
- R7. nit, `learning/templates/learning/session_list.html:8`: `test_ac33` doesn't check `hx-trigger="change, submit"`. → fixed in step 19 (accepted by user, round 2)

### Manual check, 2026-10-02

- M1. should-fix, `learning/views.py` `goal_list`: "Oldest first" changes nothing in the browser. The default list isn't newest first because Django ignores `Meta.ordering` on the annotated (GROUP BY) query, so both orders come out in pk order. → fixed in step 20

## Files

**New, `learning` app:**

- `learning/__init__.py`, `apps.py`, `migrations/__init__.py`: from `startapp` (D25).
- `learning/models.py`: `Goal`, `LearningSession` (step 0).
- `learning/migrations/0001_initial.py`: both models (step 0).
- `learning/admin.py`: both models (D16).
- `learning/forms.py`: `GoalForm`, `SessionForm` (D27).
- `learning/views.py`: the eight views from D20.
- `learning/urls.py`: the D20 routes.
- `learning/templatetags/__init__.py`, `learning/templatetags/learning_extras.py`: the `duration` filter (D24), a stub from step 0, filled in step 10.
- `learning/templates/learning/goal_list.html`, `_goal_list.html`, `goal_form.html`, `session_list.html`, `_session_list.html`, `session_form.html`.

**New, theme:**

- `theme/templates/messages.html`: the messages partial (D17).

**New, tests:**

- `tests/test_learning_data.py`, `tests/test_goals.py`, `tests/test_sessions.py`, `tests/test_learning_extras.py`, `tests/test_learning_messages.py`.

**Changed:**

- `learning_companion/settings.py`: `"learning"` in `INSTALLED_APPS`, `TIME_ZONE = "Europe/Berlin"` (D4).
- `learning_companion/urls.py`: `include("learning.urls")`.
- `theme/templates/base.html`: the Goals nav link and the messages include.
- `core/templates/core/home.html`: links to goals and sessions.
- `tests/conftest.py`: the D31 fixtures and helpers.
- `tests/test_admin.py`: AC41.
- `tests/test_home.py`: AC40.

**For reference:**

- `accounts/views.py`, `accounts/forms.py`: the view, form and M2M save patterns.
- `accounts/templates/accounts/profile_form.html`: the form page layout.
- `tests/test_profile.py`, `tests/test_signup.py`, `tests/test_account_delete.py`: the access, invalid-form and delete test patterns.

**Local only, not tracked:** `db.sqlite3`, migrated in step 0.

## Verification

After each new test, `make test ARGS="-k <test name>"` fails for the reason in the step's Red, or passes where the Red says it already holds.

After each Green, `make test` passes in full.

At the end:

- `make test`: all tests pass, 64 from before plus the new ones.
- `make lint`: no errors.
- `make format`: no files changed.
- `.venv/bin/python manage.py makemigrations --check --dry-run`: no missing migrations.

The project has no type check or separate build step.

When done, ask the user whether they want to do these checks by hand (D30). They cover what tests without a browser can't see (D28):

1. `make dev`, log in, and open Goals from the nav.
2. Create three goals with different statuses. Click Planned: only the list changes, without a full page reload, and the address bar shows `?status=planned`. Reload: the filter stays. Click "Oldest first": the order flips and the status filter stays.
3. Click Delete on a goal with sessions. The browser asks `Delete “<title>” and its N sessions?`. Cancel: nothing changes. Confirm: the row disappears without a reload, and "Goal deleted." appears at the top.
4. Open Sessions from the goals list. Pick a goal in the dropdown: only the list changes, and the address bar shows `?goal=<pk>`.
5. Create a session dated tomorrow: the form shows "The date can't be in the future." The date field starts with today's date.
6. Delete a session: the browser asks "Delete this session?", and after confirming the row disappears and "Session deleted." appears.
