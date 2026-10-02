# Build log: plans/feature-resource-library-for-attaching-reference-material-to-goals-plan.md

## 2026-10-02

- Baseline: make test … 145 passed
- Step 0: makemigrations learning … created 0002_resource.py; make migrate … applied
- Step 0 check: make test … 145 passed (test_ac24_migrations_are_committed included); make lint … clean
- Step 1 red: make test ARGS="-k 'test_ac19 or test_ac18'" … test_ac19_resource_registered_in_admin failed on the assertion, test_ac19_staff_lists_resources on NoReverseMatch for admin:learning_resource_changelist; both new AC18 tests passed on first run, as planned
- Step 1 green: make test … 149 passed
- Step 2 red: make test ARGS="tests/test_goal_detail.py" … 5 failed, all on NoReverseMatch for goal_detail
- Step 2 green: make test … 154 passed; refactor (goal_list uses _goals_with_totals): make test … 154 passed
- Step 3 red: make test ARGS="-k test_ac2_goal_list_links_to_detail" … 1 failed on the planned assertion (re.search returned None)
- Step 3 green: make test … 155 passed
- Step 4 red: make test ARGS="tests/test_resources.py" … 5 failed: AC8, AC16, AC17, AC26 on the planned assertion; AC24 on ValueError from content.index, the same cause (no resources listed)
- Step 4 green: make test … 160 passed
- Step 5 red: make test ARGS="tests/test_resources.py" … 26 failed: 23 on NoReverseMatch for resource_create; AC5, AC6, AC32 on KeyError 'form' (the detail page has no form yet, read before the reverse)
- Step 5 green: make test … 186 passed
- Step 6 red: make test ARGS="-k test_ac25" … test_ac25_tags_are_saved_and_shown failed on the planned assertion (set() != {Python, Testing}); test_ac25_tags_are_optional passed on first run, as planned
- Step 6 green: make test … 188 passed
- Step 7 red: make test ARGS="-k 'test_ac27_edit_resource or test_ac33 or test_ac29_other_users_resource or test_ac36_edit'" … 7 failed, all on NoReverseMatch for resource_edit
- Step 7 green: make test … 195 passed
- Step 8 red: make test ARGS="-k 'test_ac28_delete_resource or test_ac28_htmx_delete_removes_row or test_ac38 or test_ac37'" … 5 failed, all on NoReverseMatch for resource_delete (test_goals.py's test_ac28_htmx_delete_removes_row matched the name and passed)
- Step 8 green: make test … 200 passed
- Step 9 red: make test ARGS="-k test_ac30_delete" … test_ac30_delete_goal_from_detail failed on the planned assertion (no form posting to goal_delete on the detail page); test_ac30_delete_from_detail_without_htmx passed on first run, as planned
- Step 9 green: make test … 202 passed
- Verify: make test … 202 passed; make lint … clean; makemigrations --check --dry-run … No changes detected
- Verify: ruff format --check learning tests … 4 files would be reformatted; a ruff format meant for those 4 ran with no paths and reformatted 10 files, 6 of them guides/*.md outside the plan. Restoring guides/ with git checkout was denied by the permission check, so it is left to the user. After: ruff format --check learning tests … 29 files already formatted; make test … 202 passed; make lint … clean
- Manual checks: the user confirmed checks 1-5; check 6 (AC31) failed, the browser blocks example.com/post with "Please enter a URL". User chose fix (a), recorded as D26; rework step 10 added, AC31 unticked.
- Step 10 red: make test ARGS="-k test_ac31_url_field_is_plain_text" … 1 failed on the planned assertion (the input is type="url")
- Step 10 green: make test … 203 passed; make lint … clean; ruff format --check on the 2 changed files … clean
- Manual check 6 (AC31) repeated after step 10: confirmed by the user. AC31 ticked.

## 2026-10-02, review round 1 rework

- Baseline: make test … 203 passed
- Step 11 red: none planned (tightened test). make test ARGS="-k test_ac25_tags_are_saved_and_shown" … 1 passed; with the tag span removed for one run … 1 failed; span restored … 1 passed
- Step 11 green: make test … 203 passed
- Step 12 red: none planned (tightened test). make test ARGS="-k test_ac21_detail_page_shows_goal_fields" … 1 passed; with the session-count span removed for one run … 1 failed; span restored
- Step 12 green: make test … 203 passed
- Step 13 red: make test ARGS="-k test_r4_goal_actions_are_in_a_div" … 1 failed on the planned assertion (the actions sit in a <p>)
- Step 13 green: make test … 204 passed
- Step 14 red: make test ARGS="-k test_ac19_admin_url_without_scheme_gets_https" … 1 failed on the planned assertion (stored http://example.com/x)
- Step 14 green: make test … 205 passed
- Verify: make test … 205 passed; make lint … 2 errors (RUF012 learning/admin.py:21, FURB167 tests/test_resources.py:255), fixed with a ClassVar annotation and re.DOTALL, then clean; makemigrations --check … No changes detected; ruff format --check learning tests … 29 files already formatted; make test … 205 passed
