#!/usr/bin/env bash
# Sequencer of F-hills (lead, batch 5; decision 0025 item 5): keeps the chain C (a chain
# registered with nrpic-run whose first job was put on hold with `scontrol hold`) held while
# chain B runs, and releases it once B has ended (STATUS DONE, FAILED or STOPPED), so that at
# most two card jobs of this owner are eligible at a time. It writes no file outside its log
# and touches no git index.
#
#   setsid nohup tracks/F-hills/binary_conv/scripts/seq_release.sh <rundir of B> <job name of C> \
#       >> /data/haiyangw/nrpic/scratch/F-hills/seq/seq.log 2>&1 < /dev/null &
#
# See it: cat /data/haiyangw/nrpic/scratch/F-hills/seq/seq.pid; tail seq.log; ps -p <pid>
# Stop it without releasing C: touch /data/haiyangw/nrpic/scratch/F-hills/seq/STOP
#   (it exits within five minutes), or kill <pid> (numeric). Release C by hand:
#   scontrol release <job id>  (squeue -u $USER -n <job name of C>).
set -uo pipefail
B=${1:?rundir of chain B}
CNAME=${2:?Slurm job name of chain C}
SEQ=/data/haiyangw/nrpic/scratch/F-hills/seq
STOP=$SEQ/STOP
echo $$ > "$SEQ/seq.pid"
log() { echo "$(date '+%F %T') $*"; }
log "start: B=$B C=$CNAME pid=$$"
while true; do
  if [[ -e $STOP ]]; then log "STOP file present: exit, C left as it is"; exit 0; fi
  st=$(head -c 40 "$B/chain/STATUS" 2>/dev/null || echo UNKNOWN)
  pend=$(squeue -h -u "$USER" -n "$CNAME" -t PD -o '%i %r' 2>/dev/null)
  case $st in
    DONE*|FAILED*|STOPPED*)
      if [[ -z $pend ]]; then
        log "B ended ($st); no pending job of C (running, ended or cancelled): exit"; exit 0
      fi
      while read -r j r; do
        [[ -z $j ]] && continue
        if scontrol release "$j"; then log "B ended ($st): released job $j of C"; fi
      done <<< "$pend"
      exit 0 ;;
    *)
      while read -r j r; do
        [[ -z $j ]] && continue
        if [[ $r != JobHeldUser ]]; then
          scontrol hold "$j" && log "B is $st: held job $j of C (reason was $r)"
        fi
      done <<< "$pend" ;;
  esac
  sleep 300
done
