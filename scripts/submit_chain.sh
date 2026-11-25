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
#   athena killed by a signal from outside the job      -> resubmit from the newest
#     (exit status 137 or 143 and no "Terminating on"      restart, at most
#     line of AthenaK, or 143 with "Terminating on         MAX_OUTSIDE_KILLS (2) times in
#     signal SIGTERM"; the job itself got no signal)       a row; then FAILED (decision 0021
#                                                         item 6: other projects on this
#                                                         machine run `pkill -x athena`)
# On SIGTERM the job resubmits at once, while it still can, and then waits for the
# executable: an AthenaK with the handler of utils/term_signal.cpp finishes its cycle,
# writes a restart file and exits with status 143 inside the grace period of the batch
# system (KillWait, 30 s on anta), so the next segment continues from the cycle of the
# signal; an older executable dies at once and the segment is lost back to its last
# scheduled restart file, as before.
# Segments: MAX_SEGMENTS caps the attempts that count. An attempt cut by a signal
# (SIGTERM to the job, or a kill from outside) before the executable's own wall-clock
# limit ATHENA_WALL does not count (decision 0032 item 2: preemptions used up the
# chains' segments); chain/uncounted holds their number. At most MAX_TERM_IN_A_ROW (20)
# attempts in a row may end by SIGTERM; then FAILED. When the last counted segment has
# ended without finishing the run, the chain ends there with STATUS FAILED
# "MAX_SEGMENTS=N reached": no further job is submitted only to say so.
# The input MUST contain a restart output block (file_type = rst) with a dt or dcycle
# short enough that a preemption loses little work; restart files land in <rundir>/rst/.
#
# The executable is copied into <rundir>/chain/athena at (re)start, so rebuilding while a
# chain runs does not change the binary that reads its restart files. Re-running the
# start command on an existing <rundir> resumes from the newest restart (e.g. after a
# FAILED segment was fixed, or to pick up a new binary).
# The copy is started under a run-specific name, <rundir>/chain/<PROC_NAME> (a hard link
# to chain/athena; default nrc-<8 hex digits of the rundir path>), so that its process
# name is not "athena" and a kill by name from another project (pkill -x athena, pkill
# athena, killall athena) does not hit it. An ATHENA_EXE that is a wrapper script which
# exec's another binary runs under that binary's name: the protection then does not hold.
#
# Environment at start: ATHENA_EXE (default build_gpu/src/athena), ATHENA_WALL (athena -t,
#   default 00:50:00), SLURM_TIME (default 00:59:00), CPUS (1), PARTITION (preempt),
#   MAX_SEGMENTS (default 100), JOB_NAME (default chain-<rundir name>),
#   PROC_NAME (process name of the run, 1 to 15 of [A-Za-z0-9._-], not containing
#   "athena"; default nrc-<hash>), MAX_OUTSIDE_KILLS (default 2),
#   MAX_TERM_IN_A_ROW (default 20),
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

# The process name of a run is the base name of the file executed (at most 15
# characters). The default is derived from the rundir, so it is the same at every
# (re)start of one chain and differs between chains.
default_proc_name() { echo "nrc-$(printf '%s' "$RUNDIR" | sha1sum | cut -c1-8)"; }
check_proc_name() {
  if [[ ! $1 =~ ^[A-Za-z0-9._-]{1,15}$ || ${1,,} == *athena* || $1 == athena* ]]; then
    echo "ERROR: PROC_NAME '$1' must be 1 to 15 of [A-Za-z0-9._-] and not contain 'athena'." >&2
    return 1
  fi
}
link_proc_name() {  # chain/<PROC_NAME>: the same file as chain/athena
  ln -f "$C/athena" "$C/$PROC_NAME" 2>/dev/null || cp -p "$C/athena" "$C/$PROC_NAME"
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
  echo "attempts: $(cat "$C/segment" 2>/dev/null || echo 0), of which not counted as segments (cut by a signal): $(cat "$C/uncounted" 2>/dev/null || echo 0); cap: $(sed -n 's/^MAX_SEGMENTS=//p' "$C/config.sh" 2>/dev/null)"
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
  # a chain that has used its segments would submit a job only to fail in it
  if (( $(cat "$C/segment" 2>/dev/null || echo 0) - $(cat "$C/uncounted" 2>/dev/null || echo 0) >= ${MAX_SEGMENTS:-100} )); then
    echo "ERROR: chain in $RUNDIR has used its ${MAX_SEGMENTS:-100} segments ($(cat "$C/segment") attempts, $(cat "$C/uncounted" 2>/dev/null || echo 0) not counted); raise MAX_SEGMENTS." >&2
    exit 1
  fi
  rm -f "$C/STOP"
  cp "$input" "$C/input.athinput"
  cp "$EXE" "$C/athena.tmp" && mv "$C/athena.tmp" "$C/athena"
  PROC_NAME=${PROC_NAME:-$(default_proc_name)}
  check_proc_name "$PROC_NAME" || exit 1
  link_proc_name || exit 1
  if [[ $(head -c 2 "$C/athena") == '#!' ]]; then
    echo "WARNING: $EXE is a script; a binary it exec's runs under its own name, not $PROC_NAME."
  fi
  {
    printf 'SCRIPT=%q\nSCRIPTS=%q\nEXE_SRC=%q\n' "$SCRIPTS/submit_chain.sh" "$SCRIPTS" "$EXE"
    printf 'ATHENA_WALL=%q\nSLURM_TIME=%q\nCPUS=%q\nPARTITION=%q\n' \
      "${ATHENA_WALL:-00:50:00}" "${SLURM_TIME:-00:59:00}" "${CPUS:-1}" "${PARTITION:-preempt}"
    printf 'MAX_SEGMENTS=%q\nJOB_NAME=%q\nSLURM_EXTRA=%q\nCHECK_CMD=%q\n' "${MAX_SEGMENTS:-100}" \
      "${JOB_NAME:-chain-$(basename "$RUNDIR")}" "${SLURM_EXTRA:-}" "${CHECK_CMD:-}"
    printf 'PROC_NAME=%q\nMAX_OUTSIDE_KILLS=%q\n' "$PROC_NAME" "${MAX_OUTSIDE_KILLS:-2}"
    printf 'MAX_TERM_IN_A_ROW=%q\n' "${MAX_TERM_IN_A_ROW:-20}"
    printf 'EXTRA_ARGS=('; for a in "$@"; do printf ' %q' "$a"; done; printf ' )\n'
  } > "$C/config.sh"
  # shellcheck source=/dev/null
  source "$C/config.sh"
  [[ $ATHENA_WALL =~ ^[0-9]+:[0-9]+:[0-9]+$ ]] || { echo "ATHENA_WALL must be hh:mm:ss" >&2; exit 1; }
  seg=$(cat "$C/segment" 2>/dev/null || echo 0)
  log_event "start/resume: exe=$EXE as $C/$PROC_NAME args=${EXTRA_ARGS[*]}"
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
# chains started before PROC_NAME existed get the default name at their next segment
PROC_NAME=${PROC_NAME:-$(default_proc_name)}
MAX_OUTSIDE_KILLS=${MAX_OUTSIDE_KILLS:-2}
MAX_TERM_IN_A_ROW=${MAX_TERM_IN_A_ROW:-20}   # chains started before it existed
check_proc_name "$PROC_NAME" || { set_status FAILED "PROC_NAME"; exit 1; }
if ! [[ $C/athena -ef $C/$PROC_NAME ]] && ! cmp -s "$C/athena" "$C/$PROC_NAME"; then
  link_proc_name
fi

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
# attempts cut by a signal before the executable's own wall-clock limit do not count
uncounted=$(cat "$C/uncounted" 2>/dev/null || echo 0)
if (( seg - uncounted > MAX_SEGMENTS )); then set_status FAILED "MAX_SEGMENTS=$MAX_SEGMENTS reached"; exit 1; fi
set_status RUNNING
# seconds of ATHENA_WALL (hh:mm:ss): an attempt that is signalled after that long has had
# its whole segment and counts
IFS=: read -r wh wm ws <<< "$ATHENA_WALL"
wall_s=$(( 10#${wh:-0} * 3600 + 10#${wm:-0} * 60 + 10#${ws:-0} ))
SECONDS=0

term=0
child=
on_term() {
  term=1
  [[ -n $child ]] && kill -TERM "$child" 2>/dev/null
}
trap on_term TERM INT

# resubmit <reason> [cut]: "cut" marks an attempt ended by a signal; it does not count
# as a segment unless it had run for ATHENA_WALL. After the last counted segment no job
# is submitted: it could only report that the cap is reached.
resubmit() {
  if [[ -f $C/STOP ]]; then set_status STOPPED "STOP file present"; return; fi
  if [[ ${2:-} == cut ]] && (( SECONDS < wall_s )); then
    uncounted=$((uncounted + 1))
    echo "$uncounted" > "$C/uncounted"
    log_event "attempt $seg cut after ${SECONDS} s: not counted as a segment ($uncounted not counted, $((seg - uncounted)) of $MAX_SEGMENTS used)"
  elif (( seg - uncounted >= MAX_SEGMENTS )); then
    set_status FAILED "MAX_SEGMENTS=$MAX_SEGMENTS reached after attempt $seg ($uncounted not counted); the run is not finished: raise MAX_SEGMENTS and give the start command again"
    return
  fi
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

  "$SCRIPTS/_athena_job.sh" "$RUNDIR" "$log" "$C/$PROC_NAME" "${args[@]}" &
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
  # killed by a signal that did not reach this job: an AthenaK without the handler of
  # utils/term_signal.cpp dies at once (SIGTERM gives 143, SIGKILL 137, no "Terminating
  # on" line); one with the handler answers SIGTERM by a restart file, the line
  # "Terminating on signal SIGTERM" and status 143
  if (( rc == 137 || rc == 143 )) && ! grep -q '^Terminating on' "$log"; then
    outcome="KILLED:$rc"; break
  fi
  if (( rc == 143 )) && grep -q '^Terminating on signal SIGTERM' "$log"; then
    outcome="KILLED:$rc"; break
  fi

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
            nt=$(( $(cat "$C/term_row" 2>/dev/null || echo 0) + 1 ))
            echo "$nt" > "$C/term_row"
            if (( nt > MAX_TERM_IN_A_ROW )); then
              set_status FAILED "ended by SIGTERM $nt times in a row"
            else
              # first the resubmission, while this script lives; the next segment waits
              # for the lock until the executable is gone
              resubmit "resubmitted after SIGTERM" cut
            fi
            # then the executable gets the rest of the grace period: one with the
            # handler finishes its cycle and writes a restart file (SIGKILL ends the
            # wait otherwise, and this script with it)
            t_term=$SECONDS
            while kill -0 "$child" 2>/dev/null; do wait "$child"; done
            if grep -q '^Terminating on signal SIGTERM' "$log"; then
              log_event "the run stopped by itself $((SECONDS - t_term)) s after the signal: $(grep -m1 '^restart outputs written' "$log")"
            else
              log_event "the run ended $((SECONDS - t_term)) s after the signal without a restart file of its own"
            fi
            (( nt > MAX_TERM_IN_A_ROW )) && exit 1 ;;
  KILLED:*) nk=$(( $(cat "$C/outside_kills" 2>/dev/null || echo 0) + 1 ))
            echo "$nk" > "$C/outside_kills"
            if grep -q '^Terminating on signal SIGTERM' "$log"; then
              log_event "athena stopped on a SIGTERM from outside the job (exit ${outcome#KILLED:}, restart file written; $nk in a row)"
            else
              log_event "athena killed from outside the job (exit ${outcome#KILLED:}, no termination message; $nk in a row)"
            fi
            if (( nk > MAX_OUTSIDE_KILLS )); then
              set_status FAILED "killed from outside $nk times in a row (exit ${outcome#KILLED:})"; exit 1
            fi
            resubmit "resubmitted after an outside kill ($nk of at most $MAX_OUTSIDE_KILLS)" cut ;;
  CONTINUE) echo 0 > "$C/outside_kills"; echo 0 > "$C/term_row"
            log_event "wall-clock limit reached at '$final'"
            resubmit "resubmitted after wall-clock stop" ;;
  DONE:*)   echo 0 > "$C/outside_kills"; echo 0 > "$C/term_row"
            log_event "finished: $final"; set_status DONE "${outcome#DONE:}" ;;
  FAILED:*) set_status FAILED "${outcome#FAILED:}"; exit 1 ;;
esac
exit 0
