#!/usr/bin/env bash
# Release held card jobs of D-bh-dress one at a time, so that at most two D jobs are eligible
# to run (decision 0025 item 5). Each held job is the FIRST segment of a chain registered with
# `nrpic-run submit --launcher chain` and held at once with `scontrol hold <jobid>`; once
# released, the chain resubmits its own later segments (job name = its run id, "D-...").
#
# Usage:  setsid nohup tracks/D-bh-dress/g2long/tools/sequencer.sh <dir> > /dev/null 2>&1 &
#   <dir>/queue     lines "<run_id> <jobid>" in the order of release (written by the lead)
#   <dir>/released  appended "<date> <run_id> <jobid>" as each is released
#   <dir>/log       one line per check that changes something, and every hour
#   <dir>/pid       the sequencer's process id
#   <dir>/STOP      create this file to make the sequencer exit at its next check
# See: tail <dir>/log; squeue -u $USER. Stop: touch <dir>/STOP (or kill <pid>, by number).
# Release by hand instead: scontrol release <jobid>.
set -u
DIR=${1:?usage: sequencer.sh <dir>}
INTERVAL=${INTERVAL:-120}
MAXACTIVE=${MAXACTIVE:-2}
echo $$ > "$DIR/pid"
touch "$DIR/released"
log() { echo "$(date '+%F %T %Z') $*" >> "$DIR/log"; }
log "start pid $$ interval ${INTERVAL}s max active $MAXACTIVE"
last_hour=""
while true; do
  if [[ -e $DIR/STOP ]]; then log "STOP file: exit"; rm -f "$DIR/pid"; exit 0; fi
  # next queued entry not yet released
  next=""
  while read -r rid jid; do
    [[ -z ${rid:-} || $rid == \#* ]] && continue
    grep -q " $rid $jid\$" "$DIR/released" && continue
    next="$rid $jid"; break
  done < "$DIR/queue"
  if [[ -z $next ]]; then log "queue empty: every job released; exit"; rm -f "$DIR/pid"; exit 0; fi
  rid=${next% *}; jid=${next#* }
  # active D jobs: running, or pending for any reason other than a user hold
  active=$(squeue -u "$USER" -h -o '%j|%T|%r' 2>/dev/null | awk -F'|' \
    '$1 ~ /^D-/ && !($2 == "PENDING" && $3 ~ /JobHeld/) {n++} END {print n+0}')
  state=$(squeue -h -j "$jid" -o '%T|%r' 2>/dev/null)
  if [[ -z $state ]]; then
    log "job $jid of $rid is no longer in the queue (cancelled?): skipped"
    echo "$(date '+%F %T') $rid $jid" >> "$DIR/released"
    continue
  fi
  if (( active < MAXACTIVE )); then
    if scontrol release "$jid" 2>> "$DIR/log"; then
      echo "$(date '+%F %T') $rid $jid" >> "$DIR/released"
      log "released $jid ($rid); active D jobs before: $active"
    else
      log "scontrol release $jid failed"
    fi
  fi
  hour=$(date +%F-%H)
  if [[ $hour != "$last_hour" ]]; then log "alive; next $rid $jid ($state); active $active"; last_hour=$hour; fi
  sleep "$INTERVAL"
done
