#!/usr/bin/env bash
# Sequencer of the C-sidm long card runs (batch 5; decision 0025 item 5; changed in batch 11).
#
#   tracks/C-sidm/longruns/seq/seq.sh run       the loop (start it with setsid nohup, below)
#   tracks/C-sidm/longruns/seq/seq.sh status    state of every item, the queue position
#   tracks/C-sidm/longruns/seq/seq.sh stop      ask the loop to exit (touches STOP); running
#                                               card jobs are NOT cancelled
#
# Start (from any directory; it outlives the session):
#   setsid nohup /data/haiyangw/nrpic/wt/C-sidm/tracks/C-sidm/longruns/seq/seq.sh run \
#     >> /data/haiyangw/nrpic/scratch/C-sidm/seq/nohup.out 2>&1 < /dev/null &
#
# What it does, every POLL seconds (300):
#  1. STOP file in the state directory -> exit.
#  2. Every submitted item whose card work has ended (chain or resume: chain/STATUS is DONE,
#     FAILED or STOPPED and its job is gone from squeue; batch: its job is gone from squeue)
#     is closed with `harness/bin/nrpic-run finish <run_id>` (checksums, manifest commit); a
#     resume item is closed with `--status` set from the chain's STATUS, because its manifest
#     was already final before the resume.
#  3. While fewer than SLOTS (2) items are active AND fewer than SLOTS jobs named C-* are in
#     squeue (any state; jobs a session submitted by hand count too), the next item of
#     queue.txt is submitted. The pause flag /data/haiyangw/nrpic/locks/PAUSE does NOT stop
#     submissions (decision 0026 item 2: a card run uses none of the account's usage); its
#     presence is logged. Why the next item waits is logged whenever the reason changes
#     (decision 0030 item 4).
#     - batch / chain items: `harness/bin/nrpic-run submit` (registered, --package
#       tracks/C-sidm/longruns, executable of release core-v0.6). A chain gets the process
#       name of the queue (written into its chain/config.sh before its first segment starts).
#     - resume items (batch 11): continue a registered chain that ended FAILED or STOPPED
#       because it ran out of segments (preemption), in place, from its newest restart file:
#       `scripts/submit_chain.sh <its run dir> <its deck> [athena arg]` with MAX_SEGMENTS =
#       its segment count + the number in the queue line, JOB_NAME = its run id, the same
#       executable and process name. The manifest gets a `continuations` entry (committed).
#       The run is never repeated from t = 0.
#  4. After the item `timing` is closed, its log is read: if the collisionless M/8 deck ran
#     slower than 0.45 of the zone-cycle rate of core-v0.3 (7.28e6 zone-cycles/s, run (vi);
#     i.e. above about 18 s per M, where four segments of 50 min no longer hold 600 M) the
#     loop writes STOP and exits, so that a session re-sizes the chains (JOURNAL.md, T).
# A submission that the harness refuses (dirty package, index lock, budget) is retried at
# the next poll, at most 12 times, then marked SUBMIT_FAILED and skipped.
# Git: nrpic-run commits manifests on track/C-sidm in this worktree; the loop waits while
# the index lock or a merge is in progress. It never pushes.
set -uo pipefail

WT=/data/haiyangw/nrpic/wt/C-sidm
PKG=tracks/C-sidm/longruns
Q=$WT/$PKG/seq/queue.txt
SCR=/data/haiyangw/nrpic/scratch/C-sidm
S=$SCR/seq
STATE=$S/state.tsv          # item  run_id  launcher  jobid  status  tries
LOG=$S/seq.log
EXE=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena
SLOTS=${SLOTS:-2}
POLL=${POLL:-300}
SEG_FLOOR=${SEG_FLOOR:-20}
PAUSE=/data/haiyangw/nrpic/locks/PAUSE
GITDIR=/data/haiyangw/nrpic/.git/worktrees/C-sidm
mkdir -p "$S"
touch "$STATE"

log() { echo "$(date -u +%FT%TZ) $*" >> "$LOG"; }

queue_items() { grep -vE '^[[:space:]]*(#|$)' "$Q"; }
state_get() { awk -F'\t' -v i="$1" '$1==i' "$STATE" | tail -n 1; }
state_set() {  # item run_id launcher jobid status tries
  local tmp; tmp=$(mktemp "$S/.state.XXXXXX")
  awk -F'\t' -v i="$1" '$1!=i' "$STATE" > "$tmp"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$@" >> "$tmp"
  mv "$tmp" "$STATE"
}
c_jobs_in_queue() { squeue -h -u "${USER:-haiyangw}" -o '%j' 2>/dev/null | grep -c '^C-'; }
job_in_queue() { [[ -n $1 && $1 != - && -n $(squeue -h -j "$1" -o %T 2>/dev/null) ]]; }
wait_git() {
  local n=0
  while [[ -e $GITDIR/index.lock || -e $GITDIR/MERGE_HEAD ]]; do
    sleep 20; n=$((n + 1)); (( n > 90 )) && return 1
  done
  return 0
}

is_active() {  # run_id launcher jobid
  local run=$1 la=$2 jid=$3 st
  if [[ $la == chain || $la == resume ]]; then
    st=$(cat "$SCR/$run/chain/STATUS" 2>/dev/null || echo NONE)
    jid=$(cat "$SCR/$run/chain/jobid" 2>/dev/null || echo "$jid")
    case $st in DONE|FAILED|STOPPED) job_in_queue "$jid" && return 0; return 1 ;; *) return 0 ;; esac
  fi
  job_in_queue "$jid"
}

close_finished() {
  local item run la jid st tries fargs cst
  while IFS=$'\t' read -r item run la jid st tries; do
    [[ $st == SUBMITTED ]] || continue
    is_active "$run" "$la" "$jid" && continue
    wait_git || { log "close $item: git busy, later"; continue; }
    fargs=()
    if [[ $la == resume ]]; then
      cst=$(cat "$SCR/$run/chain/STATUS" 2>/dev/null || echo NONE)
      case $cst in DONE) fargs=(--status completed) ;; STOPPED) fargs=(--status stopped) ;;
                   *) fargs=(--status failed) ;; esac
    fi
    if (cd "$WT" && harness/bin/nrpic-run finish "$run" "${fargs[@]}") >> "$LOG" 2>&1; then
      state_set "$item" "$run" "$la" "$jid" CLOSED "$tries"; log "closed $item ($run)"
      [[ $item == timing ]] && check_timing "$run"
    else
      log "close $item ($run): nrpic-run finish failed; retry at the next poll"
    fi
  done < <(cat "$STATE")
}

check_timing() {
  local run=$1 f rate
  rate=$(grep -h 'zone-cycles/cpu_second' "$SCR/$run"/T_A8_ctrl/*.log 2>/dev/null | tail -n 1 | awk -F'=' '{print $2+0}')
  log "timing: T_A8_ctrl zone-cycles/cpu_second = ${rate:-none} (core-v0.3 on M/8: 7.28e6)"
  if [[ -z $rate ]] || awk -v r="$rate" 'BEGIN{exit !(r < 0.45*7.28e6)}'; then
    log "timing: slower than about 18 s per M or unreadable -> STOP (re-size the chains first)"
    touch "$S/STOP"
  fi
}

active_count() { awk -F'\t' '$5=="SUBMITTED"' "$STATE" | wc -l; }

next_item() {  # first queue line not yet submitted, closed or abandoned
  local line item st
  while read -r line; do
    item=${line%% *}
    st=$(state_get "$item" | cut -f5)
    [[ -z $st || $st == RETRY ]] && { echo "$line"; return 0; }
  done < <(queue_items)
  return 1
}

refuse() {  # item launcher tries message: count a refused submission
  local item=$1 la=$2 tries=$(( $3 + 1 ))
  if (( tries >= 12 )); then state_set "$item" - "$la" - SUBMIT_FAILED "$tries"; log "submit $item: abandoned after $tries tries ($4)"
  else state_set "$item" - "$la" - RETRY "$tries"; log "submit $item: refused (try $tries): $4"; fi
  return 1
}

note_continuation() {  # run_id max_segments from_restart xarg item: entry in the manifest
  local mf=$WT/tracks/C-sidm/runs/$1/manifest.json
  python3 -I - "$mf" "$1" "$2" "$3" "$4" "$5" <<'PY' || return 1
import json, sys, datetime
mf, run, mx, rst, xarg, item = sys.argv[1:7]
m = json.load(open(mf))
c = m.setdefault("continuations", [])
c.append({"at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          "by": "tracks/C-sidm/longruns/seq/seq.sh (queue item %s)" % item,
          "kind": "in-place resume of a chain cut by preemption (out of segments)",
          "status_before": m.get("status"), "from_restart": rst,
          "max_segments": int(mx), "extra_athena_args": [] if xarg == "-" else [xarg],
          "predictions": "tracks/C-sidm/JOURNAL.md 2026-11-21T20:25Z; resume rule 2026-11-24 entry"})
json.dump(m, open(mf, "w"), indent=2)
open(mf, "a").write("\n")
PY
  (cd "$WT" && git commit -q -m "C(run): continue $1 in place from its newest restart (seq.sh $5)" \
     -m "Chain cut by preemption (out of segments); resumed with MAX_SEGMENTS $2${4:+, athena arg $4}." \
     -- "tracks/C-sidm/runs/$1/manifest.json") >> "$LOG" 2>&1
}

resume_item() {
  local line=$1 item la add run pn deck xarg purpose tries R C st seg max rst out jid mst
  read -r item la add run pn deck xarg purpose <<< "$line"
  tries=$(state_get "$item" | cut -f6); tries=${tries:-0}
  R=$SCR/$run; C=$R/chain
  st=$(cat "$C/STATUS" 2>/dev/null || echo NONE)
  case $st in FAILED|STOPPED) ;;
    *) state_set "$item" "$run" resume - SUBMIT_FAILED "$tries"
       log "resume $item: chain $run is $st, not FAILED or STOPPED -> skipped"; return 1 ;; esac
  job_in_queue "$(cat "$C/jobid" 2>/dev/null)" && { refuse "$item" resume "$tries" "a job of $run is still in squeue"; return 1; }
  mst=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1])).get("status"))' \
        "$WT/tracks/C-sidm/runs/$run/manifest.json" 2>/dev/null)
  [[ $mst == failed || $mst == stopped ]] || { refuse "$item" resume "$tries" "manifest of $run is '$mst', not closed"; return 1; }
  wait_git || { log "resume $item: git busy, later"; return 1; }
  seg=$(cat "$C/segment" 2>/dev/null || echo 0)
  max=$((seg + add))
  rst=$(find "$R/rst" -maxdepth 1 -name '*.rst' -printf '%T@ %p\n' 2>/dev/null | sort -k1,1gr | head -1 | cut -d' ' -f2-)
  note_continuation "$run" "$max" "${rst:-none}" "$xarg" "$item" || { refuse "$item" resume "$tries" "manifest note failed"; return 1; }
  local xa=(); [[ $xarg != - ]] && xa=("$xarg")
  out=$(cd "$WT" && ATHENA_EXE=$EXE MAX_SEGMENTS=$max JOB_NAME=$run PROC_NAME=$pn \
        scripts/submit_chain.sh "$R" "$WT/$deck" "${xa[@]}" 2>&1); echo "$out" >> "$LOG"
  jid=$(grep -oE 'chain started in .*: job [0-9]+' <<< "$out" | grep -oE '[0-9]+$')
  [[ -n $jid ]] || { refuse "$item" resume "$tries" "submit_chain.sh did not start"; return 1; }
  state_set "$item" "$run" resume "$jid" SUBMITTED "$tries"
  log "resumed $item: $run from ${rst##*/} (segments $seg -> at most $max${xarg:+, $xarg}; Slurm $jid)"
  return 0
}

submit_item() {
  local line=$1 item la gh np pn deck purpose out run jid tries
  read -r item la gh np pn deck purpose <<< "$line"
  [[ $la == resume ]] && { resume_item "$line"; return $?; }
  tries=$(state_get "$item" | cut -f6); tries=${tries:-0}
  wait_git || { log "submit $item: git busy, later"; return 1; }
  local args=(submit --kind scouting --gate G2 --package "$PKG" --exe "$EXE" --particles "$np"
              --gpu-hours "$gh" --purpose "longruns $item: $purpose (seq.sh; JOURNAL.md)")
  if [[ $la == batch ]]; then
    args+=(--launcher batch --list "$deck" --wall 00:55:00)
  else
    args+=(--launcher chain -- "$deck")
  fi
  out=$(cd "$WT" && harness/bin/nrpic-run "${args[@]}" 2>&1); echo "$out" >> "$LOG"
  run=$(grep -oE 'submitted (C-[0-9]{8}-[0-9]{6}-[0-9a-f]{7}) as Slurm job [0-9]+' <<< "$out" | awk '{print $2}')
  jid=$(grep -oE 'as Slurm job [0-9]+' <<< "$out" | awk '{print $4}')
  if [[ -z $run || -z $jid ]]; then refuse "$item" "$la" "$tries" "nrpic-run refused"; return 1; fi
  state_set "$item" "$run" "$la" "$jid" SUBMITTED "$tries"
  log "submitted $item as $run (Slurm $jid)"
  if [[ $la == chain && $pn != - ]]; then   # process name of this owner, before segment 1 runs
    local C=$SCR/$run/chain tmp
    if [[ -f $C/config.sh ]] && ! grep -q "^PROC_NAME=$pn\$" "$C/config.sh"; then
      tmp=$(mktemp "$C/.config.XXXXXX")
      sed "s/^PROC_NAME=.*/PROC_NAME=$pn/" "$C/config.sh" > "$tmp" && mv "$tmp" "$C/config.sh"
      ln -f "$C/athena" "$C/$pn" 2>/dev/null || cp -p "$C/athena" "$C/$pn"
      log "  $item: PROC_NAME $pn"
    fi
  fi
  if [[ $la == chain && -f $SCR/$run/chain/config.sh ]]; then
    # batch 11: a preempted segment counts as a segment; with a restart every 10 M it wastes
    # under two minutes, so the segment cap (gpu-hours / 59 min) is raised to SEG_FLOOR. The
    # card time used is what sacct reports at finish; the reservation of the harness stays
    # at the gpu-hours of the queue line (README "Operating the sequencer").
    local C2=$SCR/$run/chain mx tmp2
    mx=$(sed -n 's/^MAX_SEGMENTS=//p' "$C2/config.sh")
    if [[ -n $mx ]] && (( mx < SEG_FLOOR )); then
      tmp2=$(mktemp "$C2/.config.XXXXXX")
      sed "s/^MAX_SEGMENTS=.*/MAX_SEGMENTS=$SEG_FLOOR/" "$C2/config.sh" > "$tmp2" && mv "$tmp2" "$C2/config.sh"
      log "  $item: MAX_SEGMENTS $mx -> $SEG_FLOOR"
    fi
  fi
  return 0
}

status() {
  echo "state directory $S; loop pid $(cat "$S/seq.pid" 2>/dev/null || echo none)" \
       "$( [[ -e $S/STOP ]] && echo '(STOP requested)')"
  local line item st
  while read -r line; do
    item=${line%% *}; st=$(state_get "$item")
    printf '%-9s %s\n' "$item" "${st:-(waiting)}" | cut -c1-150
  done < <(queue_items)
  echo "C-* jobs in squeue: $(c_jobs_in_queue)"; tail -n 5 "$LOG" 2>/dev/null
}

case ${1:-} in
  status) status; exit 0 ;;
  stop) touch "$S/STOP"; echo "STOP written; the loop exits at its next poll"; exit 0 ;;
  run) echo "seq.sh: retired on 2026-11-24 (decision 0033: no sequencers of owners; card runs reach" \
            "Slurm only through harness/bin/nrpic-queue). Queue an item with" \
            "tracks/C-sidm/longruns/seq/qitem.sh (HANDOFF.md)." >&2; exit 1 ;;
  *) sed -n '2,12p' "$0"; exit 1 ;;
esac

if [[ -e $S/seq.pid ]] && kill -0 "$(cat "$S/seq.pid")" 2>/dev/null; then
  echo "a loop already runs (pid $(cat "$S/seq.pid"))" >&2; exit 1
fi
echo $$ > "$S/seq.pid"
rm -f "$S/STOP"
log "loop start pid $$ slots $SLOTS poll $POLL (submits through the pause flag: decision 0026 item 2)"
last_wait=
last_pause=
while true; do
  if [[ -e $S/STOP ]]; then log "STOP: exit"; rm -f "$S/seq.pid"; exit 0; fi
  close_finished
  [[ -e $S/STOP ]] && continue
  if [[ -e $PAUSE ]]; then
    [[ $last_pause == yes ]] || log "pause flag present: submissions go on (decision 0026 item 2)"
    last_pause=yes
  else
    last_pause=
  fi
  while (( $(active_count) < SLOTS )) && (( $(c_jobs_in_queue) < SLOTS )); do
    line=$(next_item) || break
    submit_item "$line" || break
    last_wait=
    sleep 5
  done
  if line=$(next_item); then
    why="next ${line%% *}: $(active_count) item(s) active, $(c_jobs_in_queue) C-* job(s) in squeue (slots $SLOTS)"
    [[ $why == "$last_wait" ]] || log "waiting: $why"
    last_wait=$why
  elif (( $(active_count) == 0 )); then
    log "queue done: exit"; rm -f "$S/seq.pid"; exit 0
  fi
  sleep "$POLL"
done
