# Project card moves without permission: refinement

## Context

Let `/manager-tdd` move cards on the GitHub project board without a permission prompt each
time, when a pipeline stage that justifies the move starts or is complete, and say which
move it made. Today `gh project item-edit` is an `ask` rule, so the user approves every
move. This is a change to the Claude Code tooling (settings, skill text, CLAUDE.md), not
to the Django app. The pipeline in `.claude/` is meant to be reusable: copied into other
projects and adjusted there. Branch: `feature/15-project-card-moves-without-permission`.

Source: #15 (https://github.com/GPlastok/learning-companion/issues/15)

## Progress

Refinement done on 2026-10-02, updated the same day for #15 with the user's answers (see
"Answered" below). The survey was not re-run: nothing under `.claude/`, `CLAUDE.md` or
`tests/` changed in between. All open questions are answered. Nothing planned or built yet.
Next: a plan is written.

Plan written on 2026-10-02: plans/feature-project-card-moves-without-permission-plan.md.

Built on 2026-10-02, see plans/feature-project-card-moves-without-permission-plan.md.

Plan updated on 2026-10-02 for review round 1 (R2, R3).

Built on 2026-10-02 after review round 1, see plans/feature-project-card-moves-without-permission-plan.md.

## Acceptance criteria

- [ ] When `/manager-tdd` moves a card to another column, no permission prompt appears.
- [ ] When a stage finishes, the card moves to the column of the stage that comes next in
      `/manager-tdd`'s stage table: Refined after `/refine`, In Progress after
      `/plan-tdd-feature`, Review after `/implement-tdd-feature`. After `/review-tdd`, a
      clean review leaves it in Review; rework moves it to the column of the finding's
      route (In Progress, Refined or Todo).
- [ ] When `/manager-tdd` starts a stage and the card isn't in that stage's column, it
      moves the card there before running the stage.
- [ ] A card already in the right column isn't moved again.
- [ ] Each move is named in `/manager-tdd`'s output (card, from column, to column).
- [ ] When review is clean, `/manager-tdd` ticks the issue's criteria without a permission
      prompt, and still never unticks one.
- [ ] `git push`, `gh pr create`, `gh pr comment`, `gh issue create` and
      `gh issue comment` still ask before running.
- [ ] `/new-ticket` still shows the draft and asks before it creates an issue.
- [ ] No skill moves a card to Done, with or without a prompt.
- [ ] A failed move is still reported, and the run carries on.
- [ ] `/ticket`, `/review-tdd` and the other skills still never move cards.
- [ ] CLAUDE.md and the `/manager-tdd` skill no longer say the user approves each card
      move or the criteria edit, and CLAUDE.md's list of commands that run without a prompt matches the
      settings.

## Files and functions

Permission settings

- `.claude/settings.json:3-11`: `allow` list, only make and git rules; no gh rule.
- `.claude/settings.json:18-27`: `ask` list; `Bash(gh project item-edit *)` at line 24,
  `Bash(gh issue edit *)` at line 21.
- `.claude/settings.local.json`: not found. User-level `~/.claude/settings.json` has no gh
  rules.

Card-move flow

- `.claude/skills/manager-tdd/SKILL.md:4`: description says "with the user approving each
  move" and "with the user approving the edit" (criteria ticking).
- `.claude/skills/manager-tdd/SKILL.md:6`: `allowed-tools` lists `Bash(gh project
  list:*)`, `view:*`, `field-list:*`, `item-list:*`, `item-edit:*`, `gh issue view:*`,
  `gh issue edit:*` (colon form).
- `.claude/skills/manager-tdd/SKILL.md:82-90`: stage table with the card column per stage.
- `.claude/skills/manager-tdd/SKILL.md:134-157`: section 5 "Move the card": board lookup,
  id lookup once per run, the `gh project item-edit` call, never to Done, report a failed
  move and carry on. Lines 137-139: "which the project's settings make the user approve, so
  say which move you're asking for."
- `.claude/skills/manager-tdd/SKILL.md:188-197`: criteria ticking via `gh issue edit`;
  line 196 says it is an `ask` rule; line 197 points back to card-move failure handling.
- `.claude/skills/manager-tdd/SKILL.md:66-71`: the only in-skill confirmation is which card
  to start (`AskUserQuestion`). There is no confirmation before a move other than the
  permission prompt.
- `.claude/skills/review-tdd/SKILL.md:4,19,190-191` and `.claude/skills/ticket/SKILL.md:4,16-18`:
  say they never move cards.

Docs

- `CLAUDE.md:89-90`: "`gh project item-edit` always ask first (`ask` rules)", in one
  sentence with `gh issue edit` and the others.
- `CLAUDE.md:94-95`: commands that run without a prompt (make and git only).
- `CLAUDE.md:109-110`: "each move goes through `gh project item-edit`, which you approve.
  No skill moves a card to Done."
- `CLAUDE.md:116`: criteria ticking "through `gh issue edit`, which you approve".

Hooks

- `.claude/hooks/block-ai-attribution.sh:9`: matches `git commit` and
  `gh (pr|issue) (create|edit|comment)`; does not match `gh project`.
- `.claude/hooks/check-plan-progress.sh:23`: ignores changes under `plans/`, `.claude/` and
  `.github/`; changes to `CLAUDE.md` or `tests/` count as code.

## Current data shapes

`.claude/settings.json` permissions today:

```json
"allow": ["Bash(make test)", "Bash(make test ARGS=*)", "Bash(make lint)",
          "Bash(make format)", "Bash(git status)", "Bash(git diff *)", "Bash(git log *)"],
"ask": ["Bash(gh issue comment *)", "Bash(gh issue create *)", "Bash(gh issue edit *)",
        "Bash(gh pr comment *)", "Bash(gh pr create *)", "Bash(gh project item-edit *)",
        "Bash(git push *)", "Bash(git push)"]
```

The move command (`.claude/skills/manager-tdd/SKILL.md:153-154`):

```
gh project item-edit --id <item> --project-id <project> --field-id <status field> --single-select-option-id <option>
```

## Tests

- pytest + pytest-django, config in `pyproject.toml:6-8` (`testpaths = ["tests"]`). Full
  suite `make test`, one test `make test ARGS="-k test_ac3"`. Names follow
  `test_ac<n>_<behaviour>`.
- Nothing tests `.claude/settings.json`, permission rules or skill text. No CI
  (`.github/workflows` not found). `manager-tdd` has no evals.
- Closest pattern: `tests/test_docs.py:20-26`, `test_ac11_claude_md_commands_match_makefile`,
  reads `CLAUDE.md` and `Makefile` from `REPO_ROOT` and asserts they agree.
- Whether a prompt appears can only be seen in a live session: a manual check, as in
  `plans/feature-project-setup-dependencies-and-django-scaffold-plan.md:33` (D10).
- `make lint` (ruff) checks Python only; no JSON or markdown linter.

## Patterns to follow

- One commit that changes the rule in `settings.json`, the CLAUDE.md "Applies to every
  stage" bullets and the `/manager-tdd` SKILL.md text together, with a body line naming
  the rule change: commit `b1df5ab` (added `gh issue edit` to `ask`).
- settings.json rules use the space form (`Bash(gh project item-edit *)`, line 24); skill
  `allowed-tools` uses the colon form (`manager-tdd/SKILL.md:6`).
- Repo-file consistency tests read files from `REPO_ROOT` (`tests/test_docs.py:4`).
- CLAUDE.md: a stack or tooling change is raised as a question with options, not switched
  on its own; work comes from GitHub issues.
- No earlier plan has a decision on permissions, `ask` rules or the board.

## Open questions

None left.

### Answered (2026-10-02, in conversation)

- Of the board commands, only `gh project item-edit` needs to run without a prompt; the
  read commands are not the point.
- `gh issue edit` runs without a prompt too.
- The rule goes in the shared `.claude/settings.json`, because the pipeline is meant to be
  copied to other projects.
- `/manager-tdd` keeps naming each move in its output.
- A live check confirms there's no prompt for a real move, which also settles whether the
  skill's `allowed-tools` entry or the `ask` rule wins.
- The work gets a GitHub issue first: #15.
- `gh issue create` keeps its prompt, and `/new-ticket` keeps showing the draft and asking.
  Not part of this ticket.
- Timing: keep the stage table as it is, made automatic. The card moves when a stage
  finishes; when a stage starts, `/manager-tdd` checks the card's column and moves it if
  it's wrong.
- No pytest test for now. Consistency between `settings.json`, CLAUDE.md and the skills is
  checked by reading them (in review).
