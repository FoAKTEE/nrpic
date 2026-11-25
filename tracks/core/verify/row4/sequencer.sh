#!/usr/bin/env bash
# Sequencer of core's card jobs (decision 0025 item 5): at most two card jobs of owner core
# eligible at a time. The chains are registered and submitted at once with nrpic-run, the
# first segments beyond two are held at once (scontrol hold); this process releases them one
# at a time, in the order given, whenever fewer than two core jobs (job names "core-...") are
# running or pending without a hold, at two looks 90 s apart (a chain's own resubmission
# between two segments takes seconds). It touches no file of a worktree and runs no git.
#
#   setsid nohup tracks/core/verify/row4/sequencer.sh <jobid> [<jobid> ...] \
#       >> /data/haiyangw/nrpic/scratch/core/tmp/lead_b5/sequencer.log 2>&1 < /dev/null &
#
# Stop it: touch the stop file (default /data/haiyangw/nrpic/scratch/core/tmp/lead_b5/
# sequencer.stop; the environment variable SEQ_STOP names another; it exits at its next look
# and releases nothing more), or kill its process id (in the log's first line).
# Every tenth look (15 min) it logs why the next job still waits (decision 0030 item 4).
set -u
STOP=${SEQ_STOP:-/data/haiyangw/nrpic/scratch/core/tmp/lead_b5/sequencer.stop}
pending=("$@")
low=0
looks=0
echo "$(date -u +%FT%TZ) sequencer pid $$ starts; held jobs in order: ${pending[*]}"
eligible() {
  squeue -h -u "$(id -un)" -o "%i %j %T %r" 2>/dev/null | awk '
    $2 ~ /^core-/ { if ($3 == "PENDING" && $4 ~ /Held/) next; if ($3 == "PENDING" || $3 == "RUNNING" || $3 == "CONFIGURING" || $3 == "COMPLETING") n++ }
    END { print n + 0 }'
}
while ((${#pending[@]})); do
  if [ -e "$STOP" ]; then echo "$(date -u +%FT%TZ) stop file found; exiting with ${pending[*]} still held"; exit 0; fi
  j=${pending[0]}
  if ! squeue -h -j "$j" -o "%i" 2>/dev/null | grep -q "^$j$"; then
    echo "$(date -u +%FT%TZ) job $j no longer queued; dropped"; pending=("${pending[@]:1}"); continue
  fi
  n=$(eligible)
  if [ "$n" -lt 2 ]; then low=$((low + 1)); else low=0; fi
  if [ "$low" -ge 2 ]; then
    if scontrol release "$j"; then echo "$(date -u +%FT%TZ) eligible core jobs $n: released $j"
    else echo "$(date -u +%FT%TZ) release of $j failed"; fi
    pending=("${pending[@]:1}"); low=0
  elif [ $((looks % 10)) -eq 0 ]; then
    echo "$(date -u +%FT%TZ) waiting: $j held; $n core job(s) eligible (release below 2, two looks in a row); still held: ${pending[*]}"
  fi
  looks=$((looks + 1))
  sleep 90
done
echo "$(date -u +%FT%TZ) all jobs released; sequencer exits"
