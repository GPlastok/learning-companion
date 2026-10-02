# Build log: plans/feature-project-card-moves-without-permission-plan.md

## 2026-10-02

- Branch check: on `feature/15-project-card-moves-without-permission`. Staleness: no commits touch `.claude/` or `CLAUDE.md` since the plan.
- Baseline: `make test` … 64 passed.
- Step 1 red: `jq -r '.permissions.allow[]' .claude/settings.json | grep gh` … no gh rules in allow; both rules in `ask`. AC7 ask list and AC8 `git diff main -- .claude/skills/new-ticket/` (empty, "Never skip this step" at line 77) already pass, as planned.
- Step 1 green: `jq . .claude/settings.json` parses; allow lists `Bash(gh issue edit *)` and `Bash(gh project item-edit *)`; ask lists exactly the six planned rules; new-ticket diff empty. `make test` … 64 passed.
- Step 2 red: `grep -n "Refined after it" .claude/skills/manager-tdd/SKILL.md` … line 84; section 3 had no finish-move or start-check rule; section 5 had no same-column skip. AC9 ("Never move a card to Done") and AC10 ("report it and carry on") already present, as planned.
- Step 2 green: "Refined after it" gone, row 84 reads Todo, sentence under the table at line 92, start and finish rules at lines 105-109, current column at 159-160, same-column skip at 163, lines 167-168 unchanged. `make test` … 64 passed.
- Step 3 red: `grep -n "asking for" .claude/skills/manager-tdd/SKILL.md` … line 148 (the plan said 139; step 2 added lines above it); no line format for a move.
- Step 3 green: "asking for" gone; intro says "name each move you make"; line format `Card #15: Refined → In Progress.` after the move command. `make test` … 64 passed.
- Step 4 red: `grep -n "approv" .claude/skills/manager-tdd/SKILL.md` … lines 4 and 208 (plan: 196); `grep -n "approve" CLAUDE.md` … lines 61, 110, 116; CLAUDE.md:89-90 listed both commands as `ask`. Line 61 is `gh issue create`, which keeps its prompt (D6). AC11 `git diff main -- .claude/skills/review-tdd/ .claude/skills/ticket/` already empty, as planned.
- Step 4 green: no "approv" left in the manager-tdd skill; CLAUDE.md "approve" only at line 61 (D6); the "always ask first" bullet matches the six `ask` rules and the "run without a prompt" bullet matches the nine `allow` rules; review-tdd and ticket diffs empty. `make test` … 64 passed.
- Verification: `make test` … 64 passed; `make lint` … All checks passed!; `jq . .claude/settings.json` … parses.
- Step 5 (manual, AC1, AC6): listed for the user at the end of the run.

## 2026-10-02, rework after review round 1

- Branch check: on `feature/15-project-card-moves-without-permission`. Baseline: `make test` … 64 passed.
- Step 6 red: `grep -n "in Done" .claude/skills/manager-tdd/SKILL.md` … no match; section 5 step 4 had no Done rule.
- Step 6 green: `grep -n "in Done"` … line 163, "Card in Done: skip the move and say so." `make test` … 64 passed.
- Step 7 red: section 5 step 3 (lines 156-160) looked up the item ID "once per run" and kept the card's status, "update it after each move".
- Step 7 green: "once per run" (line 156) names only the project ID and the `Status` field; the item ID is looked up per issue; step 4 re-reads the status with `gh project item-list` just before each move; `grep -c "after each move"` … 0. `make test` … 64 passed.
- Verification: `make test` … 64 passed; `make lint` … All checks passed!; `jq . .claude/settings.json` … parses.
- Step 5 (manual, AC1, AC6): still pending, listed for the user.

## 2026-10-02, manual check AC6

- Step 5.3 (AC6): `gh issue view 15 --json body -q .body`, then `gh issue edit 15 --body-file - <<'ISSUE_BODY_END' ... ISSUE_BODY_END` with the body unchanged … edit succeeded; a second `gh issue view 15` diffed identical to the first.
- User confirmed: no permission prompt for `gh issue edit`. AC6 ticked. AC1 still pending.

## 2026-10-02, manual check AC1

- Step 5.2 (AC1): `/manager-tdd 15` re-read card #15's status with `gh project item-list` … In Progress (the user had moved it there); `gh project item-edit --id PVTI_lAHOBRcEDc4BlToBzg-E2Vc ... --single-select-option-id 7fc0c5eb` … succeeded; re-read … Review. Move line: `Card #15: In Progress → Review.`
- User confirmed: no permission prompt for `gh project item-edit`. AC1 ticked. No manual checks pending.
