#!/usr/bin/env bash
# Sequencer of the g2prod card runs (decision 0025 item 5): keeps at most two card jobs of
# owner E-stoch-inf eligible (Slurm job names starting with "E-", which nrpic-run gives every
# batch and chain job of this owner), submits the next line of g2prod/queue.txt through
# harness/bin/nrpic-run when fewer are queued or running, closes finished runs with
# `nrpic-run finish`, and retries a submission refused by the allotment every RETRY seconds.
#
# Start (outlives the session):
#   cd /data/haiyangw/nrpic/wt/E-stoch-inf && setsid nohup bash tracks/E-stoch-inf/g2prod/scripts/sequencer.sh \
#       > /data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/nohup.out 2>&1 < /dev/null &
# See:   cat /data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/{pid,state.tsv}; tail .../seq.log
# Stop:  touch /data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/STOP   (it exits within POLL s;
#        running chains continue; stop a chain with harness/bin/nrpic-run stop <run_id>)
#        or kill "$(cat /data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/pid)"   (numeric pid)
# State: state.tsv has one line per label: label, run_id or -, status (submitted|finished|refused|error).
set -uo pipefail
WT=/data/haiyangw/nrpic/wt/E-stoch-inf
Q=$WT/tracks/E-stoch-inf/g2prod/queue.txt
S=/data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq
EXE=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena
DECK=tracks/E-stoch-inf/g2prod/inputs/usr_prod.athinput
PRE="tracks/E-stoch-inf/g2prod/JOURNAL.md#entry-1"
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
  # close runs whose job has left the queue (chain: STATUS DONE/FAILED/STOPPED)
  for lab in $(awk '$3=="submitted" {print $1}' "$S/state.tsv" | sort -u); do
    [[ $(state_of "$lab") == submitted ]] || continue
    rid=$(runid_of "$lab"); in_queue "$rid" && continue
    if [[ -d /data/haiyangw/nrpic/scratch/E-stoch-inf/$rid/chain ]]; then
      st=$(cat "/data/haiyangw/nrpic/scratch/E-stoch-inf/$rid/chain/STATUS" 2>/dev/null || echo "")
      case "$st" in DONE) fs=(--status completed) ;; FAILED*) fs=(--status failed) ;; STOPPED*) fs=(--status stopped) ;; *) continue ;; esac
    else fs=(); fi                       # a batch job: nrpic-run reads its outcome itself
    if harness/bin/nrpic-run finish "$rid" "${fs[@]}" >> "$S/seq.log" 2>&1; then
      set_state "$lab" "$rid" finished; log "finished $lab $rid (${fs[*]:-batch})"
    else log "finish of $lab $rid failed; will retry"; fi
  done
  # next label to submit
  next=""
  while read -r lab gh rest; do
    [[ -z $lab || $lab == \#* ]] && continue
    s=$(state_of "$lab"); [[ -z $s || $s == refused || $s == error ]] && { next="$lab"; nextgh="$gh"; nextrest="$rest"; break; }
  done < "$Q"
  if [[ -z $next ]]; then
    open=0; for l in $(awk '{print $1}' "$S/state.tsv" | sort -u); do [[ $(state_of "$l") == submitted ]] && open=1; done
    if (( open == 0 )); then
      log "queue empty and every run closed: exit"; rm -f "$S/pid"; exit 0
    fi
  elif (( $(n_eligible) < MAXJ )); then
    now=$(date +%s)
    if [[ $(state_of "$next") == refused ]] && (( now - last_try < RETRY )); then :; else
      last_try=$now
      purpose="g2prod $next: ${nextrest%%|*}; release core-v0.6 card build; criteria SCOPE 4c, predictions g2prod/JOURNAL.md entry 1"
      read -r -a args <<< "${nextrest#*|}"
      out=$(harness/bin/nrpic-run submit --kind production --gate G2 --preregistered "$PRE" \
              --package tracks/E-stoch-inf/g2prod --launcher chain --gpu-hours "$nextgh" --exe "$EXE" \
              --purpose "$purpose" -- "$DECK" "${args[@]}" 2>&1); rc=$?
      echo "$out" >> "$S/seq.log"
      rid=$(grep -oE 'E-[0-9]{8}-[0-9]{6}-[0-9a-f]{7}' <<< "$out" | head -1)
      if (( rc == 0 )) && [[ -n $rid ]]; then
        cfg=/data/haiyangw/nrpic/scratch/E-stoch-inf/$rid/chain/config.sh
        [[ -f $cfg ]] && sed -i "s/^PROC_NAME=.*/PROC_NAME=E-$next/" "$cfg"
        set_state "$next" "$rid" submitted; log "submitted $next as $rid (process name E-$next)"
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
