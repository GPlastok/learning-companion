---
name: plan-tdd-feature
description: Turns a /refine refinement file into a test-driven build plan. Reads plans/feature-<feature-name>-refinement.md, asks the user any open questions it still has, then writes plans/feature-<feature-name>-plan.md with one red-green step per function or behaviour, each listing the acceptance criteria it covers, and runs /unslop on it. In a repo with no project yet, its step 0 sets up the project, its tooling and a first passing test. Writes no code or tests. Use when the user types /plan-tdd-feature, asks for a TDD plan, or says a refined feature is ready to plan. If no refinement file exists, it sends the user to /refine first.
argument-hint: "<feature name, as given to /refine>"
allowed-tools: Read, Glob, Grep, Write, Edit, Skill, AskUserQuestion, Bash(ls:*), Bash(git log:*), Bash(git status:*)
---

# Plan a TDD feature

Take the refinement file that `/refine` wrote and turn it into a plan someone can build
test-first: one step per function or behaviour, each listing the acceptance criteria it
covers, and each naming the failing tests to write, why they fail, and the least code
that makes them pass.

The plan is the only file this skill creates. Don't write tests, stubs or source code,
and don't touch docs or decision records. Writing the tests is the first thing the build
session does, and it goes better when the user has read the plan first.

## 1. Find the refinement file

Take the feature name from `$ARGUMENTS` or the conversation and turn it into the same
kebab-case slug `/refine` uses (`Inventory drop` gives `inventory-drop`). Look for
`plans/feature-<slug>-refinement.md`.

- No name given: list `plans/feature-*-refinement.md`. Use it if there's exactly one,
  otherwise ask which one.
- The name doesn't match a file exactly: check the list for a close match (a typo, a
  different word order) and ask before using it.
- **No refinement file at all: stop.** Tell the user to run `/refine <feature name>`
  first, and say why in one sentence: the plan's tests come from the refinement's
  acceptance criteria, so without them the plan would rest on guesses. Don't survey the
  codebase yourself to fill the gap. That's `/refine`'s job.

If `plans/feature-<slug>-plan.md` already exists, read it and ask whether to update or
replace it. Its Progress section may record work that's already done. If its `## Review`
section has findings marked `→ plan`, those are why it needs updating: settle each one
(as questions in step 3 if needed), change the criteria and steps it affects, and mark the
finding `→ plan updated <date>`. Keep the steps already done and their tests as they are.

## 2. Read the context

- Read the whole refinement file.
- Read the project's guidance (`CLAUDE.md`, `AGENTS.md` and what they point to) and any
  decision records the refinement cites.
- Read one or two existing test files the refinement names as the pattern to copy, so
  the planned tests match the real helpers, naming and layout (test modules, classes or
  `describe` blocks). Read the test naming rules in the guidance files too.
- If the refinement's survey found no project or no test suite ("not found"), there is
  nothing to copy or spot-check. Take the stack, layout and commands from the guidance
  files instead, and plan a setup step 0 (step 4).
- Spot-check that the paths and functions the refinement names still exist. If
  `git log` shows commits since the refinement's date that touch those files, note what
  changed. If something the plan depends on is gone, tell the user and ask whether to
  re-run `/refine` rather than planning against a stale survey.

## 3. Settle the open questions

`/refine` isn't allowed to answer its own open questions. They are behaviours the feature
description left undecided, or facts the survey couldn't find. A TDD plan can't leave them
open, because every test pins down one exact behaviour. A guessed answer becomes a test
that is wrong from the first line.

Number every question Q1, Q2, ... and keep the number everywhere: in the question you
ask, in the decision that records the answer, and in any `blocked by Q<n>` mark. Use the
refinement's numbering if it has one. Designing the tests in step 4 can turn up
behaviours the refinement doesn't pin down, for example the exact separator or an edge
case nobody mentioned. Treat those as questions too, numbered after the refinement's,
rather than picking an answer yourself.

For each question:

1. Check whether it's already answered: in the conversation, in `$ARGUMENTS`, in an
   existing plan file, or because the code now settles it. Note where the answer came
   from.
2. Ask the user all the unanswered ones together. Use `AskUserQuestion` (up to four
   per call) when a question has a few natural answers, and offer the options the
   refinement and the code suggest. Ask in plain text when it's open-ended. Start each
   question with its number (`Q3. Should the file end with a newline?`), and in plain
   text use a numbered list so the user can answer by number. Don't mark one option as
   recommended. The refinement deliberately left the choice to the user.
3. Record every answer as a numbered decision (D1, D2, ...) in the plan, with the
   question number and its source: `D1. (Q1) <question>: <answer>. Source: user,
   2026-09-29.` Decisions that come from the code, not from a question, have no Q.
4. If an answer implies behaviour none of the existing criteria cover, add a new
   criterion and mark it `(from D<n>)`.
5. If the user skips a question or says "not yet", don't guess. Mark every criterion
   that depends on it `blocked by Q<n>` and leave it out of the steps. The plan still
   lists it, so nobody forgets it.

If the refinement has no open questions and the tests raise none, say so in the plan's
Decisions section and move on.

## 4. Group the criteria into steps

Number the criteria AC1, AC2, ... in the refinement's order, then add any new ones from
step 3. Then group them into steps. **A step covers one function or one behaviour**, for
example "the file text for a normal story", "the file name's date part" or "the button
is disabled when there's nothing to export". It lists every criterion it covers in its
heading.

- Every criterion that isn't blocked maps to exactly one step, and the criteria list
  shows which (`→ step 3`). That's what lets a reviewer see that nothing was skipped.
- Inside a step, each criterion gets at least one test, or one row of a table-driven
  test, whose name carries its AC number. Use the project's naming rule if the guidance
  sets one, for example `test_ac14_prefixes_player_lines` with pytest or
  `it("AC14. prefixes every player line with '> '")` with Jest or Vitest. The build
  session can then still tick criteria off one at a time.
- Put criteria that exercise the same function with different inputs into one step,
  often as one table-driven test (`@pytest.mark.parametrize`, `it.each`). Ten slug rules
  for one file-name function are one step, not ten.
- A criterion that holds as soon as its step's code exists ("the file has no raw JSON",
  "a reload gives the same text") is written as a test in that step. It doesn't get a
  step of its own that starts green, and it doesn't need a "break it temporarily" check.
- Split a step when its Green would change more than one function or component, or when
  its tests need different setup. A plan for a small feature usually ends up with five
  to twelve steps. Many more than that means the steps are too small.
- Manual checks for the same screen can share a step, with one numbered check per
  criterion.

Every step has the same parts:

- **Test.** The file, the test names (and the class or `describe` block they sit in), and
  what each test arranges, does and asserts, labelled with its AC. Use concrete input
  values, and name the helpers the test file already has or should add.
- **Red.** The exact reason the tests fail before the code exists, for example "fails on
  the assertion: `format_story` returns an empty string" or "fails: the response has no
  `ended` field". A test that fails for the wrong reason, such as an import error or a
  typo, proves nothing. If a stub is needed so the test fails on its assertion, that stub
  belongs to step 0. If some rows already pass because of an earlier step, say which ones.
- **Green.** The smallest change that makes this step's tests pass without breaking the
  earlier ones, with the file and function. Don't design ahead for later steps.
- **Refactor.** Only if there's a real cleanup at this point. Otherwise "none".

Order the steps so each builds on the last: the plain happy path first, then edge cases,
then errors. A criterion may say something the current test setup can't check, for
example UI behaviour when the tests have no browser or DOM, or a live model call. Don't quietly add new test tooling. Make that step a manual check with exact
click-by-click instructions and expected results, and add a decision noting the gap (the
user can decide later to add the tooling).

Add a **step 0** only for shared groundwork several steps need: new types, a stub with
the real signature that raises or throws "not implemented", a test helper, or a decision
record the project's rules require. If nothing is needed, leave step 0 out.

**Setup step 0 for a repo with no project yet.** When the refinement says there is no
project or no test suite, step 0 creates them, and every later step builds on it. Write
it as `## Step 0: project setup` with these parts instead of Test, Red, Green and
Refactor:

- **Setup.** What to create, using only the stack, layout and commands the guidance files
  name: the project and app skeleton, the dependency files with every package listed by
  name, the test runner config, the linter config, and the command file (a Makefile, an
  npm `scripts` block) with the commands the guidance lists. A package or tool the
  guidance doesn't name is an open item in Decisions, not part of step 0.
- **First test.** One test that passes once the setup exists and proves the runner works
  against the real project, for example that the home URL returns 200 or that settings
  load. Name the file and the test. It's expected to pass when first run; there is no red
  run, since there is no code yet for it to fail against.
- **Check.** The commands that must pass at the end of step 0: the full suite (exactly one
  test, passing), the single-test command, and lint.

Put `No test suite yet: step 0 creates it.` in the plan's Progress, so the build knows to
run its baseline after step 0. Criteria about the setup itself (the app starts, the lint
command runs) belong to step 0 and are ticked when its Check passes or, for something only
a person can see, become manual checks.

## 5. Write the plan

Write `plans/feature-<slug>-plan.md`. Match the existing plans in `plans/`: short,
factual, real paths and names. Use these sections in this order:

```markdown
# <Feature name>: TDD plan

## Context
What's being built, in two or three sentences, with a link to the refinement file. The
branch if there is one. What's in scope and what's left for later.

## Progress
Plan written on <date>. Nothing built yet. Next: step 0 (or step 1).
No test suite yet: step 0 creates it. (Only for a setup step 0.)

## Decisions
D1. (Q1) <question, shortened>: <answer>. Source: <user, date / conversation>.
D2. <fact the code settles>. Source: code.
Or: "The refinement had no open questions."

## Acceptance criteria
- [ ] AC1. <criterion, copied from the refinement> → step 1
- [ ] AC2. <criterion> → step 1
- [ ] AC4. <criterion> → blocked by Q2
- [ ] AC6. <criterion> (from D1) → step 3

## Step 0: groundwork
(Only if needed. For a repo with no project yet: `## Step 0: project setup`, with
Setup, First test and Check.)

## Step 1: AC1, AC2, <short name>
**Test.** ...
**Red.** ...
**Green.** ...
**Refactor.** ...

## Files
New, changed, and for reference, each one with a few words on why.

## Verification
The commands to run and what they should show: the suite red after each new test and
green after each change, then lint, and type-check or build if the project has them.
Use the refinement's commands, or the guidance files' when step 0 creates them.
```

Use today's date. Every path, function and command must come from the refinement or from
a file you read. If something needed for a step isn't in either, put it in Decisions as
an open item instead of inventing it.

## 6. Run /unslop on the plan

Invoke the `unslop` skill on `plans/feature-<slug>-plan.md` and apply its edits to the
file. Keep code identifiers, paths, commands, test names, AC and D numbers exactly as
they are. Unslop is for the prose around them. The plan is read by whoever builds the
feature, often in a fresh session, and plain sentences save them from guessing what a
step means.

## 7. Record it and report

In the refinement file, add one line to its Progress section: `Plan written on <date>:
plans/feature-<slug>-plan.md.` Change nothing else there. It's `/refine`'s record of the
survey.

Then reply in a few lines: the plan's path, the number of steps and criteria, the
decisions recorded, and any blocked criteria or manual-check steps. Don't print the
plan, and don't start building.
