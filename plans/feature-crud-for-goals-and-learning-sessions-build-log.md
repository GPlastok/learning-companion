# Build log: plans/feature-crud-for-goals-and-learning-sessions-plan.md

## 2026-10-02

- Baseline: make test … 64 passed, on feature/4-crud-for-goals-and-learning-sessions.
- Step 0: startapp learning, models, 0001_initial, stub filter, empty learning/urls.py, fixtures. make migrate OK; make test … 64 passed; make lint clean; makemigrations --check: No changes detected.
- Step 1 red: make test ARGS="-k test_ac23_account_delete_removes or test_ac24_migrations or test_ac41" … 2 failed (AC41, is_registered False), 2 passed (AC23, AC24, as planned)
- Step 1 green: make test … 68 passed
- Step 2 red: make test ARGS="tests/test_goals.py" … 6 failed, NoReverseMatch for goal_create (5) and goal_list (1)
- Step 2 green: make test … 74 passed
- Step 3 red: make test ARGS="-k test_ac4_edit or test_ac5_edit" … 2 failed, NoReverseMatch for goal_edit
- Step 3 green: make test … 76 passed
- Step 4 red: make test ARGS="-k test_ac6_delete_goal or test_ac8_other or test_ac27 or test_ac28" … 5 failed: 4 on NoReverseMatch for goal_delete, AC27 on its hx-confirm assertion (it checks the list before reversing goal_delete); 4 AC8 goal_edit rows passed, as planned
- Step 4 green: make test … 85 passed
- Step 5 red: make test ARGS="tests/test_sessions.py" … 6 failed, NoReverseMatch for session_create (5) and session_list (1)
- Step 5 green: make test … 91 passed
- Step 6 red: make test ARGS="-k test_ac16 or test_ac30 or test_ac31" … 4 failed, 7 passed (no_date, no_duration as planned): zero saved a session (302), negative hit the DB CHECK constraint, AC30 got a 302 for minutes=60 (TypeError on missing form context), AC31 on TIME_ZONE "UTC"
- Step 6 green: make test … 97 passed
- Step 7 red: make test ARGS="-k test_ac17 or test_ac32" … 2 failed, NoReverseMatch for session_edit (3 passed are ticket-3 test_ac17_cohort_* matched by -k)
- Step 7 green: make test … 99 passed
- Step 8 red: make test ARGS="-k test_ac18_delete_session or test_ac20_other or test_ac29" … 4 failed, NoReverseMatch for session_delete; 4 AC20 session_edit rows passed, as planned. Refactor: _deleted_response helper
- Step 8 green: make test … 107 passed
- Step 9 red: make test ARGS="-k test_ac9_filter or test_ac10_no or test_ac11_empty or test_ac37 or test_ac38" … 5 failed on the planned assertions (AC9 x3, AC11, AC38), AC10 and AC37 passed as planned
- Step 9 green: make test … 114 passed
- Step 10 red: make test ARGS="-k test_ac36 or test_ac21_no" … 6 failed: 4 filter rows on NotImplementedError from the stub, rows test on its assertion ("Sept. 30, 2026"), empty state on its assertion
- Step 10 green: make test … 120 passed
- Step 11 red: make test ARGS="-k test_ac35_goal" … 1 failed on the row assertion (no "Planned" label); newest-first already held. Test fix before green: toggle found by its text, since status links also carry order=oldest
- Step 11 green: make test … 121 passed
- Step 12 red: make test ARGS="-k test_ac33" … 1 failed on the planned assertion ("Docker notes" shown under ?goal=)
- Step 12 green: make test … 122 passed
- Step 13 red: make test ARGS="-k test_ac39" … 8 failed: 6 on ValueError from the test helper (no id="messages" in the page), 2 HTMX rows on assert id="messages" in ""
- Step 13 green: make test … 130 passed
- Step 14 red: make test ARGS="-k test_ac22_pages or test_ac40" … 1 failed (AC40, no Goals nav link); 8 AC22 rows passed as planned
- Step 14 green: make test … 139 passed
- Verify: make test … 139 passed.
- Verify: make lint … first 3 errors: RUF012 on SessionForm.Meta.widgets (date widget moved to __init__), I001 import order in tests/test_goals.py and tests/test_sessions.py (ruff --fix). Then: All checks passed.
- Verify: make format … reformatted the feature's files, and also the Python code blocks in 6 guides/*.md files that were unformatted before the build (from 0bfa9e5); the guides were restored with git checkout. ruff format --check: only those 6 guides would change.
- Verify: makemigrations --check --dry-run … No changes detected.

## 2026-10-02, review round 1 rework

- Baseline: make test … 139 passed.
- Step 15 red: make test ARGS="-k test_ac33" … 1 failed, ValueError "Field id expected a number but got ²", as planned
- Step 15 green: make test … 139 passed
- Step 16 red: None, test-only change. Check: with the session-count span removed from _goal_list.html the AC35 test failed (1 failed); with the span restored it passed
- Step 16 green: make test … 139 passed
- Step 17 red: make test ARGS="-k test_ac43" … 2 failed on the template assertion (only the partial rendered), as planned
- Step 17 green: make test … 141 passed
- Step 18 red: make test ARGS="-k test_ac42" … 3 failed: 25_hours and 24_hours_1_min on assert 302 == 200, huge on OverflowError from SQLite; exactly_24_hours passed, as planned
- Step 18 green: make test … 145 passed
- Verify: make test … 145 passed; make lint … All checks passed!; ruff format --check learning tests … 26 files already formatted; makemigrations --check --dry-run … No changes detected.
- Step 19 red: None, test-only change. Mutation check: removing hx-target or hx-swap from either Delete form, or hx-trigger from the session filter form, failed the extended AC28, AC29 or AC33 test; each attribute was restored
- Step 19 green: make test … 145 passed
- Verify (round 2 rework): make test … 145 passed; make lint … All checks passed!; ruff format --check learning tests … clean; makemigrations --check … No changes detected.

## 2026-10-02, manual check rework

- M1 reported by the user: Oldest first changes nothing.
- Step 20 red: make test ARGS="-k test_ac35_goal" … 1 failed, assert index("Newest goal") < index("Learn Django") (pk order), as planned
- Step 20 green: make test … 145 passed
- Verify: make test … 145 passed; make lint … All checks passed!; ruff format --check learning tests … clean; makemigrations --check … No changes detected.
