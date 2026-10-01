# Story word count: TDD plan

## Context
In `/adventure`, the top bar shows the open story's word count. The counting and the label go in a new `src/lib/wordCount.ts` and are built test-first. The header change is in `AdventureApp.tsx` and is checked by hand, because Vitest runs in a `node` environment with no DOM. Survey and criteria: [feature-story-word-count-refinement.md](feature-story-word-count-refinement.md).

**In scope:** `countWords`, `storyWordCount`, `wordCountLabel`, and the count in the `/adventure` top bar.
**Out of scope:** a count on `/chat`, per-beat counts, and new test tooling.

## Progress
Plan written on 2026-09-29.
Step 0 done: stubs and helpers in place, 42 tests pass.
Step 1 done: 43 tests pass, 42 before the build plus 1 new.
Next: step 2.

## Decisions
D1. (Q1) What counts as a word? Any run of non-whitespace characters, punctuation included. Source: user, 2026-09-29.
D2. (Q2) Where does the count go? At the right end of the top bar, on the same line as the title. Source: user, 2026-09-29.
D3. (Q3) Does it include a streaming reply? No. It counts the stored `story.messages` only, so it changes once per turn. Source: user, 2026-09-29.
D4. Vitest runs with `environment: "node"`, so the header is a manual check. Source: code, `vitest.config.ts`.

## Acceptance criteria
- [x] AC1. Words separated by single spaces are counted: `The nurse smiles.` is 3 words. → step 1
- [ ] AC2. Runs of spaces, tabs and newlines count as one separator. → step 2
- [ ] AC3. Empty or whitespace-only text is 0 words. → step 2
- [ ] AC4. A story's count adds the player's messages and each beat's `story` text. Option labels and JSON keys aren't counted. → step 3
- [ ] AC5. A beat that isn't valid JSON adds 0 words, and counting doesn't throw. → step 5
- [ ] AC6. The top bar shows the open story's count at its right end. → step 4
- [ ] AC7. The label is singular for one word (`1 word`) and uses a thousands separator (`1,234 words`). → step 6
- [ ] AC8. With no story open, the top bar shows no count. → step 4

## Step 0: groundwork
Create `src/lib/wordCount.ts` with the real signatures, each throwing `new Error("not implemented")`:
- `countWords(text: string): number`
- `storyWordCount(messages: Message[]): number`, with `import type { Message } from "@/app/actions"`
- `wordCountLabel(count: number): string`

Create `src/lib/wordCount.test.ts` with the imports and two helpers:
```ts
const user = (content: string): Message => ({ role: "user", content });
const beat = (b: { story: string; options?: string[]; ended?: boolean }): Message => ({
  role: "assistant",
  content: JSON.stringify({ story: b.story, options: b.options ?? ["Go on"], ended: b.ended ?? false }),
});
```
No tests yet. `npm test` still shows the 42 existing tests green.

## Step 1: AC1, plain words
**Test.** `describe("countWords")`, `it("AC1. counts words separated by single spaces")`: `countWords("The nurse smiles.")` is `3`.
**Red.** Fails: `countWords` throws `not implemented`.
**Green.** In `countWords`: `return text.split(" ").length;`
**Refactor.** None.

## Step 2: AC2, AC3, whitespace and empty text
**Test.** In `describe("countWords")`, one `it.each` table of `[name, text, expected]`:
- `"AC2. treats a run of spaces as one separator"`, `"The  nurse   smiles."`, `3`
- `"AC2. treats newlines and tabs as separators"`, `"The nurse\n\nsmiles.\tNow."`, `4`
- `"AC3. counts empty text as 0"`, `""`, `0`
- `"AC3. counts whitespace-only text as 0"`, `"  \n\t "`, `0`

**Red.** Every row fails on the assertion: `split(" ")` counts the empty strings between spaces and doesn't split on newlines or tabs.
**Green.** In `countWords`: `return text.split(/\s+/).filter(Boolean).length;`
**Refactor.** None.

## Step 3: AC4, a story's count
**Test.** `describe("storyWordCount")`:
- `it("AC4. adds the player's lines and each beat's story text")`: `[user("I wake up"), beat({ story: "The nurse smiles.", options: ["Follow her", "Run away"] }), user("Follow her")]` is `8`.
- `it("AC4. counts no option labels or JSON keys")`: `[beat({ story: "Dark.", options: ["One two three four"] })]` is `1`.
- `it("AC4. is 0 for a story with no messages")`: `[]` is `0`.

**Red.** Every test fails: `storyWordCount` throws `not implemented`.
**Green.** In `storyWordCount`, sum over `messages`: a `user` message adds `countWords(content)`, an `assistant` message adds `countWords(JSON.parse(content).story ?? "")`, anything else adds `0`.
**Refactor.** None.

## Step 4: AC6, AC8, the count in the top bar (manual)
**Green.** In `AdventureApp.tsx`, add `justify-between` to the `<header>`'s classes. After the `<h1>`, render `{activeStory && <p className="pb-2 text-sm text-gray-500">{storyWordCount(activeStory.messages)} words</p>}`, importing `storyWordCount` from `@/lib/wordCount`.
**Manual check.**
1. AC6: start `npm run dev`, open `/adventure`, click "New adventure" and send `I wake up`. Expected: once the reply has finished, the right end of the top bar shows `<n> words`, where `n` is 3 plus the words in the reply's story text. It doesn't change while the reply streams (D3).
2. AC8: in DevTools → Application → Local Storage, delete `"stories"` and reload. Expected: with no story open, the top bar shows only "The Study".

## Step 5: AC5, broken beats
**Test.** In `describe("storyWordCount")`:
- `it("AC5. adds 0 for a beat that isn't valid JSON")`: `[user("Start"), { role: "assistant", content: "not json" }, user("Go on")]` is `3`.
- `it("AC5. adds 0 for a beat with no story yet")`: `[user("Start"), { role: "assistant", content: "{}" }]` is `1`.

**Red.** The first fails: `JSON.parse` throws `SyntaxError` out of `storyWordCount`. The second already passes, because of `?? ""`.
**Green.** In `storyWordCount`, wrap the `JSON.parse` in `try`/`catch` and add `0` on a parse error.
**Refactor.** None.

## Step 6: AC7, the label
**Test.** `describe("wordCountLabel")`, one `it.each` table of `[name, count, expected]`:
- `"AC7. plural for 0"`, `0`, `"0 words"`
- `"AC7. singular for 1"`, `1`, `"1 word"`
- `"AC7. plural for 2"`, `2`, `"2 words"`
- `"AC7. thousands separator"`, `1234`, `"1,234 words"`

**Red.** Every row fails: `wordCountLabel` throws `not implemented`.
**Green.** In `wordCountLabel`: `` return `${count.toLocaleString("en-US")} ${count === 1 ? "word" : "words"}`; ``. In `AdventureApp.tsx`, replace `{storyWordCount(activeStory.messages)} words` with `{wordCountLabel(storyWordCount(activeStory.messages))}`.
**Refactor.** None.
**Manual check.** Re-run step 4's check 1. Expected: the label reads like `57 words`, with no double "words".

## Files
**New**
- `src/lib/wordCount.ts`: `countWords`, `storyWordCount`, `wordCountLabel`.
- `src/lib/wordCount.test.ts`: the tests for steps 1–3, 5 and 6.

**Changed**
- `src/app/components/AdventureApp.tsx`: the count in the header (steps 4 and 6).

**Reference**
- `src/lib/ascii.test.ts`: test layout to copy.
- `src/app/actions.ts:37`: `Message`.

## Verification
- After writing a step's tests: `npx vitest run src/lib/wordCount.test.ts` shows them red for the reason in the step's **Red** part.
- After each **Green**: `npm test` is all green, the 42 existing tests plus the new ones.
- After steps 4 and 6: the manual checks behave as described.
- At the end:
  - `npm run lint`: 0 errors (the 2 existing warnings in `ChatApp.tsx:8` may remain).
  - `npx tsc --noEmit`: clean.
  - `npm run build`: succeeds.
