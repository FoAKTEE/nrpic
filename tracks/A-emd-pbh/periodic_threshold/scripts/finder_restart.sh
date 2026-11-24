#!/usr/bin/env bash
# F2 of periodic_threshold (JOURNAL 2026-11-24 13:25Z): the release finder restarted from P0L's
# card restart files, two or three cycles (tlim = T + 0.025, dt 0.0098) with a search every cycle, for several initial radii.
#   finder_restart.sh <outdir> <P0L run dir>
# Processor build: threaded release v0.6 (scratch/core/exe/core_nrpic_v06/athena_cpu_omp), 2 threads (session limit of six cores beside the 4-core analysis).
set -uo pipefail
OUT=$1; RUN=$2
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
for spec in "140:3:0.15" "140:3:0.3" "140:3:1.0" "140:3:2.0" "100:2:0.3" "100:2:1.0"; do
  IFS=: read -r T K R0 <<< "$spec"
  RST=$RUN/rst/peak.0000$K.rst
  D=$OUT/t${T}_r${R0}
  mkdir -p "$D"
  echo "== t=$T rst=$RST r0=$R0 $(date +%T)"
  ATHENA_EXE=$EXE THREADS=2 "$ROOT/scripts/cpu_run.sh" "$D" "$RST" \
    time/tlim=$T.025 \
    fastflow/find_every=1 fastflow/start_time_0=0.0 fastflow/initial_radius_0=$R0 \
    fastflow/flow_iterations_0=1000 fastflow/verbose=false
  echo "exit $? $(date +%T)"
  grep -v "^#" "$D"/peak.horizon_status_0.txt 2>/dev/null | tail -2
done
