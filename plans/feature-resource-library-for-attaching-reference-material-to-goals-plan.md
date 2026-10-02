# Resource library for attaching reference material to goals: TDD plan

## Context

This ticket adds a `Resource` model to the `learning` app: a URL, a title, a type (article, video, repo or doc) and optional tags, attached to one goal. It also adds the goal detail page that #4 left for this ticket (#4 D14).

The detail page shows the goal, lists its resources with a type badge each, and holds the form for attaching a new one. Resources can be edited on their own page and deleted from the detail page.

Refinement: [feature-resource-library-for-attaching-reference-material-to-goals-refinement.md](feature-resource-library-for-attaching-reference-material-to-goals-refinement.md). Source: #5.

Branch: `feature/5-resource-library-for-attaching-reference-material-to-goals`.

**In scope:**

- the `Resource` model, its migration and admin;
- the goal detail page, and a link to it from each goal title in the goals list;
- attaching, editing and deleting resources, with tags;
- deleting a goal from its detail page.

**Not in scope:**

- listing the goal's sessions on the detail page (D1);
- a resource count on the goals list, or resources in the goal delete popup (D17);
- HTMX for the attach form (D11);
- a styled delete modal (#19).

Edit and delete go beyond the ticket's text. The user chose to include them (D12).

## Progress

Plan written on 2026-10-02. Nothing built yet. The suite has 145 passing tests before the build.
Step 0 done: 145 passed, 145 before the build.
Step 1 done: 149 passed, 145 before the build.
Step 2 done: 154 passed, 145 before the build.
Step 3 done: 155 passed, 145 before the build.
Step 4 done: 160 passed, 145 before the build.
Step 5 done: 186 passed, 145 before the build.
Step 6 done: 188 passed, 145 before the build.
Step 7 done: 195 passed, 145 before the build.
Step 8 done: 200 passed, 145 before the build.
Step 9 done: 202 passed, 145 before the build.
Deviations: AC5, AC6 and AC32 went red on `KeyError: 'form'`, not on `NoReverseMatch`, because they read the form from the detail page before reversing `resource_create`. AC24 went red on `ValueError` from `content.index`, the same cause as the planned assertion (no resources listed). `ruff format` reformatted 4 of the new or changed files after step 9. A mistaken repo-wide `ruff format` also rewrote code blocks in 6 `guides/*.md` files, which this build doesn't own; the user restores them (see build log).
Built on 2026-10-02.

Manual check on 2026-10-02 found M1 (check 6, AC31): 1 rework step added (10). AC31 is open again until it's built.
Step 10 done: 203 passed, 145 before the build.
Built on 2026-10-02, M1 fix included. The user confirmed all six manual checks, check 6 after the fix.
Review round 1 on 2026-10-02: 4 rework steps added (11, 12, 13, 14). The user restored `guides/` (R2).
Step 11 done: 203 passed, 145 before the build.
Step 12 done: 203 passed, 145 before the build.
Step 13 done: 204 passed, 145 before the build.
Step 14 done: 205 passed, 145 before the build.
Deviations in the rework: steps 11 and 12 had no red, as planned; each tightened test was seen to fail once with its span removed. Lint asked for two changes the plan didn't spell out: `re.DOTALL` in place of `re.S` in step 11's test (FURB167), and a `ClassVar` annotation on `ResourceAdmin.formfield_overrides` (RUF012), like #4's RUF012 deviation.
Built on 2026-10-02, review round 1 rework included.
Reviewed on 2026-10-02, round 2: no rework.

## Decisions

The user answered the questions on 2026-10-02.

### The detail page

D1. (Q1) The goal detail page shows:

- the title, description, status label, session count ("1 session") and total time ("1 h 30 min");
- an Edit link to `goal_edit`;
- a Delete button (D19).

It doesn't list the goal's sessions. Source: user, 2026-10-02.

D2. (Q2) In the goals list, each goal's title becomes a link to its detail page.

- The sessions list's goal titles stay plain text.
- `goal_create` and `goal_edit` still redirect to `goal_list` after saving.

Source: user, 2026-10-02.

D3. (Q3) The detail page lives at `goals/<int:pk>/`, named `goal_detail`. Source: user, 2026-10-02.

D19. (Q22) The detail page has a Delete button for the goal.

- It's a POST form with `hx-post` to `goal_delete` and the same `hx-confirm` text as the list: `Delete “Learn Django” and its 1 session?`.
- It carries `<input type="hidden" name="from" value="detail">`.
- For an HTMX request with `from=detail`, `goal_delete` returns `HttpResponseClientRedirect(reverse("goal_list"))` from `django_htmx.http`. The browser then loads the goals list, which shows "Goal deleted.".
- Without HTMX, `goal_delete` redirects to `goal_list` as it does today.
- The list's HTMX delete (#4 D9) stays as it is.

Source: user, 2026-10-02; the mechanism: plan, accepted by the user.

### Resources and their fields

D4. (Q4) The detail page shows resources in one list, each with a type badge, not one section per type. Source: user, 2026-10-02.

D5. (Q5) Resources are listed newest first: `Meta.ordering = ("-created_at", "-pk")`. The `-pk` keeps the order fixed when two have the same timestamp. Source: user, 2026-10-02; tie-break: plan.

D6. (Q16) The type is a nested `Resource.Type(models.TextChoices)`, stored in `type = CharField(max_length=20, choices=Type.choices)`:

- `ARTICLE = "article", "Article"`
- `VIDEO = "video", "Video"`
- `REPO = "repo", "Repo"`
- `DOC = "doc", "Doc"`

Source: user, 2026-10-02, following #4 D23.

D7. (Q6) The title is required, at most 200 characters, like `Goal.title`. Source: user, 2026-10-02.

D8. (Q7, Q23) URL rules:

- Django's default URL check decides what's valid. It accepts `http`, `https`, `ftp` and `ftps` and rejects other schemes, such as `javascript:` and `file:`.
- At most 500 characters: `url = models.URLField(max_length=500)`.
- The form declares `url = forms.URLField(label="URL", max_length=500, assume_scheme="https")`. Input typed without a scheme, such as `example.com/post`, is stored as `https://example.com/post`. Passing `assume_scheme` also silences Django 5.2's `RemovedInDjango60Warning` (`django/forms/fields.py:778-792`).
- `localhost:8000/docs` without `http://` is rejected, because Django reads `localhost:` as a scheme. `http://localhost:8000/docs` is accepted.

Source: user, 2026-10-02. The first answer was http and https only. The user changed it to "allow all for now" once Django's default check turned out to need less code. Django's default is the safe reading of "all".

D9. (Q8) The same URL can be attached twice to one goal. Source: user, 2026-10-02.

D10. (Q9) The type has no default. The form's select starts on Django's blank choice `---------`, so the user has to pick one. Source: user, 2026-10-02.

D14. (Q12) Resources take optional tags from the admin-maintained `core.Tag` list.

- `tags = models.ManyToManyField("core.Tag", blank=True)`.
- The form uses a checkbox list, like `SessionForm.tags` (`learning/forms.py:20-24`).
- Each resource shows its tags as a comma-separated list, like the sessions list (`_session_list.html:8`). The type is the badge.

Source: user, 2026-10-02; display: plan, following #4 D5.

D15. (Q13) Resource links open in a new tab: `target="_blank" rel="noopener noreferrer"`. Source: user, 2026-10-02.

### Attach, edit and delete

D11. (Q10) The attach form sits on the detail page and posts to its own route.

- Route: `goals/<int:pk>/resources/new/`, named `resource_create`, POST only (`require_POST`).
- It's a normal post with no HTMX.
- On success: save, show "Resource added.", and redirect to `goal_detail`.
- On an invalid post: re-render the detail page with the bound form and its errors, status 200.

Source: user, 2026-10-02.

D12. (Q11, Q17, Q18) The user edits a resource on its own page.

- Route: `resources/<int:pk>/edit/`, named `resource_edit`, template `learning/resource_form.html`.
- The form edits `url`, `title`, `type` and `tags`. It has no goal field, so a resource stays on its goal.
- Saving shows "Resource updated." and redirects to the resource's `goal_detail`.

The ticket only asks for attaching. The user added edit and delete. Source: user, 2026-10-02.

D13. (Q19) The user deletes a resource from the detail page, the same way as goals and sessions (#4 D9).

- Route: `resources/<int:pk>/delete/`, named `resource_delete`, POST only.
- The Delete button is a POST form with `hx-post`, `hx-confirm="Delete “<title>”?"`, `hx-target="closest li"` and `hx-swap="outerHTML"`.
- With HTMX: `_deleted_response` returns the out-of-band messages, so the row disappears and "Resource deleted." shows.
- Without HTMX: redirect to the resource's `goal_detail`. `_deleted_response(request, reverse("goal_detail", args=[goal_pk]))` already does this, since `redirect` accepts a URL.

Source: user, 2026-10-02.

D16. (Q14, Q20) The texts:

- messages: "Resource added.", "Resource updated." and "Resource deleted.";
- empty state: "No resources yet.".

Source: user, 2026-10-02.

D17. (Q15) The goals list shows no resource count, and the goal delete popup doesn't mention resources. Source: user, 2026-10-02.

D18. (Q21) Opening the edit page of another user's resource, posting to it, or deleting it gives 404. A missing id gives 404 too.

- Ownership goes through the goal: `get_object_or_404(Resource, pk=pk, goal__user=request.user)`.
- `Resource` has no user field.

Source: #4 D1 and D18.

### Code layout and tests

D20. `Resource` lives in `learning/models.py` (ticket-3 D1).

- `goal = ForeignKey(Goal, on_delete=models.CASCADE, related_name="resources")`, following #4 D22.
- `created_at = DateTimeField(auto_now_add=True)`.
- `__str__` returns the title.
- Registered in the admin with `list_display = ("title", "goal", "type", "created_at")`, following #4 D16.

Source: plan.

D21. The new views are function-based with `@login_required`. `resource_create` and `resource_delete` put `@login_required` above `@require_POST`, so an anonymous visitor goes to login before the method check. Source: #4 D26.

D22. `goal_detail` needs the same session count and total time as `goal_list`. A helper `_goals_with_totals(user)` in `learning/views.py` returns `Goal.objects.filter(user=user).annotate(session_count=..., total_minutes=...)`, and both views use it. Source: plan.

D23. Test layout:

- `tests/test_goal_detail.py` (new): the detail page, its link from the list, and deleting a goal from it.
- `tests/test_resources.py` (new): attaching, listing, editing and deleting resources.
- `tests/test_admin.py` and `tests/test_learning_data.py` get the admin and cascade tests.
- New fixtures in `tests/conftest.py`: `resource(goal)`, `other_resource(other_goal)`, and the plain helper `resource_data(**overrides)`.
- HTMX responses are tested without a browser (#4 D28).

The popups, the in-place removal and the new tab stay manual checks (Verification). Source: plan.

D24. AC20 (migration committed) is checked by the existing `test_ac24_migrations_are_committed` (`tests/test_learning_data.py:20-21`). It runs `makemigrations --check` for every app, so it fails as soon as a model change has no migration. Source: plan.

D25. Automated tests cover every criterion. When the build is done, it asks the user whether they want to do the manual checks in Verification. Source: #4 D30.

### During the manual checks

D26. (M1) Django draws `ResourceForm.url` as `<input type="url">`. The browser then refuses to submit `example.com/post` ("Please enter a URL"), so D8's `https://` rule never runs. The test passed because it posts without a browser. Answer:

- the URL field uses `forms.TextInput(attrs={"inputmode": "url"})`, so the browser sends any text and phones still show the URL keyboard;
- the server's checks stay as they are, so invalid URLs get the form's own error ("Enter a valid URL.") in place of the browser's popup;
- the edit page uses the same form, so the fix covers it too.

This adds to D8. Source: user, 2026-10-02, during the manual checks.

### During review

D27. (Q24, R5) The admin's resource form follows D8's scheme rule as well. `ResourceAdmin` gets `formfield_overrides = {models.URLField: {"assume_scheme": "https"}}`, so staff input without a scheme is stored with `https://` and Django's `RemovedInDjango60Warning` goes away. This adds to D8 and D20. Source: user (accepted default), 2026-10-02, during review.

## Acceptance criteria

- [x] AC1. A logged-in user can open a detail page for each of their own goals. It shows the goal's title. → step 2
- [x] AC2. From the goals list, the user can reach each goal's detail page. → step 3
- [x] AC3. Opening the detail page of another user's goal, or of a goal id that doesn't exist, gives 404. → step 2
- [x] AC4. A visitor who isn't logged in and opens a goal detail page is sent to the login page, and comes back to the detail page after logging in. → step 2
- [x] AC5. The goal detail page has a form for attaching a resource, with fields for URL, title and type. → step 5
- [x] AC6. The type offers exactly four choices: article, video, repo and doc. → step 5
- [x] AC7. Submitting the form with a valid URL, title and type stores one resource linked to that goal. After the submit, the resource appears on the goal's detail page. → step 5
- [x] AC8. Each resource on the detail page shows its title, links to its URL, and shows its type. → step 4
- [x] AC9. A URL that isn't a valid web address is rejected with an error on the form, and nothing is stored. → step 5
- [x] AC10. A missing URL is rejected with an error on the form, and nothing is stored. → step 5
- [x] AC11. A type outside the four choices is rejected with an error on the form, and nothing is stored. → step 5
- [x] AC12. A rejected submission keeps the values the user entered. → step 5
- [x] AC13. Posting a resource to another user's goal, or to a goal id that doesn't exist, gives 404 and stores nothing. → step 5
- [x] AC14. After a successful attach, reloading the page doesn't attach the resource a second time. → step 5
- [x] AC15. A confirmation message shows after a resource is attached. → step 5
- [x] AC16. A goal's detail page shows only that goal's resources, never another goal's. → step 4
- [x] AC17. A goal with no resources shows an empty-state message where the resources would be. → step 4
- [x] AC18. Deleting a goal deletes its resources. Deleting an account deletes the resources of its goals and leaves other users' resources alone. → step 1
- [x] AC19. Staff can see and manage resources in the admin. → step 1, step 14
- [x] AC20. The migration for the new model is committed (`makemigrations --check` finds nothing). → step 0
- [x] AC21. The detail page also shows the goal's description, status label, session count ("1 session"), total time ("1 h 30 min") and an Edit link. (from D1) → step 2, step 12
- [x] AC22. A missing title, or one longer than 200 characters, is rejected with an error on the form, and nothing is stored. (from D7) → step 5
- [x] AC23. A URL of 500 characters is accepted; one of 501 is rejected with an error on the form. (from D8) → step 5
- [x] AC24. A goal's resources are listed newest first. (from D5) → step 4
- [x] AC25. A resource can carry tags from the admin-maintained tag list. Tags are optional, and each resource shows its tags. (from D14) → step 6, step 11
- [x] AC26. Each resource link opens in a new tab, with `target="_blank"` and `rel="noopener noreferrer"`. (from D15) → step 4
- [x] AC27. The user can edit a resource's URL, title, type and tags on its own page. Saving goes back to the goal's detail page and shows "Resource updated.". (from D12) → step 7
- [x] AC28. The user can delete a resource from the detail page after a confirmation popup. With HTMX the row disappears and "Resource deleted." shows; without HTMX the browser goes back to the detail page. A GET deletes nothing. (from D13) → step 8
- [x] AC29. Opening or posting the edit page of another user's resource, or of a missing id, gives 404 and changes nothing. (from D18) → step 7
- [x] AC30. Deleting a goal from its detail page asks first, then lands on the goals list with "Goal deleted.". (from D19) → step 9
- [x] AC31. A URL typed without a scheme is stored with `https://`: `example.com/post` becomes `https://example.com/post`. (from D8) → step 5, step 10
- [x] AC32. The type field starts on the blank choice, so the user has to pick a type. (from D10) → step 5
- [x] AC33. The edit form has no goal field, and a resource stays on its goal when edited. (from D12) → step 7
- [x] AC34. The same URL can be attached twice to one goal. (from D9) → step 5
- [x] AC35. A visitor who isn't logged in and posts to the attach route is sent to the login page, and nothing is stored. (from D11) → step 5
- [x] AC36. A visitor who isn't logged in and opens a resource's edit page is sent to the login page. (from D12) → step 7
- [x] AC37. A visitor who isn't logged in and posts to a resource's delete route is sent to the login page, and nothing is deleted. (from D13) → step 8
- [x] AC38. Deleting another user's resource, or a missing id, gives 404 and deletes nothing. (from D18) → step 8
- [x] AC39. URLs with the schemes `http`, `https`, `ftp` and `ftps` are accepted. (from D8) → step 5

## Step 0: groundwork

No tests of its own. The 145 existing tests have to stay green.

**The model.** In `learning/models.py`, add `Resource` after `LearningSession`:

- the nested `Type(models.TextChoices)` from D6;
- `goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="resources")`;
- `url = models.URLField(max_length=500)`;
- `title = models.CharField(max_length=200)`;
- `type = models.CharField(max_length=20, choices=Type.choices)`, with no default (D10);
- `tags = models.ManyToManyField("core.Tag", blank=True)`;
- `created_at = models.DateTimeField(auto_now_add=True)`;
- `Meta.ordering = ("-created_at", "-pk")` (D5);
- `__str__` returns the title.

A comment cites D18: no user field, the owner is the goal's user.

**The migration.** Run `.venv/bin/python manage.py makemigrations learning`. It creates `learning/migrations/0002_resource.py`. That makes AC20 true, and the existing `test_ac24_migrations_are_committed` checks it (D24).

**Fixtures.** In `tests/conftest.py`, import `Resource` next to `Goal` and add:

- `resource(goal)`: `Resource.objects.create(goal=goal, url="https://docs.djangoproject.com/en/5.2/topics/db/models/", title="Django models docs", type="doc")`;
- `other_resource(other_goal)`: `Resource.objects.create(goal=other_goal, url="https://doc.rust-lang.org/book/", title="The Rust book", type="doc")`;
- `resource_data(**overrides)`: a plain function, like `goal_data`, returning `{"url": "https://www.youtube.com/watch?v=abc123", "title": "Django ORM talk", "type": "video"}` updated with the overrides.

**The local database.** Run `make migrate`. If it stops on a missing `SECRET_KEY`, ask the user to run it.

**Check.**

- `make test` passes the 145 existing tests, `test_ac24_migrations_are_committed` included.
- `make lint` is clean.

## Step 1: AC18, AC19, admin and cascade

**Test.** In `tests/test_admin.py`, import `Resource`, then add:

- `test_ac19_resource_registered_in_admin()`: assert `admin.site.is_registered(Resource)`.
- `test_ac19_staff_lists_resources(admin_client, resource)`: GET `reverse("admin:learning_resource_changelist")`. Assert 200 and that "Django models docs" is in the content. Mark it `@pytest.mark.django_db`, since the file has no `pytestmark`.

In `tests/test_learning_data.py`, import `Resource`, then add:

- `test_ac18_goal_delete_removes_resources(logged_in_client, goal, resource, other_resource)`: POST `reverse("goal_delete", args=[goal.pk])`. Assert no `Resource` with `goal__pk=goal.pk` remains, and that `other_resource` still exists.
- `test_ac18_account_delete_removes_resources(logged_in_client, user, resource, other_resource)`: POST `reverse("account_delete")`. Assert no `Resource` with `goal__user__pk=user.pk` remains, and that `other_resource` still exists.

**Red.** `test_ac19_resource_registered_in_admin` fails on the assertion: `is_registered` returns `False`. `test_ac19_staff_lists_resources` fails with `NoReverseMatch` for `admin:learning_resource_changelist`, since the admin has no URL for an unregistered model.

The two AC18 tests pass on their first run, because step 0's `ForeignKey` already cascades. The build log records them as green from the start. They pin the behaviour against later changes.

**Green.** In `learning/admin.py`, import `Resource` and add `@admin.register(Resource)` with `list_display = ("title", "goal", "type", "created_at")` (D20).

**Refactor.** None.

## Step 2: AC1, AC3, AC4, AC21, the goal detail page

**Test.** New file `tests/test_goal_detail.py`, with `pytestmark = pytest.mark.django_db`:

- `test_ac1_detail_page_shows_title(logged_in_client, goal)`: GET `reverse("goal_detail", args=[goal.pk])`. Assert 200 and "Learn Django" in the content.
- `test_ac21_detail_page_shows_goal_fields(logged_in_client, goal, session)`: GET the detail page. Assert the content contains "Models and views", "Planned", "1 session", "1 h 30 min" and `href="{reverse("goal_edit", args=[goal.pk])}"`.
- `test_ac3_other_users_goal_detail_is_404(logged_in_client, other_goal, target)`, parametrized over `target` in `["other", "missing"]` like `test_ac8_other_users_goal_is_404` (`tests/test_goals.py`): pk is `other_goal.pk` or `999999`. Assert 404.
- `test_ac4_detail_page_requires_login(client, goal, password)`: GET the detail URL. Assert 302 and `response.url == f"{reverse('login')}?next={url}"`. Then POST `{"username": "ada", "password": password}` to `response.url`. Assert 302 and `response.url == url`.

**Red.** All four fail with `NoReverseMatch` for `goal_detail`.

**Green.**

- `learning/urls.py`: `path("goals/<int:pk>/", views.goal_detail, name="goal_detail")`, before `goals/<int:pk>/edit/`.
- `learning/views.py`: add the helper `_goals_with_totals(user)` (D22), returning `Goal.objects.filter(user=user).annotate(session_count=Count("sessions"), total_minutes=Coalesce(Sum("sessions__duration_minutes"), 0))`. Add `goal_detail(request, pk)` with `@login_required`: `goal = get_object_or_404(_goals_with_totals(request.user), pk=pk)`, then render `learning/goal_detail.html` with `{"goal": goal}`.
- New `learning/templates/learning/goal_detail.html`. It extends `base.html` and loads `learning_extras`, inside `<section class="py-16 max-w-xl">` like `profile_detail.html`. It shows:
  - `<h1 class="text-3xl font-bold">{{ goal.title }}</h1>`;
  - the description in a `<p>` when it's not empty;
  - the status badge `<span class="px-2 border rounded">{{ goal.get_status_display }}</span>`;
  - `{{ goal.session_count }} session{{ goal.session_count|pluralize }}` and `{{ goal.total_minutes|duration }}`;
  - an Edit link to `goal_edit` and a "Back to goals" link to `goal_list`.

**Refactor.** `goal_list` uses `_goals_with_totals(request.user)` in place of its own `filter(...).annotate(...)` (`learning/views.py:24-27`). Its tests stay green.

## Step 3: AC2, the goal title links to the detail page

**Test.** In `tests/test_goal_detail.py`:

- `test_ac2_goal_list_links_to_detail(logged_in_client, goal)`: GET `reverse("goal_list")`. Assert that `re.search(rf'<a href="{reverse("goal_detail", args=[goal.pk])}"[^>]*>Learn Django</a>', content)` matches.

**Red.** It fails on the assertion: the title is a plain `<span>` (`_goal_list.html:22`).

**Green.** In `learning/templates/learning/_goal_list.html:22`, replace the span with `<a href="{% url 'goal_detail' goal.pk %}" class="font-bold underline">{{ goal.title }}</a>`.

**Refactor.** None.

## Step 4: AC8, AC16, AC17, AC24, AC26, the resource list on the detail page

**Test.** New file `tests/test_resources.py`, with `pytestmark = pytest.mark.django_db`. Each test GETs `reverse("goal_detail", args=[goal.pk])`.

- `test_ac8_resource_shows_title_link_and_type(logged_in_client, goal, resource)`: assert a match for `rf'<a href="{resource.url}"[^>]*>Django models docs</a>'`, and that `<span class="px-2 border rounded">Doc</span>` is in the content.
- `test_ac26_link_opens_in_new_tab(logged_in_client, goal, resource)`: find the `<a href="{resource.url}"[^>]*>` tag with `re.search`. Assert it matches and contains `target="_blank"` and `rel="noopener noreferrer"`.
- `test_ac16_only_this_goals_resources(logged_in_client, user, goal, resource, other_resource)`: create a second goal `Goal.objects.create(user=user, title="Learn SQL")` with `Resource.objects.create(goal=..., url="https://sqlbolt.com/", title="SQL tutorial", type="article")`. Assert "Django models docs" is in the content, and "SQL tutorial" and "The Rust book" aren't.
- `test_ac17_empty_state(logged_in_client, goal)`: assert "No resources yet." is in the content.
- `test_ac24_newest_first(logged_in_client, goal)`: create "Older talk" then "Newer talk" with `Resource.objects.create(goal=goal, url="https://example.com/1", title=..., type="video")`. Assert `content.index("Newer talk") < content.index("Older talk")`.

**Red.** All five fail on their assertions: the detail page lists no resources and has no empty state.

**Green.**

- `goal_detail` adds `"resources": goal.resources.all()` to the context.
- `goal_detail.html` gets a `<h2 class="mt-8 text-xl font-bold">Resources</h2>` and a `<ul class="mt-2 space-y-2">`. Each resource is `<li id="resource-{{ r.pk }}" class="p-4 bg-white border rounded">` with:
  - `<a href="{{ r.url }}" target="_blank" rel="noopener noreferrer" class="font-bold underline">{{ r.title }}</a>`;
  - `<span class="px-2 border rounded">{{ r.get_type_display }}</span>`.
- `{% empty %}` gives `<li class="text-gray-600">No resources yet.</li>`.

**Refactor.** None.

## Step 5: AC5, AC6, AC7, AC9–AC15, AC22, AC23, AC31, AC32, AC34, AC35, AC39, attaching a resource

**Test.** In `tests/test_resources.py`, import `resource_data` from `conftest`. Let `url = reverse("resource_create", args=[goal.pk])`.

The form on the page:

- `test_ac5_detail_has_attach_form(logged_in_client, goal)`: GET the detail page. Assert `{"url", "title", "type"} <= set(response.context["form"].fields)` and that `<form method="post" action="{url}"` is in the content.
- `test_ac6_type_has_four_choices(logged_in_client, goal)`: on the form from the detail page, assert `[v for v, _ in form.fields["type"].choices if v] == ["article", "video", "repo", "doc"]`.
- `test_ac32_type_starts_blank(logged_in_client, goal)`: assert `form.fields["type"].choices[0][0] == ""` and `not form["type"].value()`.

Attaching:

- `test_ac7_attach_stores_and_shows(logged_in_client, goal)`: GET `url` and assert 405. POST `resource_data()`. Assert 302 and `response.url == reverse("goal_detail", args=[goal.pk])`. Assert the single `Resource.objects.get(goal=goal)` has the URL, title and type from `resource_data`, and that the detail page contains "Django ORM talk".
- `test_ac14_reload_does_not_attach_twice(logged_in_client, goal)`: POST `resource_data()`, then GET `response.url` twice. Assert `Resource.objects.count() == 1`.
- `test_ac15_message_after_attach(logged_in_client, goal)`: POST `resource_data()` with `follow=True`. Assert "Resource added." is in the content.
- `test_ac34_same_url_twice(logged_in_client, goal)`: POST `resource_data()` twice. Assert `Resource.objects.filter(goal=goal).count() == 2`.
- `test_ac31_url_without_scheme_gets_https(logged_in_client, goal)`: POST `resource_data(url="example.com/post")`. Assert the stored URL is `"https://example.com/post"`.
- `test_ac39_url_schemes_accepted(logged_in_client, goal, value)`, parametrized over `"http://example.com/a"`, `"https://example.com/a"`, `"ftp://ftp.example.com/file.pdf"` and `"ftps://ftp.example.com/file.pdf"`: POST `resource_data(url=value)`. Assert 302 and that the stored URL equals `value`.

Rejections. Each posts and asserts 200, the field name in `response.context["form"].errors`, and `Resource.objects.count() == 0`:

- `test_ac9_invalid_url_is_rejected(logged_in_client, goal, value)`, parametrized over `"not a url"`, `"javascript:alert(1)"`, `"file:///etc/passwd"` and `"localhost:8000/docs"`, with field `url`;
- `test_ac10_missing_url_is_rejected`: `url=""`, field `url`;
- `test_ac11_unknown_type_is_rejected`: `type="podcast"`, field `type`;
- `test_ac22_title_rules(logged_in_client, goal, title)`, parametrized over `""` and `"x" * 201`, field `title`.

The other rejection and access tests:

- `test_ac23_url_length(logged_in_client, goal, extra, accepted)`, parametrized over `(480, True)` and `(481, False)`: POST `resource_data(url="https://example.com/" + "a" * extra)`, which is 500 or 501 characters. Assert `Resource.objects.count() == (1 if accepted else 0)`. For the rejected row, also assert `"url"` in the form errors.
- `test_ac12_rejected_submission_keeps_values(logged_in_client, goal)`: POST `resource_data(url="not a url", title="Kept title")`. Assert `value="not a url"` and `value="Kept title"` are in the content.
- `test_ac13_attach_to_other_goal_is_404(logged_in_client, other_goal, target)`, parametrized over `"other"` and `"missing"`: POST `resource_data()` to `reverse("resource_create", args=[pk])`. Assert 404 and `Resource.objects.count() == 0`.
- `test_ac35_attach_requires_login(client, goal)`: POST `resource_data()`. Assert 302, `response.url == f"{reverse('login')}?next={url}"`, and `Resource.objects.count() == 0`.

**Red.** Every test fails with `NoReverseMatch` for `resource_create`.

**Green.**

- `learning/forms.py`: `ResourceForm(forms.ModelForm)` with `url = forms.URLField(label="URL", max_length=500, assume_scheme="https")` (D8) and `Meta.model = Resource`, `Meta.fields = ("url", "title", "type")`.
- `learning/urls.py`: `path("goals/<int:pk>/resources/new/", views.resource_create, name="resource_create")`.
- `learning/views.py`: a helper `_render_goal_detail(request, goal, form)` renders `goal_detail.html` with `goal`, `resources` and `form`. `goal_detail` calls it with `ResourceForm()`. `resource_create(request, pk)` has `@login_required` above `@require_POST` (D21):
  - it looks the goal up with `get_object_or_404(_goals_with_totals(request.user), pk=pk)` and binds `ResourceForm(request.POST)`;
  - if valid: `form.instance.goal = goal`, `form.save()`, `messages.success(request, "Resource added.")`, `redirect("goal_detail", pk=goal.pk)`;
  - else: `_render_goal_detail(request, goal, form)`.
- `goal_detail.html`: below the list, `<h2>Add a resource</h2>` and `<form method="post" action="{% url 'resource_create' goal.pk %}" class="mt-4 space-y-4">` with `{% csrf_token %}`, `{{ form.as_p }}` and a "Add resource" submit button styled like `goal_form.html:9`.

**Refactor.** None.

## Step 6: AC25, tags on resources

**Test.** In `tests/test_resources.py`, import `Tag` from `core.models`:

- `test_ac25_tags_are_saved_and_shown(logged_in_client, goal)`: `tags = Tag.objects.filter(name__in=["Python", "Testing"])`. POST `resource_data(tags=[t.pk for t in tags])` to `resource_create`. Assert the stored resource's `set(tags.values_list("name", flat=True)) == {"Python", "Testing"}`, and that the detail page contains "Python" and "Testing".
- `test_ac25_tags_are_optional(logged_in_client, goal)`: POST `resource_data()`. Assert one resource is stored and `resource.tags.count() == 0`.

**Red.** `test_ac25_tags_are_saved_and_shown` fails on the assertion: the form has no `tags` field, so the posted tags are ignored and the set is empty.

`test_ac25_tags_are_optional` passes on its first run, because step 5 stores resources without tags. The build log records it as green from the start.

**Green.**

- `ResourceForm`: add `tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)`, as in `SessionForm`, and add `"tags"` to `Meta.fields`. `form.save()` saves the many-to-many with the default `commit=True`.
- `_render_goal_detail`: `goal.resources.prefetch_related("tags")`.
- `goal_detail.html`: each resource gets `<span>{% for tag in r.tags.all %}{{ tag.name }}{% if not forloop.last %}, {% endif %}{% endfor %}</span>`, as in `_session_list.html:8`.

**Refactor.** None.

## Step 7: AC27, AC29, AC33, AC36, editing a resource

**Test.** In `tests/test_resources.py`. Let `url = reverse("resource_edit", args=[resource.pk])`.

- `test_ac27_edit_resource(logged_in_client, goal, resource)`: assert the detail page contains `href="{url}"`. GET `url` and assert 200. POST `resource_data(url="https://example.com/new", title="Renamed", type="article", tags=[python.pk])`, where `python = Tag.objects.get(name="Python")`. Assert 302 and `response.url == reverse("goal_detail", args=[goal.pk])`. After `refresh_from_db()`, assert the URL, title, type and tag names. POST again with `follow=True` and assert "Resource updated." is in the content.
- `test_ac33_edit_form_has_no_goal_field(logged_in_client, user, goal, resource)`: GET `url` and assert `"goal" not in response.context["form"].fields`. Create `second = Goal.objects.create(user=user, title="Learn SQL")` and POST `resource_data(goal=second.pk)`. Assert `resource.goal == goal` after `refresh_from_db()`.
- `test_ac29_other_users_resource_edit_is_404(logged_in_client, other_resource, method, target)`, parametrized over `method` in `["get", "post"]` and `target` in `["other", "missing"]`: pk is `other_resource.pk` or `999999`. A POST sends `resource_data(title="Hijacked")`. Assert 404, and that `other_resource.title` is still "The Rust book".
- `test_ac36_edit_requires_login(client, resource)`: GET `url`. Assert 302 and `response.url == f"{reverse('login')}?next={url}"`.

**Red.** All four fail with `NoReverseMatch` for `resource_edit`.

**Green.**

- `learning/urls.py`: `path("resources/<int:pk>/edit/", views.resource_edit, name="resource_edit")`.
- `learning/views.py`: `resource_edit(request, pk)` with `@login_required`:
  - `resource = get_object_or_404(Resource, pk=pk, goal__user=request.user)` (D18) and `form = ResourceForm(request.POST or None, instance=resource)`;
  - if valid: save, `messages.success(request, "Resource updated.")`, `redirect("goal_detail", pk=resource.goal_id)`;
  - else: render `learning/resource_form.html` with `form` and `resource`.
- New `learning/templates/learning/resource_form.html`, shaped like `goal_form.html`: `<h1>Edit resource</h1>`, the POST form with `{{ form.as_p }}` and Save, and `<a href="{% url 'goal_detail' resource.goal_id %}">Back to goal</a>`.
- `goal_detail.html`: each resource gets `<a href="{% url 'resource_edit' r.pk %}" class="underline">Edit</a>`.

**Refactor.** None.

## Step 8: AC28, AC37, AC38, deleting a resource

**Test.** In `tests/test_resources.py`. Let `url = reverse("resource_delete", args=[resource.pk])`.

- `test_ac28_delete_resource(logged_in_client, goal, resource)`:
  - On the detail page, find `re.search(rf'<form[^>]+hx-post="{url}"[^>]*>', content)`. Assert it matches and contains `hx-confirm="Delete “Django models docs”?"`, `hx-target="closest li"` and `hx-swap="outerHTML"`.
  - GET `url` and assert 405, with the resource still there.
  - POST `url` and assert 302, `response.url == reverse("goal_detail", args=[goal.pk])`, and that the resource is gone.
- `test_ac28_htmx_delete_removes_row(logged_in_client, resource)`: POST `url` with `headers={"HX-Request": "true"}`. Assert 200, and that the content contains `hx-swap-oob="true"` and "Resource deleted." but not `id="resource-{resource.pk}"`. Assert the resource is gone.
- `test_ac38_other_users_resource_delete_is_404(logged_in_client, other_resource, target)`, parametrized over `"other"` and `"missing"`: POST. Assert 404 and that `other_resource` still exists.
- `test_ac37_delete_requires_login(client, resource)`: POST `url`. Assert 302 to `f"{reverse('login')}?next={url}"`, with the resource still there.

**Red.** All four fail with `NoReverseMatch` for `resource_delete`.

**Green.**

- `learning/urls.py`: `path("resources/<int:pk>/delete/", views.resource_delete, name="resource_delete")`.
- `learning/views.py`: `resource_delete(request, pk)` with `@login_required` above `@require_POST`:
  - `resource = get_object_or_404(Resource, pk=pk, goal__user=request.user)`, keep `goal_pk = resource.goal_id`, then delete;
  - `messages.success(request, "Resource deleted.")`;
  - `return _deleted_response(request, reverse("goal_detail", args=[goal_pk]))` (D13). Import `reverse` from `django.urls`.
- `goal_detail.html`: each resource gets the Delete form from D13, shaped like `_goal_list.html:28-34`, with `hx-confirm="Delete “{{ r.title }}”?"`.

**Refactor.** None.

## Step 9: AC30, deleting a goal from its detail page

**Test.** In `tests/test_goal_detail.py`. Let `url = reverse("goal_delete", args=[goal.pk])`.

- `test_ac30_delete_goal_from_detail(logged_in_client, goal, session)`:
  - On the detail page, find `re.search(rf'<form[^>]+hx-post="{url}"[^>]*>', content)`. Assert it matches and contains `hx-confirm="Delete “Learn Django” and its 1 session?"`. Assert the content contains `<input type="hidden" name="from" value="detail">`.
  - POST `{"from": "detail"}` to `url` with `headers={"HX-Request": "true"}`. Assert 200, `response["HX-Redirect"] == reverse("goal_list")`, and that the goal is gone.
  - GET `reverse("goal_list")` and assert "Goal deleted." is in the content.
- `test_ac30_delete_from_detail_without_htmx(logged_in_client, goal)`: POST `{"from": "detail"}` to `url`. Assert 302 and `response.url == reverse("goal_list")`.

**Red.** `test_ac30_delete_goal_from_detail` fails on the first assertion: the detail page has no form posting to `goal_delete`.

`test_ac30_delete_from_detail_without_htmx` passes on its first run, because `goal_delete` already redirects a plain POST to `goal_list` (#4 D9). The build log records it as green from the start.

**Green.**

- `goal_detail.html`: next to the Edit link, a `<form method="post" action="{% url 'goal_delete' goal.pk %}" class="inline">` with:
  - `hx-post` to the same URL;
  - `hx-confirm="Delete “{{ goal.title }}” and its {{ goal.session_count }} session{{ goal.session_count|pluralize }}?"`;
  - `{% csrf_token %}`, the hidden `from` input and the red Delete button from `_goal_list.html:33`.
- `learning/views.py`, in `goal_delete` after the message: `if request.htmx and request.POST.get("from") == "detail": return HttpResponseClientRedirect(reverse("goal_list"))` (D19). Import it from `django_htmx.http`.

`test_ac28_htmx_delete_removes_row` in `tests/test_goals.py` must stay green, since the list's delete sends no `from`.

**Refactor.** None.

## Step 10: rework M1, AC31, the browser lets a URL without a scheme through

**Test.** In `tests/test_resources.py`, next to `test_ac31_url_without_scheme_gets_https`:

- `test_ac31_url_field_is_plain_text(logged_in_client, goal)`: GET the detail page. Find `re.search(r'<input[^>]+name="url"[^>]*>', content)`. Assert it matches, contains `type="text"` and `inputmode="url"`, and doesn't contain `type="url"`.

**Red.** It fails on the assertion: the input is `type="url"` with no `inputmode`.

**Green.** In `learning/forms.py`, `ResourceForm.url` gets `widget=forms.TextInput(attrs={"inputmode": "url"})` (D26). A comment cites D26.

**Refactor.** None.

**Manual check.** Repeat Verification check 6.

## Step 11: rework R1, AC25, tags checked in the resource's own row

**Test.** In `tests/test_resources.py`, change `test_ac25_tags_are_saved_and_shown`: keep the stored-tags assertion, and replace the two whole-page checks with `re.search(rf'<li id="resource-{resource.pk}"[^>]*>(?:(?!</li>).)*Python, Testing', content, re.S)`. Assert it matches.

**Red.** None: the test is tightened, and the code already renders the tags in the row (`goal_detail.html:31`). Check it passes, then check it fails when the tag `<span>` is removed for one run, and put the span back. The build log records both runs.

**Green.** None.

**Refactor.** None.

## Step 12: rework R3, AC21, the session count checked in its own span

**Test.** In `tests/test_goal_detail.py`, in `test_ac21_detail_page_shows_goal_fields`, replace `assert "1 session" in content` with `assert "<span>1 session</span>" in content`.

**Red.** None: the test is tightened, and the span already exists (`goal_detail.html:12`). Check it passes, then check it fails when the span is removed for one run, and put the span back. The build log records both runs.

**Green.** None.

**Refactor.** None.

## Step 13: rework R4, the goal's Edit and Delete sit in a div

**Test.** In `tests/test_goal_detail.py`, add `test_r4_goal_actions_are_in_a_div(logged_in_client, goal)`: GET the detail page. Assert `re.search(rf'<div class="mt-4 flex gap-4">\s*<a href="{reverse("goal_edit", args=[goal.pk])}"', content)` matches.

**Red.** It fails on the assertion: Edit and Delete are wrapped in `<p class="mt-4 flex gap-4">` (`goal_detail.html:15`).

**Green.** In `learning/templates/learning/goal_detail.html`, change that `<p>` and its closing `</p>` (lines 15 and 24) to `<div>` and `</div>`.

**Refactor.** None.

## Step 14: rework R5, AC19, the admin form assumes https

**Test.** In `tests/test_admin.py`, add `test_ac19_admin_url_without_scheme_gets_https(admin_client, goal)`, marked `@pytest.mark.django_db`: POST `{"goal": goal.pk, "url": "example.com/x", "title": "Admin link", "type": "doc"}` to `reverse("admin:learning_resource_add")`. Assert 302, and that `Resource.objects.get(title="Admin link").url == "https://example.com/x"`.

**Red.** It fails on the assertion: the admin stores `http://example.com/x`, because the model's form field assumes `http`.

**Green.** In `learning/admin.py`, import `models` from `django.db` and add `formfield_overrides = {models.URLField: {"assume_scheme": "https"}}` to `ResourceAdmin`, with a comment citing D27.

**Refactor.** None.

## Review

### Round 1, 2026-10-02

- R1. should-fix, `tests/test_resources.py:252`: AC25's test finds "Python" and "Testing" anywhere on the page, and the attach form's tag checkboxes always show them. → fixed in step 11 (auto)
- R2. should-fix, `guides/02`–`07-*.md`: changed by the build's mistaken repo-wide `ruff format`, outside the plan's Files. → fixed by the user, 2026-10-02 (`git checkout -- guides/`)
- R3. nit, `tests/test_goal_detail.py:25`: AC21's "1 session" check also matches the Delete popup text. → fixed in step 12
- R4. nit, `learning/templates/learning/goal_detail.html:15`: the goal's Delete form sits inside a `<p>`, which HTML doesn't allow, so Delete falls out of the row. → fixed in step 13
- R5. nit, `learning/admin.py:16`: the admin's URL field assumes `http` and warns. Q24 answered in D27. → fixed in step 14

### Round 2, 2026-10-02

- R6. nit, `tests/test_goal_detail.py:94`: step 13's test is named `test_r4_...`, not after an AC. → rejected by user, 2026-10-02 (R4 pinned no criterion, and `/review-tdd` names such rework tests `test_r<n>_...`)

## Files

**New:**

- `learning/migrations/0002_resource.py`: the `Resource` table and its tags table.
- `learning/templates/learning/goal_detail.html`: the detail page, the resource list and the attach form.
- `learning/templates/learning/resource_form.html`: the resource edit page.
- `tests/test_goal_detail.py`: AC1–AC4, AC21, AC30.
- `tests/test_resources.py`: AC5–AC17, AC22–AC29, AC31–AC39.

**Changed:**

- `learning/models.py`: `Resource`.
- `learning/admin.py`: `ResourceAdmin`.
- `learning/forms.py`: `ResourceForm`.
- `learning/urls.py`: `goal_detail`, `resource_create`, `resource_edit`, `resource_delete`.
- `learning/views.py`: `_goals_with_totals`, `_render_goal_detail`, `goal_detail`, `resource_create`, `resource_edit`, `resource_delete`; `goal_list` uses the helper; `goal_delete` gets the detail-page redirect.
- `learning/templates/learning/_goal_list.html`: the title links to the detail page.
- `tests/conftest.py`: `resource`, `other_resource`, `resource_data`.
- `tests/test_admin.py`: AC19.
- `tests/test_learning_data.py`: AC18.

**For reference:**

- `accounts/templates/accounts/profile_detail.html`: the detail page layout and the badge style.
- `learning/templates/learning/_session_list.html`: the tag list.
- `theme/templates/messages.html`: the out-of-band messages.

## Verification

After each step:

- `make test ARGS="-k <the step's test names>"` shows the new tests red for the reason in Red, then green after the change.
- `make test` stays green for the whole suite, 145 tests before the build.

At the end:

- `make test` and `make lint` pass. The project has no type-check or build command.
- `.venv/bin/python manage.py makemigrations --check --dry-run` reports no changes.

Manual checks, offered to the user at the end (D25). Run `make dev` and log in as a user with a goal:

1. **AC2.** On `/goals/`, click a goal's title. The goal's detail page opens.
2. **AC26.** Attach a resource, then click its title. The link opens in a new tab, and the app's tab stays on the detail page.
3. **AC32.** On the detail page, the Type select shows `---------` until a type is picked. Submitting without one shows an error.
4. **AC28.** Click Delete on a resource. The browser asks "Delete “<title>”?". Cancel leaves it. OK removes the row without a reload, and "Resource deleted." appears.
5. **AC30.** Click Delete on the goal on its detail page. The browser asks "Delete “<title>” and its N sessions?". OK lands on `/goals/` with "Goal deleted.", and the goal is gone.
6. **AC31.** Attach `example.com/post`. The link points to `https://example.com/post`.
