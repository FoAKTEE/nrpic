#!/usr/bin/env bash
# Continue a cut chain of this owner IN PLACE from its newest restart file, as one entry of the
# shared card queue (decision 0033; harness/RULES.md, section "Shared card queue").
#
#   tracks/A-emd-pbh/threshold_ball/scripts/continue_chain.sh <run_id> <MAX_SEGMENTS> [--dry-run]
#
# Queue it (from the worktree root, worktree committed):
#   harness/bin/nrpic-queue add --label <label> [--after <label>] [--priority N] \
#     --cmd 'tracks/A-emd-pbh/threshold_ball/scripts/continue_chain.sh <run_id> <MAX_SEGMENTS>'
#
# What it does: the same registered run (no new manifest), the same run directory
# scratch/A-emd-pbh/<run_id>, the same executable (chain/config.sh EXE_SRC, checked cmp-identical
# to the chain's copy), the same deck (the manifest's, checked identical to chain/input.athinput),
# the same arguments (config.sh EXTRA_ARGS), JOB_NAME = <run_id> and the same PROC_NAME; only
# MAX_SEGMENTS is set from the second argument (segments are counted over the whole chain, in
# chain/segment). scripts/submit_chain.sh then submits exactly ONE job, which resumes from the
# newest rst/*.rst. Its line "chain started in <rundir>: job <id>" tells the queue run and job.
# After a submission the continuation is appended to the manifest's "notes" and that one path is
# committed (path-limited); a failure there is reported on stderr but does not fail the entry,
# because the job has been submitted.
# Refuses (exit 1, nothing submitted): outside the dispatcher (no NRPIC_QUEUE_DISPATCH) unless
# --dry-run, a job of the chain still in squeue, chain STATUS DONE, no restart file, a changed
# deck or executable, MAX_SEGMENTS not above the segments already used.
set -uo pipefail

die() { echo "continue_chain: $*" >&2; exit 1; }

[[ $# -ge 2 ]] || die "usage: $0 <run_id> <MAX_SEGMENTS> [--dry-run]"
RUN_ID=$1; MAXSEG=$2; DRY=0
[[ ${3:-} == --dry-run ]] && DRY=1
[[ $RUN_ID =~ ^A-[0-9]{8}-[0-9]{6}-[0-9a-f]{7}$ ]] || die "not a run id of A-emd-pbh: $RUN_ID"
[[ $MAXSEG =~ ^[0-9]+$ ]] || die "MAX_SEGMENTS must be a whole number: $MAXSEG"

WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
DATA=/data/haiyangw/nrpic/scratch/A-emd-pbh
RUNDIR=$DATA/$RUN_ID
C=$RUNDIR/chain
MAN=tracks/A-emd-pbh/runs/$RUN_ID/manifest.json
[[ -f $WT/$MAN ]] || die "no manifest $WT/$MAN"
[[ -f $C/config.sh ]] || die "no chain in $RUNDIR"
if (( ! DRY )) && [[ -z ${NRPIC_QUEUE_DISPATCH:-} ]]; then
  die "card runs reach Slurm only through the shared queue: add this line with nrpic-queue add --cmd (or use --dry-run)"
fi

# shellcheck source=/dev/null
source "$C/config.sh"
[[ $JOB_NAME == "$RUN_ID" ]] || die "chain JOB_NAME '$JOB_NAME' is not the run id"
[[ -x $EXE_SRC ]] || die "executable $EXE_SRC missing"
cmp -s "$EXE_SRC" "$C/athena" || die "executable $EXE_SRC differs from the chain's copy $C/athena"

DECK=$(python3 -I -c 'import json,sys; m=json.load(open(sys.argv[1])); print(m["command"][2])' "$WT/$MAN") \
  || die "cannot read the deck from $MAN"
[[ -f $DECK ]] || die "deck $DECK missing"
cmp -s "$DECK" "$C/input.athinput" || die "deck $DECK differs from the chain's copy $C/input.athinput"

seg=$(cat "$C/segment" 2>/dev/null || echo 0)
(( MAXSEG > seg )) || die "MAX_SEGMENTS $MAXSEG leaves no segment (already used: $seg)"
status=$(cat "$C/STATUS" 2>/dev/null || echo none)
[[ $status != DONE ]] || die "chain is DONE"
jid=$(cat "$C/jobid" 2>/dev/null || true)
if [[ -n $jid && -n $(squeue -h -j "$jid" -o %T 2>/dev/null) ]]; then die "job $jid of the chain is still in squeue"; fi
if [[ -n $(squeue -h -u "$USER" -n "$RUN_ID" -o %i 2>/dev/null) ]]; then die "a job named $RUN_ID is in squeue"; fi
rst=$(find "$RUNDIR/rst" -maxdepth 1 -name '*.rst' -printf '%T@ %p\n' 2>/dev/null | sort -k1,1gr -k2,2r | head -1 | cut -d' ' -f2-)
[[ -n $rst ]] || die "no restart file in $RUNDIR/rst"
last=$(grep -E "wall-clock limit reached|Terminating|STATUS" "$C/events.log" | tail -1)

echo "continue_chain: run $RUN_ID, segments used $seg, MAX_SEGMENTS $MAX_SEGMENTS -> $MAXSEG, status $status (last job $jid not in squeue)"
echo "continue_chain: newest restart $rst; last event: $last"
echo "continue_chain: exe $EXE_SRC as $PROC_NAME; deck $DECK"
CMD=(env ATHENA_EXE="$EXE_SRC" JOB_NAME="$JOB_NAME" PROC_NAME="$PROC_NAME" MAX_SEGMENTS="$MAXSEG"
     ATHENA_WALL="$ATHENA_WALL" SLURM_TIME="$SLURM_TIME" CPUS="$CPUS" PARTITION="$PARTITION"
     SLURM_EXTRA="$SLURM_EXTRA" CHECK_CMD="$CHECK_CMD" MAX_OUTSIDE_KILLS="$MAX_OUTSIDE_KILLS"
     "$SCRIPT" "$RUNDIR" "$DECK" "${EXTRA_ARGS[@]}")
if (( DRY )); then
  printf 'continue_chain: dry run, would run:'; printf ' %q' "${CMD[@]}"; echo
  exit 0
fi

out=$("${CMD[@]}" 2>&1); rc=$?
echo "$out"
(( rc == 0 )) || die "submit_chain.sh exited $rc; nothing recorded"
newjid=$(sed -nE 's/.*chain started in .*: job ([0-9]+).*/\1/p' <<<"$out" | tail -1)

# record the continuation in the manifest (notes) and commit that one path
note="$(date -u +%Y-%m-%dT%H:%M:%SZ) continued in place by queue entry ${NRPIC_QUEUE_DISPATCH%%:*}: job ${newjid:-?}, from $(basename "$rst"), segments used $seg, MAX_SEGMENTS $MAXSEG, same exe/deck/args (threshold_ball/scripts/continue_chain.sh)"
if python3 -I - "$WT/$MAN" "$note" <<'PY'
import json, sys
p, note = sys.argv[1], sys.argv[2]
m = json.load(open(p))
old = m.get("notes") or ""
m["notes"] = (old + "\n" if old else "") + note
with open(p + ".tmp", "w") as f:
    json.dump(m, f, indent=2)
    f.write("\n")
import os
os.replace(p + ".tmp", p)
PY
then
  gd=$(git -C "$WT" rev-parse --absolute-git-dir)
  for _ in $(seq 1 60); do             # wait up to five minutes for another writer of the index
    [[ -e $gd/index.lock ]] || break
    sleep 5
  done
  git -C "$WT" commit -q -m "Continue chain $RUN_ID in place from $(basename "$rst") (queue, job ${newjid:-?})" \
    -m "Same registered run, exe, deck and arguments; MAX_SEGMENTS $MAXSEG." \
    -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- "$MAN" \
    || echo "continue_chain: WARNING: manifest note written but not committed ($MAN)" >&2
else
  echo "continue_chain: WARNING: could not write the note into $MAN" >&2
fi
exit 0
