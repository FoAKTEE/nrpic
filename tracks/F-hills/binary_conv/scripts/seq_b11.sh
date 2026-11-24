#!/usr/bin/env bash
# Sequencer of F-hills, lead batch 11 (decisions 0025 item 5, 0026, 0030 item 4). Two jobs:
#
#  1. Hold: a chain listed with an AFTER chain stays held (scontrol hold) until the AFTER chain
#     has ended for good, so that at most two card jobs of this owner are eligible at a time.
#  2. Continue a chain cut by its segment cap: a chain whose STATUS is FAILED with the reason
#     "MAX_SEGMENTS=... reached" (preempted segments count as segments) is started again in place
#     from its newest restart file (scripts/submit_chain.sh resumes an existing run directory),
#     with MAX_SEGMENTS raised by floor(left / 0.9833 h), where left = CEILING - the card time the
#     chain's jobs have used (sacct ElapsedRaw over its job name). CEILING is the card-hours
#     registered for the run (nrpic-run submit --gpu-hours), so the run never uses more than it
#     was registered for. A chain that FAILED for any other reason is left alone (logged).
#
# A chain has ended for good when its STATUS is DONE or STOPPED, when it FAILED for another
# reason, or when it is cut and less than one segment of card time is left. The sequencer exits
# when every chain has ended for good, or at once when <seqdir>/STOP exists. It writes only its
# log and pid file, touches no git index, and never deletes a file.
#
#   setsid nohup tracks/F-hills/binary_conv/scripts/seq_b11.sh <seqdir> <table> \
#       >> <seqdir>/seq_b11.log 2>&1 < /dev/null &
#
# <table>: one chain per line, `name rundir ceiling_hours after_name|- deck`; comments with #
#   (deck: the input file the run was registered with; only its copy test matters on a resume,
#   AthenaK restarts from the newest rst/*.rst of the run directory).
# See it: cat <seqdir>/seq_b11.pid; ps -p <pid>; tail <seqdir>/seq_b11.log
# Dry pass (logs what it would do, submits and holds nothing, exits after one pass): SEQ_DRY=1.
# Stop it: touch <seqdir>/STOP (exits within five minutes) or kill <pid> (numeric only).
set -uo pipefail
SEQ=${1:?seq dir}
TABLE=${2:?table}
SEG_H=0.98333              # Slurm limit of one segment, 59 min
echo $$ > "$SEQ/seq_b11.pid"
log() { echo "$(date '+%F %T') $*"; }
log "start pid=$$ table=$TABLE"

declare -A RUNDIR CEIL AFTER ENDED DECK
NAMES=()
while read -r n d c a k; do
  [[ -z ${n:-} || $n == \#* ]] && continue
  NAMES+=("$n"); RUNDIR[$n]=$d; CEIL[$n]=$c; AFTER[$n]=$a; DECK[$n]=$k; ENDED[$n]=0
done < "$TABLE"

status_of() { head -c 40 "${RUNDIR[$1]}/chain/STATUS" 2>/dev/null || echo UNKNOWN; }
jobname_of() { (source "${RUNDIR[$1]}/chain/config.sh" 2>/dev/null; echo "${JOB_NAME:-}"); }
cut_by_cap() { grep 'STATUS FAILED' "${RUNDIR[$1]}/chain/events.log" 2>/dev/null | tail -1 | grep -q 'MAX_SEGMENTS='; }
used_hours() {
  local jn; jn=$(jobname_of "$1")
  sacct -n -X -P -S 2026-11-20 --name "$jn" -o ElapsedRaw 2>/dev/null |
    awk '{s += $1} END {printf "%.4f", s / 3600}'
}
active_jobs() { squeue -h -u "$USER" -n "$(jobname_of "$1")" -o '%i %t %r' 2>/dev/null; }

check_end() {      # sets ENDED[n]=1 when the chain has ended for good
  local n=$1 st left
  st=$(status_of "$n")
  case $st in
    DONE*|STOPPED*) ENDED[$n]=1; log "$n ended ($st)" ;;
    FAILED*)
      if cut_by_cap "$n"; then
        left=$(awk -v c="${CEIL[$n]}" -v u="$(used_hours "$n")" 'BEGIN {print c - u}')
        if awk -v l="$left" -v s="$SEG_H" 'BEGIN {exit !(l < s)}'; then
          ENDED[$n]=1; log "$n cut by its cap and only ${left} card-hours left of ${CEIL[$n]}: ended"
        fi
      else
        ENDED[$n]=1; log "$n FAILED for a reason other than the cap: left alone ($(grep 'STATUS FAILED' "${RUNDIR[$n]}/chain/events.log" | tail -1))"
      fi ;;
  esac
}

continue_chain() { # resubmit a chain cut by its cap, in place, within its ceiling
  local n=$1 d=${RUNDIR[$1]} used left add seg newmax
  [[ -n $(active_jobs "$n") ]] && return
  used=$(used_hours "$n")
  left=$(awk -v c="${CEIL[$n]}" -v u="$used" 'BEGIN {print c - u}')
  add=$(awk -v l="$left" -v s="$SEG_H" 'BEGIN {print int(l / s)}')
  (( add >= 1 )) || return
  seg=$(cat "$d/chain/segment" 2>/dev/null || echo 0)
  newmax=$((seg + add))
  if [[ ${SEQ_DRY:-0} == 1 ]]; then
    log "DRY $n: would continue in place: used ${used} of ${CEIL[$n]}, MAX_SEGMENTS ${seg} -> ${newmax}, deck ${DECK[$n]}"
    return
  fi
  (
    source "$d/chain/config.sh"
    export ATHENA_EXE=$EXE_SRC ATHENA_WALL SLURM_TIME CPUS PARTITION JOB_NAME SLURM_EXTRA \
      CHECK_CMD PROC_NAME MAX_OUTSIDE_KILLS MAX_SEGMENTS=$newmax
    "$SCRIPT" "$d" "${DECK[$n]}" "${EXTRA_ARGS[@]}"
  ) && log "$n continued in place: used ${used} of ${CEIL[$n]} card-hours, MAX_SEGMENTS ${seg} -> ${newmax}" \
    || log "$n: resubmission FAILED (see the chain's events.log)"
}

hold_or_release() {
  local n=$1 a=${AFTER[$1]} j st r
  [[ $a == - ]] && return
  while read -r j st r; do
    [[ -z ${j:-} || $st != PD ]] && continue
    if [[ ${SEQ_DRY:-0} == 1 ]]; then log "DRY $n: job $j ($r), after $a ended=${ENDED[$a]:-1}"; continue; fi
    if (( ${ENDED[$a]:-1} )); then
      [[ $r == JobHeldUser ]] && scontrol release "$j" && log "$a has ended: released job $j of $n"
    else
      [[ $r != JobHeldUser ]] && scontrol hold "$j" && log "$a runs: held job $j of $n (reason was $r)"
    fi
  done <<< "$(active_jobs "$n")"
}

while true; do
  if [[ -e $SEQ/STOP ]]; then log "STOP file present: exit, chains left as they are"; exit 0; fi
  all=1
  for n in "${NAMES[@]}"; do
    (( ENDED[$n] )) && continue
    check_end "$n"
    if (( ! ENDED[$n] )); then
      all=0
      st=$(status_of "$n")
      if [[ $st == FAILED* ]] && cut_by_cap "$n"; then
        a=${AFTER[$n]}
        if [[ $a == - ]] || (( ${ENDED[$a]:-1} )); then continue_chain "$n"; fi
      fi
      hold_or_release "$n"
    fi
  done
  (( all )) && { log "every chain has ended: exit"; exit 0; }
  [[ ${SEQ_DRY:-0} == 1 ]] && { log "DRY: one pass done"; exit 0; }
  sleep 300
done
