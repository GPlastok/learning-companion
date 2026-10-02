---
name: review-tdd
description: >-
  Reviews a feature after /implement-tdd-feature has built it. A fresh sub-agent reads the branch diff against the plan and checks code quality, that every ticked acceptance criterion has a test that would catch a regression, and that the build stayed inside the plan. Each finding gets a route (rework in implement, plan change, plan-wording fix, refine, user decision or follow-up ticket) and an auto-fix verdict. After the user accepts findings, it records them in the plan's Review section and adds rework steps that /implement-tdd-feature builds test-first. Never edits code, commits, posts to GitHub or moves cards. Use when the user types /review-tdd, asks to review a built feature or its branch, or when /manager-tdd reaches the review stage.
argument-hint: "<feature name> [--auto]"
model: opus
effort: high
allowed-tools: Agent, Read, Glob, Grep, Write, Edit, Skill, AskUserQuestion, Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git merge-base:*), Bash(git ls-files:*), Bash(git rev-parse:*), Bash(git symbolic-ref:*)
---

# Review a TDD feature

Review a built feature the way a second engineer would: someone who didn't write the code
reads the diff with the plan next to it. The build already proved the planned tests pass and
asked the user to do the manual checks. Don't repeat that work. Review asks what the build
can't ask itself: is the code good, do the tests really protect the criteria, and did the
build stay inside what the plan agreed?

The plan is the only file this skill writes, and only after the user (or `--auto`, see
section 5) has accepted the findings. Never edit source or tests, commit, push, comment on
GitHub or move a board card.

## 1. Find the plan and check it's built

Take the feature name from `$ARGUMENTS` or the conversation, and turn it into the kebab-case
slug the other skills use. Read `plans/feature-<slug>-plan.md`, the refinement it links to
and `plans/feature-<slug>-build-log.md`.

- No plan: **stop**. Point to `/plan-tdd-feature` (or `/refine` if there's no refinement).
- No name given: list `plans/feature-*-plan.md`, use it if there's exactly one, otherwise ask.
- Progress doesn't say `Built on <date>` and some steps aren't done: **stop**. Say which
  step is next and point to `/implement-tdd-feature`. Reviewing half a feature produces
  findings the next steps would have fixed anyway.
- `Built on <date>, manual checks pending: ...` is fine. List the pending checks in the
  report, and don't do them.

Count the review rounds already in the plan's `## Review` section. This run is the next one.

## 2. Collect the diff

Find the default branch (`git symbolic-ref refs/remotes/origin/HEAD`, or `main`) and the
base: `git merge-base HEAD <default branch>`. The build doesn't commit, so the review covers
committed and uncommitted work together:

- `git diff <base> --stat` and `git diff <base>` (working tree against the base);
- `git ls-files --others --exclude-standard` for new files not yet added.

If the current branch is the default branch and the diff is empty, **stop** and ask which
branch holds the feature.

## 3. Run the reviewer in a fresh sub-agent

The session that built the feature is the worst judge of it. Even when this session didn't
build it, the reviewer should start clean. Launch one `general-purpose` agent with `model: opus` and give it:
the plan path, the refinement path, the build log path, the base commit, the list of changed
and new files, the project's guidance files (`CLAUDE.md`, `AGENTS.md`) and the brief below.

> **Review brief.** Read the plan, the refinement and the project guidance first, then the
> full diff and every new file. Report facts with `path:line`. Don't edit any file. Check:
>
> 1. **Correctness.** Bugs, unhandled edge cases and error paths, wrong assumptions about
>    data, races, anything that breaks under input the criteria mention. If a `code-review`
>    skill is available, invoke it on this diff at medium effort, without `--fix` or
>    `--comment`, and fold its findings in after checking each one.
> 2. **Tests protect the criteria.** For every ticked `AC<n>`, find its test by the AC
>    number in its name (`test_ac<n>_...`, or an `AC<n>.` prefix) and read the assertion. Would it fail if the behaviour broke? Flag tests that
>    assert too little (only that something is defined, a snapshot of anything, a mock
>    called), tests the plan lists but the code lacks, and a ticked AC with no test.
> 3. **Inside the plan.** Files changed that aren't in the plan's Files list. Behaviour the
>    plan doesn't describe. Decisions made during the build (`during build` in Decisions)
>    and whether the code follows them. New dependencies.
> 4. **Project rules.** Anything the guidance files or cited decision records forbid or
>    require that the diff ignores.
> 5. **Build record.** Every step in Progress has a red line before its green in the build
>    log. Note gaps; don't rerun anything to fill them.
>
> Don't report style preferences the project's linter or guidance doesn't back, and don't
> report anything you can't point to in the code. For each finding return one block:
>
> ```text
> F<n>. <severity: blocker | should-fix | nit> | <path:line>
> What: <one or two sentences>
> Evidence: <the code line, the missing assertion, or the rule it breaks>
> Fix: <the smallest change, in a sentence>
> Files the fix touches: <paths>
> Changes plan, criteria or decisions: <yes/no, and what>
> Changes a public signature, schema, stored data, config or dependencies: <yes/no, and what>
> ```
>
> End with `No findings.` if there are none.

## 4. Check the findings and route them

Read the line behind every finding before you pass it on. Drop any you can't confirm, and
say how many you dropped. Number the rest R1, R2, ... continuing from earlier rounds.

Give each finding a **route**, by its cause:

| Cause | Route |
|---|---|
| The code is wrong or under-tested, the plan is right | `implement`: a rework step |
| The plan or its criteria are wrong or incomplete | `plan`: re-run `/plan-tdd-feature` |
| Only the plan's wording is off; no criterion, decision meaning or step changes | `plan-text`: fixed in the plan by this skill |
| The refinement's facts about the codebase are wrong | `refine`: re-run `/refine` |
| A behaviour nobody decided, or a trade-off | `user`: a question, numbered after the plan's last Q |
| Worth doing, not needed for this feature (most nits) | `follow-up`: a new ticket via `/new-ticket` |

Then give each `implement` finding an **auto-fix** verdict. It is auto-fixable only when
all of these hold, and the verdict names the first rule that fails:

1. The route is `implement`, and the fix changes no plan text, criterion or decision.
2. Every file the fix touches is listed as new or changed in the plan's **Files** section.
3. It adds no dependency and changes no public signature, schema, stored data or config.
4. Its severity is `blocker` or `should-fix`. Nits are never worth an unasked change.

Two more rules belong to whoever runs the rework, and `/manager-tdd` checks them: the suite,
lint and type-check pass afterwards, and there are at most two review rounds.

## 5. Ask which findings to accept

Show the findings as a numbered list: `R<n>`, severity, `path:line`, what's wrong, the fix,
the route, and the auto-fix verdict. Then ask, by number, which to accept, which to reject,
and for `user` findings, the answer. Use `AskUserQuestion` for findings with a few natural
answers, and plain text otherwise.

With `--auto` in the arguments (set by `/manager-tdd`), accept auto-fixable findings
without asking, and still ask about every other finding. If none needs asking, don't ask.

No findings: skip to section 7.

## 6. Record the accepted findings in the plan

Edit `plans/feature-<slug>-plan.md` only. Never edit source, tests, the refinement (apart
from the one Progress line below), or decision records.

For an accepted `plan-text` finding, make the wording fix in the plan yourself and mark
the finding `→ plan updated <date>`. If the fix turns out to change a criterion, a
decision's meaning or a step, it is a `plan` finding instead.

**Review section.** Add or extend `## Review`, placed after the last step and before
`## Files`. One heading per round, one line per finding, rejected ones included so nobody
raises them again:

```markdown
## Review
### Round 1, 2026-10-01
- R1. should-fix, `notes/services.py:12`: counts "  " as one word. → step 9 (auto)
- R2. blocker, `notes/tests/test_views.py:40`: AC4 test only checks the status code. → step 10
- R3. should-fix: AC6 says nothing about pasted text. → plan
- R4. nit: rename `n` to `count`. → follow-up
- R5. should-fix: retry on a failed save? → rejected by user, 2026-10-01
```

**Rework steps** for accepted `implement` findings. Append them after the last step,
numbered after it, in the plan's step format:

- Heading: `## Step <n>: rework R<m>, AC<k>, <short name>` (the AC part only if the
  finding concerns a criterion).
- **Test.** A test that reproduces the finding: concrete input, the expected result, in the
  file (and class or `describe` block) the original step used. Name it with the AC number
  if there is one, otherwise with the finding number, in the plan's naming style
  (`test_ac4_...` or `test_r3_...` with pytest, an `AC4.` or `R3.` prefix with `it`).
- **Red.** Why it fails now, quoting the current behaviour. For a pure refactor with no
  behaviour change, write `None: refactor only, the suite stays green.`
- **Green.** The fix, in the file and function it names.
- **Refactor.** Usually `None.`

Untick the criteria a rework step reopens (`- [x]` back to `- [ ]`), and change their arrow
to the rework step. A criterion whose test was weak is not done until the new test passes.

**Other routes.**

- `plan`: mark the finding `→ plan`. `/plan-tdd-feature` reads open `→ plan` findings when it
  updates the plan.
- `refine`: mark the finding `→ refine`, and add one line to the refinement's Progress:
  `Review round <n> on <date> found facts to recheck: see R<m> in plans/feature-<slug>-plan.md.`
- `user`: record the answer as a new decision, `D<n>. (Q<k>) <question>: <answer>. Source:
  user, <date>, during review.`, then route the finding by the answer.
- `follow-up`: mark it `→ follow-up`. Offer `/new-ticket` for it in the report; don't run it.

**Progress.** Replace the `Built on` line with what's next, for example: `Review round 1 on
2026-10-01: 2 rework steps added (9, 10). Next: step 9.` If nothing needs rework, write
`Reviewed on <date>, round <n>: no rework.`

## 7. Report

In a few lines:

- the verdict: **clean**, **rework** (steps added), or **blocked** (plan, refine or user
  routes open);
  accepted `plan-text` fixes don't block: with only those, the verdict is clean;
- the findings by route, with numbers, and how many were dropped as unconfirmed;
- manual checks still pending from the build;
- the next command: `/implement-tdd-feature <feature>` for rework, `/plan-tdd-feature` or
  `/refine` for those routes, or, when clean, stage the changes and run `/ship`, then push
  the branch and open a PR with `Closes #<n>` (the issue from the refinement's `Source:`
  line);
- the board column the card belongs in now: **In progress** for rework, **Refined** for a
  plan change, **Todo** for a refine, **Review** when clean. Don't move it yourself.

Never add a `Co-Authored-By` trailer or any other AI attribution anywhere.
