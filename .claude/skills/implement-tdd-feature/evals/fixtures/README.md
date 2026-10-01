# Fixtures

A small made-up feature, "story word count": three pure functions in `src/lib/wordCount.ts` and a count in the `/adventure` top bar. The plan names only files and functions that exist in the repo, so a staleness check passes on a clean checkout.

Each directory mirrors the repo layout. To set up an eval, check out a clean copy of the repo (a `git worktree` works), then copy each file the eval lists to the path after `fixtures/<scenario>/`. Drop the `.fixture` suffix as you copy: `fixtures/resume/src/lib/wordCount.ts.fixture` goes to `src/lib/wordCount.ts`. The suffix stops the project's test runner and linter from picking the fixture code up inside `.claude/`.

- `fresh/`: the refinement, and a plan with nothing built. Step 4 is a manual check in the middle, and step 6 has a second one.
- `resume/`: the plan with steps 0–2 marked done, and the source and tests as they stand after step 2 (47 tests pass).
- `false-red/`: the plan with steps 0–1 done, but `countWords` already has step 2's code. Step 2's tests pass as soon as they're written.

Where an eval's `expected_output` says "Setup: on branch `feature/story-word-count`", create that branch in the copy before running it. Otherwise leave it on `main`.
