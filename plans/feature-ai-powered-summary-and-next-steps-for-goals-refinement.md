# AI-powered summary and next steps for goals: refinement

## Context

On a goal's detail page, the user asks the OpenAI Chat Completions API for two things: a progress summary built from the goal's recent sessions and resources, and 2-3 concrete next learning actions built from the goal and its past sessions. The replies are shown on the page, the next steps as a short list. The API key is read from the environment, never hard-coded.

This is the first ticket that calls an external API. The `openai` package isn't installed yet, and no test mocks anything.

No feature branch yet; the current branch is `worktree-agent-ac70a2b46f0a2d928`.

Source: #6 (https://github.com/GPlastok/learning-companion/issues/6). The ticket has no acceptance criteria of its own, so all criteria below were written by refinement.

## Progress

Refinement done on 2026-10-02. Nothing planned or built yet. Next: the user answers the open questions, then a plan is written.

Plan written on 2026-10-02: plans/feature-ai-powered-summary-and-next-steps-for-goals-plan.md.

## Acceptance criteria

- [ ] The goal detail page has a "Generate summary" action and a "Suggest next steps" action.
- [ ] Using "Generate summary" sends one Chat Completions request whose content includes the goal and its recent sessions and resources, and the returned summary text is shown on the goal's detail page.
- [ ] Using "Suggest next steps" sends one Chat Completions request whose content includes the goal and its past sessions, and the reply is shown on the detail page as a list of 2-3 items.
- [ ] The request for one goal never contains another goal's sessions or resources, or another user's data.
- [ ] Using either action on another user's goal, or on a goal id that doesn't exist, gives 404 and sends no request.
- [ ] A visitor who isn't logged in and uses either action is sent to the login page, and no request is sent.
- [ ] The API key is read from `OPENAI_API_KEY` in the environment or `.env`; no key appears in the source code.
- [ ] With `OPENAI_API_KEY` empty, using either action sends no request and shows a message that the AI features aren't configured; the rest of the detail page still works.
- [ ] When the API call fails (network error, timeout, authentication error, rate limit, server error), the user sees an error message on the detail page instead of a server error, and the page still works.
- [ ] Model output is shown as text: HTML in the reply is escaped, not rendered.
- [ ] A goal with no sessions (and, for the summary, no resources) still gives a clear result: either a reply or a message, never a server error.
- [ ] The test suite never calls the real OpenAI API, whatever `OPENAI_API_KEY` is set to in the shell.

## Files and functions

**Routes**

- `learning_companion/urls.py:23-28`: `home`, `admin/`, then `include("accounts.urls")` and `include("learning.urls")` at `""`, with no namespaces.
- `learning/urls.py:5-22`: flat names. `goals/<int:pk>/` → `goal_detail` (l.8). `goals/<int:pk>/resources/new/` → `resource_create` (l.11-15) is the only route nested under a goal.

**Views** (`learning/views.py`)

- `_deleted_response(request, list_name)` (15-20): for HTMX, renders `messages.html` with `oob=True`; otherwise redirects.
- `_goals_with_totals(user)` (23-28): the user's goals annotated with `session_count` and `total_minutes` (#5 D22).
- `goal_list` (31-58): `@login_required`, `@vary_on_headers("HX-Request")`, returns `_goal_list.html` for HTMX that isn't a history restore.
- `_render_goal_detail(request, goal, form)` (61-67): context `goal`, `resources` (`goal.resources.prefetch_related("tags")`), `form`. Sessions are not passed.
- `goal_detail(request, pk)` (70-73): `@login_required`, GET only, `get_object_or_404(_goals_with_totals(request.user), pk=pk)`, no HTMX branch.
- `goal_delete` (99-109): returns `HttpResponseClientRedirect(reverse("goal_list"))` for an HTMX post with `from=detail` (#5 D19).
- `resource_create` (167-178): `@login_required` above `@require_POST`; an invalid post re-renders through `_render_goal_detail` with status 200.

**Templates**

- `learning/templates/learning/goal_detail.html`: title and description (6-9), status, session count and total time (10-14), the actions `<div class="mt-4 flex gap-4">` with Edit and the HTMX Delete form (15-24), Resources list with the empty state "No resources yet." (25-44), the add-resource form (45-50), "Back to goals" (51). It doesn't list sessions. `tests/test_goal_detail.py:94-102` pins the actions div's markup.
- `learning/templates/learning/_session_list.html:1-22`: the session rows, used only by the sessions list.
- `theme/templates/base.html`: loads `django_htmx` and `{% htmx_script %}` (1, 10), includes `messages.html` above the content (32).
- `theme/templates/messages.html:1-5`: `<div id="messages">`, `hx-swap-oob="true"` when `oob` is set. Every message uses one green success style; there is no error style.

**Other**

- `learning/templatetags/learning_extras.py:6-14`: the `duration` filter (minutes → "1 h 30 min").
- `learning_companion/settings.py:143`: `OPENAI_API_KEY = env("OPENAI_API_KEY", default="")`.
- No OpenAI client, HTTP client (`requests`, `httpx`, `urllib`), services module, logger, `hx-indicator`, `JsonResponse`, `StreamingHttpResponse` or async view exists in app code.

## Current data shapes

`learning/models.py:5-26` (Goal):

```python
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

`learning/models.py:29-42` (LearningSession):

```python
# No user field: the owner is the goal's user (D18).
goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="sessions")
date = models.DateField()
# Entered as hours and minutes, stored as whole minutes (D2).
duration_minutes = models.PositiveIntegerField()
notes = models.TextField(blank=True)
tags = models.ManyToManyField("core.Tag", blank=True)

class Meta:
    ordering = ("-date", "-pk")
```

No `created_at` field. Dates can't be in the future (`learning/forms.py:40-45`).

`learning/models.py:45-65` (Resource):

```python
goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="resources")
url = models.URLField(max_length=500)
title = models.CharField(max_length=200)
type = models.CharField(max_length=20, choices=Type.choices)  # article, video, repo, doc
tags = models.ManyToManyField("core.Tag", blank=True)
created_at = models.DateTimeField(auto_now_add=True)

class Meta:
    ordering = ("-created_at", "-pk")
```

`core/models.py:4-13`: `Tag(name=CharField(max_length=50, unique=True))`, ordered by name, 21 seeded tags.

"Recent": sessions already come newest date first and resources newest first. No query slices them or filters by date range.

No model stores an AI reply, summary or cache. No `CACHES` or `LOGGING` setting (Django's defaults apply).

Settings (`learning_companion/settings.py`):

```python
env = environ.Env()
environ.Env.read_env(env("ENV_FILE", default=str(BASE_DIR / ".env")))
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
```

No setting for the model name or a timeout. `settings_test.py:5-10` doesn't set `OPENAI_API_KEY`, so a key exported in the shell reaches the tests.

Packages: `requirements.txt` has `Django~=5.2.0`, `django-environ==0.14.0`, `django-htmx==1.29.0`, `django-tailwind==4.5.0`. `openai` is not in it and not in the main checkout's venv.

## Tests

- Runner: pytest 9.1.1 with pytest-django, `DJANGO_SETTINGS_MODULE = "learning_companion.settings_test"`, `testpaths = ["tests"]` (`pyproject.toml:6-8`).
- Commands: `make test`, `make test ARGS="-k test_ac3"`, `make lint` (`ruff check .`), `make format`. No type-check or build target, and no CI workflow.
- Status: 205 passed, ruff clean (run with the main checkout's venv; this worktree has no `.venv`, so `make test` fails here with `.venv/bin/python: No such file or directory`).
- Files live flat in `tests/`. Nearest: `test_goal_detail.py`, `test_resources.py`, `test_sessions.py`, `test_settings.py`.
- Fixtures in `tests/conftest.py`: `user`, `other_user`, `goal` ("Learn Django"), `other_goal`, `session` (2026-09-30, 90 min, with notes), `other_session`, `resource`, `other_resource`, `staff_user`, `logged_in_client`. Helpers `goal_data`, `session_data`, `resource_data` are imported directly (`from conftest import resource_data`).
- Typical view test: `logged_in_client`, `reverse(...)`, `response.content.decode()`, substring or `re.search` checks (`tests/test_goal_detail.py:18-27`). HTMX: `headers={"HX-Request": "true"}`, template names, `HX-Redirect`, `Vary` (`tests/test_goals.py:256-262, 352-354`, `tests/test_goal_detail.py:73-78`).
- 404 tests parametrize `target` over "other" and "missing" (`tests/test_goal_detail.py:30-36`); login tests check the `?next=` redirect (`:39-50`).
- `OPENAI_API_KEY` is already covered: read from the environment and env file, default `""` (`tests/test_settings.py:46-64, 90-95`), in a subprocess.
- `tests/test_docs.py:20-26` checks the Makefile targets against CLAUDE.md's Commands table.
- Gaps: nothing mocks anything. `monkeypatch`, `unittest.mock`, `settings`, `override_settings`, `responses` and `respx` are not used anywhere, and no mocking library is installed. Nothing covers AI, summaries or next steps.

## Patterns to follow

- The stack says "OpenAI Chat Completions, synchronous" (CLAUDE.md, Stack). A change of approach is raised as a question, not switched.
- The key is read through django-environ with an empty default (scaffold D8, `learning_companion/settings.py:143`). Claude may not read or write `.env` or `.env.*`; `.env.example` already lists `OPENAI_API_KEY=sk-your-key-here` (scaffold plan, lines 221-226) and the user edits it by hand (scaffold D10).
- New packages get exact `==` pins (scaffold D2, `requirements.txt`).
- Another user's goal or a missing id is 404 via an owner-scoped `get_object_or_404` (#4 D1, `learning/views.py:72`). Child rows filter on `goal__user` (#4 D18).
- Function-based views with `@login_required`; POST-only actions add `@require_POST` below it (#4 D26, `learning/views.py:167-168`).
- HTMX: partials start with `_`, the view returns the partial for `request.htmx` and not a history restore, with `@vary_on_headers("HX-Request")` (#4 D10, D33, `learning/views.py:32, 56-58`). Forms work with and without HTMX: `method="post"`, `action` and a matching `hx-post` (`goal_detail.html:17-23`).
- The detail page is rendered through one helper so other paths can re-render it (`_render_goal_detail`, `learning/views.py:61-67`).
- Feedback goes through `messages`, out of band for HTMX (`learning/views.py:19`, `theme/templates/messages.html:1`).
- Durations are shown with the `duration` filter (`learning_extras.py:6-14`).
- Styling: section heading `<h2 class="mt-8 text-xl font-bold">`, cards `p-4 bg-white border rounded`, empty state `<li class="text-gray-600">` (`goal_detail.html:25, 28, 42`).
- Comments cite decision ids (`learning/views.py:24`). D numbers repeat across plans, so cite the ticket too.
- Tests: `test_ac<n>_...` names, parametrize for tables, fixtures in `tests/conftest.py`, every criterion automated with manual checks offered at the end (#4 D30, #5 D25).

## Open questions

1. How does the app call OpenAI: the official `openai` Python SDK (a new pinned dependency) or plain HTTP? Which version is pinned?
2. Which model is used (for example `gpt-4o-mini`), and is it fixed in code or read from a setting such as `OPENAI_MODEL`?
3. What counts as "recent" for the summary: the last N sessions and resources, the last N days, or all of them? Does "past sessions" for next steps mean all sessions or the same window?
4. Which fields go into each request: goal title, description and status; session date, duration, notes and tags; resource title, type, URL and tags? Is the total time sent pre-computed (for "You spent 5 hours on Docker")?
5. How are the two actions triggered: buttons that post with HTMX and swap the reply into the page, or a normal post that reloads the detail page? Are they GET or POST?
6. Is the reply stored (on the goal, or in a new model with a timestamp) so it shows again after a reload, or is it shown once and lost on reload? If stored, is it replaced by the next one, and is the date shown?
7. How is the "2-3 next steps" reply turned into a list: ask the model for a numbered list and split the lines, ask for JSON (structured output), or something else? What happens if the reply has fewer than 2 or more than 3 items?
8. What happens when the key is empty: are the buttons hidden, disabled, or shown with a "not configured" message after clicking?
9. What does the user see on an API failure, and what are the texts? Is there a timeout, and how long? Is the failure logged?
10. While the request runs (it can take seconds), does the page show a loading state or disable the button?
11. What does the action do for a goal with no sessions and no resources: call the API anyway, or show a message without calling it?
12. Is there any limit on how often a user can trigger the actions (cost control), or none for now?
13. What language and tone should the prompts ask for, and does the prompt text live in code, a template, or a setting?
14. How do tests replace the API call: `monkeypatch` or `unittest.mock` on a small wrapper function, or a mocking library (a new dev dependency)? Should the test settings force `OPENAI_API_KEY` to a fake value so a shell key never reaches the tests?
15. Should the reply's Markdown (bold, lists) be rendered, or shown as plain escaped text?
16. Does the detail page start listing the goal's sessions as part of this ticket, or does it stay as it is (#5 D1 says it doesn't list them)?
