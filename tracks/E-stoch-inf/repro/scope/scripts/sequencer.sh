#!/usr/bin/env bash
# Sequencer of the repro/scope card runs: a copy of tracks/E-stoch-inf/g2prod/scripts/sequencer.sh
# (batch 5) with a launcher and a deck or list per queue line. Keeps at most MAXJ card jobs of owner
# E-stoch-inf eligible (Slurm job names starting with "E-": every batch and chain job of this owner,
# the lead's included), submits the next line of repro/scope/queue.txt through harness/bin/nrpic-run,
# closes finished runs with `nrpic-run finish` (which commits the manifest), and retries a
# submission refused by the allotment every RETRY seconds.
#
# Start (outlives the session):
#   cd /data/haiyangw/nrpic/wt/E-stoch-inf && setsid nohup bash tracks/E-stoch-inf/repro/scope/scripts/sequencer.sh \
#       > /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/nohup.out 2>&1 < /dev/null &
# See:   cat /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/{pid,state.tsv}; tail .../seq.log
# Stop:  touch /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/STOP  (exits within POLL s;
#        running chains continue; stop a chain with harness/bin/nrpic-run stop <run_id>)
#        or kill "$(cat /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/pid)"   (numeric pid)
# Pause: while /data/haiyangw/nrpic/locks/PAUSE exists nothing new is submitted (decision 0019).
# State: state.tsv, one line per event: label, run_id or -, status (submitted|finished|refused|error|skipped).
set -uo pipefail
WT=/data/haiyangw/nrpic/wt/E-stoch-inf
Q=$WT/tracks/E-stoch-inf/repro/scope/queue.txt
S=/data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq
EXE=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena
PKG=tracks/E-stoch-inf/repro/scope
PRE="tracks/E-stoch-inf/repro/scope/JOURNAL.md#entry-1"
MAXJ=${MAXJ:-2}; POLL=${POLL:-300}; RETRY=${RETRY:-900}
mkdir -p "$S"; touch "$S/state.tsv"
echo $$ > "$S/pid"
log() { echo "$(date '+%F %T %Z') $*" >> "$S/seq.log"; }
state_of() { awk -v l="$1" '$1==l {s=$3} END {print s}' "$S/state.tsv"; }
runid_of() { awk -v l="$1" '$1==l {r=$2} END {print r}' "$S/state.tsv"; }
set_state() { echo -e "$1\t$2\t$3\t$(date -u +%FT%TZ)" >> "$S/state.tsv"; }
n_eligible() { squeue -h -u "$USER" -o '%j %T' 2>/dev/null | awk '$1 ~ /^E-/ && ($2=="PENDING" || $2=="RUNNING" || $2=="CONFIGURING" || $2=="REQUEUED") {n++} END {print n+0}'; }
in_queue() { squeue -h -u "$USER" -o '%j' 2>/dev/null | grep -qx "$1"; }
log "sequencer start pid $$ (MAXJ=$MAXJ POLL=$POLL RETRY=$RETRY)"
last_try=0
while true; do
  [[ -e $S/STOP ]] && { log "STOP file: exit"; rm -f "$S/pid"; exit 0; }
  cd "$WT" || { log "no worktree"; sleep "$POLL"; continue; }
  # close runs whose job has left the queue (chain: STATUS DONE/FAILED/STOPPED; batch: nrpic-run reads it)
  for lab in $(awk '$3=="submitted" {print $1}' "$S/state.tsv" | sort -u); do
    [[ $(state_of "$lab") == submitted ]] || continue
    rid=$(runid_of "$lab"); in_queue "$rid" && continue
    if [[ -d /data/haiyangw/nrpic/scratch/E-stoch-inf/$rid/chain ]]; then
      st=$(cat "/data/haiyangw/nrpic/scratch/E-stoch-inf/$rid/chain/STATUS" 2>/dev/null || echo "")
      case "$st" in DONE) fs=(--status completed) ;; FAILED*) fs=(--status failed) ;; STOPPED*) fs=(--status stopped) ;; *) continue ;; esac
    else fs=(); fi
    if harness/bin/nrpic-run finish "$rid" "${fs[@]}" >> "$S/seq.log" 2>&1; then
      set_state "$lab" "$rid" finished; log "finished $lab $rid (${fs[*]:-batch})"
    else log "finish of $lab $rid failed; will retry"; fi
  done
  # next label to submit
  next=""
  while read -r lab gh lau deck rest; do
    [[ -z $lab || $lab == \#* ]] && continue
    s=$(state_of "$lab"); [[ -z $s || $s == refused || $s == error ]] && { next="$lab"; nextgh="$gh"; nextlau="$lau"; nextdeck="$deck"; nextrest="$rest"; break; }
  done < "$Q"
  if [[ -z $next ]]; then
    open=0; for l in $(awk '{print $1}' "$S/state.tsv" | sort -u); do [[ $(state_of "$l") == submitted ]] && open=1; done
    if (( open == 0 )); then
      log "queue empty and every run closed: exit"; rm -f "$S/pid"; exit 0
    fi
  elif [[ -e /data/haiyangw/nrpic/locks/PAUSE ]]; then
    log "PAUSE flag: nothing submitted"
  elif (( $(n_eligible) < MAXJ )); then
    now=$(date +%s)
    if [[ $(state_of "$next") == refused ]] && (( now - last_try < RETRY )); then :; else
      last_try=$now
      purpose="repro/scope $next: ${nextrest%%|*}; arXiv:2512.14649 reproduction, release core-v0.6 card build; predictions repro/scope/JOURNAL.md entry 1"
      read -r -a args <<< "${nextrest#*|}"
      if [[ $nextlau == batch ]]; then
        out=$(harness/bin/nrpic-run submit --kind production --gate G2 --preregistered "$PRE" \
                --package "$PKG" --launcher batch --gpu-hours "$nextgh" --exe "$EXE" --list "$nextdeck" \
                --wall 00:30:00 --purpose "$purpose" 2>&1); rc=$?
      else
        out=$(harness/bin/nrpic-run submit --kind production --gate G2 --preregistered "$PRE" \
                --package "$PKG" --launcher chain --gpu-hours "$nextgh" --exe "$EXE" \
                --purpose "$purpose" -- "$nextdeck" "${args[@]}" 2>&1); rc=$?
      fi
      echo "$out" >> "$S/seq.log"
      rid=$(grep -oE 'E-[0-9]{8}-[0-9]{6}-[0-9a-f]{7}' <<< "$out" | head -1)
      if (( rc == 0 )) && [[ -n $rid ]]; then
        cfg=/data/haiyangw/nrpic/scratch/E-stoch-inf/$rid/chain/config.sh
        [[ -f $cfg ]] && sed -i "s/^PROC_NAME=.*/PROC_NAME=E-$next/" "$cfg"
        set_state "$next" "$rid" submitted; log "submitted $next as $rid"
      elif grep -q 'refused: beyond the allotment' <<< "$out"; then
        set_state "$next" - refused; log "refused by the allotment: $next; retry in $RETRY s"
      else
        n_err=$(awk -v l="$next" '$1==l && $3=="error"' "$S/state.tsv" | wc -l)
        if (( n_err >= 3 )); then set_state "$next" - skipped; log "ERROR x3, skipped $next"
        else set_state "$next" - error; log "ERROR submitting $next (rc $rc); retry next poll"; fi
      fi
    fi
  fi
  sleep "$POLL"
done
