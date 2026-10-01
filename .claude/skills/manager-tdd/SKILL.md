---
name: manager-tdd
description: >-
  Runs a feature through the whole TDD pipeline: /ticket or /refine, /plan-tdd-feature, /implement-tdd-feature and /review-tdd, picking the next stage from the files in plans/ so it can resume at any point. Stops only where a human is needed (open questions, the build's own stops, manual checks, review findings that need a decision) and at the end, where the user runs /ship. Auto-fixes review findings that pass strict rules, for at most two review rounds. Moves the issue's card on the GitHub project board as the stages change, with the user approving each move. With no argument, picks the next card from the board, confirms it with the user, and offers the next one when a ticket finishes. Use when the user types /manager-tdd, or asks to run, drive or take a ticket or feature through the pipeline end to end.
argument-hint: "[issue number, or feature name; none picks the next card from the board]"
allowed-tools: Skill, Read, Glob, Grep, AskUserQuestion, Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git merge-base:*), Bash(git ls-files:*), Bash(git remote:*), Bash(git rev-parse:*), Bash(gh issue view:*), Bash(gh project list:*), Bash(gh project view:*), Bash(gh project field-list:*), Bash(gh project item-list:*), Bash(gh project item-edit:*)
---

# Manager

Take one feature from ticket to a reviewed build by running the pipeline's skills in order.
The manager doesn't plan, build or review anything itself: each skill does its own job and
keeps its own stops. What the manager adds is that the user doesn't have to type the next
command, and that the board shows where the feature is.

The pipeline: `/new-ticket` (optional), `/ticket`, `/refine`, `/plan-tdd-feature`,
`/implement-tdd-feature`, `/review-tdd`, then `/ship`, which only the user can run.

Never edit source, tests or plan files yourself, never commit or push, and never open a PR.
The skills you run edit what they own. If you notice yourself writing code, stop: that's a
step the build skill should run.

## 1. Find the feature

From `$ARGUMENTS`:

- **An issue number or URL** (`12`, `#12`, a GitHub issue URL): look for a refinement whose
  Context has `Source: #12` (Grep `plans/feature-*-refinement.md`). Found: that's the
  feature. Not found: the first stage is `/ticket 12`.
- **A feature name**: turn it into the kebab-case slug the other skills use and look for
  `plans/feature-<slug>-*.md`. Nothing there: the first stage is `/refine <feature name>`.
  Mention that `/new-ticket` can create an issue first if the user wants one on the board.
- **Nothing**: pick the next card from the board (section 1a). If there's no board, or no
  card qualifies, list the features in `plans/` with the stage each is at (section 2), and
  ask which one.

## 1a. Pick the next card from the board

Find the board as in section 5, steps 2 and 3 (the project the guidance files name, if
they name one). Read every card once:

```bash
gh project item-list <number> --owner <owner> --format json --limit 200
```

Each item has the card's `status` (its column) and its `content` (`type`, `number`,
`title`). Keep only items whose `content.type` is `Issue`: a draft or a pull request can't
go through `/ticket`. Take the columns in this order and pick the first card that
qualifies:

1. **In Progress**: a build was interrupted.
2. **Review**: a review or its rework was interrupted.
3. **Refined**, the top card.
4. **Todo**, the top card.

For In Progress and Review, work out each card's stage from the files (section 2) and skip
a card whose stage is done (reviewed clean). It's waiting for the user's `/ship` and PR,
not for the manager. Name the skipped cards in the pick message.

**Card order.** `gh project item-list` returns cards in the project's position order (the
API's default, `POSITION` ascending), and a board column shows its cards in that order
while the board view has no sort set. Inside a column, the first card in the output is
the top card. A view with its own sort shows a different order, which the output can't
reveal, so the user checks the pick against the board.

**Confirm before starting.** Show the pick: issue number and title, its column, its stage
from the files, and why it was picked (`In Progress comes first`). List the other cards in
that column in the order you read them, so the user can see whether it matches the board.
Then ask with `AskUserQuestion`: start this card, pick another (the user names it), or
stop. Start nothing without a yes. On a yes, carry on with that issue number as if the
user had passed it (section 1).

If no card qualifies, say which columns were empty or held only cards waiting for `/ship`,
and fall back to listing the features in `plans/`.

## 2. Work out the stage from the files

There is no state file. The plan files are the state, so a run can stop anywhere and the
next run (in this session or a new one) resumes from the same place. Check in this order and
take the first that matches:

| Files say | Stage to run | Card column |
|---|---|---|
| No refinement | `/ticket <n>` or `/refine <name>` | Refined after it |
| Refinement, no plan | `/plan-tdd-feature <name>` | Refined |
| Plan has open `→ plan` findings in Review | `/plan-tdd-feature <name>` (update) | Refined |
| Refinement Progress points to open `→ refine` findings | `/refine <name>` (update) | Todo |
| Plan Progress has a `Next: step <n>` | `/implement-tdd-feature <name>` | In Progress |
| Plan Progress says `Built on` | `/review-tdd <name> --auto` | Review |
| Progress says `Reviewed on ... no rework` | done: section 6 | Review |

`/ticket` hands over to `/refine` itself. After `/refine`, go straight to
`/plan-tdd-feature`: it asks the open questions, so that's where the user answers them.

## 3. Run the stages

Run the stage, then work out the stage again from the files and run the next one. Keep going
until a skill stops for the user or the feature is done. Before each stage, say in one line
which stage is next and why (`Plan says Built on 2026-10-01, so reviewing.`).

Invoke each skill with the `Skill` tool, passing the feature name (and `--auto` for
`review-tdd`). Let it run to its end. Don't answer its questions for the user, and don't
skip its stops.

**When a skill stops for the user** (an open question, a stale plan, the default-branch
check, a test that passes too early, a manual check, a review finding that needs a
decision): stop too. Pass on what it asks without rewording it, and say that `/manager-tdd
<feature>` carries on after the answer. When the user answers in this conversation, give the
answer to the stage that asked, then continue the loop.

**Never run** `/ship` (the user runs it; its frontmatter blocks other skills anyway),
`/new-ticket` unasked, or a stage the files don't call for.

## 4. Review rounds and auto-fixes

`/review-tdd --auto` accepts the findings it marks auto-fixable without asking, and asks the
user about the rest. Auto-fixable means: routed to `implement`, no change to the plan,
criteria or decisions, only files the plan's Files list names, no new dependency or change to
a public signature, schema, stored data or config, and not a nit. `review-tdd` owns those
rules. The manager adds the last two:

1. **The checks pass.** After `/implement-tdd-feature` builds the rework steps, its own
   verification runs the suite, lint, type-check and build. Read its report. Anything red:
   stop and show it.
2. **The fix stayed inside the plan.** Compare `git diff <merge-base> --name-only` and
   `git ls-files --others --exclude-standard` with the plan's Files list. A file outside it:
   stop, name the file and the rework step that touched it, and ask whether to add it to
   the plan or undo the change. Don't undo it yourself.
3. **At most two review rounds.** Count the `### Round` headings in the plan's Review
   section. After round 2, if review still finds anything, stop and hand the findings to the
   user, even auto-fixable ones. Review and rework chasing each other means something is
   wrong in the plan, not in the code.

## 5. Move the card

The board shows where the feature is, so move its card when the stage changes, using the
column in section 2. Only the manager moves cards; the other skills never do. Every move
goes through `gh project item-edit`, which the project's settings make the user approve, so
say which move you're asking for.

1. Get the issue number from the refinement's `Source: #<n>` line (or `$ARGUMENTS`). No
   issue: skip all card moves and say so once.
2. Find the board: `gh project list --owner <repo owner>`. With one project, use it. With
   several, use the one whose `gh project item-list` contains the issue, and ask if that's
   still ambiguous.
3. Look up, once per run: the project ID (`gh project view <number> --owner <owner> --format
   json`), the `Status` field and its options (`gh project field-list ... --format json`),
   and the item ID of the issue's card (`gh project item-list ... --format json`, the item
   whose `content.number` is the issue).
4. Match the column by name, ignoring case. A column that doesn't exist: skip that move and
   name it in the report. The card not on the board: skip and say so (the board's
   Auto-add workflow should add it).
5. Move: `gh project item-edit --id <item> --project-id <project> --field-id <status field>
   --single-select-option-id <option>`.

Never move a card to Done. GitHub's workflows do that when the PR merges or the issue
closes. If a move fails, report it and carry on; the code matters more than the card.

## 6. Finish

The feature is done for the manager when review is clean. Report in a few lines:

- the stages run in this session, and the review rounds with their findings by route;
- criteria still open: blocked, or waiting for a manual check;
- the card's column;
- the user's remaining steps: confirm any pending manual checks, stage the changes, run
  `/ship`, then push the branch and open a PR whose description says `Closes #<n>`.

When the run stopped early instead, report the stage it stopped at, what the user needs to
answer or do, and that `/manager-tdd <feature>` resumes from there.

**Offer the next card.** When the feature finished (review clean) and there's a board, run
the pick in section 1a again. The card just finished is in Review and reviewed clean, so
the pick skips it. Show the next pick the same way and ask whether to start it. Don't offer
one after a run that stopped early: the user has an answer to give first.

Never add a `Co-Authored-By` trailer or any other AI attribution anywhere.
