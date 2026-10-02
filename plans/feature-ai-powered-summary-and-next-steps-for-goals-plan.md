# AI-powered summary and next steps for goals: TDD plan

## Context

A goal's detail page gets an AI sidebar. Its two actions, "Generate summary" and "Suggest next steps", each send one OpenAI Chat Completions request built from the goal's own data and show the reply in the sidebar. The page also starts listing the goal's sessions. Refinement: [feature-ai-powered-summary-and-next-steps-for-goals-refinement.md](feature-ai-powered-summary-and-next-steps-for-goals-refinement.md). Source: #6.

No feature branch yet. Create one before building, for example `feature/6-ai-powered-summary-and-next-steps-for-goals`. The build stops on `main`.

In scope: the two actions, the sidebar with a follow-up chat kept in the Django session, the sessions list on the detail page, and the tests' guard against real API calls.

Left for later:
- storing replies in the database (D14, #29);
- a credit limit (D16, #28);
- Markdown rendering (#27).

## Progress

Plan written on 2026-10-02. Nothing built yet.
Next: step 0.

## Decisions

The user answered Q1-Q20 on 2026-10-02.

### The API call

D1. (Q1) The app calls OpenAI through the official `openai` SDK, pinned as `openai==3.24.0` in `requirements.txt` (exact pin, scaffold D2). 3.24.0 was the latest release on 2026-10-02.

The SDK sends its requests through `httpx2` (its dependency `httpx2<3,>=2.12.0`, not `httpx`). Tests use `httpx2.MockTransport` from it. That's a transitive dependency, so nothing else is added to the requirements files. Source: user, 2026-10-02; the wheel's metadata, read 2026-10-02.

D2. (Q2) The model comes from a setting: `OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4o-mini")` in `learning_companion/settings.py`. The user supplies the key when the live check needs it. Source: user, 2026-10-02.

D3. (Q9) The client is built with a 30 s timeout and `max_retries=0`, so the user waits at most 30 s. Source: user, 2026-10-02.

D4. (Q14) All SDK use lives in a new `learning/ai.py`.

- `_client()` builds `OpenAI(api_key=settings.OPENAI_API_KEY, timeout=30.0, max_retries=0)`.
- `chat(messages) -> str` calls `_client()` outside its `try`, then `client.chat.completions.create(model=settings.OPENAI_MODEL, messages=messages)`. It returns `choices[0].message.content`, or `""` when that's `None`.
- Any `openai.OpenAIError` becomes `AIError(type(exc).__name__)`, raised `from exc`.
- Views call it as `ai.chat(...)` (`from learning import ai`), so tests can swap the module attribute.

Source: user, 2026-10-02.

### What goes into the request

D5. (Q3) "Recent" means the 5 newest sessions (by `-date, -pk`, the model's ordering) and the 5 newest resources (by `-created_at, -pk`). Both actions use the same window. The goal's session count and total time cover all its sessions. Source: user, 2026-10-02.

D6. (Q4) The request carries:

- the goal: title, description, status label, session count and total time, formatted with the `duration` filter (`1 h 30 min`);
- each session: date (`2026-09-30`), duration, tags, notes;
- each resource (summary only): title, type label, tags. The URL is left out.

The next-steps request has no resources: the ticket bases next steps on "the goal and its past sessions". Source: user, 2026-10-02; next steps without resources: the ticket text.

D7. (Q13) The prompts are English, short and encouraging, in the second person, and ask for plain text without Markdown. They are constants in `learning/ai.py`:

- `SUMMARY_PROMPT = "You are a friendly learning coach. Write a short progress summary of 3 to 4 sentences in English, in the second person, from the goal, sessions and resources below. Answer in plain text, without Markdown."`
- `NEXT_STEPS_PROMPT = "You are a friendly learning coach. Suggest 2 to 3 concrete next learning actions for the goal below, based on its past sessions. Answer in English plain text, without Markdown, as a numbered list with one action per line."`

Source: user, 2026-10-02.

D8. Each request is two messages: `{"role": "system", "content": <prompt>}` and `{"role": "user", "content": <the goal context>}`. The context is built only from `goal` and its own `sessions` and `resources`, so no other goal's or user's data can enter it (AC4). Source: plan.

### The page

D9. (Q5) Each action is a POST form with a matching `hx-post`, like the Delete form (`goal_detail.html:17-23`).

- Routes: `goals/<int:pk>/summary/` named `goal_summary`, and `goals/<int:pk>/next-steps/` named `goal_next_steps`. Flat names, as in #4 D20.
- `@login_required` above `@require_POST` (#4 D26). A GET gets 405.
- With HTMX, the view returns `learning/_ai_result.html` and the form swaps it into `#ai-chat` (`hx-target="#ai-chat"`).
- Without HTMX, the view re-renders the whole detail page with the result, through `_render_goal_detail`, status 200.

POST because every click costs money and sends data out. Source: user, 2026-10-02.

D10. (Q17b) The AI panel is a collapsible sidebar: `<aside id="ai-panel">` holding `<details open>` with `<summary>AI coach</summary>`.

- On wide screens (`lg:`) it sits right of the page content in a three-column grid: content in two columns, the aside in one.
- On narrow screens it stacks below the content, so it covers nothing.
- `<details>` opens and closes without JavaScript. It starts open on every screen size; opening it only on wide screens would need JavaScript.

Source: user ("sidebar it is"), 2026-10-02; the layout: plan.

D11. (Q10) While a request runs, `hx-indicator="#ai-thinking"` shows `<p id="ai-thinking" class="htmx-indicator">Thinking…</p>`, and `hx-disabled-elt="find button"` disables the clicked button. The tests check the markup; seeing it is a manual check. Source: user, 2026-10-02.

D12. (Q16) The detail page lists the goal's sessions, under the actions and above Resources, with an `<h2>Sessions</h2>`.

- It reuses `learning/_session_list.html` as it is (#4 D13 row contents), so each row also shows the goal's title.
- Deleting a row with HTMX removes it in place. Without HTMX, `session_delete` redirects to the sessions list, as it does today.

This replaces #5 D1's "It doesn't list the goal's sessions". Source: user ("yes for UX reasons"), 2026-10-02; reuse: plan.

D13. (Q15) Replies are shown as escaped plain text. The summary goes through `linebreaksbr`, which escapes under autoescape and keeps line breaks. Markdown is #27. Source: user, 2026-10-02.

### Replies, messages and failures

D14. (Q6) Replies are not stored in the database. The user first chose browser storage, then dropped it because it brings in JavaScript. #29 adds storage with a model and a migration. Until then the chat lives in the Django session (D25). Source: user, 2026-10-02.

D15. (Q7) The next-steps reply becomes a list in `ai.parse_steps(text) -> list[str]`.

- It keeps lines that start with a number and `.` or `)`, as in `1. ` or `2) `, strips the number and the surrounding spaces, and keeps at most 3.
- The view shows the items as an `<ol>`.
- If no line matches, the view shows the whole reply as a paragraph, like a summary.

Source: user, 2026-10-02.

D16. (Q12) No usage limit in this ticket. The user wants any limit to count credit spent, not clicks. A follow-up ticket covers it if that's worth doing. Source: user, 2026-10-02.

D17. (Q8) With `OPENAI_API_KEY` empty, the buttons still show. Using one sends no request and shows "AI features aren't configured yet. Set OPENAI_API_KEY to use them." in the error style. Source: user, 2026-10-02.

D18. (Q9) Any `AIError` shows "The AI service didn't answer. Please try again later." in the result area, status 200.

- The error style is `<p class="p-4 bg-red-50 border border-red-300 rounded">`. `messages.html` stays green-only.
- `learning/views.py` logs `logger.warning("AI request failed: %s", exc)`, where `exc` carries the SDK error's class name (D4). The key is never logged. No `LOGGING` setting is added; Django's defaults apply.

Source: user, 2026-10-02.

D19. (Q11) A goal with no data:

- Summary with no sessions and no resources: no request, and the notice "Log a session or add a resource first, then ask for a summary." in `<p class="text-gray-600">`.
- Next steps with no sessions: the request is sent anyway, with the goal alone.

Source: user, 2026-10-02.

D20. A view checks in this order: login, then the owner-scoped lookup (404), then the empty key (D17), then the empty goal (D19), then the call. A foreign or missing goal is 404 even when the key is empty, as AC5 requires. Source: plan, from AC5 and AC8.

### Chat

D21. (Q17a) The AI panel becomes a real chat: after a summary or next steps, the user can type follow-up questions, and the conversation keeps its earlier turns. This goes beyond the ticket text; the user asked for it. Source: user, 2026-10-02.

D25. (Q18) The conversation lives in the Django session until #29 stores it.

- Key: `f"ai_chat_{goal.pk}"`, one conversation per goal. The `django_session` table already exists, so there's no migration.
- Value: a list of turns, `{"question": str, "reply": str, "steps": list[str]}`. `steps` is `parse_steps`'s result for next steps and `[]` otherwise.
- The two actions add a turn too, with the button text as the question: "Generate summary" or "Suggest next steps".
- The detail page renders the stored turns in `#ai-chat`, so the chat survives a reload. Logging out flushes the session and ends it.
- Only successful replies become turns. An error or a notice shows once and isn't stored.

Source: user ("b until the migration or storage"), 2026-10-02; the turn shape: plan.

D26. (Q19) Limits:

- a follow-up message is 1 to 1000 characters after stripping spaces;
- the session keeps the last 10 turns, and older ones are dropped when a new one is added;
- each follow-up request sends all kept turns.

The user may revise these later. Source: user (accepted default), 2026-10-02.

D27. Follow-ups post to `goals/<int:pk>/chat/`, named `goal_chat`, with the field `message`.

- The request is `ai.chat_messages(goal, turns, message)`: one system message, `CHAT_PROMPT` + a blank line + the summary context (goal, sessions, resources), then each kept turn as a user and an assistant message, then the new user message.
- `CHAT_PROMPT = "You are a friendly learning coach. Answer the user's questions about the goal below in a few sentences, in English plain text, without Markdown."`
- An empty message shows the notice "Type a question first." A longer one shows "A message can be at most 1000 characters." Neither sends a request.
- `goal_chat` follows the same rules as the two actions: login, 404 (D20), the empty key (D17), failures (D18), escaping (D13). It skips the empty-goal check (D19).

Source: plan, following D9 and D25.

D28. Each new turn is appended rather than replacing the panel. All three forms get `hx-swap="beforeend"` on `#ai-chat`, and the HTMX response holds only the new turn: the question, then the reply. Without HTMX, the whole page re-renders and shows every stored turn. The chat form also gets `hx-on::after-request="this.reset()"`, htmx's own attribute, so the textbox empties after sending. No script file is added. Source: plan.

D29. (Q20) A "Clear chat" button empties a goal's chat.

- Route: `goals/<int:pk>/chat/clear/`, named `goal_chat_clear`, `@login_required` above `@require_POST`. The goal is looked up owner-scoped, so another user's or a missing goal is 404.
- It removes `f"ai_chat_{goal.pk}"` from the session and sends no request to OpenAI.
- The button is a POST form with `hx-post`, `hx-confirm="Clear this chat?"`, `hx-target="#ai-chat"` and `hx-swap="innerHTML"`, following the delete forms (#4 D9).
- With HTMX, the response is an empty `HttpResponse("")`, so the panel empties in place. Without HTMX, it redirects to `goal_detail`.

Source: user ("add clear chat"), 2026-10-02; the mechanism: plan.

### Tests

D22. (Q14) Tests never reach OpenAI.

- `settings_test.py` sets `OPENAI_API_KEY = "test-key-not-real"` after its `from .settings import *`. It's an assignment, not `setdefault`, so a key exported in the shell is overridden.
- An autouse fixture `block_openai` in `tests/conftest.py` replaces `learning.ai._client` with a function that calls `pytest.fail(...)`. `pytest.fail` raises an exception outside the `Exception` hierarchy, so `chat`'s `except openai.OpenAIError` can't swallow it. The fixture returns the original `_client`, so the client tests can build the real one.
- View tests use a `fake_chat` fixture that replaces `learning.ai.chat`, records each `messages` list, and returns `fake_chat.reply` or raises `fake_chat.error`.
- `chat` itself is tested against `httpx2.MockTransport`: the test replaces `ai._client` with one that has `http_client=httpx2.Client(transport=...)`.

No new test dependency: `monkeypatch`, `caplog` and pytest-django's `settings` fixture are already available. Source: user, 2026-10-02.

D23. The no-JavaScript paths, the sidebar layout, the loading state and one real API call are manual checks (Verification). Automated tests cover every criterion, as in #4 D30 and #5 D25. Source: #5 D25.

D24. `.env.example` gets `OPENAI_MODEL=gpt-4o-mini` under `OPENAI_API_KEY`. Claude may not write `.env.*`, so the build lists the line and the user adds it (scaffold D10). Source: scaffold D10.

## Acceptance criteria

- [ ] AC1. The goal detail page has a "Generate summary" action and a "Suggest next steps" action. → step 6
- [ ] AC2. Using "Generate summary" sends one Chat Completions request whose content includes the goal and its recent sessions and resources, and the returned summary text is shown on the goal's detail page. → step 5
- [ ] AC3. Using "Suggest next steps" sends one Chat Completions request whose content includes the goal and its past sessions, and the reply is shown on the detail page as a list of 2-3 items. → step 6
- [ ] AC4. The request for one goal never contains another goal's sessions or resources, or another user's data. → step 3
- [ ] AC5. Using either action on another user's goal, or on a goal id that doesn't exist, gives 404 and sends no request. → step 6
- [ ] AC6. A visitor who isn't logged in and uses either action is sent to the login page, and no request is sent. → step 6
- [ ] AC7. The API key is read from `OPENAI_API_KEY` in the environment or `.env`; no key appears in the source code. → step 1
- [ ] AC8. With `OPENAI_API_KEY` empty, using either action sends no request and shows a message that the AI features aren't configured; the rest of the detail page still works. → step 8
- [ ] AC9. When the API call fails (network error, timeout, authentication error, rate limit, server error), the user sees an error message on the detail page instead of a server error, and the page still works. → step 9
- [ ] AC10. Model output is shown as text: HTML in the reply is escaped, not rendered. → step 6
- [ ] AC11. A goal with no sessions (and, for the summary, no resources) still gives a clear result: either a reply or a message, never a server error. → step 8
- [ ] AC12. The test suite never calls the real OpenAI API, whatever `OPENAI_API_KEY` is set to in the shell. → step 1
- [ ] AC13. The model comes from `OPENAI_MODEL`, default `gpt-4o-mini`, and `chat` sends it with the messages. (from D2) → step 1
- [ ] AC14. The summary request carries the goal's title, description, status, session count and total time, the 5 newest sessions (date, duration, tags, notes) and the 5 newest resources (title, type, tags, no URL). The next-steps request carries the same goal fields and sessions, and no resources. (from D5, D6) → step 3
- [ ] AC15. `parse_steps` turns a numbered reply into at most 3 items, and returns an empty list when no line is numbered. (from D15) → step 4
- [ ] AC16. With HTMX, either action returns only the result partial; without HTMX, it returns the whole detail page with the result; a GET gets 405. (from D9) → step 6
- [ ] AC17. The client uses the key from settings, a 30 s timeout and no retries. (from D3) → step 1
- [ ] AC18. Both action forms show "Thinking…" and disable their button while the request runs. (from D11) → step 6
- [ ] AC19. The detail page lists the goal's own sessions, newest first, with "No sessions yet." when there are none. (from D12) → step 7
- [ ] AC20. The AI panel is a collapsible sidebar (`<aside>` with `<details>`) that holds the actions and the result area. (from D10) → step 5
- [ ] AC21. After a reply, the user can send a follow-up question in the AI panel; the request carries the earlier turns, and the question and reply join the conversation. (from D21, D27) → step 11
- [ ] AC22. A follow-up message must be 1 to 1000 characters; an empty or longer one sends no request and shows a message. (from D26, D27) → step 11
- [ ] AC23. The summary prompt asks for plain text without Markdown; the next-steps prompt asks for 2 to 3 actions as a numbered list. (from D7) → step 3
- [ ] AC24. `chat` turns every SDK failure (401, 429, 500, a connection error, a timeout) into `AIError`, named after the SDK error's class. (from D4) → step 2
- [ ] AC25. A failed call is logged as a warning with the error's class name, never the key. (from D18) → step 9
- [ ] AC26. Each successful action adds its question and reply as a turn in the Django session for that goal, keeping the last 10 turns; the detail page shows them again after a reload, and a new turn is appended in the panel. (from D25, D26, D28) → step 10
- [ ] AC27. Follow-up messages follow the actions' rules: login, 404 for another user's or a missing goal, the empty key, the failure message, and escaped output, with no request where the actions send none. (from D27) → step 11
- [ ] AC28. "Clear chat" removes the goal's stored turns after a confirm popup, sends no request, and leaves other goals' chats alone; another user's or a missing goal gives 404. (from D29) → step 12

## Step 0: groundwork

**Dependency.** Add `openai==3.24.0` to `requirements.txt`, after `django-tailwind`, and run `make install`. `make test` stays green (205 passed).

**Stub module.** Create `learning/ai.py` with the real names, each raising `NotImplementedError`:

- `class AIError(Exception)` (complete, not a stub);
- `SUMMARY_PROMPT = ""`, `NEXT_STEPS_PROMPT = ""` and `CHAT_PROMPT = ""`;
- `_client()`, `chat(messages)`, `summary_messages(goal)`, `next_steps_messages(goal)`, `chat_messages(goal, turns, message)`, `parse_steps(text)`.

**Fixtures.** Add these to `tests/conftest.py`, with `import learning.ai` at the top:

- `block_openai` (autouse, D22): `original = learning.ai._client`; `monkeypatch.setattr(learning.ai, "_client", blocked)`, where `blocked()` calls `pytest.fail("A test reached the real OpenAI client. Use fake_chat or replace learning.ai._client.")`; returns `original`.
- `class FakeChat`, whose `__init__` sets `self.calls = []`, `self.reply = "You are doing well."` and `self.error = None` (instance attributes, so tests don't share calls). `__call__(messages)` appends to `calls`, raises `error` if set, else returns `reply`.
- `fake_chat(monkeypatch)`: `monkeypatch.setattr(learning.ai, "chat", FakeChat())` and returns it.

**Check.** `make test` green and `make lint` clean.

## Step 1: AC7, AC12, AC13, AC17, the client and the request

**Test.** In `tests/test_settings.py`, add `"OPENAI_MODEL": getattr(settings, "OPENAI_MODEL", None)` to `SCRIPT`. Then add:

- `test_ac13_openai_model_setting`, parametrized: no `OPENAI_MODEL` gives `"gpt-4o-mini"`; `OPENAI_MODEL="gpt-test"` gives `"gpt-test"`. Use `load_settings(tmp_path, SECRET_KEY="x", ...)`.
- `test_ac12_test_settings_override_shell_key`: `load_settings(tmp_path, DJANGO_SETTINGS_MODULE="learning_companion.settings_test", OPENAI_API_KEY="sk-from-shell")` gives `OPENAI_API_KEY == "test-key-not-real"`.

New file `tests/test_ai.py`. Its helpers:

- `MESSAGES = [{"role": "user", "content": "Hi"}]`.
- `completion(text)`: an `httpx2.Response(200, json=...)` holding a minimal chat completion: `{"id": "c1", "object": "chat.completion", "created": 0, "model": "gpt-test", "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": text}}]}`.
- `use_transport(monkeypatch, handler)`: replaces `ai._client` with `lambda: OpenAI(api_key=settings.OPENAI_API_KEY, base_url="https://api.test/v1", max_retries=0, http_client=httpx2.Client(transport=httpx2.MockTransport(handler)))`.

Its tests:

- `test_ac7_client_uses_key_from_settings(block_openai)`: `block_openai().api_key == "test-key-not-real"`.
- `test_ac17_client_timeout_and_no_retries(block_openai)`: the client's `timeout == 30.0` and `max_retries == 0`.
- `test_ac13_chat_sends_model_and_messages(monkeypatch, settings)`: `settings.OPENAI_MODEL = "gpt-test"`. The handler records `json.loads(request.content)` and the `Authorization` header, and returns `completion("Hello")`. Assert `chat(MESSAGES) == "Hello"`, the body's `model == "gpt-test"`, `messages == MESSAGES`, and the header is `"Bearer test-key-not-real"` (AC7).
- `test_ac12_unpatched_chat_fails_the_test`: `with pytest.raises(pytest.fail.Exception): ai.chat(MESSAGES)`.
- `test_ac7_no_api_key_in_source`: no `*.py` or `*.html` file under `accounts/`, `core/`, `learning/`, `learning_companion/` or `theme/templates/` matches `sk-[A-Za-z0-9_-]{16,}`.

The existing `test_ac5_reads_settings` and `test_ac15_defaults` already cover reading the key from the environment and `.env` (AC7).

**Red.**
- `test_ac13_openai_model_setting` fails on the assertion: the value is `None`.
- `test_ac12_test_settings_override_shell_key` fails: it gets `"sk-from-shell"`.
- The `test_ai.py` tests fail with `NotImplementedError` from the stubs.
- `test_ac7_no_api_key_in_source` passes from the start. It's a guard that holds before and after, not a red test.

**Green.**
- `learning_companion/settings.py`: `OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4o-mini")` under `OPENAI_API_KEY`.
- `learning_companion/settings_test.py`: `OPENAI_API_KEY = "test-key-not-real"` after the star import.
- `learning/ai.py`: `_client()` as in D4, and `chat()` that calls `_client()` and returns `response.choices[0].message.content or ""`, still without the `try`.

**Refactor.** None.

## Step 2: AC24, SDK failures become AIError

**Test.** In `tests/test_ai.py`, `test_ac24_chat_raises_ai_error`, parametrized over `(handler, name)`:

- `httpx2.Response(401, json={"error": {"message": "bad key"}})` → `"AuthenticationError"`;
- `httpx2.Response(429, json={"error": {"message": "slow down"}})` → `"RateLimitError"`;
- `httpx2.Response(500, json={"error": {"message": "boom"}})` → `"InternalServerError"`;
- a handler that raises `httpx2.ConnectError("down")` → `"APIConnectionError"`;
- a handler that raises `httpx2.ReadTimeout("slow")` → `"APITimeoutError"`.

Each row: `use_transport(...)`, then `with pytest.raises(ai.AIError) as info: ai.chat(MESSAGES)`, and `str(info.value) == name`.

**Red.** Fails: `chat` lets `openai.AuthenticationError` (and the others) through, so `pytest.raises(ai.AIError)` doesn't catch them.

**Green.** In `chat`, wrap the `create` call in `try` / `except openai.OpenAIError as exc: raise AIError(type(exc).__name__) from exc`. `_client()` stays outside the `try`.

**Refactor.** None.

## Step 3: AC4, AC14, AC23, the request messages

**Test.** In `tests/test_ai.py`, a helper `content(messages)` returns `messages[1]["content"]`. The tests:

- `test_ac14_summary_carries_goal_sessions_and_resources(goal, session, resource)`:
  - `messages[0] == {"role": "system", "content": ai.SUMMARY_PROMPT}` and `messages[1]["role"] == "user"`;
  - the content contains `"Learn Django"`, `"Models and views"`, `"Planned"`, `"1 h 30 min"`, `"2026-09-30"`, `"Read the ORM docs"`, `"Django models docs"` and `"Doc"`;
  - it doesn't contain `"docs.djangoproject.com"`.
- `test_ac14_window_is_five_newest(goal)`: create 6 sessions dated 2026-09-01 to 2026-09-06 with notes `"note 1"` to `"note 6"`, and 6 resources titled `"res 1"` to `"res 6"`, created in that order. The summary content has `"note 2"` to `"note 6"` and `"res 2"` to `"res 6"`, but not `"note 1"` or `"res 1"`. It still says `"6 sessions"`.
- `test_ac14_next_steps_has_sessions_not_resources(goal, session, resource)`: `messages[0]["content"] == ai.NEXT_STEPS_PROMPT`; the content has `"Learn Django"` and `"Read the ORM docs"`, but not `"Django models docs"`.
- `test_ac4_no_other_goals_data(goal, session, resource, other_goal, other_session, other_resource, user)`: also create the user's second goal `"Learn SQL"`, with a session whose notes are `"Joins"` and a resource titled `"SQL book"`. For both builders, the content has none of `"Learn Rust"`, `"Borrow checker"`, `"The Rust book"`, `"Learn SQL"`, `"Joins"` or `"SQL book"`.
- `test_ac23_prompts`: `"plain text" in ai.SUMMARY_PROMPT` and `"Markdown" in ai.SUMMARY_PROMPT`; `"2 to 3" in ai.NEXT_STEPS_PROMPT` and `"numbered list" in ai.NEXT_STEPS_PROMPT`.

**Red.**
- The builder tests fail with `NotImplementedError`.
- `test_ac23_prompts` fails on the assertion: the prompts are `""`.

**Green.** In `learning/ai.py`:

- set the two prompts to D7's text;
- `_goal_lines(goal)` gives `Goal: <title>`, `Description: <description>`, `Status: <label>`, and `Sessions so far: <n>, total time <duration>`. It computes `n` and the total itself, with `goal.sessions.aggregate(...)`, so it works on a plain or an annotated goal;
- `_session_lines(goal)` gives one line per session in `goal.sessions.prefetch_related("tags")[:5]`: `- 2026-09-30, 1 h 30 min, tags: <names or none>. Notes: <notes>`;
- `_resource_lines(goal)` does the same for `goal.resources.prefetch_related("tags")[:5]`: `- <title> (<type label>), tags: <names or none>`;
- `summary_messages(goal)` joins all three. `next_steps_messages(goal)` joins the goal and session lines. Each returns the two messages from D8.

Use `learning.templatetags.learning_extras.duration` for the times.

**Refactor.** None.

## Step 4: AC15, parse the next steps

**Test.** In `tests/test_ai.py`, `test_ac15_parse_steps`, parametrized over `(text, expected)`:

- `"1. Read the docs\n2. Build a model\n3. Write tests"` → the three texts;
- `"1) A\n2) B"` → `["A", "B"]`;
- `"Here you go:\n1. A\n2. B\n3. C\n4. D"` → `["A", "B", "C"]`;
- `"  1.   Spaced out  "` → `["Spaced out"]`;
- `"Just keep practising."` → `[]`.

**Red.** Fails with `NotImplementedError` from the stub.

**Green.** `parse_steps` uses `re.findall(r"^\s*\d+[.)]\s+(.+?)\s*$", text, re.MULTILINE)[:3]`.

**Refactor.** None.

## Step 5: AC2, AC20, the summary action in the sidebar

**Test.** New file `tests/test_goal_ai.py`, with `pytestmark = pytest.mark.django_db` and `HTMX = {"HX-Request": "true"}`:

- `test_ac2_summary_sends_one_request_and_shows_reply(logged_in_client, goal, session, resource, fake_chat)`:
  - set `fake_chat.reply = "You spent 1 h 30 min on Django."` and post to `reverse("goal_summary", args=[goal.pk])` with `headers=HTMX`;
  - expect status 200, `len(fake_chat.calls) == 1`, and the reply in the content;
  - `learning/_ai_result.html` is among `[t.name for t in response.templates]`;
  - the sent user content contains `"Learn Django"`, `"Read the ORM docs"` and `"Django models docs"`.
- `test_ac20_ai_panel_is_a_sidebar(logged_in_client, goal)`: on GET `goal_detail`, `re.search` finds `<aside id="ai-panel"`, `<details open`, `<summary[^>]*>AI coach</summary>` and `id="ai-chat"`, in that order, and the summary form's `hx-post` is inside the aside.

**Red.** Both tests fail with `NoReverseMatch` for `goal_summary`.

**Green.**

- `learning/urls.py`: `path("goals/<int:pk>/summary/", views.goal_summary, name="goal_summary")`.
- `learning/views.py`:
  - `from learning import ai`;
  - `_render_goal_detail(request, goal, form, ai_context=None)` adds `ai_context` to its context;
  - `_ai_response(request, goal, ai_context)` returns `render(request, "learning/_ai_result.html", ai_context)` for `request.htmx`, else `_render_goal_detail(request, goal, ResourceForm(), ai_context)`;
  - `goal_summary` (`@login_required`, `@require_POST`): `goal = get_object_or_404(_goals_with_totals(request.user), pk=pk)`, then `_ai_response(request, goal, {"ai_reply": ai.chat(ai.summary_messages(goal))})`.
- New `learning/templates/learning/_ai_result.html`: `ai_error` in the red block (D18), else `ai_notice` in `<p class="text-gray-600">`, else `ai_steps` as `<ol class="list-decimal pl-6">`, else `ai_reply` as `<p>{{ ai_reply|linebreaksbr }}</p>`.
- `learning/templates/learning/goal_detail.html`:
  - wrap the page in `<div class="lg:grid lg:grid-cols-3 lg:gap-8">`;
  - the existing `<section>` gets `lg:col-span-2`;
  - add `<aside id="ai-panel" class="py-16">` with `<details open class="p-4 bg-white border rounded">`, `<summary class="font-bold">AI coach</summary>`, the summary form, and `<div id="ai-chat" class="mt-4">{% include "learning/_ai_result.html" %}</div>`.
  - The form: `method="post"`, `action` and `hx-post` set to `{% url 'goal_summary' goal.pk %}`, `hx-target="#ai-chat"`, `{% csrf_token %}`, and the button `Generate summary` (`px-4 py-2 bg-black text-white rounded`).

The existing `test_r4_goal_actions_are_in_a_div` still has to pass, so leave the Edit/Delete `<div class="mt-4 flex gap-4">` as it is.

**Refactor.** None.

## Step 6: AC1, AC3, AC5, AC6, AC10, AC16, AC18, next steps and the rules for both actions

**Test.** In `tests/test_goal_ai.py`, `ROUTES = ["goal_summary", "goal_next_steps"]`. Parametrize over `ROUTES` where noted.

- `test_ac3_next_steps_shows_a_list(logged_in_client, goal, session, fake_chat)`:
  - reply `"1. Read the QuerySet docs\n2. Build a blog model\n3. Write a model test"`, posted with HTMX;
  - one call, whose user content has `"Read the ORM docs"`;
  - the content has `<ol` and exactly 3 `<li>`, the first `<li>Read the QuerySet docs</li>`.
- `test_ac3_unnumbered_reply_is_a_paragraph`: reply `"Keep practising."` gives `<p>Keep practising.</p>` and no `<ol`.
- `test_ac1_detail_page_has_both_actions(logged_in_client, goal)`: the GET page has a form with `hx-post` for each route, and the button texts `Generate summary` and `Suggest next steps`.
- `test_ac16_without_htmx_returns_whole_page` (over `ROUTES`): a post without HTMX gives 200, `learning/goal_detail.html` among the templates, `<aside id="ai-panel"` and the reply in the content.
- `test_ac16_get_is_405` (over `ROUTES`): a GET gives 405 and `fake_chat.calls == []`.
- `test_ac5_other_or_missing_goal_is_404` (over `ROUTES` × `target` in `["other", "missing"]`, as in `test_goal_detail.py:30-36`): 404 and no calls.
- `test_ac6_anonymous_goes_to_login(client, goal, fake_chat)` (over `ROUTES`): 302 to `f"{reverse('login')}?next={url}"` and no calls.
- `test_ac10_reply_html_is_escaped` (over `ROUTES`): reply `"1. <b>bold</b>\n2. <script>x</script>"` gives `&lt;b&gt;bold&lt;/b&gt;` and `&lt;script&gt;` in the content, and no `<b>bold</b>` or `<script>x</script>`.
- `test_ac18_forms_show_loading_state(logged_in_client, goal)` (over `ROUTES`): the form whose `hx-post` is the route also has `hx-indicator="#ai-thinking"` and `hx-disabled-elt="find button"`. The page has `<p id="ai-thinking" class="htmx-indicator`.

**Red.**
- Every `goal_next_steps` row and `test_ac1_detail_page_has_both_actions` fail with `NoReverseMatch` for `goal_next_steps`.
- `test_ac18`'s `goal_summary` row fails on the assertion: the form has no `hx-indicator`.
- The `goal_summary` rows of `test_ac16`, `test_ac5`, `test_ac6` and `test_ac10` already pass, because step 5 built that route.

**Green.**

- `learning/urls.py`: `path("goals/<int:pk>/next-steps/", views.goal_next_steps, name="goal_next_steps")`.
- `learning/views.py`: `goal_next_steps`, decorated and looked up like `goal_summary`. It runs `reply = ai.chat(ai.next_steps_messages(goal))` and `steps = ai.parse_steps(reply)`, then passes `{"ai_steps": steps}` if `steps`, else `{"ai_reply": reply}`, to `_ai_response`.
- `goal_detail.html`:
  - add the next-steps form beside the summary form, built the same way, with the button `Suggest next steps`;
  - give both forms `hx-indicator="#ai-thinking"` and `hx-disabled-elt="find button"`;
  - add `<p id="ai-thinking" class="htmx-indicator text-gray-600">Thinking…</p>` above `#ai-chat`.

**Refactor.** If the two forms differ only in route and label, move them into an `{% include %}` with `with url=... label=...`. Otherwise none.

## Step 7: AC19, the goal's sessions on the detail page

**Test.** In `tests/test_goal_detail.py`:

- `test_ac19_detail_page_lists_sessions(logged_in_client, goal, session, other_session)`:
  - add a second session on `goal`, dated 2026-09-20, with notes `"Older one"`;
  - the page has `<h2 class="mt-8 text-xl font-bold">Sessions</h2>`, `"30 Sep 2026"`, `"Read the ORM docs"` and `"Older one"`, with `"Read the ORM docs"` before `"Older one"`;
  - it has `reverse("session_edit", args=[session.pk])`, and not `"Borrow checker"`.
- `test_ac19_no_sessions_yet(logged_in_client, goal)`: the page has `"No sessions yet."`.

**Red.** Fails on the assertion: the page has no Sessions heading and no session rows.

**Green.**

- `_render_goal_detail` adds `"sessions": goal.sessions.select_related("goal").prefetch_related("tags")`.
- `goal_detail.html`, between the Edit/Delete div and the Resources heading, adds `<h2 class="mt-8 text-xl font-bold">Sessions</h2>` and `<div class="mt-2">{% include "learning/_session_list.html" %}</div>`.

**Refactor.** None.

## Step 8: AC8, AC11, no key and no data

**Test.** In `tests/test_goal_ai.py`:

- `test_ac8_empty_key_sends_nothing` (over `ROUTES`, with `settings`, `goal`, `session`, `resource` and `fake_chat`): set `settings.OPENAI_API_KEY = ""` and post with HTMX. Expect 200, `"AI features aren't configured yet. Set OPENAI_API_KEY to use them."` inside `<p class="p-4 bg-red-50`, and `fake_chat.calls == []`.
- `test_ac8_page_still_works_without_key(settings, logged_in_client, goal, resource)`: with the empty key, GET `goal_detail` gives 200 with `"Django models docs"` and `"Generate summary"`.
- `test_ac8_foreign_goal_is_404_without_key(settings, logged_in_client, other_goal, fake_chat)` (over `ROUTES`): 404 (D20).
- `test_ac11_summary_of_empty_goal(logged_in_client, goal, fake_chat)`: `"Log a session or add a resource first, then ask for a summary."` and no calls.
- `test_ac11_summary_with_only_a_resource_is_sent(logged_in_client, goal, resource, fake_chat)`: one call.
- `test_ac11_next_steps_of_empty_goal_is_sent(logged_in_client, goal, fake_chat)`: one call and the reply shown.

**Red.**
- `test_ac8_empty_key_sends_nothing` and `test_ac11_summary_of_empty_goal` fail on the assertion: one call is made and the message is missing.
- `test_ac8_page_still_works_without_key`, `test_ac8_foreign_goal_is_404_without_key` and the other two AC11 tests already pass. They pin behaviour that has to survive this step's change.

**Green.** In `learning/views.py`, add `NOT_CONFIGURED` and `EMPTY_SUMMARY` with D17 and D19's texts.

- Both views return `_ai_response(request, goal, {"ai_error": NOT_CONFIGURED})` when `not settings.OPENAI_API_KEY`, after the lookup.
- `goal_summary` then returns `{"ai_notice": EMPTY_SUMMARY}` when `not goal.sessions.exists() and not goal.resources.exists()`.

Import `django.conf.settings`.

**Refactor.** None.

## Step 9: AC9, AC25, a failed call

**Test.** In `tests/test_goal_ai.py`:

- `test_ac9_failure_shows_error` (over `ROUTES` × `htmx` in `[True, False]`): set `fake_chat.error = ai.AIError("RateLimitError")`. Expect status 200 and `"The AI service didn't answer. Please try again later."` inside `<p class="p-4 bg-red-50`. Without HTMX, the page also has `"Django models docs"` (the `resource` fixture), so the page still works.
- `test_ac25_failure_is_logged(logged_in_client, goal, session, fake_chat, caplog)`: with the same error and `caplog.set_level("WARNING", logger="learning.views")`, `"AI request failed: RateLimitError"` is in `caplog.text` and `"test-key-not-real"` is not.

**Red.** Fails: `AIError` reaches the test client, which re-raises it.

**Green.** In `learning/views.py`:

- add `logger = logging.getLogger(__name__)` and `AI_FAILED` with D18's text;
- in both views, wrap the `ai.chat(...)` call in `try` / `except ai.AIError as exc:` that runs `logger.warning("AI request failed: %s", exc)` and returns `_ai_response(request, goal, {"ai_error": AI_FAILED})`.

**Refactor.** If both views now repeat the key check, the lookup and the `try`, pull them into one helper `_ask_ai(request, pk, build, needs_data)`. Otherwise none.

## Step 10: AC26, the actions keep their turns in the session

**Test.** In `tests/test_goal_ai.py`, a helper `store_turns(client, goal, turns)` does `s = client.session; s[f"ai_chat_{goal.pk}"] = turns; s.save()`, and `turn(question, reply, steps=())` builds one turn dict. The tests:

- `test_ac26_actions_store_turns(logged_in_client, goal, session, fake_chat)`:
  - post `goal_summary` with reply `"Summary text"`, then `goal_next_steps` with reply `"1. A\n2. B"`;
  - `logged_in_client.session[f"ai_chat_{goal.pk}"]` equals `[turn("Generate summary", "Summary text"), turn("Suggest next steps", "1. A\n2. B", ["A", "B"])]`, with `steps` as lists.
- `test_ac26_detail_page_shows_stored_turns(logged_in_client, goal, user)`:
  - store those two turns for `goal`;
  - create the user's second goal `"Learn SQL"` and store `turn("Generate summary", "SQL reply")` for it;
  - GET `goal_detail` for `goal`: the part after `id="ai-chat"` has `"Summary text"` and `<li>A</li>`, and the page has no `"SQL reply"`.
- `test_ac26_keeps_last_ten_turns(logged_in_client, goal, session, fake_chat)`: store 10 turns with questions `"q0"` to `"q9"`, then post `goal_summary`. The stored list has 10 turns, the first `"q1"` and the last `"Generate summary"`.
- `test_ac26_errors_and_notices_are_not_stored(logged_in_client, goal, fake_chat)`: post `goal_summary` for the empty goal (a notice). Then set `fake_chat.error = ai.AIError("RateLimitError")` and post `goal_next_steps` (an error). After both, `f"ai_chat_{goal.pk}"` is still not in `logged_in_client.session`.
- `test_ac26_htmx_response_holds_only_the_new_turn(logged_in_client, goal, session, fake_chat)`: store `turn("Generate summary", "Old reply")`, then post `goal_summary` with HTMX and reply `"New reply"`. The content has `"Generate summary"` and `"New reply"`, and not `"Old reply"`.
- `test_ac26_forms_append` (over `ROUTES`): the form whose `hx-post` is the route has `hx-swap="beforeend"`.

**Red.**
- `test_ac26_actions_store_turns` and `test_ac26_keeps_last_ten_turns` fail with `KeyError`: the session has no `ai_chat_<pk>` key, or the list still has the old 10.
- `test_ac26_detail_page_shows_stored_turns` fails on the assertion: the page doesn't read the session.
- `test_ac26_forms_append` fails on the assertion.
- `test_ac26_errors_and_notices_are_not_stored` and `test_ac26_htmx_response_holds_only_the_new_turn` already pass. They pin behaviour the change has to keep.

**Green.** In `learning/views.py`:

- `_turns(request, goal)` returns `request.session.get(f"ai_chat_{goal.pk}", [])`;
- `_add_turn(request, goal, question, reply, steps)` assigns `request.session[key] = (_turns(request, goal) + [turn])[-10:]`. Reassigning the key marks the session as changed;
- after a successful reply, `goal_summary` calls `_add_turn(request, goal, "Generate summary", reply, [])` and passes `{"ai_question": "Generate summary", "ai_reply": reply}`. `goal_next_steps` does the same with `"Suggest next steps"` and `steps`, and passes `ai_steps` or `ai_reply` as before;
- `_ai_response` without HTMX passes only `ai_error` and `ai_notice` on to the page, because the stored turns already show the reply;
- `_render_goal_detail` adds `"chat": _turns(request, goal)`.

In the templates:

- `_ai_result.html` starts with `{% if ai_question %}<p class="mt-4 text-right text-gray-700">{{ ai_question }}</p>{% endif %}`, before its existing branches.
- In `goal_detail.html`, `#ai-chat` holds `{% for turn in chat %}{% include "learning/_ai_result.html" with ai_question=turn.question ai_reply=turn.reply ai_steps=turn.steps only %}{% endfor %}`, then `{% if ai_error or ai_notice %}{% include "learning/_ai_result.html" %}{% endif %}`. The `only` keeps a page-level `ai_error` out of the stored turns.
- Both action forms get `hx-swap="beforeend"`.

**Refactor.** None.

## Step 11: AC21, AC22, AC27, follow-up messages

**Test.** In `tests/test_ai.py`:

- `test_ac21_chat_messages(goal, session, resource)`: `ai.chat_messages(goal, [turn], "What next?")`, where `turn` is `{"question": "Generate summary", "reply": "Nice work.", "steps": []}`.
  - `messages[0]["role"] == "system"`, its content starts with `ai.CHAT_PROMPT` and contains `"Read the ORM docs"` and `"Django models docs"`;
  - `messages[1:]` equals `[{"role": "user", "content": "Generate summary"}, {"role": "assistant", "content": "Nice work."}, {"role": "user", "content": "What next?"}]`;
  - `"plain text" in ai.CHAT_PROMPT`.

In `tests/test_goal_ai.py`, with `CHAT = "goal_chat"`:

- `test_ac21_follow_up_joins_conversation(logged_in_client, goal, session, fake_chat)`:
  - store `turn("Generate summary", "Nice work.")`, then post `{"message": "  What next?  "}` with HTMX and reply `"Try forms."`;
  - one call. Its last message is `{"role": "user", "content": "What next?"}`, and it contains `{"role": "assistant", "content": "Nice work."}`;
  - the content has `"What next?"` and `"Try forms."`;
  - the stored list has 2 turns, the last `turn("What next?", "Try forms.")`.
- `test_ac21_detail_page_has_chat_form(logged_in_client, goal)`: the form with `hx-post` for `goal_chat` has `hx-target="#ai-chat"`, `hx-swap="beforeend"`, `hx-on::after-request="this.reset()"`, `hx-indicator="#ai-thinking"` and `hx-disabled-elt="find button"`. It holds `<textarea name="message"` with `maxlength="1000"` and the button `Send`.
- `test_ac22_message_length`, parametrized over `(message, text)`:
  - `""` → `"Type a question first."`;
  - `"   "` → `"Type a question first."`;
  - `"x" * 1001` → `"A message can be at most 1000 characters."`.

  Each row: no call, and nothing stored.
- `test_ac22_thousand_characters_is_sent`: `"x" * 1000` gives one call.
- `test_ac27_chat_rules`, one test per rule, as in steps 6, 8 and 9:
  - another user's or a missing goal gives 404 with no call;
  - anonymous gives the login redirect with `?next=`;
  - a GET gives 405;
  - the empty key gives `"AI features aren't configured yet. Set OPENAI_API_KEY to use them."` with no call;
  - `fake_chat.error = ai.AIError("APITimeoutError")` gives `"The AI service didn't answer. Please try again later."` and stores nothing;
  - reply `"<b>bold</b>"` and message `"<i>me</i>"` both come back escaped.

**Red.**
- `test_ac21_chat_messages` fails with `NotImplementedError` from the stub.
- `test_ac21_detail_page_has_chat_form` fails on the assertion, since the page has no chat form yet.
- The view tests fail with `NoReverseMatch` for `goal_chat`.

**Green.**

- `learning/ai.py`:
  - `CHAT_PROMPT` with D27's text;
  - `chat_messages` joins `CHAT_PROMPT`, a blank line and the summary context lines from step 3, then the turns and the message, as in D27.
- `learning/urls.py`: `path("goals/<int:pk>/chat/", views.goal_chat, name="goal_chat")`.
- `learning/views.py`: `goal_chat` (`@login_required`, `@require_POST`). It looks the goal up and checks the key as the actions do. Then:
  - `message = request.POST.get("message", "").strip()`;
  - an empty message gives the notice `EMPTY_MESSAGE`, and one over 1000 characters the notice `TOO_LONG`, both with D27's texts;
  - otherwise it runs `ai.chat(ai.chat_messages(goal, _turns(request, goal), message))` in the same `try` as step 9;
  - on success it calls `_add_turn(request, goal, message, reply, [])` and passes `{"ai_question": message, "ai_reply": reply}` to `_ai_response`.

  If step 9 made `_ask_ai`, route `goal_chat` through it.
- `goal_detail.html`: below `#ai-chat`, in the aside, add the chat form as in the test, with `{% csrf_token %}`, `<label for="ai-message">Ask a follow-up question</label>`, `<textarea id="ai-message" name="message" maxlength="1000" required rows="3" class="w-full border rounded">` and the `Send` button.

**Refactor.** None.

## Step 12: AC28, clear the chat

**Test.** In `tests/test_goal_ai.py`, with `CLEAR = "goal_chat_clear"`:

- `test_ac28_clear_chat_with_htmx(logged_in_client, goal, user, fake_chat)`:
  - store `turn("Generate summary", "Nice work.")` for `goal`;
  - create the user's second goal `"Learn SQL"` and store a turn for it too;
  - post to `goal_chat_clear` for `goal` with HTMX;
  - expect 200 with an empty body, `f"ai_chat_{goal.pk}"` gone from the session, the second goal's key still there, and `fake_chat.calls == []`.
- `test_ac28_clear_chat_without_htmx(logged_in_client, goal)`: store a turn and post without HTMX. Expect a 302 to `reverse("goal_detail", args=[goal.pk])`, and the detail page no longer shows `"Nice work."`.
- `test_ac28_clear_button(logged_in_client, goal)`: the page has a form with `hx-post` for `goal_chat_clear`, `hx-confirm="Clear this chat?"`, `hx-target="#ai-chat"` and `hx-swap="innerHTML"`, and the button `Clear chat`.
- `test_ac28_clear_rules`:
  - over `target` in `["other", "missing"]`: 404;
  - anonymous: the login redirect with `?next=`;
  - a GET: 405.

**Red.** Every test fails with `NoReverseMatch` for `goal_chat_clear`.

**Green.**

- `learning/urls.py`: `path("goals/<int:pk>/chat/clear/", views.goal_chat_clear, name="goal_chat_clear")`.
- `learning/views.py`: `goal_chat_clear` (`@login_required`, `@require_POST`). It runs `get_object_or_404(Goal, pk=pk, user=request.user)` and `request.session.pop(f"ai_chat_{goal.pk}", None)`. It returns `HttpResponse("")` for `request.htmx`, else `redirect("goal_detail", pk=goal.pk)`. Import `HttpResponse` from `django.http`.
- `goal_detail.html`: below the chat form, add the clear form as in the test, with `{% csrf_token %}` and the button `Clear chat` (`text-red-700 underline`).

**Refactor.** None.

## Files

New:

- `learning/ai.py`: the client, `chat`, the prompts, the message builders (`chat_messages` included), `parse_steps`, `AIError`.
- `learning/templates/learning/_ai_result.html`: one turn's question, then the reply, the list, the notice or the error.
- `tests/test_ai.py`: `chat`, its errors, the messages, `parse_steps`.
- `tests/test_goal_ai.py`: the three routes, the sidebar and the session turns.

Changed:

- `requirements.txt`: `openai==3.24.0`.
- `learning_companion/settings.py`: `OPENAI_MODEL`.
- `learning_companion/settings_test.py`: the fake key.
- `learning/urls.py`: `goal_summary`, `goal_next_steps`, `goal_chat`, `goal_chat_clear`.
- `learning/views.py`: the four views, `_ai_response`, `_turns`, `_add_turn`, `_render_goal_detail`'s `ai_context`, `sessions` and `chat`, the logger.
- `learning/templates/learning/goal_detail.html`: the grid, the sidebar with the stored turns and the chat form, the sessions list.
- `tests/conftest.py`: `block_openai`, `FakeChat`, `fake_chat`.
- `tests/test_settings.py`: `OPENAI_MODEL` in `SCRIPT`, the AC12 and AC13 tests.
- `tests/test_goal_detail.py`: the AC19 tests.

For reference:

- `learning/templates/learning/_session_list.html`: reused unchanged.
- `learning/templatetags/learning_extras.py`: `duration`.
- `.env.example`: the user adds `OPENAI_MODEL=gpt-4o-mini` (D24).

## Verification

After each new test, `make test ARGS="-k test_ac<n>"` shows it red for the reason in its step. After each Green, the whole `make test` is green. At the end, `make test` and `make lint` pass. The project has no type-check or build target.

Manual checks (D23), with `make dev`:

- M1. Sidebar layout (AC20). On a wide window the AI coach panel sits right of the goal. On a phone-width window it sits below Resources and covers nothing. Clicking "AI coach" closes and opens it.
- M2. Loading state (AC18). With a real key, click "Generate summary": "Thinking…" shows and the button is disabled until the reply appears.
- M3. A real call (AC2, AC3). The user puts their key in `.env`. "Generate summary" on a goal with sessions gives a short plain-text summary, and "Suggest next steps" a list of 2 or 3 items.
- M4. Without JavaScript (AC16). With JavaScript turned off in the browser, both buttons reload the detail page with the result in the sidebar.
- M5. No key (AC8). With `OPENAI_API_KEY` removed from `.env` and the server restarted, either button shows the "not configured" message in red.
- M6. Sessions on the page (AC19). The goal's sessions show under the actions. Deleting one asks first and removes the row.
- M7. The chat (AC21, AC26). With a real key, generate a summary, then ask "What should I focus on this week?". The answer refers to the goal and appears under the summary, and the textbox empties. Reload: both turns are still there. Open another goal: its panel is empty. Log out and back in: the chat is gone.
- M8. Clear chat (AC28). With a few turns in the panel, click "Clear chat". A popup asks "Clear this chat?". OK empties the panel, and a reload keeps it empty. Cancel changes nothing.
