#!/usr/bin/env bash
# Sequencer of A-emd-pbh card runs (decision 0025 item 5): keeps at most two card jobs of this
# owner (Slurm job names starting with "A-") queued or running, and submits the next entry of a
# queue file through harness/bin/nrpic-run when fewer are present. Each queue line holds the
# arguments of `nrpic-run submit` (shell words; '#' lines and blank lines are skipped).
#
#   setsid nohup tracks/A-emd-pbh/threshold_ball/scripts/sequencer.sh <queue file> <state dir> \
#       > <state dir>/nohup.out 2>&1 < /dev/null &
#
# State dir (under scratch/A-emd-pbh/): sequencer.pid, sequencer.log, done.txt (line number,
# time, exit status, run id), STOP (create it to make the sequencer exit at its next check).
# A refused submission (dirty package, budget, lock) is retried at the next check, at most
# five times per line; then the line is marked skipped. The worktree must stay on branch
# track/A-emd-pbh with the package tracks/A-emd-pbh/threshold_ball committed.
set -uo pipefail
QUEUE=$(readlink -f "$1"); STATE=$(readlink -f "$2")
WT=/data/haiyangw/nrpic/wt/A-emd-pbh
MAXJOBS=${MAXJOBS:-2}; PERIOD=${PERIOD:-300}
mkdir -p "$STATE"; touch "$STATE/done.txt"
echo $$ > "$STATE/sequencer.pid"
log() { echo "$(date '+%F %T') $*" >> "$STATE/sequencer.log"; }
log "start pid $$ queue $QUEUE"
declare -A tries
lastwait=""
while true; do
  if [ -e "$STATE/STOP" ]; then log "STOP file found; exit"; rm -f "$STATE/sequencer.pid"; exit 0; fi
  n=$(squeue -h -u "$USER" -o '%j' 2>/dev/null | grep -c '^A-')
  if [ "$n" -ge "$MAXJOBS" ]; then
    # decision 0030 item 4: say why the queue waits (once per change of the reason)
    w="waiting: $n A-jobs queued or running (limit $MAXJOBS)"
    if [ "$w" != "$lastwait" ]; then log "$w"; lastwait=$w; fi
  fi
  if [ "$n" -lt "$MAXJOBS" ]; then
    lastwait=""
    lineno=0; next=""
    while IFS= read -r line || [ -n "$line" ]; do
      lineno=$((lineno + 1))
      case "$line" in ''|'#'*) continue;; esac
      if grep -q "^$lineno " "$STATE/done.txt"; then continue; fi
      next=$line; break
    done < "$QUEUE"
    if [ -z "$next" ]; then log "queue finished; exit"; rm -f "$STATE/sequencer.pid"; exit 0; fi
    log "line $lineno: $n A-jobs in squeue, submitting"
    out=$(cd "$WT" && eval "harness/bin/nrpic-run submit $next" 2>&1); rc=$?
    echo "$out" | tail -5 >> "$STATE/sequencer.log"
    rid=$(echo "$out" | grep -o 'registered A-[0-9-]*-[0-9a-f]*' | head -1 | cut -d' ' -f2)
    if [ "$rc" -eq 0 ] && [ -n "$rid" ]; then
      echo "$lineno $(date '+%F_%T') rc=0 $rid" >> "$STATE/done.txt"; log "line $lineno -> $rid"
      sleep 60; continue
    fi
    tries[$lineno]=$(( ${tries[$lineno]:-0} + 1 ))
    log "line $lineno refused (rc=$rc, try ${tries[$lineno]})"
    if [ "${tries[$lineno]}" -ge 5 ]; then
      echo "$lineno $(date '+%F_%T') rc=$rc skipped" >> "$STATE/done.txt"; log "line $lineno skipped"
    fi
  fi
  sleep "$PERIOD"
done
