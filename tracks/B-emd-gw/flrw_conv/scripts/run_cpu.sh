#!/usr/bin/env bash
# Processor runs of flrw_conv on core's threaded executable (scratch/core/exe/
# core_build-openmp/athena_cpu, release-v0.3 options only), one after another.
#   run_cpu.sh <list>     lines "<name> <athinput> [athena args...]" as for gpu_batch.sh;
#                         output $NRPIC_RUN_DIR/<name>/ (status in $NRPIC_RUN_DIR/status)
# Environment: THREADS (default 6), ATHENA_CPU_EXE.
set -euo pipefail
out=${NRPIC_RUN_DIR:?run through nrpic-run}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
EXE=${ATHENA_CPU_EXE:-/data/haiyangw/nrpic/scratch/core/exe/core_build-openmp/athena_cpu}
THREADS=${THREADS:-6}
list=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
export OMP_NUM_THREADS=$THREADS OMP_PROC_BIND=true
rc=0
while read -r line; do
  [[ -z $line || $line == \#* ]] && continue
  # shellcheck disable=SC2086
  set -- $line
  name=$1; deck=$WT/$2; shift 2
  d=$out/$name
  mkdir -p "$d"
  cp "$deck" "$d/"
  OMP_PLACES=$(python3 "$WT/tracks/B-emd-gw/flrw_conv/scripts/omp_places.py" "$THREADS")
  export OMP_PLACES
  echo "# $(date -Is) places=$OMP_PLACES load=$(cut -d' ' -f1-3 /proc/loadavg)" > "$d/athena.log"
  if ( cd "$d" && "$EXE" -i "$deck" -d "$d" "$@" >> "$d/athena.log" 2>&1 ); then r=0; else r=$?; rc=1; fi
  echo "$(date +%H:%M:%S) rc=$r $name" >> "$out/status"
done < "$list"
exit $rc
