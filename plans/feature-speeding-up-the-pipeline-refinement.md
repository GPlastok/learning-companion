# Speeding up the pipeline: refinement

## Context

Make the TDD pipeline faster by changing the skills in `.claude/skills/`. The ticket names four changes: model routing per stage, plan questions with suggested defaults, a lighter red/green record in `/implement-tdd-feature`, and plans that stay short yet detailed enough for a Sonnet build. A fifth item asks for any other round trips seen in the #3 run that added no safety.

Each change is shown as a diff and edited only after the user's OK. Each one also states the time it saves and what it costs in safety or quality.

This is a tooling change, like #15. No Django code changes. The #3 precondition is met: PR #12 merged as `382f7aa`. No branch yet; `main` is checked out.

Source: #10 (https://github.com/GPlastok/learning-companion/issues/10)

## Progress

Refinement done on 2026-10-02. Nothing planned or built yet. Next: the user answers the open questions, then a plan is written.

Plan written on 2026-10-02: plans/feature-speeding-up-the-pipeline-plan.md.

Built on 2026-10-02, see plans/feature-speeding-up-the-pipeline-plan.md.

Built on 2026-10-02 after review round 1, see plans/feature-speeding-up-the-pipeline-plan.md.

Built on 2026-10-02 after review round 2, see plans/feature-speeding-up-the-pipeline-plan.md.

Built on 2026-10-02 after review round 3, see plans/feature-speeding-up-the-pipeline-plan.md.

## Acceptance criteria

The ticket has no criteria section or checklist, so refinement wrote these from the ticket text.

**How changes are made**

- [ ] Every change to a file under `.claude/skills/` is shown to the user as a diff before the file is edited.
- [ ] No skill file changes until the user has OK'd that change. A change the user rejects is not made.
- [ ] Every proposed change states how much time it saves and what it costs in safety or quality.

**Model routing (ticket item 1)**

- [ ] `/refine`'s three Explore sub-agents run on Haiku.
- [ ] `/plan-tdd-feature` runs on Opus at high effort.
- [ ] `/implement-tdd-feature` runs on Sonnet at medium effort.
- [ ] `/review-tdd`'s reviewer sub-agent runs on Opus.
- [ ] Where a stage's model or effort can't be set from the skill, the user is told the manual way (`/model`, `/effort`) to use before that stage.

**Plan questions (ticket item 2)**

- [ ] Each question `/plan-tdd-feature` asks carries a suggested default with a one-line reason.
- [ ] Questions are asked in plain text as a numbered list, never through `AskUserQuestion`.
- [ ] No answer is recorded as a decision unless the user gave it. The user still decides every question.

**Red, green and the record (ticket item 3)**

- [ ] For a step that adds a new route, a red run that fails with `NoReverseMatch` for that route counts as the planned red. No stub is added only to get an assertion failure.
- [ ] Progress and the build log are updated in the same tool call as the step's green run.
- [ ] The build log has one line per red run and one per green run.
- [ ] A test that passes when the plan says it should fail still stops the build.

**Plans (ticket item 4)**

- [ ] Plans `/plan-tdd-feature` writes are in short paragraphs: one idea each, decisions as a lead sentence plus bullets, and Test, Red and Green parts of two or three sentences.
- [ ] Each plan step still names the file, test names, concrete inputs, the red reason and the smallest green, so a Sonnet build needs no extra question.

**Other round trips (ticket item 5)**

- [ ] Every other round-trip cost proposed from the #3 run cites its evidence from that run, and states its time saved and its safety or quality cost, like items 1 to 4.

## Files and functions

The paths below are relative to `.claude/` unless written in full.

**Skill frontmatter today**

- No SKILL.md has a `model:` or `effort:` key. Only `skills/ship/SKILL.md` has `disable-model-invocation: true`.
- `skills/plan-tdd-feature/SKILL.md:5`: `allowed-tools` includes `AskUserQuestion`.
- `skills/implement-tdd-feature/SKILL.md:5`: `allowed-tools: Read, Glob, Grep, Write, Edit, Skill, AskUserQuestion, Bash`.

**Sub-agent launches**

- `skills/refine/SKILL.md:67-90`, section 3: three `Explore` agents in one message. No model is named.
- `skills/review-tdd/SKILL.md:49-88`, section 3: one `general-purpose` reviewer. No model is named.
  - `:58-62`: the reviewer calls the `code-review` skill at medium effort, which starts a nested agent.
  - `:92` (section 4): the main session reads the line behind every finding again.
- `skills/manager-tdd/SKILL.md:111`: every stage is invoked through the `Skill` tool in the same session.

**Plan questions**

- `skills/plan-tdd-feature/SKILL.md:72-80`: check whether a question is already answered, then ask all open ones together.
  - It uses `AskUserQuestion` (up to four per call) when a question has a few natural answers, plain text otherwise.
  - "Don't mark one option as recommended. The refinement deliberately left the choice to the user."
- `skills/plan-tdd-feature/SKILL.md:81-88`: decision format `D1. (Q1) <question>: <answer>. Source: user, <date>.`
- `skills/refine/SKILL.md:152`: refine's open questions don't answer or recommend an option.
- Other skills that use `AskUserQuestion`: `review-tdd/SKILL.md:120-121`, `manager-tdd/SKILL.md:69`, `new-ticket/SKILL.md:72`.

**Red and stubs**

- `skills/plan-tdd-feature/SKILL.md:125-129`: "A test that fails for the wrong reason, such as an import error or a typo, proves nothing. If a stub is needed so the test fails on its assertion, that stub belongs to step 0."
- `skills/implement-tdd-feature/SKILL.md:153-163`: a red for a different reason means fixing the test and running it again. A test that passes early means stopping. Neither skill mentions `NoReverseMatch`.

**Record and build log**

- `skills/implement-tdd-feature/SKILL.md:122-128`: one log line for every test, lint, type-check or build command run, plus one per stop and per answer.
- `skills/implement-tdd-feature/SKILL.md:176-185`, step 6 "Record": tick, append to the log "if you haven't as you went", update Progress. It doesn't say which tool call to use.
- `skills/implement-tdd-feature/SKILL.md:164-172`: the whole suite runs after each Green and after each Refactor that isn't "none".

**Plan shape**

- `skills/plan-tdd-feature/SKILL.md:114-132`: five to twelve steps, and the detail for each part.
- `skills/plan-tdd-feature/SKILL.md:168`: "Match the existing plans in `plans/`: short, factual, real paths and names." There is no rule on paragraph length.
- `skills/plan-tdd-feature/SKILL.md:216-222`: an `/unslop` pass on the plan.

**Hook**

- `hooks/check-plan-progress.sh:15-27`: blocks once if a file outside `plans/`, `.claude/` and `.github/` is newer than the newest plan. It checks timestamps only, not the build log.

**Memory rules the skills don't carry**

These sit in `/home/georgios/.claude/projects/-mnt-DATA-Documents--WRK-bootcamp-neuefische-learning-companion/memory/`:

- `plain-text-choices.md`: no `AskUserQuestion`, "even where a skill says to use AskUserQuestion".
- `discuss-choices-first.md`: options with implications and "my lean". This conflicts with `plan-tdd-feature/SKILL.md:79-80`.
- `plans-short-paragraphs.md`: short lead sentences plus bullets, Test/Red/Green parts of two or three sentences.
- `check-earlier-decisions.md`: read earlier plans' Decisions before asking. No SKILL.md mentions it.

## Current data shapes

**Model and effort settings**

Per the Claude Code docs (claude-code-guide agent, https://code.claude.com/docs/en/skills and `/sub-agents`):

- Skill frontmatter supports `model` (aliases `opus`, `sonnet`, `haiku`, `fable`, or full IDs) and `effort` (`low`, `medium`, `high`, `xhigh`, `max`).
- The docs don't say whether a skill's `model` lasts beyond the skill, or applies when another skill calls it through the `Skill` tool.
- The Agent tool takes a `model` parameter. On the Anthropic API, `Explore` defaults to Opus.
- Manual commands: `/model <model>` and `/effort <level>`.

**What the #3 run used**

These come from transcript `8da063d8-….jsonl`, one session that ran every stage inline through `/manager-tdd`.

- Model: every assistant message and all 11 sub-agents ran `claude-opus-5-5`.
- Explore agents: 33-46 s each, 4 tool uses each.
- Reviewer rounds: 117-212 s each. Each round also ran a nested `code-review` agent for about a minute.
- Implement, first run: 49 tool calls, 46 of them Bash, in about 9 min of active work.
  - About 16 full-suite and 14 targeted test runs.
  - The plan and log were updated through Bash heredocs and a scratchpad `rec.py`. There were 0 Edit calls on them.
- Plan stage: about 30 questions in 6 rounds, none with a default. About 10 answers just accepted what was proposed ("choose core if it is sensible", "q7, q16 ok. if you say so"). The plan was written in full twice.

**Build log line** (`plans/feature-authentication-and-profile-management-build-log.md:14-17`)

```
- Step 1 red: make test ARGS="tests/test_signup.py" … 4 failed with NoReverseMatch for `signup` (planned first red). Added the route and a stub.
- Step 1 red: same command … 4 failed: no `accounts/signup.html` in templates, no form in context, empty redirect chain (planned).
- Step 1 green: make test … 4 failed: NoReverseMatch for `login` (template link, route comes in step 3) and no database access. …
- Step 1 green: make test … 15 passed.
```

**Plan formats** (auth plan, 768 lines, 22 steps, 34 decisions)

- Decisions: `D3. (Q2a) Primary keys are integers … Source: user, 2026-10-01.`
- AC ticks: `- [x] AC<n>. <text> → step <n>`.
- Steps: `## Step <n>: AC<x>, <title>`, with `**Test.**`, `**Red.**`, `**Green.**` and `**Refactor.**` parts.
- Progress: one paragraph per event, 37 of them by the end.

## Round-trip costs seen in the #3 run

These are facts from the survey for ticket item 5, not proposals.

1. **Stub-only red reruns.** Steps 1 and 7 each added an `HttpResponse("")` stub after `NoReverseMatch` and ran red again in a separate call. Steps 6 and 9 added stubs too. The step 7 stub made two rows pass at red, which was logged as a deviation (build log line 29). Steps 3 and 10 accepted `NoReverseMatch` without trouble. Plan lines 337, 449, 483 and 527 prescribed the stubs.
2. **Separate record calls.** Steps 1, 3, 4, 7 and 8 updated Progress and the log in their own call after green. Steps 2, 5, 6, 9 and 10 did it inside the green call.
3. **Output filtered too tightly, then rerun.** `tail -3` or `grep | uniq -c` hid the failure, and a second call showed it. This happened four times (T:349→353, T:596→604, T:614→618, T:953→957).
4. **Questions with no default.** Round 1 had 18 questions with options only. The user handed some back ("not sure what that means", "I dont know"), and a round of explanations followed. Round 3 re-listed open items ("I thought i answered already").
5. **The plan rewritten in full twice.** The second rewrite came from a changed answer and a style preference that arrived after the plan was written.
6. **Findings checked twice.** The main session re-read every finding the reviewer had confirmed (`review-tdd/SKILL.md:92`). The reviewer also re-ran the suite and lint that implement had just run.
7. **A one-line wording fix routed to the plan.** R7 (D26 wording) went through `/plan-tdd-feature` plus two card moves.
8. **Review rounds past the cap.** There were four rounds. The user asked for rounds 3 and 4 (`manager-tdd/SKILL.md:139` caps the manager at two).
9. **One false-positive Stop-hook block** after non-plan work in `guides/` (T:1291). There were none during implement.
10. **Card-move prompts.** About 11 permission waits. #15 (`fd0fd6d`) already fixed this.

"T:" is a line in the transcript.

## Tests

- pytest + pytest-django (`pyproject.toml:6-8`). `make test` runs 64 passing tests today. One test: `make test ARGS="-k test_ac3"`. `make lint` runs ruff, which checks Python only.
- No test reads `.claude/skills/`. `tests/test_docs.py:20-26` reads `CLAUDE.md` and the `Makefile` and is the closest pattern. No CI exists.
- Skill evals: `skills/implement-tdd-feature/evals/evals.json` (7 evals, fixtures `fresh/`, `resume/`, `false-red/`) and `skills/plan-tdd-feature/evals/evals.json` (3 evals). Nothing in the repo runs them.
  - The fixtures are a TypeScript app (`src/lib/wordCount.ts`, `npm run dev`), not Django.
  - plan-tdd-feature eval id 1 asserts "Red parts name an assertion failure reason, not an import/missing-module error".
  - That eval lists `fixtures/feature-story-export-refinement.md`, which doesn't exist.
- How #15 checked skill-text changes (`plans/feature-project-card-moves-without-permission-plan.md`):
  - grep and jq read checks per AC, with Red and Green;
  - negative greps prove old wording is gone;
  - `git diff main -- <skill dir>` is empty for skills that must not change;
  - `make test` and `make lint` stay as before;
  - live checks in a new session for what only a session shows.
  - D7 scoped "no pytest test" to #15 only.
- Which model ran a stage shows only in a live session (the transcript's `model` field, or `/model` status). That makes it a manual check.

## Patterns to follow

- Skill-text tickets verify with read checks plus live checks, as in #15 (`plans/feature-project-card-moves-without-permission-plan.md:105-188`).
- Frontmatter keys sit between `name`/`description`/`argument-hint` and `allowed-tools`, as in `skills/ship/SKILL.md:2-6`.
- Skills point to the project's guidance generically ("`CLAUDE.md`, `AGENTS.md` and what they point to"), for example `skills/implement-tdd-feature/SKILL.md:22`. None names a memory file.
- Numbered Q/D format, carried across stages: `skills/plan-tdd-feature/SKILL.md:63-88`.
- CLAUDE.md: a stack or tooling change is raised as a question with options. CLAUDE.md's Pipeline section (`CLAUDE.md:44-96`) describes each stage, so it may need to match the skills.
- Memory rules: plain-text numbered choices, options with a lean, short paragraphs, and earlier decisions cited instead of re-asked.
- Earlier decisions:
  - #15 D7 scoped "no pytest test" to that ticket.
  - #15 D3: the pipeline in `.claude/` is meant to be copied to other projects. Rules go in shared files.

## Open questions

1. Where does the user's OK on each diff happen in the pipeline? The ticket says to show each change as a diff and wait for the OK before editing, but `/implement-tdd-feature` edits files itself and doesn't stop between steps.
2. `/manager-tdd` runs every stage inline in one session through the `Skill` tool. The docs don't say whether a skill's `model`/`effort` frontmatter applies when it is invoked that way, or whether it persists into the next stage. How should this be settled: a live check, or the manual `/model` route from the start?
3. Should the reviewer's Opus be set explicitly (Agent `model: opus`), or left to inherit the session's model, which would be Sonnet if implement switched it?
4. Do the suggested defaults replace the rule "Don't mark one option as recommended" (`plan-tdd-feature/SKILL.md:79-80`) only in `/plan-tdd-feature`, or also in `/refine`'s open questions (`refine/SKILL.md:152`)?
5. When the user answers only the questions they disagree with, may a reply like "rest as suggested" accept all remaining defaults at once? Or must each question get an explicit answer?
6. Should "no `AskUserQuestion`" apply only to `/plan-tdd-feature`, as the ticket says? Or also to `/review-tdd`, `/manager-tdd` and `/new-ticket`, which the memory rule covers?
7. Does the `NoReverseMatch` rule apply only to a route the step itself adds? What about a link to a route a later step adds, like the `login` link in #3 step 1's green?
8. "One line per red and green": does a step whose red or green runs twice (a test fixed, or a green that needed a second pass) still get one line each, or one per run?
9. How is "detailed enough for a Sonnet build" judged: by a live Sonnet build of the next ticket, or by review against the plan skill's step rules?
10. Should the skill evals be updated to match? plan eval id 1 asserts the opposite of the `NoReverseMatch` rule, and the evals' fixtures are TypeScript and partly missing.
11. Is a pytest test wanted for any of this, or does #15's approach of read checks plus live checks (its D7) apply to this ticket too?
12. Should CLAUDE.md's Pipeline section be updated with the skill changes, or only the skills themselves?
13. How should the time saved be stated: from the #3 transcript's counts and durations, or as a rough estimate per change?
