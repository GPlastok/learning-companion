# Speeding up the pipeline: TDD plan

## Context

Make the pipeline faster by changing the skills in `.claude/skills/` and the Pipeline section of `CLAUDE.md`. The changes cover four areas:

- model routing per stage;
- plan questions with suggested defaults;
- a lighter red/green record;
- short plans that a Sonnet build can still follow.

Item 5 of the ticket adds three more fixes from the #3 run.

Refinement: [feature-speeding-up-the-pipeline-refinement.md](feature-speeding-up-the-pipeline-refinement.md). Source: #10.

Branch: `feature/10-speeding-up-the-pipeline`.

This is a tooling change, like #15. No Django code changes.

Every change is listed below as C1 to C12, with its exact diff, what it saves and what it costs (D1, D13). The user OKs or rejects each one. The build applies only the changes the user OK'd.

**In scope:**

- the frontmatter and text of `refine`, `plan-tdd-feature`, `implement-tdd-feature`, `review-tdd` and `manager-tdd`;
- the Pipeline section of `CLAUDE.md` (D12).

**Not in scope, follow-up tickets:**

- updating the skill evals to the new rules, and their TypeScript fixtures (D10);
- a token counter per stage (D14);
- plain-text questions instead of `AskUserQuestion` in `/review-tdd`, `/manager-tdd` and `/new-ticket` (D6).

## Progress

Plan written on 2026-10-02. Baseline: 64 tests pass. All changes C1 to C12 OK'd on 2026-10-02 (D21, D24).

Steps 1-5 done: 64 tests pass, as before (no Python changes). The five frontmatter steps were checked red and green together, with one log line each for red and green.

Steps 6-9 done: 64 tests pass. Checked together the same way. The Record snippet was also run on a dummy plan in the scratchpad: it ticked, logged and moved `Next:` as intended.

Step 10 done: 64 tests pass. Step 11 done: the diff holds only the OK'd changes, in the six planned files.

Verification: `make test` 64 passed, `make lint` passed.

Review round 1 on 2026-10-02: 2 rework steps added (13, 14). R8 fixed in the plan. R6 and R7 became steps 15 and 16 (D29).

Steps 13-16 done: 64 tests pass, as before. A `sed` for the Review marks also changed the AC13, AC14 and AC23 arrows; they were set back to `→ step 13`/`→ step 14`, and R6 was marked by hand.

Observed during the rework build: `/implement-tdd-feature`, invoked inline by `/manager-tdd` through the `Skill` tool, ran on `claude-sonnet-5-5`. That is evidence for AC6's model part. Its effort level and the other stages still need step 12's check.

Verification: `make test` 64 passed, `make lint` passed.

Review round 2 on 2026-10-02: 3 rework steps added (17, 18, 19). R12's plan text was fixed in C10. A round 3 follows (D34). Manual checks still pending: AC4, AC5, AC6, AC7, AC19 (step 12).

Steps 17-19 done: 64 tests pass, as before. The step 17 dry runs ran on a copy of this plan and on a small plan. Step 19's `diff` of the shipped Output and Record text against C10's "As changed by review" blocks came back clean.

Verification: `make test` 64 passed, `make lint` passed.

Review round 3 on 2026-10-02: 1 rework step added (20). No fourth round (D35). Manual checks still pending: AC4, AC5, AC6, AC7, AC19 (step 12).

Step 20 done: 64 tests pass, as before. The dry run with the last-step form moved Progress to `Next: verify.` without a warning.

Verification: `make test` 64 passed, `make lint` passed.

Built on 2026-10-02 after review round 3, manual checks pending: AC4, AC5, AC6, AC7, AC19 (step 12, live model check).

Reviewed on 2026-10-02, round 3: no rework left after step 20, and no fourth round (D35). Manual checks still pending: AC4, AC5, AC6, AC7, AC19.

Observed for step 12: after each stage the session stays on that stage's model. `/manager-tdd` ran on `claude-sonnet-5-5` right after each `/implement-tdd-feature` run, and on `claude-opus-5-5` after `/review-tdd`. So a skill's `model` lasts beyond the skill itself, and each stage still sets its own (D15).

## Decisions

D1. (Q1) The OK on each diff happens at the plan stage, for this ticket's changes only. The plan holds every diff. The user OKs or rejects each one, and the build applies only the OK'd ones. Source: user, 2026-10-02.

D2. (Q2) Model and effort go in skill frontmatter. A live run checks that they take effect. CLAUDE.md also writes down the manual way (`/model`, `/effort` before a stage) as a fallback. Source: user, 2026-10-02.

D3. (Q3) The reviewer's Agent call names `model: opus`. A model named on the Agent call holds whatever the session runs, so it also holds when `/review-tdd` is started by hand. Source: user, 2026-10-02.

D4. (Q4) Suggested defaults apply only to `/plan-tdd-feature`'s questions. `/refine` keeps listing open questions without answers. Source: user, 2026-10-02.

D5. (Q5) A reply like "rest as suggested" accepts every remaining default. Those decisions are recorded as `Source: user (accepted default), <date>`. Source: user, 2026-10-02.

D6. (Q6) "No `AskUserQuestion`" goes into `/plan-tdd-feature` only, as the ticket says. The other skills are a follow-up. Source: user, 2026-10-02.

D7. (Q7) `NoReverseMatch` counts as red only when it names a route the step itself adds. `NoReverseMatch` for any other route is an error to fix. A link to a route a later step adds is left out until that step, or the steps are reordered. Source: user, 2026-10-02.

D8. (Q8) The build log gets one red line and one green line per step. A retry goes inside that line, for example `… 4 failed on the missing template, then 4 failed on the planned assertion`. Source: user, 2026-10-02.

D9. (Q9) The detail check for "a Sonnet build can follow it" works two ways:

- the next ticket's build runs on Sonnet as the live test;
- review checks plans against the plan skill's step rules.

Source: user, 2026-10-02.

D10. (Q10) The evals stay as they are in this ticket. A follow-up ticket updates them later, after the skills have settled. Source: user, 2026-10-02.

D11. (Q11) No pytest test. As in #15 (its D7), each step is checked by reading the files (`grep`, `git diff`), and runtime behaviour gets a live check. Source: user, 2026-10-02.

D12. (Q12) CLAUDE.md's Pipeline section is updated where a changed rule appears in it. Source: user, 2026-10-02.

D13. (Q13) Each change states its time saved from the #3 transcript's counts. Where the gain depends on a model's speed, that part is marked as an estimate. Source: user, 2026-10-02.

D14. (Q14) A token counter is a follow-up ticket. This ticket states time, not tokens. Source: user, 2026-10-02.

D15. (Q15) Every stage skill sets its own model and effort in frontmatter, so the order of stages doesn't matter, by hand or through the manager. Source: user, 2026-10-02.

D16. The values per skill follow from the ticket and D15:

- `refine`: `opus`, `high`;
- `plan-tdd-feature`: `opus`, `high`;
- `implement-tdd-feature`: `sonnet`, `medium`;
- `review-tdd`: `opus`, `high`;
- `manager-tdd`: `opus`, `high`.

`high` for refine, review and manager matches the plan stage's effort. The ticket leaves those three open, so the user can change them through C1, C4 and C5. Source: plan.

D17. `ticket`, `new-ticket`, `ship` and `unslop` get no model. `ticket` hands over to `refine`, which sets its own model. The other three do short, mechanical work or are run by the user. Source: plan.

D18. The green run and the record share one Bash call: run the suite, and only when it passes, tick, append the log line and replace `Next:`. `implement-tdd-feature`'s `allowed-tools` already lists `Bash`, so the compound command needs no permission prompt (`.claude/skills/implement-tdd-feature/SKILL.md:5`). Steps 2, 5, 6, 9 and 10 of #3 already recorded this way. Source: code.

D19. Item 5 adds three changes. Two come from the refinement's round-trip list for #3, and one from the #4 refinement:

- C10's output rule: four reruns in #3 came from output filtered too tightly;
- C7: the "check earlier decisions" memory rule, added to the plan skill, from the #4 refinement re-asking settled questions;
- C11: a plan-wording route in `/review-tdd`, from #3's R7.

The double check of review findings (`review-tdd/SKILL.md:92`) stays, because it drops false findings and so adds safety. Source: plan, from the refinement.

D20. `.claude/hooks/check-plan-progress.sh` ignores `.claude/` but counts `CLAUDE.md` (#15 D12). After step 10, the build updates Progress before it stops. Source: code.

D21. (Q16) The user OK'd C1, C3, C4, C5, C6, C7, C9, C10, C11 and C12. C8 is OK'd with clearer wording: short paragraphs are about splitting the text, not shortening the plan. Its diff now says so. Source: user, 2026-10-02.

D22. (Q16) C5 keeps `effort: high` for now. The user may lower `/manager-tdd` to `medium` later. Source: user, 2026-10-02.

D23. (Q16) C7 is a stopgap. The user plans a new decision system later, so the earlier-decisions rule may be replaced then. Source: user, 2026-10-02.

D24. (Q17) C2 is OK'd as planned: `AskUserQuestion` comes off `plan-tdd-feature`'s `allowed-tools`. The list grants tools without a prompt and doesn't block others, so C6's "Never use `AskUserQuestion`" is the rule and the header matches it. Source: user, 2026-10-02.

D25. (Q18, R1, R2, R3, R5) The Record snippet changes as the user OK'd in review round 1:

- the record goes in the step's last whole-suite run (Green's, or Refactor's when there is one);
- `Next:` is matched anywhere on the line, and a `grep -q` check prints a warning when Progress didn't change;
- the snippet appends the red line, written from the red run already seen, and the green line;
- Progress gives the count against the baseline (`Step 3 done: 51 passed, 42 before the build.`).

Source: user, 2026-10-02, during review.

D26. (Q19, R4) The "show 40 lines of output" rule moves out of Red into a general rule at the top of section 4, for every test, lint, type-check or build command. Source: user, 2026-10-02, during review.

D27. (Q21, R8) D19 and step 11 now say C7's evidence comes from the #4 refinement and the memory rule, not the #3 run. Source: user, 2026-10-02, during review.

D28. (Q22, R9) The grouped log lines for steps 1-5 and 6-9 are accepted as they are. Later builds log per step. Source: user, 2026-10-02, during review.

D29. (Q20, R6, R7) Both are fixed now as rework steps 15 and 16, with the diffs shown in review round 1. Source: user, 2026-10-02, during review.

D30. (Q23, R10) The Record snippet's `sed` and its warning check work only inside the `## Progress` section. This changes D25's second bullet: `Next:` is matched anywhere on a line, but only inside Progress. Source: user, 2026-10-02, during review.

D31. (Q23, R10) The plan template in `plan-tdd-feature/SKILL.md` puts `Next:` on its own line, under "Plan written on <date>. Nothing built yet.". Source: user, 2026-10-02, during review.

D32. (Q24, R11) After the last step, Record drops the `Next:` line instead of moving it, and section 7 writes `Built on`. Source: user, 2026-10-02, during review.

D33. (Q25, R12) C10 in this plan shows the shipped text "as changed by review", and step 11's diff check runs again after the rework (step 19). Source: user, 2026-10-02, during review.

D34. (Q26) A third review round runs after the round 2 rework, beyond `/manager-tdd`'s two-round rule. Source: user, 2026-10-02, during review.

D35. (Q27, R13) After the last step, Record writes `Next: verify.` instead of dropping `Next:`. Section 7 replaces that line with `Built on`. `/manager-tdd`'s stage row matches any `Next:` line (`Next: step <n>` or `Next: verify`). This changes D32. No fourth review round: the build checks the fix with a dry run. Source: user, 2026-10-02, during review.

## Acceptance criteria

- [x] AC1. Every change to a file under `.claude/skills/` is shown to the user as a diff before the file is edited. → step 19
- [x] AC2. No skill file changes until the user has OK'd that change. A change the user rejects is not made. → step 19
- [x] AC3. Every proposed change states how much time it saves and what it costs in safety or quality. → step 11
- [ ] AC4. `/refine`'s three Explore sub-agents run on Haiku. → step 12
- [ ] AC5. `/plan-tdd-feature` runs on Opus at high effort. → step 12
- [ ] AC6. `/implement-tdd-feature` runs on Sonnet at medium effort. → step 12
- [ ] AC7. `/review-tdd`'s reviewer sub-agent runs on Opus. → step 12
- [x] AC8. Where a stage's model or effort can't be set from the skill, the user is told the manual way (`/model`, `/effort`) to use before that stage. → step 10
- [x] AC9. Each question `/plan-tdd-feature` asks carries a suggested default with a one-line reason. → step 6
- [x] AC10. Questions are asked in plain text as a numbered list, never through `AskUserQuestion`. → step 6
- [x] AC11. No answer is recorded as a decision unless the user gave it. The user still decides every question. → step 6
- [x] AC12. For a step that adds a new route, a red run that fails with `NoReverseMatch` for that route counts as the planned red. No stub is added only to get an assertion failure. → step 8
- [x] AC13. Progress and the build log are updated in the same tool call as the step's green run. → step 17
- [x] AC14. The build log has one line per red run and one per green run. → step 13
- [x] AC15. A test that passes when the plan says it should fail still stops the build. → step 8
- [x] AC16. Plans `/plan-tdd-feature` writes are in short paragraphs: one idea each, decisions as a lead sentence plus bullets, and Test, Red and Green parts of two or three sentences. → step 7
- [x] AC17. Each plan step still names the file, test names, concrete inputs, the red reason and the smallest green, so a Sonnet build needs no extra question. → step 7
- [x] AC18. Every other round-trip cost proposed from the #3 run cites its evidence from that run, and states its time saved and its safety or quality cost, like items 1 to 4. → step 11
- [ ] AC19. `refine`, `review-tdd` and `manager-tdd` set their own model and effort, so a stage that follows `/implement-tdd-feature` doesn't run on Sonnet. (from D15) → step 12
- [x] AC20. "Rest as suggested" accepts every remaining default, and those decisions say "accepted default". (from D5) → step 6
- [x] AC21. A `NoReverseMatch` for a route the step doesn't add is treated as an error, not as red. (from D7) → step 8
- [x] AC22. `/plan-tdd-feature` and `/refine` check earlier plans' Decisions before asking, and cite a decision that settles a question instead of asking it. (from D19) → step 7
- [x] AC23. A failing test, lint or check run shows enough output in the same call to read the failure, with no second call just to see it. (from D19) → step 14
- [x] AC24. A review finding that only fixes plan wording, changing no criterion, decision meaning or step, is fixed by `/review-tdd` in the plan, without a `/plan-tdd-feature` run or card moves. (from D19) → step 10

## The changes

Each change has its diff, then **Saves** and **Costs**. "T:" is a line in the #3 transcript `8da063d8-….jsonl`. Paths are relative to the repo root.

### C1. `/refine`: Explore on Haiku, its own model

`.claude/skills/refine/SKILL.md`:

```diff
 argument-hint: "<feature name, and optionally a sentence on what it should do, or acceptance criteria you already have>"
+model: opus
+effort: high
 allowed-tools: Agent, Read, Glob, Grep, Write, Bash(ls:*), Bash(git ls-files:*), Bash(git log:*), Bash(git status:*)
```

```diff
 Send all three Agent calls in a single message so they run concurrently. Use the `Explore`
-agent type. Give each one the feature description, any supplied criteria and the stack
+agent type with `model: haiku`. Give each one the feature description, any supplied criteria and the stack
 details from step 2.
```

**Saves.** In #3 the three Explore agents ran on Opus for 33, 46 and 46 s, with 4 tool uses and about 23k tokens each. Haiku should bring the wall clock to about 20 s. That is an estimate: the transcript has no Haiku run. So it saves about 25 s per refine, and most of the tokens' cost.

**Costs.** Haiku may misread a file or miss one. The synthesis stays on Opus and already rechecks doubtful claims itself (`refine/SKILL.md:94-95`), so a wrong fact is more likely caught than written.

### C2. `/plan-tdd-feature`: Opus at high effort, no `AskUserQuestion`

`.claude/skills/plan-tdd-feature/SKILL.md`:

```diff
 argument-hint: "<feature name, as given to /refine>"
-allowed-tools: Read, Glob, Grep, Write, Edit, Skill, AskUserQuestion, Bash(ls:*), Bash(git log:*), Bash(git status:*)
+model: opus
+effort: high
+allowed-tools: Read, Glob, Grep, Write, Edit, Skill, Bash(ls:*), Bash(git log:*), Bash(git status:*)
```

**Saves.** No time by itself. It keeps planning on Opus after a Sonnet build, for example in a rework plan update.

**Costs.** None in safety.

### C3. `/implement-tdd-feature`: Sonnet at medium effort

`.claude/skills/implement-tdd-feature/SKILL.md`:

```diff
 argument-hint: "<feature name, as given to /refine and /plan-tdd-feature>"
+model: sonnet
+effort: medium
 allowed-tools: Read, Glob, Grep, Write, Edit, Skill, AskUserQuestion, Bash
```

**Saves.** The #3 first build ran on Opus: 49 tool calls in about 9 min of active work. The three rework runs took 5 to 7 calls each. Sonnet at medium effort should cut that by a third to a half, so about 3 to 4 min per build. That is an estimate.

**Costs.** This is the largest quality risk of the ticket. A thin step invites a wrong guess. The guards are:

- C8's detail rule;
- the build's own stops (stale plan, early pass, plan/code mismatch);
- review on Opus.

### C4. `/review-tdd`: reviewer on Opus, its own model

`.claude/skills/review-tdd/SKILL.md`:

```diff
 argument-hint: "<feature name> [--auto]"
+model: opus
+effort: high
 allowed-tools: Agent, Read, Glob, Grep, Write, Edit, Skill, AskUserQuestion, …
```

(The `allowed-tools` line stays as it is. It is shortened here.)

```diff
-build it, the reviewer should start clean. Launch one `general-purpose` agent and give it:
+build it, the reviewer should start clean. Launch one `general-purpose` agent with `model: opus` and give it:
```

**Saves.** No time. It keeps review on Opus right after a Sonnet build (D3, D15).

**Costs.** None in safety.

### C5. `/manager-tdd`: its own model

`.claude/skills/manager-tdd/SKILL.md`:

```diff
 argument-hint: "[issue number, or feature name; none picks the next card from the board]"
+model: opus
+effort: high
 allowed-tools: Skill, Read, Glob, Grep, AskUserQuestion, …
```

**Saves.** No time. The manager's own choices between stages stay on Opus.

**Costs.** None in safety. If `model` lasts only while a skill runs, this line does nothing, and the live check in step 12 shows it.

### C6. `/plan-tdd-feature`: questions with a suggested default

`.claude/skills/plan-tdd-feature/SKILL.md`, section 3:

```diff
-2. Ask the user all the unanswered ones together. Use `AskUserQuestion` (up to four
-   per call) when a question has a few natural answers, and offer the options the
-   refinement and the code suggest. Ask in plain text when it's open-ended. Start each
-   question with its number (`Q3. Should the file end with a newline?`), and in plain
-   text use a numbered list so the user can answer by number. Don't mark one option as
-   recommended. The refinement deliberately left the choice to the user.
-3. Record every answer as a numbered decision (D1, D2, ...) in the plan, with the
-   question number and its source: `D1. (Q1) <question>: <answer>. Source: user,
-   2026-09-29.` Decisions that come from the code, not from a question, have no Q.
+2. Ask the user all the unanswered ones together, in plain text as a numbered list.
+   Never use `AskUserQuestion`. Start each question with its number (`Q3. Should the
+   file end with a newline?`) and give the options the refinement and the code suggest.
+   End each question with a suggested default and a one-line reason (`Suggested: (a),
+   it matches how the profile page does it.`), so the user only answers where they
+   disagree. The suggestion is not a decision: wait for the user's reply.
+3. Record every answer as a numbered decision (D1, D2, ...) in the plan, with the
+   question number and its source: `D1. (Q1) <question>: <answer>. Source: user,
+   2026-09-29.` A reply like "rest as suggested" accepts every remaining default;
+   record those as `Source: user (accepted default), <date>`. A question the reply
+   doesn't cover, and doesn't accept in bulk, is still open. Decisions that come from
+   the code, not from a question, have no Q.
```

**Saves.** In #3, round 1 had 18 questions with options only. The user handed some back ("not sure what that means", "I dont know", T:149), which forced an explanation round (T:162). Round 3 re-listed open items (T:173). About 10 answers just accepted what was proposed. Defaults with a reason should save one or two question rounds per plan. In #3 each round waited minutes for the user.

**Costs.** Anchoring: the user may accept a default they would have questioned. The one-line reason makes the default easy to argue with, and nothing is decided without a reply (AC11).

### C7. `/plan-tdd-feature` and `/refine`: check earlier decisions first

`.claude/skills/plan-tdd-feature/SKILL.md`, section 3:

```diff
-1. Check whether it's already answered: in the conversation, in `$ARGUMENTS`, in an
-   existing plan file, or because the code now settles it. Note where the answer came
-   from.
+1. Check whether it's already answered: in the conversation, in `$ARGUMENTS`, in an
+   existing plan file, in the `## Decisions` of earlier `plans/feature-*-plan.md`, or
+   because the code now settles it. Note where the answer came from, and cite an
+   earlier ticket's decision by ticket and number (`ticket-3 D1`) instead of asking again.
```

`.claude/skills/refine/SKILL.md`, the Open questions template:

```diff
 ## Open questions
 Things the codebase can't answer, including behaviour the acceptance criteria couldn't
-pin down. Phrase each as a question. Don't answer it or recommend an option.
+pin down. Phrase each as a question. Don't answer it or recommend an option. Before
+listing one, check the `## Decisions` of earlier `plans/feature-*-plan.md`: a question an
+earlier decision settles goes under "Patterns to follow" with its citation (`ticket-3 D1`).
```

**Saves.** The #4 refinement re-asked three questions that ticket-3's D1, D18 and D9 had settled, and the user had to point it out (memory `check-earlier-decisions.md`). That cost a correction round and three questions. Today the rule lives only in one user's memory. In the skill, it travels with the pipeline (#15 D3).

**Costs.** An earlier decision may get applied where the situation has changed. The citation keeps that visible, so the user can reopen it.

### C8. `/plan-tdd-feature`: short paragraphs, detail for a Sonnet build

`.claude/skills/plan-tdd-feature/SKILL.md`, section 5:

```diff
 Write `plans/feature-<slug>-plan.md`. Match the existing plans in `plans/`: short,
-factual, real paths and names. Use these sections in this order:
+factual, real paths and names. Split the text into short paragraphs, one idea each.
+This is about layout, not length: keep every detail the plan needs, and break it up.
+
+- a decision is a short lead sentence, with bullets for its parts;
+- a Test, Red or Green part is two or three sentences, with bullets for lists of
+  fields, routes, files or inputs.
+
+The build may run on a smaller model, so each step names the file, the test names,
+the concrete inputs, the exact red reason and the smallest green. A builder who reads
+only that step should need no question.
+
+Use these sections in this order:
```

**Saves.** In #3 the plan was rewritten in full a second time, partly for the "short paragraphs" preference that arrived after the first write (T:257-284, about 90 s of generation plus a re-read). This change saves that rewrite. It also gives a Sonnet build what it needs, with no stop to ask.

**Costs.** None in safety. Plans may get a little longer for the detail rule.

### C9. `NoReverseMatch` as the red for a new route

`.claude/skills/plan-tdd-feature/SKILL.md`, section 4, Red part:

```diff
   `ended` field". A test that fails for the wrong reason, such as an import error or a
-  typo, proves nothing. If a stub is needed so the test fails on its assertion, that stub
-  belongs to step 0. If some rows already pass because of an earlier step, say which ones.
+  typo, proves nothing. A step that adds a route can name `NoReverseMatch` for that route
+  as its red: don't plan a stub view only to reach an assertion. Any other stub needed so
+  the test fails on its assertion belongs to step 0. If some rows already pass because of
+  an earlier step, say which ones.
```

`.claude/skills/implement-tdd-feature/SKILL.md`, section 4, Red:

```diff
   - A test fails for a different reason (an import error, a typo, a wrong helper): fix
     the test, not the code, and run it again. A test that fails for the wrong reason
     proves nothing about the behaviour.
+  - A step that adds a route: `NoReverseMatch` naming that route is a valid red, and no
+    stub is added to get past it. `NoReverseMatch` naming any other route is a wrong
+    reason: fix it (leave out a link to a later step's route) and run again.
```

The "stop and report it" rule for a test that passes too early stays word for word (AC15).

**Saves.** In #3, steps 1, 6, 7 and 9 added stub views. Steps 1 and 7 each spent an extra call on the stub and a second red run (T:402→409, T:539→543). The step 7 stub also made two rows pass at red, which became a logged deviation. This change saves about 4 calls, roughly 1 to 2 min, on a ticket with several new routes, and removes that kind of early pass.

**Costs.** The red then proves that the route is missing, not that the assertions fail against a real response. An assertion that would pass against any view isn't caught at red. Review still checks assertion strength: the #3 reviewer probed it in a scratchpad.

### C10. One call for green and its record, one log line each, readable failures

`.claude/skills/implement-tdd-feature/SKILL.md`, the build log paragraph:

```diff
 Its first line names the plan, and each run adds a dated heading. Under it, append one
-line for every test, lint, type-check or build command you run: the step, the command,
-and what it showed (`Step 3 red: make test ARGS="-k test_ac7" … 3 failed, all on the
-planned assertion`). Add one line for each stop and each answer the user gave. Progress says
+line per red and one per green for each step, plus one per check in Verification: the
+step, the command, and what it showed (`Step 3 red: make test ARGS="-k test_ac7" … 3
+failed, all on the planned assertion`). A rerun goes into the same line (`… 4 failed on
+the missing template, then 4 failed on the planned assertion`). Add one line for each stop
+and each answer the user gave. Progress says
 where the build stands, and the log shows how it got there: that each test really was
 red first, and what the checks said.
```

Section 4, Red, a new first bullet:

```diff
   **Red** part.
+  - Show enough output to read the failure in the same call: pipe through
+    `2>&1 | tail -n 40`, not `tail -3` or a count of matching lines.
```

Section 4, Record:

```diff
-6. **Record.** Edit the plan:
+6. **Record.** Record in the same Bash call as the green run, so recording never costs a
+   call of its own. Run the suite, and only when it passes, tick, append the log line and
+   replace `Next:`:
+
+   ```bash
+   out=$(make test 2>&1); code=$?; printf '%s\n' "$out" | tail -n 40
+   if [ $code -eq 0 ]; then
+     n=$(printf '%s\n' "$out" | grep -oE '[0-9]+ passed' | tail -1)
+     sed -i 's/^- \[ \] AC7\./- [x] AC7./' plans/feature-<slug>-plan.md
+     echo "- Step 3 green: make test … $n" >> plans/feature-<slug>-build-log.md
+     sed -i "s/^Next: step 3\.\$/Step 3 done: $n.\nNext: step 4./" plans/feature-<slug>-plan.md
+   fi
+   ```
+
+   Use the project's suite command in place of `make test`. A deviation from the plan
+   gets its own Edit to Progress afterwards. What the record holds:
```

(The three bullets under Record stay as they are. "Append the step's commands and results to the build log, if you haven't as you went" becomes "Append the step's red and green lines to the build log".)

**As changed by review.** D25, D26, D30 to D32 and D35 changed C10 after the user OK'd it. Once steps 17, 18 and 20 are built, the shipped text reads as follows.

The output rule sits at the top of section 4 (D26):

```markdown
**Output.** For every test, lint, type-check or build command, show enough output to read
a failure in the same call: pipe through `2>&1 | tail -n 40`, not `tail -3` or a count of
matching lines.
```

Green and Refactor each end with a line on the Record call (D25):

```markdown
   When the step's Refactor is "none", this run is the Record call (step 6).
…
   again; this run is the Record call. "None" means none.
```

Record (D25, D30, D31):

```markdown
6. **Record.** Record in the step's last whole-suite run (Green's, or Refactor's), in the
   same Bash call, so recording never costs a call of its own. Only when the suite passes:
   tick, append the step's red line (written from the red run you saw) and green line,
   and move `Next:`. Check that Progress really changed:

   ```bash
   out=$(make test 2>&1); code=$?; printf '%s\n' "$out" | tail -n 40
   if [ $code -eq 0 ]; then
     n=$(printf '%s\n' "$out" | grep -oE '[0-9]+ passed' | tail -1)
     plan=plans/feature-<slug>-plan.md; log=plans/feature-<slug>-build-log.md
     sed -i 's/^- \[ \] AC7\./- [x] AC7./' "$plan"
     printf '%s\n' '- Step 3 red: make test ARGS="-k test_ac7" … 3 failed, all on the planned assertion' \
       "- Step 3 green: make test … $n" >> "$log"
     sed -i "/^## Progress/,/^## /s/Next: step 3\./Step 3 done: $n, 42 before the build.\nNext: step 4./" "$plan"
     sed -n '/^## Progress/,/^## /p' "$plan" | grep -q "Next: step 4\." || echo "Progress NOT updated: fix it with an Edit"
   fi
   ```

   Use the project's suite command in place of `make test`. After the last step, write
   `Next: verify.` instead (and check for that); section 7 replaces it with `Built on`.
   A deviation from the plan gets its own Edit to Progress afterwards. What the record holds:
   …
   - Update **Progress**: which step is done, the test count against the baseline
     (`Step 3 done: 51 passed, 42 before the build.`), …
```

**Saves.** In #3:

- steps 1, 3, 4, 7 and 8 recorded in a separate call after green (T:433, 466, 486, 558, 577);
- four failures were filtered too tightly and needed a second call to read (T:349→353, T:596→604, T:614→618, T:953→957);
- step 1 had four log lines.

That is about 9 calls per first build. The #3 build averaged about 11 s per call (49 calls in about 9 min), so this saves roughly 1.5 to 2 min per first build, less on Sonnet and in rework runs, which already recorded inside the green call. The log is also shorter.

**Costs.**

- A rerun's details are folded into one line, so the log is less granular.
- The log still shows red before green for every step, which is what the reviewer checks (`review-tdd/SKILL.md:72-73`).
- The record only fires on a passing run, so nothing is ticked on red.

### C11. `/review-tdd`: plan-wording fixes without a plan stage

`.claude/skills/review-tdd/SKILL.md`, section 4, the route table:

```diff
 | The plan or its criteria are wrong or incomplete | `plan`: re-run `/plan-tdd-feature` |
+| Only the plan's wording is off; no criterion, decision meaning or step changes | `plan-text`: fixed in the plan by this skill |
 | The refinement's facts about the codebase are wrong | `refine`: re-run `/refine` |
```

Section 6, after "Edit `plans/feature-<slug>-plan.md` only. …":

```diff
+For an accepted `plan-text` finding, make the wording fix in the plan yourself and mark
+the finding `→ plan updated <date>`. If the fix turns out to change a criterion, a
+decision's meaning or a step, it is a `plan` finding instead.
```

**Saves.** In #3, R7 (D26's wording) went through a `/plan-tdd-feature` run plus two card moves (T:695, T:718). That costs about one stage, roughly 2 to 3 min, and two moves each time it happens.

**Costs.** `/plan-tdd-feature`'s own pass (re-reading context, `/unslop`) doesn't run for that fix. The route is limited to wording, and the user still accepts the finding first.

### C12. CLAUDE.md: the models and the changed rules

`CLAUDE.md`, Pipeline section, after the stage table:

```diff
 | 7   | `/ship`                  | a commit of the staged changes                                                  | committed, or a test/lint failure                   |
+
+Models: each skill sets its own in frontmatter. `/refine`, `/plan-tdd-feature`,
+`/review-tdd` and `/manager-tdd` run on Opus at high effort, and `/implement-tdd-feature`
+on Sonnet at medium. `/refine`'s Explore agents run on Haiku and `/review-tdd`'s reviewer
+on Opus. If a stage runs on the wrong model, set it by hand before the stage:
+`/model opus` and `/effort high`, or `/model sonnet` and `/effort medium` for the build.
```

Rules 4, 5 and 6:

```diff
 4. **`/plan-tdd-feature`** asks the open questions (Q1, Q2, ...), records answers as
-   decisions (D1, ...) and writes one red-green step per behaviour, each naming its ACs.
+   decisions (D1, ...) and writes one red-green step per behaviour, each naming its ACs.
+   Each question carries a suggested default; "rest as suggested" accepts the rest.
```

```diff
 5. **`/implement-tdd-feature`** builds the plan step by step: tests first, seen red for
-   the planned reason, then the smallest green, then the whole suite. It only builds what
+   the planned reason (for a new route, `NoReverseMatch` for that route), then the
+   smallest green, then the whole suite. It only builds what
```

```diff
-   each finding (implement, plan, refine, user, follow-up) and writes only the plan. It
+   each finding (implement, plan, plan-text, refine, user, follow-up) and writes only the plan. It
```

**Saves.** No time. CLAUDE.md stays true to the skills (D12), and the manual fallback is written down (D2, AC8).

**Costs.** None.

## Step 1: C1, AC4 (text), refine

**Test.** Read checks on `.claude/skills/refine/SKILL.md`:

- `sed -n 1,8p` shows `model: opus` and `effort: high` above `allowed-tools`.
- `grep -n "model: haiku"` finds the section 3 line.

**Red.** Neither line exists: no SKILL.md has a `model:` key.

**Green.** Apply C1, if Q16 OK'd it. If C1 was rejected, skip the step and say so in Progress.

**Refactor.** None.

## Step 2: C2, plan-tdd-feature frontmatter

**Test.** `sed -n 1,8p .claude/skills/plan-tdd-feature/SKILL.md` shows `model: opus` and `effort: high`, and `allowed-tools` has no `AskUserQuestion`.

**Red.** No model line, and `AskUserQuestion` is in `allowed-tools` (line 5).

**Green.** Apply C2.

**Refactor.** None.

## Step 3: C3, implement-tdd-feature frontmatter

**Test.** `sed -n 1,8p .claude/skills/implement-tdd-feature/SKILL.md` shows `model: sonnet` and `effort: medium`.

**Red.** No model line.

**Green.** Apply C3.

**Refactor.** None.

## Step 4: C4, review-tdd frontmatter and reviewer

**Test.** Read checks on `.claude/skills/review-tdd/SKILL.md`:

- `sed -n 1,9p` shows `model: opus` and `effort: high`;
- `grep -n "general-purpose\` agent with \`model: opus\`"` finds section 3.

**Red.** Neither exists.

**Green.** Apply C4.

**Refactor.** None.

## Step 5: C5, manager-tdd frontmatter

**Test.** `sed -n 1,9p .claude/skills/manager-tdd/SKILL.md` shows `model: opus` and `effort: high`.

**Red.** No model line.

**Green.** Apply C5.

**Refactor.** None.

## Step 6: C6, AC9, AC10, AC11, AC20, plan questions

**Test.** Read checks on `.claude/skills/plan-tdd-feature/SKILL.md`:

- AC9: `grep -n "suggested default and a one-line reason"` finds section 3.
- AC10: `grep -n "AskUserQuestion"` finds only the line "Never use `AskUserQuestion`".
- AC11: `grep -n "The suggestion is not a decision"` and `grep -n "is still open"` both match.
- AC20: `grep -n "accepted default"` matches.
- `grep -n "Don't mark one option as"` finds nothing.

**Red.** The section 3 text at lines 75-83 says to use `AskUserQuestion` and not to recommend. None of the new lines exist.

**Green.** Apply C6.

**Refactor.** None.

## Step 7: C7, C8, AC16, AC17, AC22, plan shape and earlier decisions

**Test.** Read checks:

- AC22: `grep -n "earlier \`plans/feature-\*-plan.md\`"` matches in both `plan-tdd-feature/SKILL.md` section 3 and `refine/SKILL.md`'s Open questions template, and `grep -n "ticket-3 D1"` matches in both.
- AC16: `grep -n "short paragraphs, one idea each"` matches in `plan-tdd-feature/SKILL.md` section 5.
- AC17: `grep -n "should need no question"` matches in the same place.

**Red.** None of these lines exist. `check-earlier-decisions.md` and `plans-short-paragraphs.md` live only in memory.

**Green.** Apply C7 and C8, each one only if Q16 OK'd it.

**Refactor.** None.

## Step 8: C9, AC12, AC15, AC21, the NoReverseMatch red

**Test.** Read checks:

- AC12: `grep -n "NoReverseMatch"` matches in `plan-tdd-feature/SKILL.md` section 4 and in `implement-tdd-feature/SKILL.md` section 4 Red.
- AC21: `grep -n "naming any other route is a wrong"` matches in `implement-tdd-feature/SKILL.md`.
- AC15: `grep -n "stop and report it"` still matches, and `git diff main -- .claude/skills/implement-tdd-feature/SKILL.md` shows no change to that bullet.

**Red.** Neither skill mentions `NoReverseMatch`. AC15's check already passes and guards the rule while editing.

**Green.** Apply C9.

**Refactor.** None.

## Step 9: C10, AC13, AC14, AC23, the record and the log

**Test.** Read checks on `.claude/skills/implement-tdd-feature/SKILL.md`:

- AC13: `grep -n "same Bash call as the green run"` matches section 4 Record, and the snippet is there.
- AC14: `grep -n "one per green for each step"` matches the build log paragraph, and `grep -n "line for every test, lint"` finds nothing.
- AC23: `grep -n "tail -n 40"` matches section 4 Red.
- The snippet's shell parses: copy it to the scratchpad with the placeholders filled in and run `bash -n` on it.

**Red.** The build log paragraph says one line for every command (lines 123-126). Record is a separate edit (lines 176-182).

**Green.** Apply C10.

**Refactor.** None.

## Step 10: C11, C12, AC8, AC24, review route and CLAUDE.md

**Test.** Read checks:

- AC24: `grep -n "plan-text"` matches the route table and section 6 of `review-tdd/SKILL.md`, and the Pipeline rule 6 of `CLAUDE.md`.
- AC8: `grep -n "/model opus"` matches in `CLAUDE.md`'s Pipeline section.
- `grep -n "NoReverseMatch"` and `grep -n "rest as suggested"` match in `CLAUDE.md`, for any of C6 and C9 the user OK'd.

**Red.** None of these lines exist.

**Green.** Apply C11 and C12, each one only if Q16 OK'd it. Drop the lines of C12 that describe a change the user rejected. Then update Progress before stopping (D20).

**Refactor.** None.

## Step 11: AC1, AC2, AC3, AC18, the diff matches the OK'd changes

**Test.**

- `git diff main --stat` lists only the files the OK'd changes name. `git status --porcelain` shows nothing else outside `plans/`.
- `git diff main -- .claude/skills/ CLAUDE.md` shows exactly the OK'd diffs from "The changes", and none of a rejected one.
- AC3, AC18: every change C1 to C12 in this plan has a **Saves** and a **Costs** paragraph. C10 and C11 (item 5) cite #3 evidence, and C7 cites the #4 refinement and the memory rule.

**Red.** None: a check of the steps above. It passes once they are done.

**Green.** None. Fix a mismatch by undoing the extra edit, and log it.

**Refactor.** None.

## Step 12: AC4, AC5, AC6, AC7, AC19, live model check

D2 and D11: only a live session shows which model ran. The user does this check in a new session, and the build lists it at the end.

1. Run `/manager-tdd` on the next ticket, or start the stages by hand.
2. After each stage, open the session's transcript in `~/.claude/projects/-mnt-DATA-Documents--WRK-bootcamp-neuefische-learning-companion/` and read the `model` field of the assistant messages for that stage, and `resolvedModel` for its sub-agents. `/model` with no argument shows the current one.
3. Expected:
   - `/refine`: main messages `claude-opus-5-5`, the three Explore agents a Haiku model;
   - `/plan-tdd-feature`: `claude-opus-5-5`;
   - `/implement-tdd-feature`: `claude-sonnet-5-5`;
   - `/review-tdd`: main messages `claude-opus-5-5`, the reviewer `claude-opus-5-5`;
   - the manager's messages after the build: `claude-opus-5-5`.
4. If a stage ran on the wrong model, the frontmatter didn't take. Use the manual way from CLAUDE.md and record the result in Progress.

## Step 13: rework R1, R2, R3, R5, AC13, AC14, the Record snippet

**Test.** Read checks on `.claude/skills/implement-tdd-feature/SKILL.md`, plus a dry run:

- R2: `grep -n "this run is the Record call"` matches both Green and Refactor, and `grep -n "last whole-suite run"` matches Record.
- R1: the snippet's `sed` has no `^Next:` anchor, and `grep -n 'Progress NOT updated'` matches.
- R3: `grep -n "Step 3 red:"` matches inside the snippet.
- R5: `grep -n "42 before the build"` matches both the snippet and the Progress bullet, and `grep -n "plus 9 new"` finds nothing.
- AC13, AC14: copy the snippet to the scratchpad with `<slug>` set to `demo` and the suite replaced by `printf "5 passed in 1s\n"`. Run it on a dummy plan whose Progress line is `Plan written on 2026-10-02. Nothing built yet. Next: step 3.` (mid-line, as the template writes it) and a `- [ ] AC7.` line. Expected:
  - AC7 is ticked;
  - the plan has `Step 3 done: 5 passed, 42 before the build.` and `Next: step 4.`;
  - the log has a red line and a green line;
  - no warning is printed.

  Then run it again on a plan with no `Next: step 3.`. Expected: it prints `Progress NOT updated: fix it with an Edit`.

**Red.** The current snippet anchors `^Next:`, so on the mid-line dummy Progress stays unchanged and no warning appears. It writes no red line, and the Green and Refactor text has no "Record call" line.

**Green.** Apply the Q18 diff (D25) to Green, Refactor, Record and the Progress bullet.

**Refactor.** None.

## Step 14: rework R4, AC23, the output rule for every command

**Test.**

- `grep -n "tail -n 40"` in `.claude/skills/implement-tdd-feature/SKILL.md` matches one line in a general paragraph above "For every other step:", which names test, lint, type-check and build commands.
- It no longer matches under "2. **Red.**".

**Red.** The rule sits only under Red (line 160).

**Green.** Move the bullet into a paragraph at the top of section 4:

```diff
 Work through step 0 (if the plan has one) and then every numbered step, in order.
+
+**Output.** For every test, lint, type-check or build command, show enough output to read
+a failure in the same call: pipe through `2>&1 | tail -n 40`, not `tail -3` or a count of
+matching lines.
```

and delete the two-line bullet under Red.

**Refactor.** None.

## Step 15: rework R6, plan-text in review-tdd's description and verdict

**Test.** Read checks on `.claude/skills/review-tdd/SKILL.md`:

- `grep -n "plan change, plan-wording fix, refine"` matches the description;
- `grep -n "accepted \`plan-text\` fixes don't block"` matches section 7.

**Red.** Neither line exists. The description lists "plan change, refine, user decision or follow-up ticket".

**Green.** In the description, change "plan change, refine" to "plan change, plan-wording fix, refine". In section 7, after the verdict bullet's "routes open);", add the line `  accepted \`plan-text\` fixes don't block: with only those, the verdict is clean;`.

**Refactor.** None.

## Step 16: rework R7, no link to a later step's route

**Test.** `grep -n "plan a link to a route a later step adds"` matches the Green part of `.claude/skills/plan-tdd-feature/SKILL.md` section 4.

**Red.** No match. Green says only "Don't design ahead for later steps."

**Green.** Replace "Don't design ahead for later steps." in that part with "Don't design ahead for later steps, and don't plan a link to a route a later step adds: leave it to that step, or reorder the steps."

**Refactor.** None.

## Step 17: rework R10, AC13, the snippet only touches Progress

**Test.** Read checks plus two dry runs in the scratchpad:

- `grep -n '/^## Progress/,/^## /s/Next: step 3' .claude/skills/implement-tdd-feature/SKILL.md` matches the snippet's `sed`.
- `grep -n "sed -n '/^## Progress/,/^## /p'"` matches the warning check.
- In `plan-tdd-feature/SKILL.md`'s plan template, `Plan written on <date>. Nothing built yet.` and `Next: step 0 (or step 1).` sit on separate lines.
- Dry run 1: copy `plans/feature-speeding-up-the-pipeline-plan.md` to the scratchpad. Its Progress has no `Next: step 3.`, but step 13's text quotes it. Run the snippet with `<slug>` filled in and `printf "5 passed in 1s\n"` as the suite. Expected:
  - it prints `Progress NOT updated: fix it with an Edit`;
  - `diff` against the original shows one changed line: the snippet's example tick of `- [ ] AC7.`. Step 13's text stays as it is.
- Dry run 2: a plan with `## Progress`, the line `Next: step 3.`, then `## Decisions` and a step text that quotes `Next: step 3.`. Expected:
  - Progress gets `Step 3 done: 5 passed, 42 before the build.` and `Next: step 4.`;
  - the step text is unchanged;
  - no warning.

**Red.** The current `sed` has no Progress range. Dry run 1 rewrites step 13's lines 673 and 679 and prints no warning, as the round 2 reviewer reproduced. The template still has `Next:` mid-line.

**Green.** In the snippet, apply the Q23 diff (D30). In `plan-tdd-feature/SKILL.md`, split the template line `Plan written on <date>. Nothing built yet. Next: step 0 (or step 1).` into two lines (D31).

**Refactor.** None.

## Step 18: rework R11, no `Next:` after the last step

**Test.** `grep -n "After the last step, drop the"` matches the Record part of `.claude/skills/implement-tdd-feature/SKILL.md`, right after "Use the project's suite command in place of `make test`.".

**Red.** No match.

**Green.** After "Use the project's suite command in place of `make test`." add "After the last step, drop the `Next:` line instead; section 7 writes `Built on`." (D32).

**Refactor.** None.

## Step 19: rework R12, AC1, AC2, the diff matches the plan again

**Test.** Re-run step 11's checks after steps 17 and 18:

- `git diff main --stat` lists only the six files in Files.
- The section 4 Output paragraph, Green's and Refactor's Record lines, and the whole Record part of `implement-tdd-feature/SKILL.md` match C10's "As changed by review" text word for word. `diff` the extracted text against the plan's blocks.
- The other changes still match their C diffs.

**Red.** None: a check of steps 17 and 18. It passes once they are done.

**Green.** None. Fix a mismatch by changing the skill to match the plan, and log it.

**Refactor.** None.

## Step 20: rework R13, `Next: verify.` until `Built on`

**Test.** Read checks plus a dry run in the scratchpad:

- `grep -n 'write$'` and `grep -n 'Next: verify.\` instead'` match the Record part of `.claude/skills/implement-tdd-feature/SKILL.md`, and `grep -n "drop the"` finds nothing there.
- Section 7: `grep -n "Replace the \`Next: verify.\` line"` matches.
- `.claude/skills/manager-tdd/SKILL.md`: the stage row reads ``| Plan Progress has a `Next:` line (`Next: step <n>` or `Next: verify`) |``.
- C10's "As changed by review" Record block still `diff`s clean against the shipped Record part.
- Dry run: run the snippet on a plan whose Progress has `Next: step 3.`, but with the last-step form, so the `sed` writes `Next: verify.` and the check looks for it. Expected: Progress has `Step 3 done: … 42 before the build.` and `Next: verify.`, and no warning.

**Red.** Line 206 says "drop the `Next:` line". Section 7 says "Update the plan's Progress to `Built on <date>.`". The manager's row says `Next: step <n>`.

**Green.** Make three edits:

- In Record, replace "After the last step, drop the `Next:` line instead; section 7 writes `Built on`." with "After the last step, write `Next: verify.` instead (and check for that); section 7 replaces it with `Built on`."
- In section 7, replace "Update the plan's Progress to `Built on <date>.`" with "Replace the `Next: verify.` line in Progress with `Built on <date>.`".
- In `manager-tdd/SKILL.md`, replace the row text ``Plan Progress has a `Next: step <n>` `` with ``Plan Progress has a `Next:` line (`Next: step <n>` or `Next: verify`) ``.

**Refactor.** None.

## Review

### Round 1, 2026-10-02

- R1. blocker, `.claude/skills/implement-tdd-feature/SKILL.md:195`: the Record `sed` anchors `^Next:`, which the pipeline never writes, so Progress silently stays stale. → fixed in step 13
- R2. should-fix, `.claude/skills/implement-tdd-feature/SKILL.md:185`: Record's "same call as the green run" ignores Refactor's suite run. → fixed in step 13
- R3. should-fix, `.claude/skills/implement-tdd-feature/SKILL.md:194`: the snippet writes no red line. → fixed in step 13
- R4. should-fix, `.claude/skills/implement-tdd-feature/SKILL.md:160`: the output rule covers only Red runs. → fixed in step 14
- R5. nit, `.claude/skills/implement-tdd-feature/SKILL.md:195`: the snippet's Progress format contradicts the bullet below it. → fixed in step 13
- R6. nit, `.claude/skills/review-tdd/SKILL.md:5`: `plan-text` is missing from the description and from section 7's verdict. → fixed in step 15
- R7. nit, `.claude/skills/plan-tdd-feature/SKILL.md:138`: D7's planner side (no link to a later step's route) is missing. → fixed in step 16
- R8. nit, `plans/feature-speeding-up-the-pipeline-plan.md:618`: step 11 and D19 say C7 cites #3. → plan updated 2026-10-02 (D27)
- R9. nit, `plans/feature-speeding-up-the-pipeline-build-log.md:8`: grouped red/green lines for steps 1-5 and 6-9. → no action (D28)

### Round 2, 2026-10-02

- R10. should-fix, `.claude/skills/implement-tdd-feature/SKILL.md:201`: without the anchor, the snippet rewrites every `Next: step 3.` in the plan, and the warning check reads the whole file. → fixed in step 17
- R11. nit, `.claude/skills/implement-tdd-feature/SKILL.md:201`: nothing says to drop `Next:` after the last step. → fixed in step 18
- R12. nit, `plans/feature-speeding-up-the-pipeline-plan.md:411`: C10 still shows the old snippet, and step 11 wasn't re-run after the rework. → plan updated 2026-10-02 (D33), checked in step 19

### Round 3, 2026-10-02

- R13. nit, `.claude/skills/implement-tdd-feature/SKILL.md:206`: after the last step neither `Next:` nor `Built on` is in Progress until section 7, and no manager row matches that. → fixed in step 20

## Files

Changed, each only if its change is OK'd:

- `.claude/skills/refine/SKILL.md`: C1, C7
- `.claude/skills/plan-tdd-feature/SKILL.md`: C2, C6, C7, C8, C9
- `.claude/skills/implement-tdd-feature/SKILL.md`: C3, C9, C10
- `.claude/skills/review-tdd/SKILL.md`: C4, C11
- `.claude/skills/manager-tdd/SKILL.md`: C5, step 20
- `CLAUDE.md`: C12

The plan's own records:

- `plans/feature-speeding-up-the-pipeline-plan.md`: Progress and ticks
- `plans/feature-speeding-up-the-pipeline-build-log.md`: new

For reference: `.claude/skills/*/evals/evals.json` (not changed, D10) and `.claude/hooks/check-plan-progress.sh` (D20).

## Verification

- After each step, run its read checks. They fail before the edit for the reason under Red, and pass after it.
- After step 10, `make test` (64 passed, as before) and `make lint` (clean). No Python changes.
- Step 11's diff check, then step 12's live check, before `/ship`.
