---
name: implement-tdd-feature
description: Builds a feature test-first from the plan /plan-tdd-feature wrote. Reads plans/feature-<feature-name>-plan.md, resumes from its Progress section, and for each step writes the planned tests, runs them red, writes the smallest code that turns them green, runs the whole suite, then ticks the step's acceptance criteria, updates Progress and appends to a build log. Runs the whole plan in one go and stops only when a human is needed. Manual checks are collected and listed at the end. Doesn't commit. Use when the user types /implement-tdd-feature, asks to build, implement or start coding a planned feature, or says a TDD plan is ready to build. If there's no plan, it sends the user to /plan-tdd-feature (or /refine) first.
argument-hint: "<feature name, as given to /refine and /plan-tdd-feature>"
allowed-tools: Read, Glob, Grep, Write, Edit, Skill, AskUserQuestion, Bash
---

# Implement a TDD feature

Build a feature from the plan that `/plan-tdd-feature` wrote, one step at a time, test
first. Each step's tests are written and seen to fail for the reason the plan gives, then
the smallest code the plan describes makes them pass, and the whole suite stays green.
The plan's Progress section is the record of the work, so a later session can pick up
where this one stopped. A build log next to the plan keeps every command and its result.

The plan is the spec. Write the tests it lists and the code it describes, in the files it
names. When the plan and the code disagree, stop and ask. Don't quietly improvise: an
unrecorded change leaves the plan wrong for the next reader, and a test changed so it
passes proves nothing.

Take every command, path and convention from the plan and the project's guidance files
(`CLAUDE.md`, `AGENTS.md` and what they point to). Assume nothing about the stack.

## When to stop

Build the whole plan in one run. Don't stop between steps to report progress: Progress in
the plan is the record, and the user reads the summary at the end. Stop and wait for the
user only when a human has to decide or check something:

1. There's no plan, or no refinement either (section 1).
2. The plan is stale: files or functions it names are gone, or changed since it was
   written (section 3).
3. A step depends on an open item in Decisions (section 3).
4. The work would start on the default branch (section 3).
5. A test passes although the plan says it should fail (section 4).
6. The plan and the code disagree: a Green doesn't work, a planned test is wrong, or the
   code has moved (section 5).
7. A new dependency or new test tooling seems necessary that the plan doesn't list.

Manual checks are not a reason to stop. Leave their criteria unticked, carry on, and list
all the checks at the end (section 6). Stop at a manual check early only when the plan
says a later step builds on the UI that check covers.

After any stop, once the user answers, carry on from where the run stopped. Don't start
again from the top.

## 1. Find the plan

Take the feature name from `$ARGUMENTS` or the conversation and turn it into the same
kebab-case slug the other two skills use (`Inventory drop` gives `inventory-drop`). Look
for `plans/feature-<slug>-plan.md`.

- The plan exists: use it.
- No plan, but `plans/feature-<slug>-refinement.md` exists: **stop.** Propose running
  `/plan-tdd-feature <feature name>`, and say why in one sentence: the tests come from
  the plan's steps, so without a plan there's nothing to build test-first.
- Neither exists: **stop.** Propose running `/refine <feature name>` first, then
  `/plan-tdd-feature <feature name>`.
- No name given: list `plans/feature-*-plan.md`. Use it if there's exactly one,
  otherwise ask which one.
- The name doesn't match a file exactly: check the list for a close match (a typo, a
  different word order) and ask before using it.

In every stop case, write no files and don't survey the codebase to fill the gap. That's
the job of the earlier skills, and they ask the user questions this skill can't. Keep the
reply to what's missing and what to run next. Don't list the plans for other features:
they don't help the user decide anything.

## 2. Read the context

- Read the whole plan, and the refinement file it links to.
- Read the project's guidance and what it points to, including any framework docs it
  says to read before writing framework code. Read them before the step that needs them.
- Read the decision records the plan or refinement cites.
- Read the files each step changes, and the existing test files the plan names as the
  pattern, so new code and tests match their style: comment density, naming, helpers
  and test layout (modules, classes or `describe` blocks).
- Read the plan's **Progress** section, and the build log if there is one. Progress says
  which steps are done and which comes next. Never redo a step it marks done, and never rewrite that step's tests. They
  already passed red and green once, and a rewrite would lose that.

## 3. Check the plan is ready to build

Do the branch check first. It's the cheapest one, and the user's answer may be needed
before anything else is worth running.

**Branch.** Run `git status` and check the current branch. If it's the default branch,
propose creating `feature/<slug>` and wait for the answer. Don't switch or create
branches on your own. If the user agrees, create it from the current state. If they say
to stay, stay. Uncommitted changes from steps already marked done are expected on a
resume. Unrelated changes are worth a mention before you start.

**Blocked criteria.** Criteria marked `blocked by Q<n>` stay out of the build. Skip
them, and list them in the final report so nobody forgets them.

**Open decisions.** If a step depends on an item in Decisions that is still open (no
answer, "to decide", "open item"), ask it as a numbered question before that step.
Continue the plan's numbering (after Q8 comes Q9). Record the answer as a new decision,
as in section 5, then build the step.

**Staleness.** Check that the files and functions the plan names still exist (Glob and
Grep). Files the plan lists as new, including everything a setup step 0 creates, aren't
expected to exist yet. Then look for changes since the plan was written: find the commit that last
changed the plan (`git log -1 -- <plan path>`) and list the commits after it that touch
the plan's files (`git log <commit>..HEAD -- <files>`). If the plan isn't committed,
use the date in its Progress. Changes the Progress section already accounts for, such as
the steps built so far, are expected. If something is gone, or a change the plan
doesn't account for touches code a step relies on, stop. Say what changed and ask
whether to re-run `/plan-tdd-feature`.

**Baseline.** Run the full test suite once with the project's command. Note the number
of passing tests, because each Progress update compares against it. If the suite is
already red, stop and report it. The failure isn't this feature's, and building on a red
suite hides which tests the new code broke. One exception: some runners treat a test file
with no tests in it yet (as after a step 0 that only adds helpers), or a run that collects
no tests, as a failure (pytest exits with code 5, Vitest reports a failed file). That's
expected until the next step adds a test. Note it in Progress and carry on.

If the plan's Progress says `No test suite yet: step 0 creates it.`, there's nothing to
run yet. Skip the baseline here and run it right after step 0 instead (section 4).

**Build log.** Start or continue `plans/feature-<slug>-build-log.md`, next to the plan.
Its first line names the plan, and each run adds a dated heading. Under it, append one
line for every test, lint, type-check or build command you run: the step, the command,
and what it showed (`Step 3 red: make test ARGS="-k test_ac7" … 3 failed, all on the
planned assertion`). Add one line for each stop and each answer the user gave. Progress says
where the build stands, and the log shows how it got there: that each test really was
red first, and what the checks said.

## 4. Build one step at a time

Work through step 0 (if the plan has one) and then every numbered step, in order.

**Setup step 0** (`## Step 0: project setup`, with Setup, First test and Check parts) is
built differently, because there's no suite to go red against yet:

1. Create what its **Setup** lists, with the packages it names. Installing those packages
   is part of the plan, so it isn't a stop. Anything the step doesn't name still is.
2. Write the **First test** and run the full suite. It must pass with exactly that one
   test. If it fails, fix the setup, not the test. If it can't pass without something the
   step doesn't list, go to section 5.
3. Run every command in **Check**. Each must pass.
4. This run is the baseline: one passing test. Log the commands and results, tick the
   criteria step 0 covers, and replace the `No test suite yet` line in Progress with
   `Step 0 done: 1 test passes.`

For every other step:

1. **Test.** Write exactly the tests the step describes, in the file it names: the same
   test names with their AC numbers, in the same module, class or `describe` block, with
   the same concrete input values and helpers. Don't add tests the plan doesn't list, and don't drop any. The plan's
   reader should find the tests it promised under the names it promised.
2. **Red.** Run only the new tests, with the single-test command from the plan's
   Verification section or the project guidance. Compare the output with the step's
   **Red** part.
   - A test fails for a different reason (an import error, a typo, a wrong helper): fix
     the test, not the code, and run it again. A test that fails for the wrong reason
     proves nothing about the behaviour.
   - A test the plan says should fail passes instead: **stop and report it.** Show the
     test, what the plan expected, and the output. Either the behaviour already exists,
     or the test doesn't check what the plan thinks it does. Either way the user
     decides, because both "carry on" and "change the test" change the plan.
   - Rows the plan says already pass are expected to pass. Check that they do.
3. **Green.** Make the smallest change the step's **Green** part describes, in the file
   and function it names. Don't build ahead for later steps: their tests have to fail
   first, and code written early would make them pass before they're written. Follow
   the project's guidance while you write it (for example rules about which files may
   import what, or what a given kind of file may export). Then run the whole suite. It
   must be all green, including every earlier test. If it isn't, fix the code, not an
   earlier test. If the plan's Green can't make the tests pass, go to section 5.
4. **Refactor.** Only what the step's **Refactor** part says, then run the whole suite
   again. "None" means none.
5. **Manual check.** If the step has one, don't tick its criteria. Keep the plan's
   numbered, click-by-click checks for the end-of-run list. If the step also has tests,
   the criterion waits for both.
6. **Record.** Edit the plan:
   - Tick the criteria this step's tests cover (`- [ ]` becomes `- [x]`). Tick only
     criteria whose tests you saw pass, and none that wait for a manual check.
   - Append the step's commands and results to the build log, if you haven't as you went.
   - Update **Progress**: which step is done, the test count (`Step 3 done: 51 tests
     pass, 42 before the build plus 9 new.`), anything that went differently from the
     plan, and the next step. Replace the old "Next:" line, and keep the history short.

Update Progress after every step, not only at the end. If the run is cut off, the next
session resumes from what it says.

**Rework steps.** Steps headed `Step <n>: rework R<m>` come from `/review-tdd`, which
appends them after a review and sets Progress to the first one. Build them like any other
step, with two differences:

- If the step's **Red** says `None: refactor only`, skip the red run. Make the change, then
  run the whole suite, which must stay green.
- Add the rework test next to the earlier tests. Change or remove an earlier step's test
  only when the rework step's **Test** part says so. That's the reviewed exception to
  never rewriting a done step's tests.

When a rework step is done, change its finding in the plan's `## Review` section from
`→ step <n>` to `→ fixed in step <n>`.

## 5. When the plan and the code disagree

Stop if a step's Green doesn't make its tests pass, a planned test is wrong (it asserts
something the criterion doesn't say, or can't pass as written), or the code has moved
since the plan (a function has a different signature, a file has been split). Then:

- Explain what's wrong in a few lines, with the failing output or the line of code.
- Propose a fix: a changed test, a different Green, or a smaller step.
- Once the user agrees, record it in the plan's Decisions section as a new decision,
  numbered after the last one: `D<n>. <what changed and why>. Source: user, <date>,
  during build.` Note it in Progress, then carry on.

A new dependency or new test tooling is the same kind of stop. Don't install anything the
plan doesn't list. Ask, and record the answer as a decision.

Never edit the refinement file apart from the one Progress line in section 7. It's
`/refine`'s record of the survey. Never edit an accepted decision record. If the
project's rules say a change needs a new decision record, write one the way the rules
describe, and say so in the report.

## 6. Verify

After the last step, run everything in the plan's **Verification** section: the full
test suite, lint, and type-check or build if the project has them, with the project's
commands. Report each result
as it is. For a failure, include the relevant output. A known warning the plan says may
remain is not a failure, but mention it.

Then give the end-of-run list of manual checks, as one numbered list:

- the command to start the app, from the project's guidance;
- for each check, its AC numbers, the click-by-click steps from the plan and the
  expected result.

If browser tooling is available (for example a Playwright MCP server or a `run` skill),
offer to drive the checks and report what you saw. The user still confirms each check
before its criterion is ticked: what counts as "looks right" is their call.

When the user confirms a check, tick its criteria and update Progress. When they report a
problem, treat it as section 5.

## 7. Record it and report

- Update the plan's Progress to `Built on <date>.`, or `Built on <date>, manual checks
  pending: AC<n>, AC<m>.` if any are still open.
- Add one line to the refinement's Progress section: `Built on <date>, see
  plans/feature-<slug>-plan.md.` Change nothing else there.

Use today's date. Then reply in a few lines:

- the steps done, and the path of the build log;
- the criteria ticked, and the ones still open (blocked, or waiting for a manual check);
- the decisions made during the build;
- the verification results;
- the numbered manual-check list, if there is one.

Don't commit, push or open a PR. Look in the project's skills folder (`.claude/skills/`)
for the next skills. If there's a review skill (`/review-tdd`), suggest it next, in a fresh
session so the reviewer isn't the session that wrote the code. Then suggest the skill that
commits or ships changes by its slash command (for example "after a clean review, run
`/ship` to test, lint and commit"). Only fall back to "commit when you're ready" if there's
neither. When `/manager-tdd` ran this skill, it runs the review itself, so leave that part
out. Never add a `Co-Authored-By` trailer or any other AI attribution anywhere,
in code, comments, plans or commit messages.
