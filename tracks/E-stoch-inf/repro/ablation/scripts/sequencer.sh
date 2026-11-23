#!/usr/bin/env bash
# Sequencer of the repro/scope AND repro/ablation card runs (Track E). It REPLACES the running copy of
# repro/scope/scripts/sequencer.sh: same state directory, same state file, same two-job rule, same
# closing of finished runs, and it reads repro/scope/queue.txt unchanged (read only) with that queue's
# executable, package and plan. The ablation queue (repro/ablation/queue.txt) is APPENDED to it with
# the branch card executable of core/noise-level2 (decision 0031 item 3), its own package and plan:
#   - lines marked "head" (the card smoke T5SMK) are submitted before the remaining scope lines
#     (about 0.05 card-hours, core's pending test T5, and it gates the 256^3 lines);
#   - lines marked "tail" come after every scope line;
#   - a line with gate SMOKE is submitted only after the smoke batch closed AND its registered check
#     (scripts/smoke_check.py through nrpic-run, local, one core) wrote verdict PASS; on FAIL the
#     ablation lines are held (state.tsv: SMOKECHK ... fail) and nothing else changes;
#   - cost guard: an ablation line is held when used + (open + 1) * est > CAP2 card-hours, used = the
#     gpu_hours of the closed ablation runs (manifests), open = ablation runs in flight, est = max(EST2,
#     mean actual of the closed 256^3 ablation runs).
#
# Start (outlives the session; the old scope sequencer must have exited first):
#   cd /data/haiyangw/nrpic/wt/E-stoch-inf && setsid nohup bash tracks/E-stoch-inf/repro/ablation/scripts/sequencer.sh \
#       > /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/nohup.out 2>&1 < /dev/null &
# See:   cat /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/{pid,state.tsv}; tail .../seq.log
# Stop:  touch /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/STOP  (exits within POLL s;
#        remove the STOP file by its literal path before a restart; running chains continue)
# Skip a queued line (e.g. RL1/UL1 of the scope queue, superseded by decision 0031): append
#   "<label>\t-\tskipped\t<date>" to state.tsv.
# Pause: while /data/haiyangw/nrpic/locks/PAUSE exists nothing new is submitted (decision 0019).
# State: state.tsv, one line per event: label, run_id or -, status
#        (submitted|finished|refused|error|skipped|pass|fail|held).
set -uo pipefail
WT=/data/haiyangw/nrpic/wt/E-stoch-inf
S=${SEQ_DIR:-/data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq}   # SEQ_DIR only for a dry test
DRY=${DRY:-0}   # DRY=1: one pass, prints what it would submit, submits and closes nothing
Q1=$WT/tracks/E-stoch-inf/repro/scope/queue.txt
EXE1=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena
PKG1=tracks/E-stoch-inf/repro/scope
PRE1="tracks/E-stoch-inf/repro/scope/JOURNAL.md#entry-1"
Q2=$WT/tracks/E-stoch-inf/repro/ablation/queue.txt
EXE2=/data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu
PKG2=tracks/E-stoch-inf/repro/ablation
PRE2="tracks/E-stoch-inf/repro/ablation/JOURNAL.md#entry-1"
CHK=tracks/E-stoch-inf/repro/ablation/scripts/smoke_check.py
CORE_REF=/data/haiyangw/nrpic/scratch/core/core-20261123-030705-6b6a4bd
SMOKE_LABEL=T5SMK
MAXJ=${MAXJ:-2}; POLL=${POLL:-300}; RETRY=${RETRY:-900}; CAP2=${CAP2:-5.0}; EST2=${EST2:-0.75}
mkdir -p "$S"; touch "$S/state.tsv"
(( DRY )) || echo $$ > "$S/pid"
log() { echo "$(date '+%F %T %Z') $*" >> "$S/seq.log"; }
state_of() { awk -v l="$1" '$1==l {s=$3} END {print s}' "$S/state.tsv"; }
runid_of() { awk -v l="$1" '$1==l {r=$2} END {print r}' "$S/state.tsv"; }
set_state() { echo -e "$1\t$2\t$3\t$(date -u +%FT%TZ)" >> "$S/state.tsv"; }
n_eligible() { squeue -h -u "$USER" -o '%j %T' 2>/dev/null | awk '$1 ~ /^E-/ && ($2=="PENDING" || $2=="RUNNING" || $2=="CONFIGURING" || $2=="REQUEUED") {n++} END {print n+0}'; }
in_queue() { squeue -h -u "$USER" -o '%j' 2>/dev/null | grep -qx "$1"; }
q2_labels() { awk '!/^#/ && NF {print $1}' "$Q2"; }
# cost of the ablation queue: prints "used open est" (card-hours, count, card-hours)
q2_cost() {
  local ids=() lab rid
  for lab in $(q2_labels); do
    rid=$(runid_of "$lab"); [[ -n $rid && $rid != - ]] && ids+=("$lab:$rid:$(state_of "$lab")")
  done
  python3 -I - "$WT" "$EST2" "${ids[@]}" <<'PY'
import json, os, sys
wt, est = sys.argv[1], float(sys.argv[2])
used, opn, big = 0.0, 0, []
for item in sys.argv[3:]:
    lab, rid, st = item.split(":")
    if st == "submitted":
        opn += 1
        continue
    try:
        m = json.load(open(os.path.join(wt, "tracks/E-stoch-inf/runs", rid, "manifest.json")))
        g = (m.get("resources") or {}).get("gpu_hours") or 0.0
    except Exception:
        g = 0.0
    used += g
    if not lab.startswith("T5"):
        big.append(g)
if big:
    est = max(est, sum(big) / len(big))
print(f"{used:.4f} {opn} {est:.4f}")
PY
}
(( DRY )) || log "sequencer (scope + ablation) start pid $$ (MAXJ=$MAXJ POLL=$POLL RETRY=$RETRY CAP2=$CAP2 EST2=$EST2)"
last_try=0; last_hold=0
while true; do
  [[ -e $S/STOP ]] && { log "STOP file: exit"; rm -f "$S/pid"; exit 0; }
  cd "$WT" || { log "no worktree"; sleep "$POLL"; continue; }
  # 1. close runs whose job has left the queue (chain: STATUS DONE/FAILED/STOPPED; batch: nrpic-run reads it)
  for lab in $( (( DRY )) || awk '$3=="submitted" {print $1}' "$S/state.tsv" | sort -u); do
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
  # 2. the registered check of the smoke batch, once it is closed
  if (( DRY == 0 )) && [[ $(state_of "$SMOKE_LABEL") == finished ]]; then
    cs=$(state_of SMOKECHK)
    if [[ -z $cs || $cs == error ]] && [[ ! -e /data/haiyangw/nrpic/locks/PAUSE ]]; then
      srid=$(runid_of "$SMOKE_LABEL")
      out=$(harness/bin/nrpic-run submit --kind scouting --gate G2 --package "$PKG2" --launcher local \
              --cores 1 --wall 00:20:00 --parent "$srid" \
              --purpose "repro/ablation: check of the card smoke $srid (core T5) against JOURNAL.md entry 1 P-T5 and core's processor run core-20261123-030705-6b6a4bd; gates the six 256^3 ablation runs" \
              -- python3 "$CHK" --run "/data/haiyangw/nrpic/scratch/E-stoch-inf/$srid" --ref "$CORE_REF" \
              --out '$NRPIC_RUN_DIR' 2>&1); rc=$?
      echo "$out" >> "$S/seq.log"
      crid=$(grep -oE 'E-[0-9]{8}-[0-9]{6}-[0-9a-f]{7}' <<< "$out" | head -1)
      v=""
      [[ -n $crid ]] && v=$(python3 -I -c "import json,sys; print(json.load(open(sys.argv[1]))['verdict'])" \
                              "/data/haiyangw/nrpic/scratch/E-stoch-inf/$crid/verdict.json" 2>/dev/null)
      if [[ $v == PASS ]]; then set_state SMOKECHK "$crid" pass; log "smoke check $crid: PASS (ablation lines free)"
      elif [[ $v == FAIL ]]; then set_state SMOKECHK "$crid" fail; log "smoke check $crid: FAIL (ablation lines held; report to core)"
      else
        n_err=$(awk '$1=="SMOKECHK" && $3=="error"' "$S/state.tsv" | wc -l)
        if (( n_err >= 3 )); then set_state SMOKECHK "${crid:--}" fail; log "smoke check: no verdict x3 (rc $rc): held"
        else set_state SMOKECHK "${crid:--}" error; log "smoke check: no verdict (rc $rc); retry next poll"; fi
      fi
    fi
  fi
  # 3. next line: ablation "head" lines, then the scope queue, then ablation "tail" lines
  next=""; nextq=""
  cand() {  # label state -> 0 if it may be submitted now
    local s; s=$(state_of "$1"); [[ -z $s || $s == refused || $s == error || $s == held ]]
  }
  while read -r lab gh lau deck kind ord gate rest; do
    [[ -z $lab || $lab == \#* || $ord != head ]] && continue
    if cand "$lab"; then next=$lab; nextq=2; ngh=$gh; nlau=$lau; ndeck=$deck; nkind=$kind; ngate=$gate; nrest=$rest; break; fi
  done < "$Q2"
  if [[ -z $next ]]; then
    while read -r lab gh lau deck rest; do
      [[ -z $lab || $lab == \#* ]] && continue
      if cand "$lab"; then next=$lab; nextq=1; ngh=$gh; nlau=$lau; ndeck=$deck; nkind=production; ngate=-; nrest=$rest; break; fi
    done < "$Q1"
  fi
  if [[ -z $next ]]; then
    while read -r lab gh lau deck kind ord gate rest; do
      [[ -z $lab || $lab == \#* || $ord != tail ]] && continue
      if cand "$lab"; then next=$lab; nextq=2; ngh=$gh; nlau=$lau; ndeck=$deck; nkind=$kind; ngate=$gate; nrest=$rest; break; fi
    done < "$Q2"
  fi
  # gate and cost guard of the ablation lines
  if [[ -n $next && $nextq == 2 ]]; then
    hold=""
    if [[ $ngate == SMOKE && $(state_of SMOKECHK) != pass ]]; then
      hold="gate: smoke check $(state_of SMOKECHK)"
    else
      read -r used opn est <<< "$(q2_cost)"
      if python3 -I -c "import sys; u,o,e,c=map(float,sys.argv[1:]); sys.exit(0 if u+(o+1)*e>c else 1)" "$used" "$opn" "$est" "$CAP2"; then
        hold="cost: used $used + ($opn + 1) x $est > $CAP2 card-hours"
      fi
    fi
    if [[ -n $hold ]]; then
      now=$(date +%s)
      if (( now - last_hold > 3600 )); then log "held $next ($hold)"; last_hold=$now; fi
      next=""
    fi
  fi
  if [[ -z $next ]]; then
    # nothing may be submitted now: exit when no run is in flight and no smoke check is due
    open=0; for l in $(awk '{print $1}' "$S/state.tsv" | sort -u); do [[ $(state_of "$l") == submitted ]] && open=1; done
    cs=$(state_of SMOKECHK); chk_due=0
    [[ $(state_of "$SMOKE_LABEL") == finished ]] && [[ -z $cs || $cs == error ]] && chk_due=1
    if (( open == 0 && chk_due == 0 && DRY == 0 )); then
      log "nothing left to submit (queues done, or the rest held) and every run closed: exit"; rm -f "$S/pid"; exit 0
    fi
  elif [[ -e /data/haiyangw/nrpic/locks/PAUSE ]]; then
    log "PAUSE flag: nothing submitted"
  elif (( DRY )); then
    echo "DRY: next $next (queue $nextq, $nlau, $ndeck, kind $nkind, gate $ngate); eligible E jobs now $(n_eligible)"
  elif (( $(n_eligible) < MAXJ )); then
    now=$(date +%s)
    if [[ $(state_of "$next") == refused ]] && (( now - last_try < RETRY )); then :; else
      last_try=$now
      if [[ $nextq == 1 ]]; then
        exe=$EXE1; pkg=$PKG1; pre=$PRE1
        purpose="repro/scope $next: ${nrest%%|*}; arXiv:2512.14649 reproduction, release core-v0.6 card build; predictions repro/scope/JOURNAL.md entry 1"
      else
        exe=$EXE2; pkg=$PKG2; pre=$PRE2
        purpose="repro/ablation $next: ${nrest%%|*}; arXiv:2512.14649 Fig. 9, branch card build core_noise-level2 (6ca93cba, decision 0031 item 3); predictions repro/ablation/JOURNAL.md entry 1"
      fi
      read -r -a args <<< "${nrest#*|}"
      pr=(); [[ $nkind == production ]] && pr=(--preregistered "$pre")
      if [[ $nlau == batch ]]; then
        out=$(harness/bin/nrpic-run submit --kind "$nkind" --gate G2 "${pr[@]}" \
                --package "$pkg" --launcher batch --gpu-hours "$ngh" --exe "$exe" --list "$ndeck" \
                --wall 00:30:00 --purpose "$purpose" 2>&1); rc=$?
      else
        out=$(harness/bin/nrpic-run submit --kind "$nkind" --gate G2 "${pr[@]}" \
                --package "$pkg" --launcher chain --gpu-hours "$ngh" --exe "$exe" \
                --purpose "$purpose" -- "$ndeck" "${args[@]}" 2>&1); rc=$?
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
  (( DRY )) && { echo "DRY: held message (if any) in $S/seq.log"; exit 0; }
  sleep "$POLL"
done
