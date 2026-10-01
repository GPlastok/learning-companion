---
name: new-ticket
description: >-
  Creates a GitHub issue from a feature description, in the layout the issue form and /ticket use. Drafts the body from the user's own words, shows the draft, and creates the issue with gh only after the user confirms. Doesn't invent acceptance criteria, doesn't edit or close issues, and doesn't start the pipeline unless asked. Use when the user types /new-ticket, or asks to add, file, create or open a ticket or issue for a feature. To pick up an existing issue, use /ticket instead.
argument-hint: "<feature title, and optionally what it should do, why, or acceptance criteria>"
allowed-tools: Read, Glob, Bash(gh issue create:*), Bash(gh issue view:*), Bash(gh label list:*), Bash(gh auth status:*), Bash(gh --version), Bash(git rev-parse:*), Bash(git remote:*), AskUserQuestion, Skill
---

# New ticket

Write a GitHub issue for a feature and create it in the layout the browser issue form
produces, so `/ticket` can read it back later. This skill is the one place in the
pipeline that writes to GitHub, and it writes only after the user has seen the exact text.
`/ticket` stays read-only for that reason.

The pipeline: **new-ticket**, `/ticket`, `/refine`, `/plan-tdd-feature`,
`/implement-tdd-feature`, `/review-tdd`, `/ship`. `/manager-tdd` can run them in order.

Creating an issue is outward-facing and can't be fully undone. On a public repo everyone
sees it, and deleting it later doesn't remove it from caches or notifications. Never
create it without a clear yes to the draft you showed.

## 1. Read the arguments

Take the feature from `$ARGUMENTS` or the conversation. The user's own words are the only
source for the issue's content. If there's no title and nothing to build one from, ask for
the feature in one sentence.

Sort what the user gave into three parts:

- **Title.** Short, in the user's words, with no prefix like "Feature:".
- **What should it do?** The behaviour from the user's side.
- **Why.** Only if the user said why.
- **Acceptance criteria.** Only items the user wrote as criteria or a checklist, copied
  word for word.

Don't invent criteria, motivation or scope. `/refine` writes criteria from the ticket text
later, and the user reviews them there. A thin ticket is fine. If **What should it do?**
would be empty, ask for it. It's the one required field in the form.

## 2. Find the layout

The headings must match the repo's issue form, so read it instead of assuming:

- Look for `.github/ISSUE_TEMPLATE/*.yml` and `*.yaml` (Glob), and read the form whose
  `labels` or `name` fits a feature.
- GitHub turns each `textarea` field's `label` into a `### <label>` heading in the issue
  body, in the order of the form. Use those labels, in that order.
- Take the default label from the form's `labels` list. Then run `gh label list` and keep
  only labels that exist, because `gh issue create` fails on an unknown label.
- No form found: use `### What should it do?`, `### Why` and `### Acceptance criteria`,
  with no label.

Leave out any section the user gave no content for, including the whole acceptance
criteria section. Don't copy the form's placeholder (`- [ ]` with nothing after it). An
empty checkbox would look to `/ticket` like one supplied criterion. With no criteria
section, `/ticket` knows there are none and `/refine` writes them.

## 3. Check gh can create the issue

Stop at the first failure and say what the user can do about it, in a line or two:

1. `gh --version`. If gh isn't installed, point to https://cli.github.com.
2. `git rev-parse --is-inside-work-tree` and `git remote -v`. gh needs a git repo with a
   GitHub remote. If there's none, suggest `git remote add origin <url>`.
3. `gh auth status`. If gh isn't logged in, suggest `gh auth login`.

## 4. Show the draft and ask

Show the repo (`owner/name`, from `git remote -v`), whether it is public if you know, the
title, the label, and the full body as it will be posted. Then ask whether to create it,
with `AskUserQuestion`: create as shown, change something, or cancel.

- **Change something.** Apply the edit, show the draft again and ask again.
- **Cancel.** Stop and write nothing.

Never skip this step, even when the user's request sounded final. They haven't seen the
layout yet.

## 5. Create the issue

Pass the body on stdin so quotes and newlines survive:

```bash
gh issue create --title "<title>" --label "<label>" --body-file - <<'EOF'
<body>
EOF
```

Leave out `--label` when there's no label. Don't add assignees, milestones or a project:
the board's **Auto-add to project** workflow puts new issues on the board by itself, and
whoever works on it assigns it.

gh prints the issue URL. If the command fails, show the error and stop. Don't retry with
different options on your own.

## 6. Report

In a few lines:

- the issue number, title and URL;
- which sections it has, and that acceptance criteria were left for `/refine` if there
  were none;
- the next step: `/ticket <number>` to start the refinement.

Offer to run `/ticket <number>` but don't run it unprompted. Starting `/refine` launches
three sub-agents, and the user may want to edit the issue first. If the user says yes,
invoke the `ticket` skill with the issue number.

Don't edit, comment on or close the issue afterwards, and never add a `Co-Authored-By`
trailer or any other AI attribution to the issue text.
