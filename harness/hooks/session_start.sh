#!/bin/bash
# SessionStart hook of the NRPIC-cosmology program (brief sections 11.3 rule 6, 11.5). PROPOSED, NOT
# INSTALLED (decision 0008).
#
# Prints the start-up brief of the session's worktree (at most 40 lines; Claude Code adds standard
# output of a SessionStart hook to the context): `harness/bin/nrpic-ctx brief --hook` when the branch
# has it, else a short fallback (owner, branch, commits main is ahead, STATUS lines, HANDOFF head).
# If $CLAUDE_ENV_FILE is set, appends `export NRPIC_*=...` lines for later Bash calls
# (`harness/bin/nrpic-env vars --export`): a convenience, not isolation (brief 11.4).
# The worktree is that of $CLAUDE_PROJECT_DIR, else the input cwd. Always exits 0.
set -u
PATH=/usr/local/bin:/usr/bin:/bin
input=$(cat)
cwd=$(printf '%s' "$input" | /usr/bin/python3 -I -c '
import json, sys
try:
    print(json.load(sys.stdin).get("cwd") or "")
except ValueError:
    print("")' 2>/dev/null)
dir=${CLAUDE_PROJECT_DIR:-$cwd}
[ -n "$dir" ] && [ -d "$dir" ] || exit 0
root=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || exit 0
common=$(git -C "$root" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || exit 0
home=$(dirname "$common")
[ -f "$home/coord/CHARTER.md" ] && [ -d "$home/tracks" ] || exit 0

{
  if [ -x "$root/harness/bin/nrpic-ctx" ]; then
    printf '%s' "$input" | (cd "$root" && timeout 20 harness/bin/nrpic-ctx brief --hook 2>&1)
  else
    branch=$(git -C "$root" rev-parse --abbrev-ref HEAD 2>/dev/null)
    case $branch in
      main) owner=orch ;; track/*) owner=${branch#track/}; owner=${owner%%--*} ;;
      core/*) owner=core ;; kb/*) owner=kb ;; *) owner=unknown ;;
    esac
    behind=$(git -C "$root" rev-list --count HEAD..main 2>/dev/null || echo "?")
    echo "nrpic session: owner $owner, branch $branch, worktree $root"
    echo "main is $behind commit(s) ahead of this branch$( [ "$behind" != 0 ] && echo ': run git merge --no-edit main first')."
    echo "harness/bin/nrpic-ctx is not on this branch yet: rules in CLAUDE.md and harness/RULES.md."
    st="$root/tracks/$owner/STATUS.md"
    if [ -f "$st" ]; then
      echo "--- tracks/$owner/STATUS.md"
      grep -E '^(gate|headline|last-result|next|blockers|needs|budget):' "$st" | cut -c1-160
    fi
    ho="$root/tracks/$owner/HANDOFF.md"
    if [ -f "$ho" ]; then
      echo "--- tracks/$owner/HANDOFF.md (first lines)"
      head -n 15 "$ho" | cut -c1-160
    fi
  fi
} | head -n 40

if [ -n "${CLAUDE_ENV_FILE:-}" ] && [ -x "$root/harness/bin/nrpic-env" ]; then
  (cd "$root" && harness/bin/nrpic-env vars --export) >> "$CLAUDE_ENV_FILE" 2>/dev/null
fi
exit 0
