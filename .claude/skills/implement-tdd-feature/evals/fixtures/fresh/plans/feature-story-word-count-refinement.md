# Story word count: refinement

## Context
In `/adventure` ("The Study"), the top bar shows how many words the open story has so far, counting the player's lines and the model's story text. There is no branch yet; the repo is on `main`.

## Progress
Refinement done on 2026-09-29. The user answered the open questions the same day (see the plan's Decisions). Nothing planned or built yet. Next: write the plan with `/plan-tdd-feature`.
Plan written on 2026-09-29: plans/feature-story-word-count-plan.md.

## Acceptance criteria
- [ ] Words separated by single spaces are counted: `The nurse smiles.` is 3 words.
- [ ] Runs of spaces, tabs and newlines count as one separator.
- [ ] Empty or whitespace-only text is 0 words.
- [ ] A story's count adds the player's messages and each beat's `story` text. Option labels and JSON keys aren't counted.
- [ ] A beat that isn't valid JSON adds 0 words, and counting doesn't throw.
- [ ] The top bar shows the open story's count at its right end.
- [ ] The label is singular for one word (`1 word`) and uses a thousands separator (`1,234 words`).
- [ ] With no story open, the top bar shows no count.

## Files and functions
- `src/app/components/AdventureApp.tsx`: `AdventureApp` owns `stories` (localStorage key `"stories"`) and `activeStory`, and renders the `<header>` with the `The Study` `<h1>`.
- `src/app/components/Adventure.tsx:19`: `parseBeat(content)` does `JSON.parse` on an assistant message and returns `Partial<Beat>`. It isn't exported.
- `src/lib/adventure.ts`: `Story` and `Beat` types.
- `src/app/actions.ts:37`: `Message = { role: "user" | "assistant" | "system"; content: string }`.

## Current data shapes
- A story is `Story` (`src/lib/adventure.ts`) with `messages: Message[]`.
- Assistant messages hold the raw beat JSON string, `{ story, options, ended }` (decision 0009).

## Tests
- Vitest, `environment: "node"` (`vitest.config.ts`), so there's no DOM. Tests are `*.test.ts` next to the code.
- `npm test` runs the suite (42 tests today). `npx vitest run <file> -t "<name>"` runs one test.
- Pattern: `src/lib/ascii.test.ts`, small local helpers at the top of the file, one `describe` per function.
- A change must also pass `npm run lint`, `npx tsc --noEmit` and `npm run build`.

## Patterns to follow
- Pure logic in `src/lib/`, tested next to it (`src/lib/ascii.ts`, `src/lib/ascii.test.ts`).
- `src/lib/openai.ts` is `server-only`; a module used by `AdventureApp` (a `"use client"` file) must not import it.

## Open questions
1. What counts as a word: any run of non-whitespace characters, or only runs with a letter in them?
2. Where in the top bar does the count go?
3. Does the count include the reply while it's still streaming?
