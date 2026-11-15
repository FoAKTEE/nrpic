#!/bin/bash
# Stop hook of the NRPIC-cosmology program (brief sections 11.5, 13.1). PROPOSED, NOT INSTALLED
# (decision 0008).
#
# Blocks the end of a turn once (exit code 2, instructions on stderr) when the session's worktree
# has uncommitted changes, or, on a track/core/kb branch, when tracks/<ID>/STATUS.md is older than
# the last commit of the branch that is not in main (STATUS, JOURNAL and HANDOFF excluded). Never
# blocks twice in a row: the input field stop_hook_active (set while Claude continues because of a
# Stop hook) lets the next attempt pass, and, should that field be absent, a marker under
# <main checkout>/locks/stop-gate/ remembers the state already blocked for this session.
# The session's worktree is that of $CLAUDE_PROJECT_DIR, else the input cwd. Outside the nrpic
# repository, and on any internal error, the hook lets the turn end.
set -u
PATH=/usr/local/bin:/usr/bin:/bin
input=$(cat)
eval "$(printf '%s' "$input" | /usr/bin/python3 -I -c '
import json, shlex, sys
try:
    d = json.load(sys.stdin)
except ValueError:
    d = {}
print("active=%s" % ("1" if d.get("stop_hook_active") else "0"))
print("cwd=%s" % shlex.quote(str(d.get("cwd") or "")))
print("sid=%s" % shlex.quote("".join(ch for ch in str(d.get("session_id") or "nosession") if ch.isalnum() or ch in "-_")))
' 2>/dev/null || echo 'active=0; cwd=; sid=nosession')"
[ "$active" = 1 ] && exit 0
dir=${CLAUDE_PROJECT_DIR:-$cwd}
[ -n "$dir" ] && [ -d "$dir" ] || exit 0
root=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || exit 0
common=$(git -C "$root" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || exit 0
home=$(dirname "$common")
[ -f "$home/coord/CHARTER.md" ] && [ -d "$home/tracks" ] || exit 0
branch=$(git -C "$root" rev-parse --abbrev-ref HEAD 2>/dev/null) || exit 0
case $branch in
  main) owner=orch ;;
  track/*) owner=${branch#track/}; owner=${owner%%--*} ;;
  core/*) owner=core ;;
  kb/*) owner=kb ;;
  *) owner= ;;
esac

problems=()
dirty=$(git -C "$root" status --porcelain --untracked-files=normal 2>/dev/null)
if [ -n "$dirty" ]; then
  n=$(printf '%s\n' "$dirty" | wc -l)
  problems+=("$n uncommitted path(s) in $root, e.g. $(printf '%s\n' "$dirty" | head -3 | cut -c4- | tr '\n' ' ')")
fi
if [ -n "$owner" ] && [ "$owner" != orch ] && [ -f "$root/tracks/$owner/STATUS.md" ]; then
  st=$(git -C "$root" log -1 --format=%ct -- "tracks/$owner/STATUS.md" 2>/dev/null)
  code=$(git -C "$root" log -1 --no-merges --format=%ct main..HEAD -- . \
           ":(exclude)tracks/$owner/STATUS.md" ":(exclude)tracks/$owner/JOURNAL.md" \
           ":(exclude)tracks/$owner/HANDOFF.md" 2>/dev/null)
  if [ -n "$code" ] && [ "${st:-0}" -lt "$code" ]; then
    problems+=("tracks/$owner/STATUS.md is older than the last commit on $branch")
  fi
fi
[ ${#problems[@]} -eq 0 ] && exit 0

# loop guard independent of stop_hook_active: block each state of the worktree once per session
state=$(printf '%s\n%s\n%s' "$(git -C "$root" rev-parse HEAD 2>/dev/null)" "$dirty" "${problems[*]}" | sha256sum | cut -c1-16)
mark_dir="$home/locks/stop-gate"
mkdir -p "$mark_dir" 2>/dev/null
mark="$mark_dir/$sid"
if [ -f "$mark" ] && [ "$(cat "$mark" 2>/dev/null)" = "$state" ]; then
  exit 0
fi
printf '%s' "$state" > "$mark" 2>/dev/null

{
  echo "Stop gate (harness/hooks/stop_gate.sh): before ending, persist the session (brief 11.3, CLAUDE.md rule 2)."
  for p in "${problems[@]}"; do echo "  - $p"; done
  if [ "$owner" = orch ] || [ -z "$owner" ]; then
    echo "Commit what is finished, path-limited (git add <paths> && git commit -m '...' -- <paths>), and push main."
  else
    echo "Do, in this order: rewrite tracks/$owner/STATUS.md (60 lines at most), append one entry to"
    echo "tracks/$owner/JOURNAL.md, rewrite tracks/$owner/HANDOFF.md for a reader with no memory, commit"
    echo "(path-limited, never git add -A of other owners' files), then git push -u origin $branch."
  fi
  echo "Files that must not be committed: move them to scratch/${owner:-<ID>}/tmp/. This gate blocks once; the next stop passes."
} >&2
exit 2
