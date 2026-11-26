#!/usr/bin/env bash
# Continue in place a card chain of F-hills that nrpic-run registered (launcher chain) and that
# ended at its segment cap or was cut (batch 25: A2, F-20261124-210400-902c650, ruling 0042
# item 2). Made for the shared card queue (harness/RULES.md, section "Shared card queue"):
#
#   harness/bin/nrpic-queue add --label L --priority 2 \
#       --cmd 'tracks/F-hills/binary_conv/scripts/continue_chain.sh <run_id> <max_segments> [--extra-input <file>]'
#   tracks/F-hills/binary_conv/scripts/continue_chain.sh --dry-run <run_id> <max_segments> [--extra-input <file>]
#
# Adapted from tracks/D-bh-dress/g2long/tools/continue_chain.sh (branch track/D-bh-dress), with:
#  - `harness/bin/nrpic-queue check-dispatch || exit 1` first (not in a dry run);
#  - segments counted as the chain script counts them: attempts (chain/segment) minus attempts
#    cut by a signal (chain/uncounted); max_segments is the new cap of counted segments;
#  - --extra-input <file>: appends `-i <absolute path>` to the chain's EXTRA_ARGS (once), so that
#    each segment's restart reads that file too (decision 0043 item 5: `<fastflow> diagnostics =
#    true` in a continued run). Tested on processors first (JOURNAL batch 25, R25).
#
# It submits AT MOST ONE Slurm job: scripts/submit_chain.sh <run dir> <deck> <EXTRA_ARGS> on the
# run's own directory scratch/F-hills/<run_id>/, with chain/config.sh's settings: JOB_NAME = run
# id, PROC_NAME, ATHENA_WALL, SLURM_TIME, the same executable (EXE_SRC, byte-compared with
# chain/athena). The chain resumes from the newest restart file in <run dir>/rst/.
# Refuses (exit 2, nothing submitted): a run id of another form; no manifest, or one that is
# closed or not a chain; no chain/config.sh; JOB_NAME not the run id; chain STATUS DONE; a job of
# that name in squeue, or squeue not answering; deck or executable not byte-identical with what
# the chain ran; no segment left under max_segments; no restart file.
# Records after a submission: a line in <run dir>/chain/continuations.log and an entry in the
# manifest's "continuations", committed path-limited. Once sbatch accepted the job the exit
# status is 0 even if that record fails, so the queue never submits the chain twice.
set -uo pipefail

die() { echo "continue_chain: $*" >&2; exit 2; }

WT=$(git rev-parse --show-toplevel 2>/dev/null) || die "not inside a git worktree"
cd "$WT" || die "cannot cd to $WT"
OWNER=F-hills
SCR=/data/haiyangw/nrpic/scratch/$OWNER
PY=/usr/bin/python3

dry=0
if [[ ${1:-} == --dry-run ]]; then dry=1; shift; fi
run=${1:-}
maxseg=${2:-}
shift 2 2>/dev/null || true
extra_in=""
if [[ ${1:-} == --extra-input ]]; then extra_in=${2:-}; [[ -n $extra_in ]] || die "--extra-input needs a file"; fi
[[ -n $run && -n $maxseg ]] || die "usage: continue_chain.sh [--dry-run] <run_id> <max_segments> [--extra-input <file>]"
[[ $run =~ ^F-[0-9]{8}-[0-9]{6}-[0-9a-f]{7}$ ]] || die "run id '$run' is not of the form F-YYYYMMDD-HHMMSS-<commit7>"
[[ $maxseg =~ ^[1-9][0-9]*$ ]] || die "max_segments '$maxseg' is not a positive integer"

if (( ! dry )); then
  harness/bin/nrpic-queue check-dispatch || exit 1
fi

RUNDIR=$SCR/$run
C=$RUNDIR/chain
MAN=tracks/$OWNER/runs/$run/manifest.json
[[ -f $MAN ]] || die "no manifest $MAN on this branch"
[[ -f $C/config.sh ]] || die "no $C/config.sh (not a chain started by scripts/submit_chain.sh)"

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

# shellcheck source=/dev/null
source "$C/config.sh" || die "cannot read $C/config.sh"
[[ ${JOB_NAME:-} == "$run" ]] || die "JOB_NAME in config.sh is '${JOB_NAME:-}', not the run id"
[[ -n ${PROC_NAME:-} ]] || die "no PROC_NAME in config.sh"
chain_script=$WT/scripts/submit_chain.sh
[[ -x $chain_script ]] || die "no executable $chain_script"
st=$(cat "$C/STATUS" 2>/dev/null || echo NONE)
[[ $st != DONE ]] || die "chain STATUS is DONE: nothing to continue"

q=$(squeue -h -n "$run" -o '%i %T' 2>&1); qrc=$?
(( qrc == 0 )) || die "squeue did not answer ($q)"
[[ -z $q ]] || die "a job of this chain is in squeue: $q"

sha() { sha256sum "$1" | cut -d' ' -f1; }
[[ $(sha "$deck") == $(sha "$C/input.athinput") ]] || die "deck $deck differs from $C/input.athinput"
[[ -x ${EXE_SRC:-} ]] || die "executable EXE_SRC='${EXE_SRC:-}' not found"
exe_sha=$(sha "$EXE_SRC")
[[ $exe_sha == $(sha "$C/athena") ]] || die "executable $EXE_SRC differs from $C/athena"

seg=$(cat "$C/segment" 2>/dev/null || echo 0)
unc=$(cat "$C/uncounted" 2>/dev/null || echo 0)
used=$((seg - unc))
(( used < maxseg )) || die "segments used $used ($seg attempts, $unc not counted), max_segments $maxseg: none left"
rst=$(find "$RUNDIR/rst" -maxdepth 1 -name '*.rst' -printf '%T@ %p\n' 2>/dev/null | sort -k1,1gr | head -1 | cut -d' ' -f2-)
[[ -n $rst ]] || die "no restart file in $RUNDIR/rst"

args=("${EXTRA_ARGS[@]}")
if [[ -n $extra_in ]]; then
  [[ $extra_in == /* ]] || extra_in=$WT/$extra_in
  [[ -r $extra_in ]] || die "extra input $extra_in not readable"
  have=0
  for ((k = 0; k < ${#args[@]}; k++)); do
    [[ ${args[k]} == -i && ${args[k+1]:-} == "$extra_in" ]] && have=1
  done
  (( have )) || args+=(-i "$extra_in")
fi

echo "run $run: chain STATUS $st, segments used $used of new cap $maxseg ($seg attempts, $unc not counted); newest restart: $rst"
echo "  exe $EXE_SRC (sha256 ${exe_sha:0:12}) as $PROC_NAME; deck $deck; extra args: ${args[*]}"
cmdline=(env "PROC_NAME=$PROC_NAME" "JOB_NAME=$JOB_NAME" "MAX_SEGMENTS=$maxseg" "ATHENA_EXE=$EXE_SRC"
         "ATHENA_WALL=$ATHENA_WALL" "SLURM_TIME=$SLURM_TIME" "CPUS=$CPUS" "PARTITION=$PARTITION"
         "SLURM_EXTRA=$SLURM_EXTRA" "CHECK_CMD=$CHECK_CMD" "MAX_OUTSIDE_KILLS=${MAX_OUTSIDE_KILLS:-2}"
         "MAX_TERM_IN_A_ROW=${MAX_TERM_IN_A_ROW:-20}"
         "$chain_script" "$RUNDIR" "$deck" "${args[@]}")
if (( dry )); then
  printf '  dry run, would run:'; printf ' %q' "${cmdline[@]}"; echo
  exit 0
fi

old_jid=$(cat "$C/jobid" 2>/dev/null || true)
"${cmdline[@]}"; rc=$?
jid=$(cat "$C/jobid" 2>/dev/null || true)
if (( rc != 0 )) || [[ -z $jid || $jid == "$old_jid" ]]; then
  echo "continue_chain: scripts/submit_chain.sh exit $rc, job id '$jid' (before '$old_jid')" >&2
  [[ -n $jid && $jid != "$old_jid" ]] || exit 1
fi

now=$(date '+%Y-%m-%dT%H:%M:%S%z')
echo "$now job $jid from $rst max_segments $maxseg extra_input ${extra_in:-none} (continue_chain.sh, shared queue)" >> "$C/continuations.log" \
  || echo "continue_chain: warning: could not write $C/continuations.log" >&2
if "$PY" -I - "$MAN" "$now" "$jid" "$rst" "$maxseg" "$used" "$seg" "${extra_in:-}" <<'EOF'
import json, os, sys
p, now, jid, rst, ms, used, seg, xin = sys.argv[1:9]
m = json.load(open(p))
m.setdefault("continuations", []).append({
    "at": now, "job_id": jid, "from_restart": rst, "segments_used_before": int(used),
    "attempts_before": int(seg), "max_segments": int(ms), "extra_input": xin or None,
    "via": "harness/bin/nrpic-queue --cmd tracks/F-hills/binary_conv/scripts/continue_chain.sh",
    "reason": "continued in place after its segment cap (ruling 0042 item 2; batch 25)"})
with open(p + ".tmp", "w") as f:
    json.dump(m, f, indent=2)
    f.write("\n")
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
echo "$jid"
exit 0
