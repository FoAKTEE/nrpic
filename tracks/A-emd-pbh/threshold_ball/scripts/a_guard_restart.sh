#!/usr/bin/env bash
# Entry 5 of threshold_ball (G1-G3): A-d0.42 restarted on processors from its t = 44 restart.
#   a_guard_restart.sh <outdir>
set -uo pipefail
OUT=$1
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
RST=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-235851-d2200d7/A-d0.42/rst/ball.00011.rst
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
for spec in "G1:" "G2:z4c/lapse_leak=0.0" "G3:particles/alpha_exc=0.3"; do
  NAME=${spec%%:*}; EXTRA=${spec#*:}
  D=$OUT/$NAME; mkdir -p "$D"
  echo "== $NAME extra='$EXTRA' $(date +%T)"
  # shellcheck disable=SC2086
  ATHENA_EXE=$EXE THREADS=4 "$ROOT/scripts/cpu_run.sh" "$D" "$RST" time/tlim=48.5 $EXTRA
  echo "exit $? $(date +%T)"
  grep -h "guard: the run stops\|first such cell" "$D"/ball.guard.txt 2>/dev/null
  grep -E "cycle=[0-9]+ time=" "$D"/athena.log | tail -1
done
