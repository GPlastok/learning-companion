---
name: ticket
description: >-
  Starts a feature from a GitHub issue. Fetches the issue with gh, pulls out its acceptance criteria if it has any, and hands the ticket text, the criteria and `Source: #<n>` to /refine, which writes the refinement file. Read-only on GitHub: doesn't create tickets, edit them or move board cards. Use when the user types /ticket, gives an issue number or issue URL and wants to start work on it, or says "pick up ticket 12", "work on issue #12" or "refine the ticket". If the user has no ticket and just names a feature, use /refine directly.
argument-hint: "<issue number or URL> [feature name, if the title is too long]"
allowed-tools: Skill, Bash(gh issue view:*), Bash(gh auth status:*), Bash(gh --version), Bash(git rev-parse:*), Bash(git remote:*)
---

# Ticket

Turn a GitHub issue into the input `/refine` needs, then run `/refine`. This skill is the
front of the pipeline: ticket, `/refine`, `/plan-tdd-feature`, `/implement-tdd-feature`,
`/review-tdd`, `/ship`. `/manager-tdd` can run them in order. It fetches and hands over. The codebase survey and the criteria work belong to
`/refine`, so don't do either here.

Only read from GitHub. Don't comment on the issue, change its labels or state, move its
card on a project board, or create new issues. The board's own workflows move cards when
issues close, and a skill that writes to GitHub would surprise the user.

## 1. Read the arguments

Take the issue from `$ARGUMENTS`. Accept `12`, `#12` or an issue URL
(`https://github.com/<owner>/<repo>/issues/12`). Anything after the issue is a feature
name the user prefers over the issue title.

If there's no issue number, stop and ask for one. Don't list open issues and pick one.

## 2. Check that gh can reach the issue

Run these in order and stop at the first that fails. Report what failed and what the user
can do about it, in one or two lines, and don't run `/refine`:

1. `gh --version`. If gh isn't installed, say so and point to https://cli.github.com.
2. `git rev-parse --is-inside-work-tree` and `git remote -v`. Skip this for a full issue
   URL, since the URL names the repo. With a bare number gh needs a git repo with a
   GitHub remote. If there's none, say so and suggest `git init` plus
   `git remote add origin <url>`, or passing the full issue URL.
3. `gh auth status`. If gh isn't logged in, suggest `gh auth login`.

## 3. Fetch the issue

```bash
gh issue view <number or URL> --json number,title,body,labels,comments,state,url
```

- If gh says the issue doesn't exist (or the number is a pull request), report that and
  stop. Don't guess a nearby number.
- If the issue is closed, say so in the report but carry on. The user may be reopening
  the work.

## 4. Find the acceptance criteria

Look in the issue body only. Comments are discussion, and treating them as criteria would
put words in the ticket's author's mouth.

The criteria are, in this order of preference:

1. The section under a heading or bold label that names them: "Acceptance criteria",
   "AC", "Definition of done", in any case and at any heading level. The section ends at
   the next heading of the same or a higher level, or at the end of the body.
2. Otherwise, a checklist (`- [ ]` or `- [x]` items) in the body.

Copy them word for word, ticked state included. Don't reword, merge, split or reorder:
`/refine` keeps supplied criteria as given so the user can tell them from the ones it
adds, and that only works if they reach it unchanged.

If there's neither a section nor a checklist, there are no criteria. That's fine. Don't
write any and don't ask the user for them. `/refine` writes them from the ticket text,
and the user judges them in the refinement file.

## 5. Hand over to /refine

Use the feature name from step 1 if the user gave one, otherwise the issue title. Call
the `refine` skill with arguments in this shape:

```text
<feature name>

Source: #<number> (<issue url>)

Ticket text:
<the issue body, minus the criteria section if you extracted one>

Labels: <comma-separated labels, or "none">

Comments:
<each comment as "- <author>: <text>", or "none">

Acceptance criteria (from ticket #<number>, verbatim):
<the criteria exactly as extracted>
```

Leave out the whole "Acceptance criteria" block when the ticket has none. Don't write
"none" there, since `/refine` would then look for criteria that aren't there.

Then let `/refine` run to the end. Its report is the answer the user wants.

## 6. Report

After `/refine` finishes, add one or two lines before its report:

- the issue number and title, and whether it is closed;
- whether criteria came from the ticket (and how many), or whether `/refine` wrote them.

Don't summarise the ticket again, and don't start planning.
