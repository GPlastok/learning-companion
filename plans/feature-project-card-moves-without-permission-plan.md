# Project card moves without permission: TDD plan

## Context

`/manager-tdd` moves board cards and ticks the issue's criteria without a permission prompt. It moves a card when a stage finishes, and when a stage starts it checks the card's column and fixes it if it's wrong. It names every move in its output.

Refinement: [feature-project-card-moves-without-permission-refinement.md](feature-project-card-moves-without-permission-refinement.md). Source: #15.

Branch: `feature/15-project-card-moves-without-permission`.

This is a tooling change: `.claude/settings.json`, the `/manager-tdd` skill and CLAUDE.md. No Django code changes.

**In scope:**

- the permission rules for `gh project item-edit` and `gh issue edit`;
- when `/manager-tdd` moves cards, and how it names the moves;
- the wording in the skill and CLAUDE.md that says the user approves moves and edits.

**Not in scope:**

- the prompt for `gh issue create` and the `/new-ticket` draft step (D6);
- a pytest test comparing the settings with CLAUDE.md (D7).

## Progress

Plan written on 2026-10-02. Baseline: 64 tests pass.

Step 1 done: 64 tests pass, as before (no Python changes).

Step 2 done: 64 tests pass. The current-column note went into section 5's lookup (step 3 of that list), next to the item ID.

Step 3 done: 64 tests pass. Line numbers in section 5 sit 9 lines lower than the plan says, because step 2 added lines above.

Step 4 done: 64 tests pass. `CLAUDE.md:61` still says "you approve" for `gh issue create`, which keeps its prompt (D6).

Verification: `make test` 64 passed, `make lint` passed, `jq` parses `.claude/settings.json`.

Review round 1 on 2026-10-02: 1 rework step added (6), 2 findings routed to the plan (R2, R3).

Plan updated on 2026-10-02 for R2 and R3: rework step 7 added (D14), step 5.3 uses the skill's heredoc form (D15).

Step 6 done: 64 tests pass. Section 5 step 4 has "Card in Done: skip the move and say so."

Step 7 done: 64 tests pass. The re-read sits at the start of section 5 step 4, before all the skip checks, so it also covers "Card in Done" and "not on the board".

Verification: `make test` 64 passed, `make lint` passed, `jq` parses `.claude/settings.json`.

Built on 2026-10-02, manual checks pending: AC1, AC6.

Reviewed on 2026-10-02, round 2: no rework. R4 (plan wording) updated in step 2. Manual checks still pending: AC1, AC6.

AC6 confirmed by the user on 2026-10-02: `gh issue edit 15` in the heredoc form ran with no permission prompt, and #15's body came back unchanged. Manual checks still pending: AC1.

AC1 confirmed by the user on 2026-10-02: `/manager-tdd 15` moved card #15 from In Progress (where the user had put it) to Review with no permission prompt. The plan's example said Todo; the start column was In Progress. No manual checks pending.

## Decisions

D1. Of the board commands, only `gh project item-edit` needs to run without a prompt. The read commands (`gh project list`, `view`, `field-list`, `item-list`) stay as they are. Source: user, 2026-10-02.

D2. `gh issue edit` runs without a prompt too. This covers every issue edit, not only ticking. The skill's rule that `/manager-tdd` only ticks, never unticks, stays. Source: user, 2026-10-02.

D3. The rules go in the shared `.claude/settings.json`. The pipeline in `.claude/` is meant to be copied to other projects and adjusted there. Source: user, 2026-10-02.

D4. `/manager-tdd` names each move in its output. Source: user, 2026-10-02.

D5. The stage table stays as it is, but runs automatically. The card moves when a stage finishes. When a stage starts, `/manager-tdd` checks the card's column and moves it if it's wrong. Source: user, 2026-10-02.

D6. `gh issue create` keeps its `ask` rule, and `/new-ticket` keeps showing the draft and asking. Source: user, 2026-10-02.

D7. No pytest test for this ticket. This applies to #15 only. It isn't a pipeline rule, and features still get pytest tests. The build checks each step by reading the files (`grep`, `jq`), and the no-prompt criteria get a live check. Review reads the settings, CLAUDE.md and the skills for inconsistencies. Source: user, 2026-10-02.

D8. (Q1) How does the live check prove `gh issue edit` runs without a prompt, given #15 has no supplied criteria to tick? In a new session, write #15's body back unchanged with `gh issue edit 15 --body-file -`. Source: user, 2026-10-02.

D9. Both rules move from `ask` to `allow`, in the space form the file already uses (`Bash(gh project item-edit *)`, `Bash(gh issue edit *)`). This follows from D3, which puts the rule in the shared settings rather than only in the skill's `allowed-tools`. Source: plan.

D10. `.claude/hooks/block-ai-attribution.sh:9` keeps checking every `gh issue edit`. Nothing changes there. Source: code.

D11. With moves at the end of a stage, the table's "Card column" means where the card is while that stage runs. The "No refinement" row then reads Todo, not "Refined after it", and every other row stays as it is. Source: code (`.claude/skills/manager-tdd/SKILL.md:82-90`) and D5.

D12. `.claude/hooks/check-plan-progress.sh:23` ignores `.claude/` but counts `CLAUDE.md`. After step 4, the build updates Progress before it stops. Source: code.

D13. (Q2) Should the start check leave a card in Done alone? Yes: in section 5 step 4 of the skill, a card in Done is not moved, and the manager says so. Source: user, 2026-10-02, during review.

D14. (R2) The manager re-reads the card's column before each skip check. In section 5 of the skill, "once per run" covers only the project ID and the `Status` field with its options. The manager looks up the item ID per issue, and re-reads the card's status with `gh project item-list` just before each same-column check. This replaces the cached column that step 2 describes. Source: user, 2026-10-02, during review.

D15. (R3) The AC6 live check writes the body back with the heredoc form from the skill's section 6 (`gh issue edit 15 --body-file - <<'ISSUE_BODY_END'`), so it tests the command shape `/manager-tdd` uses. Source: user, 2026-10-02, during review.

## Acceptance criteria

- [x] AC1. When `/manager-tdd` moves a card to another column, no permission prompt appears. → step 5
- [x] AC2. When a stage finishes, the card moves to the column of the stage that comes next in `/manager-tdd`'s stage table: Refined after `/refine`, In Progress after `/plan-tdd-feature`, Review after `/implement-tdd-feature`. After `/review-tdd`, a clean review leaves it in Review; rework moves it to the column of the finding's route (In Progress, Refined or Todo). → step 2
- [x] AC3. When `/manager-tdd` starts a stage and the card isn't in that stage's column, it moves the card there before running the stage. → step 6
- [x] AC4. A card already in the right column isn't moved again. → step 7
- [x] AC5. Each move is named in `/manager-tdd`'s output (card, from column, to column). → step 3
- [x] AC6. When review is clean, `/manager-tdd` ticks the issue's criteria without a permission prompt, and still never unticks one. → step 5
- [x] AC7. `git push`, `gh pr create`, `gh pr comment`, `gh issue create` and `gh issue comment` still ask before running. → step 1
- [x] AC8. `/new-ticket` still shows the draft and asks before it creates an issue. → step 1
- [x] AC9. No skill moves a card to Done, with or without a prompt. → step 2
- [x] AC10. A failed move is still reported, and the run carries on. → step 2
- [x] AC11. `/ticket`, `/review-tdd` and the other skills still never move cards. → step 4
- [x] AC12. CLAUDE.md and the `/manager-tdd` skill no longer say the user approves each card move or the criteria edit, and CLAUDE.md's list of commands that run without a prompt matches the settings. → step 4

## Step 1: AC7, AC8, the permission rules

**Test.** Read checks on `.claude/settings.json` and `.claude/skills/new-ticket/SKILL.md`:

- `jq -r '.permissions.allow[]' .claude/settings.json` lists `Bash(gh project item-edit *)` and `Bash(gh issue edit *)`. This is the change itself.
- AC7: `jq -r '.permissions.ask[]' .claude/settings.json` lists exactly `Bash(gh issue comment *)`, `Bash(gh issue create *)`, `Bash(gh pr comment *)`, `Bash(gh pr create *)`, `Bash(git push *)` and `Bash(git push)`.
- AC8: `git diff main -- .claude/skills/new-ticket/` is empty, and `.claude/skills/new-ticket/SKILL.md` section 4 still says "Never skip this step".
- `jq . .claude/settings.json` parses without an error.

**Red.** The allow check fails: `allow` has only make and git rules, and both gh rules are in `ask` (lines 21 and 24). The AC7 and AC8 checks already pass. They guard against removing too much while editing.

**Green.** In `.claude/settings.json`, delete `Bash(gh issue edit *)` and `Bash(gh project item-edit *)` from `ask` and add both to `allow`.

**Refactor.** None.

## Step 2: AC2, AC3, AC4, AC9, AC10, when the card moves

**Test.** Read checks on `.claude/skills/manager-tdd/SKILL.md`:

- AC2, D11: the stage table's "No refinement" row has the column Todo. A sentence under the table says the column is where the card is while that stage runs. `grep -n "Refined after it"` finds nothing.
- AC2: section 3 says that when a stage finishes (the skill ran to its end without stopping for the user), the manager works out the next stage from the files and moves the card to that stage's column. When a skill stops for the user, the card doesn't move.
- AC3: section 3 says that before each stage, the manager compares the card's column with that stage's column and moves the card first if they differ.
- AC4: section 5 says the manager compares the card's current column with the target and skips `gh project item-edit` when they're the same. The card's status is re-read with `gh project item-list` just before each same-column check (D14, step 7).
- AC9, AC10: "Never move a card to Done" and "If a move fails, report it and carry on" are still in section 5.

**Red.** `grep -n "Refined after it" .claude/skills/manager-tdd/SKILL.md` finds line 84. Section 3 (lines 95-112) has no rule for moving at the end or checking at the start. Section 5 has no same-column check. The AC9 and AC10 rows already pass.

**Green.** Edit `.claude/skills/manager-tdd/SKILL.md`:

- the stage table row (line 84) and one sentence under the table;
- section 3: the finish-move and start-check rules;
- section 5: the same-column skip.

Leave lines 156-157 as they are.

**Refactor.** None.

## Step 3: AC5, naming each move

**Test.** A read check on `.claude/skills/manager-tdd/SKILL.md` section 5. After each move, it tells the manager to write one line with the card and both columns, for example `Card #15: Refined → In Progress.` The intro no longer says "say which move you're asking for".

**Red.** `grep -n "asking for" .claude/skills/manager-tdd/SKILL.md` finds line 139. Section 5 has no line format for a move.

**Green.** Rewrite the intro of section 5 (lines 136-139) and add the line format after the move command (lines 153-154). Drop "which the project's settings make the user approve" here too.

**Refactor.** None.

## Step 4: AC11, AC12, the wording about approval

**Test.** Read checks:

- AC12: `grep -n "approv" .claude/skills/manager-tdd/SKILL.md` finds no line about card moves or the criteria edit.
- AC12: in `CLAUDE.md`, the "always ask first" bullet doesn't list `gh issue edit` or `gh project item-edit`. The "run without a prompt" bullet lists both. Each bullet matches the `ask` and `allow` lists in `.claude/settings.json` one to one.
- AC12: the Board section no longer says "which you approve" for moves or for ticking.
- AC11: `.claude/skills/review-tdd/SKILL.md` (lines 4, 19, 190-191) and `.claude/skills/ticket/SKILL.md` (lines 4, 16-18) still say they never move cards, and `git diff main -- .claude/skills/review-tdd/ .claude/skills/ticket/` is empty.

**Red.** `grep -n "approv" .claude/skills/manager-tdd/SKILL.md` finds the description (line 4) and line 196. `grep -n "approve" CLAUDE.md` finds lines 110 and 116. CLAUDE.md lines 89-90 still list both commands as `ask`. The AC11 checks already pass.

**Green.**

- `.claude/skills/manager-tdd/SKILL.md` line 4: the description says moves and the criteria edit run without a prompt, and each move is named.
- Line 196: `gh issue edit` runs without a prompt.
- `CLAUDE.md` lines 89-90 and 94-95: move both commands from the "always ask first" bullet to the "run without a prompt" bullet.
- `CLAUDE.md` lines 109-110 and 116: say the moves and the ticking run without a prompt, and that `/manager-tdd` names each move.

Then update Progress (D12).

**Refactor.** None.

## Step 5: AC1, AC6, live check (manual)

D7: no pytest test for this. The user does the check, and the build lists it at the end.

1. Commit nothing yet. Start a new Claude Code session in the repo on this branch, so the changed `.claude/settings.json` is the one loaded.
2. AC1: run `/manager-tdd 15`. The plan says `Built on`, so its stage is review, and the card should be in Review (D11). The start check moves the card there from wherever it is. Then the review itself runs, which is the normal next stage anyway.
   Expected: no permission prompt for `gh project item-edit`, and a line like `Card #15: Todo → Review.` On the board, card #15 sits in Review.
3. AC6 (D8, D15): in the same session, ask Claude to run `gh issue view 15 --json body -q .body` and then write that body back unchanged in the heredoc form the skill uses:

   ```bash
   gh issue edit 15 --body-file - <<'ISSUE_BODY_END'
   <the body, unchanged>
   ISSUE_BODY_END
   ```

   Expected: no permission prompt for `gh issue edit` (the `gh issue view` call may still ask, and isn't part of this check). Running `gh issue view 15` again shows the same body.
4. AC7 spot check: ask Claude to run `git push --dry-run`. Expected: a permission prompt appears. Decline it.

## Step 6: rework R1, AC3, leave a card in Done alone

**Test.** A read check on `.claude/skills/manager-tdd/SKILL.md` section 5 step 4 (D7): it says that a card in Done is not moved, and that the manager says so. `grep -n "in Done" .claude/skills/manager-tdd/SKILL.md` finds that line in section 5.

**Red.** Section 5 step 4 skips only a missing column, a card not on the board and a card already in the target column. Nothing stops the start check from moving a card in Done back to Review when section 6 runs again after the PR merged.

**Green.** In `.claude/skills/manager-tdd/SKILL.md` section 5 step 4, add: "Card in Done: skip the move and say so."

**Refactor.** None.

## Step 7: rework R2, AC4, re-read the card's column before skipping

**Test.** Read checks on `.claude/skills/manager-tdd/SKILL.md` section 5 (D7, D14):

- The "once per run" lookup names the project ID and the `Status` field with its options, and not the card's item ID.
- A line says the manager looks up the item ID per issue.
- A line says the manager re-reads the card's status with `gh project item-list` just before each same-column check.
- `grep -n "update it after each move"` finds nothing.

**Red.** Section 5 step 3 reads "Look up, once per run: ... and the item ID of the issue's card ... Its `status` is the card's current column; update it after each move." The manager keeps both the item ID and the column for the whole run.

**Green.** In `.claude/skills/manager-tdd/SKILL.md` section 5, split step 3: once per run for the project ID and the `Status` field; per issue for the item ID. In step 4, before "The card already in the target column: skip the move", re-read the card's status with `gh project item-list`.

**Refactor.** None.

## Review

### Round 1, 2026-10-02

- R1. should-fix, `.claude/skills/manager-tdd/SKILL.md:105-106`: the start check moves a card from Done back to Review when `/manager-tdd` runs again on a finished feature after the PR merged. Q2, answered as D13. → fixed in step 6
- R2. should-fix, `.claude/skills/manager-tdd/SKILL.md:157-163`: the same-column skip trusts a column read once per run, so a board edit made in between, or a second card started through "Offer the next card", goes unnoticed. Accepted fix from the user: re-read the card's status with `gh project item-list` just before each skip check, look the item up per issue, and keep "once per run" for the project and field IDs only. Step 2's AC4 wording changes with it. → plan updated 2026-10-02 (D14), fixed in step 7
- R3. nit, step 5.3: the AC6 live check runs `gh issue edit` freehand, not in the heredoc form the skill uses (`SKILL.md:203-206`). Accepted fix from the user: step 5.3 uses the same heredoc form. → plan updated 2026-10-02 (D15, step 5.3)

### Round 2, 2026-10-02

- R4. nit, plan step 2: its AC4 read check still described the cached column that D14 replaced. Accepted by the user. → plan updated 2026-10-02 (step 2's AC4 sentence)

## Files

Changed:

- `.claude/settings.json`: two rules move from `ask` to `allow` (step 1).
- `.claude/skills/manager-tdd/SKILL.md`: the stage table, the timing rules, the same-column skip, the move line and the approval wording (steps 2-4).
- `CLAUDE.md`: the permission bullets and the Board section (step 4).

For reference, unchanged:

- `.claude/skills/new-ticket/SKILL.md`, `.claude/skills/review-tdd/SKILL.md`, `.claude/skills/ticket/SKILL.md`: the AC8 and AC11 checks.
- `.claude/hooks/block-ai-attribution.sh`, `.claude/hooks/check-plan-progress.sh`: D10, D12.

## Verification

- After each step, run its read checks. They fail before the edit for the reason given under Red, and pass after it.
- After step 4, run `make test` and `make lint`. Both should pass as before, since no Python changes. `tests/test_docs.py` reads CLAUDE.md's Commands table, which this plan doesn't touch.
- Then `jq . .claude/settings.json` to confirm the file still parses.
- Step 5 is the user's live check. Run `/ship` only after it passes.
