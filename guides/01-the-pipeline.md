# 1. The pipeline

Before any Django: how the work was done. Every feature in this project goes through the same fixed steps, and each step leaves a file behind. This chapter follows ticket #3 from issue to merge.

## The idea in one paragraph

Nothing is built that a GitHub issue doesn't ask for. The issue is studied, questions are answered, a plan is written, and only then is code written, always test first. A fresh reviewer then reads the result. You commit, push and merge.

## The stages

| Stage | Command | What it leaves behind |
|---|---|---|
| Write the ticket | `/new-ticket` | a GitHub issue |
| Pick it up | `/ticket 3` | nothing; hands over to `/refine` |
| Study the code | `/refine` | `plans/feature-<name>-refinement.md` |
| Plan | `/plan-tdd-feature` | `plans/feature-<name>-plan.md` |
| Build | `/implement-tdd-feature` | code, tests, and `plans/feature-<name>-build-log.md` |
| Review | `/review-tdd` | a Review section in the plan |
| Commit | `/ship` | one git commit |

`/manager-tdd` runs these in order for you and moves the card on the GitHub board.

The files in `plans/` are the memory of the pipeline. If a session stops halfway, the next one reads the plan's **Progress** section and carries on from there.

## Stage by stage, with ticket #3

### The ticket

Issue #3 was short:

> Wire up the framework's built-in auth (Django auth). Create a custom User model. Add a Profile model linked to the user with name, cohort, and a list of focus_area tags.

It had one acceptance criterion: "Confirm you can sign up, log out, and log back in, and that the profile page only shows your own data."

### Refinement: look before you build

`/refine` sent three helpers to survey the repo at the same time: one for URLs and views, one for data and models, one for tests. Their findings went into the [refinement file](../plans/feature-authentication-and-profile-management-refinement.md).

Two findings mattered most:

- There were no models and no migrations yet. That's the perfect moment for a custom user (chapter 3 explains why).
- A local `db.sqlite3` already had Django's default user table in it. It would have to be recreated.

The refinement also added criteria the ticket didn't mention, like "a wrong password shows an error". And it ended with **18 open questions**: things the code couldn't answer, such as "username or email login?".

Refinement never answers its own questions. Guessing would turn into a test that's wrong from the first line.

### Planning: answer the questions, then cut the work into steps

`/plan-tdd-feature` asked you those questions. Each answer became a numbered **decision**: D1, D2 and so on. For example:

- D1: User, Profile and Cohort live in a new `accounts` app; Tag lives in `core`.
- D5: people log in with username or email.
- D13: only the owner and staff can see a profile; everyone else gets 403.

Then the plan split the work into **steps**. Each step covers one behaviour and names the criteria it proves. Every step has four parts:

- **Test**: the exact tests to write, with names like `test_ac8_login_accepts_username_or_email`.
- **Red**: why those tests fail before the code exists.
- **Green**: the smallest code that makes them pass.
- **Refactor**: cleanup, usually none.

### Building: red, green, refactor

This is test-driven development (TDD). For every step:

1. Write the test.
2. Run it and watch it **fail**, for the reason the plan predicted. That's "red".
3. Write the least code that makes it pass. That's "green".
4. Run the whole suite, so nothing else broke.

Why insist on seeing red first? A test that has never failed might not test anything. If it passes before the code exists, either the behaviour was already there, or the test checks the wrong thing.

The build log records every red and green run. Here's a real pair from step 5:

```text
- Step 5 red: … "ada" row passed (planned), 2 email rows failed with an empty redirect chain.
- Step 5 green: UsernameOrEmailBackend + AUTHENTICATION_BACKENDS. make test … 31 passed.
```

When the plan and reality disagreed, the build stopped and asked. In step 0, `ruff` rejected Django's own generated migration files. That became question Q21, and your answer became decision D29.

### Review: a second pair of eyes

`/review-tdd` gives the finished code to a fresh helper that didn't write it. It checks:

- bugs and edge cases;
- whether each test would really fail if its behaviour broke;
- whether the build stayed inside the plan.

Each finding gets a route: fix it now (a new "rework" step), change the plan, ask you, or make a follow-up ticket.

Ticket #3 went through four review rounds. Chapter 11 walks through what they found. It's worth reading: those are exactly the bugs that slip through when you write code yourself.

### Ship, push, merge

`/ship` runs the tests and the linter, and commits only what you staged. Pushing and opening the pull request are yours. The PR description says `Closes #3`, so merging closes the issue and moves its card to Done.

## The board

The GitHub project board mirrors the stages:

| Column | Means |
|---|---|
| Todo | the issue exists |
| Refined | the refinement or plan exists |
| In Progress | the plan is being built |
| Review | being reviewed, or waiting for `/ship` |
| Done | the PR merged |

Ticket #3's card went back and forth a few times. After each review round with findings it moved to In Progress for the fixes, and back to Review afterwards.

## Try it yourself

1. Open [the #3 plan](../plans/feature-authentication-and-profile-management-plan.md). Read the Decisions section and find the one about the cohort (D9). Then find the step that builds it.
2. Open [the build log](../plans/feature-authentication-and-profile-management-build-log.md). Find a step where some tests passed at "red" and the log explains why that was expected.
3. Pick any test in `tests/`. From its name (`test_ac<n>_...`), find its criterion in the plan.
