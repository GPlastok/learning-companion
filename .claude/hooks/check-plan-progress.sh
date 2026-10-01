#!/usr/bin/env bash
# Stop hook: if source or test files changed after the newest TDD plan was last written,
# remind Claude once to update the plan's Progress before stopping. The pipeline resumes
# from Progress, so a stale Progress makes the next session redo or skip work.

input=$(cat)
# Already reminded in this stop sequence: let it stop.
[[ $(jq -r '.stop_hook_active // false' <<<"$input") == true ]] && exit 0

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
shopt -s nullglob
plans=(plans/feature-*-plan.md)
(( ${#plans[@]} )) || exit 0

newest_plan=$(stat -c %Y "${plans[@]}" | sort -n | tail -1)

# Changed or new files outside plans/, .claude/ and .github/.
newest_code=0
while IFS= read -r f; do
  [[ -f $f ]] || continue
  t=$(stat -c %Y -- "$f")
  (( t > newest_code )) && newest_code=$t
done < <(git status --porcelain --untracked-files=all 2>/dev/null | cut -c4- | sed 's/.* -> //' | grep -vE '^(plans|\.claude|\.github)/')

if (( newest_code > newest_plan )); then
  jq -n '{decision: "block", reason: "Code changed after the newest plan in plans/ was last updated. If this work is a step of a TDD plan, update that plan'"'"'s Progress (step done, test count, next step) and the build log before stopping. If it is not part of a plan, stop without changes."}'
fi
exit 0
