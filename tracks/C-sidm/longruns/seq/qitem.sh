#!/usr/bin/env bash
# One item of tracks/C-sidm/longruns/seq/queue.txt, submitted by the shared card queue
# (decision 0033; harness/RULES.md "Shared card queue"). It replaces the sequencer seq.sh,
# which was stopped by the orchestrator on 2026-11-24 12:00 PST and is not to be started again.
#
#   tracks/C-sidm/longruns/seq/qitem.sh <item> [--dry-run]   submit one item (at most one job)
#   tracks/C-sidm/longruns/seq/qitem.sh close <run_id>       close a run whose card work ended
#
# Queue it from the worktree root (the line runs with bash there, under the dispatcher's marker):
#   harness/bin/nrpic-queue add --label <label> --priority <N> --cmd 'tracks/C-sidm/longruns/seq/qitem.sh <item>'
#
# What it does, from the item's line in queue.txt (the parameters committed with the predictions,
# JOURNAL.md 2026-11-21T20:25Z and 2026-11-24T13:14Z), exactly as seq.sh did for that item:
#  - chain item: `harness/bin/nrpic-run submit --kind scouting --gate G2 --package
#    tracks/C-sidm/longruns --exe <core-v0.6 card exe> --particles N --gpu-hours H --purpose ...
#    --launcher chain -- <deck>` (one job), then the chain's process name (queue line) and its
#    segment cap raised to SEG_FLOOR (20) in chain/config.sh, as seq.sh did since batch 11 (a
#    preempted segment counts as a segment; the card-hour reservation stays at H).
#  - resume item: continue a registered chain that ended FAILED or STOPPED, in place, from its
#    newest restart file: `scripts/submit_chain.sh <run dir> <deck> [athena arg]` with
#    MAX_SEGMENTS = its segment count + the number in the queue line, JOB_NAME = its run id, the
#    same executable and process name (one job). The manifest gets a `continuations` entry,
#    committed path-limited on track/C-sidm. The run is never repeated from t = 0.
# Outside the dispatcher (no NRPIC_QUEUE_DISPATCH) it refuses to submit; --dry-run checks the
# item and prints what it would do, writing nothing.
#
# close <run_id>: when no job of the run is in squeue, `harness/bin/nrpic-run finish <run_id>`,
# with --status from chain/STATUS (DONE completed, STOPPED stopped, else failed) for a run that
# was continued in place (its manifest was final before the continuation).
set -uo pipefail

WT=/data/haiyangw/nrpic/wt/C-sidm
PKG=tracks/C-sidm/longruns
Q=$WT/$PKG/seq/queue.txt
SCR=/data/haiyangw/nrpic/scratch/C-sidm
EXE=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena
SEG_FLOOR=${SEG_FLOOR:-20}
GITDIR=/data/haiyangw/nrpic/.git/worktrees/C-sidm

die() { echo "qitem.sh: $*" >&2; exit 1; }
job_in_queue() { [[ -n $1 && $1 != - && -n $(squeue -h -j "$1" -o %T 2>/dev/null) ]]; }
name_in_queue() { squeue -h -u "${USER:-$(id -un)}" -o '%j' 2>/dev/null | grep -qx "$1"; }
wait_git() {
  local n=0
  while [[ -e $GITDIR/index.lock || -e $GITDIR/MERGE_HEAD ]]; do
    sleep 10; n=$((n + 1)); (( n > 30 )) && return 1
  done
  return 0
}
manifest_status() {
  python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1])).get("status"))' \
    "$WT/tracks/C-sidm/runs/$1/manifest.json" 2>/dev/null
}

# ---------------------------------------------------------------- close <run_id>
if [[ ${1:-} == close ]]; then
  run=${2:-}; [[ $run =~ ^C-[0-9]{8}-[0-9]{6}-[0-9a-f]{7}$ ]] || die "close needs a run id of C-sidm"
  C=$SCR/$run/chain
  name_in_queue "$run" && die "a job named $run is still in squeue: not closed"
  job_in_queue "$(cat "$C/jobid" 2>/dev/null)" && die "job $(cat "$C/jobid") of $run is still in squeue"
  cst=$(cat "$C/STATUS" 2>/dev/null || echo NONE)
  fargs=()
  if python3 -I -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1])).get("continuations") else 1)' \
       "$WT/tracks/C-sidm/runs/$run/manifest.json" 2>/dev/null; then
    case $cst in DONE) fargs=(--status completed) ;; STOPPED) fargs=(--status stopped) ;;
                 *) fargs=(--status failed) ;; esac
  fi
  wait_git || die "git index busy"
  cd "$WT" && exec harness/bin/nrpic-run finish "$run" "${fargs[@]}"
fi

# ---------------------------------------------------------------- submit one item
item=${1:-}; [[ -n $item ]] || die "usage: qitem.sh <item> [--dry-run] | qitem.sh close <run_id>"
DRY=0; [[ ${2:-} == --dry-run ]] && DRY=1
if (( ! DRY )) && [[ -z ${NRPIC_QUEUE_DISPATCH:-} ]]; then
  die "refused: card runs reach Slurm only through the shared queue (decision 0033). Queue it:
  harness/bin/nrpic-queue add --label <label> --cmd 'tracks/C-sidm/longruns/seq/qitem.sh $item'"
fi
line=$(grep -vE '^[[:space:]]*(#|$)' "$Q" | awk -v i="$item" '$1==i' | head -n 1)
[[ -n $line ]] || die "no item '$item' in $Q"
read -r _ la rest <<< "$line"
cd "$WT" || die "no worktree $WT"

if [[ $la == resume ]]; then
  read -r _ _ add run pn deck xarg purpose <<< "$line"
  R=$SCR/$run; C=$R/chain
  [[ -d $C ]] || die "$run has no chain directory $C"
  st=$(cat "$C/STATUS" 2>/dev/null || echo NONE)
  case $st in FAILED|STOPPED) ;; *) die "chain $run is $st, not FAILED or STOPPED: not resumed" ;; esac
  name_in_queue "$run" && die "a job named $run is still in squeue"
  job_in_queue "$(cat "$C/jobid" 2>/dev/null)" && die "job $(cat "$C/jobid") of $run is still in squeue"
  mst=$(manifest_status "$run")
  [[ $mst == failed || $mst == stopped ]] || die "manifest of $run is '$mst', not closed (close it first)"
  [[ -f $WT/$deck ]] || die "deck $deck missing"
  seg=$(cat "$C/segment" 2>/dev/null || echo 0)
  max=$((seg + add))
  rst=$(find "$R/rst" -maxdepth 1 -name '*.rst' -printf '%T@ %p\n' 2>/dev/null | sort -k1,1gr | head -1 | cut -d' ' -f2-)
  [[ -n $rst ]] || die "$run has no restart file in $R/rst"
  xa=(); [[ $xarg != - ]] && xa=("$xarg")
  if (( DRY )); then
    echo "dry run $item: resume $run (chain $st, manifest $mst) from ${rst##*/}; segments $seg -> at most $max;"
    echo "  ATHENA_EXE=$EXE MAX_SEGMENTS=$max JOB_NAME=$run PROC_NAME=$pn scripts/submit_chain.sh $R $WT/$deck ${xa[*]}"
    exit 0
  fi
  wait_git || die "git index busy"
  python3 -I - "$WT/tracks/C-sidm/runs/$run/manifest.json" "$max" "$rst" "$xarg" "$item" "$mst" <<'PY' || die "manifest note failed"
import json, sys, datetime
mf, mx, rst, xarg, item, mst = sys.argv[1:7]
m = json.load(open(mf))
m.setdefault("continuations", []).append({
    "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "by": "tracks/C-sidm/longruns/seq/qitem.sh %s (shared card queue, decision 0033)" % item,
    "kind": "in-place resume of a chain cut by preemption or stopped while waiting",
    "status_before": mst, "from_restart": rst, "max_segments": int(mx),
    "extra_athena_args": [] if xarg == "-" else [xarg],
    "predictions": "tracks/C-sidm/JOURNAL.md 2026-11-21T20:25Z; resume rule 2026-11-24 entry"})
json.dump(m, open(mf, "w"), indent=2)
open(mf, "a").write("\n")
PY
  git commit -q -m "C(run): continue $run in place from its newest restart (qitem.sh $item)" \
     -m "Resumed through the shared card queue with MAX_SEGMENTS $max${xarg:+, athena arg $xarg}." \
     -- "tracks/C-sidm/runs/$run/manifest.json" || die "manifest commit failed"
  out=$(ATHENA_EXE=$EXE MAX_SEGMENTS=$max JOB_NAME=$run PROC_NAME=$pn \
        scripts/submit_chain.sh "$R" "$WT/$deck" "${xa[@]}" 2>&1); rc=$?
  echo "$out"
  grep -qE 'chain started in .*: job [0-9]+' <<< "$out" || die "submit_chain.sh did not start (exit $rc)"
  exit 0
fi

[[ $la == chain ]] || die "item $item has launcher '$la' (only chain and resume are queued here)"
read -r _ _ gh np pn deck purpose <<< "$line"
args=(submit --kind scouting --gate G2 --package "$PKG" --exe "$EXE" --particles "$np"
      --gpu-hours "$gh" --purpose "longruns $item: $purpose (qitem.sh via nrpic-queue; JOURNAL.md)"
      --launcher chain)
if (( DRY )); then
  harness/bin/nrpic-run "${args[@]}" --dry-run -- "$deck"; rc=$?
  echo "dry run $item: then PROC_NAME=$pn and MAX_SEGMENTS=max(cap, $SEG_FLOOR) in chain/config.sh"
  exit $rc
fi
wait_git || die "git index busy"
out=$(harness/bin/nrpic-run "${args[@]}" -- "$deck" 2>&1); rc=$?
echo "$out"
(( rc == 0 )) || { echo "$out" | head -n 3 >&2; exit "$rc"; }
run=$(grep -oE 'submitted (C-[0-9]{8}-[0-9]{6}-[0-9a-f]{7}) as Slurm job [0-9]+' <<< "$out" | awk '{print $2}')
[[ -n $run ]] || die "nrpic-run printed no run id"
C=$SCR/$run/chain
if [[ -f $C/config.sh && $pn != - ]] && ! grep -q "^PROC_NAME=$pn\$" "$C/config.sh"; then
  tmp=$(mktemp "$C/.config.XXXXXX")
  sed "s/^PROC_NAME=.*/PROC_NAME=$pn/" "$C/config.sh" > "$tmp" && mv "$tmp" "$C/config.sh"
  ln -f "$C/athena" "$C/$pn" 2>/dev/null || cp -p "$C/athena" "$C/$pn"
  echo "qitem.sh: $item PROC_NAME $pn"
fi
mx=$(sed -n 's/^MAX_SEGMENTS=//p' "$C/config.sh" 2>/dev/null)
if [[ -n $mx ]] && (( mx < SEG_FLOOR )); then
  tmp=$(mktemp "$C/.config.XXXXXX")
  sed "s/^MAX_SEGMENTS=.*/MAX_SEGMENTS=$SEG_FLOOR/" "$C/config.sh" > "$tmp" && mv "$tmp" "$C/config.sh"
  echo "qitem.sh: $item MAX_SEGMENTS $mx -> $SEG_FLOOR"
fi
exit 0
