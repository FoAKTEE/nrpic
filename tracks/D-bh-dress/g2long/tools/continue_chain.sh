#!/usr/bin/env bash
# Continue in place a card chain of D-bh-dress that nrpic-run registered (launcher chain) and
# whose Slurm job was cancelled while it waited (2026-11-24 12:00 PST, decision 0033) or that
# was cut. Made for the shared card queue (harness/RULES.md, section "Shared card queue"):
#
#   harness/bin/nrpic-queue add --label L [--after L0] --priority 2 \
#       --cmd 'tracks/D-bh-dress/g2long/tools/continue_chain.sh <run_id> [max_segments]'
#   tracks/D-bh-dress/g2long/tools/continue_chain.sh --dry-run <run_id> [max_segments]
#
# It submits AT MOST ONE Slurm job: scripts/submit_chain.sh <run dir> <deck> <EXTRA_ARGS> on
# the run's own directory scratch/D-bh-dress/<run_id>/, with the settings of its
# chain/config.sh: JOB_NAME = run id (so the queue knows the chain's jobs), PROC_NAME,
# MAX_SEGMENTS, EXTRA_ARGS (restart cadence output2/dt), ATHENA_WALL, SLURM_TIME and the
# same executable (EXE_SRC, byte-compared with chain/athena). The chain resumes from the
# newest restart file in <run dir>/rst/, or starts at t = 0 when it has none (a run that
# was cancelled before its first segment). The run id, manifest, predictions and card-hour
# reservation stay those of the original registration; nrpic-run finish later collects
# every segment's job from chain/.
# max_segments (optional) replaces MAX_SEGMENTS of config.sh; it is the total count of
# segments of the chain, the segments already used included (chain/segment).
#
# Refuses (exit 2, nothing submitted): a run id of another owner or form; no manifest, or
# one that is final or not a chain; no chain/config.sh; JOB_NAME not the run id; chain
# STATUS DONE; a job of that name in squeue, or squeue not answering; the deck of the
# manifest not byte-identical with chain/input.athinput; the executable not byte-identical
# with chain/athena; no segment left under MAX_SEGMENTS.
# Records, after a submission: a line in <run dir>/chain/continuations.log and an entry in
# the manifest's "continuations" list, committed path-limited on the branch. Once sbatch
# has accepted the job the exit status is 0 even if that record fails (a warning is
# printed), so the queue never submits the chain twice.
set -uo pipefail

die() { echo "continue_chain: $*" >&2; exit 2; }

WT=$(git rev-parse --show-toplevel 2>/dev/null) || die "not inside a git worktree"
cd "$WT" || die "cannot cd to $WT"
OWNER=D-bh-dress
SCR=/data/haiyangw/nrpic/scratch/$OWNER
PY=/usr/bin/python3

dry=0
if [[ ${1:-} == --dry-run ]]; then dry=1; shift; fi
run=${1:-}
maxseg=${2:-}
[[ -n $run ]] || die "usage: continue_chain.sh [--dry-run] <run_id> [max_segments]"
[[ $run =~ ^D-[0-9]{8}-[0-9]{6}-[0-9a-f]{7}$ ]] || die "run id '$run' is not of the form D-YYYYMMDD-HHMMSS-<commit7>"
[[ -z $maxseg || $maxseg =~ ^[1-9][0-9]*$ ]] || die "max_segments '$maxseg' is not a positive integer"

RUNDIR=$SCR/$run
C=$RUNDIR/chain
MAN=tracks/$OWNER/runs/$run/manifest.json
[[ -f $MAN ]] || die "no manifest $MAN on this branch"
[[ -f $C/config.sh ]] || die "no $C/config.sh (not a chain started by scripts/submit_chain.sh)"

# manifest: status, launcher, deck (the last argument of the registered command)
mapfile -t mf < <("$PY" -I - "$MAN" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
cmd = m.get("command") or []
print(m.get("status", ""))
print(m.get("launcher", ""))
print(m.get("run_id", ""))
print(cmd[2] if len(cmd) >= 3 else "")
EOF
)
mstatus=${mf[0]:-}; mlauncher=${mf[1]:-}; mrun=${mf[2]:-}; deck=${mf[3]:-}
[[ $mrun == "$run" ]] || die "manifest run_id '$mrun' differs from '$run'"
[[ $mlauncher == chain ]] || die "$run has launcher '$mlauncher', not chain"
case $mstatus in completed|failed|stopped) die "$run is already closed ($mstatus) in the run tool";; esac
[[ -n $deck && -f $deck ]] || die "deck '$deck' of the manifest's command not found"

# the chain's own settings (written by scripts/submit_chain.sh at its first start)
# shellcheck source=/dev/null
source "$C/config.sh" || die "cannot read $C/config.sh"
[[ ${JOB_NAME:-} == "$run" ]] || die "JOB_NAME in config.sh is '${JOB_NAME:-}', not the run id"
[[ -n ${PROC_NAME:-} ]] || die "no PROC_NAME in config.sh"
chain_script=$WT/scripts/submit_chain.sh
[[ -x $chain_script ]] || die "no executable $chain_script"
[[ ${SCRIPT:-} == "$chain_script" ]] || echo "continue_chain: note: config.sh named SCRIPT=${SCRIPT:-}; using $chain_script"
st=$(cat "$C/STATUS" 2>/dev/null || echo NONE)
[[ $st != DONE ]] || die "chain STATUS is DONE: nothing to continue"

# no job of this chain in the queue (by name; the chain resubmits under the same name)
q=$(squeue -h -n "$run" -o '%i %T' 2>&1); qrc=$?
(( qrc == 0 )) || die "squeue did not answer ($q)"
[[ -z $q ]] || die "a job of this chain is in squeue: $q"

# byte identity of deck and executable with what the chain ran so far
sha() { sha256sum "$1" | cut -d' ' -f1; }
[[ $(sha "$deck") == $(sha "$C/input.athinput") ]] || die "deck $deck differs from $C/input.athinput"
[[ -x ${EXE_SRC:-} ]] || die "executable EXE_SRC='${EXE_SRC:-}' not found"
exe_sha=$(sha "$EXE_SRC")
[[ $exe_sha == $(sha "$C/athena") ]] || die "executable $EXE_SRC differs from $C/athena"

seg=$(cat "$C/segment" 2>/dev/null || echo 0)
ms=${maxseg:-$MAX_SEGMENTS}
(( seg < ms )) || die "segments used $seg, MAX_SEGMENTS $ms: none left (pass a larger max_segments)"
rst=$(ls -1t "$RUNDIR"/rst/*.rst 2>/dev/null | head -n 1)
from=${rst:-none (starts from t = 0 with the deck)}

echo "run $run: chain STATUS $st, segments used $seg of $ms, newest restart: $from"
echo "  exe $EXE_SRC (sha256 ${exe_sha:0:12}) as $PROC_NAME; deck $deck; extra args: ${EXTRA_ARGS[*]}"
cmdline=(env "PROC_NAME=$PROC_NAME" "JOB_NAME=$JOB_NAME" "MAX_SEGMENTS=$ms" "ATHENA_EXE=$EXE_SRC"
         "ATHENA_WALL=$ATHENA_WALL" "SLURM_TIME=$SLURM_TIME" "CPUS=$CPUS" "PARTITION=$PARTITION"
         "SLURM_EXTRA=$SLURM_EXTRA" "CHECK_CMD=$CHECK_CMD" "MAX_OUTSIDE_KILLS=${MAX_OUTSIDE_KILLS:-2}"
         "$chain_script" "$RUNDIR" "$deck" "${EXTRA_ARGS[@]}")
if (( dry )); then
  printf '  dry run, would run:'; printf ' %q' "${cmdline[@]}"; echo
  exit 0
fi

old_jid=$(cat "$C/jobid" 2>/dev/null || true)
"${cmdline[@]}"; rc=$?
jid=$(cat "$C/jobid" 2>/dev/null || true)
if (( rc != 0 )) || [[ -z $jid || $jid == "$old_jid" ]]; then
  echo "continue_chain: scripts/submit_chain.sh exit $rc, job id '$jid' (before '$old_jid')" >&2
  # submitted nothing new: let the queue mark the entry failed
  [[ -n $jid && $jid != "$old_jid" ]] || exit 1
fi

now=$(date '+%Y-%m-%dT%H:%M:%S%z')
echo "$now job $jid from ${rst:-t=0} max_segments $ms (continue_chain.sh, shared queue)" >> "$C/continuations.log" \
  || echo "continue_chain: warning: could not write $C/continuations.log" >&2
if "$PY" -I - "$MAN" "$now" "$jid" "${rst:-}" "$ms" "$seg" <<'EOF'
import json, sys
p, now, jid, rst, ms, seg = sys.argv[1:7]
m = json.load(open(p))
m.setdefault("continuations", []).append({
    "at": now, "job_id": jid, "from_restart": rst or None, "segments_used_before": int(seg),
    "max_segments": int(ms),
    "via": "harness/bin/nrpic-queue --cmd tracks/D-bh-dress/g2long/tools/continue_chain.sh",
    "reason": "continued in place after its waiting job was cancelled under the queue cap (decision 0033)"})
with open(p + ".tmp", "w") as f:
    json.dump(m, f, indent=2)
    f.write("\n")
import os
os.replace(p + ".tmp", p)
EOF
then
  gd=$(git rev-parse --git-dir)
  for _ in $(seq 1 60); do [[ -e $gd/index.lock ]] || break; sleep 2; done
  git commit -q -m "Run $run: chain continued in place by the shared queue (job $jid)" -- "$MAN" \
    || echo "continue_chain: warning: manifest $MAN changed but not committed" >&2
else
  echo "continue_chain: warning: manifest $MAN not updated" >&2
fi
echo "continue_chain: $run continued as job $jid"
exit 0
