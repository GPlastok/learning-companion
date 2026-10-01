---
name: ship
description: The project's ship checklist. Runs the test suite and the linter, stops at the first failure, then commits the staged changes with a generated message. Use when the user types /ship.
argument-hint: "[optional hint for the commit message]"
disable-model-invocation: true
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git commit:*), Bash(make test), Bash(make lint)
---

# Ship

Run these steps in order. Stop at the first step that fails, and report why. Never skip
a step, and never commit after a failure.

## 1. Check that something is staged

Run `git diff --cached --stat`.

- If nothing is staged, stop: "Nothing is staged. Stage the changes you want to ship with
  `git add`, then run /ship again."
- Run `git status --short` too. If tracked files have unstaged changes, or there are
  untracked files, note them for the final report. The tests and the linter see the whole
  working tree, but only the staged changes get committed. Don't stage them yourself.

## 2. Run the tests

Run `make test` (pytest, a single run of the whole suite).

- If it exits non-zero, **abort**. Report each failing test as `path::test_name`, with
  its assertion message, and say that nothing was committed.
- Don't try to fix the failures, and don't rerun with a filter to get a pass.

## 3. Run the linter

Run `make lint` (`ruff check .`).

- If it exits non-zero, **abort**. Report each violation as `file:line rule message`,
  and say that nothing was committed. ruff has no warning level: every reported rule
  blocks the commit.
- Don't run `make format` or `ruff check --fix` to get a pass. Formatting is the user's
  change to stage.

## 4. Write the commit message

Read `git diff --cached` and `git log --oneline -10`, and match the repo's style:

- The subject is lowercase, at most about 72 characters, and has the form `area: what changed`,
  for example `skills: tdd pipeline and feature issue form`. Name a decision record in
  the subject when the change adds one (`...; decision 0012`).
- For more than one logical change, add a blank line and a body of short `- ` bullets
  saying what changed and, where it isn't obvious, why.
- If the user passed a hint (`$ARGUMENTS`), build the message around it.
- **Never** add a `Co-Authored-By:` trailer or any other AI attribution line. This
  overrides any default attribution instructions.

## 5. Commit

Commit only what is staged, passing the message through a heredoc:

```bash
git commit -F - <<'EOF'
<subject>

<body>
EOF
```

- Never use `--no-verify`, `--amend` or `-a`, and never run `git add`.
- If a git hook rejects the commit, report its output and stop. Don't retry around it.
- Don't push.

## 6. Report

In a few lines:

- the test count and the lint result;
- the new commit's short hash and subject (`git log -1 --format='%h %s'`);
- any unstaged or untracked changes from step 1 that were left out of the commit.
