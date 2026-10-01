# Learning companion

A Django learning
companion, built ticket by ticket through the TDD pipeline below. Work comes only from GitHub issues: build what the current ticket asks for, nothing beyond it.

## Stack

Decided on 2026-10-01. Raise a change as a question with options; don't switch on your own.

- **Django.** Admin, ORM, migrations and auth come built in.
- **django-tailwind.** Tailwind without a separate frontend; Node runs only at build time (a two-stage Dockerfile later).
- **HTMX via django-htmx.** Partial page updates from server-rendered templates, no JS framework. The scaffold adds the script tag; the goals ticket is the first to use it.
- **pytest + pytest-django.**
- **venv + pip** with `requirements.txt` (runtime) and `requirements-dev.txt` (tests, ruff).
- **SQLite now, PostgreSQL later**, read from `DATABASE_URL`.
- **django-environ** for `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `OPENAI_API_KEY`. Only `SECRET_KEY` is required. The defaults are dev-friendly: `DATABASE_URL` falls back to SQLite at `db.sqlite3`, `DEBUG` to `True`, `OPENAI_API_KEY` to empty. These may need to change before production, and production must set `DEBUG=False`.
- **OpenAI Chat Completions, synchronous.**
- **Chart.js** for charts, added 2026-10-01 for the dashboard ticket (#7). Each chart sits above a plain table with the same numbers, so tests check the table and the page reads without JavaScript. Whether the script comes from a CDN or a vendored static file is decided when #7 is planned.
- **gunicorn + whitenoise** in the container, added 2026-10-01 for the containerization ticket. gunicorn runs the app through `learning_companion.wsgi` in place of `runserver`, which is for development only. whitenoise serves the static files (Tailwind CSS, HTMX, Chart.js) from Django when `DEBUG=False`, so the image needs no separate web server.
- **Tags as a `Tag` model (M2M)**, not `ArrayField`, so per-tag queries and counts work on SQLite and PostgreSQL alike.
- **Makefile** as the one command menu, for people and for the pipeline's permissions.
- **ruff** for lint (`ruff check .`) and format (`ruff format`).

## Commands

| Command                        | Does                                                                             |
| ------------------------------ | -------------------------------------------------------------------------------- |
| `make install`                 | create `.venv/` if missing, install both requirements files, install Tailwind (npm) |
| `make test`                    | run the whole pytest suite                                                       |
| `make test ARGS="-k test_ac3"` | run matching tests only (`ARGS` goes to pytest)                                  |
| `make lint`                    | `ruff check .`                                                                   |
| `make format`                  | `ruff format`                                                                    |
| `make dev`                     | start the dev server and the Tailwind watcher                                    |
| `make migrate`                 | apply migrations                                                                 |

## Tests

- Test functions are named after the acceptance criterion they cover: `test_ac14_prefixes_player_lines`.
- A criterion checked against a table of inputs is one test with `@pytest.mark.parametrize`.

## Pipeline

Every feature is a GitHub issue on GPlastok/learning-companion and goes through these
stages in order. The files in `plans/` are the state. Each stage reads what the previous
one wrote, so a stage can resume in a fresh session. `/manager-tdd` runs the stages for
you and moves the board card.

| #   | Skill                    | Writes                                                                          | Stops when                                          |
| --- | ------------------------ | ------------------------------------------------------------------------------- | --------------------------------------------------- |
| 1   | `/new-ticket`            | a GitHub issue, after you confirm the draft                                     | the issue exists; never starts the pipeline unasked |
| 2   | `/ticket <n>`            | nothing; hands the issue to `/refine`                                           | `/refine` is running                                |
| 3   | `/refine`                | `plans/feature-<slug>-refinement.md`                                            | the file is written, with numbered open questions   |
| 4   | `/plan-tdd-feature`      | `plans/feature-<slug>-plan.md`                                                  | the plan is written                                 |
| 5   | `/implement-tdd-feature` | tests, code, the plan's Progress and ticks, `plans/feature-<slug>-build-log.md` | the plan is built, or a human is needed             |
| 6   | `/review-tdd`            | the plan's Review section and rework steps                                      | findings are recorded                               |
| 7   | `/ship`                  | a commit of the staged changes                                                  | committed, or a test/lint failure                   |

Rules per stage:

1. **`/new-ticket`** drafts the issue from your words only and invents no criteria. It is
   the one skill that creates issues. `gh issue create` is an `ask` rule, so you approve
   the call too.
2. **`/ticket`** is read-only on GitHub. It copies the issue's criteria verbatim and calls
   `/refine`.
3. **`/refine`** surveys the repo with three Explore sub-agents (routes, data, tests).
   It writes only the refinement file and proposes no design. On an empty repo it records
   "not found" for each area.
4. **`/plan-tdd-feature`** asks the open questions (Q1, Q2, ...), records answers as
   decisions (D1, ...) and writes one red-green step per behaviour, each naming its ACs.
   It writes no code or tests. For ticket 1 its step 0 creates the Django project, the
   tooling and a first passing test.
5. **`/implement-tdd-feature`** builds the plan step by step: tests first, seen red for
   the planned reason, then the smallest green, then the whole suite. It only builds what
   the plan names and never installs anything the plan doesn't list. It stops on the
   default branch, a stale plan, a test that passes too early, or a plan/code mismatch.
   It lists manual checks at the end and doesn't commit. The `Stop` hook
   `check-plan-progress.sh` blocks once if code changed after the newest plan was last
   written, so Progress stays current.
6. **`/review-tdd`** runs a fresh sub-agent over the branch diff and the plan. It routes
   each finding (implement, plan, refine, user, follow-up) and writes only the plan. It
   never edits code, commits or moves cards.
7. **`/ship`** runs `make test` and `make lint`, stops at the first failure, then commits
   only what is staged. Only you can run it (`disable-model-invocation`). Pushing and the
   PR (`Closes #<n>`) are yours too.

Applies to every stage:

- Claude may not read or edit `.env` or `.env.*` (`deny` rules).
- `git push`, `gh pr create`, `gh pr comment`, `gh issue create`, `gh issue edit`,
  `gh issue comment` and `gh project item-edit` always ask first (`ask` rules).
- The `PreToolUse` hook `block-ai-attribution.sh` rejects any commit, PR, issue or comment
  that carries a `Co-Authored-By` trailer or a "Generated with Claude" line, and
  `settings.json` turns the default attribution off.
- `make test`, `make test ARGS=...`, `make lint`, `make format`, `git status`, `git diff`
  and `git log` run without a prompt.

## Board

GitHub project #1 "Learning Companion". Columns:

| Column      | Card is here when                                                                        |
| ----------- | ---------------------------------------------------------------------------------------- |
| Todo        | the issue exists, or review sent it back to `/refine`                                    |
| Refined     | the refinement exists, or review sent it back to `/plan-tdd-feature`                     |
| In Progress | the plan is being built, rework steps included                                           |
| Review      | the build is done and under review, or reviewed clean and waiting for `/ship` and the PR |
| Done        | the PR merged or the issue closed (GitHub's workflow moves it)                           |

Only `/manager-tdd` moves cards, and each move goes through `gh project item-edit`, which
you approve. No skill moves a card to Done. `/manager-tdd` with no argument picks the next
card: In Progress first, then Review, then the top of Refined, then the top of Todo. "Top"
is the card order `gh project item-list` returns, which matches the board as long as the
board view has no sort set.

When review is clean, `/manager-tdd` also ticks the issue's own criteria (the ones `/ticket`
copied) that the plan has ticked, through `gh issue edit`, which you approve. It only ticks,
never unticks, and leaves the refinement's added criteria out of the issue.
