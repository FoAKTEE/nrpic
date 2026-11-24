#!/usr/bin/env bash
# Sequencer of package repro/continue (Track E): sees the five continuation chains to their end
# when no session is there to do it (2026-11-24: both cards held by another user's job of up to
# one day on the priority partition, so the chains may start, and be preempted, long after the
# session that submitted them has ended).
#
# Every POLL seconds, for each label of scripts/runs.json, the label's newest continuation run
# (scripts/conts.json, then the lines of state.tsv):
#   chain QUEUED or RUNNING        -> nothing
#   chain DONE                     -> harness/bin/nrpic-run finish <run>; label done
#   chain FAILED, cut from outside (MAX_SEGMENTS reached after a SIGTERM, or killed from outside
#     MAX_OUTSIDE_KILLS times)     -> finish <run>; then a new continuation from that run's newest
#     restart file (or, if it wrote none, from the file it started from) through
#     scripts/submit_continue.sh (RESUME=<file>), same wrapper, executable, deck and overrides,
#     one segment; at most MAXC continuations per label in all; held while the package's card
#     time (closed runs at their measured card-hours, open ones at their request) plus the new
#     request would exceed CAP card-hours (the package cap of 5)
#   chain FAILED for any other reason (non-zero exit, NaN, guard, broken restart), or STOPPED
#                                  -> finish <run>; label broken (or stopped); never resubmitted
# When every label is done, broken, stopped or exhausted: the registered join check
# (scripts/join_check.py through nrpic-run, local, one core) on the labels that are done, with a
# conts file written here (conts_seq.json), then exit. Nothing is judged here: the outcome waits
# for a session that reads join_check.json and looks at fig_join.png.
#
# Start (outlives the session):
#   cd /data/haiyangw/nrpic/wt/E-stoch-inf && setsid nohup bash tracks/E-stoch-inf/repro/continue/scripts/autocontinue.sh \
#       > /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_continue_seq/nohup.out 2>&1 < /dev/null &
# See:   cat /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_continue_seq/{pid,state.tsv}; tail .../seq.log
# Stop:  touch /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_continue_seq/STOP (exits within POLL s;
#        running chains continue; remove the STOP file by its literal path before a restart)
# DRY=1: one pass that prints what it would do and changes nothing.
# State: state.tsv, one line per event: label, run id, status (submitted|done|cut|broken|stopped|
#        exhausted|held|refused|joincheck), UTC time.
set -uo pipefail
WT=/data/haiyangw/nrpic/wt/E-stoch-inf
PKG=tracks/E-stoch-inf/repro/continue
SCR=/data/haiyangw/nrpic/scratch/E-stoch-inf
S=${SEQ_DIR:-$SCR/repro_continue_seq}
DRY=${DRY:-0}; POLL=${POLL:-300}; MAXC=${MAXC:-3}; CAP=${CAP:-5.0}; REQ=0.9833
DEADLINE=$(date -d "${UNTIL:-2026-11-26 06:00}" +%s)
LABELS="RSF256 RNC256 CL256U CL256S AL2S"
mkdir -p "$S"; touch "$S/state.tsv"
(( DRY )) || echo $$ > "$S/pid"
log() { echo "$(date '+%F %T %Z') $*" >> "$S/seq.log"; (( DRY )) && echo "$*"; return 0; }
set_state() { (( DRY )) || echo -e "$1\t$2\t$3\t$(date -u +%FT%TZ)" >> "$S/state.tsv"; }
last_status() { awk -v l="$1" '$1==l {s=$3} END {print s}' "$S/state.tsv"; }
last_run() { awk -v l="$1" '$1==l && $2!="-" {r=$2} END {print r}' "$S/state.tsv"; }
n_runs() { awk -v l="$1" '$1==l && $3=="submitted" {n++} END {print n+0}' "$S/state.tsv"; }

# seed the state from conts.json once
if [[ ! -s $S/state.tsv ]]; then
  python3 -I - "$WT/$PKG/scripts/conts.json" <<'PY' >> "$S/state.tsv"
import json, sys, datetime
t = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
for lab, ids in json.load(open(sys.argv[1])).items():
    for r in ids:
        print(f"{lab}\t{r}\tsubmitted\t{t}")
PY
fi

# card-hours of every run in state.tsv: closed at their measured gpu_hours, open at their request
cost() {
  python3 -I - "$WT" $(awk '$2 ~ /^E-/ {print $2}' "$S/state.tsv" | sort -u) <<'PY'
import json, os, sys
wt, ids = sys.argv[1], sys.argv[2:]
tot = 0.0
for r in ids:
    p = os.path.join(wt, "tracks/E-stoch-inf/runs", r, "manifest.json")
    try:
        m = json.load(open(p))
    except Exception:
        continue
    res = m.get("resources") or {}
    if m.get("status") in ("completed", "failed", "stopped"):
        tot += res.get("gpu_hours") or 0.0
    else:
        tot += res.get("gpu_hours_requested") or 0.0
print(f"{tot:.4f}")
PY
}

# restart file a new continuation of run $1 starts from
next_restart() {
  local rd=$SCR/$1 f
  f=$(find "$rd/rst" -maxdepth 1 -name '*.rst' -printf '%T@ %p\n' 2>/dev/null | sort -k1,1gr -k2,2r | head -1 | cut -d' ' -f2-)
  if [[ -z $f ]]; then
    f=$(python3 -I -c 'import json,sys; a=json.load(open(sys.argv[1]))["argv"]; print([x.split("=",1)[1] for x in a if x.startswith("nrpic_resume=")][0])' "$rd/.nrpic/launch.json")
  fi
  echo "$f"
}

finish_run() {
  (( DRY )) && { echo "would finish $1"; return 0; }
  (cd "$WT" && harness/bin/nrpic-run finish "$1") >> "$S/seq.log" 2>&1
}

try_continue() {   # $1 label, $2 run to continue from
  local lab=$1 rid=$2 n c rst out new
  n=$(n_runs "$lab")
  if (( n >= MAXC )); then log "$lab: $n continuations already, no more"; set_state "$lab" "$rid" exhausted; return; fi
  c=$(cost)
  if python3 -I -c "import sys; sys.exit(0 if $c + $REQ <= $CAP + 1e-9 else 1)"; then :; else
    log "$lab: held (card-hours $c + $REQ > $CAP)"; [[ $(last_status "$lab") == held ]] || set_state "$lab" "$rid" held; return
  fi
  rst=$(next_restart "$rid")
  if [[ ! -r $rst || ! -r $rst.sf ]]; then log "$lab: no readable restart after $rid ($rst)"; set_state "$lab" "$rid" broken; return; fi
  if (( DRY )); then echo "would continue $lab from $rst"; return; fi
  out=$(cd "$WT" && RESUME=$rst "$WT/$PKG/scripts/submit_continue.sh" "$lab" 2>&1)
  echo "$out" >> "$S/seq.log"
  new=$(sed -n 's/^submitted \(E-[0-9]*-[0-9]*-[0-9a-f]*\) as Slurm job.*/\1/p' <<< "$out" | tail -1)
  if [[ -n $new ]]; then
    set_state "$lab" "$new" submitted; log "$lab: continued $rid from $(basename "$rst") as $new"
  else
    log "$lab: submission refused or failed (retry next round)"; [[ $(last_status "$lab") == refused ]] || set_state "$lab" "$rid" refused
  fi
}

joincheck() {
  python3 -I - "$S/state.tsv" "$S/conts_seq.json" <<'PY'
import json, sys
runs, status = {}, {}
for line in open(sys.argv[1]):
    lab, rid, st = line.split("\t")[:3]
    if st == "submitted":
        runs.setdefault(lab, []).append(rid)
    status[lab] = st
json.dump({l: r for l, r in runs.items() if status.get(l) == "done"}, open(sys.argv[2], "w"), indent=1)
PY
  if (( DRY )); then echo "would run the join check"; cat "$S/conts_seq.json"; return; fi
  (cd "$WT" && harness/bin/nrpic-run submit --kind production --gate G2 --package "$PKG" --launcher local --cores 1 \
     --wait 3600 --preregistered "$PKG/JOURNAL.md#entry-1" --input "$S/conts_seq.json" \
     --purpose "repro/continue join check J1-J4 of the continued runs (started by scripts/autocontinue.sh)" \
     -- python3 "$PKG/scripts/join_check.py" --conts "$S/conts_seq.json" --out '$NRPIC_RUN_DIR') >> "$S/seq.log" 2>&1
  set_state ALL - joincheck
}

log "start (pid $$, DRY=$DRY, POLL=$POLL, MAXC=$MAXC, CAP=$CAP)"
while :; do
  [[ -f $S/STOP ]] && { log "STOP file: exit"; exit 0; }
  (( $(date +%s) > DEADLINE )) && { log "deadline: exit (running chains continue)"; exit 0; }
  open=0
  for lab in $LABELS; do
    st=$(last_status "$lab"); rid=$(last_run "$lab")
    case $st in
      done|broken|stopped|exhausted) continue ;;
      cut|held|refused) open=$((open + 1)); try_continue "$lab" "$rid"; continue ;;
    esac
    open=$((open + 1))
    cs=$(cat "$SCR/$rid/chain/STATUS" 2>/dev/null || echo none)
    case $cs in
      QUEUED|RUNNING|none) ;;
      DONE) finish_run "$rid"; set_state "$lab" "$rid" done; log "$lab: $rid DONE" ;;
      STOPPED) finish_run "$rid"; set_state "$lab" "$rid" stopped; log "$lab: $rid STOPPED" ;;
      FAILED)
        why=$(grep 'STATUS FAILED' "$SCR/$rid/chain/events.log" | tail -1)
        finish_run "$rid"
        if grep -qE 'MAX_SEGMENTS=[0-9]+ reached|killed from outside' <<< "$why"; then
          set_state "$lab" "$rid" cut; log "$lab: $rid cut ($why)"; try_continue "$lab" "$rid"
        else
          set_state "$lab" "$rid" broken; log "$lab: $rid BROKEN ($why): not continued"
        fi ;;
      *) log "$lab: $rid chain status '$cs' not understood" ;;
    esac
  done
  # all labels settled?
  settled=1
  for lab in $LABELS; do
    case $(last_status "$lab") in done|broken|stopped|exhausted) ;; *) settled=0 ;; esac
  done
  if (( settled )); then
    log "all labels settled: $(for l in $LABELS; do printf '%s=%s ' "$l" "$(last_status "$l")"; done)"
    joincheck; log "exit"; exit 0
  fi
  (( DRY )) && exit 0
  sleep "$POLL"
done
