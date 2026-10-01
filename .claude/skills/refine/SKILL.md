---
name: refine
description: Studies the codebase before a new feature is built. Launches three sub-agents at once to survey the route structure, the data layer and the test setup, then writes the findings and the feature's acceptance criteria to plans/feature-<feature-name>-refinement.md. Does not plan or implement. Use when the user types /refine, says "use refine" or says "study the codebase", including when they name a feature they are about to build.
argument-hint: "<feature name, and optionally a sentence on what it should do, or acceptance criteria you already have>"
allowed-tools: Agent, Read, Glob, Grep, Write, Bash(ls:*), Bash(git log:*), Bash(git status:*)
---

# Refine

Write down what the codebase looks like before anyone builds a feature in it. Three
sub-agents survey different areas at the same time, and you merge their reports into one
refinement file. A later session can start from that file instead of re-reading the repo,
so it needs real paths, real names and real shapes.

This skill defines and describes. It doesn't plan or implement. Apart from the
refinement file, it is read-only: no edits to source, tests or docs, and no code. Don't
propose a design, an approach, a list of changes or build steps. Planning comes after the
user has read this file and answered its open questions. A plan written earlier gets
built on guesses.

Assume nothing about the project. Find the stack, the layout and the conventions in the
repo.

## 1. Pin down the feature

Take the feature from `$ARGUMENTS` or from the conversation. If there's no name, ask
for one. The file name and the survey both depend on it.

Check whether the input already carries acceptance criteria, whatever the source: a
checklist or an "Acceptance criteria" section in `$ARGUMENTS`, in text the user pasted, or
handed over by another skill. Note where they came from if the input says so (a ticket
number, a document, "pasted by the user"). Don't look anywhere else for them: no ticket
system, no network. If there are none, you write the criteria yourself in step 5, as usual.

Turn the name into a kebab-case slug: `inventory-drop` gives
`plans/feature-inventory-drop-refinement.md`. Create `plans/` if it's missing.

If the file exists, read it and ask whether to update or replace it. It may hold answers
the user already gave.

## 2. Read the ground rules

Before launching anything, read the project's own guidance and pass the relevant parts to
the sub-agents:

- Root-level instruction and overview files (`CLAUDE.md`, `AGENTS.md`, `README*`) and
  whatever they point to.
- The manifest and config files that show the stack (`package.json`, `pyproject.toml`,
  `go.mod`, `Cargo.toml`, `Gemfile` and the like).
- Existing plans, decision records and notes, wherever the project keeps them. Read the
  ones near the feature's area. If there's a list of known problems, note it so the
  survey doesn't report them as new.

If the guidance says the framework differs from what you remember, or points to bundled
docs, tell the sub-agents to read those docs.

## 3. Launch three sub-agents in one message

Send all three Agent calls in a single message so they run concurrently. Use the `Explore`
agent type. Give each one the feature description, any supplied criteria and the stack
details from step 2. Tell each to report facts with `path:line` references, to write "not found" instead of
guessing, and to find its own starting points, since you don't know the layout.

**Routes and entry points.** How the app is entered and divided: routes, pages, handlers,
commands or endpoints. Where server and client code meet, the signatures of the main
functions at that boundary, and how requests and responses (streaming included) are
wired. Shared components and modules. Report what sits near the feature's area, not where
new code should go.

**Data layer.** Where data comes from, lives and changes: databases, storage, external
APIs or SDK clients, schemas, models, types, constants, configuration, and how history or
state gets passed around. Quote type or schema excerpts instead of paraphrasing them.

**Tests.** The runner and its config, where tests live, the commands for the full suite
and for one test, and how a typical test is built (fixtures, mocks, naming). What is
covered, and what isn't near the feature's area. Include the lint, type-check and build
commands, since a change has to pass those too.

Ask each sub-agent to list the existing patterns in its area that a new feature should
copy.

## 4. Synthesize

Merge the three reports. If they disagree or a claim looks doubtful, check the file
yourself with a Read or Grep. Keep what the feature needs and cut the rest. Don't paste
the reports in whole.

## 5. Write the refinement file

Write `plans/feature-<slug>-refinement.md` with these sections in this order. Match the
tone of any plans already in the repo: short and factual. If a section doesn't apply,
say so in one line.

```markdown
# <Feature name>: refinement

## Context
What the feature is, in two or three sentences, and the branch if there is one. If the
description or criteria came from somewhere identifiable, add a line `Source: <where>`.

## Progress
Refinement done on <date>. Nothing planned or built yet. Next: the user answers the open
questions, then a plan is written.

## Acceptance criteria
A checklist of what must be true for the feature to be done, written as behaviour someone
can observe: what a user sees or does, what the system returns or stores. Each item
gives a clear pass or fail in a test or a manual check and says nothing about how the
feature is built. Cover the normal path, edge cases and failures (errors, empty state,
reload, partial or interrupted results). Draw them from the feature description and from
how existing features behave. If the description leaves a behaviour open, put it under
"Open questions" and don't invent a criterion.

- [ ] <criterion>

If the input supplied criteria, split the section in two so the user can tell them apart:

- `### Supplied` holds the given criteria in their original wording, unticked. Don't
  rewrite, merge, reorder or drop any. If one is vague, untestable or contradicts what the
  codebase does, keep it as given and add an open question about it.
- `### Added by refinement` holds only criteria the description and the survey show are
  missing, such as an edge case or failure the supplied list doesn't cover. Leave it
  out if there are none. Never repeat a supplied criterion here.

## Files and functions
Paths and function names in the area the feature touches or sits next to, grouped by
area. One line each on what it does today.

## Current data shapes
Type, schema or record excerpts, and where each is stored or produced.

## Tests
How tests are written and run: commands, file locations, the structure of a typical test,
gaps near this feature, and the other checks a change has to pass.

## Patterns to follow
Existing conventions the feature should copy, each with a `path:line` example, plus the
constraints from the project's guidance files and decision records.

## Open questions
Things the codebase can't answer, including behaviour the acceptance criteria couldn't
pin down. Phrase each as a question. Don't answer it or recommend an option.

1. <question>
```

Use today's date. Every path and name in the file must come from something you or a
sub-agent read. Anything you couldn't find goes under "Open questions".

Always number the open questions (`1.`, `2.`, …), in the file and in every reply that
lists them, so the user can answer by number. When a round of answers leaves some
questions open, renumber the rest from 1.

## 6. Report

Reply in a few lines: the path of the file, the two or three findings that matter most,
and the open questions to answer before planning. Don't print the file, and don't offer
a plan or start building.
