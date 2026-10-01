#!/usr/bin/env bash
# PreToolUse hook (Bash): blocks commits, PRs, issues and comments that carry AI
# attribution, such as a Co-Authored-By trailer or a "Generated with Claude Code" line.
# Checks the command text (inline -m and heredocs) and any file passed with -F/--file/--body-file.

cmd=$(jq -r '.tool_input.command // empty')

# Only commands that write a message somewhere.
if ! grep -qE '(^|[;&|[:space:]])(git[[:space:]]+commit|gh[[:space:]]+(pr|issue)[[:space:]]+(create|edit|comment))' <<<"$cmd"; then
  exit 0
fi

text=$cmd
# Message files: git commit -F <file> / --file=<file>, gh --body-file <file> / -F <file>.
while read -r f; do
  [[ -n $f && $f != "-" && -f $f ]] && text+=$'\n'$(cat -- "$f")
done < <(grep -oE '(-F|--file|--body-file)[= ]+[^ ;&|]+' <<<"$cmd" | sed -E 's/^(-F|--file|--body-file)[= ]+//; s/^["'\'']//; s/["'\'']$//')

if grep -qiE 'co-authored-by:|generated with \[?claude' <<<"$text"; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny",
    permissionDecisionReason: "AI attribution found (Co-Authored-By or \"Generated with Claude\"). This project never adds AI attribution to commits, PRs or issues. Remove the line and run the command again."}}'
fi
exit 0
