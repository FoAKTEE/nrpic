#!/usr/bin/env bash
# Chain AthenaK runs across the 1 h limit of the preempt partition.
#
#   scripts/submit_chain.sh <rundir> <athinput> [extra athena args...]   start / resume
#   scripts/submit_chain.sh --status <rundir>                            show state
#   scripts/submit_chain.sh --stop <rundir>     cancel the chain's job, no resubmission
#
# Each segment is one sbatch job (1 GPU, 1 core) that runs
#     athena -i <athinput> ... -t $ATHENA_WALL         (first segment, no restart yet)
#     athena -r <newest rst/*.rst> ... -t $ATHENA_WALL (later segments)
# AthenaK stops at the wall-clock limit -t and its Driver::Finalize() then writes every
# output once more, including a restart file. The job then decides:
#   "Terminating on time limit" or "... cycle limit"   -> DONE, no resubmission
#   "Terminating on wall clock limit" and cycle advanced -> resubmit itself
#   nonzero exit, no termination message, NaN/Inf in the final time or the last history
#   line, a history "Volume" column below half its initial value (how NaN Z4c fields
#   show up), CHECK_CMD failing, or no progress           -> FAILED, no resubmission
#   "restart file is broken" (e.g. killed mid-write)   -> rename it *.rst.bad and retry
#                                                         from the next-newest restart
#   SIGTERM (preemption, time-out, scancel)             -> resubmit from the newest
#                                                         restart, unless --stop was used
# The input MUST contain a restart output block (file_type = rst) with a dt or dcycle
# short enough that a preemption loses little work; restart files land in <rundir>/rst/.
#
# The executable is copied into <rundir>/chain/athena at (re)start, so rebuilding while a
# chain runs does not change the binary that reads its restart files. Re-running the
# start command on an existing <rundir> resumes from the newest restart (e.g. after a
# FAILED segment was fixed, or to pick up a new binary).
#
# Environment at start: ATHENA_EXE (default build_gpu/src/athena), ATHENA_WALL (athena -t,
#   default 00:50:00), SLURM_TIME (default 00:59:00), CPUS (1), PARTITION (preempt),
#   MAX_SEGMENTS (default 100), JOB_NAME (default chain-<rundir name>),
#   SLURM_EXTRA (extra sbatch options), CHECK_CMD (optional shell command run after each
#   segment that ends normally, with the rundir as $1; nonzero exit -> FAILED)
# State, Slurm output and per-segment logs are in <rundir>/chain/.
set -uo pipefail

usage() { awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"; exit 1; }
log_event() { echo "$(date '+%F %T') seg=${seg:-0} job=${SLURM_JOB_ID:-login} $*" >> "$C/events.log"; }
set_status() { echo "$1" > "$C/STATUS"; log_event "STATUS $1${2:+ ($2)}"; }

# sbatch from inside a job would otherwise inherit SLURM_* settings of the current job
clean_sbatch() {
  local unset_args=() v
  for v in $(compgen -e | grep -E '^(SLURM_|SBATCH_)'); do unset_args+=(-u "$v"); done
  env "${unset_args[@]}" sbatch "$@"
}

submit_segment() {
  local jid
  # shellcheck disable=SC2086
  jid=$(clean_sbatch --parsable -p "$PARTITION" --gres=gpu:1 -c "$CPUS" -t "$SLURM_TIME" \
          -J "$JOB_NAME" -o "$C/slurm-%j.out" $SLURM_EXTRA \
          "$SCRIPT" --job "$RUNDIR") || return 1
  echo "$jid" > "$C/jobid"
  log_event "submitted job $jid"
  echo "$jid"
}

job_active() {  # is the chain's last submitted job pending or running?
  local jid
  jid=$(cat "$C/jobid" 2>/dev/null) || return 1
  [[ -n $jid && -n $(squeue -h -j "$jid" -o %T 2>/dev/null) ]]
}

#---------------------------------------------------------------------------------------
mode=start
case ${1:-} in
  --job)    mode=job;    shift ;;
  --status) mode=status; shift ;;
  --stop)   mode=stop;   shift ;;
  -h|--help|"") usage ;;
esac
[[ -n ${1:-} ]] || usage
mkdir -p "$1" || exit 1
RUNDIR=$(cd "$1" && pwd)
C=$RUNDIR/chain
shift

#---------------------------------------------------------------------------------------
if [[ $mode == status ]]; then
  echo "STATUS: $(cat "$C/STATUS" 2>/dev/null || echo none)   job: $(cat "$C/jobid" 2>/dev/null)"
  job_active && squeue -j "$(cat "$C/jobid")"
  tail -n 15 "$C/events.log" 2>/dev/null
  ls -lt "$RUNDIR"/rst/*.rst 2>/dev/null | head -3
  exit 0
fi

if [[ $mode == stop ]]; then
  [[ -d $C ]] || { echo "no chain in $RUNDIR" >&2; exit 1; }
  touch "$C/STOP"
  if job_active; then scancel "$(cat "$C/jobid")"; echo "cancelled job $(cat "$C/jobid")"; fi
  set_status STOPPED "by --stop"
  exit 0
fi

#---------------------------------------------------------------------------------------
if [[ $mode == start ]]; then
  [[ $# -ge 1 ]] || usage
  input=$(cd "$(dirname "$1")" && pwd)/$(basename "$1"); shift
  [[ -f $input ]] || { echo "ERROR: no such input file: $input" >&2; exit 1; }
  SCRIPTS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
  EXE=${ATHENA_EXE:-$(dirname "$SCRIPTS")/build_gpu/src/athena}
  [[ -x $EXE ]] || { echo "ERROR: executable not found: $EXE" >&2; exit 1; }
  EXE=$(cd "$(dirname "$EXE")" && pwd)/$(basename "$EXE")
  if ! grep -qE '^[[:space:]]*file_type[[:space:]]*=[[:space:]]*rst([[:space:]#]|$)' "$input"; then
    echo "ERROR: $input has no restart output (an <outputN> block with file_type = rst)." >&2
    echo "       Chaining needs periodic restart files; add one with dt or dcycle." >&2
    exit 1
  fi
  # Only particle_type = nrpic is checkpointed (rst/<name>.rst.prt next to each mesh
  # restart, outputs/restart.cpp); other particle types are not stored in restart files.
  if grep -qE '^[[:space:]]*<particles>' "$input" && \
     ! grep -qE '^[[:space:]]*particle_type[[:space:]]*=[[:space:]]*nrpic([[:space:]#]|$)' "$input"; then
    echo "WARNING: <particles> with a particle_type other than nrpic: those particles are"
    echo "         not written to restart files and are lost at the first restart."
  fi
  mkdir -p "$C"
  if job_active; then
    echo "ERROR: job $(cat "$C/jobid") of this chain is still queued/running." >&2
    exit 1
  fi
  if [[ $(cat "$C/STATUS" 2>/dev/null) == DONE ]]; then
    echo "ERROR: chain in $RUNDIR is DONE (rm $C/STATUS to force)." >&2
    exit 1
  fi
  rm -f "$C/STOP"
  cp "$input" "$C/input.athinput"
  cp "$EXE" "$C/athena.tmp" && mv "$C/athena.tmp" "$C/athena"
  {
    printf 'SCRIPT=%q\nSCRIPTS=%q\nEXE_SRC=%q\n' "$SCRIPTS/submit_chain.sh" "$SCRIPTS" "$EXE"
    printf 'ATHENA_WALL=%q\nSLURM_TIME=%q\nCPUS=%q\nPARTITION=%q\n' \
      "${ATHENA_WALL:-00:50:00}" "${SLURM_TIME:-00:59:00}" "${CPUS:-1}" "${PARTITION:-preempt}"
    printf 'MAX_SEGMENTS=%q\nJOB_NAME=%q\nSLURM_EXTRA=%q\nCHECK_CMD=%q\n' "${MAX_SEGMENTS:-100}" \
      "${JOB_NAME:-chain-$(basename "$RUNDIR")}" "${SLURM_EXTRA:-}" "${CHECK_CMD:-}"
    printf 'EXTRA_ARGS=('; for a in "$@"; do printf ' %q' "$a"; done; printf ' )\n'
  } > "$C/config.sh"
  # shellcheck source=/dev/null
  source "$C/config.sh"
  [[ $ATHENA_WALL =~ ^[0-9]+:[0-9]+:[0-9]+$ ]] || { echo "ATHENA_WALL must be hh:mm:ss" >&2; exit 1; }
  seg=$(cat "$C/segment" 2>/dev/null || echo 0)
  log_event "start/resume: exe=$EXE args=${EXTRA_ARGS[*]}"
  set_status QUEUED          # before sbatch: the job may start (and finish) at once
  jid=$(submit_segment) || { set_status FAILED "sbatch failed"; echo "ERROR: sbatch failed" >&2; exit 1; }
  echo "chain started in $RUNDIR: job $jid (athena -t $ATHENA_WALL, Slurm -t $SLURM_TIME)"
  echo "monitor: scripts/submit_chain.sh --status $RUNDIR"
  exit 0
fi

#---------------------------------------------------------------------------------------
# job mode: runs inside the Slurm allocation
# shellcheck source=/dev/null
source "$C/config.sh"
seg=$(cat "$C/segment" 2>/dev/null || echo 0)

# Only one segment may run per rundir. A segment resubmitted on preemption can start
# while the previous one is still being killed, so wait for the lock (athena inherits it).
exec 9>"$C/lock"
if ! flock -w 300 9; then
  log_event "could not acquire $C/lock within 300 s; another segment is running"
  set_status FAILED "lock"
  exit 1
fi
if [[ -f $C/STOP ]]; then set_status STOPPED "STOP file present"; exit 0; fi

seg=$((seg + 1))
echo "$seg" > "$C/segment"
if (( seg > MAX_SEGMENTS )); then set_status FAILED "MAX_SEGMENTS=$MAX_SEGMENTS reached"; exit 1; fi
set_status RUNNING

term=0
child=
on_term() {
  term=1
  [[ -n $child ]] && kill -TERM "$child" 2>/dev/null
}
trap on_term TERM INT

resubmit() {
  if [[ -f $C/STOP ]]; then set_status STOPPED "STOP file present"; return; fi
  set_status QUEUED "$1"
  submit_segment >/dev/null || set_status FAILED "sbatch failed after: $1"
}

hst_volume_collapsed() {  # history files whose "Volume" column fell below half its start
  local h col
  for h in "$RUNDIR"/*.hst; do
    [[ -f $h ]] || continue
    col=$(grep -m1 -oE '\[[0-9]+\]=Volume' "$h" | tr -dc '0-9')
    [[ -n $col ]] || continue
    awk -v c="$col" '!/^#/ && NF>=c {if (n==0) f=$c+0; l=$c+0; n++}
                     END {exit !(n>1 && f>0 && l<0.5*f)}' "$h" && basename "$h"
  done
}

newest_restart() {  # newest modification time first; ties broken by higher file number
  find "$RUNDIR/rst" -maxdepth 1 -name '*.rst' -printf '%T@ %p\n' 2>/dev/null |
    sort -k1,1gr -k2,2r | head -1 | cut -d' ' -f2-
}

outcome=
for attempt in 1 2 3; do
  rst=$(newest_restart)
  if [[ -n $rst ]]; then
    args=(-r "$rst")
  else
    args=(-i "$C/input.athinput")
  fi
  args+=(-d "$RUNDIR" -t "$ATHENA_WALL" "${EXTRA_ARGS[@]}")
  log=$C/seg$(printf %03d "$seg").job${SLURM_JOB_ID:-x}.a$attempt.log
  ln -sfn "$(basename "$log")" "$C/latest.log"
  log_event "attempt $attempt: athena ${args[*]}"

  "$SCRIPTS/_athena_job.sh" "$RUNDIR" "$log" "$C/athena" "${args[@]}" &
  child=$!
  while :; do
    wait "$child"; rc=$?
    if (( rc > 128 )) && kill -0 "$child" 2>/dev/null; then
      (( term )) && break     # preempted/cancelled: do not wait for the SIGKILL
      continue
    fi
    break
  done
  if (( term )); then outcome=TERM; break; fi

  final=$(grep -E '^time=.* cycle=' "$log" | tail -1)
  last_hst=$(for h in "$RUNDIR"/*.hst; do [[ -f $h ]] && tail -n 1 "$h"; done)
  # restart-read failures: "... restart file is broken", "Header size read from restart
  # file is incorrect", "<par_end> is not found", "Unable to open restart file"
  if [[ -n $rst && $rc -ne 0 ]] && ! grep -q 'Setup complete' "$log" && \
     grep -qE 'restart file|par_end' "$log"; then
    mv "$rst" "$rst.bad"
    log_event "restart file $rst is broken -> renamed .bad, trying an older one"
    continue
  fi
  if [[ $rc -ne 0 ]]; then outcome="FAILED:athena exit status $rc"; break; fi
  if grep -qiE 'nan|inf' <<< "$final"; then outcome="FAILED:NaN/Inf in '$final'"; break; fi
  if grep -qiE '(^|[[:space:]])[-+]?(nan|inf)' <<< "$last_hst"; then
    outcome="FAILED:NaN/Inf in last history line"; break
  fi
  # The Z4c history sums only cells with chi >= excise_chi, so NaN fields show up as
  # zero norms and a collapsing "Volume" column rather than as "nan".
  vol=$(hst_volume_collapsed)
  if [[ -n $vol ]]; then outcome="FAILED:history Volume collapsed ($vol), NaN fields?"; break; fi
  if [[ -n ${CHECK_CMD:-} ]] && ! bash -c "$CHECK_CMD" _ "$RUNDIR" >> "$log" 2>&1; then
    outcome="FAILED:CHECK_CMD '$CHECK_CMD' returned nonzero"; break
  fi
  if grep -q 'Terminating on time limit' "$log"; then outcome=DONE:tlim; break; fi
  if grep -q 'Terminating on cycle limit' "$log"; then outcome=DONE:nlim; break; fi
  if grep -q 'Terminating on wall clock limit' "$log"; then
    cyc=$(sed -n 's/.* cycle=\([0-9]*\).*/\1/p' <<< "$final")
    prev=$(cat "$C/last_cycle" 2>/dev/null || echo -1)
    echo "${cyc:--1}" > "$C/last_cycle"
    if [[ -z $cyc || $cyc -le $prev ]]; then
      outcome="FAILED:no progress in this segment (cycle ${cyc:-?} <= $prev)"; break
    fi
    outcome=CONTINUE; break
  fi
  outcome="FAILED:athena exited 0 without a termination message"; break
done
[[ -z $outcome ]] && outcome="FAILED:no readable restart file after 3 attempts"

case $outcome in
  TERM)     log_event "received SIGTERM (preemption, time limit or scancel)"
            resubmit "resubmitted after SIGTERM" ;;
  CONTINUE) log_event "wall-clock limit reached at '$final'"
            resubmit "resubmitted after wall-clock stop" ;;
  DONE:*)   log_event "finished: $final"; set_status DONE "${outcome#DONE:}" ;;
  FAILED:*) set_status FAILED "${outcome#FAILED:}"; exit 1 ;;
esac
exit 0
